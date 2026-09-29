import bpy
import hashlib
import json
import math
import os
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..'))
BASE_REL = 'assets/models/whole-character-v21/attempt-construction06/murderbird-whole-character-v21.blend'
CANDIDATE_REL = 'assets/models/whole-character-v22/attempt-frame03/murderbird-whole-character-v22.blend'
BASE_SHA = '79ad3e368e7b75edbbc758b1264a1ccaf34f284c6ca185ee8441875576a6f54c'
CANDIDATE_SHA = 'd409bc72d0ce79ca8c7e2941b720573f2f1d203a006f179d928ea921da713d59'
RECEIPT_REL = 'assets/audit/whole-character-v22/attempt-frame03/receipt.json'
OUT = os.path.dirname(__file__)
OWNER_ROOTS = {'body', 'breastplate', 'neck', 'cervical-upper', 'head', 'jaw'}
FEET_ROOTS = {'left-foot', 'left-toes', 'right-foot', 'right-toes'}
EXPECTED_HEAD_DELTA = Vector((0.0, -0.04259999841451645, 0.02280000038444996))


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def object_parent_name(obj):
    return obj.parent.name if obj.parent else None


def under_any(obj, names):
    cursor = obj
    while cursor:
        if cursor.name in names:
            return True
        cursor = cursor.parent
    return False


def mesh_snapshot(obj):
    matrix = obj.matrix_world.copy()
    verts = [matrix @ v.co for v in obj.data.vertices]
    faces = [tuple(p.vertices) for p in obj.data.polygons]
    edges = [tuple(e.vertices) for e in obj.data.edges]
    return {'verts': verts, 'faces': faces, 'edges': edges}


def load_scene(path):
    bpy.ops.wm.open_mainfile(filepath=path)
    bpy.context.view_layer.update()
    return {o.name: o for o in bpy.data.objects}


def max_distance(a, b):
    if len(a) != len(b):
        return None
    return max((x - y).length for x, y in zip(a, b)) if a else 0.0


def nearest_articulated_owner(obj):
    cursor = obj
    while cursor:
        if cursor.name in OWNER_ROOTS:
            return cursor.name
        cursor = cursor.parent
    return None


