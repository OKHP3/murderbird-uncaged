"""Render four packet-driven V12 native head/neck/breast poses read-only."""
from pathlib import Path
import datetime
import hashlib
import json
import struct
import bpy
from mathutils import Matrix, Vector, Quaternion

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / 'assets/models/uncaged-cervical-envelope-v12/attempt-02/murderbird-cervical-envelope-v12.blend'
GLB = ROOT / 'assets/models/uncaged-cervical-envelope-v12/attempt-02/murderbird-cervical-envelope-v12.glb'
POSES = ROOT / 'assets/audit/uncaged-cervical-envelope-v12/attempt-02/runtime-poses/pose-snapshot.json'
OUT = ROOT / 'assets/audit/uncaged-cervical-envelope-v12/attempt-02/native-poses-v2'
EXPECTED_NATIVE = '28b18c810784a1e6872ef3743f16e5cff36e5aac66c01c9299e5195064ac7c60'
EXPECTED_GLB = '6597cee218d7c86e741b3a942a8794f3b7e832cadb814c44d91b3e7c4e84dda3'
EXPECTED_POSES = '913fb2843d8a5ae7656c3dff26119a209789539d767179eb9b051496f4e37883'
POSE_IDS = ('maker-neck-control', 'advanced-contact', 'advanced-jump-airborne',
            'inspection-open-1-separation-0.5')
DETAIL_REGIONS = {'head', 'neck', 'shoulder', 'breast'}
RES = 1200
DETAIL_ORTHO = 2.45
DETAIL_TARGET = Vector((0.0, -0.12, 1.48))
DETAIL_OFFSET = Vector((-1.55, -2.50, .92))
C = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1)))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def converted(flat):
    browser = Matrix([[flat[col * 4 + row] for col in range(4)] for row in range(4)])
    return C.inverted() @ browser @ C


def depth(obj):
    count = 0
    while obj.parent is not None:
        count += 1
        obj = obj.parent
    return count


def matrix_error(a, b):
    return max(abs(float(a[r][c]) - float(b[r][c])) for r in range(4) for c in range(4))


def rows_by_name(pose):
    rows = {}
    for row in pose['pivotMatrices']:
        if row.get('kind') == 'transform':
            rows.setdefault(row['name'], []).append(row)
    return rows


def set_pose(pose, pivots):
    rows = rows_by_name(pose)
    assert set(pivots) <= set(rows), f"pose {pose['id']} misses native pivots"
    assert all(len(rows[name]) == 1 for name in pivots), f"ambiguous native pivot names in {pose['id']}"
    for name in sorted(pivots, key=lambda n: depth(pivots[n])):
        pivots[name].matrix_world = converted(rows[name][0]['worldMatrix'])
        bpy.context.view_layer.update()
    error = max(matrix_error(pivots[name].matrix_world, converted(rows[name][0]['worldMatrix']))
                for name in pivots)
    assert error < 2e-6, f"pose matrix application mismatch for {pose['id']}: {error}"
    return error, sorted(set(rows) - set(pivots))


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
    scene.render.resolution_x = scene.render.resolution_y = RES
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.film_transparent = False


