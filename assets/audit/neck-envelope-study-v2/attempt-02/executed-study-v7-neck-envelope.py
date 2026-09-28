"""Create one native-only, bounded cervical-envelope proposal from frozen V7.

Only existing neck guard/lamina mesh coordinates are shaped in place. Object
ownership, pivots, materials, modifiers, curve guides, and every other mesh are
held fixed. The dimensions are an authored study, not measurements of art.
"""
from pathlib import Path
import datetime
import hashlib
import json
import math
import ast
import shutil

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'assets/models/uncaged-alignment-v7/murderbird-alignment-v7.blend'
POSES = ROOT / 'assets/audit/neutral-runtime-clearance-poses-v1/pose-snapshot.json'
BASE_OUT = ROOT / 'assets/models/uncaged-neck-envelope-study-v2'
BASE_AUDIT = ROOT / 'assets/audit/neck-envelope-study-v2'
OUT = BASE_OUT / 'attempt-02'
AUDIT = BASE_AUDIT / 'attempt-02'
SHARED_VALIDATOR = ROOT / 'scripts/build-uncaged-alignment-v7.py'
EXPECTED_SOURCE = 'a8fccaf024a096678415215029b34cae8270b348da2301b8872a34e72c75ed3f'
EXPECTED_POSES = '874396ede48a63d37d743a1a85ae885a10e614a4461f46c50f3a62744a9e2813'
EXPECTED_GLB = '1c82874b86af6b493ac380536de6af72a30fafa3a4b0ebb3d8790f56ffc03018'
EXPECTED_VALIDATOR = '39b6ee2285d8c49df3a902f8fac0a07589da3d41f48ae24df1e06515c839033a'
POSE_IDS = ('inspection-open-0-separation-0', 'advanced-strike-peak')
TARGETS = {
    'Cervical articulated inner guards',
    *(f'Throat formed lamina {i}' for i in range(1, 7)),
    *(f'Cervical flank lamina {side} {i}' for side in (-1, 1) for i in range(1, 7)),
}
RESOLUTION = 1100
ORTHO = 1.18
C = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1)))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def converted(flat):
    browser = Matrix([[flat[col * 4 + row] for col in range(4)] for row in range(4)])
    return C.inverted() @ browser @ C


def depth(obj):
    n = 0
    while obj.parent is not None:
        n += 1
        obj = obj.parent
    return n


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def center_y(z):
    """Interpolated centerline from the authored V5 neck-envelope stations."""
    knots = ((1.25, -.095), (1.325, -.15), (1.41, -.23), (1.48, -.283),
             (1.55, -.253), (1.60, -.218), (1.65, -.200))
    if z <= knots[0][0]:
        return knots[0][1]
    if z >= knots[-1][0]:
        return knots[-1][1]
    for (za, ya), (zb, yb) in zip(knots, knots[1:]):
        if za <= z <= zb:
            t = (z - za) / (zb - za)
            return ya + (yb - ya) * t


def shape_point(p):
    # Taper only the inferior cervical envelope. The weight reaches zero above
    # z=1.48m, preserving the head-side roots. X modestly narrows the lower
    # outline; Y reduces depth and eases the transition into the breast.
    w = 1.0 - smooth((p.z - 1.245) / (1.48 - 1.245))
    if w <= 0.0:
        return p.copy()
    x = p.x * (1.0 - .075 * w)
    # The runtime neck pivot contributes y=-.1m to the local envelope center.
    cy = center_y(p.z) - .1
    y = cy + (p.y - cy) * (1.0 - .11 * w) + .004 * w
    return Vector((x, y, p.z))


def set_pose(pose, pivots):
    rows = {}
    for row in pose['pivotMatrices']:
        if row.get('kind') != 'mesh':
            rows.setdefault(row['name'], []).append(row)
    assert set(pivots) <= set(rows), f"pose missing pivots: {sorted(set(pivots)-set(rows))}"
    assert all(len(rows[n]) == 1 for n in pivots), 'ambiguous pose pivot names'
    for name in sorted(pivots, key=lambda n: depth(pivots[n])):
        pivots[name].matrix_world = converted(rows[name][0]['worldMatrix'])
        bpy.context.view_layer.update()
    err = max(abs(pivots[n].matrix_world[r][c] - converted(rows[n][0]['worldMatrix'])[r][c])
              for n in pivots for r in range(4) for c in range(4))
    assert err < 2e-6, f"matrix application mismatch for {pose['id']}: {err}"
    return err


