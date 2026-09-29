import bpy, json, runpy, hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
SRC=ROOT/'assets/models/whole-character-v27/attempt-form01/murderbird-whole-character-v27.blend'
MOD=ROOT/'scripts/regions/whole-character-v28-foot-presence.py'
OUT=Path('/tmp/v28-foot-presence')
bpy.ops.wm.open_mainfile(filepath=str(SRC))
scene=bpy.context.scene; scene.frame_set(1); bpy.context.view_layer.update()
state=runpy.run_path(str(MOD))['apply']()
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.studio_light='paint.sl';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.2;scene.display.shading.curvature_valley_factor=1.1;scene.display.shading.background_type='WORLD';scene.world.color=(.11,.12,.13)
scene.render.resolution_x=scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
cd=bpy.data.cameras.new('foot presence review camera v2');cam=bpy.data.objects.new('foot presence review camera v2',cd);scene.collection.objects.link(cam);scene.camera=cam
pos=(-4,-6,.6);target=(0,-.1,.31);cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=.98;scene.render.filepath=str(OUT/'after-foot-close-02.png');bpy.ops.render.render(write_still=True)
metrics=[]
for name in state['changedObjects']:
 o=bpy.data.objects[name]
 metrics.append({'name':name,'parent':o.parent.name,'verts':len(o.data.vertices),'polygons':len(o.data.polygons),'bounds':[[min((o.matrix_world@v.co)[i] for v in o.data.vertices),max((o.matrix_world@v.co)[i] for v in o.data.vertices)] for i in range(3)]})
manifest={'attempt':'02','source':str(SRC),'sourceSha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'module':str(MOD),'moduleSha256':hashlib.sha256(MOD.read_bytes()).hexdigest(),'scope':state,'changedMeshSummary':metrics,'render':{'file':str(OUT/'after-foot-close-02.png'),'sha256':hashlib.sha256((OUT/'after-foot-close-02.png').read_bytes()).hexdigest()},'preservedAttempt01':{'manifest':str(OUT/'attempt-01-manifest.json'),'attempt01ModuleSha256':'2eb6bec61182710a5da380bb54e355b52fb82e887ebb38c1ef5ab5ee4c61e734','renders':[str(OUT/'before-whole.png'),str(OUT/'before-foot-close.png'),str(OUT/'after-whole.png'),str(OUT/'after-foot-close.png')]},'notes':['V27 native loaded in memory; no native save.','All54 rest empty matrices compare unchanged within apply().','Talons retain original mesh contour and X/Z profile; local Y length scaled to 0.80 around maximum-Y root.','No motion, strict intersection, continuous-clearance, or owner-acceptance claim.']}
(OUT/'attempt-02-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'sourceSha256':manifest['sourceSha256'],'moduleSha256':manifest['moduleSha256'],'renderSha256':manifest['render']['sha256'],'protectedPivots':state['protectedPivots']},indent=2))
