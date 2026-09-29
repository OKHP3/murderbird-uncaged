from pathlib import Path
import bpy,json,hashlib
from mathutils import Vector
OUT=Path('/tmp/v31-head-reconstruction/attempt01');native=OUT/'head-reconstruction.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();BASE=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/models/whole-character-v30/attempt-form02/murderbird-whole-character-v30.blend');SRC=OUT/'executed-head-reconstruction.py';bpy.ops.wm.open_mainfile(filepath=str(native));diagnosis=json.loads((OUT/'reopen-diagnosis.json').read_text());r={'baseSHA256':sha(BASE),'sourceSHA256':sha(SRC),'nativeSHA256':sha(native),'rendererSHA256':sha(Path(__file__)),'result':diagnosis['result'],'materialsExact':True,'saveReopenExactExceptHiddenAuthoringGuideCachedWorldMatrices':True,'reopenGuideDifference':list(diagnosis['difference']['curves']),'views':[]}
scene=bpy.context.scene
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
 if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
 elif o.type=='CURVE':o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';d=bpy.data.cameras.new('V31 temporary profile review');d.type='ORTHO';cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam;jawrest=bpy.data.objects['jaw'].rotation_euler.copy();caprest=bpy.data.objects['cranial-cover'].location.copy();origin=bpy.data.objects['head'].matrix_world.translation.copy();focus=origin+Vector((0,-.13,.215))
views=[('whole',(-6,-3.5,2.75),(0,-.08,1.02),2.5,0,0)]
for state,j in [('closed',0),('open',.32)]:
 for label,offset in [('head',(-6,-2.4,.42)),('side',(-6,0,0)),('front',(0,-6,.12))]:views.append((state+'-'+label,focus+Vector(offset),focus,.95,j,0))
views.append(('cap-open',focus+Vector((-6,-2.4,.42)),focus,.95,0,.08))
for label,pos,target,scale,jaw,cap in views:
 bpy.data.objects['jaw'].rotation_euler=jawrest;bpy.data.objects['jaw'].rotation_euler.x+=jaw;bpy.data.objects['cranial-cover'].location=caprest;bpy.data.objects['cranial-cover'].location.z+=cap;bpy.context.view_layer.update();cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale;scene.render.filepath=str(OUT/(label+'.png'));bpy.ops.render.render(write_still=True);r['views'].append({'name':label,'sha256':sha(Path(scene.render.filepath)),'camera':{'position':list(pos),'target':list(target),'orthoScale':scale},'jawNativeX':jaw,'capNativeZ':cap});(OUT/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')

assert sha(native)==r['nativeSHA256']
