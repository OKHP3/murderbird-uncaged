import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[4];out=[]
for label,path,names in [('v18','assets/models/whole-character-v18/attempt-01/murderbird-whole-character-v18.blend',['Breast inner access shell']),('torso05','assets/models/whole-character-v19/attempt-torso05/murderbird-whole-character-v19.blend',['Breast inner access shell','V19 fixed aperture liner'])]:
 bpy.ops.wm.open_mainfile(filepath=str(root/path));dg=bpy.context.evaluated_depsgraph_get();trees=[]
 for n in names:
  o=bpy.data.objects[n];e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();trees.append(BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[tuple(t.vertices) for t in m.loop_triangles],all_triangles=True));e.to_mesh_clear()
 for z in (1.05,1.20):
  row={'model':label,'z':z,'points':[]}
  for x in (0,.10,.18,.22,.24,.26,.28,.30,.32,.34,.36):
   hits=[t.ray_cast(Vector((x,-2,z)),Vector((0,1,0)),4)[0] for t in trees];hits=[p for p in hits if p is not None];row['points'].append([x,None if not hits else min(p.y for p in hits)])
  out.append(row)
(root/'assets/audit/whole-character-v19/torso-work/lateral-profile05.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
