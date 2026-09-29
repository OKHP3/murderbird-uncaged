"""One neutral still from pinned runtime02 native; no geometry or native writes."""
from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');AUDIT=ROOT/'assets/audit/whole-character-v20/attempt-runtime02'
NATIVE=ROOT/'assets/models/whole-character-v20/attempt-runtime02/murderbird-whole-character-v20.blend';EXPECTED='eb15a9d87de56fb8a06004d9c69448c38089f0ecacd888e3e7fde921a353d42a';IMAGE=AUDIT/'after-reference-angle.png';RECEIPT=AUDIT/'render-receipt.json';SOURCE=Path(__file__)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def art(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}
assert sha(NATIVE)==EXPECTED and not IMAGE.exists() and not RECEIPT.exists()
prior=json.loads((ROOT/'assets/audit/whole-character-v20/attempt-runtime01/receipt.json').read_text());reference=next(v for v in prior['views'] if v['path'].endswith('/after-reference-angle.png'));camera=reference['camera']
bpy.ops.wm.open_mainfile(filepath=str(NATIVE));s=bpy.context.scene;s.frame_set(1);s.render.engine='BLENDER_WORKBENCH';sh=s.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='SINGLE';sh.single_color=(.56,.58,.60);sh.show_shadows=False;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';s.world.color=(.12,.13,.14);s.render.resolution_x=s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
for o in bpy.data.objects:
 o.hide_set(False)
 if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
 if o.type=='CURVE':o.hide_render=True
cd=bpy.data.cameras.new('Temporary runtime02 reference camera');cd.type='ORTHO';cam=bpy.data.objects.new(cd.name,cd);s.collection.objects.link(cam);s.camera=cam;cam.location=camera['position'];cam.rotation_euler=(Vector(camera['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=camera['scale'];s.render.filepath=str(IMAGE);bpy.ops.render.render(write_still=True)
assert sha(NATIVE)==EXPECTED
r={'status':'exact-runtime02 native neutral review lead; not likeness or motion acceptance','native':art(NATIVE),'image':art(IMAGE),'executedRenderSource':art(SOURCE),'matchedRuntime01CameraAndClaySettings':True,'runtime01Comparison':reference,'camera':camera,'era':'builder','lighting':reference['lighting'],'settings':{'engine':'BLENDER_WORKBENCH','studioLight':'paint.sl','singleColor':[.56,.58,.60],'castShadows':False,'cavity':'BOTH','worldColor':[.12,.13,.14],'resolution':[1100,1100]},'nativeHashUnchanged':True,'limits':['Runtime01 orthographic/era views may be reused as explicitly labelled shape comparisons; this image alone is bound to runtime02.','No geometry, material or visibility change was saved to the native.']};RECEIPT.write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
