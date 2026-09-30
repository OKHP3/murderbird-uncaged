"""Read-only paired-leaf rest-surface screen; no sweep or clearance certification."""
import bpy, hashlib, json, sys
from pathlib import Path
from mathutils.bvhtree import BVHTree

native, output = map(Path, sys.argv[sys.argv.index('--') + 1:])
assert not output.exists()
bpy.ops.wm.open_mainfile(filepath=str(native))
bpy.context.view_layer.update()
groups = {}
for obj in bpy.data.objects:
    if obj.type != 'MESH' or not obj.name.startswith('V38 swept crown course '):
        continue
    stem, leaf = obj.name.rsplit(' leaf ', 1)
    groups.setdefault(stem, {})[leaf] = obj
assert len(groups) == 29 and all(set(pair) == {'1', '2'} for pair in groups.values())
def tree(obj):
    obj.data.calc_loop_triangles()
    points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
    triangles = [tuple(triangle.vertices) for triangle in obj.data.loop_triangles]
    return BVHTree.FromPolygons(points, triangles, all_triangles=True, epsilon=1e-7)
rows = []
for stem, pair in sorted(groups.items()):
    a, b = pair['1'], pair['2']
    assert a.parent == b.parent and a.parent.name == 'cranial-cover'
    hits = tree(a).overlap(tree(b))
    rows.append({'sourceCourse': stem, 'a': a.name, 'b': b.name,
                 'triangleSurfaceCandidates': len(hits)})
report = {'status': 'diagnostic; inspect lap fit before surface acceptance',
          'nativeSha256': hashlib.sha256(native.read_bytes()).hexdigest(),
          'scriptSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'pairedLeavesTested': len(rows),
          'pairsWithSurfaceCandidates': sum(row['triangleSurfaceCandidates'] > 0 for row in rows),
          'pairs': rows,
          'limits': ['Actual triangulated paired-leaf surfaces at native rest, BVH epsilon 0.1 micrometre.',
                     'Counts are surface candidates, not penetration depths or a full solid fit certificate.',
                     'No adjacent-course, fixed-seat, containment, self-intersection or continuous-motion screen.',
                     'Shared rigid ownership preserves paired-leaf relative transforms during exhibit motion.']}
output.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({key: report[key] for key in ('pairedLeavesTested', 'pairsWithSurfaceCandidates')}))
