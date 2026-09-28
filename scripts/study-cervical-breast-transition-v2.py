"""Shape-first cervical reconstruction; immutable candidate and matched clay views.

The bowed envelope and individual rigid lap plates are a reconstruction from
Candidate03, not measured engineering. No runtime selection or finished surface.
"""
from pathlib import Path
import hashlib,json,math,runpy,shutil
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'assets/models/uncaged-cervical-construction-study-v1/attempt-14/murderbird-cervical-construction-study-v1.blend'
SOURCE_SHA='ef9e28ddbce9d62aabc8181a058640ea1e8b7a339b673df37b913d96699f9440'
AUDIT=ROOT/'assets/audit/cervical-breast-transition-study-v2'
MODEL=ROOT/'assets/models/uncaged-cervical-breast-transition-study-v2'
NATIVE=MODEL/'murderbird-cervical-breast-transition-study-v2.blend'
HELPER=ROOT/'scripts/build-uncaged-alignment-v7.py'
REFERENCE=ROOT/'assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png'
ALLOW={*(f'Throat formed lamina {i}' for i in range(1,7)),
       *(f'Cervical flank lamina {s} {i}' for s in (-1,1) for i in range(1,7)),
       'Upper breast cervical yoke front','Upper breast cervical yoke left','Upper breast cervical yoke right'}
VIEWS=[('three-quarter',(-3.8,-6,3.2),(0,-.08,.98),2.55),
       ('profile',(-7.5,0,1.25),(0,-.08,.98),2.55),
       ('front',(0,-7,1.55),(0,-.08,.98),2.55),
       ('neck',(-3.4,-5,2.05),(0,-.20,1.49),.98)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def artifact(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
assert sha(SOURCE)==SOURCE_SHA
assert not AUDIT.exists() and not MODEL.exists(),'Preserve previous candidates; use a new version'
AUDIT.mkdir(parents=True);MODEL.mkdir(parents=True)
shutil.copy2(__file__,AUDIT/'executed-generator.py')
h=runpy.run_path(str(HELPER),run_name='snapshot_helpers')
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));before=h['scene_snapshot']()
assert len(before['empties'])==52 and ALLOW<=set(before['meshes'])
materials={m.name:h['material_signature'](m) for m in bpy.data.materials}

# Native Z-up, -Y forward, +X anatomical left. The entire rest outline is
# designed continuously; individual owners articulate without deforming metal.
# Z, front Y, rear Y, lateral radius. Dimensions are authored, not source metrology.
PROFILE=[(1.19,-.365,-.025,.230),(1.255,-.376,-.040,.215),
 (1.310,-.390,-.055,.208),(1.370,-.405,-.085,.188),
 (1.435,-.397,-.135,.165),(1.500,-.364,-.179,.132),
 (1.560,-.337,-.206,.112),(1.630,-.312,-.229,.095),
 (1.680,-.298,-.222,.098)]
def sample(z,k):
    if z<=PROFILE[0][0]:return PROFILE[0][k]
    if z>=PROFILE[-1][0]:return PROFILE[-1][k]
    for i,(a,b) in enumerate(zip(PROFILE,PROFILE[1:])):
        if a[0]<=z<=b[0]:
            t=(z-a[0])/(b[0]-a[0]);d=b[0]-a[0]
            lo=PROFILE[max(i-1,0)];hi=PROFILE[min(i+2,len(PROFILE)-1)]
            ma=(b[k]-lo[k])/(b[0]-lo[0]);mb=(hi[k]-a[k])/(hi[0]-a[0])
            return (2*t**3-3*t*t+1)*a[k]+(t**3-2*t*t+t)*d*ma+(-2*t**3+3*t*t)*b[k]+(t**3-t*t)*d*mb
def point(z,a,off):
    front,rear,rx=[sample(z,k) for k in (1,2,3)]
    cy=(front+rear)/2;ry=(rear-front)/2
    return Vector(((rx+off)*math.sin(a),cy-(ry+off)*math.cos(a),z))

def patch(name,top,bottom,centre,half,radial,tip=.016,skew=0,sweep=0):
    obj=bpy.data.objects[name];na=20;nt=14;verts=[];faces=[]
    for j in range(nt+1):
        t=j/nt;ease=t*t*(3-2*t)
        for k in range(na+1):
            q=2*k/na-1
            # Narrow, rounded lower edge rather than a horizontal belt.
            width=1-.30*ease
            a=centre+half*q*width+sweep*ease
            z=top+(bottom-top)*t-tip*(1-q*q)*t*t+skew*q+.004*q*q*(1-t)
            off=radial+.011*ease+.002*(1-q*q)*math.sin(math.pi*t)
            verts.append(point(z,a,off))
    for j in range(nt):
        for k in range(na):
            n=j*(na+1)+k
            faces.append((n,n+na+1,n+na+2,n+1))
    inv=obj.matrix_world.inverted();data=bpy.data.meshes.new(name+' shaped lap v2')
    data.from_pydata([inv@p for p in verts],[],faces);data.update()
    for m in obj.data.materials:data.materials.append(m)
    old=obj.data;obj.data=data
    if not old.users:bpy.data.meshes.remove(old)
    obj.modifiers.clear()
    wall=obj.modifiers.new('Rigid formed guard wall','SOLIDIFY');wall.thickness=.004;wall.offset=-1;wall.use_even_offset=True
    bevel=obj.modifiers.new('Formed edge radius','BEVEL');bevel.width=.001;bevel.segments=2
    for p in data.polygons:p.use_smooth=True
    return {'owner':obj.parent.name,'topM':top,'bottomM':bottom,'centreRad':centre,'halfSpanRad':half,'wallM':.004,'radialM':radial,'construction':'tapered curved lap; metal rigid on one inherited owner'}