def configure(scene):
    scene.render.engine = 'BLENDER_WORKBENCH'
    shade = scene.display.shading
    shade.light = 'STUDIO'
    shade.studio_light = 'paint.sl'
    shade.color_type = 'SINGLE'
    shade.single_color = (.52, .55, .57)
    shade.show_shadows = True
    shade.show_cavity = True
    shade.cavity_type = 'BOTH'
    shade.curvature_ridge_factor = 1.2
    shade.curvature_valley_factor = 1.1
    shade.background_type = 'WORLD'
    scene.world.color = (.12, .13, .14)
    scene.render.resolution_x = scene.render.resolution_y = RESOLUTION
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.film_transparent = False


def mesh_signature(obj):
    return {
        'name': obj.name,
        'type': obj.type,
        'dataName': obj.data.name if obj.data else None,
        'vertexCount': len(obj.data.vertices) if obj.type == 'MESH' else None,
        'polygonCount': len(obj.data.polygons) if obj.type == 'MESH' else None,
        'materials': [m.name if m else None for m in obj.data.materials] if obj.type == 'MESH' else [],
        'parent': obj.parent.name if obj.parent else None,
        'matrixWorld': [list(row) for row in obj.matrix_world],
        'modifiers': [(m.name, m.type) for m in obj.modifiers],
    }


def load_shared_snapshot_functions():
    """Use the exact V7 snapshot implementation without executing its builder."""
    assert sha(SHARED_VALIDATOR) == EXPECTED_VALIDATOR, 'shared V7 validator source changed'
    tree = ast.parse(SHARED_VALIDATOR.read_text())
    wanted = {'require', 'matrix_values', 'material_signature', 'mesh_signature',
              'modifier_signature', 'curve_signature', 'id_properties', 'scene_snapshot'}
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in wanted]
    assert {node.name for node in nodes} == wanted
    module = ast.Module(body=nodes, type_ignores=[])
    scope = {'bpy': bpy, 'json': json, 'hashlib': hashlib}
    exec(compile(module, str(SHARED_VALIDATOR), 'exec'), scope)
    return scope


