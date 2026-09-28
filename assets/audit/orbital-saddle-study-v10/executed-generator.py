"""Fit only the two fixed orbital mounting plates around preserved V6 brows.

This one-shot Boolean study is a local reconstruction proposal. It preserves
the full brows and leaves optics, fasteners, hierarchy, runtime selection, and
all unrelated scene data untouched.
"""
from pathlib import Path
import hashlib
import json
import math
import runpy
import shutil

import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'assets/models/uncaged-orbital-saddle-study-v6/murderbird-orbital-saddle-study-v6.blend'
BASE_SHA = 'cb811241d241b0f18f529979b77635caecb83284b8b4df29c7564d4d2bf55eec'
HELPER = ROOT / 'scripts/build-uncaged-alignment-v7.py'
HELPER_SHA = '39b6ee2285d8c49df3a902f8fac0a07589da3d41f48ae24df1e06515c839033a'
RENDERER = ROOT / 'scripts/study-v8-bill-envelope.py'
RENDERER_SHA = '2d3502a134cecb15c04ca0ce9f8db0f7555d6d8a52e5f7c9c74dfd55299f421a'
OUT = ROOT / 'assets/models/uncaged-orbital-saddle-study-v10'
AUDIT = ROOT / 'assets/audit/orbital-saddle-study-v10'
SIDES = (-1, 1)
OPENING_METRES = .08
OFFSET_METRES = .001
SLIVER_AREA_M2 = 1e-10
SLIVER_ANGLE_DEGREES = .1


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path):
    return {'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size, 'sha256': sha(path)}


def evaluated_surface(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    mesh.calc_loop_triangles()
    matrix = evaluated.matrix_world.copy()
    points = [matrix @ vertex.co for vertex in mesh.vertices]
    triangles = [tuple(tri.vertices) for tri in mesh.loop_triangles]
    centers = [sum((points[i] for i in poly.vertices), Vector()) / len(poly.vertices)
                for poly in mesh.polygons if len(poly.vertices)]
    tree = BVHTree.FromPolygons(points, triangles, all_triangles=True, epsilon=0)
    evaluated.to_mesh_clear()
    return {'points': points, 'triangles': triangles, 'polygonCenters': centers, 'tree': tree}


def point_distance_profile(surface, points):
    distances = []
    for point in points:
        nearest = surface['tree'].find_nearest(point)
        distances.append(float(nearest[3]) if nearest[0] is not None else None)
    return distances


def quantile(values, fraction):
    ordered = sorted(values)
    return ordered[min(len(ordered)-1, math.ceil(fraction*len(ordered))-1)] if ordered else None


def aperture_rays(surface, optic_surface):
    # The authored optic is a narrow X-axis lens. Probe an interior 5x5 grid
    # within 70% of its evaluated Y/Z half-widths, through the mount along +X.
    pts = optic_surface['points']
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    cy, cz = (lo[1]+hi[1])*.5, (lo[2]+hi[2])*.5
    hy, hz = (hi[1]-lo[1])*.5, (hi[2]-lo[2])*.5
    start_x = min(p.x for p in surface['points']) - .01
    max_dist = max(p.x for p in surface['points']) - start_x + .02
    coords = [-.7, -.35, 0, .35, .7]
    samples = []
    for uy in coords:
        for uz in coords:
            start = Vector((start_x, cy + uy*hy, cz + uz*hz))
            loc, normal, index, distance = surface['tree'].ray_cast(start, Vector((1,0,0)), max_dist)
            samples.append({'normalizedYZ': [uy, uz], 'hit': loc is not None,
                            'hitDistanceM': float(distance) if loc is not None else None,
                            'hitWorldXYZM': [float(v) for v in loc] if loc is not None else None})
    return {'axis': '+X', 'opticEvaluatedBoundsWorldM': {'min': lo, 'max': hi},
            'interiorGrid5x5Within70PercentOpticHalfWidth': samples,
            'limits': 'Ray screen through projected evaluated optic bounds; not a volumetric optical or renderer test.'}

def strict_crossing_count(a, b, candidates):
    """Strict noncoplanar edge-through-face crossing kernel for a named pair."""
    ids_a, ids_b, examples = set(), set(), []

    def edge_crosses(tri, other):
        normal = (other[1]-other[0]).cross(other[2]-other[0])
        if normal.length < 1e-12:
            return False
        normal.normalize()
        for i in range(3):
            p, q = tri[i], tri[(i+1) % 3]
            d0, d1 = normal.dot(p-other[0]), normal.dot(q-other[0])
            if not (d0*d1 < 0 and abs(d0) > 1e-7 and abs(d1) > 1e-7):
                continue
            hit = intersect_ray_tri(*other, q-p, p, True)
            if hit is None:
                continue
            t = (hit-p).dot(q-p)/(q-p).length_squared
            if 1e-6 < t < 1-1e-6:
                return True
        return False

    for ia, ib in candidates:
        ta = [a['points'][v] for v in a['triangles'][ia]]
        tb = [b['points'][v] for v in b['triangles'][ib]]
        if edge_crosses(ta, tb) or edge_crosses(tb, ta):
            ids_a.add(ia); ids_b.add(ib)
            if len(examples) < 8:
                examples.append({'triangleA': ia, 'triangleB': ib,
                                 'worldTriangleA': [[round(float(c), 7) for c in p] for p in ta],
                                 'worldTriangleB': [[round(float(c), 7) for c in p] for p in tb]})
    return {'candidateTrianglePairs': len(candidates), 'confirmedTrianglesA': len(ids_a),
            'confirmedTrianglesB': len(ids_b), 'examples': examples,
            'method': 'Strict noncoplanar edge-through-face tests; tangency and coplanar overlap excluded.'}


def point_parity(tree, point):
    directions = [Vector((1, math.sqrt(2), math.sqrt(3))).normalized(),
                  Vector((math.sqrt(5), -1, math.sqrt(7))).normalized(),
                  Vector((-math.sqrt(11), math.sqrt(13), 1)).normalized(),
                  Vector((-1, -math.sqrt(17), math.sqrt(19))).normalized()]
    counts = []
    for direction in directions:
        origin = point + direction * 1e-5
        hits = 0
        for _ in range(128):
            loc, _, _, _ = tree.ray_cast(origin, direction, 2.0)
            if loc is None:
                break
            hits += 1
            origin = loc + direction * 1e-6
        counts.append(hits)
    parity = [n % 2 for n in counts]
    state = ('inside' if parity[0] else 'outside') if len(set(parity)) == 1 else 'direction-disagreement'
    return {'pointWorldXYZM': [float(v) for v in point], 'rayHitCounts': counts,
            'oddEvenParities': parity, 'classification': state}


def topology_profile(obj):
    bm = bmesh.new(); bm.from_mesh(obj.data); bm.normal_update()
    edge_incidence = {edge: len(edge.link_faces) for edge in bm.edges}
    boundary_edges = sum(count == 1 for count in edge_incidence.values())
    nonmanifold_edges = sum(count != 2 for count in edge_incidence.values())
    unseen = set(bm.faces); components = []
    while unseen:
        stack = [unseen.pop()]; faces = 0
        while stack:
            face = stack.pop(); faces += 1
            for edge in face.edges:
                for adjacent in edge.link_faces:
                    if adjacent in unseen:
                        unseen.remove(adjacent); stack.append(adjacent)
        components.append(faces)
    face_areas = [float(face.calc_area()) for face in bm.faces]
    bm.free()
    mesh = obj.data; mesh.calc_loop_triangles()
    areas, triangle_min_angles = [], []
    for tri in mesh.loop_triangles:
        p = [obj.matrix_world @ mesh.vertices[i].co for i in tri.vertices]
        area = ((p[1]-p[0]).cross(p[2]-p[0])).length * .5
        areas.append(area)
        lengths = [(p[(i+1) % 3]-p[(i+2) % 3]).length for i in range(3)]
        tri_angles = []
        for i in range(3):
            a, b, opposite = lengths[(i+1) % 3], lengths[(i+2) % 3], lengths[i]
            denom = max(2*a*b, 1e-30)
            cosine = max(-1.0, min(1.0, (a*a+b*b-opposite*opposite)/denom))
            tri_angles.append(math.degrees(math.acos(cosine)))
        triangle_min_angles.append(min(tri_angles))
    return {'vertices': len(mesh.vertices), 'polygons': len(mesh.polygons),
            'evaluatedLoopTriangles': len(mesh.loop_triangles),
            'boundaryEdges': boundary_edges, 'nonManifoldEdges': nonmanifold_edges,
            'connectedFaceComponentCount': len(components), 'componentFaceCounts': sorted(components, reverse=True),
            'minimumPolygonAreaM2': min(face_areas) if face_areas else None,
            'minimumTriangleAreaM2': min(areas) if areas else None,
            'degenerateTriangleCountAreaLe1e12': sum(area <= 1e-12 for area in areas),
            'sliverTriangleCountAreaLe1e10AndAngleLt0p1Deg': sum(
                area <= SLIVER_AREA_M2 and triangle_min_angles[i] < SLIVER_ANGLE_DEGREES for i, area in enumerate(areas))}


def build_translated_brow_cutters(brow, depsgraph, prefix):
    """Copy the exact evaluated brow solid at rest and eight world-space offsets."""
    evaluated = brow.evaluated_get(depsgraph)
    evaluated_mesh = evaluated.to_mesh()
    mesh_copy = evaluated_mesh.copy()
    matrix = evaluated.matrix_world.copy()
    source_counts = {'vertices': len(evaluated_mesh.vertices), 'polygons': len(evaluated_mesh.polygons)}
    evaluated.to_mesh_clear()
    offsets = [(0.0, 0.0, 0.0)] + [
        (sx*OFFSET_METRES, sy*OFFSET_METRES, sz*OFFSET_METRES)
        for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
    cutters = []
    for index, offset in enumerate(offsets):
        cutter = bpy.data.objects.new(f'{prefix} copy {index:02d}', mesh_copy)
        bpy.context.scene.collection.objects.link(cutter)
        cutter.matrix_world = matrix.copy()
        cutter.matrix_world.translation += Vector(offset)
        cutters.append((cutter, offset))
    return cutters, {'sourceEvaluatedVertices': source_counts['vertices'],
                     'sourceEvaluatedPolygons': source_counts['polygons'],
                     'copies': [{'index': i, 'worldTranslationM': list(offset)} for i, offset in enumerate(offsets)],
                     'method': 'Sequential exact Boolean Difference with original evaluated brow solid and eight translated copies; no convex hull; this nine-copy screen is not a mathematically complete Minkowski dilation.'}


def material_signatures(helper):
    return {material.name: helper['material_signature'](material) for material in bpy.data.materials}


def render_set(native, label, fraction=None):
    bpy.ops.wm.open_mainfile(filepath=str(native))
    scene = bpy.context.scene
    scene.frame_set(1); bpy.context.view_layer.update()
    cover = bpy.data.objects['cranial-cover']
    if fraction is not None:
        cover.location.z = cover.matrix_local.translation.z + OPENING_METRES * fraction
        bpy.context.view_layer.update()
    scene.render.engine = 'BLENDER_WORKBENCH'
    shading = scene.display.shading
    shading.light = 'STUDIO'; shading.studio_light = 'paint.sl'; shading.color_type = 'MATERIAL'
    shading.show_shadows = True; shading.show_cavity = True; shading.cavity_type = 'BOTH'
    shading.background_type = 'WORLD'; scene.world.color = (.11, .12, .13)
    scene.render.resolution_x = scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    camera_data = bpy.data.cameras.new('Temporary V10 orbital study camera')
    camera = bpy.data.objects.new('Temporary V10 orbital study camera', camera_data)
    scene.collection.objects.link(camera); scene.camera = camera
    camera_data.type = 'ORTHO'
    poses = [
        ('front', (0, -6, 1.78), (0, -.3, 1.78), 1.05),
        ('profile', (-6, -.3, 1.78), (0, -.3, 1.78), 1.1),
        ('three-quarter', (-6, -3, 2.4), (0, -.29, 1.78), .88),
    ]
    records = []
    suffix = 'open-12p5' if fraction is not None else label
    for view, position, target, scale in poses:
        camera.location = position
        camera.rotation_euler = (Vector(target)-camera.location).to_track_quat('-Z', 'Y').to_euler()
        camera_data.ortho_scale = scale
        path = AUDIT / f'{suffix}-{view}.png'
        assert not path.exists(), path
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        records.append({'file': artifact(path), 'label': suffix, 'view': view,
                        'position': position, 'target': target, 'orthoScale': scale,
                        'cranialCoverLocalZDeltaM': OPENING_METRES*fraction if fraction is not None else 0.0,
                        'normalizedOpeningFraction': fraction})
    return records


def distance_summary(surface, points):
    values = []
    for point in points:
        nearest = surface['tree'].find_nearest(point)
        values.append(float(nearest[3]) if nearest[0] is not None else None)
    finite = sorted(v for v in values if v is not None)
    def q(p): return finite[min(len(finite)-1, math.ceil(p*len(finite))-1)] if finite else None
    return {'sampleCount': len(values), 'minM': min(finite) if finite else None,
            'medianM': q(.5), 'p90M': q(.9), 'maxM': max(finite) if finite else None}


def main():
    assert sha(BASE) == BASE_SHA, 'Pinned V6 orbital-study native changed'
    assert sha(HELPER) == HELPER_SHA and sha(RENDERER) == RENDERER_SHA
    assert not OUT.exists() and not AUDIT.exists(), 'Refusing to overwrite V10 study'
    AUDIT.mkdir(parents=True)
    shutil.copy2(__file__, AUDIT / 'executed-generator.py')
    helper = runpy.run_path(str(HELPER), run_name='v10_scene_snapshot_helpers')

    bpy.ops.wm.open_mainfile(filepath=str(BASE))
    bpy.context.scene.frame_set(1); bpy.context.view_layer.update()
    before = helper['scene_snapshot']()
    assert len(before['meshes']) == 699 and len(before['empties']) == 51 and len(before['curves']) == 462
    mats_before = material_signatures(helper)
    world_before = {obj.name: obj.matrix_world.copy() for obj in bpy.data.objects}
    changed = [f'Forged orbital mounting plate {side}' for side in SIDES]
    brows = [f'Forged orbital brow {side}' for side in SIDES]
    optics = [f'Seated passive optic housing {side}' for side in SIDES] + [f'Seated Advanced optic {side}' for side in SIDES]
    pins6 = [f'Orbital mounting fixing {side} 6' for side in SIDES]
    assert all(name in before['meshes'] for name in changed + brows + optics + pins6)
    before_surfaces = {}
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for side in SIDES:
        mount = bpy.data.objects[f'Forged orbital mounting plate {side}']
        before_surfaces[side] = {'mount': evaluated_surface(mount, depsgraph),
                                 'housing': evaluated_surface(bpy.data.objects[f'Seated passive optic housing {side}'], depsgraph),
                                 'optic': evaluated_surface(bpy.data.objects[f'Seated Advanced optic {side}'], depsgraph),
                                 'pin6': evaluated_surface(bpy.data.objects[f'Orbital mounting fixing {side} 6'], depsgraph)}

    cutter_receipts, topology_rows = [], []
    fail_reasons = []
    for side in SIDES:
        brow = bpy.data.objects[f'Forged orbital brow {side}']
        mount = bpy.data.objects[f'Forged orbital mounting plate {side}']
        before_topology = topology_profile(mount)
        cutters, cutter_receipt = build_translated_brow_cutters(
            brow, bpy.context.evaluated_depsgraph_get(), f'Temporary V10 brow solid {side}')
        cutter_receipt.update({'side': 'left' if side == 1 else 'right', 'brow': brow.name, 'mount': mount.name})
        cutter_receipts.append(cutter_receipt)
        shared_cutter_mesh = cutters[0][0].data if cutters else None
        for cutter, offset in cutters:
            modifier = mount.modifiers.new('Frozen V10 exact brow-solid difference', 'BOOLEAN')
            modifier.operation = 'DIFFERENCE'; modifier.solver = 'EXACT'; modifier.object = cutter
            bpy.context.view_layer.objects.active = mount; mount.select_set(True)
            bpy.ops.object.modifier_apply(modifier=modifier.name)
            bpy.data.objects.remove(cutter, do_unlink=True)
            bpy.context.view_layer.update()
        if shared_cutter_mesh and shared_cutter_mesh.users == 0:
            bpy.data.meshes.remove(shared_cutter_mesh)
        bpy.context.view_layer.update()
        after_topology = topology_profile(mount)
        row = {'mesh': mount.name, 'before': before_topology, 'after': after_topology}
        topology_rows.append(row)
        if after_topology['connectedFaceComponentCount'] > before_topology['connectedFaceComponentCount']:
            fail_reasons.append(f'{mount.name}: Boolean increased connected face components')
        if after_topology['nonManifoldEdges'] > before_topology['nonManifoldEdges']:
            fail_reasons.append(f'{mount.name}: Boolean introduced additional nonmanifold edges')
        if after_topology['degenerateTriangleCountAreaLe1e12'] > before_topology['degenerateTriangleCountAreaLe1e12']:
            fail_reasons.append(f'{mount.name}: Boolean introduced degenerate triangles')
        if after_topology['sliverTriangleCountAreaLe1e10AndAngleLt0p1Deg'] > before_topology['sliverTriangleCountAreaLe1e10AndAngleLt0p1Deg']:
            fail_reasons.append(f'{mount.name}: Boolean introduced suspect sliver triangles')

    bpy.context.view_layer.update()
    after = helper['scene_snapshot']()
    assert set(before['meshes']) == set(after['meshes'])
    assert before['empties'] == after['empties'] and before['curves'] == after['curves']
    assert len([o for o in bpy.data.objects if o.name.startswith('Temporary V10 brow solid')]) == 0
    assert set(mats_before) == set(material_signatures(helper)) and mats_before == material_signatures(helper)
    for name, prior in before['meshes'].items():
        current = after['meshes'][name]
        if name in changed:
            assert {k:v for k,v in current.items() if k != 'mesh'} == {k:v for k,v in prior.items() if k != 'mesh'}, name
            if current['mesh'] == prior['mesh']:
                fail_reasons.append(f'{name}: Boolean did not change mount geometry')
        else:
            assert current == prior, f'Unexpected object change: {name}'
    all_other_meshes_exact = all(after['meshes'][name] == prior for name, prior in before['meshes'].items() if name not in changed)
    changed_meshes_actual = [name for name, prior in before['meshes'].items() if after['meshes'][name] != prior]
    # Recheck source world matrices for all retained objects explicitly.
    max_world_error = max(max(abs(obj.matrix_world[r][c]-world_before[obj.name][r][c])
                              for r in range(4) for c in range(4)) for obj in bpy.data.objects)
    assert max_world_error < 2e-7, max_world_error

    # Surface-only measures of the unchanged passive optic/housing seat and aperture neighborhood.
    depsgraph = bpy.context.evaluated_depsgraph_get()
    seat_rows, aperture_rows, pin6_rows = [], [], []
    for side in SIDES:
        mount = bpy.data.objects[f'Forged orbital mounting plate {side}']
        housing = bpy.data.objects[f'Seated passive optic housing {side}']
        pin = bpy.data.objects[f'Orbital mounting fixing {side} 6']
        mount_after = evaluated_surface(mount, depsgraph)
        housing_after = evaluated_surface(housing, depsgraph)
        pin_after = evaluated_surface(pin, depsgraph)
        optic_after = evaluated_surface(bpy.data.objects[f'Seated Advanced optic {side}'], depsgraph)
        pre_housing_points = before_surfaces[side]['housing']['points']
        post_housing_points = housing_after['points']
        pre_housing_d = point_distance_profile(before_surfaces[side]['mount'], pre_housing_points)
        post_housing_d = point_distance_profile(mount_after, post_housing_points)
        baseline_near_ids = [i for i,d in enumerate(pre_housing_d) if d is not None and d <= .01]
        seat_delta = [abs(post_housing_d[i]-pre_housing_d[i]) for i in baseline_near_ids]
        pre_housing_to_mount = distance_summary(before_surfaces[side]['mount'], before_surfaces[side]['housing']['points'])
        post_housing_to_mount = distance_summary(mount_after, housing_after['points'])
        seat_rows.append({'side': 'left' if side == 1 else 'right', 'housing': housing.name,
                          'housingGeometryExactBySceneSnapshot': True,
                          'beforeHousingVerticesToMountSurfaceM': pre_housing_to_mount,
                          'afterHousingVerticesToMountSurfaceM': post_housing_to_mount,
                          'minDistanceDeltaM': post_housing_to_mount['minM']-pre_housing_to_mount['minM'],
                          'medianDistanceDeltaM': post_housing_to_mount['medianM']-pre_housing_to_mount['medianM'],
                          'nearSeatVertexDistanceAbsoluteDeltaM': {'sampleCount': len(seat_delta), 'p95M': quantile(seat_delta,.95), 'maxM': max(seat_delta) if seat_delta else None, 'verticesWithinBaseline10mm': len(baseline_near_ids)}})
        pre_aperture = aperture_rays(before_surfaces[side]['mount'], before_surfaces[side]['optic'])
        post_aperture = aperture_rays(mount_after, optic_after)
        pre_pattern = [row['hit'] for row in pre_aperture['interiorGrid5x5Within70PercentOpticHalfWidth']]
        post_pattern = [row['hit'] for row in post_aperture['interiorGrid5x5Within70PercentOpticHalfWidth']]
        aperture_rows.append({'side': 'left' if side == 1 else 'right', 'baseline': pre_aperture, 'candidate': post_aperture, 'interiorRayHitPatternUnchanged': pre_pattern == post_pattern})
        pre_pin_candidates = before_surfaces[side]['mount']['tree'].overlap(before_surfaces[side]['pin6']['tree'])
        post_pin_candidates = mount_after['tree'].overlap(pin_after['tree'])
        pre_cross = strict_crossing_count(before_surfaces[side]['mount'], before_surfaces[side]['pin6'], pre_pin_candidates)
        post_cross = strict_crossing_count(mount_after, pin_after, post_pin_candidates)
        pre_pin_distance = distance_summary(before_surfaces[side]['mount'], before_surfaces[side]['pin6']['points'])
        post_pin_distance = distance_summary(mount_after, pin_after['points'])
        mount_watertight = topology_rows[SIDES.index(side)]['after']['nonManifoldEdges'] == 0
        pin_parity = None
        if mount_watertight:
            parity_rows = ([point_parity(mount_after['tree'], p) for p in pin_after['points']] +
                           [point_parity(mount_after['tree'], c) for c in pin_after['polygonCenters']])
            pin_parity = {state: sum(row['classification'] == state for row in parity_rows)
                          for state in ('inside', 'outside', 'direction-disagreement')}
        pin6_rows.append({'side': 'left' if side == 1 else 'right', 'pin': pin.name,
                          'owner': pin.parent.name if pin.parent else None,
                          'unchangedGeometryAndTransform': before['meshes'][pin.name] == after['meshes'][pin.name],
                          'beforePinVerticesToMountSurfaceM': pre_pin_distance,
                          'afterPinVerticesToMountSurfaceM': post_pin_distance,
                          'beforePinMountStrictCrossing': pre_cross,
                          'afterPinMountStrictCrossing': post_cross,
                          'afterPinSampleParityWithinMount': pin_parity,
                          'limits': 'Pin6 remains unmoved; sampled surface distance/crossing and closed-shell parity only.'})
        if (seat_rows[-1]['nearSeatVertexDistanceAbsoluteDeltaM']['p95M'] is None or
            seat_rows[-1]['nearSeatVertexDistanceAbsoluteDeltaM']['p95M'] > .001):
            fail_reasons.append(f'{housing.name}: Boolean changed at least 5% of near-seat housing vertex distances by more than 1 mm')
        if pre_pattern != post_pattern:
            fail_reasons.append(f'{housing.name}: Boolean changed an interior optic-aperture ray hit')
        if abs(pin6_rows[-1]['afterPinVerticesToMountSurfaceM']['medianM'] - pin6_rows[-1]['beforePinVerticesToMountSurfaceM']['medianM']) > .001:
            fail_reasons.append(f'{pin.name}: mount support distance changed by more than 1 mm; pin remains fixed')

    # Discrete open-cover collision check at rest and all 41 normalized lifts.
    cover = bpy.data.objects['cranial-cover']; cover_local = cover.matrix_local.copy()
    sweep = []
    for step in range(41):
        fraction = step / 40
        cover.matrix_local = cover_local.copy()
        cover.location.z = cover_local.translation.z + OPENING_METRES*fraction
        bpy.context.view_layer.update()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        pair_rows = []
        for side in SIDES:
            brow = bpy.data.objects[f'Forged orbital brow {side}']
            mount = bpy.data.objects[f'Forged orbital mounting plate {side}']
            a, b = evaluated_surface(brow, depsgraph), evaluated_surface(mount, depsgraph)
            candidates = a['tree'].overlap(b['tree'])
            crossing = strict_crossing_count(a, b, candidates)
            min_distance = distance_summary(b, a['points'])['minM']
            pair_rows.append({'brow': brow.name, 'mount': mount.name,
                              'bvhTrianglePairCandidates': len(candidates),
                              'strictCrossing': crossing,
                              'sampledBrowVerticesToMountSurfaceMinM': min_distance})
        sweep.append({'openingFraction': fraction, 'cranialCoverLocalZDeltaM': OPENING_METRES*fraction,
                      'pairs': pair_rows})
    cover.matrix_local = cover_local.copy(); bpy.context.view_layer.update()
    strict_pair_rows = [pair for sample in sweep for pair in sample['pairs']
                        if pair['strictCrossing']['confirmedTrianglesA'] or pair['strictCrossing']['confirmedTrianglesB']]
    if strict_pair_rows:
        fail_reasons.append(f'{len(strict_pair_rows)} brow/mount strict-crossing pair-poses in 41-step lift sweep')

    result_status = 'held' if fail_reasons else 'neutral orbital mounting fit proposal; not selected'
    native = None
    view_rows = []
    if not fail_reasons:
        OUT.mkdir(parents=True, exist_ok=False)
        native = OUT / 'murderbird-orbital-saddle-study-v10.blend'
        bpy.context.preferences.filepaths.save_version = 0
        bpy.ops.wm.save_as_mainfile(filepath=str(native), check_existing=False)
        bpy.ops.wm.open_mainfile(filepath=str(native)); bpy.context.scene.frame_set(1); bpy.context.view_layer.update()
        assert helper['scene_snapshot']() == after, 'V10 save/reload snapshot mismatch'
        assert sha(BASE) == BASE_SHA, 'Pinned source changed during study'
        view_rows += render_set(BASE, 'before')
        view_rows += render_set(native, 'after')
        view_rows += render_set(native, 'open', .125)

    receipt = {
        'status': result_status,
        'generatedAtUtc': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
        'blenderVersion': bpy.app.version_string,
        'base': artifact(BASE), 'native': artifact(native) if native else None,
        'generator': artifact(AUDIT/'executed-generator.py'), 'helper': artifact(HELPER), 'renderer': artifact(RENDERER),
        'changedMeshes': changed_meshes_actual,
        'construction': {'operation': 'Boolean Difference applied to only two fixed mounting plates; brow remains exact.',
                        'cutter': 'Sequential exact Difference against the unchanged evaluated brow solid and eight copies translated by Cartesian ±1 mm corner offsets; not a mathematically complete Minkowski dilation.',
                        'cuttersRemoved': True, 'liveBooleanModifiers': [], 'cutterReceipts': cutter_receipts},
        'preservation': {'other697MeshSnapshotsExact': all_other_meshes_exact,
                         '51PivotsExact': before['empties'] == after['empties'],
                         '462GuidesExact': before['curves'] == after['curves'],
                         'allObjectWorldMatricesMaxErrorM': max_world_error,
                         'allMaterialsExact': mats_before == material_signatures(helper),
                         'fullBrowsGeometryAndTransformExact': all(before['meshes'][name] == after['meshes'][name] for name in brows),
                         'opticAndPassiveHousingGeometryExact': all(before['meshes'][name] == after['meshes'][name] for name in optics),
                         'saveReloadExact': bool(native), 'sourceBytesUnchanged': sha(BASE) == BASE_SHA},
        'mountTopologyAndSlivers': topology_rows,
        'opticSeatNeighborhood': seat_rows,
        'opticApertureRayScreen': aperture_rows,
        'orbitalFixingSixConsequences': pin6_rows,
        'openingSweep': {'samples': sweep, 'sampleCount': len(sweep), 'strictCrossingPairPoseCount': len(strict_pair_rows),
                         'limits': 'Rest plus 40 additional discrete normalized lift samples; no continuous clearance certificate.'},
        'views': view_rows,
        'failReasons': fail_reasons,
        'limits': ['The nine-copy offset screen is a local fitted relief, not a mathematically complete Minkowski dilation or source-exact engineering.',
                   'Outer projected fit still needs human visual review; a zero strict-crossing sweep does not prove continuous clearance.',
                   'No runtime export, app selection, browser test, owner acceptance, or publication.']
    }
    receipt_path = AUDIT / 'receipt.json'
    with receipt_path.open('x') as stream:
        json.dump(receipt, stream, indent=2); stream.write('\n')
    readme = AUDIT / 'README.md'
    with readme.open('x') as stream:
        stream.write('# Orbital saddle study V10\n\n')
        stream.write('This one-shot local reconstruction cuts only the two fixed orbital mounting plates with the exact unchanged evaluated brow solid and eight copies translated by Cartesian ±1 mm corner offsets. This preserves brow concavity but is not a mathematically complete Minkowski dilation.\n\n')
        stream.write('See [receipt.json](receipt.json) for native/input hashes, save-reload preservation, optical-seat and pin6 observations, 41 lift samples, topology, and matched views. This proposal is not exported, selected, or accepted.\n')
    print(json.dumps({'status': result_status, 'native': artifact(native) if native else None,
                      'failReasons': fail_reasons, 'strictPairPoses': len(strict_pair_rows),
                      'views': len(view_rows), 'pin6': pin6_rows}))
    if fail_reasons:
        raise RuntimeError('V10 held; no variant retry: ' + '; '.join(fail_reasons))


if __name__ == '__main__':
    main()
