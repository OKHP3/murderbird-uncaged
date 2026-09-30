import bpy,json
from mathutils.bvhtree import BVHTree
from pathlib import Path
p=Path('/Users/okh/.codex/worktrees/v38-crown-lap-fit/murderbird-uncaged')
bpy.ops.wm.open_mainfile(filepath=str(p/'assets/models/whole-character-v38/crown-fit01/murderbird-v38-crown-fit01.blend'));bpy.context.view_layer.update()
rows=[]
for col in range(1,6):
 a=bpy.data.objects[f'V38 swept crown course 3 column {col} leaf 1'];b=bpy.data.objects[f'V38 swept crown course 3 column {col} leaf 2'];a.data.calc_loop_triangles();v=[a.matrix_world@x.co for x in a.data.vertices];t=[tuple(x.vertices) for x in a.data.loop_triangles];tree=BVHTree.FromPolygons(v,t,all_triangles=True,epsilon=1e-7)
 samples=[]
 for k in range(65):
  outer=b.matrix_world@b.data.vertices[k].co;inner=b.matrix_world@b.data.vertices[k+169].co;direction=(outer-inner).normalized();origin=outer+direction*.02;dist=0;hits=[]
  for attempt in range(8):
   loc,norm,index,d=tree.ray_cast(origin,-direction,.04-dist)
   if loc is None:break
   dist+=d;hits.append({'relative':(outer-loc).dot(direction),'triangle':index,'vertices':t[index]});origin=loc-direction*1e-6;dist+=1e-6
  samples.append({'vertex':k,'row':k//13,'column':k%13,'hits':hits,'requiredInwardM':max([0]+[x['relative']+.0004 for x in hits])})
 rows.append({'object':b.name,'samples':samples})
f=Path('/tmp/murderbird-crown-fit02-seating.json');f.write_text(json.dumps(rows,indent=2))
for r in rows:
 print(r['object'],[(row,round(max(x['requiredInwardM'] for x in r['samples'] if x['row']==row),6),sum(bool(x['hits']) for x in r['samples'] if x['row']==row)) for row in range(5)])
