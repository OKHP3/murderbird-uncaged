"""Write-once V24 regional composition and matched neutral views."""
from pathlib import Path
import argparse,hashlib,json,math,runpy,shutil,sys,inspect
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'assets/models/whole-character-v23/attempt-form03/murderbird-whole-character-v23.blend'
BASE_SHA='66b6ff8c17e468c0e1ab7874728a3aea889a5630fd25dafc3392d954a1343e62'
p=argparse.ArgumentParser();p.add_argument('--attempt',required=True);p.add_argument('--region',action='append',required=True,help='Repository relative module path=expected SHA256')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);assert a.attempt.replace('-','').isalnum()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def art(p):return {'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
AUDIT=ROOT/f'assets/audit/whole-character-v24/attempt-{a.attempt}';OUT=ROOT/f'assets/models/whole-character-v24/attempt-{a.attempt}'
assert sha(BASE)==BASE_SHA
sources=[]
for item in a.region:
    path,expected=item.rsplit('=',1);src=ROOT/path
    assert src.is_relative_to(ROOT/'scripts/regions') and sha(src)==expected
    sources.append(src)
assert not AUDIT.exists() and not OUT.exists();AUDIT.mkdir(parents=True);OUT.mkdir(parents=True)
shutil.copyfile(Path(__file__),AUDIT/'executed-builder.py')
shutil.copyfile(ROOT/'scripts/regions/whole-character-v21-envelope.py',AUDIT/'executed-envelope-helper.py')
shutil.copyfile(ROOT/'scripts/build-uncaged-alignment-v7.py',AUDIT/'executed-snapshot-helper.py')
h=runpy.run_path(str(AUDIT/'executed-snapshot-helper.py'))
bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']();mats={m.name:h['material_signature'](m) for m in bpy.data.materials}
regions=[]
for src in sources:
    dest=AUDIT/('executed-'+src.name);shutil.copyfile(src,dest)
    module=runpy.run_path(str(dest));fn=module['apply'];fn.__globals__['ROOT']=ROOT
    result=fn(AUDIT/'executed-envelope-helper.py') if 'envelope_helper' in inspect.signature(fn).parameters else fn()
    regions.append({'source':art(dest),'result':result})
bpy.context.view_layer.update()
front=None;front_name=None;deps=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    if o.type=='MESH' and o.parent and o.parent.name=='upper-bill':
        ev=o.evaluated_get(deps);mesh=ev.to_mesh()
        for v in mesh.vertices:
            pt=ev.matrix_world@v.co
            if front is None or pt.y<front.y:front=pt.copy();front_name=o.name
        ev.to_mesh_clear()
contacts=[]
for name in ('bill-contact','anchor-beak'):
    o=bpy.data.objects[name];old=list(o.matrix_world.translation);m=o.matrix_world.copy();m.translation=front;o.matrix_world=m
    contacts.append({'name':name,'oldWorld':old,'newWorld':list(front),'surfaceObject':front_name})
bpy.context.view_layer.update();after=h['scene_snapshot']()
assert mats=={m.name:h['material_signature'](m) for m in bpy.data.materials}
assert set(before['empties'])==set(after['empties'])
for n,r in before['empties'].items():
    if n not in ('bill-contact','anchor-beak'):assert r==after['empties'][n],n
protected=[]
for n,r in before['meshes'].items():
    if r['parent'] in ('left-thigh','right-thigh','left-shin','right-shin','left-foot','right-foot') or 'toe' in (r['parent'] or ''):
        assert after['meshes'].get(n)==r,n;protected.append(n)
finite=[];world_bounds={}
for o in bpy.data.objects:
    if o.type=='MESH':
        ev=o.evaluated_get(deps);mesh=ev.to_mesh();assert all(math.isfinite(c) for v in mesh.vertices for c in v.co),o.name
        world=[ev.matrix_world@v.co for v in mesh.vertices]
        minimum=[min(v[k] for v in world) for k in range(3)];maximum=[max(v[k] for v in world) for k in range(3)]
        world_bounds[o.name]={'min':minimum,'max':maximum}
        # Authored-model sanity envelope, not dimensions inferred from art.
        assert all(minimum[k]>=(-.75,-.95,-.05)[k] and maximum[k]<=(.75,.75,2.15)[k] for k in range(3)),f'Outlying rigid part: {o.name}: {minimum} / {maximum}'
        finite.append(o.name);ev.to_mesh_clear()
changed=[n for n,r in before['meshes'].items() if n in after['meshes'] and after['meshes'][n]!=r]
added=sorted(set(after['meshes'])-set(before['meshes']));removed=sorted(set(before['meshes'])-set(after['meshes']))
native=OUT/'murderbird-whole-character-v24.blend';bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
receipt={'status':'Regional construction proposal; not artistic or full-motion acceptance','base':art(BASE),'native':art(native),
 'sources':[art(AUDIT/n) for n in ('executed-builder.py','executed-envelope-helper.py','executed-snapshot-helper.py')],
 'regions':regions,'contactAdjustments':contacts,'changedMeshes':changed,'addedMeshes':added,'removedMeshes':removed,
 'checks':{'finiteMeshes':len(finite),'protectedLegFootMeshesExact':len(protected),'rigNodesExactExceptRefitContact':len(before['empties'])-2,'materialsExact':True,'saveReopenExact':True,'allMeshesWithinAuthoredSanityEnvelope':True},
 'limits':['Full procedural era hardware remains outside this study.','Rigid plate clearances require movement review.','Neutral construction surfaces are not a finished exterior.'],'views':[]}
(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
(AUDIT/'world-bounds.json').write_text(json.dumps({'meaning':'Authored model outlier guard; not dimensions recovered from illustration','meshBounds':world_bounds},indent=2)+'\n')
scene=bpy.context.scene
for o in bpy.data.objects:
    if o.animation_data:o.animation_data_clear()
    if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
    elif o.type=='CURVE':o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';sh=scene.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='SINGLE';sh.single_color=(.56,.58,.60);sh.show_shadows=False;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';scene.world.color=(.12,.13,.14)
scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
data=bpy.data.cameras.new('V24 temporary neutral review camera');data.type='ORTHO';camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera);scene.camera=camera
views=[('reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5),('front',(0,-7,1.65),(0,-.08,1.02),2.5),('side',(-7,0,1.35),(0,-.08,1.02),2.5),('rear',(0,7,1.65),(0,-.08,1.02),2.5),('neck',(-6,-3.5,2.45),(0,-.27,1.48),1.3)]
for name,pos,target,scale in views:
    camera.location=pos;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=scale
    scene.render.filepath=str(AUDIT/f'after-{name}.png');bpy.ops.render.render(write_still=True)
    receipt['views'].append({**art(Path(scene.render.filepath)),'camera':{'position':pos,'target':target,'orthoScale':scale},'lighting':'neutral Workbench no cast shadows'})
    (AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
assert sha(BASE)==BASE_SHA and sha(native)==receipt['native']['sha256']
print(json.dumps({'native':receipt['native'],'checks':receipt['checks'],'views':len(receipt['views'])}))
