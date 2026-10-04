import bpy,json,hashlib,importlib.util
from pathlib import Path
from mathutils import Matrix
OUT=Path(__file__).resolve().parent/'attempt02';ROOT=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');BASE=ROOT/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend';NATIVE=OUT/'formed-head13.blend'
r=json.loads((OUT/'receipt.json').read_text());old=json.loads((ROOT/'assets/audit/cg-supervised-head12/attempt02/receipt.json').read_text())['cameras']
sp=importlib.util.spec_from_file_location('pres',ROOT/'scripts/cg-supervised-preservation.py');pres=importlib.util.module_from_spec(sp);sp.loader.exec_module(pres)
def setcam(s,c):
 cam=s.camera;cam.matrix_world=Matrix(c['matrix']);bpy.context.view_layer.update();cam.data.ortho_scale=c['scale'];cam.data.shift_x,cam.data.shift_y=c['shift'];s.render.resolution_x,s.render.resolution_y=c['resolution'];s.render.resolution_percentage=100;bpy.context.view_layer.update()
def actualcam(s):
 return {'matrix':list(map(list,s.camera.matrix_world)),'scale':s.camera.data.ortho_scale,'shift':[s.camera.data.shift_x,s.camera.data.shift_y],'resolution':[s.render.resolution_x,s.render.resolution_y]}
def setup(s):
 s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.image_settings.file_format='PNG';m=bpy.data.materials.new('HEAD13 packet clay');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.42,.42,.42,1);p.inputs['Roughness'].default_value=.75;return m
views=['source-full-bird','head-profile','head-front','head-grazing','head-far-profile']
for before in (True,False):
 bpy.ops.wm.open_mainfile(filepath=str(BASE if before else NATIVE));s=bpy.context.scene;clay=setup(s);snapshot=pres.packed_image_snapshot()
 for view in views:
  c=old['after-clay-'+view];setcam(s,c)
  for mode in ['clay','pbr']:
   name=('before-' if before else 'after-')+mode+'-'+view;s.view_layers[0].material_override=clay if mode=='clay' else None;s.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True);r['cameras'][name]=actualcam(s);print('HEAD13_PACKET',name,flush=True)
 if not before:
  new=[o for o in s.objects if o.get('cgSupervisedHead13')]
  for o in new:
   for m in o.modifiers:
    if m.type=='SUBSURF':m.show_render=False
   w=o.modifiers.new('temporary sparse cage wire','WIREFRAME');w.thickness=.0012;w.use_replace=True
  s.view_layers[0].material_override=clay
  for view in views:
   c=old['after-clay-'+view];setcam(s,c);name='wire-'+view;s.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True);r['cameras'][name]=actualcam(s)
  for o in new:
   o.modifiers.remove(o.modifiers.get('temporary sparse cage wire'))
   for m in o.modifiers:
    if m.type=='SUBSURF':m.show_render=True
  s.view_layers[0].material_override=None;setcam(s,old['after-clay-source-full-bird']);pres.retain_packed_image_ids(s);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(NATIVE),relative_remap=False);bpy.ops.wm.open_mainfile(filepath=str(NATIVE));r['final_packed_readback']=pres.verify_receiving_images(snapshot);r['saved_native_camera']=actualcam(bpy.context.scene)
r['native_sha256']=hashlib.sha256(NATIVE.read_bytes()).hexdigest();r['image_hashes']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('*.png')};r['final_camera']='after-clay-source-full-bird fixed camera04';(OUT/'receipt.json').write_text(json.dumps(r,indent=2));print('HEAD13_PACKET_COMPLETE',flush=True)
