import bpy,json,hashlib
from pathlib import Path
own=Path(__file__).resolve().parents[3]
for a in ['attempt01','attempt02']:
 p=own/'assets/audit/cg-recursive-body02'/a/'builder/receipt.json';r=json.loads(p.read_text());native=own/'assets/models/cg-recursive-body02'/a/'murderbird-body02-builder.blend';h=hashlib.sha256(native.read_bytes()).hexdigest();assert h==r['nativeSHA256'];bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;changed=[]
 for n,q in r['originalRig'].items():
  o=s.objects[n]
  if list(o.location)!=q['location'] or list(o.rotation_euler)!=q['rotation'] or list(o.scale)!=q['scale']:changed.append(n+' transform')
  for k,v in q['data'].items():
   actual=getattr(o.data,k);actual=list(actual) if k=='color' else actual
   if actual!=v:changed.append(n+' '+k)
 b=s.world.node_tree.nodes.get('Background');assert list(b.inputs[0].default_value)==r['originalWorld'][0] and b.inputs[1].default_value==r['originalWorld'][1];assert not changed,changed;r['explicitRigReadback']=dict(cameraLightsChecked=len(r['originalRig']),changed=changed,worldExact=True,nativeBytesUnchanged=True);assert hashlib.sha256(native.read_bytes()).hexdigest()==h;p.write_text(json.dumps(r,indent=2)+'\n');print('RIG_READBACK_PASS',a,len(r['originalRig']),flush=True)
