"""Write-once early native V20 cage candidate and matched clay views, no export."""
from pathlib import Path
import bpy,json,hashlib,argparse,sys,shutil,runpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--attempt',required=True);p.add_argument('--mechanism-layout');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
BASE=ROOT/'assets/models/whole-character-v19/attempt-02/murderbird-whole-character-v19.blend';EXPECTED='d98c46770101ad608fe2c50212a7b307ca66d5389f93ce7d43b79b9c7d41dded'
AUDIT=ROOT/f'assets/audit/whole-character-v20/attempt-{a.attempt}';OUT=ROOT/f'assets/models/whole-character-v20/attempt-{a.attempt}'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def art(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}
assert sha(BASE)==EXPECTED and not AUDIT.exists() and not OUT.exists();AUDIT.mkdir(parents=True);OUT.mkdir(parents=True)
shutil.copy2(__file__,AUDIT/'executed-composition.py');source=ROOT/'scripts/regions/whole-character-v20-proportions.py';shutil.copy2(source,AUDIT/'executed-proportions.py')
h=runpy.run_path(str(ROOT/'scripts/build-uncaged-alignment-v7.py'));bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']();mats={m.name:h['material_signature'](m) for m in bpy.data.materials}
result=runpy.run_path(str(source))['apply']();(AUDIT/'rig-shape-contract.json').write_text(json.dumps(result,indent=2))
if a.mechanism_layout:
 layout=json.loads(Path(a.mechanism_layout).read_text());bpy.data.objects['body']['mechanismLayoutV1']=json.dumps(layout,separators=(',',':'));shutil.copy2(a.mechanism_layout,AUDIT/'mechanism-layout-v1.json')
after=h['scene_snapshot']();assert set(before['empties'])==set(after['empties']);assert all(before['empties'][n]['parent']==after['empties'][n]['parent'] for n in before['empties']);assert mats=={m.name:h['material_signature'](m) for m in bpy.data.materials}
changed=[n for n in before['meshes'] if before['meshes'][n]!=after['meshes'][n]];native=OUT/'murderbird-whole-character-v20.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
receipt={'status':'early whole-body clay candidate; no artistic/engineering/motion acceptance','base':art(BASE),'native':art(native),'module':art(AUDIT/'executed-proportions.py'),'composer':art(AUDIT/'executed-composition.py'),'rigShapeContract':art(AUDIT/'rig-shape-contract.json'),'changedMeshes':changed,'preservation':{'rigidNamesAndParents':len(after['empties']),'materialsExact':True,'allPriorMeshIdentities':len(before['meshes']),'historicalSourceBinariesUntouched':True,'saveReopenExact':True},'views':[]}
(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2))
views=[('reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5),('front',(0,-7,1.65),(0,-.08,1.02),2.5),('side',(-7,0,1.35),(0,-.08,1.02),2.5),('neck',(-6,-3.5,2.45),(0,-.27,1.52),1.30)]
for label,path in [('after',native),('before',BASE)]:
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';sh=s.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='SINGLE';sh.single_color=(.56,.58,.60);sh.show_shadows=False;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';s.world.color=(.12,.13,.14);s.render.resolution_x=s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
 for obj in bpy.data.objects:
  obj.hide_set(False)
  if obj.type=='MESH':obj.hide_render='builder' not in obj.get('exteriorEras','maker,mechanic,builder').split(',')
  if obj.type=='CURVE':obj.hide_render=True
 cd=bpy.data.cameras.new('Temporary V20 clay camera');cd.type='ORTHO';cam=bpy.data.objects.new(cd.name,cd);s.collection.objects.link(cam);s.camera=cam
 for name,pos,target,scale in views:
  cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=scale;image=AUDIT/f'{label}-{name}.png';s.render.filepath=str(image);bpy.ops.render.render(write_still=True);receipt['views'].append({**art(image),'era':'builder','camera':{'position':pos,'target':target,'scale':scale},'lighting':'neutral native clay; cast shadows off; authoring guides hidden'})
(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2));assert sha(BASE)==EXPECTED;print(json.dumps({'native':receipt['native'],'changedMeshes':len(changed),'rigidNamesParents':len(after['empties'])}))
