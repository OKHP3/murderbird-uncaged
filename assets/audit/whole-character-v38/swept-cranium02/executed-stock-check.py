import bpy,json,sys
from pathlib import Path
from mathutils import Vector
model,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(model));rows=[]
for o in bpy.data.objects:
 if not o.name.startswith('V38 swept crown course'):continue
 m=o.data;m.calc_loop_triangles();n=len(m.vertices)//2;p=[o.matrix_world@v.co for v in m.vertices];values=[]
 for tri in m.loop_triangles:
  if all(i<n for i in tri.vertices):
   a,b,c=[p[i]for i in tri.vertices];normal=(b-a).cross(c-a).normalized();values.append(abs(normal.dot(Vector((0,0,.003)))))
 rows.append({'name':o.name,'axialNativeZStockM':.003,'actualOuterTriangleNormalProjectedStockRangeM':[min(values),max(values)]})
out.write_text(json.dumps({'meshes':rows,'limits':'Axial graph stock is3mm; projected stock against each saved outer triangle varies with slope and is not minimum continuous solid thickness/load certification. Thin nape stock requires further judgment. No model write.'},indent=2)+'\n')
