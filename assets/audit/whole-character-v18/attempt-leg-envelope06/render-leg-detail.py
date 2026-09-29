from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'assets/models/whole-character-v17/attempt-02/murderbird-whole-character-v17.blend'
FINAL = ROOT / 'assets/models/whole-character-v18/attempt-leg-envelope06/murderbird-whole-character-v18.blend'
OUT = Path(__file__).resolve().parent


def setup(scene):
    scene.render.engine = 'BLENDER_WORKBENCH'
    shade = scene.display.shading
    shade.light = 'STUDIO'; shade.studio_light = 'paint.sl'
    shade.color_type = 'SINGLE'; shade.single_color = (.52, .55, .57)
    shade.show_shadows = True; shade.show_cavity = True; shade.cavity_type = 'BOTH'
    shade.curvature_ridge_factor = 1.2; shade.curvature_valley_factor = 1.1
    shade.background_type = 'WORLD'; scene.world.color = (.12, .13, .14)
    scene.render.resolution_x = scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'; scene.render.image_settings.color_mode = 'RGB'
    scene.render.film_transparent = False
    data = bpy.data.cameras.new('V18 matched leg-detail camera')
    data.type = 'ORTHO'; data.ortho_scale = .92; data.lens = 70
    data.clip_start = .01; data.clip_end = 100
    camera = bpy.data.objects.new('V18 matched leg-detail camera', data)
    scene.collection.objects.link(camera)
    target = Vector((0.0, -.055, .415)); position = target + Vector((-.88, -1.35, .53))
    camera.location = position
    camera.rotation_euler = (target - position).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = camera; bpy.context.view_layer.update()


for source, output in ((BASE, OUT / 'before-leg-detail.png'), (FINAL, OUT / 'after-leg-detail.png')):
    bpy.ops.wm.open_mainfile(filepath=str(source)); scene = bpy.context.scene
    scene.frame_set(1)
    for obj in bpy.data.objects:
        if obj.type == 'MESH': obj.hide_render = False; obj.hide_set(False)
    setup(scene); scene.render.filepath = str(output)
    bpy.ops.render.render(write_still=True)
