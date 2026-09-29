"""Write-once V37 whole-character form composition and matched neutral views."""
from pathlib import Path
import argparse,hashlib,json,math,runpy,shutil,sys,inspect
import bpy
from mathutils import Vector
ROOT=Path(globals().get('SOURCE_ROOT',Path(__file__).resolve().parents[1]))
BASE=ROOT/'assets/models/whole-character-v35/attempt-form01/murderbird-whole-character-v35.blend'
BASE_SHA='d2c704ccf89f3f0e7dbeb3613dcdbdd964c4ba69991783783830803eecf59cb0'
p=argparse.ArgumentParser();p.add_argument('--attempt',required=True);p.add_argument('--region',action='append',required=True,help='Repository relative module path=expected SHA256')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);assert a.attempt.replace('-','').isalnum()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def art(p):return {'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
AUDIT=ROOT/f'assets/audit/whole-character-v37/attempt-{a.attempt}';OUT=ROOT/f'assets/models/whole-character-v37/attempt-{a.attempt}'
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
helper=ROOT/'scripts/regions/whole-character-v31-head-reconstruction.py'
shutil.copyfile(helper,AUDIT/'executed-regional-geometry-helper.py')
helper_sha=sha(helper)
breast_helper=ROOT/'scripts/regions/whole-character-v30-breast-form.py'
shutil.copyfile(breast_helper,AUDIT/'executed-breast-profile-helper.py')
breast_helper_sha=sha(breast_helper)
h=runpy.run_path(str(AUDIT/'executed-snapshot-helper.py'))
bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']();mats={m.name:h['material_signature'](m) for m in bpy.data.materials}
regions=[]
def names(records):
    return {entry if isinstance(entry,str) else entry['name'] for entry in records}
for src in sources:
    regional_before=h['scene_snapshot']()

    dest=AUDIT/('executed-'+src.name);shutil.copyfile(src,dest)
    module=runpy.run_path(str(dest));fn=module['apply'];fn.__globals__['ROOT']=ROOT
    result=fn(AUDIT/'executed-envelope-helper.py') if 'envelope_helper' in inspect.signature(fn).parameters else fn()
    regional_after=h['scene_snapshot']()
    bm,am=regional_before['meshes'],regional_after['meshes']
    actual_changed={n for n in bm.keys() & am.keys() if bm[n]!=am[n]}
    actual_added=set(am)-set(bm);actual_removed=set(bm)-set(am)
    declared_changed=names(result.get('changedMeshes',[]))
    declared_added=names(result.get('addedMeshes',result.get('added',[])))
    declared_removed=names(result.get('removedMeshes',result.get('removed',[])))
    assert actual_changed<=declared_changed, f'Undeclared revised meshes in {src.name}: {sorted(actual_changed-declared_changed)}'
    assert actual_added==declared_added, f'Added mesh contract mismatch in {src.name}'
    assert actual_removed==declared_removed, f'Removed mesh contract mismatch in {src.name}'
    bn,an=regional_before['empties'],regional_after['empties']
    assert set(bn)==set(an), f'Runtime node identity changed in {src.name}'
    actual_nodes={n for n in bn if bn[n]!=an[n]}
    assert actual_nodes<=names(result.get('changedNodes',[])), f'Undeclared node changes in {src.name}: {sorted(actual_nodes)}'
    assert regional_before['curves']==regional_after['curves'], f'Historical curves changed in {src.name}'
    assert mats=={m.name:h['material_signature'](m) for m in bpy.data.materials}, f'Material definitions changed in {src.name}'
    regions.append({'source':art(dest),'result':result,'compositionContract':{'actualChangedMeshes':sorted(actual_changed),'actualAddedMeshes':sorted(actual_added),'actualRemovedMeshes':sorted(actual_removed),'actualChangedNodes':sorted(actual_nodes),'undeclaredMeshSnapshotsExact':len(set(bm)&set(am)-actual_changed),'historicalCurvesExact':True,'materialDefinitionsExact':True}})
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
guides={o.name for o in bpy.data.objects if o.get('authoringGuide') is True}
assert not guides.intersection(before['empties']), 'Runtime nodes cannot be reclassified as guides'
assert not guides.intersection(before['meshes']), 'Runtime meshes cannot be hidden as guides'
runtime_empties={n:r for n,r in after['empties'].items() if n not in guides}
guide_inventory=[{'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'props':json.loads(json.dumps(dict(o.items()),default=lambda value:list(value)))} for o in bpy.data.objects if o.name in guides]
declared_nodes={n if isinstance(n,str) else n['name'] for entry in regions for n in entry['result'].get('changedNodes',[])}
# Contact markers are recomputed from actual composed bill geometry above.
declared_nodes.update(('bill-contact','anchor-beak'))
assert mats=={m.name:h['material_signature'](m) for m in bpy.data.materials}
assert set(before['empties'])==set(runtime_empties)
changed_nodes=[]
for n,r in before['empties'].items():
    now=after['empties'][n]
    assert r['parent']==now['parent'] and r['visibility']==now['visibility'],n
    if n not in declared_nodes:assert r==now,n
    else:
        assert max(abs(r['matrix'][i][j]-now['matrix'][i][j]) for i in range(3) for j in range(3))<1e-6,n
    if r!=now:changed_nodes.append({'name':n,'old':r,'new':now})
protected=[];revised_feet=[]
declared_feet={n if isinstance(n,str) else n['name'] for entry in regions for n in entry['result'].get('changedFootMeshes',[])}
# V37 explicitly revises the compact foot envelope, articulated toe pivots
# and talons together. Exact named changes are restricted to foot/digit owners;
# undeclared geometry and unrelated rests remain protected.
def foot_owner(parent):
    return parent in ('left-foot','right-foot') or 'toe' in (parent or '') or 'digit' in (parent or '')
removed_feet={n for entry in regions for n in entry['compositionContract']['actualRemovedMeshes'] if foot_owner(before['meshes'].get(n,{}).get('parent'))}
assert all(n in before['meshes'] and foot_owner(before['meshes'][n]['parent']) for n in declared_feet|removed_feet)
for n,r in before['meshes'].items():
    if r['parent'] in ('left-foot','right-foot') or 'toe' in (r['parent'] or '') or 'digit' in (r['parent'] or ''):
        if n in removed_feet:
            assert n not in after['meshes'];revised_feet.append(n)
        elif n in declared_feet:
            assert n in after['meshes'] and r['parent']==after['meshes'][n]['parent'],n;revised_feet.append(n)
        else:
            assert after['meshes'].get(n)==r,n;protected.append(n)
finite=[];world_bounds={}
for o in bpy.data.objects:
    if o.type=='MESH' and o.name not in guides:
        ev=o.evaluated_get(deps);mesh=ev.to_mesh();assert all(math.isfinite(c) for v in mesh.vertices for c in v.co),o.name
        world=[ev.matrix_world@v.co for v in mesh.vertices]
        minimum=[min(v[k] for v in world) for k in range(3)];maximum=[max(v[k] for v in world) for k in range(3)]
        world_bounds[o.name]={'min':minimum,'max':maximum}
        # Authored-model sanity envelope, not dimensions inferred from art.
        assert all(minimum[k]>=(-.75,-.95,-.05)[k] and maximum[k]<=(.75,.75,2.25)[k] for k in range(3)),f'Outlying rigid part: {o.name}: {minimum} / {maximum}'
        finite.append(o.name);ev.to_mesh_clear()
changed=[n for n,r in before['meshes'].items() if n in after['meshes'] and after['meshes'][n]!=r]
added=sorted(set(after['meshes'])-set(before['meshes']));removed=sorted(set(before['meshes'])-set(after['meshes']))
native=OUT/'murderbird-whole-character-v37.blend';bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
receipt={'status':'Regional construction proposal; not artistic or full-motion acceptance','base':art(BASE),'native':art(native),
 'sources':[art(AUDIT/n) for n in ('executed-builder.py','executed-envelope-helper.py','executed-snapshot-helper.py','executed-regional-geometry-helper.py','executed-breast-profile-helper.py')],
 'regions':regions,'nonExportingAuthoringGuides':guide_inventory,'contactAdjustments':contacts,'revisedFootReceivingMeshes':revised_feet,'supersededFootMeshes':sorted(removed_feet),'rigChanges':changed_nodes,'changedMeshes':changed,'addedMeshes':added,'removedMeshes':removed,
 'checks':{'finiteMeshes':len(finite),'protectedFootToeMeshesExact':len(protected),'declaredFootToeGeometryChanges':len(revised_feet),'unchangedRigNodesExact':len(before['empties'])-len(changed_nodes),'declaredRigNodeChanges':len(changed_nodes),'materialsExact':True,'saveReopenExact':True,'allMeshesWithinAuthoredSanityEnvelope':True},
 'limits':['Whole-character form proposal; likeness and full procedural era hardware remain unresolved.','Rigid plate clearances require movement review.','Neutral construction surfaces are not a finished exterior.'],'views':[]}
(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
(AUDIT/'world-bounds.json').write_text(json.dumps({'meaning':'Authored model outlier guard; not dimensions recovered from illustration','meshBounds':world_bounds},indent=2)+'\n')
scene=bpy.context.scene
for o in bpy.data.objects:
    if o.animation_data:o.animation_data_clear()
    if o.name in guides:o.hide_render=True
    elif o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
    elif o.type=='CURVE':o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';sh=scene.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='SINGLE';sh.single_color=(.56,.58,.60);sh.show_shadows=False;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';scene.world.color=(.12,.13,.14)
scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
data=bpy.data.cameras.new('V37 temporary neutral review camera');data.type='ORTHO';camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera);scene.camera=camera
views=[('reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5),('front',(0,-7,1.65),(0,-.08,1.02),2.5),('side',(-7,0,1.35),(0,-.08,1.02),2.5),('rear',(0,7,1.65),(0,-.08,1.02),2.5),('neck',(-6,-3.5,2.45),(0,-.27,1.48),1.3)]
for name,pos,target,scale in views:
    camera.location=pos;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=scale
    scene.render.filepath=str(AUDIT/f'after-{name}.png');bpy.ops.render.render(write_still=True)
    receipt['views'].append({**art(Path(scene.render.filepath)),'camera':{'position':pos,'target':target,'orthoScale':scale},'lighting':'neutral Workbench no cast shadows'})
    (AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
assert sha(BASE)==BASE_SHA and sha(native)==receipt['native']['sha256'] and sha(helper)==helper_sha and sha(breast_helper)==breast_helper_sha
print(json.dumps({'native':receipt['native'],'checks':receipt['checks'],'views':len(receipt['views'])}))
