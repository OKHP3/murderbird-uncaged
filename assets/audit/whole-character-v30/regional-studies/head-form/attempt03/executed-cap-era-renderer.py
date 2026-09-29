from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
OUT=Path('/tmp/v30-head-form/attempt03');native=OUT/'head-form.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(native));bound=sha(native);r={'nativeSHA256':bound,'executedRendererSHA256':sha(Path(__file__)),'views':[]}
scene=bpy.context.scene
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
 if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
 elif o.type=='CURVE':o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';d=bpy.data.cameras.new('V30 temporary head study');d.type='ORTHO';cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam

for label,era,cap in [('cap-open','builder',.08),('maker-head','maker',0),('mechanic-head','mechanic',0)]:
 for o in bpy.data.objects:
  if o.type=='MESH':o.hide_render=era not in o.get('exteriorEras','maker,mechanic,builder').split(',')
 bpy.data.objects['cranial-cover'].location.z+=cap;bpy.context.view_layer.update();pos=(-6,-2.4,2.15);target=(0,-.50,1.77);cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=.95;scene.render.filepath=str(OUT/(label+'.png'));bpy.ops.render.render(write_still=True)
 r['views'].append({'name':label,'era':era,'capNativeZDelta':cap,'imageSHA256':sha(Path(scene.render.filepath)),'AdvancedLensExcluded':all(bpy.data.objects[f'Seated Advanced optic {s}'].hide_render for s in (-1,1)) if era!='builder' else False});bpy.data.objects['cranial-cover'].location.z-=cap
assert sha(native)==bound
(OUT/'cap-era-render-receipt.json').write_text(json.dumps(r,indent=2)+'\n')
