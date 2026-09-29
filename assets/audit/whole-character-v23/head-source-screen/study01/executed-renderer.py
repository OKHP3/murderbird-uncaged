import bpy,bmesh,json,hashlib,math,runpy
from pathlib import Path
from mathutils import Vector
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=Path('/tmp/v23-head-study/attempt01');OUT.mkdir(parents=True,exist_ok=True)
source=ROOT/'scripts/regions/whole-character-v23-head.py';base=ROOT/'assets/models/whole-character-v22/attempt-frame04/murderbird-whole-character-v22.blend'
assert hashlib.sha256(base.read_bytes()).hexdigest()=='b3ac4677d2e76a0e08544323306c07f2ed7e61cd381d274a944d8e5b87031d1f'
bpy.ops.wm.open_mainfile(filepath=str(base));nodes={o.name:([list(r) for r in o.matrix_world],o.parent.name if o.parent else None,dict(o.items())) for o in bpy.data.objects if o.type=='EMPTY'}
materials={m.name:repr(m) for m in bpy.data.materials};receipt=runpy.run_path(str(source))['apply']();OUT.joinpath('executed-head.py').write_bytes(source.read_bytes());OUT.joinpath('executed-renderer.py').write_bytes(Path(__file__).read_bytes())
issues=[];solids=[];dg=bpy.context.evaluated_depsgraph_get()
for name in receipt['changed']:
 o=bpy.data.objects[name];ev=o.evaluated_get(dg);m=ev.to_mesh();assert all(math.isfinite(c) for v in m.vertices for c in v.co),name
 cp=m.copy();rep=cp.validate(verbose=False);bpy.data.meshes.remove(cp);bm=bmesh.new();bm.from_mesh(m);closed=all(e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);bm.free();solids.append({'name':name,'closed':closed,'positiveVolume':vol>0,'volume':vol,'validateRepair':rep})
 if not closed or vol<=0 or rep:issues.append(name)
 ev.to_mesh_clear()
assert nodes=={o.name:([list(r) for r in o.matrix_world],o.parent.name if o.parent else None,dict(o.items())) for o in bpy.data.objects if o.type=='EMPTY'}
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
bpy.context.preferences.filepaths.save_version=0;native=OUT/'head-rest.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False)
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';sh=scene.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='SINGLE';sh.single_color=(.56,.58,.60);sh.show_shadows=False;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
for o in bpy.data.objects:
 if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
 elif o.type=='CURVE':o.hide_render=True
camdata=bpy.data.cameras.new('V23 temporary head camera');camdata.type='ORTHO';camdata.ortho_scale=.79;cam=bpy.data.objects.new(camdata.name,camdata);scene.collection.objects.link(cam);scene.camera=cam
for label,loc,jaw in [('rest',(-6,-3.0,2.8),0),('side',(-6,-.48,1.78),0),('jaw-open',(-6,-3.,2.8),.32)]:
 bpy.data.objects['jaw'].rotation_euler.x=jaw;bpy.context.view_layer.update();cam.location=loc;cam.rotation_euler=(Vector((0,-.446,1.737))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/(label+'.png'));bpy.ops.render.render(write_still=True)
r={'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'rendererSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'baseSHA256':hashlib.sha256(base.read_bytes()).hexdigest(),'nativeSHA256':hashlib.sha256(native.read_bytes()).hexdigest(),'receipt':receipt,'solids':solids,'issues':issues,'poses':[{'image':'rest.png','jawX':0},{'image':'side.png','jawX':0},{'image':'jaw-open.png','jawX':.32}],'limits':['Three neutral native stills only; no export, continuous clearance or owner likeness acceptance.']}
OUT.joinpath('result.json').write_text(json.dumps(r,indent=2)+'\n');print('RESULT',r['sourceSHA256'],len(receipt['changed']),len(receipt['removed']),issues)
