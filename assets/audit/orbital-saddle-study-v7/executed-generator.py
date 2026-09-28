"""Two-part fit correction at the removable brow's forward lower corners.

The fixed mounting bed already defines the aperture. Preserve that wall and
form each brow edge against it, applying the construction cut before saving.
"""
from pathlib import Path
import hashlib, json, runpy, shutil
import bpy, bmesh

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'assets/models/uncaged-orbital-saddle-study-v6/murderbird-orbital-saddle-study-v6.blend'
OUT = ROOT / 'assets/models/uncaged-orbital-saddle-study-v7'
AUDIT = ROOT / 'assets/audit/orbital-saddle-study-v7'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def artifact(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path), 'bytes': path.stat().st_size}

def main():
    assert sha(BASE) == 'cb811241d241b0f18f529979b77635caecb83284b8b4df29c7564d4d2bf55eec'
    assert not OUT.exists() and not AUDIT.exists()
    h = runpy.run_path(str(ROOT / 'scripts/build-uncaged-alignment-v7.py'), run_name='helpers')
    bpy.ops.wm.open_mainfile(filepath=str(BASE))
    before = h['scene_snapshot']()
    changed = []
    topology = []
    for side in (-1, 1):
        brow = bpy.data.objects[f'Forged orbital brow {side}']
        mount = bpy.data.objects[f'Forged orbital mounting plate {side}']
        cutter = bpy.data.objects.new(f'Temporary V7 mounting clearance {side}', mount.data.copy())
        bpy.context.scene.collection.objects.link(cutter)
        cutter.matrix_world = mount.matrix_world.copy()
        bm = bmesh.new()
        bm.from_mesh(cutter.data)
        bm.normal_update()
        for vertex in bm.verts:
            vertex.co += vertex.normal * .001
        bm.to_mesh(cutter.data)
        bm.free()
        modifier = brow.modifiers.new('Frozen mounting-bed clearance', 'BOOLEAN')
        modifier.operation = 'DIFFERENCE'
        modifier.solver = 'EXACT'
        modifier.object = cutter
        bpy.context.view_layer.objects.active = brow
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bpy.data.objects.remove(cutter, do_unlink=True)
        changed.append(brow.name)
        bm = bmesh.new()
        bm.from_mesh(brow.data)
        unseen = set(bm.verts)
        components = []
        while unseen:
            todo = [unseen.pop()]
            count = 0
            while todo:
                vertex = todo.pop()
                count += 1
                for edge in vertex.link_edges:
                    other = edge.other_vert(vertex)
                    if other in unseen:
                        unseen.remove(other)
                        todo.append(other)
            components.append(count)
        row = {'name': brow.name, 'vertices': len(bm.verts), 'faces': len(bm.faces),
               'nonManifoldEdges': sum(not edge.is_manifold for edge in bm.edges),
               'connectedComponentVertexCounts': components}
        assert not row['nonManifoldEdges'] and len(components) == 1, row
        topology.append(row)
        bm.free()
    bpy.context.view_layer.update()
    after = h['scene_snapshot']()
    assert before['empties'] == after['empties'] and before['curves'] == after['curves']
    assert set(before['meshes']) == set(after['meshes'])
    for name, signature in before['meshes'].items():
        if name not in changed:
            assert after['meshes'][name] == signature, name
    OUT.mkdir(parents=True)
    AUDIT.mkdir(parents=True)
    native = OUT / 'murderbird-orbital-saddle-study-v7.blend'
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(native), check_existing=False)
    bpy.ops.wm.open_mainfile(filepath=str(native))
    assert h['scene_snapshot']() == after
    shutil.copy2(__file__, AUDIT / 'executed-generator.py')
    receipt = {'status': 'unreviewed brow/bed fit proposal; not selected',
               'base': artifact(BASE), 'native': artifact(native), 'generator': artifact(AUDIT / 'executed-generator.py'),
               'changedMeshes': changed, 'topology': topology,
               'construction': 'Difference against fixed mounting bed with nominal 1mm normal expansion; applied once to rigid brow',
               'preservation': {'other697MeshesExact': True, '51PivotsAnd462GuidesExact': True,
                                'saveReloadExact': True, 'noLiveBooleanOrCutter': True},
               'limits': ['Nominal construction offset is not a verified minimum gap.',
                          'This fitted seam is a reconstruction, not a measured reference detail.',
                          'Opening clearance and retained pin seating remain unverified.',
                          'No export, app selection, owner acceptance or publication.']}
    (AUDIT / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    render = runpy.run_path(str(ROOT / 'scripts/study-v8-bill-envelope.py'), run_name='renderer')['renders']
    render.__globals__['AUDIT'] = AUDIT
    receipt['views'] = render(BASE, 'before') + render(native, 'after')
    (AUDIT / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(artifact(native)))

if __name__ == '__main__':
    main()
