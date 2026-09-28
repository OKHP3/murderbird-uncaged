"""Compose independent regional patches into a versioned editable proposal."""
from pathlib import Path
import argparse,sys,hashlib,json,runpy,shutil
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--attempt',required=True);ap.add_argument('--regions',default='head,breast,legs')
args=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
BASE=ROOT/'assets/models/uncaged-orbital-crown-v14/attempt-11/murderbird-orbital-crown-v14.blend'
EXPECTED='93cf7908906dab0746ec42ace88867b3c52cb0988c284cf6ae468eb2cce17a5a'
OUT=ROOT/f'assets/models/whole-character-v15/attempt-{args.attempt}'
AUDIT=ROOT/f'assets/audit/whole-character-v15/attempt-{args.attempt}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def art(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}
assert sha(BASE)==EXPECTED and not OUT.exists() and not AUDIT.exists()
OUT.mkdir(parents=True);AUDIT.mkdir(parents=True)
shutil.copy2(__file__,AUDIT/'executed-composition.py')
h=runpy.run_path(str(ROOT/'scripts/build-uncaged-alignment-v7.py'),run_name='v15_snapshot_helpers')
bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']();patches=[]
for region in args.regions.split(','):
    assert region in ('head','breast','legs')
    script=ROOT/f'scripts/regions/whole-character-v15-{region}.py'
    dest=AUDIT/f'executed-{region}.py';shutil.copy2(script,dest)
    result=runpy.run_path(str(script),run_name=f'v15_{region}_patch')['apply']()
    patches.append({'script':art(dest),'result':result})
after=h['scene_snapshot']()
assert before['empties']==after['empties'],'Regional patches moved or changed pivots'
assert before['curves']==after['curves'],'Regional patch changed historical curves'
changed=[n for n in before['meshes'] if n not in after['meshes'] or before['meshes'][n]!=after['meshes'][n]]
new=[n for n in after['meshes'] if n not in before['meshes']]
removed=[n for n in before['meshes'] if n not in after['meshes']]
native=OUT/'murderbird-whole-character-v15.blend'
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False)
bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
receipt={'status':'regional construction proposal; visual review pending; not accepted or selected',
 'base':art(BASE),'native':art(native),'composer':art(AUDIT/'executed-composition.py'),'patches':patches,
 'preservation':{'pivotsExact':len(after['empties']),'curvesExact':len(after['curves']),'otherMeshesExact':len(before['meshes'])-len(changed),'saveReopenExact':True},
 'changedMeshes':changed,'newMeshes':new,'removedMeshes':removed,
 'referenceScope':'July head only; owner resupplied target and Candidate03 body; hidden machinery reconstructed. No recovered dimensions.',
 'limits':['Local proposal only.','No finished materials or acceptance.','New regional geometry invalidates prior surface-clearance results for these regions.'],'views':[]}
(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')

def render(path,label):
    bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';sh=s.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='SINGLE';sh.single_color=(.56,.58,.60);sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';s.world.color=(.12,.13,.14)
    s.render.resolution_x=s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
    for o in bpy.data.objects:
        o.hide_set(False)
        if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
    cd=bpy.data.cameras.new('Temporary V15 matched camera');cam=bpy.data.objects.new(cd.name,cd);s.collection.objects.link(cam);s.camera=cam;cd.type='ORTHO'
    views=[('reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5),('head',(-6,-3.5,2.45),(0,-.27,1.62),1.10),('head-profile',(-7.5,-.3,1.63),(0,-.3,1.63),1.15),('front',(0,-7,1.65),(0,-.08,1.02),2.5),('rear',(0,7,1.65),(0,-.08,1.02),2.5),('legs',(-6,-3.5,1.65),(0,-.03,.42),1.25)]
    for name,pos,target,scale in views:
        cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=scale;f=AUDIT/f'{label}-{name}.png';s.render.filepath=str(f);bpy.ops.render.render(write_still=True);receipt['views'].append({**art(f),'camera':{'position':pos,'target':target,'scale':scale},'lighting':'neutral native Workbench'})
render(native,'after');render(BASE,'before');(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');assert sha(BASE)==EXPECTED
print(json.dumps({'native':receipt['native'],'changed':len(changed),'new':len(new),'removed':len(removed),'preservation':receipt['preservation']}))
