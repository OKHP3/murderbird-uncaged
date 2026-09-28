"""Versioned isolated native cervical/breast construction proposal.

Authored native-world profiles; editable rigid meshes, never deforming skin.
All existing pivots, materials, guides and unrelated geometry are preserved.
This study is not selected in the application and performs no GLB export.
"""
from pathlib import Path
import argparse, hashlib, json, math, runpy, shutil, sys
import bpy
from mathutils import Matrix, Vector

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'assets/models/uncaged-alignment-v8/murderbird-alignment-v8.blend'
BASE_SHA='b12c442e2f517b676cdd1fae1612730cc0ba83251d34f363285b08f2cd482478'
HELPER=ROOT/'scripts/build-uncaged-alignment-v7.py'
POSES=ROOT/'assets/audit/neutral-runtime-clearance-poses-v1/pose-snapshot.json'
POSE_SHA='874396ede48a63d37d743a1a85ae885a10e614a4461f46c50f3a62744a9e2813'
C=Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)))
ALL_ERAS='maker,mechanic,builder'
# (world Z, front Y, rear Y, lateral radius). These are authored dimensions,
# not measurements recovered from the perspective references.
PROFILE=[(1.32,-.363,-.044,.184),(1.38,-.404,-.104,.175),
         (1.42,-.416,-.136,.163),(1.47,-.411,-.167,.145),
         (1.52,-.382,-.191,.127),(1.57,-.338,-.215,.106),
         (1.61,-.304,-.237,.087),(1.646,-.293,-.252,.072)]
REPLACE={'Cervical articulated inner guards',
         *(f'Throat formed lamina {i}' for i in range(1,7)),
         *(f'Cervical flank lamina {s} {i}' for s in (-1,1) for i in range(1,7))}