def main():
    assert sha(SOURCE) == EXPECTED_SOURCE, 'frozen V7 native hash mismatch'
    assert sha(POSES) == EXPECTED_POSES, 'runtime pose packet hash mismatch'
    assert not OUT.exists() and not AUDIT.exists(), 'preserve existing candidate/audit; no overwrite'
    pose_data = json.loads(POSES.read_text())
    assert pose_data['model']['sha256'] == EXPECTED_GLB
    pose_map = {p['id']: p for p in pose_data['poses']}
    assert all(pid in pose_map for pid in POSE_IDS)
    OUT.mkdir(parents=True)
    AUDIT.mkdir(parents=True)
    script_snapshot = AUDIT / 'executed-study-v7-neck-envelope.py'
    assert not script_snapshot.exists()
    shutil.copy2(Path(__file__).resolve(), script_snapshot)

    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene = bpy.context.scene
    scene.frame_set(1)
    helper = load_shared_snapshot_functions()
    source_snapshot = helper['scene_snapshot']()
    objects = {o.name: o for o in bpy.data.objects}
    assert TARGETS <= {o.name for o in objects.values()}, f'missing target owners: {sorted(TARGETS-{o.name for o in objects.values()})}'
    assert len(TARGETS) == 19
    target_objects = [objects[n] for n in sorted(TARGETS)]
    assert all(o.type == 'MESH' and o.parent and o.parent.name == 'neck' for o in target_objects)
    assert len([o for o in objects.values() if o.type == 'EMPTY']) == 51

    before_all = {o.name: mesh_signature(o) for o in bpy.data.objects}
    target_before = {n: before_all[n] for n in sorted(TARGETS)}
    target_materials = {m.name: helper['material_signature'](m) for o in target_objects for m in o.data.materials if m}
    orphan_names = ('Neutral / edge.001', 'Neutral / plate.001')
    orphan_before = {}
    for name in orphan_names:
        material = bpy.data.materials.get(name)
        assert material and material.users == 0 and not material.use_fake_user, f'expected confirmed source orphan: {name}'
        orphan_before[name] = helper['material_signature'](material)
        material.use_fake_user = True
    change_counts = {}
    changed_meshes = []
    max_delta = 0.0
    for obj in target_objects:
        inv = obj.matrix_world.inverted()
        changed = 0
        for v in obj.data.vertices:
            world = obj.matrix_world @ v.co
            shaped = shape_point(world)
            delta = (shaped - world).length
            max_delta = max(max_delta, delta)
            if delta > 1e-8:
                changed += 1
                v.co = inv @ shaped
        obj.data.update()
        change_counts[obj.name] = {'changedVertices': changed, 'vertexCount': len(obj.data.vertices)}
        if changed > 0:
            changed_meshes.append(obj.name)
    assert max_delta > .002 and max_delta < .05, f'unexpected authored displacement bound {max_delta}'

    # Ensure only target coordinate datasets changed before saving.
    for name, old in before_all.items():
        obj = objects[name]
        now = mesh_signature(obj)
        if name in changed_meshes:
            assert old != now, f'eligible target mesh remained unchanged: {name}'
        else:
            assert old == now, f'unrelated mesh changed: {name}'
    assert target_materials == {m.name: helper['material_signature'](m) for o in target_objects for m in o.data.materials if m}
    assert orphan_before == {name: helper['material_signature'](bpy.data.materials[name]) for name in orphan_names}
    assert all(bpy.data.materials[name].use_fake_user for name in orphan_names)
    after_shape_snapshot = helper['scene_snapshot']()
    assert source_snapshot['empties'] == after_shape_snapshot['empties'], 'pivot matrices/properties/visibility changed'
    assert source_snapshot['curves'] == after_shape_snapshot['curves'], 'curves/guides changed'
    assert set(source_snapshot['meshes']) == set(after_shape_snapshot['meshes']), 'object inventory changed'
    for name in source_snapshot['meshes']:
        if name in changed_meshes:
            a, b = source_snapshot['meshes'][name], after_shape_snapshot['meshes'][name]
            assert a['mesh'] != b['mesh'] and {k:v for k,v in a.items() if k != 'mesh'} == {k:v for k,v in b.items() if k != 'mesh'}
        else:
            assert source_snapshot['meshes'][name] == after_shape_snapshot['meshes'][name], f'unrelated mesh snapshot changed: {name}'

    target_path = OUT / 'murderbird-neck-envelope-study-v2.blend'
    assert not target_path.exists()
    bpy.ops.wm.save_as_mainfile(filepath=str(target_path))
    native_sha = sha(target_path)

    expected_saved_snapshot = after_shape_snapshot
    bpy.ops.wm.open_mainfile(filepath=str(target_path))
    scene = bpy.context.scene
    helper = load_shared_snapshot_functions()
    reload_snapshot = helper['scene_snapshot']()
    assert reload_snapshot == expected_saved_snapshot, 'saved/reopened scene differs from exact pre-save expected snapshot'
    for name in orphan_names:
        assert bpy.data.materials[name].use_fake_user and helper['material_signature'](bpy.data.materials[name]) == orphan_before[name]

    # Render-only in-memory inspection of the saved candidate.
    configure(scene)
    # Apply public-era visibility only after the saved native has passed reload
    # parity. These are temporary in-memory render settings and are not saved.
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            eras = [x.strip() for x in obj.get('exteriorEras', 'maker,mechanic,builder').split(',')]
            obj.hide_render = 'builder' not in eras
            obj.hide_set(False)
    camera_data = bpy.data.cameras.new('Temporary neck study camera')
    camera = bpy.data.objects.new('Temporary neck study camera', camera_data)
    scene.collection.objects.link(camera)
    images = []
    pose_records = []
    for pose_id, view in ((POSE_IDS[0], 'side'), (POSE_IDS[1], 'three-quarter')):
        pose = pose_map[pose_id]
        matrix_error = set_pose(pose, {o.name: o for o in bpy.data.objects if o.type == 'EMPTY'})
        target = (bpy.data.objects['neck'].matrix_world.translation +
                  bpy.data.objects['breastplate'].matrix_world.translation) * .5
        offset = Vector((-5.5, 0, .15)) if view == 'side' else Vector((-3.65, -4.8, 1.45))
        camera.location = target + offset
        camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
        camera_data.type = 'ORTHO'
        camera_data.ortho_scale = ORTHO
        scene.camera = camera
        bpy.context.view_layer.update()
        out = AUDIT / f'{pose_id}-{view}.png'
        assert not out.exists()
        scene.render.filepath = str(out)
        bpy.ops.render.render(write_still=True)
        images.append({'path': str(out.relative_to(ROOT)), 'sha256': sha(out), 'bytes': out.stat().st_size,
                       'poseId': pose_id, 'view': view, 'resolution': [RESOLUTION, RESOLUTION],
                       'cameraWorld': [list(r) for r in camera.matrix_world],
                       'targetWorld': list(target), 'orthoScale': ORTHO})
        pose_records.append({'id': pose_id, 'controller': pose['controller'],
                             'pivotMatrixMaxError': matrix_error})
    bpy.data.objects.remove(camera, do_unlink=True)
    bpy.data.cameras.remove(camera_data)

    result = {
        'schema': 'native-neck-envelope-study/v2',
        'status': 'authored geometry proposal; not owner accepted',
        'createdAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'source': {'path': str(SOURCE.relative_to(ROOT)), 'sha256': EXPECTED_SOURCE,
                   'bytes': SOURCE.stat().st_size},
        'posePacket': {'path': str(POSES.relative_to(ROOT)), 'sha256': EXPECTED_POSES,
                       'declaredGlbSha256': EXPECTED_GLB},
        'candidate': {'path': str(target_path.relative_to(ROOT)), 'sha256': native_sha,
                      'bytes': target_path.stat().st_size},
        'script': {'path': str(script_snapshot.relative_to(ROOT)), 'sha256': sha(script_snapshot),
                   'workingPath': str(Path(__file__).resolve().relative_to(ROOT)), 'workingSha256': sha(Path(__file__).resolve())},
        'blenderVersion': bpy.app.version_string,
        'scope': {'eligibleMeshes': sorted(TARGETS), 'changedMeshes': sorted(changed_meshes), 'addedObjects': [], 'deletedObjects': [],
                  'changedTransforms': [], 'changedPivots': [], 'changedMaterials': [],
                  'changedCurves': [], 'curvesPreservedAsInheritedGuides': True,
                  'method': 'In-place world-coordinate transformation of existing mesh vertices; smooth height-weighted inferior taper using the parent neck pivot offset. No nearest-normal projection or topology edits.',
                  'changedVerticesByMesh': change_counts, 'maximumVertexDisplacementMeters': max_delta},
        'preservation': {'sharedSnapshotHelper': {'path': str(SHARED_VALIDATOR.relative_to(ROOT)), 'sha256': EXPECTED_VALIDATOR},
                         'sourceSnapshotExact': True, 'postShapeSnapshotDiffLimitedToTargetMeshData': True,
                         'reopenedNativeSnapshotExact': True,
                         'orphanMaterialsRetainedWithFakeUser': orphan_names,
                         'savedNativeVisibilityPreserved': True,
                         'renderEraVisibilityAppliedOnlyAfterSaveAndReloadCheck': True},
        'visualReview': {'poses': pose_records, 'renders': images,
                         'engine': 'Workbench neutral single color', 'camera': 'matched to baseline review settings',
                         'nativeSavedBeforeTemporaryPoseAndRender': True},
        'limits': ['Candidate03 guides shape direction only; no dimensions were measured from it.',
                   'Two stills only; not a complete pose or contact validation.',
                   'Runtime geometry clearance checks against the 17-pose packet are pending.',
                   'No GLB export, browser/WebGL test, human owner approval, or artistic acceptance.']
    }
    receipt = AUDIT / 'study-manifest.json'
    assert not receipt.exists()
    receipt.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': 'candidate-saved', 'path': str(target_path), 'sha256': native_sha,
                      'maxDisplacementM': max_delta, 'images': [x['path'] for x in images]}))


if __name__ == '__main__':
    main()
