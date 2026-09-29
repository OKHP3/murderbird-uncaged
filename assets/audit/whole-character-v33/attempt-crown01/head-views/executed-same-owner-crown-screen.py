from pathlib import Path
import bpy, json, hashlib
from mathutils import Vector
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree

ROOT = Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
OUT = Path(__file__).parent
NATIVE = ROOT / 'assets/models/whole-character-v33/attempt-crown01/murderbird-whole-character-v33.blend'
BOUND = 'ea4ae32563566b39604e0fd8ced46c74fa8dd74aab7b52edf418913e0215b3c3'
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

crown = sorted([o for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith('V33 swept cranial leaf ')], key=lambda o: o.name)
assert len(crown) == 29, f'Expected 29 distinct V33 cranial leaves, got {len(crown)}'
dg = bpy.context.evaluated_depsgraph_get()
items = [evaluated_mesh(o, dg) for o in crown]
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
                    first = {
                        'triangleIndices': [ia, ib],
                        'triangleAWorld': [list(v) for v in A],
                        'triangleBWorld': [list(v) for v in B],
                        'combinedCentroidWorld': list(sum(A + B, Vector()) / 6),
                    }
        if strict:
            pairs.append({
                'meshA': a[0], 'meshB': b[0],
                'owners': [bpy.data.objects[a[0]].parent.name, bpy.data.objects[b[0]].parent.name],
                'bvhCandidateTrianglePairs': len(candidates),
                'strictCrossingTrianglePairs': len(strict),
                'firstWitness': first,
            })

assert sha(NATIVE) == BOUND
result = {
    'nativeSHA256': BOUND,
    'executedScreenSHA256': sha(Path(__file__)),
    'kernelSHA256': sha(OUT / 'executed-strict-kernel.py'),
    'scope': 'Distinct V33 swept cranial leaf mesh pairs at native rest. All leaves share cranial-cover owner; same-owner inter-mesh pairs are included. Each mesh is evaluated and transformed to world space before BVH overlap and strict edge-through-face confirmation.',
    'method': 'Reused frozen proper-crossing kernel: 1e-7 plane epsilon and 1e-6 barycentric/edge margin. BVH candidates are reported separately from strict crossings; coplanar/tangent/containment cases are not established. No intra-mesh self-intersection check.',
    'pose': 'native rest (jaw delta 0, cranial-cover lift 0)',
    'cranialLeafMeshCount': len(crown),
    'candidateMeshPairCount': len(crown) * (len(crown) - 1) // 2,
    'bvhCandidateMeshPairCount': bvh_candidate_mesh_pair_count,
    'totalBvhCandidateTrianglePairs': total_bvh_candidate_triangle_pairs,
    'strictCrossingMeshPairCount': len(pairs),
    'pairs': pairs,
    'nativeUnchanged': sha(NATIVE) == BOUND,
}
(OUT / 'same-owner-crown-screen.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'strictCrossingMeshPairCount': len(pairs), 'pairs': pairs}, indent=2), flush=True)
