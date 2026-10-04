"""Align source-only clay samples with each existing after render; no saves."""
import hashlib,json,sys
from pathlib import Path
import bpy
root=Path(__file__).resolve().parents[3];inp=Path(sys.argv[sys.argv.index('--input-root')+1]);source=inp/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();pin=sha(source)
for folder,samples,resolution in [('pilot01',3,640),('pilot02',6,800),('replicated02',6,800)]:
 out=root/'assets/audit/cg-supervised-feet14'/folder;receipt=json.loads((out/'receipt.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;cam=s.camera;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=samples;s.cycles.use_denoising=True;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.resolution_x=s.render.resolution_y=resolution
 clay=bpy.data.materials.new('Feet14 matched clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.32,.32,.32,1);bs.inputs['Roughness'].default_value=.63;s.view_layers[0].material_override=clay
 for name in ('before-feet-clay','before-front-clay','before-side-clay'):
  q=receipt['cameras'][name];cam.location=q['location'];cam.rotation_euler=q['rotation'];cam.data.type='ORTHO';cam.data.ortho_scale=q['scale'];cam.data.shift_x,cam.data.shift_y=q['shift'];s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 receipt['renderSettings']={'engine':'CYCLES','samples':samples,'device':'CPU','denoising':True,'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma};receipt['sourceClaySampleAlignment']='Before-clay views re-rendered from exact immutable receiving06 with same samples as after; original helper reopened source40-sample settings. Cameras/material override/lighting unchanged; no design change.';receipt['images']={p.name:sha(p) for p in out.glob('*.png')};(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
assert sha(source)==pin;print('FEET14_MATCHED_CLAY_COMPLETE',flush=True)
