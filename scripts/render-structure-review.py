"""Matched orthographic neutral renders; no perspective illustration is an ortho."""
from pathlib import Path
import bpy, math, sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/audit/structural-reconciliation-v1';OUT.mkdir(exist_ok=True,parents=True)
variant=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'after'
model=ROOT/('assets/models/uncaged-presence-study/murderbird-presence-study.blend' if variant=='before' else 'assets/models/uncaged-structure-v1/murderbird-structure-v1.blend')
bpy.ops.wm.open_mainfile(filepath=str(model));scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.studio_light='paint.sl'
scene.display.shading.color_type='SINGLE';scene.display.shading.single_color=(.53,.56,.58);scene.display.shading.show_shadows=False;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.5;scene.display.shading.curvature_valley_factor=1.2
scene.display.shading.background_type='WORLD';scene.world.color=(.17,.18,.20)
scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
# A neutral floor gives the foot-contact comparison a visible reference plane.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.002))
bpy.context.object.name='Review floor only - excluded from model source and export'
# Hidden inactive winding drive must not contaminate silhouette comparison.
for o in bpy.data.objects:
    p=o
    while p:
        if p.name=='winding-drive':o.hide_render=True
        p=p.parent
camdata=bpy.data.cameras.new('Review camera');cam=bpy.data.objects.new('Review camera',camdata);scene.collection.objects.link(cam);scene.camera=cam;camdata.type='ORTHO';camdata.ortho_scale=2.55
for name,pos,target,scale in [('front',(0,-6,1.04),(0,0,1.04),2.55),('side',(-6,0,1.04),(0,-.08,1.04),2.55),('three-quarter',(-4.7,-6.5,2.35),(0,-.06,1.05),2.55),('rear',(0,6,1.04),(0,0,1.04),2.55),('head',(-4,-6,2.15),(0,-.3,1.74),1.18)]:
    cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();camdata.ortho_scale=scale
    scene.render.filepath=str(OUT/f'{variant}-{name}.png');bpy.ops.render.render(write_still=True)
print('MATCHED_REVIEW_RENDERED',variant)
