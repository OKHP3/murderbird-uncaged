"""Versioned isolated cervical construction proposals from the pinned V8 native.

One-stage attempts preserve the51-pivot hierarchy. Two-stage attempts add the
cervical-upper pivot, reparent the head and named guards with original rest-world
transforms, and explicitly record the52-pivot contract. Diagnostic GLB export is
optional and always uses a reopened saved native. Read-only pose reviews never
save posed or visibility state. No app integration, base overwrite, or publication.
All attempts and executed generator/review snapshots are preserved independently.
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
    if endpoints is None:
        original=[obj.matrix_world@v.co for v in obj.data.vertices]
        low=min(p.z for p in original);high=max(p.z for p in original)
        bottom=sum((p for p in original if p.z<low+.012),Vector())/len([p for p in original if p.z<low+.012])
        top=sum((p for p in original if p.z>high-.012),Vector())/len([p for p in original if p.z>high-.012])
    else:bottom,top=map(Vector,endpoints)
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

def annular_bearing(obj,centre,outer=.030,inner=.020,depth_m=.036):
    sides=40;verts=[];faces=[]
    for x in (-depth_m/2,depth_m/2):
        for radius in (outer,inner):
            for k in range(sides):
                a=2*math.pi*k/sides;verts.append(Vector(centre)+Vector((x,radius*math.cos(a),radius*math.sin(a))))
    for k in range(sides):
        nxt=(k+1)%sides
        faces.extend([(k,nxt,2*sides+nxt,2*sides+k),
                      (sides+nxt,sides+k,3*sides+k,3*sides+nxt),
                      (nxt,k,sides+k,sides+nxt),
                      (2*sides+k,2*sides+nxt,3*sides+nxt,3*sides+k)])
    mesh_into(obj,verts,faces,0)

def joint_pocket_correction(objs,additions,contract):
    from mathutils.geometry import closest_point_on_tri
    breast=objs['breastplate'];neck=objs['neck'];upper=bpy.data.objects[NEW_JOINT]
    chest={*(f'Throat formed lamina {i}' for i in (5,6)),
           *(f'Cervical flank lamina {side} {i}' for side in (-1,1) for i in (5,6))}
    for n in sorted(chest):reparent_world(objs[n],breast);objs[n]['region']='breast'
    # Reuse the original rigid courses as shaped chest extensions, avoiding an
    # additional collar placed on top of them.
    for n in list(additions):
        if n.startswith('Upper breast cervical yoke'):
            bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True);additions.remove(n)
    for i in (4,5,6):
        top,bottom=[(1.442,1.361),(1.374,1.300),(1.313,1.267)][i-4]
        patch(objs[f'Throat formed lamina {i}'],top,bottom,(-.055 if i%2 else .04),.57,.005,.037,
              sweep=(.045 if i%2 else -.045),skew=(.004 if i%2 else -.004))
    patch(objs['Cervical articulated inner guards'],1.635,1.512,0,2.72,-.025,0,.007)
    patch(bpy.data.objects['Lower cervical open backing'],1.431,1.377,0,2.72,-.032,0,.007)
    changes=[]
    for n in [f'Throat formed lamina {i}' for i in (3,4)]+[f'Cervical flank lamina {side} {i}' for side in (-1,1) for i in (3,4)]:
        o=objs[n];inv=o.matrix_world.inverted();is_upper=o.parent==upper;world=[]
        for v in o.data.vertices:
            p=o.matrix_world@v.co;d=p-MID_REST;r=math.hypot(d.y,d.z)
            radius=.188*math.sqrt(max(.04,1-(abs(p.x)/.190)**2))+.014
            # Concentric formed overlap about the true X axle. Only the front
            # overlap arc is treated; the back receives a physical joint port.
            if d.y<-.025 and abs(d.z)<.100 and r>1e-7:
                desired=max(r,radius+.007) if is_upper else min(r,radius-.020)
                p.y=MID_REST.y+d.y*desired/r;p.z=MID_REST.z+d.z*desired/r
            world.append(p);v.co=inv@p
        faces=[];removed=0
        for face in o.data.polygons:
            points=[world[i] for i in face.vertices]
            # Aperture around the actual journals, including the moving pin.
            projected=[Vector((0,p.y,p.z)) for p in points]
            centre=Vector((0,MID_REST.y,MID_REST.z))
            dist=min((closest_point_on_tri(centre,projected[0],projected[k],projected[k+1])-centre).length for k in range(1,len(projected)-1))
            posterior= is_upper and max(p.y for p in points)>MID_REST.y-.023 and min(p.z for p in points)<MID_REST.z+.055
            hardware_port=abs(sum(p.x for p in points)/len(points))>.075 and dist<.042
            if posterior or hardware_port:removed+=1;continue
            faces.append(tuple(face.vertices))
        mesh_into(o,world,faces,.006);changes.append({'mesh':n,'removedPortFaces':removed,'remainingFaces':len(faces),'rigidOwner':o.parent.name})
    # Lower and upper forged rails occupy different axial X stations at the
    # bearing. A real annular lower race clears the separate rotating axle.
    for side,n in [(-1,'Bowed passive cervical fork'),(1,'Bowed passive cervical fork.001')]:
        bottom=contract['rails'][n]['bottomInheritedCentre']
        top_n=f'Upper cervical curved load rail {side}';top=contract['rails'][top_n]['topInheritedCentre']
        contract['rails'][n]=curved_fork(objs[n],[bottom,MID_REST+Vector((side*.118,0,0))])
        contract['rails'][top_n]=curved_fork(bpy.data.objects[top_n],[MID_REST+Vector((side*.091,0,0)),top])
        annular_bearing(bpy.data.objects[f'Cervical intermediate clevis {side}'],MID_REST+Vector((side*.128,0,0)))
        axle=bpy.data.objects[f'Cervical intermediate axle {side}'];centre=MID_REST+Vector((side*.124,0,0))
        # Replace the existing upper-owned axle with a continuous shaft through
        # the genuinely open bearing bore.
        temp=bearing('Temporary joint shaft',upper,axle,centre,.0175,.068)
        mesh_into(axle,[temp.matrix_world@v.co for v in temp.data.vertices],[tuple(f.vertices) for f in temp.data.polygons],0)
        bpy.data.objects.remove(temp,do_unlink=True)
    contract['breastCoverOwnedMeshes']=sorted(chest)
    contract['lowerNeckOwnedMeshes']=[n for n in contract['lowerNeckOwnedMeshes'] if n not in chest]
    contract['jointPocketConstruction']={'changes':changes,'journalOuterRadiusM':.030,'journalBoreRadiusM':.020,
                                        'rotatingAxleRadiusM':.0175,'nominalBoreRadialGapM':.0025,
                                        'upperOuterArc':'R(x)+7mm','lowerNestedArc':'R(x)-20mm','posteriorJointPort':True}
    return chest

def closed_sector(obj,centre,span,rx,radius,top,bottom,thickness=.006,skew=0,blend=None,lower_nested=False):
    """Explicit sealed circular-sector plate: no Boolean or discarded faces.

    Each X station follows a true circular YZ arc about the intermediate axle.
    Inner/outer walls and four edge returns form a closed rigid plate.
    """
    verts=[];faces=[];na=14;nt=8
    for layer in (0,1):
        for j in range(nt+1):
            t=j/nt
            for k in range(na+1):
                a=centre+span*(2*k/na-1);x=rx*math.sin(a)
                rr=(radius*math.sqrt(max(.16,1-(x/.135)**2)) if lower_nested else radius*math.cos(a))-layer*thickness
                phi=top+(bottom-top)*t+skew*math.sin(a)
                p=MID_REST+Vector((x,-rr*math.cos(phi),rr*math.sin(phi)))
                if blend:
                    z=blend[0]+(blend[1]-blend[0])*t+skew*.045*math.sin(a)
                    q=envelope(z,a,.009-layer*thickness)
                    w=smooth(t/.42) if blend[2]=='upper' else 1-smooth((t-.74)/.26)
                    p=q.lerp(p,w)
                verts.append(p)
    n=(na+1)*(nt+1)
    for j in range(nt):
        for k in range(na):
            q=j*(na+1)+k
            f=(q,q+na+1,q+na+2,q+1);faces.extend([f,tuple(n+i for i in reversed(f))])
    boundary=list(range(na+1))+[j*(na+1)+na for j in range(1,nt+1)]+[nt*(na+1)+k for k in range(na-1,-1,-1)]+[j*(na+1) for j in range(nt-1,0,-1)]
    for i,q in enumerate(boundary):
        r=boundary[(i+1)%len(boundary)];faces.append((q,r,r+n,q+n))
    mesh_into(obj,verts,faces,0)
    return {'mesh':obj.name,'owner':obj.parent.name,'xRadiusM':rx,'throatSectorRadiusM':radius,
            'topAngleRad':top,'bottomAngleRad':bottom,'closedWallM':thickness,'vertices':len(verts),'faces':len(faces)}

def merge_plate_parts(obj,parts):
    verts=[];faces=[]
    for p in parts:
        off=len(verts);verts.extend(p.matrix_world@v.co for v in p.data.vertices)
        faces.extend(tuple(off+i for i in f.vertices) for f in p.data.polygons)
    mesh_into(obj,verts,faces,0)
    for p in parts:bpy.data.objects.remove(p,do_unlink=True)

def directional_front_sector(obj,rx,r,top,bottom,blend,lower_nested=False):
    parts=[];records=[]
    for i,(centre,span) in enumerate([(-.49,.235),(0,.255),(.49,.235)]):
        temp=make(f'Temporary longitudinal front {i}',obj.parent,obj,'neck')
        records.append(closed_sector(temp,centre,span,rx,r+(i-1)*.002,top+[.075,-.065,.040][i],
                                     bottom+[.035,-.025,.050][i],skew=.17 if i!=1 else -.13,
                                     blend=blend,lower_nested=lower_nested));parts.append(temp)
    merge_plate_parts(obj,parts);return {'mesh':obj.name,'threeClosedLongitudinalPlates':records}

def directional_root_front(obj,top,bottom,radial):
    parts=[]
    for i,(centre,span) in enumerate([(-.48,.23),(0,.25),(.48,.23)]):
        temp=make(f'Temporary sternum front {i}',obj.parent,obj,'breast')
        patch(temp,top+[.003,.007,-.002][i],bottom+[.004,0,.006][i],centre,span,radial,.002,
              sweep=.02,skew=[.007,-.004,.007][i]);parts.append(temp)
    # These profile plates retain solid formed walls and closed returns from
    # evaluated solidification, rather than concatenating bare sheets.
    verts=[];faces=[];graph=bpy.context.evaluated_depsgraph_get()
    for p in parts:
        e=p.evaluated_get(graph);m=e.to_mesh();off=len(verts)
        verts.extend(e.matrix_world@v.co for v in m.vertices);faces.extend(tuple(off+i for i in f.vertices) for f in m.polygons);e.to_mesh_clear()
    mesh_into(obj,verts,faces,0)
    for p in parts:bpy.data.objects.remove(p,do_unlink=True)

def side_crescent(obj,side,x,outer,inner,start,end,wall=.006):
    verts=[];faces=[];na=16;nr=5
    for layer in (0,1):
        for j in range(nr+1):
            u=j/nr
            for k in range(na+1):
                t=k/na;phi=start+(end-start)*t
                rr=inner+(outer-inner)*u
                # Broad connected side guard with a gentle compound dish,
                # complete annular lower boundary and thick formed returns.
                xx=side*(x+.008*math.sin(math.pi*t)*u-layer*wall)
                verts.append(MID_REST+Vector((xx,-rr*math.cos(phi),rr*math.sin(phi))))
    n=(na+1)*(nr+1)
    for j in range(nr):
        for k in range(na):
            q=j*(na+1)+k;f=(q,q+na+1,q+na+2,q+1)
            faces.extend([f,tuple(n+i for i in reversed(f))])
    b=list(range(na+1))+[j*(na+1)+na for j in range(1,nr+1)]+[nr*(na+1)+k for k in range(na-1,-1,-1)]+[j*(na+1) for j in range(nr-1,0,-1)]
    for i,q in enumerate(b):r=b[(i+1)%len(b)];faces.append((q,r,r+n,q+n))
    mesh_into(obj,verts,faces,0)
    return {'mesh':obj.name,'owner':obj.parent.name,'outerRadiusM':outer,'innerRadiusM':inner,
            'startAngleRad':start,'endAngleRad':end,'sideXStationM':side*x,'wallM':wall}

def root_seated_plate(obj,side=None,course=5):
    """Body-fixed guard nested inside the moving lower neck about its base axis."""
    parts=[];na=12;nt=7
    intervals=[(-.49,.235),(0,.255),(.49,.235)] if side is None else [(side*1.00,.29)]
    for i,(centre,span) in enumerate(intervals):
        verts=[];faces=[]
        for layer in (0,1):
            for j in range(nt+1):
                t=j/nt
                for k in range(na+1):
                    a=centre+span*(2*k/na-1);x=.195*math.sin(a)
                    r=.263-.050*math.sin(a)**2-layer*.005
                    top=(1.424 if course==5 else 1.401)-.008*math.sin(a)**2
                    bottom=(1.383 if course==5 else 1.378)+.002*math.sin(a)**2
                    z=top+(bottom-top)*t+.003*math.sin(a)*(1-t)
                    dy=math.sqrt(max(.001,r*r-(z-1.260)**2))
                    verts.append(Vector((x,-.100-dy,z)))
        n=(na+1)*(nt+1)
        for j in range(nt):
            for k in range(na):
                q=j*(na+1)+k;f=(q,q+na+1,q+na+2,q+1);faces.extend([f,tuple(n+i for i in reversed(f))])
        b=list(range(na+1))+[j*(na+1)+na for j in range(1,nt+1)]+[nt*(na+1)+k for k in range(na-1,-1,-1)]+[j*(na+1) for j in range(nt-1,0,-1)]
        for k,q in enumerate(b):r=b[(k+1)%len(b)];faces.append((q,r,r+n,q+n))
        temp=make(f'Temporary rooted plate {i}',obj.parent,obj,'breast');mesh_into(temp,verts,faces,0);parts.append(temp)
    merge_plate_parts(obj,parts)

def closed_loft(obj,grid,na,nt,wall=.006):
    verts=list(grid);faces=[];n=len(grid)
    for j in range(nt+1):
        for k in range(na+1):
            q=j*(na+1)+k
            across=grid[j*(na+1)+min(na,k+1)]-grid[j*(na+1)+max(0,k-1)]
            along=grid[min(nt,j+1)*(na+1)+k]-grid[max(0,j-1)*(na+1)+k]
            normal=along.cross(across).normalized()
            verts.append(grid[q]-wall*normal)
    for j in range(nt):
        for k in range(na):
            q=j*(na+1)+k;f=(q,q+na+1,q+na+2,q+1);faces.extend([f,tuple(n+i for i in reversed(f))])
    b=list(range(na+1))+[j*(na+1)+na for j in range(1,nt+1)]+[nt*(na+1)+k for k in range(na-1,-1,-1)]+[j*(na+1) for j in range(nt-1,0,-1)]
    for k,q in enumerate(b):r=b[(k+1)%len(b)];faces.append((q,r,r+n,q+n))
    mesh_into(obj,verts,faces,0)

def full_lateral_guard(obj,side,upper):
    na=18;nt=10;grid=[]
    for j in range(nt+1):
        t=j/nt
        for k in range(na+1):
            a=.67+(2.61-.67 if upper else 1.93-.67)*k/na
            if upper:
                top=envelope(1.518+.008*math.sin(a),side*a,.008)
                rear=smooth((a-1.63)/.98)
                x=sample(1.46,3)*math.sin(a)
                r=.163*(1-rear)+.046*rear;phi=-.105+2.15*rear
                bottom=MID_REST+Vector((side*x,-r*math.cos(phi),r*math.sin(phi)))
                p=top.lerp(bottom,smooth(t))
                # Keep the entire anterior lap outside the nested lower guard.
                if a<1.65 and t>.40:
                    d=p-MID_REST;rr=math.hypot(d.y,d.z)
                    if rr<.150:p.y=MID_REST.y+d.y*.150/rr;p.z=MID_REST.z+d.z*.150/rr
            else:
                x=.172*math.sin(a);r=.119-.046*smooth((a-1.20)/.73)
                phi=.33+.10*math.sin(a)
                top=MID_REST+Vector((side*x,-r*math.cos(phi),r*math.sin(phi)))
                bottom=envelope(1.371+.015*math.sin(a),side*a,-.022)
                p=top.lerp(bottom,t)
            grid.append(p)
    closed_loft(obj,grid,na,nt)
    return {'mesh':obj.name,'owner':obj.parent.name,'completeProfileLoft':True,'angularSpanRad':[.67,2.61 if upper else 1.93],
            'wallM':.006,'vertices':2*len(grid),'upperRearJournalTerminationRadiusM':.046 if upper else None}

def coherent_transition_correction(objs,additions,contract,full_lateral=False):
    # Begin from09's deliberate rigid joint and real bearing construction;
    # replace the visible middle/root arrangement as whole designed surfaces.
    chest=clean_section_correction(objs,additions,contract)
    for n in chest:reparent_world(objs[n],objs['body'])
    records=[]
    for i,rx,r,top,bottom in [(3,.132,.170,.35,-.080),(4,.128,.124,.23,-.65)]:
        records.append(directional_front_sector(objs[f'Throat formed lamina {i}'],rx,r,top,bottom,None))
        for side in (-1,1):
            if full_lateral:records.append(full_lateral_guard(objs[f'Cervical flank lamina {side} {i}'],side,i==3))
            else:records.append(side_crescent(objs[f'Cervical flank lamina {side} {i}'],side,
                    .187 if i==3 else .168,.178 if i==3 else .139,.069 if i==3 else .056,
                    -.12 if i==3 else -.72,1.13 if i==3 else .33))
    for i in (5,6):
        root_seated_plate(objs[f'Throat formed lamina {i}'],course=i)
        for side in (-1,1):root_seated_plate(objs[f'Cervical flank lamina {side} {i}'],side,i)
    contract['bodySternumOwnedMeshes']=sorted(chest);contract['breastCoverOwnedMeshes']=[]
    contract['jointPocketConstruction']['coherentGuardSections']=records
    contract['sternumAccessSeam']={'rootedGuardMinimumZProposalM':1.378,'breastCoverMaximumInspectionZObservedM':1.371,
        'baseAxis':list(objs['neck'].matrix_world.translation),'bodyGuardBaseRadiusRangeM':[.213,.263],
        'status':'Discrete actual21-pose clearance pending; body mounting attachment still requires explicit bracket design'}
    return chest

def clean_section_correction(objs,additions,contract,designed=False):
    breast=objs['breastplate'];neck=objs['neck'];upper=bpy.data.objects[NEW_JOINT]
    chest={*(f'Throat formed lamina {i}' for i in (5,6)),
           *(f'Cervical flank lamina {side} {i}' for side in (-1,1) for i in (5,6))}
    for n in sorted(chest):reparent_world(objs[n],objs['body'] if designed else breast);objs[n]['region']='breast'
    for n in list(additions):
        if n.startswith('Upper breast cervical yoke'):
            bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True);additions.remove(n)
    sections=[]
    for i,r,rx,top,bottom in ([(3,.187,.196,.34,-.070),(4,.147,.183,.25,-.73)] if designed else [(3,.187,.196,.34,-.070),(4,.161,.183,.25,-.73)]):
        blend=([1.508,1.432,'upper'] if i==3 else [1.480,1.351,'lower']) if designed else None
        if designed:sections.append(directional_front_sector(objs[f'Throat formed lamina {i}'],rx,r,top,bottom,blend,lower_nested=i==4))
        else:sections.append(closed_sector(objs[f'Throat formed lamina {i}'],0,.77,rx,r,top,bottom,skew=.020))
        for side in (-1,1):
            # Short deliberately ended cheeks expose the journal without a
            # clipped hole. Their rear ends retain a complete thick return.
            sections.append(closed_sector(objs[f'Cervical flank lamina {side} {i}'],side*.995,.365,
                                           rx,r,top+.18,bottom+.10,skew=side*.030,blend=blend,lower_nested=designed and i==4))
    # Low cover pieces are explicit shallow chest extensions. They do not wrap
    # behind the independently moving fork and they preserve the front mass.
    for i,top,bottom,off in ([(5,1.433,1.380,.006),(6,1.406,1.377,.002)] if designed else [(5,1.365,1.299,.050),(6,1.314,1.258,.040)]):
        if designed:directional_root_front(objs[f'Throat formed lamina {i}'],top,bottom,off)
        else:patch(objs[f'Throat formed lamina {i}'],top,bottom,(-.02 if i==5 else .025),.66,off,.014,
                   sweep=(.035 if i==5 else -.025),skew=.002)
        for side in (-1,1):
            patch(objs[f'Cervical flank lamina {side} {i}'],top-.006,bottom+.009,side*1.01,.34,off+.002,.004 if designed else .011,
                  sweep=side*.045,skew=side*.003)
    patch(objs['Cervical articulated inner guards'],1.635,1.525,0,2.72,-.025,0,.007)
    patch(bpy.data.objects['Lower cervical open backing'],1.420,1.368,0,.93,-.032,0,.007)
    for side,n in [(-1,'Bowed passive cervical fork'),(1,'Bowed passive cervical fork.001')]:
        bottom=contract['rails'][n]['bottomInheritedCentre']
        top_n=f'Upper cervical curved load rail {side}';top=contract['rails'][top_n]['topInheritedCentre']
        # The lower fork terminates at the race rim, clear of its true bore;
        # the upper rail joins the axle at a separate inboard X station.
        contract['rails'][n]=curved_fork(objs[n],[bottom,MID_REST+Vector((side*.128,0,-.036))])
        contract['rails'][top_n]=curved_fork(bpy.data.objects[top_n],[MID_REST+Vector((side*.078,0,0)),top])
        annular_bearing(bpy.data.objects[f'Cervical intermediate clevis {side}'],MID_REST+Vector((side*.128,0,0)))
        axle=bpy.data.objects[f'Cervical intermediate axle {side}'];centre=MID_REST+Vector((side*.116,0,0))
        temp=bearing('Temporary joint shaft',upper,axle,centre,.0175,.084)
        mesh_into(axle,[temp.matrix_world@v.co for v in temp.data.vertices],[tuple(f.vertices) for f in temp.data.polygons],0)
        bpy.data.objects.remove(temp,do_unlink=True)
    contract['breastCoverOwnedMeshes']=sorted(chest)
    if designed:
        contract['bodySternumOwnedMeshes']=sorted(chest);contract['breastCoverOwnedMeshes']=[]
        contract['sternumAccessSeam']={'guardMinimumZProposalM':1.375,'measuredCoverMaximumNativeZAcrossActualInspectionSamplesM':1.371,
                'status':'Discrete geometry clearance pending; intended narrow upper access seam, not clearance proof'}
    contract['lowerNeckOwnedMeshes']=[n for n in contract['lowerNeckOwnedMeshes'] if n not in chest]
    contract['jointPocketConstruction']={'method':'Explicit closed circular sectors with complete edge returns; no discarded faces',
        'sections':sections,'journalOuterRadiusM':.030,'journalBoreRadiusM':.020,'rotatingAxleRadiusM':.0175,
        'nominalBoreRadialGapM':.0025,'throatNominalOuterRadiusGapM':.026,
        'lowerForkRaceAttachment':'Race lower rim, 36mm below axle, not inside the bore',
        'status':'Construction proposal; all pose and visual clearance gates remain open'}
    return chest

def set_rederived_pose(pose,pivots):
    rows={r['name']:r for r in pose['pivotMatrices'] if r.get('kind')!='mesh'}
    originals=set(pivots)-{NEW_JOINT};assert originals<=set(rows)
    rest_mid=Matrix.Translation((0,-.135,.192))
    world_by_name={n:converted(rows[n]['worldMatrix']) for n in originals}
    # Runtime Scene owns translation/yaw outside the native root; derive each
    # native-parent local from packet world matrices instead of discarding it.
    locals_by_name={n:(world_by_name[pivots[n].parent.name].inverted()@world_by_name[n])
                    if pivots[n].parent and pivots[n].parent.name in originals
                    else world_by_name[n].copy() for n in originals}
    # Head's source parent was neck, before the added intermediate joint.
    locals_by_name['head']=world_by_name['neck'].inverted()@world_by_name['head']
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
            'sourceWorldMatricesAppliedAsProof':False,'rootWorldMatrixFromRuntimeSceneRetained':True}

def set_pose(pose,pivots):
    rows={r['name']:r for r in pose['pivotMatrices'] if r.get('kind')!='mesh'}
    assert set(pivots)<=set(rows)
    for n in sorted(pivots,key=lambda n:depth(pivots[n])):
        pivots[n].matrix_world=converted(rows[n]['worldMatrix']);bpy.context.view_layer.update()
    err=max(abs(pivots[n].matrix_world[r][c]-converted(rows[n]['worldMatrix'])[r][c])
            for n in pivots for r in range(4) for c in range(4))
    assert err<2e-6
    return err

def render(native,variant,audit,pose_data,pose_ids,two_stage=False,neutral=True):
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
    for name,pos,target,scale in (views if neutral else []):
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

def review_existing(attempt,pose_packet=None,render_actual=False):
    audit=ROOT/'assets/audit/cervical-construction-study-v1'/f'attempt-{attempt}'
    receipt=json.loads((audit/'receipt.json').read_text());native=ROOT/receipt['native']['path']
    packet=ROOT/pose_packet if pose_packet else POSES
    packet_sha=sha(packet)
    assert sha(native)==receipt['native']['sha256']
    if not pose_packet:assert packet_sha==POSE_SHA
    out=audit/('actual-runtime-joint-clearance-v1' if pose_packet else 'joint-clearance-v1');assert not out.exists();out.mkdir()
    shutil.copy2(__file__,out/'executed-review.py')
    h=runpy.run_path(str(ROOT/'scripts/diagnose-native-regional-clearance.py'),run_name='diagnostic_helpers')
    bpy.ops.wm.open_mainfile(filepath=str(native));pivots={o.name:o for o in bpy.data.objects if o.type=='EMPTY'}
    assert len(pivots)==52
    meshes={o.name:o for o in bpy.data.objects if o.type=='MESH'}
    subjects=[o for o in meshes.values() if o.parent and (o.parent.name in ['neck',NEW_JOINT] or o.name in REPLACE) and o.get('surfaceRole') in ['plate','frame']]
    targets=[o for o in meshes.values() if o.parent and o.parent.name in ['neck',NEW_JOINT,'breastplate','head','jaw','body','left-mantle','right-mantle']]
    pose_data=json.loads(packet.read_text());rows=[]
    if pose_packet:
        source_native=ROOT/pose_data['model']['path'].replace('.glb','.blend')
        bpy.ops.wm.open_mainfile(filepath=str(source_native));source_pivots={o.name:o.matrix_world.copy() for o in bpy.data.objects if o.type=='EMPTY'}
        bpy.ops.wm.open_mainfile(filepath=str(native));pivots={o.name:o for o in bpy.data.objects if o.type=='EMPTY'}
        assert set(source_pivots)==set(pivots) and max(abs(source_pivots[n][r][c]-pivots[n].matrix_world[r][c]) for n in pivots for r in range(4) for c in range(4))<2e-7
        meshes={o.name:o for o in bpy.data.objects if o.type=='MESH'}
        subjects=[o for o in meshes.values() if o.parent and (o.parent.name in ['neck',NEW_JOINT] or o.name in REPLACE) and o.get('surfaceRole') in ['plate','frame']]
        targets=[o for o in meshes.values() if o.parent and o.parent.name in ['neck',NEW_JOINT,'breastplate','head','jaw','body','left-mantle','right-mantle']]
    rest_matrices={n:o.matrix_world.copy() for n,o in meshes.items()}
    for pose in pose_data['poses']:
        if pose_packet:
            err=set_pose(pose,pivots);transforms={r['name']:r for r in pose['pivotMatrices'] if r.get('kind')!='mesh'}
            derivation={'actualWorldMatrixMaxError':err,'native52PivotMatricesApplied':True,'lowerPitchRad':converted(transforms['neck']['localMatrix']).to_quaternion().to_euler('XYZ').x,'upperPitchRad':converted(transforms[NEW_JOINT]['localMatrix']).to_quaternion().to_euler('XYZ').x,'headWorldTranslationDeltaLengthM':None,'packetModelSha256':pose_data['model']['sha256']}
        else:derivation=set_rederived_pose(pose,pivots)
        graph=bpy.context.evaluated_depsgraph_get()
        surfaces={o.name:h['surface'](o,graph) for o in set(subjects+targets)}
        considered=set();hits=[]
        for subject in subjects:
            for target in targets:
                if subject==target or subject.parent==target.parent:continue
                key=tuple(sorted([subject.name,target.name]))
                if key in considered:continue
                considered.add(key);a=surfaces[subject.name];b=surfaces[target.name]
                if not a or not b or not h['bounds_overlap'](a,b):continue
                overlaps=a['tree'].overlap(b['tree'])
                if overlaps:
                    internal={subject.parent.name,target.parent.name}=={'neck',NEW_JOINT}
                    proofs=proper_crossing_receipt(a,b,overlaps,rest_matrices[subject.name]@subject.matrix_world.inverted(),
                                                  rest_matrices[target.name]@target.matrix_world.inverted())
                    hits.append({'subject':subject.name,'target':target.name,'subjectOwner':subject.parent.name,
                                 'targetOwner':target.parent.name,'intermediateJointPair':internal,
                                 'triangleOverlapCandidates':len(overlaps),
                                 'properFaceCrossing':proofs,
                                 'example':{'subjectTriangle':h['centroid'](a,overlaps[0][0]),'targetTriangle':h['centroid'](b,overlaps[0][1])}})
        mid_local=pivots[NEW_JOINT].matrix_local.translation;head_local=pivots['head'].matrix_local.translation
        rows.append({'poseId':pose['id'],'derivation':derivation,'fixedLengthLowerM':mid_local.length,
                     'fixedLengthUpperToHeadM':head_local.length,'pairsWithOverlapCandidates':hits})
    result={'status':'Actual52 runtime poses replayed on same-rest52 candidate native; discrete surface diagnostic' if pose_packet else 'Discrete re-derived52-pivot native guard diagnostic; not continuous clearance or runtime proof',
            'native':artifact(native),'posePacket':artifact(packet),'actual52RuntimePacket':bool(pose_packet),'rows':rows,
            'subjects':[o.name for o in subjects],'targetMeshCount':len(targets),
            'limits':(['Runtime packet was captured with attempt07 geometry; candidate08 uses the identical52 rest hierarchy.','No candidate08 controller/contact recapture is claimed.'] if pose_packet else ['Old51world transforms were not applied to the changed hierarchy.','Re-derived staged contact does not solve the new bill target.'])+[
                      'BVH surface candidates require visual or proper-crossing review.','No full containment or continuous sweep proof.','No native save was performed.']}
    (out/'guard-clearance-native.json').write_text(json.dumps(result,indent=2)+'\n')
    summary=[{'poseId':r['poseId'],'internalJointGuardCandidatePairs':sum(p['intermediateJointPair'] for p in r['pairsWithOverlapCandidates']),
              'externalCandidatePairs':sum(not p['intermediateJointPair'] for p in r['pairsWithOverlapCandidates']),
              'headDeltaMm':None if pose_packet else round(r['derivation']['headWorldTranslationDeltaLengthM']*1000,4),
              'lowerPitchDeg':round(math.degrees(r['derivation']['lowerPitchRad']),3),
              'upperPitchDeg':round(math.degrees(r['derivation']['upperPitchRad']),3)} for r in rows]
    (out/'summary.json').write_text(json.dumps({'native':artifact(native),'poses':summary,
             'lowerFixedLengthRangeM':[min(r['fixedLengthLowerM'] for r in rows),max(r['fixedLengthLowerM'] for r in rows)],
             'upperFixedLengthRangeM':[min(r['fixedLengthUpperToHeadM'] for r in rows),max(r['fixedLengthUpperToHeadM'] for r in rows)]},indent=2)+'\n')
    if render_actual:
        assert pose_packet
        ids=['advanced-contact','maker-neck-and-jaw-combined','inspection-open-0.25-separation-0',
             'inspection-open-0.5-separation-0','inspection-open-0.75-separation-0']
        records=render(native,'actual52',out,pose_data,ids,neutral=False)
        (out/'render-receipt.json').write_text(json.dumps({'native':artifact(native),'posePacket':artifact(packet),
                  'views':records,'status':'Actual52 same-rest runtime pose replay; no native save'},indent=2)+'\n')
    assert sha(native)==receipt['native']['sha256'] and sha(packet)==packet_sha;print(json.dumps(summary))

def proper_crossing_receipt(a,b,pairs,to_rest_a,to_rest_b):
    from mathutils.geometry import intersect_ray_tri
    confirmed=[];ids_a=set();ids_b=set();pts_a=[];pts_b=[]
    def edge_crosses(tri,other):
        normal=(other[1]-other[0]).cross(other[2]-other[0])
        if normal.length<1e-12:return False
        normal.normalize()
        for i in range(3):
            p=tri[i];q=tri[(i+1)%3];d0=normal.dot(p-other[0]);d1=normal.dot(q-other[0])
            if not (d0*d1<0 and abs(d0)>1e-7 and abs(d1)>1e-7):continue
            hit=intersect_ray_tri(*other,q-p,p,True)
            if hit is not None:
                t=(hit-p).dot(q-p)/(q-p).length_squared
                if 1e-6<t<1-1e-6:return True
        return False
    for ia,ib in pairs:
        ta=[a['points'][v] for v in a['faces'][ia]];tb=[b['points'][v] for v in b['faces'][ib]]
        if edge_crosses(ta,tb) or edge_crosses(tb,ta):
            ids_a.add(ia);ids_b.add(ib);pts_a.extend(to_rest_a@v for v in ta);pts_b.extend(to_rest_b@v for v in tb)
            if len(confirmed)<8:confirmed.append({'subjectEvaluatedTriangle':ia,'targetEvaluatedTriangle':ib,
                        'subjectRestWorldNativeXYZ':[[round(x,7) for x in to_rest_a@v] for v in ta],
                        'targetRestWorldNativeXYZ':[[round(x,7) for x in to_rest_b@v] for v in tb]})
    bounds=lambda pts:[[round(min(p[k] for p in pts),7),round(max(p[k] for p in pts),7)] for k in range(3)] if pts else None
    return {'method':'Strict noncoplanar edge-through-face tests on evaluated triangles; tangent/coplanar contacts excluded',
            'confirmedSubjectTriangleCount':len(ids_a),'confirmedTargetTriangleCount':len(ids_b),
            'subjectEvaluatedTriangleIndices':sorted(ids_a),'targetEvaluatedTriangleIndices':sorted(ids_b),
            'subjectCrossingRestWorldBoundsNativeXYZ':bounds(pts_a),'targetCrossingRestWorldBoundsNativeXYZ':bounds(pts_b),
            'examples':confirmed,'limits':'Surface penetration evidence only; no containment depth or continuous sweep proof.'}

def mount_proposal_review(attempt,packet_path,outboard=False,lower_anterior=False):
    audit=ROOT/'assets/audit/cervical-construction-study-v1'/f'attempt-{attempt}'
    receipt=json.loads((audit/'receipt.json').read_text());native=ROOT/receipt['native']['path'];packet=ROOT/packet_path
    assert sha(native)==receipt['native']['sha256']
    out=audit/('control-mount-proposal-v3' if lower_anterior else 'control-mount-proposal-v2' if outboard else 'control-mount-proposal-v1');assert not out.exists();out.mkdir()
    shutil.copy2(__file__,out/'executed-review.py')
    h=runpy.run_path(str(ROOT/'scripts/diagnose-native-regional-clearance.py'),run_name='diagnostic_helpers')
    bpy.ops.wm.open_mainfile(filepath=str(native));pivots={o.name:o for o in bpy.data.objects if o.type=='EMPTY'};assert len(pivots)==52
    proposals={'upper-horn-tip':{'owner':NEW_JOINT,'localNativeXYZ':[-.232,-.060,.015]},
               'lower-drive-anchor':{'owner':'neck','localNativeXYZ':[-.235,-.005,.100]},
               'maker-outboard-line-guide':{'owner':'neck','localNativeXYZ':[-.250,.020,.120]}}
    if outboard:
        proposals['upper-horn-tip']['localNativeXYZ']=[-.255,-.060,.015]
        proposals['lower-drive-anchor']['localNativeXYZ']=[-.275,.010,.160]
        proposals['maker-outboard-line-guide']['localNativeXYZ']=[-.270,.035,.170]
    if lower_anterior:
        assert outboard
        proposals['lower-drive-anchor']['localNativeXYZ']=[-.280,-.110,.025]
    for row in proposals.values():
        row['localBrowserXYZ']=[row['localNativeXYZ'][0],row['localNativeXYZ'][2],-row['localNativeXYZ'][1]]
        row['restWorldNativeXYZ']=list(pivots[row['owner']].matrix_world@Vector(row['localNativeXYZ']))
        row['proposedMountNeighborhoodHalfExtentM']=[.012,.012,.012]
    targets=[o for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name in
             ['neck',NEW_JOINT,'breastplate','head','jaw','body','left-mantle','right-mantle']
             and o.get('surfaceRole')=='plate']
    pose_data=json.loads(packet.read_text());rows=[]
    for pose in pose_data['poses']:
        set_pose(pose,pivots);graph=bpy.context.evaluated_depsgraph_get();surfaces={o.name:h['surface'](o,graph) for o in targets}
        points={n:pivots[r['owner']].matrix_world@Vector(r['localNativeXYZ']) for n,r in proposals.items()}
        probes=list(points.items())
        for line,a,b in [('advanced-short-actuator','lower-drive-anchor','upper-horn-tip'),
                         ('maker-secondary-tension-line','maker-outboard-line-guide','upper-horn-tip')]:
            probes.extend((f'{line}-{i}/16',points[a].lerp(points[b],i/16)) for i in range(17))
        nearest=[]
        for name,point in probes:
            distances=[]
            for target,s in surfaces.items():
                if s:
                    hit=s['tree'].find_nearest(point)
                    if hit[0] is not None:distances.append((hit[3],target))
            dist,target=min(distances);nearest.append({'probe':name,'nearestPlate':target,'centerlineDistanceM':dist,
                    'nominal12mmHousingMarginM':dist-.012})
        line_proofs=[]
        for line,a,b in [('advanced-short-actuator','lower-drive-anchor','upper-horn-tip'),
                         ('maker-secondary-tension-line','maker-outboard-line-guide','upper-horn-tip')]:
            length=(points[b]-points[a]).length;minimum=min(r['centerlineDistanceM'] for r in nearest if r['probe'].startswith(line))
            line_proofs.append({'line':line,'lengthM':length,'minimumSampleDistanceM':minimum,
                'continuousCenterlineDistanceLowerBoundM':minimum-length/32,
                'continuousNominal12mmHousingMarginLowerBoundM':minimum-length/32-.012,
                'method':'Distance-to-surface is1-Lipschitz; uniform17 samples bound every point by half a sample step.'})
        rows.append({'poseId':pose['id'],'closestProbe':min(nearest,key=lambda r:r['centerlineDistanceM']),
                     'mountPoints':[r for r in nearest if r['probe'] in points],
                     'connectingSegmentConservativeBounds':line_proofs,
                     'actuatorEndpointDistanceM':(points['lower-drive-anchor']-points['upper-horn-tip']).length})
    result={'status':'Proposed outboard neighborhoods only; no native/control hardware implemented or accepted',
            'native':artifact(native),'actualRuntimePosePacket':artifact(packet),'mounts':proposals,'poses':rows,
            'upperHornRoot':{'owner':NEW_JOINT,'localNativeXYZ':[-.158,0,0],
                            'interface':'Existing upper-owned shaft outer face; requires a rigid outboard dogleg horn, not a floating new pivot'},
            'lowerBracketRoot':{'owner':'neck','localNativeXYZ':[-.146,-.113,.172],
                              'interface':'Lower clevis outer race rim; requires a rigid outboard/downward bracket to drive anchor'},
            'eraDriveProposal':{'Maker':'Same external neck control routes a secondary tension line through the proposed lower-owned outboard guide to upper-owned horn. Existing lower drive remains; passive return and ratio require design.',
                 'Mechanic':'Rigid passive brace pins between lower anchor and upper horn only with both neck pitches locked. No freely bending brace is proposed.',
                 'Advanced':'Short pin-ended actuator connects lower anchor to upper horn, driving the upper journal in addition to current lower driver.'},
            'limits':['Only point/line samples against native plate surfaces, not solid actuator/rod/bracket clearance.',
                      'Conservative segment bounds cover the full centerline against those plate surfaces at each discrete pose; no continuous pose sweep or full fitting geometry.',
                      'No runtime-generated15 procedural controls or powered hardware clearance is included.',
                      'Mount interfaces and dogleg brackets remain proposals; exact historic arrangement is unknown.',
                      'Housing radius12mm is a proposal. End fitting geometry and full continuous sweeps require checks.']}
    (out/'mounting-neighborhoods.json').write_text(json.dumps(result,indent=2)+'\n')
    assert sha(native)==receipt['native']['sha256'];print(json.dumps({'mounts':proposals,'minimumCenterlinePlateDistanceM':min(r['closestProbe']['centerlineDistanceM'] for r in rows),
                    'actuatorLengthRangeM':[min(r['actuatorEndpointDistanceM'] for r in rows),max(r['actuatorEndpointDistanceM'] for r in rows)]}))

def boundary_map(attempt):
    from mathutils.kdtree import KDTree
    audit=ROOT/'assets/audit/cervical-construction-study-v1'/f'attempt-{attempt}'
    receipt=json.loads((audit/'receipt.json').read_text());native=ROOT/receipt['native']['path']
    out=audit/'actual-runtime-joint-clearance-v1'/'editable-boundary-map.json';assert not out.exists()
    j=json.loads((out.parent/'guard-clearance-native.json').read_text());assert sha(native)==receipt['native']['sha256']
    h=runpy.run_path(str(ROOT/'scripts/diagnose-native-regional-clearance.py'),run_name='diagnostic_helpers')
    bpy.ops.wm.open_mainfile(filepath=str(native));graph=bpy.context.evaluated_depsgraph_get();cache={}
    names={hit[key] for row in j['rows'] for hit in row['pairsWithOverlapCandidates'] for key in ['subject','target']}
    for name in names:
        obj=bpy.data.objects[name];tree=KDTree(len(obj.data.vertices))
        for v in obj.data.vertices:tree.insert(obj.matrix_world@v.co,v.index)
        tree.balance();cache[name]=(obj,h['surface'](obj,graph),tree)
    rows=[]
    for row in j['rows']:
        if row['poseId'] not in ['runtime-rest','advanced-contact','maker-neck-and-jaw-combined','inspection-open-0.5-separation-0']:continue
        for hit in row['pairsWithOverlapCandidates']:
            if not hit['intermediateJointPair']:continue
            record={'poseId':row['poseId'],'subject':hit['subject'],'target':hit['target'],'meshes':[]}
            for key in ['subject','target']:
                name=hit[key];obj,surf,tree=cache[name];ids=hit['properFaceCrossing'][key+'EvaluatedTriangleIndices']
                controls=sorted({tree.find(surf['points'][v])[1] for i in ids for v in surf['faces'][i]})
                m={'name':name,'nativeControlVertexCount':len(obj.data.vertices),'nearestEditableControlVertexIndices':controls,
                   'confirmedEvaluatedTriangleIndices':ids}
                if len(obj.data.vertices)==209:m['patchGridRows']=sorted({i//19 for i in controls});m['patchGridColumns']=sorted({i%19 for i in controls})
                record['meshes'].append(m)
            rows.append(record)
    out.write_text(json.dumps({'method':'Same-topology evaluated triangle indices reconstructed at saved rest; nearest editable native vertices identify boundary neighborhoods. Nearest-control attribution is not identical topology. 209vertex patch grids have19 across and11 rows.',
                     'native':artifact(native),'diagnosis':artifact(out.parent/'guard-clearance-native.json'),'rows':rows},indent=2)+'\n')
    assert sha(native)==receipt['native']['sha256'];print(json.dumps({'records':len(rows),'path':str(out.relative_to(ROOT))}))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--attempt',default='01');ap.add_argument('--two-stage',action='store_true');ap.add_argument('--export',action='store_true');ap.add_argument('--review',action='store_true');ap.add_argument('--joint-pockets',action='store_true');ap.add_argument('--clean-sections',action='store_true');ap.add_argument('--designed-transition',action='store_true');ap.add_argument('--coherent-transition',action='store_true');ap.add_argument('--full-lateral',action='store_true');ap.add_argument('--pose-packet');ap.add_argument('--render-actual',action='store_true');ap.add_argument('--mount-proposal',action='store_true');ap.add_argument('--mount-outboard',action='store_true');ap.add_argument('--mount-lower-anterior',action='store_true');ap.add_argument('--boundary-map',action='store_true');args=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
    if args.boundary_map:
        boundary_map(args.attempt);return
    if args.mount_proposal:
        mount_proposal_review(args.attempt,args.pose_packet,args.mount_outboard,args.mount_lower_anterior);return
    if args.review:
        review_existing(args.attempt,args.pose_packet,args.render_actual);return
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
    retagged=(coherent_transition_correction(objs,additions,joint_contract,args.full_lateral) if args.coherent_transition else clean_section_correction(objs,additions,joint_contract,args.designed_transition) if args.clean_sections else joint_pocket_correction(objs,additions,joint_contract)) if args.joint_pockets else set()
    after=h['scene_snapshot']();changed=sorted(REPLACE|FRAME)
    if args.two_stage:
        assert set(after['empties'])==set(before['empties'])|{NEW_JOINT}
        assert all(after['empties'][n]==before['empties'][n] for n in set(before['empties'])-{'head'})
        assert after['empties']['head']['matrix']==before['empties']['head']['matrix']
    else:assert before['empties']==after['empties']
    assert before['curves']==after['curves']
    assert set(after['meshes'])==set(before['meshes'])|set(additions)
    assert all(before['meshes'][n]==after['meshes'][n] for n in set(before['meshes'])-set(changed))
    assert all({k:v for k,v in before['meshes'][n].items() if k not in (['mesh','modifiers','parent','matrix','props'] if args.joint_pockets else ['mesh','modifiers','parent','matrix'] if args.two_stage else ['mesh','modifiers'])}==
               {k:v for k,v in after['meshes'][n].items() if k not in (['mesh','modifiers','parent','matrix','props'] if args.joint_pockets else ['mesh','modifiers','parent','matrix'] if args.two_stage else ['mesh','modifiers'])} for n in changed)
    for n in changed:
        expected=dict(before['meshes'][n]['props'])
        if n in retagged:expected['region']=repr('breast')
        assert expected==after['meshes'][n]['props']
    matrix_reparent_error=max(abs(before['meshes'][n]['matrix'][r][c]-after['meshes'][n]['matrix'][r][c]) for n in changed for r in range(4) for c in range(4))
    assert matrix_reparent_error<2e-7
    assert material_signatures=={m.name:h['material_signature'](m) for m in bpy.data.materials}
    native=out/'murderbird-cervical-construction-study-v1.blend'
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False)
    bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
    (audit/'preserved-scene-snapshot.json').write_text(json.dumps(after,indent=2)+'\n')
    receipt={'status':'neutral construction proposal; visual/clearance review pending','base':artifact(BASE),'native':artifact(native),
             'generator':artifact(audit/'executed-generator.py'),'poses':artifact(POSES),
             'replace':changed,'add':additions,'profileWorldStations':PROFILE,'bandsWorldStations':bands,'twoStageContract':joint_contract,
             'preservation':{'unrelated678MeshesExact':True,'originalPivotWorldMatricesExact':True,'originalPivotHierarchyExact':not args.two_stage,'nativePivotCount':len(after['empties']),'all462GuidesExact':True,
                             'allMaterialsExact':True,'saveReloadSnapshotExact':True,'rawRestMatrixError':rest_err,'changedMeshReparentWorldError':matrix_reparent_error},
             'construction':{'sharedAllEras':True,'neckOwner':'neck','yokeOwner':'breastplate',
                 'forkEndpoints':fork_records,'sampledYokeKeepout':{**keepout_receipt,'rig':'legacy51; not a new52-rig clearance certification' if args.two_stage else 'legacy51'},'yokeEdges':yoke_records,
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
    if args.export:
        assert args.two_stage,'Only explicitly authorized diagnostic52-pivot export'
        glb=out/'murderbird-cervical-construction-study-v1.glb';assert not glb.exists()
        h['export_from_reopened_native'](native,glb,after,{n:after['meshes'][n]['modifiers'] for n in changed+additions})
        receipt['diagnosticGlb']=artifact(glb)
        receipt['limits'].append('Diagnostic GLB includes inherited proof clip; it is not a new52-joint authored action or tested runtime. No app integration.')
        (audit/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        assert sha(native)==receipt['native']['sha256']
    print(json.dumps({'native':artifact(native),'replace':len(changed),'add':len(additions),'views':len(receipt['views'])}))
if __name__=='__main__':main()
