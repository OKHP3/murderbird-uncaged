"""Versioned curved mechanical neck envelope over V11 rest articulation.

All changes are reconstructed rigid exterior geometry. Historical sources and
rest joints remain unchanged; this is not a finished-art or clearance approval.
"""
from pathlib import Path
import bpy,bmesh,math,json,hashlib,runpy,shutil,sys,argparse
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--attempt',default='01');args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
BASE=ROOT/'assets/models/uncaged-silhouette-v11/attempt-05/murderbird-silhouette-v11.blend'
SHA='28cf0e70e46fca5ea07b1d583ad1ec6492201ed865a0858b1c1da4fc355f9c0f'
OUT=ROOT/f'assets/models/uncaged-cervical-envelope-v12/attempt-{args.attempt}'
AUDIT=ROOT/f'assets/audit/uncaged-cervical-envelope-v12/attempt-{args.attempt}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def art(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
assert sha(BASE)==SHA and not OUT.exists() and not AUDIT.exists()
OUT.mkdir(parents=True);AUDIT.mkdir(parents=True);shutil.copy2(__file__,AUDIT/'executed-generator.py')
h=runpy.run_path(str(ROOT/'scripts/build-uncaged-alignment-v7.py'),run_name='neck_envelope_helpers')
bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']()
# Native Z up, -Y forward. Authored silhouette stations, not recovered measures.
# One envelope carries the front throat, lateral windows and posterior guard.
PROFILE=[(1.15,-.385,.048,.234),(1.23,-.419,.017,.218),
 (1.31,-.436,-.032,.192),(1.39,-.420,-.108,.160),
 (1.47,-.385,-.150,.137),(1.55,-.347,-.155,.131),
 (1.63,-.326,-.133,.132),(1.71,-.328,-.115,.136)]
def sample(z,k):
    if z<=PROFILE[0][0]:return PROFILE[0][k]
    if z>=PROFILE[-1][0]:return PROFILE[-1][k]
    for i,(a,b) in enumerate(zip(PROFILE,PROFILE[1:])):
        if a[0]<=z<=b[0]:
            t=(z-a[0])/(b[0]-a[0]);d=b[0]-a[0];lo=PROFILE[max(i-1,0)];hi=PROFILE[min(i+2,len(PROFILE)-1)]
            ma=(b[k]-lo[k])/(b[0]-lo[0]);mb=(hi[k]-a[k])/(hi[0]-a[0])
            return (2*t**3-3*t*t+1)*a[k]+(t**3-2*t*t+t)*d*ma+(-2*t**3+3*t*t)*b[k]+(t**3-t*t)*d*mb
def point(z,a,off):
    front,rear,rx=[sample(z,k) for k in (1,2,3)]
    return Vector(((rx+off)*math.sin(a),(front+rear)/2-((rear-front)/2+off)*math.cos(a),z))
changed={}
def plate(name,top,bottom,centre,half,radial=.008,tip=.026,sweep=0,skew=0):
    obj=bpy.data.objects[name];verts=[];faces=[];rows=12;cols=12
    for j in range(rows+1):
        t=j/rows;e=t*t*(3-2*t)
        for k in range(cols+1):
            q=2*k/cols-1
            width=1-.26*e
            a=centre+half*q*width+sweep*e
            # Long diagonal sides and a formed lower tongue break the ring line.
            z=top+(bottom-top)*t-tip*(1-q*q)*e+skew*q
            off=radial+.008*e+.002*(1-q*q)*math.sin(math.pi*t)
            verts.append(obj.matrix_world.inverted()@point(z,a,off))
    for j in range(rows):
        for k in range(cols):
            n=j*(cols+1)+k;faces.append((n,n+cols+1,n+cols+2,n+1))
    data=bpy.data.meshes.new(name+' curved v12');data.from_pydata(verts,[],faces);data.update()
    for m in obj.data.materials:data.materials.append(m)
    old=obj.data;obj.data=data
    if not old.users:bpy.data.meshes.remove(old)
    obj.modifiers.clear();wall=obj.modifiers.new('Rigid formed sheet','SOLIDIFY');wall.thickness=.004;wall.offset=-1;wall.use_even_offset=True
    bevel=obj.modifiers.new('Formed edge','BEVEL');bevel.width=.001;bevel.segments=2
    for f in data.polygons:f.use_smooth=True
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    changed[name]={'owner':obj.parent.name,'top':top,'bottom':bottom,'centre':centre,'halfSpan':half,'wall':.004,'tip':tip,'sweep':sweep,'skew':skew}
# Six separate throat lames, long rather than encircling collars. Neighbouring
# lateral lames are offset; the back guard leaves a narrow equipment window.
courses=[(1.645,1.552),(1.574,1.481),(1.503,1.410),(1.432,1.339),(1.361,1.268),(1.290,1.197)]
for i,(top,bottom) in enumerate(courses,1):
    plate(f'Throat formed lamina {i}',top,bottom,0,.62,tip=.024,skew=.007*(-1)**i)
    for side in (-1,1):
        plate(f'Cervical flank lamina {side} {i}',top+.025,bottom+.028,side*1.38,.52,tip=.029,sweep=side*.07,skew=-side*.014)
