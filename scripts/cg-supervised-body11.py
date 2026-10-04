"""BODY11 sparse anterior throat-to-keel cage diagnosis, not final exterior.
One continuous open horseshoe loft; no plates, pose/material/lighting changes.
"""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy, bmesh
from mathutils import Vector
SOURCE_SHA='72e7e53daf40b7128cdf9b173006c639bcf123952547a2576fb2de29130f06d4'
REF_SHA='645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114'
CANDIDATE_SHA='538c51bcdbf5bfce95a0932fdbbb0f5868b446f4985346d15e6cacd32430e633'
# z, anterior center y, transverse radius, horseshoe depth rise.
# Front rail expands obliquely before maximum then tucks; lateral boundary is
# open and held anterior to preserved mechanism corridor. All values inferred.
SECTIONS=[(1.56,-.236,.095,.108),(1.48,-.225,.099,.115),(1.40,-.225,.104,.127),(1.30,-.278,.142,.192),(1.24,-.355,.205,.265),(1.14,-.420,.253,.334),(.95,-.360,.224,.313),(.76,-.185,.116,.171)]
SECTIONS02=[(1.56,-.236,.095,.108),(1.48,-.270,.123,.128),(1.40,-.305,.153,.156),(1.30,-.361,.204,.227),(1.24,-.399,.246,.282),(1.14,-.450,.288,.364),(.95,-.360,.224,.313),(.76,-.185,.116,.171)]
HIDE_MANIFEST=['CGN03 recessed anterior mechanism backing -1.17', 'CGN03 recessed anterior mechanism backing -0.47', 'CGN03 recessed anterior mechanism backing 0.34', 'CGB05 breast curved feather 00-0', 'CGB05 breast curved feather 00-1', 'CGB05 breast curved feather 00-2', 'CGB05 breast curved feather 00-3', 'CGB05 breast curved feather 00-4', 'CGB05 breast curved feather 00-5', 'CGB05 breast curved feather 00-6', 'CGB05 breast curved feather 01-0', 'CGB05 breast curved feather 01-1', 'CGB05 breast curved feather 01-2', 'CGB05 breast curved feather 01-3', 'CGB05 breast curved feather 01-4', 'CGB05 breast curved feather 01-5', 'CGB05 breast curved feather 01-6', 'CGB05 breast curved feather 02-0', 'CGB05 breast curved feather 02-1', 'CGB05 breast curved feather 02-2', 'CGB05 breast curved feather 02-3', 'CGB05 breast curved feather 02-4', 'CGB05 breast curved feather 02-5', 'CGB05 breast curved feather 02-6', 'CGB05 breast curved feather 03-0', 'CGB05 breast curved feather 03-1', 'CGB05 breast curved feather 03-2', 'CGB05 breast curved feather 03-3', 'CGB05 breast curved feather 03-4', 'CGB05 breast curved feather 03-5', 'CGB05 breast curved feather 03-6', 'CGB05 breast curved feather 04-0', 'CGB05 breast curved feather 04-1', 'CGB05 breast curved feather 04-2', 'CGB05 breast curved feather 04-3', 'CGB05 breast curved feather 04-4', 'CGB05 breast curved feather 04-5', 'CGB05 breast curved feather 04-6', 'CGB05 breast curved feather 05-0', 'CGB05 breast curved feather 05-1', 'CGB05 breast curved feather 05-2', 'CGB05 breast curved feather 05-3', 'CGB05 breast curved feather 05-4', 'CGB05 breast curved feather 05-5', 'CGB05 breast curved feather 05-6', 'CGB05 breast curved feather 06-0', 'CGB05 breast curved feather 06-1', 'CGB05 breast curved feather 06-2', 'CGB05 breast curved feather 06-3', 'CGB05 breast curved feather 06-4', 'CGB05 breast curved feather 06-5', 'CGB05 breast curved feather 06-6', 'CGB05 breast curved feather 07-0', 'CGB05 breast curved feather 07-1', 'CGB05 breast curved feather 07-2', 'CGB05 breast curved feather 07-3', 'CGB05 breast curved feather 07-4', 'CGB05 breast curved feather 07-5', 'CGB05 breast curved feather 07-6', 'CGB05 breast curved feather 08-0', 'CGB05 breast curved feather 08-1', 'CGB05 breast curved feather 08-2', 'CGB05 breast curved feather 08-3', 'CGB05 breast curved feather 08-4', 'CGB05 breast curved feather 08-5', 'CGB05 breast curved feather 08-6', 'CGB05 breast curved feather 09-0', 'CGB05 breast curved feather 09-1', 'CGB05 breast curved feather 09-2', 'CGB05 breast curved feather 09-3', 'CGB05 breast curved feather 09-4', 'CGB05 breast curved feather 09-5', 'CGB05 breast curved feather 09-6', 'CGB05 breast curved feather 10-0', 'CGB05 breast curved feather 10-1', 'CGB05 breast curved feather 10-2', 'CGB05 breast curved feather 10-3', 'CGB05 breast curved feather 10-4', 'CGB05 breast curved feather 10-5', 'CGB05 breast curved feather 10-6', 'CGB05 breast curved feather 11-0', 'CGB05 breast curved feather 11-1', 'CGB05 breast curved feather 11-2', 'CGB05 breast curved feather 11-3', 'CGB05 breast curved feather 11-4', 'CGB05 breast curved feather 11-5', 'CGB05 breast curved feather 11-6', 'CGB05 cervical curved lamina 00-0', 'CGB05 cervical curved lamina 00-1', 'CGB05 cervical curved lamina 00-2', 'CGB05 cervical curved lamina 00-3', 'CGB05 cervical curved lamina 01-0', 'CGB05 cervical curved lamina 01-1', 'CGB05 cervical curved lamina 01-2', 'CGB05 cervical curved lamina 01-3', 'CGB05 cervical curved lamina 02-0', 'CGB05 cervical curved lamina 02-1', 'CGB05 cervical curved lamina 02-2', 'CGB05 cervical curved lamina 02-3', 'CGB05 cervical curved lamina 03-0', 'CGB05 cervical curved lamina 03-1', 'CGB05 cervical curved lamina 03-2', 'CGB05 cervical curved lamina 03-3', 'CGB05 cervical curved lamina 04-0', 'CGB05 cervical curved lamina 04-1', 'CGB05 cervical curved lamina 04-2', 'CGB05 cervical curved lamina 04-3', 'CGB05 cervical curved lamina 05-0', 'CGB05 cervical curved lamina 05-1', 'CGB05 cervical curved lamina 05-2', 'CGB05 cervical curved lamina 05-3', 'CGB05 cervical curved lamina 06-0', 'CGB05 cervical curved lamina 06-1', 'CGB05 cervical curved lamina 06-2', 'CGB05 cervical curved lamina 06-3', 'CGB05 cervical curved lamina 07-0', 'CGB05 cervical curved lamina 07-1', 'CGB05 cervical curved lamina 07-2', 'CGB05 cervical curved lamina 07-3', 'CGB05 cervical curved lamina 08-0', 'CGB05 cervical curved lamina 08-1', 'CGB05 cervical curved lamina 08-2', 'CGB05 cervical curved lamina 08-3', 'CGB05 cervical curved lamina 09-0', 'CGB05 cervical curved lamina 09-1', 'CGB05 cervical curved lamina 09-2', 'CGB05 cervical curved lamina 09-3', 'CGB05 -1 channel edge curved lamina 00', 'CGB05 -1 channel edge curved lamina 01', 'CGB05 -1 channel edge curved lamina 02', 'CGB05 -1 channel edge curved lamina 03', 'CGB05 -1 channel edge curved lamina 04', 'CGB05 -1 channel edge curved lamina 05', 'CGB05 -1 channel edge curved lamina 06', 'CGB05 -1 channel edge curved lamina 07', 'CGB05 -1 channel edge curved lamina 08', 'CGB05 -1 channel edge curved lamina 09', 'CGB05 -1 channel edge curved lamina 10', 'CGB05 1 channel edge curved lamina 00', 'CGB05 1 channel edge curved lamina 01', 'CGB05 1 channel edge curved lamina 02', 'CGB05 1 channel edge curved lamina 03', 'CGB05 1 channel edge curved lamina 04', 'CGB05 1 channel edge curved lamina 05', 'CGB05 1 channel edge curved lamina 06', 'CGB05 1 channel edge curved lamina 07', 'CGB05 1 channel edge curved lamina 08', 'CGB05 1 channel edge curved lamina 09', 'CGB05 1 channel edge curved lamina 10']
def apply(scene,root_path=None,era='builder'):
 if any(o.get('cgSupervisedBody11') for o in scene.objects):raise RuntimeError('Reload receiving native')
 mats={};mat_sources={}
 for o in scene.objects:
  if o.type!='MESH' or o.hide_render or not o.get('cgSupervisedBody05'):continue
  for i,f in enumerate(json.loads(o.get('cgSurfaceFamilies','[]'))):
   if i<len(o.data.materials) and o.data.materials[i]:mats.setdefault(f,o.data.materials[i]);mat_sources.setdefault(f,{'object':o.name,'slot':i,'material':o.data.materials[i].name})
 assert len(HIDE_MANIFEST)==149 and len(set(HIDE_MANIFEST))==149
 for name in HIDE_MANIFEST:
  o=scene.objects.get(name);assert o and not o.hide_render,name
  o.hide_render=True;o.hide_set(True)
 coll=bpy.data.collections.new('BODY11 diagnostic anterior open cage');scene.collection.children.link(coll)
 # Explicit ID references preserve receiving orphan packed maps through save.
 # No image, graph, material or rendered appearance is modified.
 for i,image in enumerate(bpy.data.images):
  if image.packed_file:coll['receivingPackedImage%03d'%i]=image
 vs=[];uv=[];angles=[-1.12,-1.08,-.72,-.36,0,.36,.72,1.08,1.12]
 for j,(z,y,rx,ry) in enumerate(SECTIONS):
  for k,a in enumerate(angles):
   # Inset return end is longitudinal and sparse, never torso-encircling.
   x=rx*math.sin(a);depth=ry*(1-math.cos(a))
   if k in (0,8):x*=.955;depth+=.012
   vs.append((x,y+depth,z));uv.append((k/8,j/7))
 fs=[]
 for j in range(7):
  for k in range(8):
   a=j*9+k;fs.append((a,a+1,a+10,a+9))
 d=bpy.data.meshes.new('body11 eight editable horseshoe sections');d.from_pydata(vs,[],fs);d.update()
 o=bpy.data.objects.new('CGB11 continuous anterior throat keel cage',d);coll.objects.link(o)
 for f in ('breast-armor','black-iron'):d.materials.append(mats[f])
 layer=d.uv_layers.new(name='body11-normalized-section-uv')
 for p in d.polygons:
  p.use_smooth=True
  for li in p.loop_indices:layer.data[li].uv=uv[d.loops[li].vertex_index]
 bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
 if sum((f.normal for f in bm.faces),Vector()).y>0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(d);bm.free()
 sub=o.modifiers.new('editable sparse horseshoe SubD','SUBSURF');sub.levels=sub.render_levels=2
 sol=o.modifiers.new('diagnostic thin metal section','SOLIDIFY');sol.thickness=.0018;sol.offset=-1;sol.material_offset=1;sol.material_offset_rim=1
 for k,v in {'cgSupervisedBody11':True,'cg1cRegion':'body','cg2bRegion':'body','surfaceRole':'breast-armor','cgSurfaceFamilies':json.dumps(['breast-armor','black-iron']),'exteriorEras':'maker,mechanic,builder','cgConstructionStatus':'Diagnostic smooth cage only; not final exterior; no owner acceptance','body11SectionControls':json.dumps(SECTIONS),'body11OpenHorseshoeAngles':json.dumps(angles)}.items():o[k]=v
 bpy.context.view_layer.update()
 deps=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(deps);md=ev.to_mesh();points=[tuple(o.matrix_world@v.co) for v in md.vertices];bound={'min':[min(v[i] for v in points) for i in range(3)],'max':[max(v[i] for v in points) for i in range(3)]};ev.to_mesh_clear()
 return {'evaluatedCageBounds':bound,'module':'cg-supervised-body11','era':era,'newMeshes':1,'retainedHidden':HIDE_MANIFEST,'actualCageSections':SECTIONS,'actualCageAnglesRadians':angles,'controlVertices':vs,'controlFaces':fs,'actualVisibleReceivingMaterialSources':mat_sources,'method':'One sparse open anterior horseshoe loft with continuous throat-to-keel rail and editable SubD','limits':['Smooth cage diagnosis only, not final exterior','All source depth and cage section values are inferred','Pose retained; actual breast maximum extent must be checked in extra-preservation-and-extents.json','July body excluded','No owner likeness acceptance']}
