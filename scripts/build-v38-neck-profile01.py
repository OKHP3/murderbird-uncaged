from pathlib import Path
import bpy,json,hashlib,runpy,shutil
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'assets/models/whole-character-v38/neck-profile01/murderbird-v38-neck-profile01.blend';OUT=ROOT/'assets/models/whole-character-v38/neck-profile01/attempt02';AUDIT=ROOT/'assets/audit/whole-character-v38/neck-profile01/attempt02';NATIVE=OUT/'murderbird-v38-neck-profile01-attempt02.blend';REGION=ROOT/'scripts/regions/v38-neck-profile01.py'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(BASE)=='bd8ea9eb9b5ef62cb703938f140241715b174ec4ad922d4b65b31d979ffbee99';assert not NATIVE.exists()
OUT.mkdir(parents=True,exist_ok=True);AUDIT.mkdir(parents=True,exist_ok=True);shutil.copy2(__file__,AUDIT/'executed-builder.py');shutil.copy2(REGION,AUDIT/'executed-region.py')
bpy.ops.wm.open_mainfile(filepath=str(BASE));bpy.context.view_layer.update();before={n:list(bpy.data.objects[n].matrix_world.translation)for n in['head','jaw','upper-bill','cranial-cover','builder-optics','breastplate','body']}
contract=runpy.run_path(str(REGION))['apply']();bpy.context.view_layer.update();after={n:list(bpy.data.objects[n].matrix_world.translation)for n in before};assert all(max(abs(a-b)for a,b in zip(before[n],after[n]))<1e-6 for n in before),'Recognizable head/body rest shifted: '+str((before,after))
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(NATIVE),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(NATIVE))
# Render ONLY declared study and era-native retained scene; obsolete source skins stay hidden.
scene=bpy.context.scene
for o in bpy.data.objects:
 if o.type=='MESH':o.hide_render=o.get('silhouetteStudyHistoricalHidden')is True or o.get('authoringGuide')is True or 'builder' not in str(o.get('exteriorEras','maker,mechanic,builder')).split(',')
 elif o.type=='CURVE':o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
data=bpy.data.cameras.new('temporary matched outline gate');data.type='ORTHO';camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera);scene.camera=camera;records=[]
views=[('full-bird-three-quarter',(-6,-3.5,2.75),(0,-.08,1.03),2.4),('full-bird-profile',(-7,0,2.75),(0,-.08,1.03),2.4),('full-bird-front',(0,-7,2.75),(0,-.08,1.03),2.4),('full-bird-rear',(0,7,2.75),(0,-.08,1.03),2.4),('neck-profile',(-6,0,1.95),(0,-.35,1.41),.68)]
for name,pos,target,scale in views:
 camera.location=pos;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=scale;path=AUDIT/('candidate-'+name+'.png');scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);records.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),'camera':{'position':pos,'target':target,'scale':scale}});print('MEDIA',path,flush=True)
receipt={'status':'Final rigid silhouette PROXY: stronger underjaw depth constriction; outline direction only, no functionalfit or owneracceptance','inputNative':{'path':str(BASE.relative_to(ROOT)),'sha256':sha(BASE)},'outputNative':{'path':str(NATIVE.relative_to(ROOT)),'sha256':sha(NATIVE)},'recipes':{str(p.relative_to(ROOT)):sha(p)for p in[Path(__file__),REGION]},'contract':contract,'beforeRestLandmarks':before,'afterRestLandmarks':after,'views':records,'baselineViewsSource':'assets/audit/whole-character-v38/cervical-laps01/attempt02/candidate-full-bird-three-quarter.png and candidate-full-bird-profile.png, identical cameras; reused no duplication','checksActuallyRun':['Source hash; simple shell manifold/positive stock at creation; head/body landmark rest drift<1e-6m; native save/reopen; matched wholeprofile/3Q images.'],'notRun':['Lapfit, sweptcollision, materialsfinish, runtime, ownerlikeness acceptance. ExplicitGLBscope/export follows finaloutline views, not fit certification.']}
(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('PROXY_READY',json.dumps(receipt['outputNative']),flush=True)
