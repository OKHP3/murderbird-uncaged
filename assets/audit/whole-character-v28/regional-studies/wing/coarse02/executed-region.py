"""V28 coarse02: compact outer canopy and independently nested short shield.
Native Z-up/-Y-front. Authoring dimensions are proposals, not art measurements.
No body/head/runtime edit; actual load machinery, pivots and materials retained.
"""
import bpy,bmesh,math,json
from mathutils import Vector,Matrix
OWNERS=('left-mantle','right-mantle','left-wing-shield','right-wing-shield')
CANOPY=((0,.286,-.014,1.343,.072,.162),(.18,.308,.000,1.303,.124,.195),(.38,.325,.028,1.230,.142,.215),(.62,.344,.076,1.124,.139,.207),(.82,.365,.134,1.032,.110,.181),(1,.370,.232,.924,.055,.139))
SHIELD=((0,.387,.051,1.057,.043,.106),(.45,.389,.126,1.005,.046,.113),(1,.374,.228,.936,.025,.095))
COURSES=((.005,.225,7,-1.39,1.27,.019),(.155,.440,8,-1.33,1.27,.015),(.345,.645,8,-1.26,1.25,.011),(.565,.855,7,-1.16,1.22,.007),(.765,1.000,6,-1.06,1.19,.003))

def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def node(o):return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),json.dumps(dict(o.items()),sort_keys=True,default=lambda x:list(x)))
def snap(o):return (node(o),tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(f.vertices) for f in o.data.polygons),tuple(m.name if m else None for m in o.data.materials),tuple((q.name,q.type) for q in o.modifiers),o.hide_render,o.hide_viewport)
def sample(table,t):
    t=max(table[0][0],min(table[-1][0],t));i=next((i for i in range(len(table)-1) if table[i][0]<=t<=table[i+1][0]),len(table)-2);a,b=table[i:i+2];u=(t-a[0])/(b[0]-a[0]);out=[]
    for k in range(1,6):
        slope=(b[k]-a[k])/(b[0]-a[0]);m0=slope if i==0 else (b[k]-table[i-1][k])/(b[0]-table[i-1][0]);m1=slope if i+2==len(table) else (table[i+2][k]-a[k])/(table[i+2][0]-a[0]);h=b[0]-a[0]
        out.append((2*u**3-3*u*u+1)*a[k]+(u**3-2*u*u+u)*h*m0+(-2*u**3+3*u*u)*b[k]+(u**3-u*u)*h*m1)
    return out

def point(kind,side,t,a):
    x,y,z,rx,ry=sample(CANOPY if kind=='canopy' else SHIELD,t);return Vector((side*(x+rx*math.cos(a)),y+ry*math.sin(a),z-.011*math.sin(a)*math.sin(math.pi*t)))
def normal(kind,side,t,a):
    e=.0005;along=point(kind,side,t+e,a)-point(kind,side,t-e,a);across=point(kind,side,t,a+e)-point(kind,side,t,a-e);n=across.cross(along).normalized()
    if n.dot(Vector((side*math.cos(a),math.sin(a),.15)))<0:n.negate()
    return n

def install(name,owner,verts,faces,mat,role='plate',existing=None,wall=.0035):
    o=existing or bpy.data.objects.new(name,bpy.data.meshes.new(name+' placeholder'))
    if existing is None:bpy.context.scene.collection.objects.link(o);o.parent=bpy.data.objects[owner];o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_world=Matrix.Identity(4)
    bpy.context.view_layer.update();inv=o.matrix_world.inverted();m=bpy.data.meshes.new(name+' V28 canopy construction');m.from_pydata([inv@v for v in verts],[],faces);m.materials.append(mat);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();o.data=m
    for q in list(o.modifiers):o.modifiers.remove(q)
    for f in m.polygons:f.use_smooth=True
    q=o.modifiers.new('Finite formed wall','SOLIDIFY');q.thickness=wall;q.offset=-1;q.use_even_offset=False
    o['surfaceRole']=role;o['region']='mantle' if owner.endswith('mantle') else 'wing';o['exteriorEras']='maker,mechanic,builder';o['constructionClass']='proposed-passive';o['wallM']=wall;o['geometryStatus']='V28 coarse02 compact canopy proposal; first visual gate, intersections not accepted';o['authoringRole']='One rigid owner; compact directional canopy over independent short shield, no flight train or cylindrical cuff'
    return o

