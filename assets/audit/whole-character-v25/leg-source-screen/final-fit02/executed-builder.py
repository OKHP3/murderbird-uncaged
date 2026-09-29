from pathlib import Path
import bpy,runpy,json,hashlib,shutil,sys,math
from mathutils import Vector
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
BASE=ROOT/'assets/models/whole-character-v24/attempt-form02/murderbird-whole-character-v24.blend'
SOURCE=ROOT/'scripts/regions/whole-character-v25-leg-structure.py'
OUT=Path('/tmp/v25-leg-structure')/sys.argv[-1];assert not OUT.exists();OUT.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(BASE)=='acb91013e0ca7cf98475e0d2ba6fb36d9c081c29c91b27e104bf7367d57f306d'
shutil.copyfile(SOURCE,OUT/'executed-region.py');shutil.copyfile(__file__,OUT/'executed-builder.py')
shutil.copyfile(ROOT/'scripts/build-uncaged-alignment-v7.py',OUT/'executed-snapshot-helper.py')
h=runpy.run_path(str(OUT/'executed-snapshot-helper.py'))
bpy.ops.wm.open_mainfile(filepath=str(BASE));bpy.context.view_layer.update()
mats={m.name:h['material_signature'](m) for m in bpy.data.materials}
before=h['scene_snapshot']();result=runpy.run_path(str(OUT/'executed-region.py'))['apply']()
after=h['scene_snapshot']()
assert mats=={m.name:h['material_signature'](m) for m in bpy.data.materials}
assert before['empties']==after['empties']
protected=[]
for n,r in before['meshes'].items():
 if r['parent'] not in ('left-thigh','left-shin','right-thigh','right-shin'):
  assert after['meshes'][n]==r,n;protected.append(n)
for o in bpy.data.objects:
 if o.type=='MESH':
  assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
NATIVE=OUT/'murderbird-v25-leg-structure.blend';bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(NATIVE),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(NATIVE))
assert h['scene_snapshot']()==after
receipt={'baseSha256':sha(BASE),'nativeSha256':sha(NATIVE),'sourceSha256':sha(OUT/'executed-region.py'),'result':result,
 'checks':{'exactAllRests':len(before['empties']),'exactProtectedMeshes':len(protected),'materialDefinitionsExact':True,'saveReopenExact':True},'views':[]}
(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2))
scene=bpy.context.scene
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
 if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
 elif o.type=='CURVE':o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';sh=scene.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='SINGLE';sh.single_color=(.56,.58,.60);sh.show_shadows=False;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';scene.world.color=(.12,.13,.14)
scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
d=bpy.data.cameras.new('Temporary V25 leg camera');d.type='ORTHO';camera=bpy.data.objects.new(d.name,d);scene.collection.objects.link(camera);scene.camera=camera
views=[('front',(0,-7,1.65),(0,-.08,1.02),2.5),('side',(-7,0,1.35),(0,-.08,1.02),2.5),('reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5),('leg-closeup',(-6,-3.5,1.2),(-.20,-.01,.47),.95)]
for name,pos,target,scale in views:
 camera.location=pos;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale
 scene.render.filepath=str(OUT/f'after-{name}.png');bpy.ops.render.render(write_still=True)
 receipt['views'].append({'name':name,'sha256':sha(scene.render.filepath),'camera':{'position':pos,'target':target,'orthoScale':scale}})
 (OUT/'receipt.json').write_text(json.dumps(receipt,indent=2))
assert sha(NATIVE)==receipt['nativeSha256'] and sha(BASE)==receipt['baseSha256']
print(json.dumps(receipt['checks']))
