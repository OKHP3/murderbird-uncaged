"""Versioned isolated native cervical/breast construction proposal.

Authored native-world profiles; editable rigid meshes, never deforming skin.
All existing pivots, materials, guides and unrelated geometry are preserved.
This study is not selected in the application and performs no GLB export.
"""
from pathlib import Path
import argparse, hashlib, json, math, runpy, shutil, sys
import bpy
from mathutils import Matrix, Vector, Euler
from mathutils.bvhtree import BVHTree

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
PROFILE=[(1.25,-.302,.092,.198),(1.28,-.331,.040,.194),(1.32,-.363,-.044,.184),(1.38,-.404,-.104,.175),
         (1.42,-.416,-.136,.163),(1.47,-.411,-.167,.145),
         (1.52,-.354,-.191,.116),(1.57,-.329,-.215,.102),
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

def patch(obj,top,bottom,centre,halfspan,radial=.008,pointed=.009,wall=.006,sweep=0,skew=0):
    verts=[];faces=[];across=18;along=10
    for j in range(along+1):
        t=j/along
        for k in range(across+1):
            q=2*k/across-1
            z=top+(bottom-top)*t-pointed*(1-q*q)*t**2+skew*q+.008*q*q*(1-t)
            a=centre+sweep*t+halfspan*q*(1-.38*smooth(t))
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

def curved_fork(obj, endpoints=None):
    """Paired rigid forged rails; endpoint neighbourhoods are inherited."""
    original=[obj.matrix_world@v.co for v in obj.data.vertices]
    low=min(p.z for p in original);high=max(p.z for p in original)
    bottom=sum((p for p in original if p.z<low+.012),Vector())/len([p for p in original if p.z<low+.012])
    top=sum((p for p in original if p.z>high-.012),Vector())/len([p for p in original if p.z>high-.012])
    if endpoints is not None:bottom,top=map(Vector,endpoints)
    sign=1 if top.x>0 else -1
    control_a=bottom+Vector((.040*sign,.025,.142))
    control_b=top+Vector((.046*sign,.055,-.120))
    verts=[];faces=[];rings=32;sides=12
    for j in range(rings+1):
        t=j/rings
        centre=(1-t)**3*bottom+3*(1-t)**2*t*control_a+3*(1-t)*t*t*control_b+t**3*top
        tangent=3*(1-t)**2*(control_a-bottom)+6*(1-t)*t*(control_b-control_a)+3*t*t*(top-control_b)
        normal=Vector((1,0,0));binormal=tangent.normalized().cross(normal).normalized()
        for k in range(sides):
            a=2*math.pi*k/sides;verts.append(centre+.012*math.cos(a)*normal+.013*math.sin(a)*binormal)
    for j in range(rings):
        for k in range(sides):
            n=j*sides+k;next_k=j*sides+(k+1)%sides
            faces.append((n,next_k,next_k+sides,n+sides))
    faces.append(tuple(reversed(range(sides))));faces.append(tuple(rings*sides+k for k in range(sides)))
    mesh_into(obj,verts,faces,0)
    return {'bottomInheritedCentre':list(bottom),'topInheritedCentre':list(top),'bezierControls':[list(control_a),list(control_b)]}

def swept_neck_keepout(pose_data):
    """Actual frozen pivot transforms, evaluated candidate neck meshes.

    Target surfaces are accumulated in saved breast-cover world space so the
    three independent yoke pieces can receive a conservative moving-neck notch.
    """
    bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
    subjects=[o for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name=='neck']
    breast=bpy.data.objects['breastplate'];rest_breast=breast.matrix_world.copy()
    rest_neck=bpy.data.objects['neck'].matrix_world.copy()
    points=[];faces=[]
    for pose in pose_data['poses']:
        rows={r['name']:r for r in pose['pivotMatrices'] if r.get('kind')!='mesh'}
        transform=rest_breast@converted(rows['breastplate']['worldMatrix']).inverted()@converted(rows['neck']['worldMatrix'])@rest_neck.inverted()
        for o in subjects:
            e=o.evaluated_get(deps);mesh=e.to_mesh();mesh.calc_loop_triangles();start=len(points)
            points.extend(transform@(e.matrix_world@v.co) for v in mesh.vertices)
            faces.extend(tuple(start+i for i in t.vertices) for t in mesh.loop_triangles)
            e.to_mesh_clear()
    return BVHTree.FromPolygons(points,faces,all_triangles=True),{'poseCount':len(pose_data['poses']),'surfaceTriangleCount':len(faces),'marginM':.012}

def yoke_point(z,a):
    # This section roots into the native upper breast, never a cylindrical cuff.
    t=max(0,min(1,(z-1.307)/.10))
    front=-.347-.060*smooth(t);rear=-.071-.057*t;rx=.18-.027*t
    return Vector((rx*math.sin(a),(front+rear)/2-(rear-front)/2*math.cos(a),z))

def rooted_yoke(obj,centre,span,keepout):
    across=24;along=10;angles=[centre+span*(2*k/across-1) for k in range(across+1)]
    tops=[]
    for a in angles:
        top=1.410
        for j in range(101):
            z=1.311+.001*j;p=yoke_point(z,a)
            near=keepout.find_nearest(p)
            if near[0] is not None and near[3]<.012:
                top=z-.014;break
        tops.append(max(1.325,top))
    # Conservative neighbouring minima smooth isolated keepout teeth.
    tops=[min(tops[max(0,k-2):min(across+1,k+3)]) for k in range(across+1)]
    verts=[];faces=[]
    for j in range(along+1):
        t=j/along
        for k,a in enumerate(angles):
            q=2*k/across-1;bottom=1.310-.012*(1-q*q)
            z=tops[k]*(1-t)+bottom*t
            p=yoke_point(z,a);p+=Vector((.004*math.sin(a),-.004*math.cos(a),0))
            verts.append(p)
    for j in range(along):
        for k in range(across):
            n=j*(across+1)+k;faces.append((n,n+across+1,n+across+2,n+1))
    mesh_into(obj,verts,faces,.005)
    return {'angles':angles,'upperEdgeZ':tops,'rootZ':1.310}

NEW_JOINT='cervical-upper'
MID_REST=Vector((0,-.235,1.452))
PITCH_LOWER=.35

def reparent_world(obj,parent):
    m=obj.matrix_world.copy();obj.parent=parent;obj.matrix_world=m;bpy.context.view_layer.update()

def bearing(name,owner,template,centre,rad,depth_m):
    o=make(name,owner,template,'neck');o['surfaceRole']='bearing'
    verts=[];faces=[];sides=32
    for x in (-depth_m/2,depth_m/2):
        for k in range(sides):
            a=2*math.pi*k/sides;verts.append(Vector(centre)+Vector((x,rad*math.cos(a),rad*math.sin(a))))
    for k in range(sides):faces.append((k,(k+1)%sides,(k+1)%sides+sides,k+sides))
    faces.extend([tuple(reversed(range(sides))),tuple(sides+k for k in range(sides))])
    mesh_into(o,verts,faces,0)
    return o

def two_stage_construct(objs,additions):
    neck=objs['neck'];head=objs['head'];old_head=head.matrix_world.copy()
    mid=bpy.data.objects.new(NEW_JOINT,None);bpy.context.scene.collection.objects.link(mid)
    mid.empty_display_type='ARROWS';mid.empty_display_size=.06;mid.parent=neck
    mid.matrix_world=Matrix.Translation(MID_REST);bpy.context.view_layer.update()
    reparent_world(head,mid)
    upper={*(f'Throat formed lamina {i}' for i in (1,2,3)),
           *(f'Cervical flank lamina {side} {i}' for side in (-1,1) for i in (1,2,3)),
           'Cervical articulated inner guards'}
    for n in sorted(upper):reparent_world(objs[n],mid)
    patch(objs['Cervical articulated inner guards'],1.635,1.465,0,2.72,-.025,0,.007)
    backing=make('Lower cervical open backing',neck,objs['Cervical articulated inner guards'],'neck')
    backing['surfaceRole']='frame';patch(backing,1.468,1.375,0,2.72,-.031,0,.007);additions.append(backing.name)
    rail_records={}
    # Existing base endpoints are retained, new intermediate bearings have an
    # explicit transverse X axis. The upper rails have independent rigid ownership.
    for side,name in [(-1,'Bowed passive cervical fork'),(1,'Bowed passive cervical fork.001')]:
        original=[objs[name].matrix_world@v.co for v in objs[name].data.vertices]
        low=min(p.z for p in original);high=max(p.z for p in original)
        bottom=sum((p for p in original if p.z<low+.014),Vector())/len([p for p in original if p.z<low+.014])
        top=sum((p for p in original if p.z>high-.014),Vector())/len([p for p in original if p.z>high-.014])
        middle=MID_REST+Vector((side*.105,0,0))
        rail_records[name]=curved_fork(objs[name],[bottom,middle])
        toprail=make(f'Upper cervical curved load rail {side}',mid,objs[name],'neck');toprail['surfaceRole']='frame'
        rail_records[toprail.name]=curved_fork(toprail,[middle,top]);additions.append(toprail.name)
        clevis=bearing(f'Cervical intermediate clevis {side}',neck,objs[name],MID_REST+Vector((side*.139,0,0)),.029,.024)
        pin=bearing(f'Cervical intermediate axle {side}',mid,objs[name],MID_REST+Vector((side*.153,0,0)),.018,.010)
        additions.extend([clevis.name,pin.name])
    assert max(abs(head.matrix_world[r][c]-old_head[r][c]) for r in range(4) for c in range(4))<1e-7
    return {'newPivot':NEW_JOINT,'parent':'neck','restWorldMatrix':[list(r) for r in mid.matrix_world],
            'restLocalMatrix':[list(r) for r in mid.matrix_local],'headReparentedWithRestWorldExact':True,
            'upperOwnedMeshes':sorted(upper)+[n for n in additions if 'Upper cervical' in n or 'axle' in n],
            'lowerNeckOwnedMeshes':sorted((REPLACE|FRAME)-upper)+[backing.name]+[n for n in additions if 'clevis' in n],
            'lowerPitchFraction':PITCH_LOWER,'upperPitchFraction':1-PITCH_LOWER,
            'pitchAxis':'Blender localX / browser localX','yawRollAllocation':'All retained at lower neck; upper adds localX pitch.',
            'rails':rail_records,'kinematicStatus':'Re-derived illustrative chain, not runtime contact solver or certified engineering.'}

def set_rederived_pose(pose,pivots):
    rows={r['name']:r for r in pose['pivotMatrices'] if r.get('kind')!='mesh'}
    originals=set(pivots)-{NEW_JOINT};assert originals<=set(rows)
    rest_mid=Matrix.Translation((0,-.135,.192))
    locals_by_name={n:converted(rows[n]['localMatrix']) for n in originals}
    original_pitch=locals_by_name['neck'].to_quaternion().to_euler('XYZ')
    new_neck=locals_by_name['neck'].copy();new_neck.translation=locals_by_name['neck'].translation
    e=Euler((original_pitch.x*PITCH_LOWER,original_pitch.y,original_pitch.z),'XYZ')
    new_neck=e.to_matrix().to_4x4();new_neck.translation=locals_by_name['neck'].translation
    upper=Euler((original_pitch.x*(1-PITCH_LOWER),0,0),'XYZ').to_matrix().to_4x4();upper.translation=rest_mid.translation
    for n in sorted(pivots,key=lambda n:depth(pivots[n])):
        if n=='neck':local=new_neck
        elif n==NEW_JOINT:local=upper
        elif n=='head':
            local=locals_by_name[n].copy();local.translation=Vector((0,-.100,.186))
        else:local=locals_by_name[n]
        pivots[n].matrix_world=(pivots[n].parent.matrix_world@local) if pivots[n].parent else local
        bpy.context.view_layer.update()
    old_head=converted(rows['head']['worldMatrix']);new_head=pivots['head'].matrix_world
    orientation_err=max(abs(new_head[r][c]-old_head[r][c]) for r in range(3) for c in range(3))
    # Local continuity survives; the old contact position deliberately does not.
    translation_delta=new_head.translation-old_head.translation
    return {'legacyNeckEulerXYZ':list(original_pitch),'lowerPitchRad':original_pitch.x*PITCH_LOWER,
            'upperPitchRad':original_pitch.x*(1-PITCH_LOWER),'headWorldTranslationDeltaM':list(translation_delta),
            'headWorldTranslationDeltaLengthM':translation_delta.length,'headWorldRotationMatrixDifference':orientation_err,
            'jointWorldMatrix':[list(r) for r in pivots[NEW_JOINT].matrix_world],
            'sourceWorldMatricesAppliedAsProof':False}

def set_pose(pose,pivots):
    rows={r['name']:r for r in pose['pivotMatrices'] if r.get('kind')!='mesh'}
    assert set(pivots)<=set(rows)
    for n in sorted(pivots,key=lambda n:depth(pivots[n])):
        pivots[n].matrix_world=converted(rows[n]['worldMatrix']);bpy.context.view_layer.update()
    err=max(abs(pivots[n].matrix_world[r][c]-converted(rows[n]['worldMatrix'])[r][c])
            for n in pivots for r in range(4) for c in range(4))
    assert err<2e-6
    return err

def render(native,variant,audit,pose_data,pose_ids,two_stage=False):
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
        pose=next(p for p in pose_data['poses'] if p['id']==pid);err=set_rederived_pose(pose,pivots) if two_stage else set_pose(pose,pivots)
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
    ap=argparse.ArgumentParser();ap.add_argument('--attempt',default='01');ap.add_argument('--two-stage',action='store_true');args=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
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
    # Six directional courses wrap the entire curved native neck and nest into
    # the breast. Clearance remains a separate measured gate; the prior
    # short-envelope attempt is preserved because its lower port failed likeness.
    bands=[(1.640,1.561),(1.574,1.495),(1.508,1.429),(1.442,1.361),(1.374,1.300),(1.313,1.267)]
    for i,(top,bottom) in enumerate(bands,1):
        patch(objs[f'Throat formed lamina {i}'],top,bottom,(-.035 if i%2 else .03),.72,.006,.015,sweep=(.03 if i%2 else -.035),skew=(.003 if i%2 else -.003))
        for side in (-1,1):
            patch(objs[f'Cervical flank lamina {side} {i}'],top+.006,bottom+.012,side*1.72,.91,.003,.014,sweep=side*.16,skew=side*.011)
    # Open inner backing is a formed channel, not a closed organic tube.
    patch(objs['Cervical articulated inner guards'],1.635,1.278,0,2.72,-.025,0,.007)
    fork_records={n:curved_fork(objs[n]) for n in sorted(FRAME)}
    keepout,keepout_receipt=swept_neck_keepout(pose_data)
    yoke_records={}
    additions=[]
    # The upper chest port belongs to the independently opening breast cover.
    # Its upper free edge laps outside the moving cervical apron; it does not
    # bridge the two owners or replace the forks' load path.
    for name,angle,span in [('Upper breast cervical yoke front',0,.73),
                            ('Upper breast cervical yoke left',1.36,.49),
                            ('Upper breast cervical yoke right',-1.36,.49)]:
        o=make(name,objs['breastplate'],objs['Throat formed lamina 6'],'breast')
        yoke_records[name]=rooted_yoke(o,angle,span,keepout)
        additions.append(name)
    joint_contract=two_stage_construct(objs,additions) if args.two_stage else None
    after=h['scene_snapshot']();changed=sorted(REPLACE|FRAME)
    if args.two_stage:
        assert set(after['empties'])==set(before['empties'])|{NEW_JOINT}
        assert all(after['empties'][n]==before['empties'][n] for n in set(before['empties'])-{'head'})
        assert after['empties']['head']['matrix']==before['empties']['head']['matrix']
    else:assert before['empties']==after['empties']
    assert before['curves']==after['curves']
    assert set(after['meshes'])==set(before['meshes'])|set(additions)
    assert all(before['meshes'][n]==after['meshes'][n] for n in set(before['meshes'])-set(changed))
    assert all({k:v for k,v in before['meshes'][n].items() if k not in (['mesh','modifiers','parent'] if args.two_stage else ['mesh','modifiers'])}==
               {k:v for k,v in after['meshes'][n].items() if k not in (['mesh','modifiers','parent'] if args.two_stage else ['mesh','modifiers'])} for n in changed)
    assert material_signatures=={m.name:h['material_signature'](m) for m in bpy.data.materials}
    native=out/'murderbird-cervical-construction-study-v1.blend'
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False)
    bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
    (audit/'preserved-scene-snapshot.json').write_text(json.dumps(after,indent=2)+'\n')
    receipt={'status':'neutral construction proposal; visual/clearance review pending','base':artifact(BASE),'native':artifact(native),
             'generator':artifact(audit/'executed-generator.py'),'poses':artifact(POSES),
             'replace':changed,'add':additions,'profileWorldStations':PROFILE,'bandsWorldStations':bands,'twoStageContract':joint_contract,
             'preservation':{'unrelated678MeshesExact':True,'originalPivotWorldMatricesExact':True,'originalPivotHierarchyExact':not args.two_stage,'nativePivotCount':len(after['empties']),'all462GuidesExact':True,
                             'allMaterialsExact':True,'saveReloadSnapshotExact':True,'rawRestMatrixError':rest_err},
             'construction':{'sharedAllEras':True,'neckOwner':'neck','yokeOwner':'breastplate',
                 'forkEndpoints':fork_records,'sampledYokeKeepout':keepout_receipt,'yokeEdges':yoke_records,
                 'plateOverlap':'Directional tapered rigid guards; yoke upper edges constrained by sampled candidate-neck surfaces in existing cover space.',
                 'provenance':'Authored geometric reconstruction; controlling refs support curved armored neck, not exact hidden construction.'},
             'limits':['Discrete native pose review is not continuous collision proof.','No GLB export, app edit, WebGL/fallback change or publication.',
                       'No artistic acceptance or physical engineering claim.','Inherited guides remain preserved and do not regenerate replacement meshes.']}
    (audit/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    pose_ids=['maker-jaw-control','maker-neck-control','advanced-strike-peak','inspection-open-1-separation-0']
    receipt['views']=render(BASE,'before',audit,pose_data,[])+render(native,'after',audit,pose_data,pose_ids,args.two_stage)
    assert sha(BASE)==BASE_SHA and sha(POSES)==POSE_SHA
    (audit/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    contract={'base':artifact(BASE),'study':artifact(native),'poses':artifact(POSES),
              'restPoseId':'inspection-open-0-separation-0','poseIds':[p['id'] for p in pose_data['poses']],
              'changedMeshes':changed+additions,'targetOwners':['neck','head','jaw','breastplate','body','left-mantle','right-mantle'],
              'outputDirectory':str((audit/'actual-runtime-clearance').relative_to(ROOT))}
    if not args.two_stage:(audit/'clearance-contract.json').write_text(json.dumps(contract,indent=2)+'\n')
    else:
        pose_rows=[]
        bpy.ops.wm.open_mainfile(filepath=str(native));pivots={o.name:o for o in bpy.data.objects if o.type=='EMPTY'}
        for pose in pose_data['poses']:
            derivation=set_rederived_pose(pose,pivots)
            pose_rows.append({'id':pose['id'],'derivation':derivation,'pivotMatrices':[{'name':n,'parent':o.parent.name if o.parent else None,'worldNative':[list(r) for r in o.matrix_world],'localNative':[list(r) for r in o.matrix_local]} for n,o in sorted(pivots.items())]})
        (audit/'rederived-pose-contract.json').write_text(json.dumps({'native':artifact(native),'legacyPoseSource':artifact(POSES),'sourceNative':artifact(BASE),'newNativePivotCount':52,'contract':joint_contract,'poses':pose_rows,'limits':['No old51world pose parity is claimed.','This is a fixed-length re-derived proposal; cage/bill contact solving is not recomputed.']},indent=2)+'\n')
    print(json.dumps({'native':artifact(native),'replace':len(changed),'add':len(additions),'views':len(receipt['views'])}))
if __name__=='__main__':main()
