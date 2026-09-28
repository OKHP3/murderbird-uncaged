"""Freeze a sampled opening-path relief in one rigid crown plate.

The V4 plate cleared at rest but crossed a fixed brow during early opening.
Cut against the fixed brow represented in the moving cover's rest frame.
This sampled construction operation is not a continuous-clearance proof.
"""
from pathlib import Path
import hashlib, json, runpy, shutil
import bpy, bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'assets/models/uncaged-orbital-saddle-study-v4/murderbird-orbital-saddle-study-v4.blend'
OUT = ROOT / 'assets/models/uncaged-orbital-saddle-study-v5'
AUDIT = ROOT / 'assets/audit/orbital-saddle-study-v5'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def artifact(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path), 'bytes': path.stat().st_size}

def main():
    assert sha(BASE) == 'd1afd0f5d97b48bed7828993bbedab3535acaabdec9f505afc38df9584394c4a'
    assert not OUT.exists() and not AUDIT.exists()
    h = runpy.run_path(str(ROOT / 'scripts/build-uncaged-alignment-v7.py'), run_name='helpers')
    bpy.ops.wm.open_mainfile(filepath=str(BASE))
    before = h['scene_snapshot']()
    crown = bpy.data.objects['Rounded swept crown lamina 0']
    cover = bpy.data.objects['cranial-cover']
    assert crown.parent == cover and cover.parent.name == 'head'
    # location is parent-local. Use the actual parent's world basis instead
    # of assuming that native Z always equals the current world Z.
    full_lift_world = cover.parent.matrix_world.to_3x3() @ Vector((0, 0, .08))
    operations = []
    for side in (-1, 1):
        brow = bpy.data.objects[f'Forged orbital brow {side}']
        cutter = bpy.data.objects.new(f'Temporary V5 opening relief {side}', brow.data.copy())
        bpy.context.scene.collection.objects.link(cutter)
        matrix = brow.matrix_world.copy()
        cutter.matrix_world = matrix
        bm = bmesh.new()
        bm.from_mesh(cutter.data)
        bm.normal_update()
        for vertex in bm.verts:
            vertex.co += vertex.normal * .002
        bm.to_mesh(cutter.data)
        bm.free()
        for step in range(41):
            opening = step / 40
            cutter.matrix_world = matrix.copy()
            cutter.location -= full_lift_world * opening
            bpy.context.view_layer.update()
            modifier = crown.modifiers.new(f'Frozen opening relief {side} {step}', 'BOOLEAN')
            modifier.operation = 'DIFFERENCE'
            modifier.solver = 'EXACT'
            modifier.object = cutter
            bpy.context.view_layer.objects.active = crown
            bpy.ops.object.modifier_apply(modifier=modifier.name)
            operations.append({'side': side, 'openingFraction': opening})
        bpy.data.objects.remove(cutter, do_unlink=True)
    bpy.context.view_layer.update()
    after = h['scene_snapshot']()
    assert before['empties'] == after['empties'] and before['curves'] == after['curves']
    assert set(before['meshes']) == set(after['meshes'])
    for name, signature in before['meshes'].items():
        if name != crown.name:
            assert after['meshes'][name] == signature, name
    bm = bmesh.new()
    bm.from_mesh(crown.data)
    topology = {'vertices': len(bm.verts), 'faces': len(bm.faces),
                'nonManifoldEdges': sum(not edge.is_manifold for edge in bm.edges),
                'looseVertices': sum(not vertex.link_faces for vertex in bm.verts)}
    assert not topology['nonManifoldEdges'] and not topology['looseVertices'], topology
    bm.free()
    assert not any(mod.type == 'BOOLEAN' for obj in bpy.data.objects for mod in obj.modifiers)
    OUT.mkdir(parents=True)
    AUDIT.mkdir(parents=True)
    native = OUT / 'murderbird-orbital-saddle-study-v5.blend'
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(native), check_existing=False)
    bpy.ops.wm.open_mainfile(filepath=str(native))
    assert h['scene_snapshot']() == after
    shutil.copy2(__file__, AUDIT / 'executed-generator.py')
    receipt = {'status': 'unreviewed rigid opening-path relief proposal; not selected',
               'base': artifact(BASE), 'native': artifact(native), 'generator': artifact(AUDIT / 'executed-generator.py'),
               'changedMesh': 'Rounded swept crown lamina 0', 'topology': topology,
               'construction': {'fullCoverLiftWorldXYZM': list(full_lift_world),
                                'nominalCutterNormalExpansionM': .002,
                                'sampledCutOperations': operations},
               'preservation': {'other698MeshesExact': True, '51PivotsAnd462GuidesExact': True,
                                'saveReloadExact': True, 'noConstructionCuttersOrBooleanDependencies': True},
               'limits': ['Discrete cutter placements require an independent opening sweep; they are not a continuous swept-volume proof.',
                          'The seam is reconstructed mechanical clearance, not a measured source-art detail.',
                          'No export, app selection, owner approval or publication.']}
    (AUDIT / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    render = runpy.run_path(str(ROOT / 'scripts/study-v8-bill-envelope.py'), run_name='renderer')['renders']
    render.__globals__['AUDIT'] = AUDIT
    receipt['views'] = render(BASE, 'before') + render(native, 'after')
    (AUDIT / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(artifact(native)))

if __name__ == '__main__':
    main()
