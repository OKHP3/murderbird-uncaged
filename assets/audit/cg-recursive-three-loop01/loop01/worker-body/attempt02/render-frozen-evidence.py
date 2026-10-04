import bpy,json,sys,hashlib
from pathlib import Path
root=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
own=Path('/Users/okh/.codex/worktrees/cg-supervised-oblique-breast15/murderbird-uncaged');out=own/'assets/audit/cg-recursive-body01/attempt02/builder';native=own/'assets/models/cg-recursive-body01/attempt02/murderbird-recursive-body-builder.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();nativehash=sha(native);r=json.loads((out/'receipt.json').read_text());prior=json.loads((root/'assets/audit/cg-supervised01/attempt09/builder/receipt.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene
clay=bpy.data.materials.new('frozen evidence clay');clay.use_nodes=True;clay.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.23,.23,.23,1);clay.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.64
for stage in ('before','candidate'):
 for o in s.objects:
  if o.get('cgRecursiveBody01'):o.hide_render=stage=='before'
  if o.name in r['application']['hideOverrides']:o.hide_render=stage=='candidate'
 for key in ('body-detail','side-profile','neutral-180','neutral-000'):
  for cp in (False,True):
   q=prior['cameras'][key];c=s.camera;c.location=q['location'];c.rotation_euler=q['rotation_euler'];c.data.type=q['projection'];c.data.ortho_scale=q['ortho_scale'];c.data.lens=q['lens_mm'];c.data.shift_x,c.data.shift_y=q['shift'];b=s.world.node_tree.nodes.get('Background');b.inputs[0].default_value=q['world_color'];b.inputs[1].default_value=q['world_strength'];lights=[o for o in s.objects if o.type=='LIGHT' and o.name.startswith('Supervised area')][-3:]
   for o,l in zip(lights,q['areas']):o.location=l['location'];o.rotation_euler=l['rotation_euler'];o.data.energy=l['power'];o.data.color=l['color'];o.data.size=l['size']
   s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=900;s.render.resolution_y=round(900*q['resolution'][1]/q['resolution'][0]);s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_layers[0].material_override=clay if cp else None;name=stage+'-'+key+('-clay' if cp else '-pbr');s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);r['cameras'][name]=q;r['images'][name+'.png']=sha(out/(name+'.png'));print('FROZEN_BODY_IMAGE',name,flush=True)
assert sha(native)==nativehash;r['expandedFrozenNativeSHA256']=nativehash;r['expandedRenderSettings']=dict(samples=12,resolutionWidth=900,CPUThreads=2,noNativeSave=True);(out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
