"""Read-only frozen supplement native binding proof. No scene/save/render edits."""
import bpy
import hashlib
import json
from pathlib import Path
import datetime
import sys

ROOT = Path('/Users/okh/.codex/worktrees/cg-supervised-finish04/murderbird-uncaged')
AUDIT = ROOT / 'assets/audit/cg-recursive-finish04-crown'
SOURCE = 'CGH17 frontal crown root'
SUCCESSOR = 'CGRS04 source-scale frontal crown appearance'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mesh_arrays(mesh):
    return {'positions': [list(v.co) for v in mesh.vertices], 'polygons': [list(p.vertices) for p in mesh.polygons], 'face_slots': [p.material_index for p in mesh.polygons], 'uv': [(u.name, [list(c.uv) for c in u.data]) for u in mesh.uv_layers]}


def run():
    report = {'status': 'IN_PROGRESS', 'scope': 'Saved native read-only original/evaluated crown DATA bindings and packed bytes; no apply/edit/save/render/export', 'at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'eras': {}}
    for era in ('maker', 'mechanic', 'builder'):
        base = AUDIT / ('supplement05-' + era) / era
        receipt = json.loads((base / 'receipt.json').read_text())
        if receipt['status'] != 'PASS':
            raise RuntimeError('Supplement receipt not complete')
        native = Path(receipt['native_path'])
        before = sha(native)
        if before != receipt['native_sha256']:
            raise RuntimeError('Frozen native hash differs')
        bpy.ops.wm.open_mainfile(filepath=str(native))
        scene = bpy.context.scene
        original = scene.objects[SOURCE]
        successor = scene.objects[SUCCESSOR]
        expected = next(iter(receipt['module_results'].values()))
        material = successor.data.materials[2]
        predicates = {'exact_cage_uv_face_slot_arrays': mesh_arrays(original.data) == mesh_arrays(successor.data), 'exact_world_matrix': original.matrix_world == successor.matrix_world, 'same_parent': original.parent == successor.parent, 'source_render_hidden': original.hide_render, 'source_layer_hidden': original.hide_get(), 'source_global_viewport_held': not original.hide_viewport, 'successor_render_visible': not successor.hide_render, 'successor_DATA_slot2': successor.material_slots[2].link == 'DATA', 'slot0_original_reference': successor.data.materials[0] == original.data.materials[0], 'slot1_original_reference': successor.data.materials[1] == original.data.materials[1]}
        evaluated = successor.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh()
        try:
            em = mesh.materials[2]
            predicates['evaluated_faces1912'] = len(mesh.polygons) == 1912
            predicates['evaluated_allslot2'] = all(p.material_index == 2 for p in mesh.polygons)
            predicates['evaluated_material_original_identity'] = em.original == material.original
            bindings = []
            for record in expected['newMaps']:
                role = record['role']
                im = em.node_tree.nodes['CGRS04 ' + role].image
                direct = material.node_tree.nodes['CGRS04 ' + role].image
                actual = hashlib.sha256(im.packed_file.data).hexdigest() if im.packed_file else None
                predicates[role + '_packed_bytes'] = actual == record['sha256'] == sha(Path(record['path']))
                predicates[role + '_original_ID'] = im.original == direct.original
                predicates[role + '_FILE_source'] = im.source == 'FILE'
                predicates[role + '_colorspace'] = im.colorspace_settings.name == ('sRGB' if role == 'basecolor' else 'Non-Color')
                bindings.append({'role': role, 'image': im.name, 'original_image': im.original.name, 'packed_sha256': actual, 'expected_sha256': record['sha256'], 'colorspace': im.colorspace_settings.name, 'source': im.source})
            original_normal = original.material_slots[2].material.node_tree.nodes['Image Texture.002'].image
            predicates['normal_exact_held_source_bytes'] = next(x['packed_sha256'] for x in bindings if x['role'] == 'normal') == hashlib.sha256(original_normal.packed_file.data).hexdigest()
            counts = {'mesh_empty': sum(o.type in ('MESH', 'EMPTY') for o in scene.objects), 'meshes': sum(o.type == 'MESH' for o in scene.objects), 'empties': sum(o.type == 'EMPTY' for o in scene.objects), 'materials': len(bpy.data.materials), 'FILE_images': sum(i.source == 'FILE' for i in bpy.data.images), 'packed_FILE_images': sum(i.source == 'FILE' and bool(i.packed_file) for i in bpy.data.images)}
            expected_counts = {'mesh_empty': 7690, 'meshes': 7681, 'empties': 9, 'materials': 63, 'FILE_images': 164 if era == 'builder' else 163, 'packed_FILE_images': 164 if era == 'builder' else 163}
            predicates['exact_added_resource_counts'] = counts == expected_counts
        finally:
            evaluated.to_mesh_clear()
        predicates['native_bytes_unchanged_by_readback'] = sha(native) == before
        report['eras'][era] = {'native_sha256': before, 'counts': counts, 'expected_counts': expected_counts, 'predicates': predicates, 'bindings': bindings}
        print('SUPPLEMENT05_NATIVE_READBACK', era, predicates, flush=True)
        if not all(predicates.values()):
            report['status'] = 'FAIL'; (AUDIT / 'supplement05-packed-map-readback.json').write_text(json.dumps(report, indent=2) + '\n')
            raise RuntimeError('Saved binding predicate failed; no repairs allowed')
    report['status'] = 'PASS'
    (AUDIT / 'supplement05-packed-map-readback.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    try:
        run()
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)
