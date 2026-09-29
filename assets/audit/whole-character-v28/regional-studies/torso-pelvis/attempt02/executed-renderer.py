from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector,Quaternion
OUT=Path('/tmp/v28-torso-pelvis/attempt02');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();native=OUT/'torso-pelvis.blend';r=json.loads((OUT/'receipt.json').read_text());assert sha(native)==r['nativeSHA256'];bpy.ops.wm.open_mainfile(filepath=str(native));bpy.context.view_layer.update();r['rendererSHA256']=sha(Path(__file__));r['views']=[]
scene=bpy.context.scene
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
 if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
 elif o.type=='CURVE':o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';d=bpy.data.cameras.new('V28 temporary torso study');d.type='ORTHO';cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam
rest={o.name:(o.location.copy(),o.rotation_mode,o.rotation_quaternion.copy(),o.rotation_euler.copy(),o.matrix_world.copy()) for o in bpy.data.objects if o.type=='EMPTY'}
poses=json.loads(Path('/tmp/v28-torso-pelvis/leg-studies.json').read_text())['states']
def reset():
 for n,(p,m,q,e,w) in rest.items():
  o=bpy.data.objects[n];o.location=p;o.rotation_mode=m;o.rotation_quaternion=q;o.rotation_euler=e
 bpy.context.view_layer.update()
def pose(label):
 reset()
 if label=='breast-open':bpy.data.objects['breastplate'].rotation_euler.x=1.1
 elif label in poses:
  state=poses[label];dz=state['bodyDeltaNative'][2];bpy.data.objects['body'].location.z+=dz
  for side,lp in state['legs'].items():
   hip=bpy.data.objects[side+'-thigh'];knee=bpy.data.objects[side+'-shin'];hip.location.z+=dz
   for o,key in [(hip,'hipQuaternionNative'),(knee,'kneeQuaternionNative')]:
    x,y,z,w=lp[key];o.rotation_mode='QUATERNION';o.rotation_quaternion=Quaternion((w,x,y,z))
  bpy.context.view_layer.update()
  for side in state['legs']:
   f=bpy.data.objects[side+'-foot'];f.rotation_mode='QUATERNION';f.rotation_quaternion=f.parent.matrix_world.to_quaternion().inverted()@rest[f.name][4].to_quaternion()
 bpy.context.view_layer.update()
views=[('whole',(-6,-3.5,2.75)),('front',(0,-6,1.8)),('left-side',(6,0,1.8)),('right-side',(-6,0,1.8)),('rear',(0,6,1.8)),('breast-open',(-6,-3.5,2.75)),('step',(-6,-3.5,2.75)),('crouch',(-6,-3.5,2.75))]
for label,pos in views:
 pose(label);target=(0,-.08,1.02);cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=2.5;scene.render.filepath=str(OUT/(label+'.png'));bpy.ops.render.render(write_still=True);r['views'].append({'name':label,'path':scene.render.filepath,'sha256':sha(Path(scene.render.filepath)),'camera':{'position':pos,'target':target,'orthoScale':2.5},'studyPose':label if label in poses else None});(OUT/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
assert sha(native)==r['nativeSHA256'];print('Rendered eight unchanged-native coarse studies.')
