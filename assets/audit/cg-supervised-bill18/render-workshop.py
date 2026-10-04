"""Paired read-only workshop countertest; no native or material edits."""
import bpy,json,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parent;R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');H=Path('/Users/okh/.codex/worktrees/cg-supervised-layered-crown17/murderbird-uncaged/assets/audit/cg-supervised-head17/attempt02');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sp=importlib.util.spec_from_file_location('l18',R/'scripts/cg-supervised-lighting02.py');l=importlib.util.module_from_spec(sp);sp.loader.exec_module(l);profile=l.profiles()['workshop'];refs=json.loads((H/'receipt.json').read_text())['cameras'];report={'scope':'Additional matched workshop light countertest; camera35 retained; no native save; not a lighting fix','profile':profile,'cameras':{},'inputs':{},'images':{}}
for label,native in [('before17',H/'layered-head17.blend'),('attempt02',O/'attempt02/formed-bill18.blend')]:
 pin=sha(native);report['inputs'][label]={'path':str(native),'sha256':pin};bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=4;s.cycles.use_denoising=True;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_layers[0].material_override=None
 lights=[o for o in s.objects if o.type=='LIGHT'];assert len(lights)==3
 back=s.world.node_tree.nodes.get('Background');back.inputs[0].default_value=(*profile['world_color'][:3],1);back.inputs[1].default_value=profile['world_strength']
 for o,lr in zip(lights,profile['areas']):
  o.location=lr['position'];o.rotation_euler=(Vector(lr['target'])-o.location).to_track_quat('-Z','Y').to_euler();o.data.energy=lr['power'];o.data.color=lr['color'];o.data.size=lr['size']
 for v in ['source-full-bird','head-profile']:
  rc=refs['after-pbr-'+v];s.camera.matrix_world=Matrix(rc['matrix']);s.camera.data.ortho_scale=rc['scale'];s.camera.data.shift_x,s.camera.data.shift_y=rc['shift'];s.render.resolution_x,s.render.resolution_y=rc['resolution'];p=O/label/('workshop-'+v+'.png');s.render.filepath=str(p);bpy.context.view_layer.update();bpy.ops.render.render(write_still=True);report['cameras'][v]=rc;report['images'][label+'/'+p.name]=sha(p);print('BILL18_WORKSHOP',label,v,flush=True)
 assert sha(native)==pin
(O/'workshop-receipt.json').write_text(json.dumps(report,indent=2)+'\n')
