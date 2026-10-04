import bpy,hashlib,json,importlib.util,sys,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];O=R/'assets/audit/cg-supervised-head03';I=R/'assets/models/cg-supervised01/attempt01/murderbird-supervised-builder.blend'
def mod(p):
 sp=importlib.util.spec_from_file_location('worker_module',str(p));m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(I));s=bpy.context.scene
inputsha=sha(I)
def digest(o):
 h=hashlib.sha256();h.update(str([tuple(v.co) for v in o.data.vertices]).encode());h.update(str([tuple(p.vertices) for p in o.data.polygons]).encode());h.update(str([list(r) for r in o.matrix_world]).encode())
 for u in o.data.uv_layers:h.update(str([tuple(d.uv) for d in u.data]).encode())
 return h.hexdigest()
originals={o.name:digest(o) for o in s.objects if o.type=='MESH'}
anchors={o.name:[list(r) for r in o.matrix_world] for o in s.objects if o.type=='EMPTY'}
cameras=json.loads((R/'assets/audit/cg-supervised01/attempt01/builder/receipt.json').read_text())['cameras']
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
rig=mod(R/'scripts/cinematic-cg-2b-lighting.py').profiles()['neutral']
s.world.node_tree.nodes['Background'].inputs[0].default_value=(*rig['world_color'][:3],1)
s.world.node_tree.nodes['Background'].inputs[1].default_value=rig['world_strength']
lights=sorted([o for o in s.objects if o.type=='LIGHT'],key=lambda o:o.name)
for o,d in zip(lights,rig['areas']):
 o.location=d['position'];o.rotation_euler=(Vector(d['target'])-o.location).to_track_quat('-Z','Y').to_euler();o.data.energy=d['power'];o.data.color=d['color'];o.data.size=d['size']
def render(stage):
 for name in ['canon-neutral','head-neck']:
  c=cameras[name];cam=s.camera;cam.location=c['location'];cam.rotation_euler=c['rotation_euler'];cam.data.type=c['projection'];cam.data.ortho_scale=c['ortho_scale'];cam.data.shift_x,cam.data.shift_y=c['shift'];cam.data.lens=c['lens_mm']
  s.render.resolution_x=1100;s.render.resolution_y=1100 if name=='head-neck' else 900
  if name=='head-neck': cam.data.ortho_scale=1.12
  c['actual_resolution']=[s.render.resolution_x,s.render.resolution_y];c['actual_ortho_scale']=cam.data.ortho_scale
  s.render.filepath=str(O/(stage+'-'+name+'.png'));bpy.ops.render.render(write_still=True)
if not (O/'before-head-neck.png').exists(): render('before')
receipt=mod(R/'scripts/cg-supervised-head03.py').apply(s,R,'builder')
receipt['input_path']=str(I.relative_to(R));receipt['input_sha256']=inputsha
receipt['original_mesh_count']=len(originals);receipt['changed_original_geometry_uv_transform']=[n for n,h in originals.items() if n not in s.objects or digest(s.objects[n])!=h]
receipt['changed_anchors']=[n for n,h in anchors.items() if n not in s.objects or [list(r) for r in s.objects[n].matrix_world]!=h]
render('after')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(O/'source-head03.blend'))
receipt['input_preserved']=inputsha==sha(I);receipt['cameras']=cameras
receipt['references']={str(p.relative_to(R)):sha(p) for p in [R/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg',R/'context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png']}
receipt['images']={p.name:sha(p) for p in O.glob('*.png')}
(O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('HEAD03_COMPLETE',json.dumps({k:receipt[k] for k in ['new_mesh_count','original_mesh_count','changed_original_geometry_uv_transform','changed_anchors','input_preserved']}))
