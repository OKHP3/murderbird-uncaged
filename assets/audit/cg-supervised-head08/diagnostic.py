import bpy,json,hashlib,importlib.util,math,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];O=R/'assets/audit/cg-supervised-head08/diagnostic';O.mkdir(exist_ok=True);S=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');I=S/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(I)=='72e7e53daf40b7128cdf9b173006c639bcf123952547a2576fb2de29130f06d4'
bpy.ops.wm.open_mainfile(filepath=str(I));s=bpy.context.scene
def digest(o):
 h=hashlib.sha256();a=np.empty(len(o.data.vertices)*3,dtype='<f4');o.data.vertices.foreach_get('co',a);h.update(a.tobytes());h.update(str([(tuple(p.vertices),p.material_index) for p in o.data.polygons]).encode());h.update(str([list(r) for r in o.matrix_world]).encode());h.update(str([x.name if x else None for x in o.data.materials]).encode());h.update(str(len(o.data.materials)).encode())
 for u in o.data.uv_layers:
  a=np.empty(len(u.data)*2,dtype='<f4');u.data.foreach_get('uv',a);h.update(u.name.encode());h.update(a.tobytes())
 return h.hexdigest()
originals={o.name:digest(o) for o in s.objects if o.type=='MESH'};anchors={o.name:[list(r) for r in o.matrix_world] for o in s.objects if o.type=='EMPTY'};oldvis={o.name:o.hide_render for o in s.objects if o.type=='MESH'}
backing=s.objects['CGH05 curved recessed vault above cheek opening'];assert not backing.hide_render;backing.hide_render=True;receipt={'hidden_originals':[backing.name],'visible_backing':backing.name,'hidden04':s.objects['CGH04 nine section cranial vault'].hide_render};receipt['input_sha256']=sha(I);receipt['original_mesh_count']=len(originals);receipt['changed_original_meshes']=[n for n,h in originals.items() if digest(s.objects[n])!=h];receipt['changed_anchors']=[n for n,h in anchors.items() if [list(r) for r in s.objects[n].matrix_world]!=h]
assert not receipt['changed_original_meshes'] and not receipt['changed_anchors']
# New diagnostic lights/camera only; original light/camera transforms stay intact.
for o in s.objects:
 if o.type=='LIGHT':o.hide_render=True
world=bpy.data.worlds.new('Head08 neutral review');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.08,.08,.08,1);world.node_tree.nodes['Background'].inputs[1].default_value=.4;s.world=world
for j,(pos,power,size) in enumerate([((-3,-4,5),700,4),((4,-1,3),250,4),((0,4,4),500,3)]):
 d=bpy.data.lights.new('Head08 studio '+str(j),'AREA');o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler();d.energy=power;d.size=size
cd=bpy.data.cameras.new('Head08 review camera');cam=bpy.data.objects.new(cd.name,cd);s.collection.objects.link(cam);s.camera=cam
s.render.engine='CYCLES';s.cycles.samples=4;s.cycles.use_denoising=True;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.render.film_transparent=False
clay=bpy.data.materials.new('Head08 diagnostic clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.42,.42,.42,1);bs.inputs['Roughness'].default_value=.75
frame=s.objects['CG2b head frame'].matrix_world;center=frame@Vector((0,.045,-.065));cameras={};canon=json.loads((R/'assets/audit/cg-supervised-camera04/receipt.json').read_text())['hypotheses']['ortho-35']['camera']
def render(name,angle=90,style='pbr',stage='after',full=False):
 for o in s.objects:
  if o.type=='MESH':
   if o.get('cgSupervisedHead08'):o.hide_render=stage=='before'
   elif o.name in oldvis:o.hide_render=oldvis[o.name] if stage=='before' else (True if o.name in receipt['hidden_originals'] else oldvis[o.name])
 s.view_layers[0].material_override=clay if style=='clay' else None
 cd.type='ORTHO';cd.shift_x=cd.shift_y=0
 if full:
  cam.location=canon['location'];cam.rotation_euler=canon['rotation_euler'];cd.ortho_scale=canon['ortho_scale'];cd.shift_x,cd.shift_y=canon['shift']
 else:
  cam.location=center+Vector((-5*math.sin(math.radians(angle)),-5*math.cos(math.radians(angle)),.18));cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=.91
 s.render.resolution_x=1280;s.render.resolution_y=853
 key=stage+'-'+style+'-'+name;s.render.filepath=str(O/(key+'.png'));bpy.ops.render.render(write_still=True)
 cameras[key]={'location':list(cam.location),'rotation_euler':list(cam.rotation_euler),'ortho_scale':cd.ortho_scale,'shift':[cd.shift_x,cd.shift_y],'resolution':[1280,853],'projection':'ORTHO'}
 print('HEAD08_VISIBLE',key,flush=True)

for stage in ('before','after'):
 for style in ('clay','pbr'):
  render('source-full-bird',style=style,stage=stage,full=True)
  render('head-profile',90,style,stage)
  render('head-grazing',135,style,stage)
receipt['cameras']=cameras
(O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
