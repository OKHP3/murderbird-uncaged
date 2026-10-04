"""Finite evaluated attributes and unchanged root-exporter smoke on visible candidate."""
import bpy,importlib.util,json,hashlib,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[3]
O=R/'assets/audit/cg-supervised-head05/attempt02'
bpy.ops.wm.open_mainfile(filepath=str(O/'connected-head05.blend'))
s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();bad=[];checked=[]
for o in s.objects:
 if o.type!='MESH' or o.hide_render:continue
 ev=o.evaluated_get(dg);me=ev.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
 try:
  co=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',co)
  no=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('normal',no)
  if not np.isfinite(co).all() or not np.isfinite(no).all():bad.append({'mesh':o.name,'attribute':'position/normal'})
  for uv in me.uv_layers:
   a=np.empty(len(uv.data)*2,dtype=np.float32);uv.data.foreach_get('uv',a)
   if not np.isfinite(a).all():bad.append({'mesh':o.name,'attribute':'UV '+uv.name})
  checked.append(o.name)
 finally:ev.to_mesh_clear()
receipt={'finite_visible_evaluated_attributes':not bad,'bad':bad,'visible_mesh_count':len(checked),'native_sha256':hashlib.sha256((O/'connected-head05.blend').read_bytes()).hexdigest(),'browser_visual_check':'NOT RUN; integrator scope','exporter':'scripts/cg-supervised-export.py unchanged'}
(O/'export-smoke-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
assert not bad,bad
sp=importlib.util.spec_from_file_location('exporter',R/'scripts/cg-supervised-export.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
result=m.export(s,O/'head05-static-smoke.glb')
receipt['static_export']='PASS';receipt['export']=result;receipt['glb_sha256']=hashlib.sha256((O/'head05-static-smoke.glb').read_bytes()).hexdigest()
(O/'export-smoke-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('HEAD05_EXPORT_PASS',flush=True)
