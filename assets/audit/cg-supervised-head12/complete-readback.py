import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
OUT=Path(__file__).resolve().parent
BASE=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged/assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def setup(s,c):
 s.camera.matrix_world=Matrix(c['matrix']);s.camera.data.ortho_scale=c['scale'];s.camera.data.shift_x,s.camera.data.shift_y=c['shift'];s.render.resolution_x,s.render.resolution_y=c['resolution'];s.render.resolution_percentage=100;s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;bpy.context.view_layer.update()
def clay():
 m=bpy.data.materials.new('HEAD12 readback diagnostic clay');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.42,.42,.42,1);p.inputs['Roughness'].default_value=.75;return m
for attempt in ('attempt01','attempt02'):
 out=OUT/attempt;r=json.loads((out/'receipt.json').read_text());canon=r['cameras']['after-clay-source-full-bird'].copy();r['camera_correction']='PBR matrix receipt/readback corrected to the actual fixed camera04 ortho35/elevation16 used by clay whole, before freeze; initial stale matrix capture was caught.'
 for before in (True,False):
  bpy.ops.wm.open_mainfile(filepath=str(BASE if before else out/'formed-head12.blend'));s=bpy.context.scene;setup(s,canon);s.view_layers[0].material_override=None
  name=('before-' if before else 'after-')+'pbr-source-full-bird';s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);r['cameras'][name]=canon.copy()
  target=s.objects['CG2b head frame'].matrix_world@Vector((0,.005,-.025));cam=s.camera;cam.location=target+Vector((6,0,0));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.84;cam.data.shift_x=cam.data.shift_y=0;s.render.resolution_x=s.render.resolution_y=800;bpy.context.view_layer.update();s.view_layers[0].material_override=clay();name=('before-' if before else 'after-')+'clay-head-far-profile';s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);r['cameras'][name]={'matrix':list(map(list,cam.matrix_world)),'scale':cam.data.ortho_scale,'shift':[0,0],'resolution':[800,800]}
  if not before:
   new=[o for o in s.objects if o.get('cgSupervisedHead12')]
   setup(s,canon)
   for o in new:
    w=o.modifiers.new('transient diagnostic wire','WIREFRAME');w.thickness=.0012;w.use_replace=True
   s.render.filepath=str(out/'wire-source-full-bird.png');bpy.ops.render.render(write_still=True)
   for o in new:o.modifiers.remove(o.modifiers.get('transient diagnostic wire'))
   s.view_layers[0].material_override=None;setup(s,canon);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'formed-head12.blend'),relative_remap=False)
   r['native_sha256']=sha(out/'formed-head12.blend')
 r['image_hashes']={p.name:sha(p) for p in out.glob('*.png')};r['readback_camera_render_complete']=True;(out/'receipt.json').write_text(json.dumps(r,indent=2));print('HEAD12_CAMERA_READBACK_COMPLETE',attempt,flush=True)
