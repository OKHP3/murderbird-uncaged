import bpy,hashlib,json,importlib.util,sys,math,time
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];O=R/'assets/audit/cg-supervised-head04/attempt02';O.mkdir(exist_ok=True)
S=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
I=S/'assets/models/cg-supervised01/attempt03/murderbird-supervised-builder.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(I)=='01103e35bcf16f03fc4a7b7d157bbe89d7267b8d0ca5ca8cd3f6167a6fcb8fce'
bpy.ops.wm.open_mainfile(filepath=str(I));s=bpy.context.scene
sp=importlib.util.spec_from_file_location('head04',R/'scripts/cg-supervised-head04.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
def digest(o):
 h=hashlib.sha256();h.update(str([tuple(v.co) for v in o.data.vertices]).encode());h.update(str([(tuple(p.vertices),p.material_index) for p in o.data.polygons]).encode());h.update(str([list(r) for r in o.matrix_world]).encode())
 for u in o.data.uv_layers:h.update(str([tuple(d.uv) for d in u.data]).encode())
 return h.hexdigest()
originals={o.name:digest(o) for o in s.objects if o.type=='MESH'};anchors={o.name:[list(r) for r in o.matrix_world] for o in s.objects if o.type=='EMPTY'}
oldvis={o.name:o.hide_render for o in s.objects if o.type=='MESH'}
s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
s.world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.24,.27,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.5
for o in s.objects:
 if o.type=='LIGHT':o.hide_render=True
for j,(pos,power,size) in enumerate([((-3,-4,5),650,3),((3,1,3),500,2),((-1,3,4),750,2)]):
 d=bpy.data.lights.new('Head04 studio '+str(j),'AREA');o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,1.5))-o.location).to_track_quat('-Z','Y').to_euler();d.energy=power;d.size=size
clay=bpy.data.materials.new('Head04 diagnostic clay');clay.diffuse_color=(.45,.45,.45,1);clay.use_nodes=True;clay.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.45,.45,.45,1);clay.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.72
receipt=m.apply(s,R,'builder');receipt['input_sha256']=sha(I);receipt['original_mesh_count']=len(originals);receipt['changed_original_meshes']=[n for n,h in originals.items() if digest(s.objects[n])!=h];receipt['changed_anchors']=[n for n,h in anchors.items() if [list(r) for r in s.objects[n].matrix_world]!=h]
frame=s.objects['CG2b head frame'].matrix_world;center=frame@Vector((0,.045,-.065));cameras={}
canon=json.loads((R/'assets/audit/cg-supervised01/attempt03/builder/receipt.json').read_text())['cameras']['canon-neutral']
def render(name,angle,style='pbr',stage='after',full=False,size=640):
 for o in s.objects:
  if o.type=='MESH':
   if o.get('cgSupervisedHead04'):o.hide_render=stage=='before'
   elif o.name in oldvis:o.hide_render=oldvis[o.name] if stage=='before' else (True if o.name in receipt['hidden_originals'] else oldvis[o.name])
 s.view_layers[0].material_override=clay if style=='clay' else None
 cam=s.camera;cam.data.type='ORTHO';cam.data.shift_x=cam.data.shift_y=0
 if full:
  cam.location=canon['location'];cam.rotation_euler=canon['rotation_euler'];cam.data.ortho_scale=canon['ortho_scale'];cam.data.shift_x,cam.data.shift_y=canon['shift'];w,h=size,round(size*853/1280)
 else:
  cam.location=center+Vector((-5*math.sin(math.radians(angle)),-5*math.cos(math.radians(angle)),.18));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.80;w=h=size
 s.render.resolution_x=w;s.render.resolution_y=h;s.render.filepath=str(O/(stage+'-'+style+'-'+name+'.png'));bpy.ops.render.render(write_still=True)
 cameras[stage+'-'+style+'-'+name]={'location':list(cam.location),'rotation_euler':list(cam.rotation_euler),'ortho_scale':cam.data.ortho_scale,'shift':[cam.data.shift_x,cam.data.shift_y],'resolution':[w,h],'projection':'ORTHO'}
for style in ('clay','pbr'):
 render('head-45',45,style)
for stage in ('before','after'):
 for style in ('clay','pbr'):
  for name,angle in [('head-front',0),('head-profile',90),('head-45',45)]:
   if stage=='after' and name=='head-45':continue
   render(name,angle,style,stage)
  render('full-bird',70,style,stage,True,960)
for angle in range(0,360,45):render('turntable-%03d'%angle,angle,'clay',size=360)
# Role ID diagnostic keeps same camera while replacing only new object slots.
palette={'head-armor':(.25,.5,.75,1),'black-iron':(.08,.08,.10,1),'machined-steel':(.55,.55,.6,1),'worn-bronze':(.8,.42,.08,1),'protected-optic':(.7,.12,.03,1),'protected-glass':(.15,.7,.6,1)}
ids={}
for k,c in palette.items():
 d=bpy.data.materials.new('ID '+k);d.use_nodes=True;d.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=c;d.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.8;ids[k]=d
slots={o.name:list(o.data.materials) for o in s.objects if o.type=='MESH' and o.get('cgSupervisedHead04')}
for n in slots:
 o=s.objects[n]
 for i,f in enumerate(json.loads(o['cgSurfaceFamilies'])):o.data.materials[i]=ids[f]
render('head-45',45,'material-id')
for n,ms in slots.items():
 for i,mat in enumerate(ms):s.objects[n].data.materials[i]=mat
s.view_layers[0].material_override=None
bpy.context.preferences.filepaths.save_version=0;native=O/'volumetric-head04.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native))
bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene
receipt['saved_native_preservation']={'changed_original_meshes':[n for n,h in originals.items() if digest(s.objects[n])!=h],'changed_anchors':[n for n,h in anchors.items() if [list(r) for r in s.objects[n].matrix_world]!=h]}
receipt['native_sha256']=sha(native);receipt['cameras']=cameras;receipt['input_preserved']=sha(I)==receipt['input_sha256'];receipt['source_hashes']={str(p.relative_to(S)):sha(p) for p in [S/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg',S/'context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png']};receipt['render_settings']={'engine':'CYCLES','samples':8,'view':'AgX Medium High Contrast','world_strength':.5};receipt['images']={p.name:sha(p) for p in O.glob('*.png')}
(O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('HEAD04_COMPLETE',len(receipt['images']),flush=True)
