from pathlib import Path
import bpy,runpy,json,hashlib,math,shutil
from mathutils import Vector
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=Path(__file__).parent
BASE=ROOT/'assets/models/whole-character-v32/attempt-form01/murderbird-whole-character-v32.blend';SRC=OUT/'executed-region.py';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(BASE)=='676c7226c57d492c6f63e1ce873c1d89e6222fdd46d4ec954aa4ec0db26bc26f';bpy.ops.wm.open_mainfile(filepath=str(BASE));bpy.context.view_layer.update();helper=runpy.run_path(str(ROOT/'scripts/build-uncaged-alignment-v7.py'));mats={m.name:helper['material_signature'](m) for m in bpy.data.materials};result=runpy.run_path(str(SRC))['apply']();snapshot=helper['scene_snapshot']();assert mats=={m.name:helper['material_signature'](m) for m in bpy.data.materials};native=OUT/'orbital-construction.blend';assert not native.exists();bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(native));assert helper['scene_snapshot']()==snapshot
receipt={'baseSHA256':sha(BASE),'sourceSHA256':sha(SRC),'nativeSHA256':sha(native),'executedStudySHA256':sha(Path(__file__)),'saveReopenExact':True,'materialDefinitionsExact':True,'result':result};(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
rest={n:bpy.data.objects[n].matrix_basis.copy() for n in ('jaw','cranial-cover')}
def pose(jaw=0,cap=0):
 for n,m in rest.items():bpy.data.objects[n].matrix_basis=m
 bpy.data.objects['jaw'].rotation_euler.x+=jaw;bpy.data.objects['cranial-cover'].location.z+=cap;bpy.context.view_layer.update()
scene=bpy.context.scene
for o in bpy.data.objects:
 if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
 elif o.type=='CURVE':o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14)
scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
d=bpy.data.cameras.new('V32 temporary matched head camera');d.type='ORTHO';cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam
views=json.loads((OUT/'executed-v31-camera-input.json').read_text())['views'];rendered=[]
for v in views:
 pose(v['jawNativeX'],v['capNativeZ']);c=v['camera'];cam.location=c['position'];cam.rotation_euler=(Vector(c['target'])-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=c['orthoScale'];scene.render.filepath=str(OUT/(v['name']+'.png'));bpy.ops.render.render(write_still=True)
 rendered.append({**v,'sha256':sha(Path(scene.render.filepath))})

receipt['views']=rendered;(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');assert sha(native)==receipt['nativeSHA256'];print('COMPLETE',flush=True)
