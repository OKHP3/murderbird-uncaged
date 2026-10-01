import bpy,json
from pathlib import Path
bpy.ops.wm.open_mainfile(filepath='assets/models/whole-character-v38/bill-relationship02/murderbird-v38-bill-relationship02.blend');bpy.context.view_layer.update();rows=[]
for side in(-1,1):
 o=bpy.data.objects[f'V31 passive cranial load bow {side}'];v=[o.matrix_world@p.co for p in o.data.vertices];assert len(v)==1122,(o.name,len(v));m=o.data;m.calc_loop_triangles()
 rows.append({'name':o.name,'vertexCount':len(v),'rows':[{'row':i,'centerNative':list(v[i*11+5]),'footCornerNative':[list(v[i*11+j])for j in(2,8)]}for i in range(12,32)]})
print(rows,flush=True);Path('assets/audit/whole-character-v38/throat-seated01/bow-survey.json').write_text(json.dumps(rows,indent=2)+'\n')
