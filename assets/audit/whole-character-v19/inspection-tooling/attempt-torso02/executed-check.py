"""Check a V19 candidate's five zero-separation breast-opening samples.

This read-only Blender diagnostic re-derives the inspection rotation from the
candidate's own rest hierarchy. It does not replay older world matrices, save a
native, or prove continuous clearance/containment or artistic acceptance.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import shutil
import sys

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
C = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1)))
OPEN_VALUES = (0.0, 0.25, 0.5, 0.75, 1.0)
RIB_NAMES = ('Passive rib behind access cover.002', 'Passive rib behind access cover.003')
RAIL_NAMES = ('Curved thoracic load rail', 'Curved thoracic load rail.001')
NEIGHBOR_OWNERS = ('body', 'left-mantle', 'right-mantle', 'left-wing-shield', 'right-wing-shield')


def parse_args():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument('--native', required=True, help='Repository-relative candidate .blend')
    parser.add_argument('--sha256', required=True, help='Exact candidate SHA-256')
    parser.add_argument('--out', required=True, help='New repository-relative output directory')
    parser.add_argument('--render-open', action='store_true', help='Render full-open front and three-quarter native illustrations')
    args = parser.parse_args(argv)
    for key in ('native', 'out'):
        raw = Path(getattr(args, key))
        assert not raw.is_absolute(), f'--{key} must be repository-relative'
        path = (ROOT / raw).resolve()
        assert path == ROOT or ROOT in path.parents, f'--{key} escapes repository'
        setattr(args, key, path)
    return args


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def artifact(path):
    path = Path(path)
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'bytes': path.stat().st_size}


def converted(flat):
    browser = Matrix([[flat[col * 4 + row] for col in range(4)] for row in range(4)])
    return C.inverted() @ browser @ C


def depth(obj):
    return 0 if obj.parent is None else 1 + depth(obj.parent)


def surface(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        mesh.calc_loop_triangles()
        points = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
        faces = [tuple(tri.vertices) for tri in mesh.loop_triangles]
        if not points or not faces:
            return None
        return {
            'tree': BVHTree.FromPolygons(points, faces, all_triangles=True, epsilon=0.0),
            'points': points,
            'faces': faces,
            'min': [min(point[i] for point in points) for i in range(3)],
            'max': [max(point[i] for point in points) for i in range(3)],
        }
    finally:
        evaluated.to_mesh_clear()


def bounds_overlap(a, b):
    return all(a['min'][i] <= b['max'][i] and b['min'][i] <= a['max'][i] for i in range(3))


def add_render_camera(scene, offset, target, name):
    data = bpy.data.cameras.new(name)
    data.type = 'ORTHO'
    data.ortho_scale = 4.35
    data.clip_start, data.clip_end = .01, 100.0
    camera = bpy.data.objects.new(name, data)
    scene.collection.objects.link(camera)
    camera.location = target + Vector(offset)
    camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()
    return camera, data


def render_full_open(native, expected_native_sha, out, pivot, cover, rest_local, cover_rest_local):
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.render.resolution_x = scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.film_transparent = False
    scene.display.shading.light = 'STUDIO'
    scene.display.shading.studio_light = 'paint.sl'
    scene.display.shading.color_type = 'SINGLE'
    scene.display.shading.single_color = (.52, .55, .57)
    scene.display.shading.show_shadows = False
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = 'BOTH'
    scene.display.shading.curvature_ridge_factor = 1.15
    scene.display.shading.curvature_valley_factor = 1.05
    scene.display.shading.background_type = 'WORLD'
    scene.world.color = (.12, .13, .14)
    for obj in bpy.data.objects:
        if obj.type == 'CURVE':
            obj.hide_render = True
    set_runtime_open(pivot, cover, rest_local, cover_rest_local, 1.0)
    meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']
    original_hidden = {obj.name: bool(obj.hide_render) for obj in meshes}
    era = 'builder'
    visible = []
    for obj in meshes:
        eras = [value.strip() for value in obj.get('exteriorEras', 'maker,mechanic,builder').split(',')]
        obj.hide_render = original_hidden[obj.name] or era not in eras
        if not obj.hide_render:
            visible.append(obj)
    assert visible, 'No meshes visible in builder full-open review render'
    floor_mesh = bpy.data.meshes.new('Temporary V19 open review floor mesh')
    floor_mesh.from_pydata([(-30, -30, 0), (30, -30, 0), (30, 30, 0), (-30, 30, 0)], [], [(0, 1, 2, 3)])
    floor_mesh.update()
    floor = bpy.data.objects.new('Temporary V19 open review floor', floor_mesh)
    scene.collection.objects.link(floor)
    target = Vector((0.0, -0.05, 1.05))
    views = []
    for label, offset in (('front', (0.0, -4.5, .55)), ('three-quarter', (3.3, -4.0, 1.15))):
        camera, camera_data = add_render_camera(scene, offset, target, f'Temporary V19 open {label} camera')
        old_camera = scene.camera
        scene.camera = camera
        bpy.context.view_layer.update()
        path = out / f'inspection-open-1-{label}.png'
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        views.append({'view': label, 'image': artifact(path), 'era': era,
                      'open': 1.0, 'separation': 0.0, 'cameraOffsetNative': list(offset),
                      'cameraTargetNative': list(target), 'orthographicScaleM': 4.35,
                      'floor': 'temporary native Z=0 plane'})
        scene.camera = old_camera
        bpy.data.objects.remove(camera, do_unlink=True)
        bpy.data.cameras.remove(camera_data)
    bpy.data.objects.remove(floor, do_unlink=True)
    bpy.data.meshes.remove(floor_mesh)
    assert sha(native) == expected_native_sha, 'Candidate native changed during rendering'
    return {'status': 'native Workbench illustrations derived from runtime local inspection transform; not browser captures',
            'views': views, 'visibleMeshCount': len(visible), 'hiddenHistoricalCurveCount': sum(o.type == 'CURVE' for o in bpy.data.objects)}


def descendants(obj):
    result = []
    for candidate in bpy.data.objects:
        parent = candidate.parent
        while parent is not None:
            if parent == obj:
                result.append(candidate)
                break
            parent = parent.parent
    return result


def set_runtime_open(pivot, cover, rest_local, cover_rest_local, open_value):
    """Apply the production Three local rotation after native coordinate conversion.

    Runtime assigns `breastplate.rotation.y = -open * 1.35` (Euler XYZ),
    retaining its local position and scale. Under C, browser local Y maps to
    native local Z. The cranial cover's browser local +Y translation maps to
    native local +Z. Separation is deliberately zero for this checker.
    """
    browser_local = C @ rest_local @ C.inverted()
    location, quaternion, scale = browser_local.decompose()
    euler = quaternion.to_euler('XYZ')
    preserved = {'x': float(euler.x), 'z': float(euler.z)}
    euler.y = -1.35 * open_value
    new_browser = Matrix.Translation(location) @ euler.to_matrix().to_4x4() @ Matrix.Diagonal(
        (scale.x, scale.y, scale.z, 1.0))
    pivot.matrix_local = C.inverted() @ new_browser @ C

    cover_browser = C @ cover_rest_local @ C.inverted()
    cover_location, cover_quaternion, cover_scale = cover_browser.decompose()
    cover_euler = cover_quaternion.to_euler('XYZ')
    cover_location.y += 0.08 * open_value
    cover_new_browser = Matrix.Translation(cover_location) @ cover_euler.to_matrix().to_4x4() @ Matrix.Diagonal(
        (cover_scale.x, cover_scale.y, cover_scale.z, 1.0))
    cover.matrix_local = C.inverted() @ cover_new_browser @ C
    bpy.context.view_layer.update()
    return {
        'runtimeEulerXYZ': [float(euler.x), float(euler.y), float(euler.z)],
        'preservedRuntimeEulerXandZ': preserved,
        'nativeEquivalentLocalAxis': 'Z',
        'runtimeBreastplateRotationYRadians': -1.35 * open_value,
        'runtimeBreastplateSeparationOffset': [-0.70, -0.12, 0.18],
        'nativeBreastplateSeparationOffset': [-0.70, -0.18, -0.12],
        'separation': 0.0,
        'runtimeCranialCoverTranslationY': 0.08 * open_value,
    }


def main():
    args = parse_args()
    assert args.native.is_file() and sha(args.native) == args.sha256, 'Candidate native hash mismatch'
    assert not args.out.exists(), f'Refusing to overwrite {args.out}'
    bpy.ops.wm.open_mainfile(filepath=str(args.native))
    bpy.context.scene.frame_set(1)
    pivots = {obj.name: obj for obj in bpy.data.objects if obj.type == 'EMPTY'}
    pivot = pivots.get('breastplate')
    cover = pivots.get('cranial-cover')
    assert pivot is not None and cover is not None, 'Candidate is missing breastplate or cranial-cover pivot'
    assert pivot.parent is not None, 'Breastplate pivot must remain in the authored hierarchy'
    shell = bpy.data.objects.get('Breast inner access shell')
    assert shell and shell.type == 'MESH', 'Candidate is missing the moving access shell'
    assert shell in descendants(pivot), 'Access shell is not descended from the breastplate pivot'

    targets = []
    missing = []
    for name in (*RIB_NAMES, *RAIL_NAMES):
        obj = bpy.data.objects.get(name)
        if obj is None or obj.type != 'MESH':
            missing.append(name)
        else:
            targets.append(obj)
    assert not missing, f'Missing required fixed rib/frame surfaces: {missing}'
    neighbor_targets = [obj for obj in bpy.data.objects if obj.type == 'MESH'
                        and obj.parent is not None and obj.parent.name in NEIGHBOR_OWNERS
                        and obj.parent != pivot]
    assert neighbor_targets, 'No body, mantle, or wing-shield neighbor surfaces found'
    targets.extend(obj for obj in neighbor_targets if obj not in targets)
    moving = sorted((obj for obj in descendants(pivot) if obj.type == 'MESH'), key=lambda obj: obj.name)
    assert shell in moving and moving, 'No breastplate-owned mesh surfaces found'
    assert all(obj.parent == pivot or obj in descendants(pivot) for obj in moving)
    assert all(target not in moving for target in targets), 'Moving/fixed surface ownership overlap'

    rest_local = pivot.matrix_local.copy()
    cover_rest_local = cover.matrix_local.copy()
    parent_name = pivot.parent.name
    rest_world = pivot.matrix_world.copy()
    shell_owner = shell.parent.name if shell.parent else None
    kernel_path = ROOT / 'assets/audit/cervical-construction-study-v1/attempt-07/actual-runtime-joint-clearance-v1/executed-review.py'
    runtime_path = ROOT / 'src/scene/inspection-pose.js'
    spec = importlib.util.spec_from_file_location('v19_pinned_proper_crossing_kernel', kernel_path)
    kernel = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kernel)
    proper_crossing = kernel.proper_crossing_receipt

    rows = []
    identity = Matrix.Identity(4)
    for open_value in OPEN_VALUES:
        pivot.matrix_local = rest_local
        cover.matrix_local = cover_rest_local
        bpy.context.view_layer.update()
        transform = set_runtime_open(pivot, cover, rest_local, cover_rest_local, open_value)
        depsgraph = bpy.context.evaluated_depsgraph_get()
        cache = {}

        def get_surface(obj):
            if obj.name not in cache:
                cache[obj.name] = surface(obj, depsgraph)
            return cache[obj.name]

        pairs = []
        for subject in moving:
            a = get_surface(subject)
            if a is None:
                continue
            for target in targets:
                b = get_surface(target)
                if b is None or not bounds_overlap(a, b):
                    continue
                overlaps = a['tree'].overlap(b['tree'])
                if not overlaps:
                    continue
                proof = proper_crossing(a, b, overlaps, identity, identity)
                crossed = proof['confirmedSubjectTriangleCount'] > 0
                pairs.append({
                    'movingMesh': subject.name,
                    'movingOwner': subject.parent.name if subject.parent else None,
                    'fixedMesh': target.name,
                    'fixedOwner': target.parent.name if target.parent else None,
                    'broadphaseTrianglePairs': len(overlaps),
                    'strictCrossing': crossed,
                    'strictSubjectTriangleCount': proof['confirmedSubjectTriangleCount'],
                    'strictTargetTriangleCount': proof['confirmedTargetTriangleCount'],
                    'movingCrossingBoundsXYZ': proof['subjectCrossingRestWorldBoundsNativeXYZ'],
                    'fixedCrossingBoundsXYZ': proof['targetCrossingRestWorldBoundsNativeXYZ'],
                    'examples': proof['examples'][:2] if crossed else [],
                })
        rows.append({
            'open': open_value,
            'pose': transform,
            'breastplateParent': parent_name,
            'breastplateLocalMatrixNative': [list(row) for row in pivot.matrix_local],
            'breastplateWorldMatrixNative': [list(row) for row in pivot.matrix_world],
            'strictCrossingPairs': sum(pair['strictCrossing'] for pair in pairs),
            'broadphaseCandidatePairs': len(pairs),
            'pairs': pairs,
        })

    args.out.mkdir(parents=True)
    shutil.copy2(Path(__file__), args.out / 'executed-check.py')
    shutil.copy2(kernel_path, args.out / 'proper-crossing-kernel.py')
    result = {
        'status': 'FAIL' if any(row['strictCrossingPairs'] for row in rows) else 'PASS within sampled surfaces and five discrete openings',
        'native': artifact(args.native),
        'checker': artifact(Path(__file__)),
        'kernel': artifact(kernel_path),
        'runtimeSource': artifact(runtime_path),
        'blenderVersion': bpy.app.version_string,
        'runtimeContract': {
            'source': 'src/scene/inspection-pose.js: applyInspectionPose',
            'breastplate': 'Three local Euler XYZ rotation.y = -1.35 * open; rotation.x/z, local position, and scale retained.',
            'nativeMapping': 'C^-1 * M_three * C; browser=(native X, native Z, -native Y), hence browser local Y maps to candidate native local Z.',
            'cranialCover': 'Three local position.y = rest.y + 0.08 * open; candidate native local Z += 0.08 * open.',
            'separation': 'Fixed at zero; no exploded offsets are applied.',
            'restLocalMatrixNative': [list(row) for row in rest_local],
            'restWorldMatrixNative': [list(row) for row in rest_world],
        },
        'scope': {
            'movingOwner': 'breastplate',
            'movingMeshCount': len(moving),
            'movingMeshes': [obj.name for obj in moving],
            'accessShell': {'name': shell.name, 'parent': shell_owner},
            'fixedBodyMeshes': [obj.name for obj in targets if obj.parent and obj.parent.name == 'body'],
            'fixedNeighborOwners': list(NEIGHBOR_OWNERS),
            'fixedNeighborMeshCount': len(neighbor_targets),
            'poses': rows,
        },
        'limits': [
            'Five discrete local inspection openings at zero separation only; no continuous swept-volume proof.',
            'Tests strict noncoplanar triangle-edge crossings; tangent/coplanar adjacency and full containment are not established.',
            'The fixed target set is the named breast frame/ribs plus recognized shoulder and wing-root hardware, not every scene mesh.',
            'A geometric pass does not prove bearing support, mechanical strength, visitor safety, artistic likeness, or runtime/browser acceptance.',
            'No native scene was saved or modified.',
        ],
    }
    if args.render_open:
        result['openIllustrations'] = render_full_open(args.native, args.sha256, args.out, pivot, cover, rest_local, cover_rest_local)
    report = args.out / 'breast-opening.json'
    report.write_text(json.dumps(result, indent=2) + '\n')
    assert sha(args.native) == args.sha256, 'Native changed during read-only check'
    assert sha(runtime_path) == result['runtimeSource']['sha256'], 'Runtime inspection source changed during check'
    print(json.dumps({'status': result['status'], 'crossingPairsByOpen': [r['strictCrossingPairs'] for r in rows],
                      'report': report.relative_to(ROOT).as_posix()}))


if __name__ == '__main__':
    main()
