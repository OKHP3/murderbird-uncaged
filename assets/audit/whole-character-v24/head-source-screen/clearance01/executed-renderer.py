import bpy,bmesh,json,hashlib,math,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=Path('/tmp/v24-head-study/clearance01');OUT.mkdir(exist_ok=False)
base=Path('/tmp/v24-head-study/attempt02/head-rest.blend');source=ROOT/'scripts/regions/whole-character-v24-head-clearance.py';assert hashlib.sha256(base.read_bytes()).hexdigest()=='0ed55fd11e3cca91c2e77023293a83e49f38831ff642ef58ab5c174855b1cfae';bpy.ops.wm.open_mainfile(filepath=str(base));bpy.context.view_layer.update()
lib=runpy.run_path(str(source));targets=lib['TARGETS']
def screen(angle):
 bpy.data.objects['jaw'].rotation_euler.x=angle;bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();parts={}
 for o in bpy.data.objects:
  if o.type!='MESH' or not o.parent or o.parent.name not in {'jaw','upper-bill','head','cranial-cover','builder-optics'}:continue
  ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();p=[ev.matrix_world@v.co for v in m.vertices];t=[tuple(f.vertices) for f in m.loop_triangles];parts[o.name]=(BVHTree.FromPolygons(p,t,all_triangles=True),o.parent.name);ev.to_mesh_clear()
 pairs=[]
 for name in targets:
  a=parts[name]
  for name2,b in parts.items():
   if b[1]=='jaw':continue
   hits=a[0].overlap(b[0])
   if hits:pairs.append([name,name2,b[1],len(hits)])
 return {'jawX':angle,'pairs':pairs}
angles=[0,.08,.16,.24,.32];baseline=[screen(a) for a in angles];bpy.data.objects['jaw'].rotation_euler.x=0;bpy.context.view_layer.update();receipt=lib['apply']();OUT.joinpath('executed-head-clearance.py').write_bytes(source.read_bytes());OUT.joinpath('executed-renderer.py').write_bytes(Path(__file__).read_bytes());OUT.joinpath('executed-main-head.py').write_bytes((ROOT/'scripts/regions/whole-character-v24-head.py').read_bytes())
solids=[];dg=bpy.context.evaluated_depsgraph_get()
for name in targets:
 o=bpy.data.objects[name];ev=o.evaluated_get(dg);m=ev.to_mesh();assert all(math.isfinite(x) for v in m.vertices for x in v.co);cp=m.copy();repair=cp.validate(verbose=False);bpy.data.meshes.remove(cp);bm=bmesh.new();bm.from_mesh(m);closed=all(e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free();assert closed and volume>0 and not repair;solids.append({'name':name,'closed':closed,'volume':volume,'validateRepair':repair});ev.to_mesh_clear()
bpy.context.preferences.filepaths.save_version=0;native=OUT/'head-rest.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False)
poses=[screen(a) for a in angles]
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';sh=scene.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='SINGLE';sh.single_color=(.56,.58,.60);sh.show_shadows=False;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
for o in bpy.data.objects:
 if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
 elif o.type=='CURVE':o.hide_render=True
camdata=bpy.data.cameras.new('V24 temporary head camera');camdata.type='ORTHO';camdata.ortho_scale=.79;cam=bpy.data.objects.new(camdata.name,camdata);scene.collection.objects.link(cam);scene.camera=cam
for label,loc,jaw in [('rest',(-6,-3.0,2.8),0),('side',(-6,-.48,1.78),0),('jaw-open',(-6,-3.,2.8),.32)]:
 bpy.data.objects['jaw'].rotation_euler.x=jaw;bpy.context.view_layer.update();cam.location=loc;cam.rotation_euler=(Vector((0,-.446,1.737))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/(label+'.png'));bpy.ops.render.render(write_still=True)
r={'mainSourceSHA256':hashlib.sha256((ROOT/'scripts/regions/whole-character-v24-head.py').read_bytes()).hexdigest(),'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'rendererSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'baseSHA256':hashlib.sha256(base.read_bytes()).hexdigest(),'nativeSHA256':hashlib.sha256(native.read_bytes()).hexdigest(),'receipt':receipt,'solids':solids,'baselinePoses':baseline,'poses':poses,'limits':['Named evaluated triangle BVH overlaps of3jawterminalsurfaces vs adjacent fixedhead/bill/crown/optic owners; joint-root contacts inherited unless changed.','No full model/continuous movement/appearance acceptance.']};OUT.joinpath('result.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
