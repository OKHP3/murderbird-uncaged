import bpy,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='assets/models/whole-character-v38/bill-relationship02/murderbird-v38-bill-relationship02.blend');bpy.context.view_layer.update();out=[]
for side in(-1,1):
 o=bpy.data.objects[f'V31 passive cranial load bow {side}'];m=o.data;m.calc_loop_triangles();vs=[o.matrix_world@v.co for v in m.vertices];rows=[]
 for t in m.loop_triangles:
  p=[vs[i]for i in t.vertices];c=sum(p,p[0]*0)/3
  if 1.53<c.z<1.66 and c.y<-.34:rows.append({'triangle':t.index,'vertices':[list(q)for q in p],'center':list(c),'normal':list((p[1]-p[0]).cross(p[2]-p[0]).normalized())})
 out.append({'name':o.name,'owner':o.parent.name,'patches':rows});print(o.name,len(rows),rows[::max(1,len(rows)//8)],flush=True)
Path('assets/audit/whole-character-v38/throat-construction01/frame-survey.json').write_text(json.dumps(out,indent=2)+'\n')
