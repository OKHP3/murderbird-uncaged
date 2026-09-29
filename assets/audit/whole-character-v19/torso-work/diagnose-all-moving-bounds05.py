import bpy,json
from pathlib import Path
root=Path(__file__).resolve().parents[4];bpy.ops.wm.open_mainfile(filepath=str(root/'assets/models/whole-character-v19/attempt-torso05/murderbird-whole-character-v19.blend'))
h=bpy.data.objects['breastplate'];axis=h.matrix_world.translation;dg=bpy.context.evaluated_depsgraph_get();rows=[]
for o in bpy.data.objects:
 if o.type!='MESH' or o.parent!=h:continue
 e=o.evaluated_get(dg);m=e.to_mesh();p=[e.matrix_world@v.co for v in m.vertices];mi=[min(v[k] for v in p) for k in range(3)];ma=[max(v[k] for v in p) for k in range(3)];e.to_mesh_clear()
 exception=o.name.startswith('V19 moving bottom')
 rows.append({'name':o.name,'min':mi,'max':ma,'behindAxisY':ma[1]-axis.y,'belowAxisZ':axis.z-mi[2],'newMatingSupportException':exception})
viol=[r for r in rows if not r['newMatingSupportException'] and (r['behindAxisY']>1e-6 or r['belowAxisZ']>1e-6)]
out={'axisWorldNative':list(axis),'status':'PASS' if not viol else 'FAIL','method':'all evaluated moving-owned pieces, excluding explicit new axle/root-return mating supports from fore/above criterion','violations':viol,'allMovingObjects':rows};(root/'assets/audit/whole-character-v19/attempt-torso05/all-moving-axis-bounds.json').write_text(json.dumps(out,indent=2));print(json.dumps({'axis':list(axis),'status':out['status'],'violations':viol},indent=2))
