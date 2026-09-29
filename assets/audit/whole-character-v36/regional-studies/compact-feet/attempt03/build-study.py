from pathlib import Path
import bpy,hashlib,json,runpy,shutil
from mathutils import Vector
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
BASE=ROOT/'assets/models/whole-character-v35/attempt-form01/murderbird-whole-character-v35.blend'
BASE_SHA='d2c704ccf89f3f0e7dbeb3613dcdbdd964c4ba69991783783830803eecf59cb0'
MODULE=ROOT/'scripts/regions/whole-character-v36-compact-feet-fit.py'
OUT=ROOT/'assets/models/whole-character-v36/regional-studies/compact-feet/attempt03/murderbird-whole-character-v36-compact-feet-fit.blend'
AUDIT=ROOT/'assets/audit/whole-character-v36/regional-studies/compact-feet/attempt03'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(BASE)==BASE_SHA and not OUT.exists()
shutil.copyfile(MODULE,AUDIT/'executed-whole-character-v36-compact-feet-fit.py')
# Freeze whole-object signatures for undeclared mesh owners; materials and mesh bytes are checked separately below.
def sig(o):return (tuple(tuple(round(float(c),10) for c in v.co) for v in o.data.vertices),tuple(tuple(int(i) for i in p.vertices) for p in o.data.polygons),tuple(m.name if m else None for m in o.data.materials),tuple(round(float(o.matrix_world[r][c]),10) for r in range(4) for c in range(4)))
protected={o.name:sig(o) for o in bpy.data.objects if o.type=='MESH' and (not o.parent or o.parent.name not in {'left-foot','right-foot','left-toes','right-toes',*(f'{s}-digit-{d}-{p}' for s in ('left','right') for d in (1,2,3) for p in ('proximal','distal'))})}
beartags={o.name:(tuple(tuple(round(float(c),10) for c in v.co) for v in o.data.vertices),tuple(tuple(int(i) for i in p.vertices) for p in o.data.polygons),tuple(m.name if m else None for m in o.data.materials)) for o in bpy.data.objects if o.type=='MESH' and o.get('surfaceRole')=='bearing' and o.parent and (o.parent.name.endswith('-digit-1-proximal') or '-digit-' in o.parent.name)}
module=runpy.run_path(str(MODULE));result=module['apply']()
assert all(sig(bpy.data.objects[n])==v for n,v in protected.items())
assert all((tuple(tuple(round(float(c),10) for c in v.co) for v in bpy.data.objects[n].data.vertices),tuple(tuple(int(i) for i in p.vertices) for p in bpy.data.objects[n].data.polygons),tuple(m.name if m else None for m in bpy.data.objects[n].data.materials))==v for n,v in beartags.items())
scene=bpy.context.scene;scene.frame_set(1)
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
 if o.get('authoringGuide'):o.hide_render=True
 elif o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
scene.render.engine='BLENDER_WORKBENCH';shade=scene.display.shading;shade.light='STUDIO';shade.studio_light='paint.sl';shade.color_type='SINGLE';shade.single_color=(.56,.58,.60);shade.show_shadows=False;shade.show_cavity=True;shade.cavity_type='BOTH';shade.background_type='WORLD';scene.world.color=(.12,.13,.14)
scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
data=bpy.data.cameras.new('V36 attempt03 matched neutral review camera');data.type='ORTHO';cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);scene.camera=cam
views=[('reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5),('front',(0,-7,1.65),(0,-.08,1.02),2.5),('feet-close-reference',(-1.35,-2.6,.85),(0,-.24,.15),1.05)]
receipts=[]
for name,pos,target,scale in views:
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=scale;scene.render.filepath=str(AUDIT/f'after-{name}.png');bpy.ops.render.render(write_still=True);p=Path(scene.render.filepath);receipts.append({'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size,'camera':{'position':pos,'target':target,'orthoScale':scale}})
bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(data);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(OUT),check_existing=False)
receipt={'status':'single-pass regional fit candidate; dynamic contacts remain unverified until strict screen','base':{'path':str(BASE.relative_to(ROOT)),'sha256':sha(BASE)},'module':{'path':str(MODULE.relative_to(ROOT)),'sha256':sha(MODULE)},'executedModule':{'path':str((AUDIT/'executed-whole-character-v36-compact-feet-fit.py').relative_to(ROOT)),'sha256':sha(AUDIT/'executed-whole-character-v36-compact-feet-fit.py')},'native':{'path':str(OUT.relative_to(ROOT)),'sha256':sha(OUT),'bytes':OUT.stat().st_size},'changedNodes':result['changedNodes'],'changedFootMeshes':result['changedFootMeshes'],'numericInvariants':result['numericInvariants'],'protectedUnrelatedMeshesExact':len(protected),'bearingLocalGeometryExact':len(beartags),'views':receipts,'rationale':result['rationale'],'limits':result['scopeLimitations']+['Only three neutral comparison views; owner likeness and swept motion are not established.']}
(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'native':receipt['native'],'changedNodes':receipt['changedNodes'],'changedFootMeshes':len(result['changedFootMeshes']),'protectedUnrelatedMeshesExact':len(protected),'bearingLocalGeometryExact':len(beartags),'views':receipts}))