# Reuse each editable posterior piece and its existing rigid owner. Five
# columns stagger their levels and have individually tapered lower tongues.
for course,(top,bottom) in enumerate([(1.705,1.601),(1.633,1.529),(1.561,1.457),(1.489,1.385),(1.417,1.313),(1.345,1.241)],1):
    for column,angle in enumerate([-2.02,-1.01,0,1.01,2.02],1):
        a=math.pi+angle*.55
        stagger=.018*(column%2)+.006*abs(column-3)
        plate(f'V11 posterior cervical lap {course} {column}',top+stagger,bottom+stagger,a,.34,tip=.038,sweep=(column-3)*.024,skew=(column-3)*.006)
for label,centre in [('front',0),('left',1.23),('right',-1.23)]:
    plate('Upper breast cervical yoke '+label,1.259,1.163,centre,.49,radial=.011,tip=.025)
after=h['scene_snapshot']()
assert before['empties']==after['empties'] and before['curves']==after['curves']
assert set(before['meshes'])==set(after['meshes'])
assert all(before['meshes'][n]==after['meshes'][n] for n in set(before['meshes'])-set(changed))
for n in changed:
    for k in ('parent','matrix','props','visibility'):assert before['meshes'][n][k]==after['meshes'][n][k],(n,k)
native=OUT/'murderbird-cervical-envelope-v12.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False)
bpy.ops.wm.open_mainfile(filepath=str(native));assert after==h['scene_snapshot']()
receipt={'status':'curved neck reconstruction proposal; not selected or approved','base':art(BASE),'native':art(native),'generator':art(AUDIT/'executed-generator.py'),'profile':PROFILE,'changed':changed,'preservation':{'pivotsExact':len(after['empties']),'otherMeshesExact':len(after['meshes'])-len(changed),'allGuidesExact':True,'editedPieceParentsMatricesMetadataExact':True,'saveReopenExact':True},'limits':['No owner acceptance or full movement clearance.','New profile and guard shapes are reconstructed; perspective source is not dimensional evidence.','Existing construction guides are historical and do not trace the new guard envelope.','No material finish, default model switch or publication.'],'views':[]}
(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
def render(path,label):
    bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=True;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14)
    scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
    for o in bpy.data.objects:
        o.hide_set(False)
        if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
    cd=bpy.data.cameras.new('Neck comparison camera');cam=bpy.data.objects.new(cd.name,cd);scene.collection.objects.link(cam);scene.camera=cam;cd.type='ORTHO'
    views=[('reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5),('profile',(-7.5,0,1.25),(0,-.08,1.02),2.5),('front',(0,-7,1.65),(0,-.08,1.02),2.5),('rear',(0,7,1.65),(0,-.08,1.02),2.5),('head',(-6,-3.5,2.45),(0,-.27,1.62),1.10)]
    for name,pos,target,scale in views:
        cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=scale;f=AUDIT/f'{label}-{name}.png';scene.render.filepath=str(f);bpy.ops.render.render(write_still=True);receipt['views'].append({**art(f),'label':label,'camera':{'position':pos,'target':target,'scale':scale},'lighting':'neutral Workbench; native rest geometry'})
render(native,'after');render(BASE,'before');(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');assert sha(BASE)==SHA
print(json.dumps(receipt['native']))