def digest(o):
 h=hashlib.sha256();data=[[tuple(r) for r in o.matrix_world],o.parent.name if o.parent else None,dict(o.items()),dict(o.data.items()) if o.data else None]
 if o.type=='MESH':
  data += [[(a.name,a.domain,a.data_type,[tuple(getattr(v,'color',())) for v in a.data]) for a in o.data.color_attributes], [[(g.group,g.weight) for g in v.groups] for v in o.data.vertices]]
 if o.type=='MESH':data += [[tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],[(u.name,[tuple(v.uv) for v in u.data]) for u in o.data.uv_layers],[m.name if m else None for m in o.data.materials],[p.material_index for p in o.data.polygons]]
 for v in data:h.update(repr(v).encode())
 return h.hexdigest()
def material_digest():
 result={}
 for m in bpy.data.materials:
  if m.name=='Body11 diagnostic clay':continue
  values=[m.name,tuple(m.diffuse_color),m.use_nodes]
  if m.use_nodes:
   for n in m.node_tree.nodes:
    inputs=[]
    for inp in n.inputs:
     if hasattr(inp,'default_value'):
      v=inp.default_value
      try:v=list(v)
      except TypeError:pass
      inputs.append((inp.name,v))
    values.append((n.name,n.bl_idname,n.label,inputs,n.image.name if hasattr(n,'image') and n.image else None))
   values.append([(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links])
  result[m.name]=hashlib.sha256(repr(values).encode()).hexdigest()
 return result

def packed_image_digest():
 return {i.name:hashlib.sha256(bytes(i.packed_file.data)).hexdigest() for i in bpy.data.images if i.packed_file}

def diagnostic():
 p=argparse.ArgumentParser();p.add_argument('--input-root',required=True);p.add_argument('--attempt',default='attempt01');p.add_argument('--resolution',type=int,default=800);p.add_argument('--samples',type=int,default=6);args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
 global SECTIONS
 if args.attempt=='attempt02':SECTIONS=SECTIONS02
 root=Path(__file__).resolve().parents[1];inp=Path(args.input_root);out=root/'assets/audit/cg-supervised-body11'/args.attempt;out.mkdir(parents=True,exist_ok=True)
 source=inp/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend';ref=inp/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
 assert sha(source)==SOURCE_SHA;assert sha(ref)==REF_SHA
 bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
 saved_transforms={o.name:(o.location.copy(),o.rotation_euler.copy(),o.scale.copy()) for o in s.objects if o.type in ('CAMERA','LIGHT')};saved_camera=(s.camera.data.type,s.camera.data.ortho_scale,s.camera.data.shift_x,s.camera.data.shift_y);original_materials=material_digest();original_packed=packed_image_digest()
 visibility_full={o.name:[o.hide_render,o.hide_viewport,o.hide_get()] for o in s.objects}
 candidate=inp/'assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png';assert sha(candidate)==CANDIDATE_SHA
 frozen={o.name:digest(o) for o in s.objects if o.type in ('MESH','EMPTY')};visibility={o.name:o.hide_render for o in s.objects if o.type=='MESH'}
 s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=args.samples;s.cycles.use_denoising=True;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
 prior=json.loads((inp/'assets/audit/cg-supervised01/attempt06/builder/receipt.json').read_text());cam=s.camera;cameras={};initiallights={o.name:(o.location.copy(),o.rotation_euler.copy(),o.data.energy,o.data.color[:],o.data.size) for o in s.objects if o.type=='LIGHT'}
 clay=bpy.data.materials.new('Body11 diagnostic clay');clay.diffuse_color=(.34,.34,.34,1);clay.use_nodes=True;clay.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.64;clay.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.23,.23,.23,1)
 def render(name,view='whole',claypass=False,grazing=False):
  q=json.loads((inp/'assets/audit/cg-supervised-camera04/receipt.json').read_text())['hypotheses']['ortho-35']['camera'];cam.location=q['location'];cam.rotation_euler=q['rotation_euler'];cam.data.type='ORTHO';cam.data.ortho_scale=q['ortho_scale'];cam.data.shift_x,cam.data.shift_y=q['shift']
  s.render.resolution_x=args.resolution;s.render.resolution_y=round(args.resolution*853/1280)
  if view=='whole64':
   q=json.loads((inp/'assets/audit/cg-supervised-camera04/receipt.json').read_text())['body_only_diagnostic']['camera'];cam.location=q['location'];cam.rotation_euler=q['rotation_euler'];cam.data.ortho_scale=q['ortho_scale'];cam.data.shift_x,cam.data.shift_y=q['shift']
  if view not in ('whole','whole64'):
   position={'side':(-6,0,1.2),'front':(0,-6,1.2),'body':(-6,-2.4,1.5),'whole-side':(-6,0,1.00),'whole-front':(0,-6,1.00)}[view];target=(0,-.045,.97 if view.startswith('whole-') else 1.17);cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=3.20 if view.startswith('whole-') else 1.00;cam.data.shift_x=cam.data.shift_y=0;s.render.resolution_y=round(args.resolution*853/1280)
  s.view_layers[0].material_override=clay if claypass else None
  for o in s.objects:
   if o.type!='LIGHT':continue
   loc,rot,power,color,size=initiallights[o.name];o.location=loc;o.rotation_euler=rot;o.data.energy=power;o.data.color=color;o.data.size=size
  if grazing:
   lights=[o for o in s.objects if o.type=='LIGHT'];lights[0].location=(-1,-.8,2.5);lights[0].rotation_euler=(Vector((0,0,1.1))-lights[0].location).to_track_quat('-Z','Y').to_euler();lights[0].data.size=.28;lights[0].data.energy=140
   for o in lights[1:]:o.data.energy*=.18
  cameras[name]={'location':list(cam.location),'rotation_euler':list(cam.rotation_euler),'scale':cam.data.ortho_scale,'shift':[cam.data.shift_x,cam.data.shift_y],'resolution':[s.render.resolution_x,s.render.resolution_y],'clay':claypass,'lights':[{'name':o.name,'location':list(o.location),'rotation':list(o.rotation_euler),'power':o.data.energy,'color':list(o.data.color),'size':o.data.size} for o in s.objects if o.type=='LIGHT']}
  s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 render('before-whole-pbr');render('before-whole-clay',claypass=True)
 result=apply(s,inp,'builder');render('after-whole-pbr');render('after-whole-clay',claypass=True)
 for stage in ('before','after'):
  for o in s.objects:
   if o.get('cgSupervisedBody11'):o.hide_render=stage=='before'
   elif o.name in result['retainedHidden']:o.hide_render=stage=='after'
  render(stage+'-body-grazing-clay','body',True,True)
  render(stage+'-front-clay','front',True);render(stage+'-side-clay','side',True)
  render(stage+'-profile-whole-pbr','whole-side');render(stage+'-profile-whole-clay','whole-side',True)
  render(stage+'-front-whole-pbr','whole-front');render(stage+'-front-whole-clay','whole-front',True)
  render(stage+'-whole-grazing-pbr',grazing=True);render(stage+'-whole-grazing-clay',claypass=True,grazing=True)
  render(stage+'-front-pbr','front');render(stage+'-side-pbr','side')
  render(stage+'-whole64-pbr','whole64');render(stage+'-whole64-clay','whole64',True)
 s.view_layers[0].material_override=None
 for i in range(8):
  a=math.radians(i*45);target=Vector((0,-.04,1));cam.location=target+Vector((6*math.sin(a),-6*math.cos(a),1.02));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=3.20;cam.data.shift_x=cam.data.shift_y=0;s.render.resolution_x=640;s.render.resolution_y=427
  name=f'turn-{i*45:03d}';s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);cameras[name]={'location':list(cam.location),'rotation':list(cam.rotation_euler),'scale':cam.data.ortho_scale,'resolution':[640,427]}
 render('after-whole-pbr')
 s.view_layers[0].material_override=None
 changed=[n for n,d in frozen.items() if digest(s.objects[n])!=d];unexpected=[n for n,v in visibility.items() if s.objects[n].hide_render!=v and n not in result['retainedHidden']];assert not changed and not unexpected,(changed,unexpected)
 for n,(loc,rot,scale) in saved_transforms.items():s.objects[n].location=loc;s.objects[n].rotation_euler=rot;s.objects[n].scale=scale
 cam.data.type,cam.data.ortho_scale,cam.data.shift_x,cam.data.shift_y=saved_camera
 bpy.context.view_layer.update()
 assert material_digest()==original_materials and packed_image_digest()==original_packed
 bpy.context.preferences.filepaths.save_version=0;native=out/'murderbird-body11.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native));nativehash=sha(native)
 bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;finite=[]
 for o in s.objects:
  if not o.get('cgSupervisedBody11'):continue
  assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
  assert all(math.isfinite(c) and -.00001<=c<=1.00001 for uv in o.data.uv_layers for v in uv.data for c in v.uv)
  ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());md=ev.to_mesh();assert all(math.isfinite(c) for v in md.vertices for c in v.co);assert all(math.isfinite(c) and -.00001<=c<=1.00001 for layer in md.uv_layers for v in layer.data for c in v.uv);finite.append({'name':o.name,'vertices':len(md.vertices),'evaluatedFinite':True,'normalizedUV':True});ev.to_mesh_clear()
 assert material_digest()==original_materials and packed_image_digest()==original_packed
 changedvisibility=[n for n,v in visibility_full.items() if n not in HIDE_MANIFEST and [s.objects[n].hide_render,s.objects[n].hide_viewport,s.objects[n].hide_get()]!=v];assert not changedvisibility
 for n in HIDE_MANIFEST:assert s.objects[n].hide_render and s.objects[n].hide_get()
 changedreadback=[n for n,d in frozen.items() if digest(bpy.context.scene.objects[n])!=d];assert not changedreadback
 result.update(originalPayloadDigests=frozen,receivingMaterialGraphDigests=original_materials,packedImageDigests=original_packed,diagnosticCameraLightTransformsRestoredBeforeSave=True,exactVisibilityStatesPreservedOutside149=True,candidate03SHA256=sha(candidate),finiteEvaluatedGeometryAndUV=finite,sourceSHA256=sha(source),sourceBinaryPreserved=sha(source)==SOURCE_SHA,referenceSHA256=sha(ref),nativeSHA256=nativehash,originalMeshesAndAnchorsChecked=len(frozen),receivingGeometryUVMaterialIndicesTransformsChanged=changed,savedNativePreservationReadback=changedreadback,unexpectedVisibilityChanges=unexpected,cameras=cameras,renderSettings={'engine':'CYCLES','samples':args.samples,'denoise':True,'viewTransform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure},images={f.name:sha(f) for f in out.glob('*.png')},status='Unaccepted CG proposal; likeness not established')
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print('BODY11_COMPLETE',out)
if __name__=='__main__':diagnostic()
