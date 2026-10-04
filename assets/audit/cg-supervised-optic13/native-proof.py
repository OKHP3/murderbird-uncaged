import bpy,hashlib,json,importlib.util,math
from pathlib import Path
W=Path('/Users/okh/.codex/worktrees/cg-supervised-optic-area13/murderbird-uncaged');R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');O=W/'assets/audit/cg-supervised-optic13/attempt01';N=O/'murderbird-optic13.blend';frozen=json.loads((O/'receipt.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(N),use_scripts=False);s=bpy.context.scene
spec=importlib.util.spec_from_file_location('preservation',R/'scripts/cg-supervised-preservation.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p);p.verify_receiving_images(frozen['receivingPackedImageSnapshot'])
new=[i for i in bpy.data.images if i.name.startswith('CGO13')];assert len(new)==1;i=new[0];assert i.source=='FILE' and i.colorspace_settings.name=='sRGB' and i.packed_file
payload={'nativeSHA256':hashlib.sha256(N.read_bytes()).hexdigest(),'historicalImageReadback':p.verify_receiving_images(frozen['receivingPackedImageSnapshot']),'newPackedFileImage':{'name':i.name,'source':i.source,'colorSpace':i.colorspace_settings.name,'size':list(i.size),'packedSHA256':hashlib.sha256(bytes(i.packed_file.data)).hexdigest()},'objects':[],'emissionStrengths':{m.name:m.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value for m in bpy.data.materials if m.get('cgOptic13Role')}}
for o in s.objects:
 if o.get('cgSupervisedOptic13'):
  payload['objects'].append({'name':o.name,'radialConstructionUnits':sorted({round(math.hypot(v.co.y-.005,v.co.z-.020)/.0012,4) for v in o.data.vertices}),'axialDepthsMeters':sorted({round(abs(v.co.x),7) for v in o.data.vertices}),'UVFiniteNormalized':all(math.isfinite(c) and 0<=c<=1 for u in o.data.uv_layers for v in u.data for c in v.uv)})
assert all(q['UVFiniteNormalized'] for q in payload['objects']);(W/'assets/audit/cg-supervised-optic13/native-proof.json').write_text(json.dumps(payload,indent=2)+'\n')