def sheet(name,owner,kind,side,start,end,center,half,offset,mat,joint,role='plate',existing=None,rows=20,cols=14):
    verts=[];faces=[];expected=[]
    for j in range(rows+1):
        t=j/rows;spread=1 if role=='frame' else .94-.40*ease(t)
        for k in range(cols+1):
            u=2*k/cols-1;station=start+(end-start)*t+.027*u*ease(t)+.006*(1-u*u)*ease(t);station=max(.0001,min(.9999,station));a=center+.105*ease(t)+half*spread*u;p=point(kind,side,station,a);n=normal(kind,side,station,a);verts.append(p+n*(offset+.0013*(1-u*u)*math.sin(math.pi*t)));expected.append(n)
    for j in range(rows):
        for k in range(cols):
            i=j*(cols+1)+k;ids=(i,i+1,i+cols+2,i+cols+1)
            # Coarse receiving window exposes the actual elbow races. The
            # free-edge boundary is finite on this owner; no hardware erased.
            if any(math.hypot(verts[n].y-joint.y,verts[n].z-joint.z)<.064 for n in ids):continue
            faces.append(ids)
    assert faces,name
    o=install(name,owner,verts,faces,mat,role,existing,.004 if role=='frame' else .0035)
    f=o.data.polygons[len(o.data.polygons)//2];n=o.matrix_world.to_3x3().inverted().transposed()@f.normal
    if n.dot(expected[f.vertices[0]])<0:
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    o['actualElbowReceivingRadiusM']=.064
    return o

def tube(name,owner,points,r,mat):
    verts=[];faces=[];N=10
    for i,p in enumerate(points):
        p=Vector(p);t=(Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])).normalized();u=t.cross(Vector((1,0,0)))
        if u.length<.01:u=t.cross(Vector((0,1,0)))
        u.normalize();v=t.cross(u).normalized()
        for k in range(N):verts.append(p+r*(u*math.cos(k*math.tau/N)+v*math.sin(k*math.tau/N)))
    for j in range(len(points)-1):
        for k in range(N):a=j*N+k;b=j*N+(k+1)%N;faces.append((a,b,b+N,a+N))
    faces.append(tuple(reversed(range(N))));faces.append(tuple((len(points)-1)*N+k for k in range(N)))
    o=install(name,owner,verts,faces,mat,'frame',wall=.004)
    # This is already a closed formed support, not a doubled surface tube.
    o.modifiers.clear();o['authoringRole']='Finite single-owner support proposed from retained journal seat into its own canopy/short-shield liner';return o

