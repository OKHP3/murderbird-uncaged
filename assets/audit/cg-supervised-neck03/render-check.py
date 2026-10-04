import bpy,hashlib,json,importlib.util
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent;I=R/'assets/models/cg-supervised01/attempt01/murderbird-supervised-builder.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def mod(p):
 sp=importlib.util.spec_from_file_location('worker',str(p));m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
assert sha(I)=='e5fc6a39662bcb7f5ab82679dd719757edc4f0f39fc3cc5ae433bae962409d43'
ref=R/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg'
assert sha(ref)=='645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114'
bpy.ops.wm.open_mainfile(filepath=str(I));s=bpy.context.scene
inputsha=sha(I)
def digest(o):
 h=hashlib.sha256();h.update(str([tuple(v.co) for v in o.data.vertices]).encode());h.update(str([tuple(p.vertices) for p in o.data.polygons]).encode());h.update(str([list(r) for r in o.matrix_world]).encode())
 for u in o.data.uv_layers:h.update(str([tuple(d.uv) for d in u.data]).encode())
 return h.hexdigest()
originals={o.name:digest(o) for o in s.objects if o.type=='MESH'}
anchors={o.name:[list(r) for r in o.matrix_world] for o in s.objects if o.type=='EMPTY'}
protected={o.name:[o.hide_render,o.hide_get(),[m.name for m in o.data.materials]] for o in s.objects if o.type=='MESH' and o.get('cg1cRegion') in ('head','wing','leg','foot')}
cameras=json.loads((R/'assets/audit/cg-supervised01/attempt01/builder/receipt.json').read_text())['cameras']
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
rig=mod(R/'scripts/cinematic-cg-2b-lighting.py').profiles()['neutral']
s.world.node_tree.nodes['Background'].inputs[0].default_value=(*rig['world_color'][:3],1)
s.world.node_tree.nodes['Background'].inputs[1].default_value=rig['world_strength']
lights=sorted([o for o in s.objects if o.type=='LIGHT'],key=lambda o:o.name)
for o,d in zip(lights,rig['areas']):
 o.location=d['position'];o.rotation_euler=(Vector(d['target'])-o.location).to_track_quat('-Z','Y').to_euler();o.data.energy=d['power'];o.data.color=d['color'];o.data.size=d['size']
matched={}
def render(stage):
 cam=s.camera
 for name in ['canon-neutral','neck-body']:
  c=cameras['canon-neutral'];cam.location=c['location'];cam.rotation_euler=c['rotation_euler'];cam.data.type=c['projection'];cam.data.ortho_scale=c['ortho_scale'];cam.data.shift_x,cam.data.shift_y=c['shift'];cam.data.lens=c['lens_mm']
  s.render.resolution_x=1000;s.render.resolution_y=666
  if name=='neck-body':
   cam.location=(-6,-2.14,2.00);cam.rotation_euler=(Vector((0,-.10,1.16))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.30;cam.data.shift_x=cam.data.shift_y=0;s.render.resolution_x=1000;s.render.resolution_y=1000
  matched[name]={'location':list(cam.location),'rotation_euler':list(cam.rotation_euler),'ortho_scale':cam.data.ortho_scale,'shift':[cam.data.shift_x,cam.data.shift_y],'resolution':[s.render.resolution_x,s.render.resolution_y]}
  s.render.filepath=str(O/(stage+'-'+name+'.png'));bpy.ops.render.render(write_still=True)
render('before')
receipt=mod(R/'scripts/cg-supervised-neck03.py').apply(s,R,'builder')
receipt['input_path']=str(I.relative_to(R));receipt['input_sha256']=inputsha
receipt['original_mesh_count']=len(originals);receipt['changed_original_geometry_uv_transform']=[n for n,h in originals.items() if n not in s.objects or digest(s.objects[n])!=h]
receipt['changed_anchors']=[n for n,h in anchors.items() if n not in s.objects or [list(r) for r in s.objects[n].matrix_world]!=h]
receipt['changed_protected_visibility_materials']=[n for n,h in protected.items() if h!=[s.objects[n].hide_render,s.objects[n].hide_get(),[m.name for m in s.objects[n].data.materials]]]
receipt['uv_missing_added']=[o.name for o in s.objects if o.get('cgSupervisedNeck03') and not o.data.uv_layers]
receipt['surface_family_slot_mismatch']=[o.name for o in s.objects if o.get('cgSupervisedNeck03') and len(json.loads(o['cgSurfaceFamilies']))!=len(o.data.materials)]
render('after')
receipt['input_preserved']=inputsha==sha(I);receipt['cameras']=cameras;receipt['matched_render_cameras']=matched;receipt['lighting']=rig
receipt['references']={str(ref.relative_to(R)):sha(ref)}
receipt['images']={p.name:sha(p) for p in O.glob('*.png')}
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(O/'neck03-builder-study.blend'))
receipt['native_sha256']=sha(O/'neck03-builder-study.blend')
(O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('NECK03_COMPLETE',json.dumps({k:receipt[k] for k in ['newMeshCount','original_mesh_count','changed_original_geometry_uv_transform','changed_anchors','changed_protected_visibility_materials','uv_missing_added','surface_family_slot_mismatch','input_preserved']}))
