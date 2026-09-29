import bpy,bmesh,json,hashlib,math,runpy
from pathlib import Path
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree
root=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');out=Path('/tmp/v22-cassette-study02');out.mkdir(exist_ok=False)
source=root/'scripts/regions/whole-character-v22-neck-cassette.py';base=root/'assets/models/whole-character-v22/attempt-frame04/murderbird-whole-character-v22.blend'
assert hashlib.sha256(base.read_bytes()).hexdigest()=='b3ac4677d2e76a0e08544323306c07f2ed7e61cd381d274a944d8e5b87031d1f'
bpy.ops.wm.open_mainfile(filepath=str(base));s=runpy.run_path(str(source));receipt=s['apply']();out.joinpath('executed-neck-cassette.py').write_bytes(source.read_bytes())
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
# Source snapshot/pose reset happens in-memory only; native saved with actual rest.
rest={n:(bpy.data.objects[n].rotation_mode,bpy.data.objects[n].rotation_euler.copy(),bpy.data.objects[n].rotation_quaternion.copy()) for n in ('body','neck','cervical-upper','head','cervical-joint-cover','cervical-root-cover','cervical-skull-cover')}
finite=0;issues=[];solids=[];dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
 if o.type!='MESH':continue
 ev=o.evaluated_get(dg);m=ev.to_mesh();assert all(math.isfinite(x) for v in m.vertices for x in v.co),o.name;finite+=1
 if o.name in receipt['changed']+receipt['added']:
  cp=m.copy();repair=cp.validate(verbose=False);bpy.data.meshes.remove(cp)
  bm=bmesh.new();bm.from_mesh(m);closed=all(e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free()
  solids.append({'name':o.name,'closed':closed,'volume':volume,'validateRepair':repair,'vertices':len(m.vertices)})
  if not closed or volume<=0 or repair:issues.append(o.name)
 ev.to_mesh_clear()
bpy.context.preferences.filepaths.save_version=0;native=out/'cassette-rest.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False)
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';sh=scene.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='SINGLE';sh.single_color=(.56,.58,.60);sh.show_shadows=False;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
for o in bpy.data.objects:
 if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
 elif o.type=='CURVE':o.hide_render=True
camdata=bpy.data.cameras.new('temporary cassette camera');camdata.type='ORTHO';camdata.ortho_scale=1.6;cam=bpy.data.objects.new(camdata.name,camdata);scene.collection.objects.link(cam);scene.camera=cam;cam.location=(-6,-3.5,2.45);cam.rotation_euler=(Vector((0,-.27,1.42))-cam.location).to_track_quat('-Z','Y').to_euler()
poses=[];skinnames=[n for n in receipt['added'] if bpy.data.objects[n].type=='MESH'];scope=('body','breastplate','neck','cervical-upper','head','jaw','upper-bill','cranial-cover','builder-optics','cervical-joint-cover','cervical-root-cover','cervical-skull-cover')
for label,q,yaw,hx in [('rest',0,0,0),('maker',-.14,-.45,0),('contact',.65,0,-.731)]:
 for n,(mode,euler,quat) in rest.items():o=bpy.data.objects[n];o.rotation_mode=mode;o.rotation_euler=euler;o.rotation_quaternion=quat
 bpy.data.objects['body'].rotation_euler.x=.12425 if label=='contact' else 0
 bpy.data.objects['neck'].rotation_euler.x=.35*q
 # NativeZ corresponds to browser-localY yaw.
 bpy.data.objects['neck'].rotation_mode='QUATERNION'
 bpy.data.objects['neck'].rotation_quaternion=Quaternion(Vector((1,0,0)),.35*q)@Quaternion(Vector((0,0,1)),yaw)
 bpy.data.objects['cervical-upper'].rotation_euler.x=.65*q;bpy.data.objects['head'].rotation_euler.x=hx;bpy.data.objects['cervical-joint-cover'].rotation_euler.x=.325*q
 for node,target in [('cervical-root-cover','neck'),('cervical-skull-cover','head')]:
  joint=bpy.data.objects[target];cover=bpy.data.objects[node];restJoint=rest[target][1].to_quaternion();restCover=rest[node][1].to_quaternion();currentJoint=joint.rotation_quaternion if joint.rotation_mode=='QUATERNION' else joint.rotation_euler.to_quaternion();delta=currentJoint@restJoint.inverted()
  cover.rotation_mode='QUATERNION';cover.rotation_quaternion=Quaternion().slerp(delta,.5)@restCover
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();parts={}
 for o in bpy.data.objects:
  if o.type!='MESH' or not o.parent or o.parent.name not in scope:continue
  ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();pts=[ev.matrix_world@v.co for v in m.vertices];tri=[tuple(t.vertices) for t in m.loop_triangles]
  if pts and tri:parts[o.name]=(o.parent.name,BVHTree.FromPolygons(pts,tri,all_triangles=True),[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)])
  ev.to_mesh_clear()
 pairs=[]
 for n in skinnames:
  a=parts[n]
  for n2,b in parts.items():
   if a[0]==b[0] or(n2 in skinnames and n2<n):continue
   if any(a[3][i]<b[2][i] or b[3][i]<a[2][i] for i in range(3)):continue
   hits=a[1].overlap(b[1])
   if hits:pairs.append([n,n2,len(hits)])
 poses.append({'label':label,'totalPitch':q,'neckYawNativeZ':yaw,'headLocalX':hx,'pairs':pairs});print('POSE',label,len(pairs),json.dumps(pairs))
 scene.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)
result={'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'baseSHA256':hashlib.sha256(base.read_bytes()).hexdigest(),'nativeSHA256':hashlib.sha256(native.read_bytes()).hexdigest(),'applyReceipt':receipt,'finiteEvaluatedMeshes':finite,'finiteIssues':issues,'solids':solids,'poses':poses,'limits':['Only3discrete actual relationships, not whole motion or continuous clearance.','Changed25skins vs adjacent scoped owners; same-owner overlaps not screened.','Primitive Boolean receiving cavity geometry is a coarse construction proposal.']}
out.joinpath('result.json').write_text(json.dumps(result,indent=2)+'\n');print('SUMMARY',result['sourceSHA256'],finite,issues)
