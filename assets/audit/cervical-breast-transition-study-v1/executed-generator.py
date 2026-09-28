"""One coupled lower-throat / upper-breast reconstruction proposal from attempt14.

Creates one pinned native candidate and first-look views. The application,
materials, pivots, and all non-allowlisted geometry remain untouched.
"""
from pathlib import Path
import hashlib,json,math,shutil,runpy
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'assets/models/uncaged-cervical-construction-study-v1/attempt-14/murderbird-cervical-construction-study-v1.blend'
SOURCE_SHA='ef9e28ddbce9d62aabc8181a058640ea1e8b7a339b673df37b913d96699f9440'
MODEL=ROOT/'assets/models/uncaged-cervical-breast-transition-study-v1'
AUDIT=ROOT/'assets/audit/cervical-breast-transition-study-v1'
NATIVE=MODEL/'murderbird-cervical-breast-transition-study-v1.blend'
CANDIDATE03=ROOT/'assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png'
HELPER=ROOT/'scripts/build-uncaged-alignment-v7.py'
ALLOW={*(f'Throat formed lamina {i}' for i in (4,5,6)),
       *(f'Cervical flank lamina {s} {i}' for s in (-1,1) for i in (4,5,6)),
       'Upper breast cervical yoke front','Upper breast cervical yoke left','Upper breast cervical yoke right'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def artifact(p):return {'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)}
if sha(SOURCE)!=SOURCE_SHA:raise RuntimeError('Pinned attempt14 native hash mismatch')
if AUDIT.exists() or MODEL.exists():raise RuntimeError('Refusing to overwrite an existing proposal')
AUDIT.mkdir(parents=True);MODEL.mkdir(parents=True)
shutil.copy2(__file__,AUDIT/'executed-generator.py')
h=runpy.run_path(str(HELPER),run_name='transition_snapshot_helpers')
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene
objs={o.name:o for o in bpy.data.objects}; before=h['scene_snapshot']()
assert len(before['empties'])==52 and set(ALLOW)<=set(before['meshes'])
materials={m.name:h['material_signature'](m) for m in bpy.data.materials}

# Reconstructed neck envelope: a broad lower throat tapering upward into the
# articulated fork. The front courses lap downward, while lateral plates wrap
# around each flank; deliberately overlap the distinct upper-owner course.
PROFILE=[(1.225,.170,-.190,.180),(1.300,.160,-.200,.170),
         (1.365,.142,-.215,.158),(1.435,.112,-.215,.150),
         (1.500,.085,-.195,.132),(1.555,.066,-.180,.112)]
def sample(z,k):
    if z<=PROFILE[0][0]:return PROFILE[0][k]
    if z>=PROFILE[-1][0]:return PROFILE[-1][k]
    for a,b in zip(PROFILE,PROFILE[1:]):
        if a[0]<=z<=b[0]:
            t=(z-a[0])/(b[0]-a[0]);t=t*t*(3-2*t)
            return a[k]*(1-t)+b[k]*t
def point(z,ang,radial=0):
    rx=sample(z,1);cy=sample(z,2);ry=sample(z,3)
    return Vector(((rx+radial)*math.sin(ang),cy-(ry+radial)*math.cos(ang),z))

def closed_band(obj,z_top,z_bottom,a0,a1,offset=.004,wall=.006,teardrop=.008):
    across=32;along=14;outer=[];inner=[]
    for j in range(along+1):
        t=j/along
        for k in range(across+1):
            q=2*k/across-1
            z=z_top+(z_bottom-z_top)*t-teardrop*(1-q*q)*t*t
            ang=a0+(a1-a0)*(k/across)+.035*q*t
            outer.append(point(z,ang,offset));inner.append(point(z,ang,offset-wall))
    verts=outer+inner;faces=[];n=(along+1)*(across+1)
    for j in range(along):
        for k in range(across):
            i=j*(across+1)+k
            faces.extend([(i,i+1,i+across+2,i+across+1),
                          (n+i,n+i+across+1,n+i+across+2,n+i+1)])
    for k in range(across):
        faces.extend([(k,n+k,n+k+1,k+1),
                      (along*(across+1)+k,along*(across+1)+k+1,n+along*(across+1)+k+1,n+along*(across+1)+k)])
    for j in range(along):
        a=j*(across+1);b=(j+1)*(across+1)
        faces.extend([(a,b,n+b,n+a),(a+across,n+a+across,n+b+across,b+across)])
    obj=bpy.data.objects[obj.name]
    local=[obj.matrix_world.inverted()@v for v in verts]
    mesh=bpy.data.meshes.new(obj.name+' transition proposal mesh');mesh.from_pydata(local,[],faces);mesh.update()
    for mat in obj.data.materials:mesh.materials.append(mat)
    old=obj.data;obj.data=mesh
    if old.users==0:bpy.data.meshes.remove(old)
    return {'vertices':len(mesh.vertices),'polygons':len(mesh.polygons),'topZ':z_top,'bottomZ':z_bottom,'arcRadians':[a0,a1],'wallM':wall,'radialOffsetM':offset,'construction':'closed curved loft; overlapping rigid lap course'}

bands={}
for idx,(top,bottom) in zip((4,5,6),[(1.505,1.365),(1.420,1.285),(1.335,1.225)]):
    name=f'Throat formed lamina {idx}'
    bands[name]=closed_band(objs[name],top,bottom,-1.22,1.22,offset=.005,wall=.006,teardrop=.010)
    for side in (-1,1):
        n=f'Cervical flank lamina {side} {idx}'
        bands[n]=closed_band(objs[n],top+.004,bottom+.010,side*1.10,side*2.70,offset=.004,wall=.006,teardrop=.008)

# Coupled breast transition: reshape the three existing opening lips into a
# wide U-shaped shoulder apron. The front segment stays low over the sternum;
# the side wings rise and blend into the neck guard ends. Existing shell pivots
# and the breast opening transform are untouched. These are reconstruction
# dimensions; the rest-silhouette still requires independent visual review.
def deform_yoke(name,kind):
    o=objs[name];mesh=o.data;assert len(mesh.vertices)==275, (name,len(mesh.vertices))
    inv=o.matrix_world.inverted(); across=25;along=11;new=[]
    for i,v in enumerate(mesh.vertices):
        j=i//across;k=i%across;q=2*k/(across-1)-1;t=j/(along-1)
        p=o.matrix_world@v.co
        if kind=='front':
            # Sternum-facing apron with a low center relieved for the throat.
            wing=abs(q)**2.2
            p.x*=1.30
            p.y-=.010+.004*(1-t)
            p.z += (1-t)*(.008+.050*wing) - t*.010
        else:
            # Bilateral rising shoulder wings; their top edges meet the wrapped
            # throat courses, rather than forming a full cylindrical cuff.
            p.x += (1 if kind=='left' else -1)*(.008+.018*(1-t))
            p.y-=.008
            p.z += (1-t)*(.030+.018*(1-abs(q))) - t*.008
        new.append(inv@p)
    data=bpy.data.meshes.new(name+' coupled apron proposal mesh');data.from_pydata(new,[],[tuple(p.vertices) for p in mesh.polygons]);data.update()
    for mat in mesh.materials:data.materials.append(mat)
    old=o.data;o.data=data
    if old.users==0:bpy.data.meshes.remove(old)
    if not any(m.type=='SOLIDIFY' for m in o.modifiers):
        solid=o.modifiers.new('Formed breast apron wall','SOLIDIFY');solid.thickness=.004;solid.offset=-1
    return {'vertexCount':len(data.vertices),'polygonCount':len(data.polygons),'modifier':[{'name':m.name,'type':m.type,'thickness':m.thickness if m.type=='SOLIDIFY' else None} for m in o.modifiers], 'construction':'existing yoke grid broadened into front apron or rising side wing; distinct breastplate owner retained'}
yokes={n:deform_yoke(n,k) for n,k in [('Upper breast cervical yoke front','front'),('Upper breast cervical yoke left','left'),('Upper breast cervical yoke right','right')]}

after=h['scene_snapshot']()
assert before['empties']==after['empties'] and before['curves']==after['curves']
assert set(before['meshes'])==set(after['meshes'])
assert all(before['meshes'][n]==after['meshes'][n] for n in set(before['meshes'])-ALLOW)
assert materials=={m.name:h['material_signature'](m) for m in bpy.data.materials}
for n in ALLOW:
    for key in ('parent','matrix','props'):
        assert before['meshes'][n][key]==after['meshes'][n][key],(n,key)
NATIVE.parent.mkdir(parents=True,exist_ok=True)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(NATIVE),check_existing=False)
bpy.ops.wm.open_mainfile(filepath=str(NATIVE));reopened=h['scene_snapshot']()
assert set(reopened['meshes'])==set(after['meshes']) and reopened['empties']==after['empties'] and reopened['curves']==after['curves']
assert all(reopened['meshes'][n]==after['meshes'][n] for n in set(after['meshes'])-ALLOW)

receipt={'status':'one coupled native proposal; visual review first; no broad validation yet',
 'source':artifact(SOURCE),'candidate03':artifact(CANDIDATE03),'native':artifact(NATIVE),
 'generator':artifact(AUDIT/'executed-generator.py'),'replace':sorted(ALLOW),'add':[],
 'preservation':{'all52PivotsParentAndMatricesExact':True,'allCurvesExact':True,'allMaterialsAndPropertiesExact':True,'allNonAllowlistedMeshesExact':True,'changedObjectParentsRestMatricesAndPropsExact':True,'saveReloadStructuralSnapshotVerified':True},
 'construction':{'lowerNeck':bands,'breastOpeningApron':yokes,'ownership':'Throat guard courses remain on their original neck or cervical-upper rigid owners; all three apron pieces remain on breastplate. These surfaces intentionally lap at rest but move with distinct owners during inspection.','dimensions':'Reconstructed analytic taper and apron rises; no exact illustration metrology.'},
 'limits':['No runtime or GLB change.','Candidate03 governs neck/breast shape; July head-only reference does not govern this region.','Selected era images are historical authoring views, not independent era-reference art; the current folder copies are LFS pointers and were not used as source authority.','No motion/clearance test has yet run; first-look visuals are the next review gate.']}
(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')

# First-look views of the exact reopened candidate, neutral workbench only.
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=True;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14)
scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
cd=bpy.data.cameras.new('Transition review camera');cam=bpy.data.objects.new(cd.name,cd);scene.collection.objects.link(cam);scene.camera=cam;cd.type='ORTHO'
views=[('full-three-quarter',(-3.8,-6.0,3.2),(0,-.08,.98),2.8),('full-side',(-7.5,-.2,1.4),(0,-.08,.98),2.65),('neck-breast-closeup',(-3.4,-5.0,2.05),(0,-.22,1.42),1.05)]
view_records=[]
for name,pos,target,scale in views:
    cam.location=Vector(pos);aim=Vector(target);cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=scale
    path=AUDIT/(name+'.png');scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
    view_records.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),'bytes':path.stat().st_size,'camera':{'position':pos,'target':target,'orthoScale':scale}})
receipt['views']=view_records;(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'native':artifact(NATIVE),'allowlist':sorted(ALLOW),'views':view_records},indent=2))
