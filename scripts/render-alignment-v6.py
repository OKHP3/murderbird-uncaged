"""Neutral authoring comparison views; metadata distinguishes perspective/ortho."""
from pathlib import Path
import bpy,math,json,sys,hashlib,shutil
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/audit/alignment-v6';OUT=OUT/'baseline' if '--baseline' in sys.argv else OUT;OUT.mkdir(parents=True,exist_ok=True)
source_path=ROOT/('assets/models/uncaged-alignment-v3/murderbird-alignment-v3.blend' if '--baseline' in sys.argv else 'assets/models/uncaged-alignment-v6/murderbird-alignment-v6.blend')
if '--v5-comparison' in sys.argv:
 OUT=ROOT/'assets/audit/alignment-v6/v5-comparison';OUT.mkdir(parents=True,exist_ok=True)
 source_path=ROOT/'assets/models/uncaged-alignment-v5/murderbird-alignment-v5.blend'
model_path=source_path.with_suffix('.glb')
bpy.ops.wm.open_mainfile(filepath=str(source_path))
scene=bpy.context.scene;scene.frame_set(1)
scene.render.engine='BLENDER_WORKBENCH';sh=scene.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='MATERIAL';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.curvature_ridge_factor=1.2;sh.curvature_valley_factor=1.1;sh.background_type='WORLD';scene.world.color=(.11,.12,.13)
scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
camdata=bpy.data.cameras.new('Neutral review camera');cam=bpy.data.objects.new('Neutral review camera',camdata);scene.collection.objects.link(cam);scene.camera=cam
model_sha=hashlib.sha256(model_path.read_bytes()).hexdigest()
source_sha=hashlib.sha256(source_path.read_bytes()).hexdigest()
records=[]
def render(name,pos,target,scale=2.4,perspective=False):
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='PERSP' if perspective else 'ORTHO';camdata.ortho_scale=scale;camdata.lens=70
 scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True);records.append({'image':name+'.png','sha256':hashlib.sha256((OUT/(name+'.png')).read_bytes()).hexdigest(),'bytes':(OUT/(name+'.png')).stat().st_size,'modelSha256':model_sha,'sourceSha256':source_sha,'generatorSources':json.loads((source_path.parent/'alignment-inventory.json').read_text())['generatedFiles'],'camera':list(pos),'target':list(target),'projection':camdata.type,'orthoScale':scale,'lens':70,'lighting':'neutral workbench studio, no textures','scope':'authored reconstruction, not source metrology'})
def era(e):
 for o in scene.objects:
  if o.type=='MESH':o.hide_render=e not in o.get('exteriorEras','maker,mechanic,builder').split(',');o.hide_set(False)
era('builder')
quick='--quick' in sys.argv
views=[('three-quarter',(-4.7,-6.5,2.30),(0,-.1,1.08),2.4),('side-right',(-6,0,1.08),(0,-.1,1.08),2.4),('head',(-4,-6,2.01),(0,-.29,1.88),.83)]
views += [('head-profile-right',(-6,-.29,1.80),(0,-.29,1.80),.80),('head-profile-left',(6,-.29,1.80),(0,-.29,1.80),.80)]
if quick:views += [('front',(0,-6,1.08),(0,-.10,1.08),2.4),('rear',(0,6,1.08),(0,.05,1.08),2.4)]
if not quick:views += [('front',(0,-6,1.08),(0,-.10,1.08),2.4),('rear',(0,6,1.08),(0,.05,1.08),2.4),('side-left',(6,0,1.08),(0,-.1,1.08),2.4),('left-three-quarter',(4.7,-6.5,2.3),(0,-.10,1.08),2.4),('elevated',(-4,-6,5.5),(0,-.1,1.08),2.4),('low',(-4,-6,.2),(0,-.1,1.08),2.4),('feet',(-4,-6,.6),(0,-.10,.31),.98),('mantle',(4,0,1.4),(.32,.08,1.26),.85),('breast',(-2,-6,1.50),(0,-.14,1.32),1.15)]
for name,pos,target,scale in views:render('alignment-'+name,pos,target,scale)
if not quick:
 for e in ['maker','mechanic','builder']:
  era(e)
  pos=(3.15,-4.5,1.90) if e!='builder' else (-3.15,-4.5,1.90)
  render(e+'-reference-perspective',pos,(0,-.10,1.07),2.4,True)
  render(e+'-front',(0,-6,1.08),(0,-.1,1.08))
  render(e+'-rear',(0,6,1.08),(0,-.1,1.08))
  for side in [-1,1]:render(e+('-right' if side<0 else '-left'),(side*6,0,1.08),(0,-.1,1.08))
(OUT/'authoring-views.json').write_text(json.dumps(records,indent=2)+'\n')

if not quick and '--baseline' not in sys.argv and '--v5-comparison' not in sys.argv:
 modeldir=ROOT/'assets/models/uncaged-alignment-v6';inventory_path=modeldir/'alignment-inventory.json';inventory=json.loads(inventory_path.read_text())
 for row in inventory['generatedFiles']:
  if row['path'].endswith('-preview.png'):
   dest=ROOT/row['path'];assert not dest.exists() or hashlib.sha256(dest.read_bytes()).hexdigest()==row['sha256'],'Preserve manually changed preview before regeneration: '+str(dest)
 inventory['generatedFiles']=[row for row in inventory['generatedFiles'] if not row['path'].endswith('-preview.png')]
 for name in ['maker','mechanic','builder']:
  dest=modeldir/(name+'-preview.png');shutil.copy2(OUT/(name+'-reference-perspective.png'),dest)
  inventory['generatedFiles'].append({'path':str(dest.relative_to(ROOT)),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
 inventory_path.write_text(json.dumps(inventory,indent=2)+'\n')
