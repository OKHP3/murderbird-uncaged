import bpy, hashlib, json, runpy, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
NATIVE=ROOT/'assets/models/whole-character-v23/attempt-form03/murderbird-whole-character-v23.blend'
EXPECTED='66b6ff8c17e468c0e1ab7874728a3aea889a5630fd25dafc3392d954a1343e62'
OUT=Path('/tmp/v24-breast-study/attempt-01')
MODULE=ROOT/'scripts/regions/whole-character-v24-breast.py'

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
assert sha(NATIVE)==EXPECTED
bpy.ops.wm.open_mainfile(filepath=str(NATIVE))
scene=bpy.context.scene
for obj in bpy.data.objects:
 if obj.animation_data: obj.animation_data_clear()
 if obj.type=='MESH':obj.hide_render='builder' not in obj.get('exteriorEras','maker,mechanic,builder').split(',')
 elif obj.type=='CURVE':obj.hide_render=True
scene.render.engine='BLENDER_WORKBENCH'
sh=scene.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='SINGLE';sh.single_color=(.56,.58,.60);sh.show_shadows=False;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';scene.world.color=(.12,.13,.14)
scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
camdata=bpy.data.cameras.new('V24 temporary matched neutral camera');camdata.type='ORTHO';camera=bpy.data.objects.new(camdata.name,camdata);scene.collection.objects.link(camera);scene.camera=camera
views=[('front',(0,-7,1.65),(0,-.08,1.02),2.5),('side',(-7,0,1.35),(0,-.08,1.02),2.5),('three-quarter',(-6,-3.5,2.75),(0,-.08,1.02),2.5)]
receipt={'native':{'path':str(NATIVE),'sha256':EXPECTED},'modulePath':str(MODULE),'moduleSha256':sha(MODULE),'lighting':'neutral Workbench no cast shadows','views':[]}
def render(label,view,phase):
 name,pos,target,scale=view
 camera.location=pos;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camdata.ortho_scale=scale
 scene.render.filepath=str(OUT/f'{phase}-{name}.png');bpy.ops.render.render(write_still=True)
 p=Path(scene.render.filepath);receipt['views'].append({'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size,'phase':phase,'camera':{'position':pos,'target':target,'orthoScale':scale}})
for view in views:render('before',view,'before')
proposal=runpy.run_path(str(MODULE))['apply']()
for view in views:render('after',view,'after')
receipt['proposal']=proposal
receipt['studyNative']={'path':str(OUT/'murderbird-v24-breast-study.blend')}
bpy.ops.wm.save_as_mainfile(filepath=receipt['studyNative']['path'])
receipt['studyNative']['sha256']=sha(receipt['studyNative']['path'])
(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'studyNative':receipt['studyNative'],'removed':len(proposal['removedNames']),'created':len(proposal['createdNames']),'views':len(receipt['views'])}))
