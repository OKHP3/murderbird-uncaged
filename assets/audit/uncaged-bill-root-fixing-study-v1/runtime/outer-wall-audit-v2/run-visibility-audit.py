"""Read-only outside-in X-axis visibility audit against every native head mesh."""
from pathlib import Path
import hashlib
import json
import math

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[5]
NATIVE = ROOT / 'assets/models/uncaged-bill-root-fixing-study-v1/murderbird-bill-root-fixing-study-v1.blend'
NATIVE_SHA = '4d7568d1c2ba7cab716876f57a6c20cb6a788d4daeef1d5d34f85c1910ed2bbe'
GLB = ROOT / 'assets/models/uncaged-bill-root-fixing-study-v1/murderbird-bill-root-fixing-study-v1.glb'
GLB_SHA = 'f5c0f5ad99ace316ed84426d2a1148a093706612c9602d78b93023d46d989e6e'
OUT = Path(__file__).resolve().parent
PINS = [f'Bill root fixing{s}' for s in ('', '.001', '.002', '.003')]
RAY_ORIGIN_ABS_X = .4


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path):
    return {'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size, 'sha256': sha(path)}


def evaluated_triangles(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    mesh.calc_loop_triangles()
    points = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
    triangles = [tuple(tri.vertices) for tri in mesh.loop_triangles]
    tree = BVHTree.FromPolygons(points, triangles, all_triangles=True, epsilon=0)
    topology = {'vertices': len(points), 'polygons': len(mesh.polygons), 'evaluatedLoopTriangles': len(triangles)}
    evaluated.to_mesh_clear()
    return {'tree': tree, 'topology': topology}


def one_hit(tree, origin, direction, distance=.8):
    loc, normal, triangle, ray_distance = tree.ray_cast(origin, direction, distance)
    if loc is None:
        return None
    return {'pointWorldXYZM': [float(v) for v in loc], 'normalWorldXYZ': [float(v) for v in normal],
            'triangleIndex': int(triangle), 'distanceFromOutsideOriginM': float(ray_distance)}


def main():
    assert sha(NATIVE) == NATIVE_SHA and sha(GLB) == GLB_SHA
    assert not (OUT / 'visibility-audit.json').exists(), 'Refusing to overwrite visibility audit'
    bpy.ops.wm.open_mainfile(filepath=str(NATIVE))
    bpy.context.scene.frame_set(1); bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    all_head = [obj for obj in bpy.data.objects if obj.type == 'MESH' and obj.get('region') == 'head']
    assert all_head, 'No meshes tagged region=head'
    head_surfaces = {obj.name: evaluated_triangles(obj, depsgraph) for obj in all_head}
    out = []
    for pin_name in PINS:
        pin_obj = bpy.data.objects[pin_name]
        pin_surface = head_surfaces[pin_name]
        # The object-axis test line is through the actual evaluated pin centroid YZ.
        ev_pin = pin_obj.evaluated_get(depsgraph); mesh = ev_pin.to_mesh()
        pin_points = [ev_pin.matrix_world @ vertex.co for vertex in mesh.vertices]
        ev_pin.to_mesh_clear()
        centroid = sum(pin_points, Vector()) / len(pin_points)
        side = 1 if centroid.x > 0 else -1
        origin = Vector((side * RAY_ORIGIN_ABS_X, centroid.y, centroid.z))
        direction = Vector((-side, 0, 0))
        own_hit = one_hit(head_surfaces[pin_name]['tree'], origin, direction)
        hits = []
        for obj in all_head:
            if obj.name == pin_name:
                continue
            hit = one_hit(head_surfaces[obj.name]['tree'], origin, direction)
            if hit:
                hits.append({'mesh': obj.name,
                             'owner': obj.parent.name if obj.parent else None,
                             'region': obj.get('region'),
                             'surfaceRole': obj.get('surfaceRole'),
                             'exteriorEras': obj.get('exteriorEras'),
                             **hit,
                             'beforePinOutwardSurface': bool(own_hit and hit['distanceFromOutsideOriginM'] < own_hit['distanceFromOutsideOriginM'] - 1e-6),
                             'afterPinOutwardSurface': bool(own_hit and hit['distanceFromOutsideOriginM'] > own_hit['distanceFromOutsideOriginM'] + 1e-6)})
        hits.sort(key=lambda row: row['distanceFromOutsideOriginM'])
        blockers = [row for row in hits if row['beforePinOutwardSurface']]
        out.append({'pin': pin_name, 'anatomicalSide': 'left' if side > 0 else 'right',
                    'pinParent': pin_obj.parent.name if pin_obj.parent else None,
                    'pinWorldCentroidXYZM': [float(v) for v in centroid],
                    'ray': {'originWorldXYZM': [float(v) for v in origin],
                            'directionWorldXYZ': [float(v) for v in direction]},
                    'pinOutwardSurfaceHit': own_hit,
                    'firstOtherHeadMeshHit': hits[0] if hits else None,
                    'firstOccludingMeshBeforePinHead': blockers[0] if blockers else None,
                    'allOtherHeadMeshHitsSorted': hits})
    result = {
        'status': 'read-only signed-X axis visibility audit across all meshes tagged region=head',
        'generatedAtUtc': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
        'blenderVersion': bpy.app.version_string,
        'native': artifact(NATIVE), 'glb': artifact(GLB), 'script': artifact(Path(__file__).resolve()),
        'scope': {'headRegionMeshCount': len(all_head), 'excludedOnly': PINS,
                  'selectionRule': "Every evaluated MESH with region == 'head'; no parent, era, role, collider, or surface-pair simplification.",
                  'representation': 'Evaluated native mesh; Blender calc_loop_triangles() triangles; BVH one-hit per opaque head-region mesh.'},
        'rayOriginAbsXM': RAY_ORIGIN_ABS_X,
        'pins': out,
        'limits': ['This is a single world-X line per fastener through its vertex-average YZ, not a projected area, multi-view visibility, or rendered occlusion test.',
                   'Every region=head mesh is treated as opaque regardless of era visibility; exteriorEras is reported for interpreting hits.',
                   'Only exact first intersections are measured; no collision, containment, or design-intent claim.']
    }
    path = OUT / 'visibility-audit.json'
    with path.open('x') as stream:
        json.dump(result, stream, indent=2); stream.write('\n')
    print(json.dumps({'meshCount': len(all_head), 'pins': {
        row['pin']: {'pinOutwardSurfaceX': row['pinOutwardSurfaceHit']['pointWorldXYZM'][0] if row['pinOutwardSurfaceHit'] else None,
                     'firstOther': None if row['firstOtherHeadMeshHit'] is None else row['firstOtherHeadMeshHit']['mesh'],
                     'firstOccluder': None if row['firstOccludingMeshBeforePinHead'] is None else row['firstOccludingMeshBeforePinHead']['mesh'],
                     'aheadHits': sum(hit['beforePinOutwardSurface'] for hit in row['allOtherHeadMeshHitsSorted'])}
        for row in out}, 'receipt': str(path)}))


if __name__ == '__main__':
    main()
