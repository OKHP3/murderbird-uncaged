import bpy,json,sys
from pathlib import Path
model,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(model));o=bpy.data.objects['V32 formed mandibular bowl'];p=[o.matrix_world@v.co for v in o.data.vertices];rows=[]
for y in [-.63,-.60,-.58,-.56,-.54,-.52,-.50,-.48,-.46]:
 q=[v for v in p if abs(v.y-y)<.011 and abs(v.x)>.125];rows.append({'y':y,'count':len(q),'boundsXZ':[[min(v[k]for v in q),max(v[k]for v in q)]for k in(0,2)]if q else None})
out.write_text(json.dumps(rows,indent=2)+'\n')
