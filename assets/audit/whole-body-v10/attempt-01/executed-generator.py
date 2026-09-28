"""One supervisor-owned neutral whole-body candidate, immutable per attempt.

Combine the fuller two-joint neck with the selected V9 bill. Fit the upper
mantle inward and strengthen inherited limb members while preserving bearing
end neighbourhoods. No material polish, source overwrite or app selection.
"""
from pathlib import Path
import argparse,hashlib,json,math,runpy,shutil,sys,tempfile
import bpy
from mathutils import Matrix,Vector

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--attempt',default='01');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
BASE=ROOT/'assets/models/uncaged-cervical-breast-transition-study-v2/murderbird-cervical-breast-transition-study-v2.blend'
BASE_SHA='f98d4a5a3dbed932b82ac1abc82e51dc79356321a3a9292ed718749387c403a8'
V9=ROOT/'assets/models/uncaged-alignment-v9/murderbird-alignment-v9.blend'
V9_SHA='4d7568d1c2ba7cab716876f57a6c20cb6a788d4daeef1d5d34f85c1910ed2bbe'
HELPER=ROOT/'scripts/build-uncaged-alignment-v7.py'
OUT=ROOT/f'assets/models/uncaged-whole-body-v10/attempt-{args.attempt}'
AUDIT=ROOT/f'assets/audit/whole-body-v10/attempt-{args.attempt}'
NATIVE=OUT/'murderbird-whole-body-v10.blend'
HEAD=['Profiled upper bill blade 0','Profiled upper bill blade 1','Forked forged mandible -1','Forked forged mandible 1','Distal mandible bridge']
PINS=['Bill root fixing']+[f'Bill root fixing.{i:03}' for i in range(1,4)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def artifact(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
assert sha(BASE)==BASE_SHA and sha(V9)==V9_SHA
assert not OUT.exists() and not AUDIT.exists(),'Use a new attempt; never overwrite a study'
OUT.mkdir(parents=True);AUDIT.mkdir(parents=True)
shutil.copy2(__file__,AUDIT/'executed-generator.py')
h=runpy.run_path(str(HELPER),run_name='whole_body_helpers')

# Transfer only the five selected bill geometries and the four fixing matrices.
with tempfile.TemporaryDirectory(prefix='murderbird-v10-transfer-') as temp:
    package=Path(temp)/'selected-v9-head.blend'
    bpy.ops.wm.open_mainfile(filepath=str(V9));h['scene_snapshot']()
    selected={n:h['mesh_signature'](bpy.data.objects[n]) for n in HEAD}
    pin_world={n:bpy.data.objects[n].matrix_world.copy() for n in PINS}
    originals={n:{'world':bpy.data.objects[n].matrix_world.copy(),'mats':[m.name for m in bpy.data.objects[n].data.materials]} for n in HEAD}
    clones=[]
    for n in HEAD:
        source=bpy.data.objects[n];o=source.copy();o.data=source.data.copy();o.name='V10_TRANSFER::'+n;o.parent=None;o.matrix_world=source.matrix_world.copy();clones.append(o)
    bpy.data.libraries.write(str(package),set(clones),compress=True)
    bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']()
    materials={m.name:h['material_signature'](m) for m in bpy.data.materials}
    original_mats={m.name:m for m in bpy.data.materials}
    for m in original_mats.values():
        if m.users==0:m.use_fake_user=True
    with bpy.data.libraries.load(str(package),link=False) as (_,data):data.objects=['V10_TRANSFER::'+n for n in HEAD]
    for name,source in zip(HEAD,data.objects):
        target=bpy.data.objects[name]
        assert max(abs(target.matrix_world[r][c]-originals[name]['world'][r][c]) for r in range(4) for c in range(4))<1e-7
        data_mesh=source.data;data_mesh.materials.clear()
        for m in originals[name]['mats']:data_mesh.materials.append(original_mats[m])
        target.data=data_mesh;bpy.data.objects.remove(source,do_unlink=True)
        assert h['mesh_signature'](target)==selected[name]
    for n,w in pin_world.items():bpy.data.objects[n].matrix_world=w
    for m in list(bpy.data.materials):
        if m.name not in original_mats:
            assert m.users==0;bpy.data.materials.remove(m)

changed=set(HEAD+PINS);construction={}

def mantle_point(p,side):
    """Monotonic inward fitting of high inner coverts, leaving outer span stable."""
    q=p.copy();x=abs(p.x)
    zweight=smooth((p.z-1.245)/.105)
    # Max derivative of this 55mm/100mm Gaussian is <0.48: no X-axis fold.
    shift=.055*math.exp(-((x-.330)/.100)**2)*zweight
    q.x-=side*shift
    return q

for o in list(bpy.data.objects):
    if o.type!='MESH' or not o.parent:continue
    side=1 if o.parent.name=='left-mantle' else -1 if o.parent.name=='right-mantle' else 0
    if not side:continue
    if 'shoulder covert' in o.name or 'oblique shoulder saddle' in o.name:
        inv=o.matrix_world.inverted();maximum=0
        for v in o.data.vertices:
            p=o.matrix_world@v.co;q=mantle_point(p,side);maximum=max(maximum,(q-p).length);v.co=inv@q
        o.data.update();changed.add(o.name)
        construction[o.name]={'operation':'fit upper inner mantle toward torso','owner':o.parent.name,'maximumRestVertexDisplacementM':maximum,'fixedPivot':True}
    elif o.name.startswith('Shoulder covert root pin'):
        w=o.matrix_world.copy();p=w.translation.copy();w.translation=mantle_point(p,side);o.matrix_world=w;changed.add(o.name)
        construction[o.name]={'operation':'rigid pin translation to fitted coverts','owner':o.parent.name,'maximumRestVertexDisplacementM':(w.translation-p).length}

# Thicken cross-sections only between the bearing seats. The first and last
# 15% of each existing load span remain exactly unchanged, preserving the
# fitted interfaces; no new floating cage or replacement joint is introduced.
def limb_point(p,a,b):
    axis=b-a;length=axis.length;unit=axis/length;t=(p-a).dot(unit)/length
    w=smooth((t-.15)/.22)*smooth((.85-t)/.22)
    centre=a+axis*t
    return centre+(p-centre)*(1+.50*w),w

for side in ('left','right'):
    for part,child in (('thigh','shin'),('shin','foot')):
        owner=bpy.data.objects[f'{side}-{part}'];end=bpy.data.objects[f'{side}-{child}'];a=owner.matrix_world.translation.copy();b=end.matrix_world.translation.copy()
        for o in list(bpy.data.objects):
            if o.type!='MESH' or o.parent!=owner:continue
            reshape=('tapered passive load rail' in o.name or f'shaped {part} guard' in o.name)
            fixing=o.name.startswith('Limb sheath fixing')
            if reshape:
                inv=o.matrix_world.inverted();maximum=0;protected_error=0
                for v in o.data.vertices:
                    p=o.matrix_world@v.co;q,w=limb_point(p,a,b);maximum=max(maximum,(q-p).length)
                    if w==0:protected_error=max(protected_error,(q-p).length)
                    v.co=inv@q
                o.data.update();changed.add(o.name)
                construction[o.name]={'operation':'increase middle cross-section, fixed end neighbourhoods','owner':owner.name,'spanEndsNative':[list(a),list(b)],'peakCrossSectionFactor':1.5,'endFractionProtected':.15,'maximumDisplacementM':maximum,'protectedWorldErrorM':protected_error,'eraClass':'inherited-passive'}
            elif fixing:
                w=o.matrix_world.copy();old=w.translation.copy();w.translation,_=limb_point(old,a,b);o.matrix_world=w;changed.add(o.name)
                construction[o.name]={'operation':'rigid fixing follows reshaped guard','owner':owner.name,'displacementM':(w.translation-old).length}

bpy.context.view_layer.update();after=h['scene_snapshot']()
assert before['empties']==after['empties'] and before['curves']==after['curves']
assert set(before['meshes'])==set(after['meshes'])
assert all(before['meshes'][n]==after['meshes'][n] for n in set(before['meshes'])-changed)
assert {m.name:h['material_signature'](m) for m in bpy.data.materials}==materials
for n in changed:
    assert before['meshes'][n]['parent']==after['meshes'][n]['parent']
    assert before['meshes'][n]['props']==after['meshes'][n]['props']
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(NATIVE),check_existing=False)
bpy.ops.wm.open_mainfile(filepath=str(NATIVE));assert h['scene_snapshot']()==after
receipt={'status':'whole-body neutral proposal awaiting independent views and motion review; not selected',
 'base':artifact(BASE),'selectedBillSource':artifact(V9),'native':artifact(NATIVE),'generator':artifact(AUDIT/'executed-generator.py'),'helper':artifact(HELPER),
 'changedFromNeckV2':sorted(changed),'construction':construction,
 'preservation':{'all52PivotsExactToNeckV2':True,'allGuideCurvesExact':True,'allMaterialsExact':True,'unlistedMeshesExact':len(before['meshes'])-len(changed),'headGeometryExactToV9':True,'saveReopenSnapshotExact':True},
 'limits':['The neck V2/source14 hierarchy differs from selected V9 by its optional upper cervical joint. Motion support exists but this new full candidate is untested.','Shoulder and limb shape changes are authored dimensions, not perspective illustration measurements.','Historical guide curves remain preserved but do not regenerate altered surfaces.','No new material finish, era power component, runtime selection or publication.'],
 'views':[]}
(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=True;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14)
scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
for o in bpy.data.objects:
    if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',');o.hide_set(False)
cd=bpy.data.cameras.new('Whole-body matched camera');cam=bpy.data.objects.new(cd.name,cd);scene.collection.objects.link(cam);scene.camera=cam;cd.type='ORTHO'
views=[('three-quarter',(-3.8,-6,3.2),(0,-.08,.98),2.55),('profile',(-7.5,0,1.25),(0,-.08,.98),2.55),('front',(0,-7,1.55),(0,-.08,.98),2.55),('rear',(0,7,1.55),(0,-.08,.98),2.55),('neck-shoulder',(-3.4,-5,2.05),(0,-.14,1.43),1.12)]
for name,pos,target,scale in views:
    cam.location=Vector(pos);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=scale
    out=AUDIT/f'{name}.png';scene.render.filepath=str(out);bpy.ops.render.render(write_still=True)
    receipt['views'].append({**artifact(out),'camera':{'position':pos,'target':target,'scale':scale},'era':'builder in neutral clay'})
(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
assert sha(NATIVE)==receipt['native']['sha256']
print(json.dumps({'native':receipt['native'],'meshes':len(after['meshes']),'changedFromBase':len(changed),'pivots':len(after['empties']),'views':len(views)}))