def world_mesh(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        matrix = evaluated.matrix_world
        verts = [matrix @ v.co for v in mesh.vertices]
        polys = [tuple(poly.vertices) for poly in mesh.polygons]
        if len(verts) < 3 or not polys:
            return None
        tree = BVHTree.FromPolygons(verts, polys, all_triangles=False, epsilon=0.0)
        bounds = tuple((min(v[i] for v in verts), max(v[i] for v in verts)) for i in range(3))
        return tree, verts, polys, bounds
    finally:
        evaluated.to_mesh_clear()


def bounds_overlap(a, b, epsilon=1e-6):
    return all(a[i][0] <= b[i][1] + epsilon and b[i][0] <= a[i][1] + epsilon for i in range(3))


def scene_snapshot(path):
    objects = load_scene(path)
    empties = {n: o for n, o in objects.items() if o.type == 'EMPTY'}
    meshes = {n: o for n, o in objects.items() if o.type == 'MESH'}
    mesh_ancestors = {}
    for name, obj in meshes.items():
        chain = []
        cursor = obj
        while cursor:
            chain.append(cursor.name)
            cursor = cursor.parent
        mesh_ancestors[name] = chain
    snap = {
        'emptyParents': {n: object_parent_name(o) for n, o in empties.items()},
        'emptyWorld': {n: o.matrix_world.copy() for n, o in empties.items()},
        'meshData': {n: mesh_snapshot(o) for n, o in meshes.items()},
        'meshNames': set(meshes),
        'meshAncestors': mesh_ancestors,
    }
    return snap


def pairwise_shape_check(base, candidate, names):
    checked = []
    failures = []
    for name in names:
        if name not in base['meshData'] or name not in candidate['meshData']:
            failures.append({'name': name, 'issue': 'missing corresponding mesh'})
            continue
        a, b = base['meshData'][name], candidate['meshData'][name]
        if len(a['verts']) != len(b['verts']) or a['faces'] != b['faces'] or a['edges'] != b['edges']:
            failures.append({'name': name, 'issue': 'mesh topology or vertex count changed'})
            continue
        # Compare all indexed world-space edge lengths: translation/rotation is allowed,
        # while scale or geometric reshaping is not.
        edge_delta = 0.0
        for i, j in a['edges']:
            da = (a['verts'][i] - a['verts'][j]).length
            db = (b['verts'][i] - b['verts'][j]).length
            edge_delta = max(edge_delta, abs(da - db))
        # Also compare the complete indexed point-cloud distances from its centroid,
        # which catches edits to isolated/unconnected vertices.
        ca = sum(a['verts'], Vector()) / max(1, len(a['verts']))
        cb = sum(b['verts'], Vector()) / max(1, len(b['verts']))
        radial_delta = max((abs((va - ca).length - (vb - cb).length) for va, vb in zip(a['verts'], b['verts'])), default=0.0)
        checked.append({'name': name, 'vertexCount': len(a['verts']), 'edgeLengthMaxDeltaM': edge_delta, 'radialProfileMaxDeltaM': radial_delta})
    return checked, failures


def rest_crossings(path):
    objects = load_scene(path)
    groups = {owner: [] for owner in OWNER_ROOTS}
    for obj in objects.values():
        if obj.type != 'MESH':
            continue
        owner = nearest_articulated_owner(obj)
        if owner:
            groups[owner].append(obj)
    cached = {}
    for owner, members in groups.items():
        for obj in members:
            result = world_mesh(obj)
            if result:
                cached[obj.name] = (owner, *result)

    intersections = []
    pair_tests = 0
    names = sorted(cached)
    for idx, name_a in enumerate(names):
        owner_a, tree_a, verts_a, faces_a, bounds_a = cached[name_a]
        for name_b in names[idx + 1:]:
            owner_b, tree_b, verts_b, faces_b, bounds_b = cached[name_b]
            if owner_a == owner_b or not bounds_overlap(bounds_a, bounds_b):
                continue
            pair_tests += 1
            overlap = tree_a.overlap(tree_b)
            if not overlap:
                continue
            # Keep the record bounded and identify the approximate region from a small
            # deterministic sample of overlapping triangle-centroid pairs.
            sample = overlap[:min(200, len(overlap))]
            points = []
            for face_a, face_b in sample:
                if face_a >= len(faces_a) or face_b >= len(faces_b):
                    continue
                ca = sum((verts_a[i] for i in faces_a[face_a]), Vector()) / len(faces_a[face_a])
                cb = sum((verts_b[i] for i in faces_b[face_b]), Vector()) / len(faces_b[face_b])
                points.append((ca + cb) * 0.5)
            center = sum(points, Vector()) / len(points) if points else Vector()
            intersections.append({
                'ownerA': owner_a, 'objectA': name_a,
                'ownerB': owner_b, 'objectB': name_b,
                'overlapFacePairCount': len(overlap),
                'sampledIntersectionCentroidNative': [round(float(v), 6) for v in center],
                'sampleCountForCentroid': len(points),
            })
    intersections.sort(key=lambda item: item['overlapFacePairCount'], reverse=True)
    return {'objectCountByOwner': {k: len(v) for k, v in groups.items()}, 'bboxCandidatePairTests': pair_tests, 'intersectingObjectPairs': len(intersections), 'worstPairs': intersections[:12]}


def main():
    base_path = os.path.join(ROOT, BASE_REL)
    candidate_path = os.path.join(ROOT, CANDIDATE_REL)
    receipt_path = os.path.join(ROOT, RECEIPT_REL)
    for path, expected in ((base_path, BASE_SHA), (candidate_path, CANDIDATE_SHA)):
        if sha(path) != expected:
            raise RuntimeError('Input SHA mismatch: ' + path)
    receipt = json.load(open(receipt_path, 'r'))
    expected_bearing_names = receipt.get('roundBearingMeshes', [])
    base = scene_snapshot(base_path)
    candidate = scene_snapshot(candidate_path)

    empty_names_common = sorted(set(base['emptyParents']) & set(candidate['emptyParents']))
    parent_diffs = [
        {'name': n, 'baseParent': base['emptyParents'][n], 'candidateParent': candidate['emptyParents'][n]}
        for n in empty_names_common if base['emptyParents'][n] != candidate['emptyParents'][n]
    ]
    missing_empty_base = sorted(set(base['emptyParents']) - set(candidate['emptyParents']))
    added_empty = sorted(set(candidate['emptyParents']) - set(base['emptyParents']))
    parent_count = len(empty_names_common)

    common_mesh_names = base['meshNames'] & candidate['meshNames']
    head_names = sorted(n for n in common_mesh_names if 'head' in base['meshAncestors'][n])
    head_results, head_missing = [], []
    for name in head_names:
        a, b = base['meshData'][name]['verts'], candidate['meshData'][name]['verts']
        if len(a) != len(b):
            head_missing.append({'name': name, 'reason': 'vertex count differs'})
            continue
        residual = max(((vb - va) - EXPECTED_HEAD_DELTA).length for va, vb in zip(a, b)) if a else 0.0
        head_results.append({'name': name, 'vertices': len(a), 'maxResidualAfterExpectedTranslationM': residual})

    feet_names = sorted(n for n in common_mesh_names if any(root in base['meshAncestors'][n] for root in FEET_ROOTS))
    feet_results, feet_failures = [], []
    for name in feet_names:
        a, b = base['meshData'][name]['verts'], candidate['meshData'][name]['verts']
        if len(a) != len(b):
            feet_failures.append({'name': name, 'reason': 'vertex count differs'})
            continue
        delta = max_distance(a, b)
        feet_results.append({'name': name, 'vertices': len(a), 'maxWorldVertexDeltaM': delta})

    bearing_results, bearing_failures = pairwise_shape_check(base, candidate, expected_bearing_names)
    # The report is intended to identify current worst local surface intersections,
    # not establish whole-model or motion clearance.
    overlap_results = rest_crossings(candidate_path)

    out = {
        'status': 'independent pinned-native structural comparison plus bounded rest-surface sample; no motion or acceptance claim',
        'inputs': {
            'base': {'path': BASE_REL, 'sha256': BASE_SHA, 'bytes': os.path.getsize(base_path)},
            'candidate': {'path': CANDIDATE_REL, 'sha256': CANDIDATE_SHA, 'bytes': os.path.getsize(candidate_path)},
            'builderReceipt': {'path': RECEIPT_REL, 'sha256': sha(receipt_path)},
        },
        'parentGraph': {
            'commonEmptyNodeCount': parent_count,
            'parentRelationshipChanges': parent_diffs,
            'missingEmptyNodes': missing_empty_base,
            'addedEmptyNodes': added_empty,
            'exact53NodeParentGraphPreserved': parent_count == 53 and not parent_diffs and not missing_empty_base and not added_empty,
        },
        'headRigidTranslation': {
            'expectedNativeDeltaM': list(EXPECTED_HEAD_DELTA),
            'meshCount': len(head_results),
            'maxResidualM': max((r['maxResidualAfterExpectedTranslationM'] for r in head_results), default=0.0),
            'largestResidualMeshes': sorted(head_results, key=lambda r: r['maxResidualAfterExpectedTranslationM'], reverse=True)[:8],
            'vertexCountMismatches': head_missing,
        },
        'feetUnchanged': {
            'meshCount': len(feet_results),
            'maxWorldVertexDeltaM': max((r['maxWorldVertexDeltaM'] for r in feet_results), default=0.0),
            'largestDeltaMeshes': sorted(feet_results, key=lambda r: r['maxWorldVertexDeltaM'], reverse=True)[:8],
            'vertexCountMismatches': feet_failures,
        },
        'bearingShape': {
            'receiptNamedMeshCount': len(expected_bearing_names),
            'checkedMeshCount': len(bearing_results),
            'maxEdgeLengthDeltaM': max((r['edgeLengthMaxDeltaM'] for r in bearing_results), default=0.0),
            'maxCenteredVertexRadiusDeltaM': max((r['radialProfileMaxDeltaM'] for r in bearing_results), default=0.0),
            'largestDeviations': sorted(bearing_results, key=lambda r: max(r['edgeLengthMaxDeltaM'], r['radialProfileMaxDeltaM']), reverse=True)[:8],
            'failures': bearing_failures,
            'method': 'Indexed topology and world-space edge lengths plus centered indexed vertex radii; translation/rotation allowed; no bearing fit or functional clearance inferred.',
        },
        'restCrossOwnerSurfaceSample': {
            'method': 'Evaluated mesh BVH surface-overlap pairs among body, breastplate, neck, cervical-upper, head and jaw owner groups at saved rest pose; approximate overlap-face centroid for localization.',
            **overlap_results,
            'limits': ['Surface overlap does not prove solid containment or distinguish intended mating contact.', 'Scope is limited to listed anatomical owner groups at rest; no joint motion, hardware attachment, or complete scene clearance was tested.'],
        },
    }
    outpath = os.path.join(OUT, 'independent-frame-check.json')
    with open(outpath, 'x') as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write('\n')
    print('WROTE', outpath)
    print(json.dumps({
        'parentCount': parent_count, 'parentDiffs': len(parent_diffs), 'addedEmpties': len(added_empty), 'missingEmpties': len(missing_empty_base),
        'headMeshes': len(head_results), 'headMaxResidual': out['headRigidTranslation']['maxResidualM'],
        'feetMeshes': len(feet_results), 'feetMaxDelta': out['feetUnchanged']['maxWorldVertexDeltaM'],
        'bearingMeshes': len(bearing_results), 'bearingFailures': len(bearing_failures),
        'restCrossOwnerPairs': overlap_results['intersectingObjectPairs'], 'worstPairs': overlap_results['worstPairs'][:6],
    }, indent=2))


main()
