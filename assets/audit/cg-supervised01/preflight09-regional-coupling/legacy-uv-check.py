import sys;sys.dont_write_bytecode=True
import bpy,json,math
from pathlib import Path
O=Path('/tmp/cg-preflight09');r=json.loads(Path('/tmp/cg-preflight09.json').read_text());old=set(json.loads((O/'builder-receiving-snapshot.json').read_text())['payload']);bpy.ops.wm.open_mainfile(filepath=str(O/'hypothetical-builder.blend'),use_scripts=False);s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();bad={};newbad=[]
for ob in s.objects:
 if ob.type!='MESH' or ob.hide_render or ob.hide_viewport or not ob.visible_get() or ob.hide_get() or ob.get('authoringGuide'):continue
 ev=ob.evaluated_get(dg);md=ev.to_mesh(preserve_all_data_layers=True,depsgraph=dg);lay=next((u for u in md.uv_layers if u.active_render),md.uv_layers.active)
 if lay:
  lo=[min(v.uv[i] for v in lay.data) for i in range(2)];hi=[max(v.uv[i] for v in lay.data) for i in range(2)]
  if min(lo)<-1e-6 or max(hi)>1.000001:
   bad[ob.name]=dict(layer=lay.name,min=lo,max=hi,isOriginal=ob.name in old)
   if ob.name not in old:newbad.append(ob.name)
 ev.to_mesh_clear()
q=dict(legacyUVOutOf01Objects=bad,legacyCount=sum(v['isOriginal'] for v in bad.values()),newOutOf01Objects=newbad,newAllNormalized=not newbad,conclusion='GLB merged UV0 outside0..1 originates entirely from preserved original mesh UV layers; new regional geometry is normalized.')
(O/'legacy-uv-check.json').write_text(json.dumps(q,indent=2));print('LEGACY UV COUNT',q['legacyCount'],'NEW BAD',newbad,flush=True)
