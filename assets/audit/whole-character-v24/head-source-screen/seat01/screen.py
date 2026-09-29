from pathlib import Path
import bpy,bmesh,json,hashlib,math,runpy,shutil
from mathutils import Vector
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=Path('/tmp/v24-head-study/seat01')
base=ROOT/'assets/models/whole-character-v24/attempt-form01/murderbird-whole-character-v24.blend';source=ROOT/'scripts/regions/whole-character-v24-receiver-seat.py'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(base)=='5a4217ae9865abee8b270901f98bebc84f3b59409fae8abf2b01950dca6fc7aa'
bpy.ops.wm.open_mainfile(filepath=str(base));bpy.context.view_layer.update()
r=json.loads((ROOT/'assets/audit/whole-character-v24/attempt-form01/receipt.json').read_text());main=r['regions'][0]['result'];names=main['changed']+main['added'];assert len(names)==57
h=runpy.run_path(str(ROOT/'assets/audit/whole-character-v24/attempt-form01/executed-snapshot-helper.py'));before=h['scene_snapshot']();mats={m.name:h['material_signature'](m) for m in bpy.data.materials}
lib=runpy.run_path(str(source));targets=lib['TARGETS'];shutil.copyfile(source,OUT/'executed-receiver-seat.py')
def check():
 dg=bpy.context.evaluated_depsgraph_get();results=[]
 for n in names:
  o=bpy.data.objects[n];ev=o.evaluated_get(dg);m=ev.to_mesh();v=[ev.matrix_world@p.co for p in m.vertices];assert all(math.isfinite(c) for p in v for c in p)
  result={'name':n,'parent':o.parent.name,'evaluatedWorldBounds':lib['bounds'](v),'vertices':len(v)}
  if n in targets:
   bm=bmesh.new();bm.from_mesh(m);result.update(closed=all(e.is_manifold for e in bm.edges),volume=bm.calc_volume(signed=True));bm.free();assert result['closed'] and result['volume']>0
   cp=m.copy();result['validateRepair']=cp.validate();bpy.data.meshes.remove(cp);assert not result['validateRepair']
  ev.to_mesh_clear();results.append(result)
 return results
bounds_before=check();(OUT/'before-evaluated-bounds.json').write_text(json.dumps(bounds_before,indent=2)+'\n')
receipt=lib['apply']();bounds_after=check();after=h['scene_snapshot']()
assert before['empties']==after['empties'] and len(before['empties'])==54
assert mats=={m.name:h['material_signature'](m) for m in bpy.data.materials}
assert {n:r for n,r in before['meshes'].items() if n not in targets}=={n:r for n,r in after['meshes'].items() if n not in targets}
ordinary=[r['evaluatedWorldBounds'] for r in bounds_after if r['name'] not in targets];region=[[min(r[0][k] for r in ordinary)-.020 for k in range(3)],[max(r[1][k] for r in ordinary)+.020 for k in range(3)]]
inside=[r['name'] for r in bounds_after if all(r['evaluatedWorldBounds'][0][k]>=region[0][k] and r['evaluatedWorldBounds'][1][k]<=region[1][k] for k in range(3))];assert len(inside)==57
bpy.context.preferences.filepaths.save_version=0;native=OUT/'head-seated.blend';assert not native.exists();bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
result={'baseSHA256':sha(base),'sourceSHA256':sha(source),'screenSHA256':sha(Path(__file__)),'nativeSHA256':sha(native),'receipt':receipt,'evaluatedBefore':bounds_before,'evaluatedAfter':bounds_after,'headRegionBounds':region,'boundsRegionMethod':'55 protected changed head forms evaluated bounds union plus20mm margin; two receiver bounds checked against that independent region','all57WithinRegion':len(inside),'nodesExact':54,'otherMeshesExact':len(before['meshes'])-2,'materialsExact':True,'saveReopenExact':True}
(OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
scene=bpy.context.scene
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
 if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
 elif o.type=='CURVE':o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';sh=scene.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='SINGLE';sh.single_color=(.56,.58,.60);sh.show_shadows=False;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
data=bpy.data.cameras.new('V24 temporary seat review camera');data.type='ORTHO';data.ortho_scale=2.5;cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);scene.camera=cam;cam.location=(-6,-3.5,2.75);cam.rotation_euler=(Vector((0,-.08,1.02))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/'after-reference-angle.png');bpy.ops.render.render(write_still=True)
result['render']={'sha256':sha(Path(scene.render.filepath)),'camera':{'location':[-6,-3.5,2.75],'target':[0,-.08,1.02],'orthoScale':2.5}};(OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n');assert sha(base)==result['baseSHA256'];print(json.dumps({k:result[k] for k in ('sourceSHA256','nativeSHA256','all57WithinRegion','nodesExact','otherMeshesExact','saveReopenExact')}))