def apply():
    bpy.context.view_layer.update();nodes={o.name:node(o) for o in bpy.data.objects if o.type=='EMPTY'};original={o.name:snap(o) for o in bpy.data.objects if o.type=='MESH'};removed=[];added=[];changed=[]
    mats={label:(bpy.data.objects[f'V21 refined {label} mantle course 1 plate 3'].data.materials[0],bpy.data.objects[f'V21 refined {label} compact shield course 1 plate 4'].data.materials[0],bpy.data.objects[f'{label} swept upper wing load member'].data.materials[0]) for label in ['left','right']}
    for o in list(bpy.data.objects):
        if o.type!='MESH' or not o.parent or o.parent.name not in OWNERS:continue
        replace=(o.name.startswith('V21 refined ') and not o.name.endswith('shoulder journal bonnet')) or o.name.startswith('V23 shoulder arch ')
        if replace:
            removed.append({'name':o.name,'owner':o.parent.name,'reason':'Exterior packet replaced by compact oblique canopy / nested short shield'});bpy.data.objects.remove(o,do_unlink=True)
    for label,side in [('left',1),('right',-1)]:
        mantle=label+'-mantle';shield=label+'-wing-shield';joint=bpy.data.objects[shield].matrix_world.translation.copy();skin,shieldmat,frame=mats[label]
        backing=bpy.data.objects[f'{label} profiled mantle backing v4 {mantle}'];sheet(backing.name,mantle,'canopy',side,.005,.990,.010,1.34,-.007,backing.data.materials[0],joint,'frame',backing,32,24);changed.append(backing.name)
        for row,(start,end,N,a,b,layer) in enumerate(COURSES):
            step=(b-a)/N
            for k in range(N):
                center=a+(k+.5)*step+(.12*step if row%2 else -.06*step);name=f'V28 {label} canopy oblique course {row+1} plate {k+1}'
                o=sheet(name,mantle,'canopy',side,start+.007*math.sin(k*1.3+row),end-.017*k/max(1,N-1),center,step*.485,layer,skin,joint);added.append(o.name)
        o=sheet(f'V28 {label} canopy anterior folded return',mantle,'canopy',side,.07,.90,-1.31,.11,.014,skin,joint,'guard',rows=28,cols=10);added.append(o.name)
        backing=bpy.data.objects[f'{label} profiled mantle backing v4 {shield}'];sheet(backing.name,shield,'shield',side,.01,.95,.05,1.17,-.004,backing.data.materials[0],joint,'frame',backing,24,20);changed.append(backing.name)
        for row,(start,end,N,a,b) in enumerate([(.025,.58,5,-1.00,1.20),(.43,.99,5,-.91,1.16)]):
            step=(b-a)/N
            for k in range(N):
                o=sheet(f'V28 {label} short nested shield {row+1} plate {k+1}',shield,'shield',side,start,end-.016*k, a+(k+.5)*step+row*.05,step*.485,.007-row*.004,shieldmat,joint);added.append(o.name)
        o=sheet(f'V28 {label} short shield leading fold',shield,'shield',side,.035,.92,-1.04,.12,.008,shieldmat,joint,'guard',rows=22,cols=10);added.append(o.name)
        pivot=bpy.data.objects[mantle].matrix_world.translation.copy()
        for k,a in enumerate([-.50,.50]):
            end=point('canopy',side,.13,a);start=pivot+Vector((side*.030,0,0));o=tube(f'V28 {label} canopy receiving load bow {k+1}',mantle,[start,start.lerp(end,.5)+Vector((side*.013,0,0)),end],.007,frame);added.append(o.name)
        for k,a in enumerate([-.50,.50]):
            end=point('shield',side,.23,a);start=joint+Vector((side*.014,0,0));o=tube(f'V28 {label} nested shield receiving fork {k+1}',shield,[start,start.lerp(end,.5),end],.006,frame);added.append(o.name)
    bpy.context.view_layer.update();assert nodes=={o.name:node(o) for o in bpy.data.objects if o.type=='EMPTY'};removednames={p['name'] for p in removed};outside={n:s for n,s in original.items() if n not in changed and n not in removednames};assert all(snap(bpy.data.objects[n])==s for n,s in outside.items())
    return {'region':'compact outer mantle canopy and short nested shield','study':'V28 coarse02; first visual gate before detail','status':'inferred editable construction proposal; intersections may remain and are not accepted','changedMeshes':changed,'removed':removed,'added':added,'changedNodes':[],'nodesExact':len(nodes),'outsideMeshesExact':len(outside),'canopyTable':CANOPY,'shieldTable':SHIELD,'plateCourses':COURSES,'construction':'Five oblique tapered canopy courses wrap around the retained elbow window at rest. Two short independently owned shield courses nest underneath and retain the existing short shove. Open shaped liners and finite single-owner receiving bows replace sleeve backing hierarchy; no circular cuff or hanging flight train.','preserved':['All actual named pivots/rests, shaft/races/load members and left travel restriction','Head/body/feet and outside wing geometry','Original material definitions and passive three-era eligibility','Existing motion APIs; no src edit'],'limits':['Actual rendered whole-wing identity is the first gate; interowner clearances and support attachment remain to be measured after that gate.','Finite mechanical proposal; no physical simulation, continuous collision proof or exact dimensions from art.']}
