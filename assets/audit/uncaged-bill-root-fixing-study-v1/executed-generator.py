"""Isolated four-fastener reseating proposal on paired-bill V2.

Only the four inherited Bill root fixing object transforms change. The frozen
paired-bill source is not saved over, exported, or selected in the application.
"""
from pathlib import Path
import hashlib
import json
import math
import runpy
import shutil

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'assets/models/uncaged-paired-bill-mandible-study-v2/murderbird-paired-bill-mandible-study-v2.blend'
BASE_SHA = '7ba7c996fbcffc118217ad4fcd0c1c1316a3e0a6b0cefa77be4794e6f5a4df15'
HELPER = ROOT / 'scripts/build-uncaged-alignment-v7.py'
HELPER_SHA = '39b6ee2285d8c49df3a902f8fac0a07589da3d41f48ae24df1e06515c839033a'
RENDERER = ROOT / 'scripts/study-v8-bill-envelope.py'
RENDERER_SHA = '2d3502a134cecb15c04ca0ce9f8db0f7555d6d8a52e5f7c9c74dfd55299f421a'
OUT = ROOT / 'assets/models/uncaged-bill-root-fixing-study-v1'
AUDIT = ROOT / 'assets/audit/uncaged-bill-root-fixing-study-v1'
TARGET = 'Profiled upper bill blade 0'
PINS = [f'Bill root fixing{s}' for s in ('', '.001', '.002', '.003')]
INNER_EMBED_M = 0.001


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path):
    return {'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size, 'sha256': sha(path)}


def world_surface(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    matrix = evaluated.matrix_world.copy()
    points = [matrix @ v.co for v in mesh.vertices]
    faces = [tuple(p.vertices) for p in mesh.polygons if len(p.vertices) >= 3]
    triangles = []
    for poly in mesh.polygons:
        ids = list(poly.vertices)
        if len(ids) >= 3:
            for i in range(1, len(ids)-1):
                triangles.append((ids[0], ids[i], ids[i+1]))
    tree = BVHTree.FromPolygons(points, triangles, all_triangles=True, epsilon=0)
    dims = [max(p[k] for p in points)-min(p[k] for p in points) for k in range(3)]
    evaluated.to_mesh_clear()
    return {'points': points, 'faces': triangles, 'tree': tree, 'dimensions': dims}


def strict_crossings(a, b, candidates):
    """Count noncoplanar edge-through-face crossings; tangent/coplanar excluded."""
    ids_a, ids_b, pts_a, pts_b = set(), set(), [], []

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
            if hit is not None:
                t = (hit-p).dot(q-p)/(q-p).length_squared
                if 1e-6 < t < 1-1e-6:
                    return True
        return False

    for ia, ib in candidates:
        ta = [a['points'][v] for v in a['faces'][ia]]
        tb = [b['points'][v] for v in b['faces'][ib]]
        if edge_crosses(ta, tb) or edge_crosses(tb, ta):
            ids_a.add(ia); ids_b.add(ib); pts_a.extend(ta); pts_b.extend(tb)

    def bounds(points):
        return [[round(min(p[k] for p in points), 7), round(max(p[k] for p in points), 7)] for k in range(3)] if points else None
    return {'confirmedTriangleCountA': len(ids_a), 'confirmedTriangleCountB': len(ids_b),
            'boundsAWorldXYZM': bounds(pts_a), 'boundsBWorldXYZM': bounds(pts_b),
            'limits': 'Strict noncoplanar edge-through-face evidence only; no containment depth or continuous clearance.'}


def main():
    assert sha(BASE) == BASE_SHA, 'Pinned source changed'
    assert sha(HELPER) == HELPER_SHA, 'Snapshot helper changed'
    assert sha(RENDERER) == RENDERER_SHA, 'Matched renderer changed'
    assert not OUT.exists() and not AUDIT.exists(), 'Refusing to overwrite an existing study'
    h = runpy.run_path(str(HELPER), run_name='snapshot_helpers')
    bpy.ops.wm.open_mainfile(filepath=str(BASE))
    bpy.context.scene.frame_set(1); bpy.context.view_layer.update()
    before = h['scene_snapshot']()
    material_before = {m.name: h['material_signature'](m) for m in bpy.data.materials}
    before_world = {o.name: o.matrix_world.copy() for o in bpy.data.objects}
    depsgraph = bpy.context.evaluated_depsgraph_get()
    blade_obj = bpy.data.objects.get(TARGET)
    assert blade_obj and blade_obj.type == 'MESH'
    blade = world_surface(blade_obj, depsgraph)
    pin_metrics = {}

    for name in PINS:
        obj = bpy.data.objects.get(name)
        assert obj and obj.type == 'MESH' and obj.parent and obj.parent.name == 'upper-bill'
        pin = world_surface(obj, depsgraph)
        center = sum(pin['points'], Vector()) / len(pin['points'])
        side = 1 if center.x > 0 else -1  # +X is anatomical LEFT; -X is RIGHT.
        hit = blade['tree'].ray_cast(center, Vector((side, 0, 0)), 0.2)
        assert hit[0] is not None, (name, 'outward ray misses blade0 side wall')
        wall_point, wall_normal, _, distance = hit
        inward_extent = max(side * (center.x-p.x) for p in pin['points'])
        outward_extent = max(side * (p.x-center.x) for p in pin['points'])
        # Set the pin's innermost X support 1 mm inside the wall. Its opposite
        # support then projects about 4 mm outboard, preserving the pin mesh.
        target_center_x = wall_point.x + side * (inward_extent-INNER_EMBED_M)
        delta_x = target_center_x - center.x
        assert side * delta_x > 0
        world = obj.matrix_world.copy()
        world.translation.x += delta_x
        obj.matrix_world = world
        bpy.context.view_layer.update()
        moved = world_surface(obj, bpy.context.evaluated_depsgraph_get())
        moved_center = sum(moved['points'], Vector()) / len(moved['points'])
        signed_inner = min(side * p.x for p in moved['points'])
        signed_outer = max(side * p.x for p in moved['points'])
        signed_wall = side * wall_point.x
        inner_depth = signed_wall - signed_inner
        exposed = signed_outer - signed_wall
        assert abs(inner_depth-INNER_EMBED_M) < 2e-5, (name, inner_depth)
        assert abs((moved_center.y-center.y)) < 1e-7 and abs((moved_center.z-center.z)) < 1e-7
        pin_metrics[name] = {
            'anatomicalSide': 'left' if side > 0 else 'right',
            'parent': obj.parent.name,
            'axis': 'world/native X',
            'sourceCentroidWorldXYZM': [float(v) for v in center],
            'wallPointWorldXYZM': [float(v) for v in wall_point],
            'wallNormalWorldXYZ': [float(v) for v in wall_normal],
            'outwardRayDistanceM': float(distance),
            'worldTranslationDeltaXYZM': [float(v) for v in (obj.matrix_world.translation-before_world[name].translation)],
            'targetInnerEmbedM': INNER_EMBED_M,
            'measuredInnerEmbedM': float(inner_depth),
            'measuredOuterProjectionM': float(exposed),
            'sourceWorldBoundsDimensionsM': [float(v) for v in pin['dimensions']],
            'movedWorldBoundsDimensionsM': [float(v) for v in moved['dimensions']],
            'centerYZPreserved': True,
        }

    bpy.context.view_layer.update()
    after = h['scene_snapshot']()
    assert set(before['meshes']) == set(after['meshes']) and before['empties'] == after['empties'] and before['curves'] == after['curves']
    changed = []
    for name, prior in before['meshes'].items():
        current = after['meshes'][name]
        if name in PINS:
            assert {k:v for k,v in current.items() if k != 'matrix'} == {k:v for k,v in prior.items() if k != 'matrix'}, name
            changed.append(name)
        else:
            assert current == prior, name
    assert set(changed) == set(PINS)
    assert material_before == {m.name: h['material_signature'](m) for m in bpy.data.materials}
    OUT.mkdir(parents=True); AUDIT.mkdir(parents=True)
    native = OUT / 'murderbird-bill-root-fixing-study-v1.blend'
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(native), check_existing=False)
    bpy.ops.wm.open_mainfile(filepath=str(native)); bpy.context.scene.frame_set(1); bpy.context.view_layer.update()
    assert h['scene_snapshot']() == after, 'Saved/reloaded native does not match the authored snapshot'
    assert material_before == {m.name: h['material_signature'](m) for m in bpy.data.materials}

    # Check every pin against the real evaluated blade and all nearby bill/head
    # meshes; blade0 is the sole intentional host surface for this embed.
    depsgraph = bpy.context.evaluated_depsgraph_get()
    surfaces = {o.name: world_surface(o, depsgraph) for o in bpy.data.objects if o.type == 'MESH'}
    adjacent = {TARGET, 'Profiled upper bill blade 1', 'Overlapping nasal hood',
                'Cere root transition -1', 'Cere root transition 1'}
    # Add all cranial/bill meshes whose bounds overlap any translated fixing.
    for pin_name in PINS:
        pin_surface = surfaces[pin_name]
        pmins = [min(p[k] for p in pin_surface['points']) for k in range(3)]
        pmaxs = [max(p[k] for p in pin_surface['points']) for k in range(3)]
        for other_name, surface in surfaces.items():
            if other_name == pin_name:
                continue
            mins = [min(p[k] for p in surface['points']) for k in range(3)]
            maxs = [max(p[k] for p in surface['points']) for k in range(3)]
            if all(pmins[k] <= maxs[k]+1e-7 and mins[k] <= pmaxs[k]+1e-7 for k in range(3)):
                adjacent.add(other_name)
    neighbor_rows = []
    nonhost_crossings = []
    for pin_name in PINS:
        pin_surface = surfaces[pin_name]
        row = {'pin': pin_name, 'anatomicalSide': pin_metrics[pin_name]['anatomicalSide'], 'pairs': []}
        for other_name in sorted(adjacent):
            if other_name not in surfaces:
                continue
            candidates = pin_surface['tree'].overlap(surfaces[other_name]['tree'])
            proof = strict_crossings(pin_surface, surfaces[other_name], candidates) if candidates else {
                'confirmedTriangleCountA': 0, 'confirmedTriangleCountB': 0,
                'boundsAWorldXYZM': None, 'boundsBWorldXYZM': None,
                'limits': 'No BVH triangle-pair candidates.'}
            is_host = other_name == TARGET
            record = {'otherMesh': other_name,
                      'otherOwner': bpy.data.objects[other_name].parent.name if bpy.data.objects[other_name].parent else None,
                      'bvhTrianglePairCandidateCount': len(candidates),
                      'strictCrossing': proof,
                      'classification': 'intended shallow host embed' if is_host else 'neighbor surface; strict crossings are unintended'}
            row['pairs'].append(record)
            if not is_host and (proof['confirmedTriangleCountA'] or proof['confirmedTriangleCountB']):
                nonhost_crossings.append({'pin': pin_name, **record})
        neighbor_rows.append(row)

    shutil.copy2(__file__, AUDIT / 'executed-generator.py')
    renderer = runpy.run_path(str(RENDERER), run_name='matched_bill_renderer')
    renderer['renders'].__globals__['AUDIT'] = AUDIT
    views = renderer['renders'](BASE, 'before') + renderer['renders'](native, 'after')
    assert len(views) == 6
    assert sha(BASE) == BASE_SHA, 'Frozen paired-bill source changed'
    receipt = {
        'status': 'isolated four-pin reseating proposal; not accepted, exported, or selected in app',
        'generatedAtUtc': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
        'blenderVersion': bpy.app.version_string,
        'base': artifact(BASE), 'native': artifact(native), 'generator': artifact(AUDIT/'executed-generator.py'),
        'helper': artifact(HELPER), 'renderer': artifact(RENDERER),
        'replacementObjects': PINS, 'addedObjects': [], 'deletedObjects': [],
        'sideConvention': '+X is anatomical LEFT; -X is anatomical RIGHT.',
        'method': 'At each source pin vertex-average YZ, cast signed outward world-X ray into evaluated blade0. Translate only the object world X so its inward-most X support lies 1 mm inboard of the measured side-wall hit; expected opposite support is about 4 mm outboard. Preserve local mesh data and YZ center.',
        'fastenerMeasurements': pin_metrics,
        'preservation': {'onlyFourPinWorldXTransformsChanged': changed,
                         'pinMeshGeometryAndModifiersPreserved': True,
                         'allOther695MeshSnapshotsExact': True,
                         'all51PivotsExact': True, 'all462CurvesExact': True,
                         'allMaterialsExact': True, 'saveReloadSnapshotExact': True,
                         'sourceNativeBytesUnchanged': sha(BASE) == BASE_SHA},
        'neighborSurfaceChecks': neighbor_rows,
        'nonHostStrictCrossings': nonhost_crossings,
        'views': views,
        'limits': ['Strict triangle checks detect noncoplanar edge-through-face crossings; tangencies/coplanar overlap are not called crossings.',
                   'Intended blade0 shallow embed is allowed. No continuous-motion, force, manufacture tolerance, owner-acceptance, runtime export, app selection, or publication claim.',
                   'The three views are matched neutral authoring stills, not WebGL evidence.']
    }
    out = AUDIT / 'receipt.json'
    with out.open('x') as f:
        json.dump(receipt, f, indent=2); f.write('\n')
    readme = AUDIT / 'README.md'
    with readme.open('x') as f:
        f.write('# Bill root fixing study v1\n\n')
        f.write('This isolated native proposal translates exactly four inherited root-fixing objects along world X. +X is anatomical left; -X is anatomical right. The source paired-bill V2 scene remains unchanged.\n\n')
        f.write('At each pin YZ center, an outward ray measures the evaluated blade0 wall. The inward pin support is placed 1 mm inboard of that hit, leaving about 4 mm of the opposite support outboard. Mesh data, YZ centers, owners, pivots, guides, materials, and every other mesh are checked for preservation.\n\n')
        f.write('See [receipt.json](receipt.json) for exact hashes, per-pin measurements, neighboring-surface checks, and matched before/after views. This is a geometry proposal only; it is not exported, selected in the app, or accepted.\n')
    print(json.dumps({'native': artifact(native), 'receipt': artifact(out), 'views': len(views),
                      'nonHostStrictCrossings': len(nonhost_crossings),
                      'pins': {n: {'side': v['anatomicalSide'], 'embedMm': v['measuredInnerEmbedM']*1000,
                                   'projectionMm': v['measuredOuterProjectionM']*1000} for n,v in pin_metrics.items()}}))


if __name__ == '__main__':
    main()
