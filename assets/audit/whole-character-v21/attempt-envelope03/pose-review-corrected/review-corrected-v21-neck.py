"""Corrected in-memory neck pose renders and focused V21 cervical BVH screen."""
from pathlib import Path
import datetime
import hashlib
import json
import math
import shutil

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
NATIVE = ROOT / 'assets/models/whole-character-v21/attempt-envelope03/murderbird-whole-character-v21.blend'
CONTRACT = ROOT / 'assets/audit/whole-character-v21/attempt-envelope03/construction-contract.json'
EXPECTED_NATIVE = '720c343645ef2de298a50e53c82fad66448c187b1eaf9311de2514cac079f280'
assert not (OUT / 'review.json').exists(), 'Refusing to overwrite this review'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def artifact(path):
    path = Path(path)
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'bytes': path.stat().st_size}


def clear_in_memory_animation(scene):
    cleared = []
    for obj in bpy.data.objects:
        if obj.animation_data is not None:
            obj.animation_data_clear()
            cleared.append(f'object:{obj.name}')
        data = getattr(obj, 'data', None)
        if data is not None and hasattr(data, 'animation_data') and data.animation_data is not None:
            data.animation_data_clear()
            cleared.append(f'data:{data.name}')
    if scene.animation_data is not None:
        scene.animation_data_clear()
        cleared.append(f'scene:{scene.name}')
    return cleared


def pose_rotations(pivots, pitch):
    for name in ('neck', 'cervical-upper', 'head'):
        pivots[name].rotation_euler = (0.0, 0.0, 0.0)
    pivots['neck'].rotation_euler.x = .35 * pitch
    pivots['cervical-upper'].rotation_euler.x = .65 * pitch
    pivots['head'].rotation_euler.x = -pitch
    bpy.context.view_layer.update()


def world_x_degrees(obj):
    return math.degrees(obj.matrix_world.to_quaternion().to_euler('XYZ').x)


