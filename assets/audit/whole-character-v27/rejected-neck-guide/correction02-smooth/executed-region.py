"""One-hinge passive captive-guide prototype; no runtime integration.
Native Z-up/-Y-front. Guard solids stay rigid and keep their authored forms.
All guide dimensions and travel are proposed, not owner-approved engineering.
"""
import bpy,bmesh,math,json
from mathutils import Vector,Matrix,Quaternion
from mathutils.bvhtree import BVHTree
GUARDS=[f'V23 cervical 2 directional guard {k}' for k in (2,3,4)]
CHAIN=['neck','cervical-mid-a','cervical-mid-b','cervical-upper']
NAME='cervical-mid-a-front-guard-slide'
ROTATION_FRACTION=1.0
ANGLES=sorted(set([-.035,0]+[.1625*i/10 for i in range(1,11)]))

def meshworld(o):
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@p.co for p in m.vertices];t=[tuple(p.vertices) for p in m.loop_triangles];ev.to_mesh_clear();return v,t

def straddle(A,B):
    n=(A[1]-A[0]).cross(A[2]-A[0]);n.normalize();d=[n.dot(p-A[0]) for p in B];return min(d)<-1e-7 and max(d)>1e-7

def crossing(a,b):
    out=0
    for i,j in a[2].overlap(b[2]):
        A=[a[0][n] for n in a[1][i]];B=[b[0][n] for n in b[1][j]]
        if straddle(A,B) and straddle(B,A):out+=1
    return out

def tri(v,t):return (v,t,BVHTree.FromPolygons(v,t,all_triangles=True))

def _tube(name,points,r,owner,material,role='frame'):
    verts=[];faces=[];N=8
    for i,p in enumerate(points):
        p=Vector(p);t=(Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])).normalized();u=t.cross(Vector((1,0,0)))
        if u.length<.01:u=t.cross(Vector((0,1,0)))
        u.normalize();v=t.cross(u).normalized()
        for k in range(N):verts.append(p+r*(u*math.cos(k*math.tau/N)+v*math.sin(k*math.tau/N)))
    for i in range(len(points)-1):
        for k in range(N):a=i*N+k;b=i*N+(k+1)%N;faces.append((a,b,b+N,a+N))
    faces.append(tuple(reversed(range(N))));faces.append(tuple((len(points)-1)*N+k for k in range(N)))
    o=bpy.data.objects.new(name,bpy.data.meshes.new(name));bpy.context.scene.collection.objects.link(o);o.parent=bpy.data.objects[owner];o.matrix_world=Matrix.Identity(4);bpy.context.view_layer.update();inv=o.matrix_world.inverted();o.data.from_pydata([inv@p for p in verts],[],faces);o.data.materials.append(material)
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update();o['exteriorEras']='maker,mechanic,builder';o['surfaceRole']=role;o['region']='neck';o['constructionClass']='proposed-passive';o['geometryStatus']='V27 captive guide coarse proposal; appearance/clearance unaccepted';return o

def _interpolate(law,angle):
    # Analytic cubic travel, with zero slope at the rest seat and contact end.
    # Stored knots are measurement witnesses, not piecewise motion corners.
    rest=next(row for row in law if row['angle']==0);end=law[-1]
    t=max(0,min(1,angle/end['angle']));t=t*t*(3-2*t)
    return Vector(rest['translation']).lerp(Vector(end['translation']),t)

def carrier_pose(angle,law,fraction=None):return Matrix.Translation(_interpolate(law,angle))@Matrix.Rotation(angle*(ROTATION_FRACTION if fraction is None else fraction),4,'X')

def proof_update():
    o=bpy.data.objects[NAME];c=json.loads(o['cervicalGuardGuideV1']);driver=bpy.data.objects[c['driver']];rest=Matrix(c['driverRestLocal']);d=rest.to_quaternion().inverted()@driver.matrix_local.to_quaternion();angle=d.to_euler('XYZ').x
    o.matrix_local=Matrix(c['carrierRestLocal'])@carrier_pose(angle,c['law'],c['rotationFraction']);bpy.context.view_layer.update();return angle

