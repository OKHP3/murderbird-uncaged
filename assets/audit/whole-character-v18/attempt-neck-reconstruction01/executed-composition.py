"""Compose bounded exterior regions on the pinned V17 attempt02 construction.

Editable rigid surfaces, no material polish or owner-acceptance implication.
Each run writes a new attempt and freezes the exact executed regional sources.
"""
from pathlib import Path
import argparse, sys, hashlib, json, runpy, shutil
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--attempt',required=True)
p.add_argument('--regions',default='breast-fit,orbital-fit,leg-envelope')
p.add_argument('--full-review',action='store_true',help='Add leg, opposite profile and early-era comparison views')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
BASE=ROOT/'assets/models/whole-character-v17/attempt-02/murderbird-whole-character-v17.blend'
EXPECTED='7d371907b279eb3d625e67164d84a78b2901a5cb6a79917def07f48ff8792d7b'
OUT=ROOT/f'assets/models/whole-character-v18/attempt-{a.attempt}'
AUDIT=ROOT/f'assets/audit/whole-character-v18/attempt-{a.attempt}'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def art(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path),'bytes':path.stat().st_size}
assert sha(BASE)==EXPECTED and not OUT.exists() and not AUDIT.exists()
OUT.mkdir(parents=True);AUDIT.mkdir(parents=True)
shutil.copy2(__file__,AUDIT/'executed-composition.py')
h=runpy.run_path(str(ROOT/'scripts/build-uncaged-alignment-v7.py'),run_name='v18_snapshot_helpers')
bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']()
materials={m.name:h['material_signature'](m) for m in bpy.data.materials}
patches=[]
claimed=set()
for region in a.regions.split(','):
    assert region in ('breast-fit','neck-lap-fit','neck-reconstruction','orbital-fit','leg-envelope')
    source=ROOT/f'scripts/regions/whole-character-v18-{region}.py'
    frozen=AUDIT/f'executed-{region}.py';shutil.copy2(source,frozen)
    regional_before=h['scene_snapshot']()
    result=runpy.run_path(str(source),run_name=f'v18_{region}_patch')['apply']()
    result.pop('createdObjects',None)
    bpy.context.view_layer.update();regional_after=h['scene_snapshot']()
    actual_changed=sorted(n for n in regional_before['meshes']
      if regional_before['meshes'][n]!=regional_after['meshes'].get(n))
    actual_new=sorted(set(regional_after['meshes'])-set(regional_before['meshes']))
    touched=set(actual_changed+actual_new)
    assert not claimed.intersection(touched),f'Regional edits overlap: {sorted(claimed.intersection(touched))}'
    claimed.update(touched)
    patches.append({'source':art(frozen),'result':result,
      'observedChangedMeshes':actual_changed,'observedNewMeshes':actual_new})
bpy.context.view_layer.update();after=h['scene_snapshot']()
assert before['empties']==after['empties'],'Exterior modules changed articulation or landmarks'
assert before['curves']==after['curves'],'Exterior modules changed historical authoring curves'
assert materials=={m.name:h['material_signature'](m) for m in bpy.data.materials},'Material definitions changed during geometry pass'
changed=[n for n in before['meshes'] if before['meshes'][n]!=after['meshes'].get(n)]
new=[n for n in after['meshes'] if n not in before['meshes']]
removed=[n for n in before['meshes'] if n not in after['meshes']]
for name in new:
    obj=bpy.data.objects[name]
    assert obj.parent and obj.parent.type=='EMPTY',f'New mesh has no rigid owner: {name}'
    assert obj.get('exteriorEras') and obj.get('region') and obj.get('surfaceRole'),f'Missing export eligibility: {name}'
native=OUT/'murderbird-whole-character-v18.blend'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False)
bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after,'Native reopen mismatch'
receipt={'status':'regional exterior construction proposal; no likeness or clearance acceptance',
 'base':art(BASE),'native':art(native),'composer':art(AUDIT/'executed-composition.py'),'regions':patches,
 'preservation':{'exactRigidNodes':len(after['empties']),'exactHistoricalGuides':len(after['curves']),
 'exactUnchangedMeshes':len(before['meshes'])-len(changed),'exactMaterialDefinitions':True,'saveReopenExact':True},
 'changedMeshes':changed,'addedMeshes':new,'removedMeshes':removed,
 'authority':'July head only; selected Maker breast construction, Candidate03 and owner target for whole-character recognition. Qualitative dimensions and unseen connections are proposals.',
 'limits':['New breast/head/leg surfaces need fresh movement-clearance review.','Targeted regional repairs do not establish whole-body continuous clearance.','No finished material pass or artistic acceptance.'],'views':[]}
(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')

def render(path,label):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH'
    sh=s.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='SINGLE'
    sh.single_color=(.56,.58,.60);sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH'
    sh.background_type='WORLD';s.world.color=(.12,.13,.14)
    s.render.resolution_x=s.render.resolution_y=1100;s.render.resolution_percentage=100
    s.render.image_settings.file_format='PNG'
    for obj in bpy.data.objects:
        obj.hide_set(False)
        if obj.type=='MESH':obj.hide_render='builder' not in obj.get('exteriorEras','maker,mechanic,builder').split(',')
        if obj.type=='CURVE':obj.hide_render=True
    cd=bpy.data.cameras.new('Temporary V18 matched camera');cd.type='ORTHO'
    cam=bpy.data.objects.new(cd.name,cd);s.collection.objects.link(cam);s.camera=cam
    views=[('reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5),
      ('front',(0,-7,1.65),(0,-.08,1.02),2.5),('side',(-7,0,1.35),(0,-.08,1.02),2.5),
      ('rear',(0,7,1.65),(0,-.08,1.02),2.5),
      ('head',(-6,-3.5,2.45),(0,-.27,1.56),1.12),
      ('breast',(-6,-4,1.9),(0,-.1,1.04),1.35)]
    render_views=[(*view,'builder') for view in views]
    if a.full_review:
        render_views.extend([
          ('opposite-side',(7,0,1.35),(0,-.08,1.02),2.5,'builder'),
          ('legs',(-6,-3.5,1.45),(0,-.08,.44),1.3,'builder'),
          ('shoulder',(-6,-3.5,2.75),(-.1,.0,1.12),1.3,'builder'),
        ])
        for era in ('maker','mechanic'):
            render_views.extend([(f'{era}-{name}',pos,target,scale,era)
              for name,pos,target,scale in views[:4]])
    for name,pos,target,scale,era in render_views:
        for obj in bpy.data.objects:
            if obj.type=='MESH':obj.hide_render=era not in obj.get('exteriorEras','maker,mechanic,builder').split(',')
        cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
        cd.ortho_scale=scale;image=AUDIT/f'{label}-{name}.png';s.render.filepath=str(image)
        bpy.ops.render.render(write_still=True)
        receipt['views'].append({**art(image),'era':era,'camera':{'position':pos,'target':target,'scale':scale},'lighting':'neutral native Workbench; guide curves hidden'})
render(native,'after');render(BASE,'before')
(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
assert sha(BASE)==EXPECTED
print(json.dumps({'native':receipt['native'],'changed':len(changed),'added':len(new),'removed':len(removed),'preservation':receipt['preservation']}))
