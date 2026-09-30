import bpy,json
from mathutils.bvhtree import BVHTree
from pathlib import Path
p=Path('/Users/okh/.codex/worktrees/v38-crown-lap-fit/murderbird-uncaged')
bpy.ops.wm.open_mainfile(filepath=str(p/'assets/models/whole-character-v38/crown-fit01/murderbird-v38-crown-fit01.blend'));bpy.context.view_layer.update()
rows=[]
for col in range(1,6):
 a=bpy.data.objects[f'V38 swept crown course 3 column {col} leaf 1'];b=bpy.data.objects[f'V38 swept crown course 3 column {col} leaf 2'];a.data.calc_loop_triangles();v=[a.matrix_world@x.co for x in a.data.vertices];t=[tuple(x.vertices) for x in a.data.loop_triangles];innertris=[face for face in t if all(i>=169 for i in face)];tree=BVHTree.FromPolygons(v,innertris,all_triangles=True,epsilon=1e-7)
 samples=[]
 for k in range(65):
  outer=b.matrix_world@b.data.vertices[k].co;loc,normal,index,d=tree.find_nearest(outer)
  signed=(outer-loc).dot(normal);required=max(0,.0004-signed)
  samples.append({'vertex':k,'row':k//13,'column':k%13,'signedInnerFaceDistanceM':signed,'innerNormal':list(normal),'nearestPoint':list(loc),'requiredNormalMoveM':required})
 rows.append({'object':b.name,'samples':samples})
f=Path('/tmp/murderbird-crown-fit02-normal-seating.json');f.write_text(json.dumps(rows,indent=2))
for r in rows:print(r['object'],[(row,round(max(x['requiredNormalMoveM'] for x in r['samples'] if x['row']==row),6)) for row in range(5)])
