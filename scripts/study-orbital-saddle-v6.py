"""Isolated ownership proposal: removable brow/crown over a seated optic bed.

Preserve V4 geometry and its closed world-space appearance. A fixing follows
the rigid surface its axis actually meets; the optic/mounting bed stays fixed.
"""
from pathlib import Path
import hashlib, json, runpy, shutil
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'assets/models/uncaged-orbital-saddle-study-v4/murderbird-orbital-saddle-study-v4.blend'
OUT = ROOT / 'assets/models/uncaged-orbital-saddle-study-v6'
AUDIT = ROOT / 'assets/audit/orbital-saddle-study-v6'

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
    all_world = {o.name: o.matrix_world.copy() for o in bpy.data.objects}
    assignments = []
    for side in (-1, 1):
        brow = bpy.data.objects[f'Forged orbital brow {side}']
        mount = bpy.data.objects[f'Forged orbital mounting plate {side}']
        surfaces = {}
        for obj in (brow, mount):
            surfaces[obj.name] = BVHTree.FromPolygons(
                [obj.matrix_world @ vertex.co for vertex in obj.data.vertices],
                [tuple(face.vertices) for face in obj.data.polygons])
        selected = [brow]
        for pin in [o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith(f'Orbital mounting fixing {side} ')]:
            centre = sum((pin.matrix_world @ vertex.co for vertex in pin.data.vertices), Vector()) / len(pin.data.vertices)
            rays = []
            for name, tree in surfaces.items():
                hit, _, _, distance = tree.ray_cast(Vector((side * .4, centre.y, centre.z)), Vector((-side, 0, 0)), .4)
                if hit is not None:
                    rays.append((distance, name, hit))
            assert rays, ('No supporting surface on fixing axis', pin.name)
            distance, supporting_name, hit = min(rays, key=lambda row: row[0])
            follows_brow = supporting_name == brow.name
            assignments.append({'name': pin.name, 'surfaceOnOutwardAxis': supporting_name,
                                'hitWorldXYZ': list(hit), 'newOwner': 'cranial-cover' if follows_brow else pin.parent.name})
            if follows_brow:
                selected.append(pin)
        for obj in selected:
            matrix = obj.matrix_world.copy()
            obj.parent = bpy.data.objects['cranial-cover']
            obj.matrix_parent_inverse = Matrix.Identity(4)
            obj.matrix_world = matrix
            if obj == brow:
                assignments.append({'name': obj.name, 'newOwner': 'cranial-cover', 'reason': 'Removable brow/crown proposal'})
    bpy.context.view_layer.update()
    after = h['scene_snapshot']()
    changed = {row['name'] for row in assignments if row['newOwner'] == 'cranial-cover'}
    assert before['empties'] == after['empties'] and before['curves'] == after['curves']
    for name, signature in before['meshes'].items():
        if name not in changed:
            assert after['meshes'][name] == signature, name
        else:
            assert after['meshes'][name]['mesh'] == signature['mesh'], name
    maximum_error = max(max(abs(obj.matrix_world[r][c] - all_world[obj.name][r][c]) for r in range(4) for c in range(4)) for obj in bpy.data.objects)
    assert maximum_error < 2e-7
    OUT.mkdir(parents=True)
    AUDIT.mkdir(parents=True)
    native = OUT / 'murderbird-orbital-saddle-study-v6.blend'
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(native), check_existing=False)
    bpy.ops.wm.open_mainfile(filepath=str(native))
    assert h['scene_snapshot']() == after
    shutil.copy2(__file__, AUDIT / 'executed-generator.py')
    receipt = {'status': 'unreviewed inspection ownership proposal; not selected',
               'base': artifact(BASE), 'native': artifact(native), 'generator': artifact(AUDIT / 'executed-generator.py'),
               'assignments': assignments,
               'preservation': {'all699MeshGeometriesExact': True, 'allClosedWorldMatricesMaxErrorM': maximum_error,
                                '51PivotsAnd462GuidesExact': True, 'saveReloadExact': True},
               'limits': ['An axis hit identifies the candidate parent surface, not full fastening or clearance proof.',
                          'Brow/mount crossings already present at rest require separate treatment.',
                          'This ownership proposal does not erase inherited crown/nasal-hood opening conflicts.',
                          'No export, app selection, owner approval or publication.']}
    (AUDIT / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(artifact(native)))

if __name__ == '__main__':
    main()
