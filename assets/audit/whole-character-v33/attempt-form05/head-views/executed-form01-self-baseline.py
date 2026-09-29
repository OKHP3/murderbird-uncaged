from pathlib import Path
import bpy, json, hashlib
from mathutils import Vector
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree

ROOT = Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
OUT = Path(__file__).parent
NATIVE = ROOT / 'assets/models/whole-character-v33/attempt-form01/murderbird-whole-character-v33.blend'
BOUND = '122076fb0faa92a78d800c6a97e1d8fcad9d3dd19f9a97693bdb26861a2df850'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(NATIVE) == BOUND
bpy.ops.wm.open_mainfile(filepath=str(NATIVE))
bpy.context.view_layer.update()

kernel = (OUT / 'executed-strict-kernel.py').read_text()
exec(kernel[kernel.index('def inside'):kernel.index('poses=[]')])

def evaluated_mesh(obj, depsgraph):
    ev = obj.evaluated_get(depsgraph)
    mesh = ev.to_mesh()
    mesh.calc_loop_triangles()
    verts = [ev.matrix_world @ v.co for v in mesh.vertices]
    tris = [tuple(t.vertices) for t in mesh.loop_triangles]
    ev.to_mesh_clear()
    return (obj.name, verts, tris, BVHTree.FromPolygons(verts, tris, all_triangles=True))

