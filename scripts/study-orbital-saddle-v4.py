"""Four-part rigid correction of V3's orbital/temporal interference.

This is an isolated proposal. It preserves V3, cuts real relief in the two
moving temporal plates and relocates two retained pins onto exposed saddles.
Construction cutters are applied once and removed before saving or posing.
"""
from pathlib import Path
import hashlib, json, runpy, shutil
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'assets/models/uncaged-orbital-saddle-study-v3/murderbird-orbital-saddle-study-v3.blend'
OUT = ROOT / 'assets/models/uncaged-orbital-saddle-study-v4'
AUDIT = ROOT / 'assets/audit/orbital-saddle-study-v4'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def artifact(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path), 'bytes': path.stat().st_size}

def main():
    assert sha(BASE) == '37571798a49747c65014000f01e2ae19332cf49249dc8b0040d8c6af7e766b49'
    assert not OUT.exists() and not AUDIT.exists(), 'Preserve existing versions'
    h = runpy.run_path(str(ROOT / 'scripts/build-uncaged-alignment-v7.py'), run_name='helpers')
    bpy.ops.wm.open_mainfile(filepath=str(BASE))
    before = h['scene_snapshot']()
    changes = []
    for side in (-1, 1):
        brow = bpy.data.objects[f'Forged orbital brow {side}']
        temporal = bpy.data.objects[f'Swept temporal lamina {side} 0 0']
        cutter = bpy.data.objects.new(f'Temporary V4 saddle relief {side}', brow.data.copy())
        bpy.context.scene.collection.objects.link(cutter)
        cutter.matrix_world = brow.matrix_world.copy()
        bm = bmesh.new()
        bm.from_mesh(cutter.data)
        bm.normal_update()
        for vertex in bm.verts:
            vertex.co += vertex.normal * .002
        bm.to_mesh(cutter.data)
        bm.free()
        modifier = temporal.modifiers.new('Frozen V4 saddle relief', 'BOOLEAN')
        modifier.operation = 'DIFFERENCE'
        modifier.solver = 'EXACT'
        modifier.object = cutter
        bpy.context.view_layer.objects.active = temporal
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bpy.data.objects.remove(cutter, do_unlink=True)
        changes.append({'name': temporal.name, 'operation': 'Rigid relief against V3 saddle with nominal 2mm vertex-normal expansion; applied once'})

        pin = bpy.data.objects[f'Orbital mounting fixing {side} 3']
        matrix = pin.matrix_world.copy()
        inverse = matrix.inverted()
        points = [matrix @ vertex.co for vertex in pin.data.vertices]
        centre = sum(points, Vector()) / len(points)
        # The previous station sat under the moving temporal plate. Move this
        # retained pin forward on the fixed saddle, preserving shape and axis.
        translation = Vector((0, -.382 - centre.y, 1.879 - centre.z))
        points = [point + translation for point in points]
        tree = BVHTree.FromPolygons(
            [brow.matrix_world @ vertex.co for vertex in brow.data.vertices],
            [tuple(face.vertices) for face in brow.data.polygons])
        hit, _, _, _ = tree.ray_cast(Vector((side * .4, -.382, 1.879)), Vector((-side, 0, 0)), .4)
        assert hit is not None, ('No saddle surface for retained fixing', pin.name)
        outward_delta = side * hit.x - .001 - min(side * point.x for point in points)
        for vertex, point in zip(pin.data.vertices, points):
            point.x += side * outward_delta
            vertex.co = inverse @ point
        pin.data.update()
        changes.append({'name': pin.name, 'operation': 'Rigid pin translation to exposed fixed saddle',
                        'oldCentreWorldXYZ': list(centre), 'newAxisWorldYZ': [-.382, 1.879],
                        'surfaceHitWorldXYZ': list(hit), 'nominalBaseEmbedM': .001})

    bpy.context.view_layer.update()
    after = h['scene_snapshot']()
    allowed = {row['name'] for row in changes}
    assert before['empties'] == after['empties'] and before['curves'] == after['curves']
    for name, signature in before['meshes'].items():
        if name not in allowed:
            assert after['meshes'][name] == signature, name
    assert set(before['meshes']) == set(after['meshes'])
    topology = []
    for name in sorted(allowed):
        obj = bpy.data.objects[name]
        assert not any(mod.type == 'BOOLEAN' for mod in obj.modifiers)
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        row = {'name': name, 'vertices': len(bm.verts), 'faces': len(bm.faces),
               'nonManifoldEdges': sum(not edge.is_manifold for edge in bm.edges),
               'looseVertices': sum(not vertex.link_faces for vertex in bm.verts)}
        assert not row['nonManifoldEdges'] and not row['looseVertices'], row
        topology.append(row)
        bm.free()
    OUT.mkdir(parents=True)
    AUDIT.mkdir(parents=True)
    native = OUT / 'murderbird-orbital-saddle-study-v4.blend'
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(native), check_existing=False)
    bpy.ops.wm.open_mainfile(filepath=str(native))
    assert h['scene_snapshot']() == after
    shutil.copy2(__file__, AUDIT / 'executed-generator.py')
    receipt = {'status': 'unreviewed four-part rigid correction; not selected', 'base': artifact(BASE),
               'native': artifact(native), 'generator': artifact(AUDIT / 'executed-generator.py'),
               'changes': changes, 'topology': topology,
               'preservation': {'untouchedMeshesExact': len(before['meshes']) - len(allowed),
                                '51PivotsAnd462GuidesExact': True, 'saveReloadExact': True,
                                'noConstructionCuttersOrBooleanDependencies': True},
               'limits': ['Nominal seam relief and fixing embed require evaluated clearance checks.',
                          'Reconstructed seams and fixing station are proposals, not recovered reference dimensions.',
                          'No export, app integration, surface finishing, publication or artistic acceptance.']}
    (AUDIT / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    render = runpy.run_path(str(ROOT / 'scripts/study-v8-bill-envelope.py'), run_name='renderer')['renders']
    render.__globals__['AUDIT'] = AUDIT
    receipt['views'] = render(BASE, 'before') + render(native, 'after')
    (AUDIT / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(artifact(native)))

if __name__ == '__main__':
    main()
