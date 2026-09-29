"""Read-only matched rendering of the owner-rejected V10 native for progress review."""
from pathlib import Path
import hashlib,json
import bpy
from mathutils import Vector
ROOT=Path.cwd()
SRC=ROOT/'assets/models/uncaged-whole-body-v10/attempt-02/murderbird-whole-body-v10.blend'
OUT=ROOT/'assets/audit/whole-character-v18/rejected-v10-matched'
EXPECTED='6b2b43209d0474771010f3711f7d7ad2c00521f4d331c22a17d998f61a86c69f'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SRC)==EXPECTED
assert not (OUT/'receipt.json').exists()
bpy.ops.wm.open_mainfile(filepath=str(SRC))
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH'
sh=s.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='SINGLE'
sh.single_color=(.56,.58,.60);sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH'
sh.background_type='WORLD';s.world.color=(.12,.13,.14)
s.render.resolution_x=s.render.resolution_y=1100;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'
for obj in bpy.data.objects:
 obj.hide_set(False)
 if obj.type=='MESH':obj.hide_render='builder' not in obj.get('exteriorEras','maker,mechanic,builder').split(',')
 if obj.type=='CURVE':obj.hide_render=True
cd=bpy.data.cameras.new('Temporary matched review camera');cd.type='ORTHO'
cam=bpy.data.objects.new(cd.name,cd);s.collection.objects.link(cam);s.camera=cam
views=[('reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5),('front',(0,-7,1.65),(0,-.08,1.02),2.5),('side',(-7,0,1.35),(0,-.08,1.02),2.5),('head',(-6,-3.5,2.45),(0,-.27,1.56),1.12)]
rows=[]
for name,pos,target,scale in views:
 path=OUT/f'{name}.png';assert not path.exists()
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=scale
 s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
 rows.append({'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'position':pos,'target':target,'orthographicScale':scale})
assert sha(SRC)==EXPECTED
(OUT/'receipt.json').write_text(json.dumps({'status':'Owner-rejected V10 re-rendered with V18 matched neutral camera and light; no source edits or acceptance','native':{'path':SRC.relative_to(ROOT).as_posix(),'sha256':EXPECTED},'scriptSha256':sha(Path(__file__)),'views':rows},indent=2)+'\n')