construction={}
courses=[(1.653,1.563),(1.589,1.499),(1.525,1.435),
         (1.462,1.372),(1.400,1.310),(1.338,1.250)]
for i,(top,bottom) in enumerate(courses,1):
    n=f'Throat formed lamina {i}'
    construction[n]=patch(n,top,bottom,0,.64,.006,tip=.017,skew=.003*(-1)**i)
    for side in (-1,1):
        n=f'Cervical flank lamina {side} {i}'
        # Offset adjacent seams, with a small posterior swept tip; open back
        # deliberately retains visible frame rather than closing a rigid collar.
        construction[n]=patch(n,top+.014,bottom+.010,side*1.32,.76,.007,
            tip=.020,skew=-side*.008,sweep=side*.045)
for label,centre,half in [('front',0,.67),('left',1.32,.67),('right',-1.32,.67)]:
    n='Upper breast cervical yoke '+label
    construction[n]=patch(n,1.294,1.218,centre,half,.009,tip=.020,skew=0,sweep=0)

after=h['scene_snapshot']()
assert before['empties']==after['empties'] and before['curves']==after['curves']
assert set(before['meshes'])==set(after['meshes'])
assert all(before['meshes'][n]==after['meshes'][n] for n in set(before['meshes'])-ALLOW)
assert materials=={m.name:h['material_signature'](m) for m in bpy.data.materials}
for n in ALLOW:
    for k in ('parent','matrix','props','visibility'):assert before['meshes'][n][k]==after['meshes'][n][k],(n,k)
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(NATIVE),check_existing=False)
bpy.ops.wm.open_mainfile(filepath=str(NATIVE));reopened=h['scene_snapshot']();assert after==reopened
receipt={'status':'neutral shape proposal awaiting visual and clearance review; not integrated',
 'source':artifact(SOURCE),'native':artifact(NATIVE),'generator':artifact(AUDIT/'executed-generator.py'),
 'snapshotHelper':artifact(HELPER),'reference':artifact(REFERENCE),
 'replace':sorted(ALLOW),'added':[],'profile':PROFILE,'construction':construction,
 'preservation':{'all52PivotParentsAndWorldMatricesExact':True,'all462GuideCurvesExact':True,
 'allMaterialsExact':True,'otherMeshesExact':len(before['meshes'])-len(ALLOW),
 'changedMeshOwnershipRestMatricesAndPropertiesExact':True,'saveReopenSnapshotExact':True},
 'scope':['Candidate03 controls the visible neck/breast relationship. Hidden overlap geometry is reconstructed.',
 'July head-only source supplies no body proportions. Head/bill geometry in this source is historical V8, not selected V9.',
 'Only guards and breast transition reshaped. Existing joint drives, shoulder, limbs and runtime are untouched.',
 'Original guide curves remain unchanged historical construction aids; do not claim they trace the new surfaces.',
 'No material polish, skin deformation, export, live selection or publication. Clearance and attachment checks pending.'],
 'views':[]}
(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
def render_model(path,tag):
    bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
    scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH'
    s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60)
    s.show_shadows=True;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14)
    scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    for o in bpy.data.objects:
        if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',');o.hide_set(False)
    cd=bpy.data.cameras.new('Matched cervical camera');cam=bpy.data.objects.new(cd.name,cd);scene.collection.objects.link(cam);scene.camera=cam;cd.type='ORTHO'
    for name,pos,target,scale in VIEWS:
        cam.location=Vector(pos);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=scale
        out=AUDIT/f'{tag}-{name}.png';scene.render.filepath=str(out);bpy.ops.render.render(write_still=True)
        receipt['views'].append({**artifact(out),'camera':{'position':pos,'target':target,'orthoScale':scale},'era':'builder visibility; neutral clay'})
        (AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
render_model(NATIVE,'after')
render_model(SOURCE,'before')
assert sha(NATIVE)==receipt['native']['sha256']
print(json.dumps({'native':receipt['native'],'changed':len(ALLOW),'views':len(receipt['views'])}))
