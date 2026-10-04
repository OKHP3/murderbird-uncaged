import bpy,json,hashlib,importlib.util,math,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];O=R/'assets/audit/cg-supervised-head08/attempt02';O.mkdir(exist_ok=True);S=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');I=S/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(I)=='72e7e53daf40b7128cdf9b173006c639bcf123952547a2576fb2de29130f06d4'
bpy.ops.wm.open_mainfile(filepath=str(I));s=bpy.context.scene
sp=importlib.util.spec_from_file_location('head08',R/'scripts/cg-supervised-head08.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
def digest(o):
 h=hashlib.sha256();a=np.empty(len(o.data.vertices)*3,dtype='<f4');o.data.vertices.foreach_get('co',a);h.update(a.tobytes());h.update(str([(tuple(p.vertices),p.material_index) for p in o.data.polygons]).encode());h.update(str([list(r) for r in o.matrix_world]).encode());h.update(str([x.name if x else None for x in o.data.materials]).encode());h.update(str(len(o.data.materials)).encode())
 for u in o.data.uv_layers:
  a=np.empty(len(u.data)*2,dtype='<f4');u.data.foreach_get('uv',a);h.update(u.name.encode());h.update(a.tobytes())
 return h.hexdigest()
originals={o.name:digest(o) for o in s.objects if o.type=='MESH'};anchors={o.name:[list(r) for r in o.matrix_world] for o in s.objects if o.type=='EMPTY'};oldvis={o.name:o.hide_render for o in s.objects if o.type=='MESH'}
receipt=m.apply(s,R,'builder');receipt['input_sha256']=sha(I);receipt['original_mesh_count']=len(originals);receipt['changed_original_meshes']=[n for n,h in originals.items() if digest(s.objects[n])!=h];receipt['changed_anchors']=[n for n,h in anchors.items() if [list(r) for r in s.objects[n].matrix_world]!=h]
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
# First pair prioritized within checkpoint bound.
for stage in ('before','after'):
 for style in ('clay','pbr'):render('source-full-bird',style=style,stage=stage,full=True)
for stage in ('before','after'):render('head-profile',90,'clay',stage)
for stage in ('before','after'):
 for style in ('clay','pbr'):
  for name,a in [('head-front',0),('head-profile',90),('head-grazing',135)]:
   if style=='clay' and name=='head-profile':continue
   render(name,a,style,stage)
  # full pair prioritized above
for angle in range(0,360,45):render('turntable-%03d'%angle,angle,'clay')
# Restore candidate and save editable full native, then read it back.
for o in s.objects:
 if o.get('cgSupervisedHead08'):o.hide_render=False
 elif o.name in oldvis:o.hide_render=True if o.name in receipt['hidden_originals'] else oldvis[o.name]
s.view_layers[0].material_override=None;bpy.context.preferences.filepaths.save_version=0;native=O/'formed-head08.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene
receipt['saved_native_preservation']={'changed_original_meshes':[n for n,h in originals.items() if digest(s.objects[n])!=h],'changed_anchors':[n for n,h in anchors.items() if [list(r) for r in s.objects[n].matrix_world]!=h]}
assert not receipt['saved_native_preservation']['changed_original_meshes'] and not receipt['saved_native_preservation']['changed_anchors']
dg=bpy.context.evaluated_depsgraph_get();bad=[];uvbad=[];new=[o for o in s.objects if o.get('cgSupervisedHead08')];tot=0
for o in new:
 eo=o.evaluated_get(dg);em=eo.to_mesh();tot+=len(em.vertices)
 if any(not all(math.isfinite(v) for v in q.co) for q in em.vertices):bad.append(o.name)
 eo.to_mesh_clear()
 if not o.data.uv_layers or any(not all(math.isfinite(v) and -.001<=v<=1.001 for v in d.uv) for d in o.data.uv_layers.active.data):uvbad.append(o.name)
receipt['evaluated_geometry']={'new_meshes':len(new),'evaluated_vertices':tot,'nonfinite_meshes':bad,'invalid_normalized_uv_meshes':uvbad};assert not bad and not uvbad
bpy.ops.object.select_all(action='DESELECT')
for o in new:o.select_set(True)
smoke=O/'head08-static-smoke.glb';bpy.ops.export_scene.gltf(filepath=str(smoke),export_format='GLB',use_selection=True,export_animations=False,export_apply=True,export_materials='NONE')
receipt['static_export_smoke']={'path':smoke.name,'bytes':smoke.stat().st_size,'sha256':sha(smoke),'scope':'new head sheets only, evaluated modifiers, no materials/animation; not integrated runtime export'}
receipt['native_sha256']=sha(native);receipt['script_sha256']=sha(R/'scripts/cg-supervised-head08.py');receipt['input_preserved']=sha(I)==receipt['input_sha256'];receipt['cameras']=cameras;receipt['camera_status']='Global35 source hypothesis reused identically before/after; estimated, not calibrated';receipt['render_settings']={'engine':'CYCLES','samples':4,'denoise':True,'view':'AgX Medium High Contrast','world_strength':.4,'source_aspect':[1280,853]};receipt['images']={p.name:sha(p) for p in O.glob('*.png')};receipt['source_hashes']={str(p.relative_to(S)):sha(p) for p in [S/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg',S/'context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png']};receipt['not_run']=['three-era integration','finish rerouting','browser/export parity','animation','owner acceptance','engineering','remote CI/deployment']
(O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('HEAD08_COMPLETE',len(receipt['images']),flush=True)
