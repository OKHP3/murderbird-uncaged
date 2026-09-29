"""Matched source shoulder closeup for V36 attempt-02."""
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[6]
BASE = ROOT / "assets/models/whole-character-v35/attempt-form01/murderbird-whole-character-v35.blend"
OUT = Path(__file__).resolve().parent / "before-shoulder-closeup.png"
bpy.ops.wm.open_mainfile(filepath=str(BASE))
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
sh=scene.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='SINGLE';sh.single_color=(.56,.58,.60);sh.show_shadows=False;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';scene.world.color=(.12,.13,.14)
scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
data=bpy.data.cameras.new('V36 shoulder receiver review camera');data.type='ORTHO'
camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera);scene.camera=camera
pos=(-1.15,-.95,1.48);target=(-.30,-.04,1.19)
camera.location=pos;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=.92
scene.render.filepath=str(OUT);bpy.ops.render.render(write_still=True)
print(f"Rendered V35 source SHA-bound file {BASE} to {OUT}; same camera as V36 attempt02 shoulder-closeup.")