FRAME={'Bowed passive cervical fork','Bowed passive cervical fork.001'}


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def artifact(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
def converted(flat):return C.inverted()@Matrix([[flat[col*4+row] for col in range(4)] for row in range(4)])@C
def depth(o):return 0 if not o.parent else 1+depth(o.parent)
def smooth(t):return max(0,min(1,t))**2*(3-2*max(0,min(1,t)))

def sample(z,field):
    if z<=PROFILE[0][0]:return PROFILE[0][field]
    if z>=PROFILE[-1][0]:return PROFILE[-1][field]
    for i,(a,b) in enumerate(zip(PROFILE,PROFILE[1:])):
        if a[0]<=z<=b[0]:
            t=(z-a[0])/(b[0]-a[0]);dz=b[0]-a[0]
            ia=max(0,i-1);ib=min(len(PROFILE)-1,i+2)
            ma=(b[field]-PROFILE[ia][field])/(b[0]-PROFILE[ia][0])
            mb=(PROFILE[ib][field]-a[field])/(PROFILE[ib][0]-a[0])
            return ((2*t**3-3*t**2+1)*a[field]+(t**3-2*t**2+t)*dz*ma+
                    (-2*t**3+3*t**2)*b[field]+(t**3-t**2)*dz*mb)

def envelope(z,a,radial=0):
    front,rear,rx=(sample(z,k) for k in (1,2,3));cy=(front+rear)/2;ry=(rear-front)/2
    return Vector(((rx+radial)*math.sin(a),cy-(ry+radial)*math.cos(a),z))

def mesh_into(obj,verts,faces,solid=.006):
    inv=obj.matrix_world.inverted()
    old=obj.data
    data=bpy.data.meshes.new(obj.name+' cervical study mesh')
    data.from_pydata([inv@Vector(v) for v in verts],[],faces);data.update()
    for m in old.materials:data.materials.append(m)
    obj.data=data
    obj.modifiers.clear()
    if solid:
        m=obj.modifiers.new('Rigid formed wall','SOLIDIFY');m.thickness=solid;m.offset=-1
    bevel=obj.modifiers.new('Small formed edge','BEVEL');bevel.width=.0014;bevel.segments=2
    for f in data.polygons:f.use_smooth=True
    return obj

def patch(obj,top,bottom,centre,halfspan,radial=.008,pointed=.009,wall=.006):
    verts=[];faces=[];across=18;along=10
    for j in range(along+1):
        t=j/along
        for k in range(across+1):
            q=2*k/across-1
            z=top+(bottom-top)*t-pointed*(1-q*q)*t**3
            a=centre+halfspan*q*(1-.06*t)
            # Upper edge is nested; lower free lip stands proud of next course.
            off=radial+.010*smooth(t)+.004*(1-q*q)*math.sin(math.pi*t)
            verts.append(envelope(z,a,off))
    for j in range(along):
        for k in range(across):
            n=j*(across+1)+k;faces.append((n,n+across+1,n+across+2,n+1))
    return mesh_into(obj,verts,faces,wall)

def make(name,owner,template,region):
    o=bpy.data.objects.new(name,bpy.data.meshes.new(name+' mesh'))
    bpy.context.scene.collection.objects.link(o);o.parent=owner;o.matrix_world=owner.matrix_world.copy()
    for m in template.data.materials:o.data.materials.append(m)
    for k,v in template.items():o[k]=v
    o['region']=region;o['surfaceRole']='plate';o['exteriorEras']=ALL_ERAS
    o['constructionClass']='inherited-passive';o['proposal']=True
    return o

def set_pose(pose,pivots):
    rows={r['name']:r for r in pose['pivotMatrices'] if r.get('kind')!='mesh'}
    assert set(pivots)<=set(rows)
    for n in sorted(pivots,key=lambda n:depth(pivots[n])):
        pivots[n].matrix_world=converted(rows[n]['worldMatrix']);bpy.context.view_layer.update()
    err=max(abs(pivots[n].matrix_world[r][c]-converted(rows[n]['worldMatrix'])[r][c])
            for n in pivots for r in range(4) for c in range(4))
    assert err<2e-6
    return err

def render(native,variant,audit,pose_data,pose_ids):
    bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene
    scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading
    s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.52,.55,.57)
    s.show_shadows=True;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD'
    scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=1100
    scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
    scene.render.image_settings.color_mode='RGB'
    for o in bpy.data.objects:
        if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras',ALL_ERAS).split(',');o.hide_set(False)
    cd=bpy.data.cameras.new('Temporary cervical review camera');cam=bpy.data.objects.new(cd.name,cd)
    scene.collection.objects.link(cam);scene.camera=cam;cd.type='ORTHO'
    views=[('front',(0,-6,1.05),(0,-.1,.99),2.40),
           ('profile-left',(-6,-.10,1.0),(0,-.1,.99),2.40),
           ('profile-right',(6,-.10,1.0),(0,-.1,.99),2.40),
           ('three-quarter',(-4.25,-5.9,3.24),(0,-.10,.99),2.40),
           ('neck-profile',(-6,-.25,1.52),(0,-.25,1.52),.94),
           ('neck-three-quarter',(-4,-6,2),(0,-.23,1.47),1.10)]
    records=[]
    for name,pos,target,scale in views:
        cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
        cd.ortho_scale=scale;p=audit/f'{variant}-{name}.png';assert not p.exists()
        scene.render.filepath=str(p);bpy.ops.render.render(write_still=True)
        records.append({**artifact(p),'view':name,'variant':variant,'position':pos,'target':target,'orthoScale':scale})
    pivots={o.name:o for o in bpy.data.objects if o.type=='EMPTY'}
    for pid in pose_ids:
        pose=next(p for p in pose_data['poses'] if p['id']==pid);err=set_pose(pose,pivots)
        # Follow actual neck while keeping enough breast/head context for collisions.
        target=pivots['neck'].matrix_world.translation+Vector((0,-.10,.19))
        for name,offset in [('pose-profile',(-6,0,.05)),('pose-three-quarter',(-4,-6,1.3))]:
            cam.location=target+Vector(offset);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
            cd.ortho_scale=1.5;p=audit/f'{variant}-{pid}-{name}.png';assert not p.exists()
            scene.render.filepath=str(p);bpy.ops.render.render(write_still=True)
            records.append({**artifact(p),'view':name,'variant':variant,'poseId':pid,'poseError':err,
                            'position':list(cam.location),'target':list(target),'orthoScale':cd.ortho_scale})
    return records

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--attempt',default='01');args=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
    out=ROOT/'assets/models/uncaged-cervical-construction-study-v1'/f'attempt-{args.attempt}'
    audit=ROOT/'assets/audit/cervical-construction-study-v1'/f'attempt-{args.attempt}'
    assert not out.exists() and not audit.exists();out.mkdir(parents=True);audit.mkdir(parents=True)
    assert sha(BASE)==BASE_SHA and sha(POSES)==POSE_SHA
    assert sha(HELPER)=='39b6ee2285d8c49df3a902f8fac0a07589da3d41f48ae24df1e06515c839033a'
    shutil.copy2(__file__,audit/'executed-generator.py')
    h=runpy.run_path(str(HELPER),run_name='snapshot_helpers')
    bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']()
    material_signatures={m.name:h['material_signature'](m) for m in bpy.data.materials}
    assert len(before['empties'])==51 and len(before['meshes'])==699
    objs={o.name:o for o in bpy.data.objects};assert REPLACE|FRAME<=set(objs)
    neck=objs['neck'];assert abs(neck.matrix_world.translation.y+.1)<1e-7
    pose_data=json.loads(POSES.read_text());rest=next(p for p in pose_data['poses'] if p['id']=='inspection-open-0-separation-0')
    pivots={o.name:o for o in bpy.data.objects if o.type=='EMPTY'}
    rows={r['name']:r for r in rest['pivotMatrices'] if r.get('kind')!='mesh'}
    rest_err=max(abs(pivots[n].matrix_world[r][c]-converted(rows[n]['worldMatrix'])[r][c]) for n in pivots for r in range(4) for c in range(4))
    assert rest_err<2e-6
    # Six short courses wrap the actual curved throat/lateral envelope. Lower
    # neck runs end above the breast's highest lateral fixing stations.
    bands=[(1.640,1.596),(1.606,1.561),(1.571,1.525),(1.535,1.489),(1.499,1.452),(1.462,1.411)]
    for i,(top,bottom) in enumerate(bands,1):
        patch(objs[f'Throat formed lamina {i}'],top,bottom,0,.73,.009,.009)
        for side in (-1,1):
            patch(objs[f'Cervical flank lamina {side} {i}'],top-.004,bottom+.003,side*1.29,.59,.004,.006)
    # Open inner backing is a formed channel, not a closed organic tube.
    patch(objs['Cervical articulated inner guards'],1.639,1.414,0,1.87,-.015,0,.007)
    # Existing passive forks already terminate at the same real interfaces.
    # Ease only their middle path; preserve both endpoint neighborhoods.
    for n in FRAME:
        o=objs[n];inv=o.matrix_world.inverted()
        for v in o.data.vertices:
            p=o.matrix_world@v.co;t=(p.z-1.275)/(1.654-1.275)
            w=math.sin(math.pi*max(0,min(1,t)))**2
            p.y-=.020*w
            v.co=inv@p
        o.data.update()
    additions=[]
    # The upper chest port belongs to the independently opening breast cover.
    # Its upper free edge laps outside the moving cervical apron; it does not
    # bridge the two owners or replace the forks' load path.
    for name,angle,span in [('Upper breast cervical yoke front',0,.73),
                            ('Upper breast cervical yoke left',1.29,.57),
                            ('Upper breast cervical yoke right',-1.29,.57)]:
        o=make(name,objs['breastplate'],objs['Throat formed lamina 6'],'breast')
        patch(o,1.427,1.334,angle,span,.031,.012,.007)
        additions.append(name)
    after=h['scene_snapshot']();changed=sorted(REPLACE|FRAME)
    assert before['empties']==after['empties'] and before['curves']==after['curves']
    assert set(after['meshes'])==set(before['meshes'])|set(additions)
    assert all(before['meshes'][n]==after['meshes'][n] for n in set(before['meshes'])-set(changed))
    assert all({k:v for k,v in before['meshes'][n].items() if k not in ['mesh','modifiers']}==
               {k:v for k,v in after['meshes'][n].items() if k not in ['mesh','modifiers']} for n in changed)
    assert material_signatures=={m.name:h['material_signature'](m) for m in bpy.data.materials}
    native=out/'murderbird-cervical-construction-study-v1.blend'
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False)
    bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
    (audit/'preserved-scene-snapshot.json').write_text(json.dumps(after,indent=2)+'\n')
    receipt={'status':'neutral construction proposal; visual/clearance review pending','base':artifact(BASE),'native':artifact(native),
             'generator':artifact(audit/'executed-generator.py'),'poses':artifact(POSES),
             'replace':changed,'add':additions,'profileWorldStations':PROFILE,'bandsWorldStations':bands,
             'preservation':{'unrelated678MeshesExact':True,'all51PivotsExact':True,'all462GuidesExact':True,
                             'allMaterialsExact':True,'saveReloadSnapshotExact':True,'rawRestMatrixError':rest_err},
             'construction':{'sharedAllEras':True,'neckOwner':'neck','yokeOwner':'breastplate',
                 'forkEndpoints':'Existing native fork geometry retained, only midspan eased by at most20mm; no new joints.',
                 'plateOverlap':'Radial course lapping; independently owned cervical apron and chest yoke.',
                 'provenance':'Authored geometric reconstruction; controlling refs support curved armored neck, not exact hidden construction.'},
             'limits':['Discrete native pose review is not continuous collision proof.','No GLB export, app edit, WebGL/fallback change or publication.',
                       'No artistic acceptance or physical engineering claim.','Inherited guides remain preserved and do not regenerate replacement meshes.']}
    (audit/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    pose_ids=['maker-jaw-control','maker-neck-control','advanced-strike-peak','inspection-open-1-separation-0']
    receipt['views']=render(BASE,'before',audit,pose_data,[])+render(native,'after',audit,pose_data,pose_ids)
    assert sha(BASE)==BASE_SHA and sha(POSES)==POSE_SHA
    (audit/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    contract={'base':artifact(BASE),'study':artifact(native),'poses':artifact(POSES),
              'restPoseId':'inspection-open-0-separation-0','poseIds':[p['id'] for p in pose_data['poses']],
              'changedMeshes':changed+additions,'targetOwners':['neck','head','jaw','breastplate','body','left-mantle','right-mantle'],
              'outputDirectory':str((audit/'actual-runtime-clearance').relative_to(ROOT))}
    (audit/'clearance-contract.json').write_text(json.dumps(contract,indent=2)+'\n')
    print(json.dumps({'native':artifact(native),'replace':len(changed),'add':len(additions),'views':len(receipt['views'])}))
if __name__=='__main__':main()
