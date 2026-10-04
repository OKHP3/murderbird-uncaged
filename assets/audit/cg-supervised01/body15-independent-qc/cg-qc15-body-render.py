import bpy,json
from pathlib import Path
ROOT=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');WT=Path('/Users/okh/.codex/worktrees/cg-supervised-oblique-breast15/murderbird-uncaged');r=json.loads((WT/'assets/audit/cg-supervised-body15/attempt01/receipt.json').read_text())
for version,path in [('13',ROOT/'assets/audit/cg-supervised-body13/attempt01/murderbird-body13.blend'),('15',WT/'assets/audit/cg-supervised-body15/attempt01/murderbird-body15.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;q=r['cameras']['final15-side-clay'];cam=s.camera;cam.location=q['location'];cam.rotation_euler=q['rotation_euler'];cam.data.type='ORTHO';cam.data.ortho_scale=q['scale'];cam.data.shift_x,cam.data.shift_y=q.get('shift',[0,0])
 for l in q['lights']:
  o=s.objects[l['name']];o.location=l['location'];o.rotation_euler=l['rotation'];o.data.energy=l['power'];o.data.color=l['color'];o.data.size=l['size']
 c=bpy.data.materials.get('Body11 diagnostic clay')
 if not c:
  c=bpy.data.materials.new('Body11 diagnostic clay');c.use_nodes=True;c.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.23,.23,.23,1);c.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.64
 s.view_layers[0].material_override=c;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_percentage=100;s.render.resolution_x=1024;s.render.resolution_y=round(1024*q['resolution'][1]/q['resolution'][0]);s.render.image_settings.file_format='PNG';s.render.filepath='/tmp/cg-qc15-body-fresh'+version+'-side-clay.png';bpy.ops.render.render(write_still=True);print('FRESH_RENDER',version,flush=True)
