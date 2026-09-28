"""Neutral authoring comparison views; metadata distinguishes perspective/ortho."""
from pathlib import Path
import bpy,math,json,sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/audit/neutral-v2';OUT=OUT/'baseline' if '--baseline' in sys.argv else OUT;OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/('assets/models/uncaged-exterior-v1/murderbird-exterior-v1.blend' if '--baseline' in sys.argv else 'assets/models/uncaged-neutral-v2/murderbird-neutral-v2.blend')))
scene=bpy.context.scene;scene.frame_set(1)
scene.render.engine='BLENDER_WORKBENCH';sh=scene.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='MATERIAL';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.curvature_ridge_factor=1.2;sh.curvature_valley_factor=1.1;sh.background_type='WORLD';scene.world.color=(.11,.12,.13)
scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
camdata=bpy.data.cameras.new('Neutral review camera');cam=bpy.data.objects.new('Neutral review camera',camdata);scene.collection.objects.link(cam);scene.camera=cam
records=[]
def render(name,pos,target,scale=2.4,perspective=False):
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='PERSP' if perspective else 'ORTHO';camdata.ortho_scale=scale;camdata.lens=70
 scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True);records.append({'image':name+'.png','camera':list(pos),'target':list(target),'projection':camdata.type,'orthoScale':scale,'lens':70,'lighting':'neutral workbench studio, no textures','scope':'authored reconstruction, not source metrology'})
def era(e):
 for o in scene.objects:
  if o.type=='MESH':o.hide_render=e not in o.get('exteriorEras','maker,mechanic,builder').split(',');o.hide_set(False)
era('builder')
quick='--quick' in sys.argv
views=[('three-quarter',(-4.7,-6.5,2.30),(0,-.1,1.08),2.4),('side-right',(-6,0,1.08),(0,-.1,1.08),2.4),('head',(-4,-6,2.01),(0,-.29,1.88),.83)]
if not quick:views += [('front',(0,-6,1.08),(0,-.10,1.08),2.4),('rear',(0,6,1.08),(0,.05,1.08),2.4),('side-left',(6,0,1.08),(0,-.1,1.08),2.4),('left-three-quarter',(4.7,-6.5,2.3),(0,-.10,1.08),2.4),('elevated',(-4,-6,5.5),(0,-.1,1.08),2.4),('low',(-4,-6,.2),(0,-.1,1.08),2.4),('feet',(-4,-6,.6),(0,-.10,.31),.98),('mantle',(4,0,1.4),(.32,.08,1.26),.85),('breast',(-2,-6,1.50),(0,-.14,1.32),1.15)]
for name,pos,target,scale in views:render('neutral-'+name,pos,target,scale)
if not quick:
 for e in ['maker','mechanic','builder']:
  era(e)
  pos=(3.15,-4.5,1.90) if e!='builder' else (-3.15,-4.5,1.90)
  render(e+'-reference-perspective',pos,(0,-.10,1.07),2.4,True)
  render(e+'-front',(0,-6,1.08),(0,-.1,1.08))
  render(e+'-rear',(0,6,1.08),(0,-.1,1.08))
  for side in [-1,1]:render(e+('-right' if side<0 else '-left'),(side*6,0,1.08),(0,-.1,1.08))
(OUT/'authoring-views.json').write_text(json.dumps(records,indent=2)+'\n')
