"""Write-once V23 composed construction study and neutral review views."""
from pathlib import Path
import argparse, hashlib, json, math, runpy, shutil, sys
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'assets/models/whole-character-v22/attempt-frame04/murderbird-whole-character-v22.blend'
BASE_SHA='b3ac4677d2e76a0e08544323306c07f2ed7e61cd381d274a944d8e5b87031d1f'
p=argparse.ArgumentParser();p.add_argument('--attempt',required=True);p.add_argument('--head-sha',required=True);p.add_argument('--body-sha',required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);assert a.attempt.replace('-','').isalnum()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def art(p):return {'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
AUDIT=ROOT/f'assets/audit/whole-character-v23/attempt-{a.attempt}';OUT=ROOT/f'assets/models/whole-character-v23/attempt-{a.attempt}'
headsrc=ROOT/'scripts/regions/whole-character-v23-head.py';bodysrc=ROOT/'scripts/regions/whole-character-v23-body.py'
assert sha(BASE)==BASE_SHA and sha(headsrc)==a.head_sha and sha(bodysrc)==a.body_sha
assert not AUDIT.exists() and not OUT.exists();AUDIT.mkdir(parents=True);OUT.mkdir(parents=True)
for src,name in [(Path(__file__),'executed-builder.py'),(headsrc,'executed-head.py'),(bodysrc,'executed-body.py'),(ROOT/'scripts/regions/whole-character-v21-envelope.py','executed-envelope-helper.py')]:shutil.copyfile(src,AUDIT/name)
h=runpy.run_path(str(ROOT/'scripts/build-uncaged-alignment-v7.py'))
bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']();mats={m.name:h['material_signature'](m) for m in bpy.data.materials}
head=runpy.run_path(str(AUDIT/'executed-head.py'))['apply']()
module=runpy.run_path(str(AUDIT/'executed-body.py'));module['apply'].__globals__['ROOT']=ROOT
body=module['apply']();bpy.context.view_layer.update();after=h['scene_snapshot']()
assert mats=={m.name:h['material_signature'](m) for m in bpy.data.materials}
protected=set()
for n,v in before['meshes'].items():
    if v['parent'] in ('left-thigh','right-thigh','left-shin','right-shin','left-foot','right-foot') or 'toe' in v['parent']:
        assert after['meshes'].get(n)==v,n;protected.add(n)
finite=[];deps=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    if o.type=='MESH':
        e=o.evaluated_get(deps);m=e.to_mesh();assert all(math.isfinite(c) for v in m.vertices for c in v.co),o.name
        finite.append(o.name);e.to_mesh_clear()
native=OUT/'murderbird-whole-character-v23.blend';bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
receipt={'status':'coordinated silhouette and structural proposal; no artistic or full-motion acceptance',
 'base':art(BASE),'native':art(native),'sources':[art(AUDIT/n) for n in ('executed-builder.py','executed-head.py','executed-body.py','executed-envelope-helper.py')],
 'head':head,'body':body,'checks':{'finiteMeshes':len(finite),'protectedLegFootMeshesExact':len(protected),'materialsExact':True,'saveReopenExact':True},
 'limits':['No runtime hardware socket rederivation or era filtering validation.','New neck links and guard laps need full movement review.','Neutral surfaces show construction only; no finish approval.'],'views':[]}
(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
scene=bpy.context.scene
for o in bpy.data.objects:
    if o.animation_data:o.animation_data_clear()
    if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
    elif o.type=='CURVE':o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';sh=scene.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='SINGLE';sh.single_color=(.56,.58,.60);sh.show_shadows=False;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';scene.world.color=(.12,.13,.14)
scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
data=bpy.data.cameras.new('V23 temporary neutral review camera');data.type='ORTHO';camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera);scene.camera=camera
views=[('reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5),('front',(0,-7,1.65),(0,-.08,1.02),2.5),('side',(-7,0,1.35),(0,-.08,1.02),2.5),('rear',(0,7,1.65),(0,-.08,1.02),2.5),('neck',(-6,-3.5,2.45),(0,-.27,1.48),1.3)]
for name,pos,target,scale in views:
    camera.location=pos;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=scale
    scene.render.filepath=str(AUDIT/f'after-{name}.png');bpy.ops.render.render(write_still=True)
    receipt['views'].append({**art(Path(scene.render.filepath)),'camera':{'position':pos,'target':target,'orthoScale':scale},'lighting':'neutral Workbench no cast shadows'})
    (AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
assert sha(BASE)==BASE_SHA and sha(native)==receipt['native']['sha256']
print(json.dumps({'native':receipt['native'],'checks':receipt['checks'],'views':len(receipt['views'])}))