def add_camera(scene):
    data = bpy.data.cameras.new('Temporary V12 neck pose review camera')
    data.type = 'ORTHO'
    data.ortho_scale = DETAIL_ORTHO
    data.lens = 70
    data.clip_start, data.clip_end = .01, 100
    obj = bpy.data.objects.new('Temporary V12 neck pose review camera', data)
    scene.collection.objects.link(obj)
    obj.location = DETAIL_TARGET + DETAIL_OFFSET
    obj.rotation_euler = (DETAIL_TARGET - obj.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    return obj, data


def camera_bounds(objects, camera):
    inverse = camera.matrix_world.inverted()
    points = []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in objects:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            points.extend(inverse @ (evaluated.matrix_world @ vertex.co) for vertex in mesh.vertices)
        finally:
            evaluated.to_mesh_clear()
    assert points
    lo = [min(p[i] for p in points) for i in range(3)]
    hi = [max(p[i] for p in points) for i in range(3)]
    half = DETAIL_ORTHO / 2
    assert lo[2] > -camera.data.clip_end and hi[2] < -camera.data.clip_start
    assert lo[0] > -half * .965 and hi[0] < half * .965, f'horizontal crop {lo[0]:.3f}..{hi[0]:.3f}'
    assert lo[1] > -half * .965 and hi[1] < half * .965, f'vertical crop {lo[1]:.3f}..{hi[1]:.3f}'
    return {'cameraLocalMin': lo, 'cameraLocalMax': hi,
            'minimumBorderMarginM': min(half - max(abs(lo[0]), abs(hi[0])),
                                        half - max(abs(lo[1]), abs(hi[1])))}


def exported_rest_worlds():
    raw=GLB.read_bytes();length=struct.unpack_from('<I',raw,12)[0]
    doc=json.loads(raw[20:20+length]);out={}
    def visit(index,parent):
        node=doc['nodes'][index]
        if 'matrix' in node:
            local=Matrix([[node['matrix'][col*4+row] for col in range(4)] for row in range(4)])
        else:
            q=node.get('rotation',[0,0,0,1]);local=Matrix.LocRotScale(Vector(node.get('translation',[0,0,0])),Quaternion((q[3],q[0],q[1],q[2])),Vector(node.get('scale',[1,1,1])))
        world=parent@local
        if node.get('name') in out:raise AssertionError('Duplicate export node '+node['name'])
        if node.get('name'):out[node['name']]=C.inverted()@world@C
        for child in node.get('children',[]):visit(child,world)
    for root in doc['scenes'][doc.get('scene',0)]['nodes']:visit(root,Matrix.Identity(4))
    return out


def main():
    assert sha(NATIVE) == EXPECTED_NATIVE, 'V12 native hash mismatch'
    assert sha(GLB) == EXPECTED_GLB, 'V12 GLB hash mismatch'
    assert sha(POSES) == EXPECTED_POSES, 'runtime pose packet hash mismatch'
    OUT.mkdir(parents=True, exist_ok=True)
    frozen_script = OUT / 'executed-renderer.py'
    if frozen_script.exists():
        assert sha(frozen_script) == sha(Path(__file__).resolve()), 'frozen renderer differs from executed source'
    else:
        frozen_script.write_bytes(Path(__file__).resolve().read_bytes())
    pose_data = json.loads(POSES.read_text())
    assert pose_data['model']['sha256'] == EXPECTED_GLB
    pose_map = {pose['id']: pose for pose in pose_data['poses']}
    assert all(pose_id in pose_map for pose_id in POSE_IDS)
    bpy.ops.wm.open_mainfile(filepath=str(NATIVE))
    scene = bpy.context.scene
    scene.frame_set(1)
    bpy.context.view_layer.update()
    pivots = {obj.name: obj for obj in bpy.data.objects if obj.type == 'EMPTY'}
    assert len(pivots) == 52, f'expected 52 native pivots, found {len(pivots)}'

    rest = pose_map.get('runtime-rest')
    assert rest, 'pose packet missing runtime-rest sample'
    rest_rows = rows_by_name(rest)
    assert set(pivots) <= set(rest_rows) and all(len(rest_rows[n]) == 1 for n in pivots)
    rest_error = max(matrix_error(pivots[n].matrix_world, converted(rest_rows[n][0]['worldMatrix'])) for n in pivots)
    # runtime-rest is grounded and translated by the live controller; it is not authored rest.
    exported_rest=exported_rest_worlds()
    export_rest_error=max(matrix_error(pivots[n].matrix_world,exported_rest[n]) for n in pivots)
    assert export_rest_error < 2e-6, f'native rest differs from raw GLB rest: {export_rest_error}'
    procedural_rows = sorted(set(rows_by_name(rest)) - set(pivots))

    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        eligible_regions = obj.get('region') in DETAIL_REGIONS
        obj.hide_set(False)
        obj.hide_render = not eligible_regions
    detail_meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH' and not obj.hide_render]
    assert detail_meshes
    configure(scene)
    camera, camera_data = add_camera(scene)
    records = []
    for pose_id in POSE_IDS:
        pose = pose_map[pose_id]
        error, excluded = set_pose(pose, pivots)
        assert excluded == procedural_rows, 'packet-only transform inventory changed across poses'
        era = pose.get('controller', {}).get('era') or pose.get('motionMetrics', {}).get('era')
        assert era in {'maker', 'mechanic', 'builder'}, f'pose has no production era: {pose_id}'
        visible = []
        for obj in detail_meshes:
            eras = [token.strip() for token in obj.get('exteriorEras', 'maker,mechanic,builder').split(',')]
            obj.hide_render = era not in eras
            if not obj.hide_render:
                visible.append(obj)
        root=pivots['murderbird'].matrix_world
        target=root@DETAIL_TARGET;offset=root.to_quaternion()@DETAIL_OFFSET
        camera.location=target+offset;camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
        bpy.context.view_layer.update()
        scene.camera = camera
        framing = camera_bounds(visible, camera)
        path = OUT / f'{pose_id}-head-neck-breast.png'
        assert not path.exists()
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        records.append({'poseId': pose_id, 'category': pose['category'], 'era': era,
            'elapsedSeconds': pose.get('elapsedSeconds'), 'motionMetrics': pose.get('motionMetrics'),
            'pivotMatrixMaxError': error, 'nativePivotCountApplied': len(pivots),
            'packetOnlyTransformNamesNotApplied': excluded,
            'visibleMeshCount': len(visible), 'regions': sorted(DETAIL_REGIONS),
            'cameraTargetBlenderM': list(target), 'cameraOffsetBlenderM': list(offset),
            'orthoScaleM': DETAIL_ORTHO, 'framing': framing,
            'image': {'path': str(path.relative_to(ROOT)), 'sha256': sha(path), 'bytes': path.stat().st_size}})

    bpy.data.objects.remove(camera, do_unlink=True)
    bpy.data.cameras.remove(camera_data)
    result = {
        'schema': 'cervical-envelope-v12-native-pose-renders/v1',
        'status': 'pose-packet-driven native review; not browser-frame captures or acceptance',
        'generatedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'native': {'path': str(NATIVE.relative_to(ROOT)), 'sha256': sha(NATIVE), 'bytes': NATIVE.stat().st_size},
        'glb': {'path': str(GLB.relative_to(ROOT)), 'sha256': sha(GLB), 'bytes': GLB.stat().st_size},
        'posePacket': {'path': str(POSES.relative_to(ROOT)), 'sha256': sha(POSES),
            'declaredModel': pose_data['model'],
            'sourceNote': 'Deterministic Three.js runtime matrix samples replayed on the native Blender hierarchy; these are not captured browser frames.'},
        'script': {'path': str(Path(__file__).resolve().relative_to(ROOT)), 'sha256': sha(Path(__file__).resolve()),
            'frozenExecutedCopy': str(frozen_script.relative_to(ROOT)), 'frozenSha256': sha(frozen_script)},
        'blenderVersion': bpy.app.version_string,
        'nativePivotCount': len(pivots), 'authoredVsSettledRuntimeRestDifference': rest_error, 'rawExportRestMatrixMaxError': export_rest_error,
        'packetOnlyProceduralTransformsNotApplied': procedural_rows,
        'render': {'engine': 'BLENDER_WORKBENCH', 'resolution': [RES, RES],
            'lighting': 'paint.sl studio, cavity and shadows', 'regions': sorted(DETAIL_REGIONS),
            'framingSubject': 'evaluated mesh vertices after modifiers; curves excluded',
            'eraVisibility': 'selected per packet controller/motionMetrics era'},
        'poses': records,
        'limits': ['Four discrete packet samples only; no continuous clearance or collision validation.',
            'Native authoring renders are not browser/WebGL images.',
            'No native save, geometry change, runtime change, or export was performed by this renderer.'],
    }
    manifest = OUT / 'pose-render-manifest.json'
    assert not manifest.exists()
    manifest.write_text(json.dumps(result, indent=2) + '\n')
    assert sha(NATIVE) == EXPECTED_NATIVE and sha(GLB) == EXPECTED_GLB and sha(POSES) == EXPECTED_POSES
    print(json.dumps({'status': result['status'], 'poses': len(records), 'nativePivotCount': len(pivots),
        'nativeSha256': result['native']['sha256'], 'glbSha256': result['glb']['sha256'],
        'posePacketSha256': result['posePacket']['sha256']}, indent=2))


main()