def mesh_tree(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles()
        matrix = evaluated.matrix_world
        vertices = [matrix @ vertex.co for vertex in mesh.vertices]
        polygons = [tuple(tri.vertices) for tri in mesh.loop_triangles]
        if len(polygons) < 4:
            return None, vertices
        return BVHTree.FromPolygons(vertices, polygons, all_triangles=True), vertices
    finally:
        evaluated.to_mesh_clear()


def overlap_screen(contract, pose_id):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    added = [item for item in contract['added'] if item['owner'] in ('neck', 'cervical-upper')]
    groups = {'neck': [], 'cervical-upper': []}
    for item in added:
        obj = bpy.data.objects.get(item['name'])
        assert obj is not None and obj.type == 'MESH', f"Missing new mesh {item['name']}"
        tree, vertices = mesh_tree(obj, depsgraph)
        if tree is not None:
            lo = [min(float(v[i]) for v in vertices) for i in range(3)]
            hi = [max(float(v[i]) for v in vertices) for i in range(3)]
            groups[item['owner']].append((item, tree, lo, hi))

    pairs = []
    for a in groups['neck']:
        for b in groups['cervical-upper']:
            if any(a[3][axis] < b[2][axis] or b[3][axis] < a[2][axis] for axis in range(3)):
                continue
            hits = a[1].overlap(b[1])
            if not hits:
                continue
            names = {a[0]['name'], b[0]['name']}
            pairs.append({
                'lowerOwnerMesh': a[0]['name'], 'upperOwnerMesh': b[0]['name'],
                'lowerRole': a[0].get('role'), 'upperRole': b[0].get('role'),
                'intersectingTrianglePairs': len(hits),
                'classification': 'unresolved rigid inter-owner surface intersection; no lap/contact exemption applied',
            })
    pairs.sort(key=lambda row: row['intersectingTrianglePairs'], reverse=True)
    return {'poseId': pose_id, 'testedNewNeckOwnerMeshes': sum(map(len, groups.values())),
            'lowerOwnerMeshCount': len(groups['neck']), 'upperOwnerMeshCount': len(groups['cervical-upper']),
            'interOwnerIntersectingMeshPairCount': len(pairs), 'intersections': pairs}


def main():
    assert NATIVE.is_file() and sha(NATIVE) == EXPECTED_NATIVE, 'Pinned V21 native missing/hash mismatch'
    assert CONTRACT.is_file()
    contract = json.loads(CONTRACT.read_text())
    script_copy = OUT / 'executed-review-corrected-v21-neck.py'
    shutil.copy2(__file__, script_copy)

    bpy.ops.wm.open_mainfile(filepath=str(NATIVE))
    scene = bpy.context.scene
    animation_cleared = clear_in_memory_animation(scene)
    scene.frame_set(1)
    bpy.context.view_layer.update()
    pivots = {name: bpy.data.objects[name] for name in ('neck', 'cervical-upper', 'head')}
    assert all(tuple(round(v, 6) for v in p.rotation_euler) == (0.0, 0.0, 0.0) for p in pivots.values())

    scene.render.engine = 'BLENDER_WORKBENCH'
    shading = scene.display.shading
    shading.light = 'STUDIO'
    shading.studio_light = 'paint.sl'
    shading.color_type = 'SINGLE'
    shading.single_color = (.56, .58, .60)
    shading.show_shadows = False
    shading.show_cavity = True
    shading.cavity_type = 'BOTH'
    shading.background_type = 'WORLD'
    scene.world.color = (.12, .13, .14)
    scene.render.resolution_x = scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    for obj in bpy.data.objects:
        if obj.type == 'CURVE':
            obj.hide_render = True

    camera_data = bpy.data.cameras.new('Temporary corrected cervical review camera')
    camera_data.type = 'ORTHO'
    camera_data.ortho_scale = 1.55
    camera = bpy.data.objects.new(camera_data.name, camera_data)
    scene.collection.objects.link(camera)
    camera.location = (-2.15, -2.9, 2.05)
    target = Vector((0.0, -.24, 1.43))
    camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = camera

    poses = [
        ('rest', 0.0, {'neck': 0.0, 'cervical-upper': 0.0, 'head': 0.0}),
        ('corrected-dip-plus-065', .65, {'neck': .2275, 'cervical-upper': .4225, 'head': -.65}),
        ('corrected-extension-minus-065', -.65, {'neck': -.2275, 'cervical-upper': -.4225, 'head': .65}),
    ]
    renders = []
    clear_before_override = clear_in_memory_animation(scene)
    for pose_id, pitch, local_expected in poses:
        clear_in_memory_animation(scene)
        pose_rotations(pivots, pitch)
        pre_render_world = {name: world_x_degrees(obj) for name, obj in pivots.items()}
        expected_world = {'neck': math.degrees(.35 * pitch),
                          'cervical-upper': math.degrees(pitch), 'head': 0.0}
        pre_error = max(abs(pre_render_world[name] - expected_world[name]) for name in expected_world)
        assert pre_error < .02, f'{pose_id} pre-render world rotation error: {pre_error}'
        intersections = overlap_screen(contract, pose_id)
        image = OUT / f'{pose_id}.png'
        assert not image.exists(), f'Refusing to overwrite {image}'
        scene.render.filepath = str(image)
        bpy.ops.render.render(write_still=True)
        post_render_world = {name: world_x_degrees(obj) for name, obj in pivots.items()}
        post_error = max(abs(post_render_world[name] - expected_world[name]) for name in expected_world)
        assert post_error < .02, f'{pose_id} pose changed during render evaluation: {post_error}'
        renders.append({
            'id': pose_id, 'requestedLocalX': local_expected,
            'actualWorldXDegreesBeforeRender': pre_render_world,
            'actualWorldXDegreesAfterRender': post_render_world,
            'expectedWorldXDegrees': expected_world,
            'maxWorldRotationErrorDegreesAfterRender': post_error,
            'interOwnerSurfaceScreen': intersections,
            'image': artifact(image),
        })

    bpy.data.objects.remove(camera, do_unlink=True)
    bpy.data.cameras.remove(camera_data)
    result = {
        'schema': 'whole-character-v21-corrected-neck-pose-review/v1',
        'status': 'three corrected in-memory authoring poses; no runtime or engineering acceptance',
        'generatedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'native': artifact(NATIVE), 'constructionContract': artifact(CONTRACT),
        'reviewScript': artifact(Path(__file__).resolve()), 'executedReviewScript': artifact(script_copy),
        'blenderVersion': bpy.app.version_string,
        'animationDataClearedInMemory': animation_cleared,
        'animationDataClearedImmediatelyBeforePoseOverrides': clear_before_override,
        'poses': renders,
        'collisionMethod': 'Pairwise BVH triangle-face overlap of evaluated new V21 neck/cervical-upper meshes in world space at three discrete poses.',
        'limits': [
            'Earlier envelope03 native-dip image is not reliable head-angle evidence because frame evaluation reset inherited head animation before the pose was applied.',
            'Animation clearing and pose changes occurred in memory only; source native was not saved or exported.',
            'BVH reports triangle intersection candidates, not penetration depth, continuous clearance, joint friction, or physical support.',
            'Named throat/nape underlaps are flagged as designed lap candidates, but the screen does not grant them acceptance.',
            'Only new meshes owned by neck and cervical-upper were compared; surrounding body, breast, head, and runtime collisions are outside scope.',
        ],
    }
    path = OUT / 'review.json'
    path.write_text(json.dumps(result, indent=2) + '\n')
    assert sha(NATIVE) == EXPECTED_NATIVE, 'Native input changed during in-memory review'
    print(json.dumps({'review': artifact(path), 'renders': [row['image'] for row in renders],
                      'poseIntersectionCounts': [row['interOwnerSurfaceScreen']['interOwnerIntersectingMeshPairCount'] for row in renders]}, indent=2))


main()
