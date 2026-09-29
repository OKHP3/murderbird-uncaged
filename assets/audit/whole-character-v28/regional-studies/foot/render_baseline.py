import bpy
from pathlib import Path
from mathutils import Vector
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
SRC=ROOT/'assets/models/whole-character-v27/attempt-form01/murderbird-whole-character-v27.blend'
OUT=Path('/tmp/v28-foot-presence')
bpy.ops.wm.open_mainfile(filepath=str(SRC))
scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update()
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.studio_light='paint.sl';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.2;scene.display.shading.curvature_valley_factor=1.1;scene.display.shading.background_type='WORLD';scene.world.color=(.11,.12,.13)
scene.render.resolution_x=scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
cd=bpy.data.cameras.new('foot presence review camera');cam=bpy.data.objects.new('foot presence review camera',cd);scene.collection.objects.link(cam);scene.camera=cam
for name,pos,target,scale in [('whole',(-4.7,-6.5,2.30),(0,-.1,1.08),2.4),('foot-close',(-4,-6,.6),(0,-.1,.31),.98)]:
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=scale;scene.render.filepath=str(OUT/f'before-{name}.png');bpy.ops.render.render(write_still=True)