groups = {
    'cranial-cover': sorted([o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith('V33 swept cranial leaf ')], key=lambda o: o.name),
    'head': sorted([o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith('V33 swept temporal leaf ')], key=lambda o: o.name),
}
assert len(groups['cranial-cover']) == 29
assert len(groups['head']) == 14
dg = bpy.context.evaluated_depsgraph_get()
pairs_by_owner = {}
for owner, objects in groups.items():
    items = [evaluated_mesh(o, dg) for o in objects]
    pairs = []
    bvh_candidate_mesh_pair_count = 0
    total_bvh_candidate_triangle_pairs = 0
    for i, a in enumerate(items):
        for b in items[i + 1:]:
            candidates = a[3].overlap(b[3])
            if candidates:
                bvh_candidate_mesh_pair_count += 1
                total_bvh_candidate_triangle_pairs += len(candidates)
            strict = []
            first = None
            for ia, ib in candidates:
                A = [a[1][k] for k in a[2][ia]]
                B = [b[1][k] for k in b[2][ib]]
                if any(edge(A[k], A[(k + 1) % 3], B) or edge(B[k], B[(k + 1) % 3], A) for k in range(3)):
                    strict.append([ia, ib])
                    if first is None:
                        first = {'triangleIndices': [ia, ib], 'triangleAWorld': [list(v) for v in A], 'triangleBWorld': [list(v) for v in B], 'combinedCentroidWorld': list(sum(A + B, Vector()) / 6)}
            if strict:
                pairs.append({'meshA': a[0], 'meshB': b[0], 'owner': owner, 'bvhCandidateTrianglePairs': len(candidates), 'strictCrossingTrianglePairs': len(strict), 'firstWitness': first})
    pairs_by_owner[owner] = {'leafMeshCount': len(objects), 'candidateMeshPairCount': len(objects) * (len(objects) - 1) // 2, 'bvhCandidateMeshPairCount': bvh_candidate_mesh_pair_count, 'totalBvhCandidateTrianglePairs': total_bvh_candidate_triangle_pairs, 'strictCrossingMeshPairCount': len(pairs), 'pairs': pairs}

assert sha(NATIVE) == BOUND
result = {
    'nativeSHA256': BOUND,
    'executedScreenSHA256': sha(Path(__file__)),
    'kernelSHA256': sha(OUT / 'executed-strict-kernel.py'),
    'scope': 'Distinct V33 swept cranial leaf pairs owned by cranial-cover and distinct swept temporal leaf pairs owned by head, at native rest. Cross-owner cranial/temporal pairs and intra-mesh self-intersections are excluded. Each mesh is evaluated and transformed to world space before BVH overlap and strict edge-through-face confirmation.',
    'method': 'Reused frozen proper-crossing kernel: 1e-7 plane epsilon and 1e-6 barycentric/edge margin. BVH candidates are reported separately from strict crossings; coplanar/tangent/containment cases are not established. No intra-mesh self-intersection check.',
    'pose': 'native rest (jaw delta 0, cranial-cover lift 0)',
    'groups': pairs_by_owner,
    'nativeUnchanged': sha(NATIVE) == BOUND,
}
(OUT / 'form01-baseline-same-owner-leaf-screen.json').write_text(json.dumps(result, indent=2) + '\n')
# Same-owner inter-mesh screen above intentionally excludes self-intersection. This separate pass checks each evaluated leaf mesh against its own triangles, discarding all candidate triangle pairs sharing a vertex before strict confirmation.
def triangle_role(triangle_index):
    polygon_index = triangle_index // 2
    if polygon_index < 840:
        cell = polygon_index // 2
        i, j = divmod(cell, 14)
        return {'surface': 'outer' if polygon_index % 2 == 0 else 'inner', 'uCell': i, 'vCell': j, 'uCenter': (i + .5) / 30, 'vCenter': (j + .5) / 14}
    edge = polygon_index - 840
    if edge < 15: role = 'root-rim'
    elif edge < 45: role = 'v-max-rim'
    elif edge < 59: role = 'tip-rim'
    else: role = 'v-min-rim'
    return {'surface': role, 'rimSegment': edge}
self_results = []
role_histogram = {}
u_histogram = {'u<0.2': 0, '0.2<=u<0.8': 0, 'u>=0.8': 0, 'rim': 0}
for owner, objects in groups.items():
    for obj in objects:
        item = evaluated_mesh(obj, dg)
        candidates = item[3].overlap(item[3])
        tested = 0
        strict = []
        for ia, ib in candidates:
            if ia >= ib:
                continue
            tri_a, tri_b = item[2][ia], item[2][ib]
            if set(tri_a).intersection(tri_b):
                continue
            tested += 1
            A = [item[1][k] for k in tri_a]
            B = [item[1][k] for k in tri_b]
            if any(edge(A[k], A[(k + 1) % 3], B) or edge(B[k], B[(k + 1) % 3], A) for k in range(3)):
                role_a, role_b = triangle_role(ia), triangle_role(ib)
                role_key = role_a['surface'] + ' x ' + role_b['surface']
                role_histogram[role_key] = role_histogram.get(role_key, 0) + 1
                stations = [role_a.get('uCenter'), role_b.get('uCenter')]
                for u in stations:
                    if u is None: u_histogram['rim'] += 1
                    elif u < .2: u_histogram['u<0.2'] += 1
                    elif u < .8: u_histogram['0.2<=u<0.8'] += 1
                    else: u_histogram['u>=0.8'] += 1
                strict.append({'triangleIndices': [ia, ib], 'triangleRoles': [role_a, role_b], 'triangleAVertices': list(tri_a), 'triangleBVertices': list(tri_b), 'triangleAWorld': [list(v) for v in A], 'triangleBWorld': [list(v) for v in B], 'combinedCentroidWorld': list(sum(A + B, Vector()) / 6)})
        self_results.append({'owner': owner, 'mesh': obj.name, 'vertexCount': len(item[1]), 'triangleCount': len(item[2]), 'rawSelfBVHCandidates': len(candidates), 'testedNonAdjacentCandidatePairs': tested, 'strictNonAdjacentSelfCrossingCount': len(strict), 'witnesses': strict[:20]})
self_out = {'nativeSHA256': BOUND, 'executedScreenSHA256': sha(Path(__file__)), 'kernelSHA256': sha(OUT / 'executed-strict-kernel.py'), 'method': 'Evaluated triangle self-overlap per V33 cranial/temporal leaf mesh at native rest. Candidate pairs are canonicalized to ia<ib and excluded if triangles share any vertex; remaining BVH candidates use frozen strict edge-through-face test (1e-7 plane epsilon, 1e-6 barycentric/edge margin). No containment or coplanar/tangent proof.', 'meshesWithStrictNonAdjacentSelfCrossings': sum(bool(x['strictNonAdjacentSelfCrossingCount']) for x in self_results), 'strictNonAdjacentSelfCrossingTrianglePairCount': sum(x['strictNonAdjacentSelfCrossingCount'] for x in self_results), 'triangleRolePairHistogram': role_histogram, 'uStationParticipationHistogram': u_histogram, 'meshes': self_results, 'nativeUnchanged': sha(NATIVE) == BOUND}
(OUT / 'form01-baseline-leaf-self-triangle-screen.json').write_text(json.dumps(self_out, indent=2) + '\n')
print(json.dumps({'ownerPairStrictCounts': {k: v['strictCrossingMeshPairCount'] for k, v in pairs_by_owner.items()}, 'selfCrossingMeshes': self_out['meshesWithStrictNonAdjacentSelfCrossings'], 'selfCrossingTrianglePairs': self_out['strictNonAdjacentSelfCrossingTrianglePairCount']}, indent=2), flush=True)
