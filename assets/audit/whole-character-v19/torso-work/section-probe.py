import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[4]
native=root/'assets/models/whole-character-v19/attempt-torso02/murderbird-whole-character-v19.blend'
bpy.ops.wm.open_mainfile(filepath=str(native));dg=bpy.context.evaluated_depsgraph_get()
names=['Breast inner access shell','Throat formed lamina 3','Throat formed lamina 4','Throat formed lamina 5','Throat formed lamina 6','Lower cervical open backing']
trees={};bounds={}
for n in names:
 o=bpy.data.objects[n];e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();p=[e.matrix_world@v.co for v in m.vertices];f=[tuple(t.vertices) for t in m.loop_triangles];trees[n]=BVHTree.FromPolygons(p,f,all_triangles=True,epsilon=0);bounds[n]={'min':[min(v[i] for v in p) for i in range(3)],'max':[max(v[i] for v in p) for i in range(3)]};e.to_mesh_clear()
rows=[]
for z in (1.18,1.23,1.26,1.29,1.32,1.35):
 r={'worldZ':z,'centerPlaneX':0,'frontY':{}}
 for n,t in trees.items():
  hit,normal,index,distance=t.ray_cast(Vector((0,-2,z)),Vector((0,1,0)),4)
  r['frontY'][n]=None if hit is None else hit.y
 rows.append(r)
out={'method':'evaluated triangle ray from native (X0,Y−2,Zsection) toward +Y; null means no center-plane surface hit at that height','sections':rows,'evaluatedBounds':bounds,'native':'assets/models/whole-character-v19/attempt-torso02/murderbird-whole-character-v19.blend'}
(root/'assets/audit/whole-character-v19/attempt-torso02/readonly-center-sections.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
