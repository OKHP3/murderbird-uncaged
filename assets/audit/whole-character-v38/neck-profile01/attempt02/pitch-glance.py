import bpy,json
from pathlib import Path
from mathutils import Matrix,Vector
A=Path(__file__).resolve().parent;R=A.parents[4];N=R/'assets/models/whole-character-v38/neck-profile01/attempt02/murderbird-v38-neck-profile01-attempt02.blend'
bpy.ops.wm.open_mainfile(filepath=str(N))
for name in['neck','cervical-mid-a','cervical-mid-b','cervical-upper']:
 o=bpy.data.objects[name];o.matrix_basis=o.matrix_basis@Matrix.Rotation(.10675220489501955,4,'X')
o=bpy.data.objects['head'];o.matrix_basis=o.matrix_basis@Matrix.Rotation(-.5090505059024657,4,'X');bpy.context.view_layer.update()
for o in bpy.data.objects:
 if o.type=='MESH':o.hide_render=o.get('silhouetteStudyHistoricalHidden')is True or o.get('authoringGuide')is True or' builder'==str(o.get('exteriorEras','')) or 'builder'not in str(o.get('exteriorEras','maker,mechanic,builder')).split(',')
 elif o.type=='CURVE':o.hide_render=True
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';d=s.display.shading;d.light='STUDIO';d.studio_light='paint.sl';d.color_type='SINGLE';d.single_color=(.56,.58,.60);d.show_shadows=False;d.show_cavity=True;d.cavity_type='BOTH';d.background_type='WORLD';s.world.color=(.12,.13,.14);s.render.resolution_x=s.render.resolution_y=1200;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
c=bpy.data.cameras.new('temporary priorangle diagnostic');c.type='ORTHO';c.ortho_scale=.80;o=bpy.data.objects.new(c.name,c);s.collection.objects.link(o);s.camera=o;o.location=(-6,0,1.95);o.rotation_euler=(Vector((0,-.35,1.41))-o.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(A/'candidate-prior-angle-neck-profile.png');bpy.ops.render.render(write_still=True)
(A/'pitch-glance.json').write_text(json.dumps({'neckPitchEach':.10675220489501955,'headPitch':-.5090505059024657,'status':'PreviouscontactANGLE body-rest diagnostic applied to NEW redistributed layout; not actual currentstrike/contact, no finite clearance acceptance. Four rigid proxy seams intentionally lack solved slidinglaps. Native/GLB notrewritten.'},indent=2)+'\n')