def apply():
    bpy.context.view_layer.update();nodes={o.name:o.matrix_world.copy() for o in bpy.data.objects if o.type=='EMPTY'};origins={n:bpy.data.objects[n].matrix_local.copy() for n in CHAIN};restdriver=origins['cervical-mid-a'];parent=bpy.data.objects['neck'];J=bpy.data.objects['cervical-mid-a'].matrix_world.copy();Jinv=J.inverted();source={n:([Jinv@p for p in meshworld(bpy.data.objects[n])[0]],meshworld(bpy.data.objects[n])[1]) for n in GUARDS};law=[];previous=Vector((0,0,0));derive=[]
    # Finite, bounded lattice measured against evaluated plate solids. This
    # derives a proposed path rather than inventing a visual displacement.
    global ROTATION_FRACTION
    cached=[]
    for angle in ANGLES:
        for n in CHAIN:bpy.data.objects[n].matrix_local=origins[n]@Matrix.Rotation(angle,4,'X')
        bpy.context.view_layer.update();reference=parent.matrix_world@restdriver;neighbors=[]
        for o in bpy.data.objects:
            if o.type!='MESH' or o.name in GUARDS or not o.parent:continue
            if o.name.startswith('V23 cervical ') and 'directional guard' in o.name or o.parent.name in ['breastplate','body','head','cranial-cover','jaw','upper-bill'] and o.get('surfaceRole') in ['plate','shell','guard','recess']:
                v,t=meshworld(o);neighbors.append((o.name,tri(v,t)))
        cached.append((angle,reference,neighbors))
    choices=[]
    for fraction in (.75,1.0):
        for forward in (.008,.012,.016,.020,.024,.028,.032):
            for lift in (0,.006,.012,.018,.024):
                rows=[];candidate=[]
                for angle,reference,neighbors in cached:
                    t=max(0,min(1,angle/.1625));t=t*t*(3-2*t)
                    c=Vector((0,-(.008+(forward-.008)*t),lift*t));M=reference@Matrix.Translation(c)@Matrix.Rotation(angle*fraction,4,'X');pairs=[];witnesses=0
                    for n,(v,triangles) in source.items():
                        part=tri([M@p for p in v],triangles)
                        for other,q in neighbors:
                            hits=crossing(part,q)
                            if hits:pairs.append((n,other,hits));witnesses+=hits
                    candidate.append({'angle':angle,'translation':list(c)});rows.append({'angle':angle,'totalPitch':angle*4,'strictPairs':len(pairs),'witnesses':witnesses,'pairs':pairs})
                score=(sum(r['strictPairs'] for r in rows),max(r['strictPairs'] for r in rows),sum(r['witnesses'] for r in rows),math.hypot(forward,lift))
                choices.append((score,fraction,candidate,rows))
        print('GLOBAL_GUIDE_SEARCH',fraction,flush=True)
    best=min(choices,key=lambda x:x[0]);ROTATION_FRACTION=best[1];law=best[2];derive=best[3]
    print('GLOBAL_GUIDE_SELECTED',best[0],ROTATION_FRACTION,law[-1],flush=True)
    for n in CHAIN:bpy.data.objects[n].matrix_local=origins[n]
    bpy.context.view_layer.update();assert all((bpy.data.objects[n].matrix_world-nodes[n]).to_3x3().magnitude<1e-6 for n in [])
    carrier=bpy.data.objects.new(NAME,None);bpy.context.scene.collection.objects.link(carrier);carrier.parent=parent;carrier.matrix_world=J;bpy.context.view_layer.update();carrierrest=carrier.matrix_local.copy();restC=_interpolate(law,0);carrier.matrix_local=carrierrest@carrier_pose(0,law);bpy.context.view_layer.update()
    # Authored guard vertices/modifiers/materials remain unchanged. Capture
    # placement relative to the unshifted joint, then retain the measured seat.
    for n in GUARDS:
        o=bpy.data.objects[n];local=Jinv@o.matrix_world;o.parent=carrier;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_local=local
    carrier['constructionClass']='proposed-passive';carrier['cervicalGuardGuideV1']=json.dumps({'schema':1,'driver':'cervical-mid-a','parent':'neck','angleRange':[-.035,.1625],'rotationFraction':ROTATION_FRACTION,'carrierRestLocal':[list(r) for r in carrierrest],'driverRestLocal':[list(r) for r in restdriver],'law':law,'restSeatTranslation':list(restC),'status':'finite sampled actual-solid derived prototype; runtime not integrated'})
    # Two distinct follower paths constrain orientation as well as position.
    # A third, inverse-hinge path is the actual positive cam/push-pull coupling.
    metal=bpy.data.objects['V23 cervical 1 distal race -1'].data.materials[0];frame=bpy.data.objects['V23 cervical 1 load link -1'].data.materials[0];added=[];hardware=[];samples=[ANGLES[0]+(ANGLES[-1]-ANGLES[0])*i/80 for i in range(81)]
    pins=[Vector((-.090,-.052,.012)),Vector((-.100,-.040,.037))];lug=Vector((-.121,-.046,.024));camPin=Vector((-.121,-.007,.010))
    def install(n,p,r,owner,mat):o=_tube(n,p,r,owner,mat);added.append(o.name);return o
    def track(prefix,positions,owner):
        # Opposed closed rails and retained axial cheeks define a captive slot;
        # finite rollers occupy its centerline. No broad collar surrounds neck.
        for side in (-1,1):install(prefix+f' rail {side}',[p+Vector((0,side*.0048,0)) for p in positions],.0022,owner,frame)
        for side in (-1,1):install(prefix+f' retaining cheek {side}',[p+Vector((side*.009,0,0)) for p in positions],.0018,owner,metal)
        for end in (0,-1):
            direction=(positions[0]-positions[1]).normalized() if end==0 else (positions[-1]-positions[-2]).normalized();center=positions[end]+direction*.008
            install(prefix+f' end stop {end}',[center+Vector((0,-.0065,0)),center+Vector((0,.0065,0))],.0022,owner,frame)
    paths=[]
    for i,p in enumerate(pins):
        pts=[J@(carrier_pose(a,law)@p) for a in samples];track(f'V27 mid-a captive guide {i+1}',pts,'neck');paths.append({'kind':'fixed-guide','localPin':list(p),'worldRestPath':[[float(c) for c in x] for x in pts]})
        M=J@carrier_pose(0,law);install(f'V27 mid-a guide roller {i+1}',[M@(p+Vector((-.006,0,0))),M@(p+Vector((.006,0,0)))],.0024,NAME,metal)
    # The rigid push-pull member and its two clevis pins stay one carrier-owned
    # assembly. Its cam end is captured in a slot fixed to the moving hinge.
    M=J@carrier_pose(0,law);install('V27 mid-a rigid push-pull member',[M@lug,M@camPin],.0032,NAME,frame)
    for label,p in [('carrier',lug),('cam follower',camPin)]:install('V27 mid-a '+label+' clevis pin',[M@(p+Vector((-.007,0,0))),M@(p+Vector((.007,0,0)))],.0024,NAME,metal)
    cams=[J@(Matrix.Rotation(-a,4,'X')@(carrier_pose(a,law)@camPin)) for a in samples];track('V27 mid-a positive drive cam',cams,'cervical-mid-a');paths.append({'kind':'hinge-cam','localPin':list(camPin),'worldRestPath':[[float(c) for c in x] for x in cams]})
    # Compact mounting webs connect each fixed slot to the actual side bearing.
    for i,p in enumerate(pins):install(f'V27 mid-a fixed guide mounting web {i+1}',[J@Vector((-.071,0,0)),J@p],.0035,'neck',frame)
    install('V27 mid-a drive cam mounting web',[J@Vector((-.083,0,0)),J@camPin],.0035,'cervical-mid-a',frame)
    # Three rigid tabs meet actual evaluated guard wall vertices, with a
    # carrier-owned crossbow connecting the plates to both guide followers.
    attachments=[]
    for n,(v,t) in source.items():
        cx=sum(p.x for p in v)/len(v);p=min(v,key=lambda q:(q-Vector((cx,-.130,.027))).length_squared);attachments.append(p)
        install('V27 mid-a plate attachment '+n.rsplit(' ',1)[-1],[M@p,M@Vector((p.x,-.095,.024)),M@lug],.0030,NAME,frame)
    for i,p in enumerate(pins):install(f'V27 mid-a carrier follower web {i+1}',[M@lug,M@p],.0032,NAME,frame)
    carrier['plateAttachments']=json.dumps([list(p) for p in attachments])
    carrier['guidePaths']=json.dumps(paths);carrier['pushPullLug']=json.dumps(list(lug));carrier['camFollower']=json.dumps(list(camPin));bpy.context.view_layer.update()
    for n,m in nodes.items():assert max(abs(bpy.data.objects[n].matrix_world[r][c]-m[r][c]) for r in range(4) for c in range(4))<1e-6,n
    return {'status':'one-hinge coarse construction proposal; root visual/clearance gate required before extension','reparentedGuards':GUARDS,'guardMeshFormsExact':True,'addedNodes':[NAME],'addedMeshes':added,'changedOriginalStructuralNodes':[],'derivedLaw':law,'rotationFraction':ROTATION_FRACTION,'globalGuideScore':list(best[0]),'derivation':derive,'finiteSamplingOnly':True,'mechanism':'Two captive fixed guides constrain a rigid carrier; hinge-owned positive cam slot drives a constant-length captive push-pull follower assembly.','runtimeProposal':'Optional cervicalGuardGuidesV1; setPitch/updateCovers synchronize guide; capture/restore/reset include carrier. No src changes.','limits':['Guide rail collision/pressure angle/manufacturability unproven.','Original other-guard/head/body crossings remain independent.','No continuous collision or physics certificate.']}
