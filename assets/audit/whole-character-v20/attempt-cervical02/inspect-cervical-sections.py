import bpy,json
from pathlib import Path
BASE=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
bpy.ops.wm.open_mainfile(filepath=str(BASE/'assets/models/whole-character-v20/attempt-cervical02/murderbird-whole-character-v20.blend'))
dg=bpy.context.evaluated_depsgraph_get();groups={}
for name in ('Breast inner access shell','Throat formed lamina 1','Throat formed lamina 2','Throat formed lamina 3','Throat formed lamina 4','Throat formed lamina 5','Throat formed lamina 6','Lower cervical open backing'):
 o=bpy.data.objects[name];e=o.evaluated_get(dg);m=e.to_mesh();pts=[o.matrix_world@v.co for v in m.vertices];m.calc_loop_triangles();sections={}
 for z in (1.28,1.32,1.36,1.40,1.44,1.48,1.52,1.56,1.60,1.64):
  hits=[]
  for t in m.loop_triangles:
   vv=[pts[i] for i in t.vertices]
   for a,b in zip(vv,vv[1:]+vv[:1]):
    if (a.z-z)*(b.z-z)<0:
     p=a+(b-a)*((z-a.z)/(b.z-a.z))
     if abs(p.x)<.10:hits.append(p)
  if hits:sections[str(z)]={'frontY':min(p.y for p in hits),'rearY':max(p.y for p in hits),'centerBandX':.10}
 groups[name]={'owner':o.parent.name,'bounds':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)],'sections':sections};e.to_mesh_clear()
out=BASE/'assets/audit/whole-character-v20/attempt-cervical02/cervical-sections.json';out.write_text(json.dumps(groups,indent=2));print(json.dumps(groups,indent=2))
