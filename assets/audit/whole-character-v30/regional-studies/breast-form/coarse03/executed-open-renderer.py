from pathlib import Path
import bpy,json,hashlib,shutil
from mathutils import Vector,Matrix
OUT=Path('/tmp/v30-breast-form/coarse03');native=OUT/'murderbird-v30-breast-form.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(native)=='f90d8f9176db62e007f7a578f23f388004f6cdf4b71f49a1016ff2b5cdda9969';shutil.copyfile(Path(__file__),OUT/'executed-open-renderer.py')
def configure(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();rest={n:bpy.data.objects[n].matrix_local.copy() for n in ['left-mantle','right-mantle','left-wing-shield','right-wing-shield']}
 for o in bpy.data.objects:
  if o.animation_data:o.animation_data_clear()
  if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
  elif o.type=='CURVE':o.hide_render=True
 scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';d=bpy.data.cameras.new('V29 nested interface comparison');d.type='ORTHO';cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam;return rest,scene,d,cam

rest,scene,d,cam=configure(native);o=bpy.data.objects['breastplate'];o.matrix_local=o.matrix_local.copy()@Matrix.Rotation(1.1,4,'X');bpy.context.view_layer.update();views=[]
for label,pos,target,scale in [('front',(0,-6,1.05),(0,-.10,1.05),2.35),('side',(-6,0,1.05),(0,-.10,1.05),2.35),('reference-angle',(-6,-3.5,2.45),(0,-.10,1.05),2.35),('breast-closeup',(-3,-1,1.35),(0,-.25,1.10),1.05)]:
 d.ortho_scale=scale;cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/f'open-{label}.png');assert not Path(scene.render.filepath).exists();bpy.ops.render.render(write_still=True);views.append({'path':Path(scene.render.filepath).name,'sha256':sha(Path(scene.render.filepath))})
assert sha(native)=='f90d8f9176db62e007f7a578f23f388004f6cdf4b71f49a1016ff2b5cdda9969';(OUT/'open-render-receipt.json').write_text(json.dumps({'nativeSha256':sha(native),'rendererSha256':sha(OUT/'executed-open-renderer.py'),'breastOpeningRad':1.1,'views':views},indent=2)+'\n')
