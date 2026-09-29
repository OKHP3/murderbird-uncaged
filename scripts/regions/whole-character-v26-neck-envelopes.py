"""V26 short rigid cervical coverage derived around the hinge sweep.

This replaces all forty broad directional guard cores, not only terminal
lips. Native Z-up/-Y-front. All named rests and head geometry stay exact.
The qualitative owner image controls the S-curve; dimensions below are an
inferred construction proposal, not recovered engineering dimensions.
"""
import bpy,bmesh,math,json
from mathutils import Vector

PROFILE=((.78,-.165,.125,.170),(.87,-.247,.139,.210),(.99,-.365,.128,.252),(1.12,-.425,.095,.280),(1.245,-.417,.038,.258),(1.335,-.382,-.035,.205),(1.410,-.352,-.106,.145),(1.48,-.379,-.160,.116),(1.555,-.428,-.213,.109),(1.635,-.446,-.256,.100))
JOINTS=(('neck',(0,-.188,1.335)),('cervical-mid-a',(0,-.229,1.410)),('cervical-mid-b',(0,-.270,1.480)),('cervical-upper',(0,-.321,1.550)))
SECTORS=((-1.22,-.74),(-.72,-.25),(-.23,.23),(.25,.72),(.74,1.22),(1.245,1.82),(1.84,2.45),(-2.45,-1.84),(-1.82,-1.245),(2.47,math.tau-2.47))
GUARDS=[f'V23 cervical {i+1} directional guard {k+1}' for i in range(4) for k in range(10)]
BREAST=['V24 continuous recessed breast backing']+[f'V24 breast course 01 panel {i:02}' for i in range(1,7)]
WALL=.0035;CLEAR=.008;PITCH=(-.14/4,.65/4);YAW=(-.45,0,.45)


def sample(z,k):
    x=[r[0] for r in PROFILE];y=[r[k] for r in PROFILE]
    if z<=x[0]:return y[0]
    if z>=x[-1]:return y[-1]
    h=[b-a for a,b in zip(x,x[1:])];d=[(b-a)/v for a,b,v in zip(y,y[1:],h)];m=[d[0]]
    for i in range(1,len(x)-1):
        if d[i-1]*d[i]<=0:m.append(0.)
        else:
            w1=2*h[i]+h[i-1];w2=h[i]+2*h[i-1];m.append((w1+w2)/(w1/d[i-1]+w2/d[i]))
    m.append(d[-1])
    for i in range(len(x)-1):
        if x[i]<=z<=x[i+1]:
            t=(z-x[i])/h[i]
            return (2*t**3-3*t*t+1)*y[i]+(t**3-2*t*t+t)*h[i]*m[i]+(-2*t**3+3*t*t)*y[i+1]+(t**3-t*t)*h[i]*m[i+1]


def point(z,angle,off):
    front,rear,width=[sample(z,k) for k in (1,2,3)]
    return Vector(((width+off)*math.sin(angle),(front+rear)/2-((rear-front)/2+off)*math.cos(angle),z))


def _props(o):return json.dumps(dict(o.items()),default=lambda x:list(x),sort_keys=True)
def _node(o):return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),_props(o))
def _mesh(o):return (_node(o),tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons),tuple(m.name if m else None for m in o.data.materials),o.hide_render,o.hide_viewport)


def _lower_edge(index,angle,root,distal,off):
    """Withdraw the ENTIRE proximal plate boundary from the pitch sweep.

    At each angular column, a bisection locates the lowest point whose swept
    Z stays above the proximal joint plane. Root yaw is included before its
    pitch, matching the native rest-relative quaternion composition. This is
    a finite endpoint envelope, not a full continuous-clearance certificate.
    """
    def floor(z):
        p=point(z,angle,off)-root;values=[]
        for yaw in YAW if index==0 else (0,):
            dy=math.sin(yaw)*p.x+math.cos(yaw)*p.y
            for pitch in (PITCH[0],0,PITCH[1]):values.append(dy*math.sin(pitch)+p.z*math.cos(pitch))
        return min(values)
    lo=root.z+WALL+CLEAR;hi=distal.z-CLEAR-.007
    assert floor(hi)>CLEAR+WALL,(index,angle,'No coverage can meet the finite endpoint envelope')
    for _ in range(20):
        mid=(lo+hi)*.5
        if floor(mid)>CLEAR+WALL:hi=mid
        else:lo=mid
    return hi


def _surface(index,sector,root,distal):
    # The two owners at a hinge use concentric spherical portions. A sphere
    # stays centered under its owner's hinge rotation and root yaw. The
    # intervening short transition preserves the rest S-curve and volume.
    proximal=(.207,.148,.127,.119)[index]
    distal_radius=(.156,.135,.127,.116)[index]
    a,b=sector;rows=20;cols=16;verts=[];spans=[]
    low=root.z-.014;high=distal.z+.014
    mid=(root.z+distal.z)*.5
    for j in range(rows+1):
        z=low+(high-low)*j/rows
        for k in range(cols+1):
            angle=a+.008+(b-a-.016)*k/cols
            # The transition is only eight millimeters tall. The spherical
            # mating portions retain enough axial extent for finite pitch.
            if z<=mid-.004:
                dz=z-root.z;r=math.sqrt(proximal*proximal-dz*dz);cy=root.y
            elif z>=mid+.004:
                dz=z-distal.z;r=math.sqrt(distal_radius*distal_radius-dz*dz);cy=distal.y
            else:
                t=(z-mid+.004)/.008;t=t*t*(3-2*t)
                ra=math.sqrt(proximal*proximal-(z-root.z)**2);rb=math.sqrt(distal_radius*distal_radius-(z-distal.z)**2)
                r=ra*(1-t)+rb*t;cy=root.y*(1-t)+distal.y*t
            # Leave a finite side journal opening without losing the front
            # continuous silhouette. Each edge remains with its one owner.
            side_window=math.exp(-((abs(math.sin(angle))-.995)/.032)**2)
            zz=z
            if j==0:zz+=.004*side_window
            if j==rows:zz-=.004*side_window
            verts.append(Vector((r*math.sin(angle),cy-r*math.cos(angle),zz)))
            if j==0:spans.append({'angle':angle,'lowerZ':zz,'upperZ':high,'proximalSphereRadiusM':proximal,'distalSphereRadiusM':distal_radius})
    faces=[]
    for j in range(rows):
        for k in range(cols):
            n=j*(cols+1)+k;faces.append((n,n+1,n+cols+2,n+cols+1))
    return verts,faces,spans


def _replace(o,verts,faces):
    bpy.context.view_layer.update();inv=o.matrix_world.inverted()
    m=bpy.data.meshes.new(o.name+' V26 swept-envelope guard')
    m.from_pydata([inv@v for v in verts],[],faces);m.update()
    for mat in o.data.materials:m.materials.append(mat)
    bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free()
    o.data=m
    for mod in list(o.modifiers):o.modifiers.remove(mod)
    for poly in m.polygons:poly.use_smooth=True
    solid=o.modifiers.new('V26 finite formed wall','SOLIDIFY');solid.thickness=WALL;solid.offset=-1;solid.use_even_offset=False
    # The middle outward normal selects the consistent side before thickness.
    center=verts[len(verts)//2];cy=(sample(center.z,1)+sample(center.z,2))/2
    normal=o.matrix_world.to_3x3().inverted().transposed()@m.polygons[len(m.polygons)//2].normal
    if normal.dot(Vector((center.x,center.y-cy,0)))<0:
        bm=bmesh.new();bm.from_mesh(m);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free()
    o['geometryStatus']='V26 inferred rigid cervical coverage proposal; movement and likeness gates pending'
    o['constructionDescription']='Concentric spherical mating portions around actual pivots with a short curved transition. Distinct adjacent radii, single rigid owner, finite wall, no added collar or stretching.'
    o['proposal']=True


def apply():
    bpy.context.view_layer.update()
    for n,p in JOINTS:assert (bpy.data.objects[n].matrix_world.translation-Vector(p)).length<1e-6,n
    for i in range(4):
        for k in range(10):assert bpy.data.objects[GUARDS[i*10+k]].parent.name==JOINTS[i][0]
    for n in BREAST:assert bpy.data.objects[n].parent.name=='breastplate'
    changed=GUARDS+BREAST;nodes={o.name:_node(o) for o in bpy.data.objects if o.type=='EMPTY'}
    protected={o.name:_mesh(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in changed}
    contracts=[]
    for i,(name,pos) in enumerate(JOINTS):
        root=Vector(pos);distal=Vector(JOINTS[i+1][1]) if i<3 else bpy.data.objects['head'].matrix_world.translation.copy()
        assert distal.z>root.z+.045
        for k,sector in enumerate(SECTORS):
            o=bpy.data.objects[GUARDS[i*10+k]];verts,faces,spans=_surface(i,sector,root,distal)
            _replace(o,verts,faces);contracts.append({'name':o.name,'owner':name,'root':list(root),'distal':list(distal),'columnCoverage':spans})
    # Cut a restrained upper receiving edge. No flared spherical collar; all
    # lower breast geometry is retained, and this mating seat stays door-owned.
    for n in BREAST:
        o=bpy.data.objects[n];old=o.data;o.data=old.copy();o.data.name=n+' V26 local root-yaw receiving seat';inv=o.matrix_world.inverted()
        low=1.270;upper=1.354;maximum=0
        points=[o.matrix_world@v.co for v in o.data.vertices];top=max(v.z for v in points);root=Vector(JOINTS[0][1])
        for v,p in zip(o.data.vertices,points):
            q=p.copy()
            if p.z>low:
                dz=p.z-root.z;target=math.sqrt(.223**2-dz**2)
                radial=Vector((p.x,p.y-root.y,0));radius=radial.length
                t=max(0,min(1,(p.z-low)/.035));t=t*t*(3-2*t)
                if radius>1e-8:
                    radial*=((radius*(1-t)+target*t)/radius);q.x=radial.x;q.y=root.y+radial.y
            v.co=inv@q;maximum=max(maximum,(q-p).length)
        o.data.update();o['geometryStatus']='V26 local spherical upper breast receiving seat proposal; opening sweep not certified'
        contracts.append({'name':n,'owner':'breastplate','lowerGeometryExactAtOrBelowZ':low,'receivingSphereRadiusM':.223,'maximumDisplacementM':maximum})
    bpy.context.view_layer.update()
    assert nodes=={o.name:_node(o) for o in bpy.data.objects if o.type=='EMPTY'}
    assert all(_mesh(bpy.data.objects[n])==s for n,s in protected.items())
    return {'region':'whole cervical guard envelopes','status':'inferred construction proposal; coarse appearance and strict pose screen required',
        'changedMeshes':changed,'added':[],'removed':[],'changedNodes':[], 'nodesExact':len(nodes),'outsideMeshesExact':len(protected),
        'contracts':contracts,'coverage':'All forty wide cores replaced by finite spherical mating portions and short curved transitions; upper six breast panels/backing receive the root sphere. Passive, original eras/material assignments retained.',
        'parameters':{'wallM':WALL,'matingSphereRadiusDifferenceM':.008,'totalPitchRangeRad':[-.14,.65],'rootYawRangeRad':[-.45,.45],'endpointAnglesOnly':True},
        'limits':['Qualitative construction proposal, not engineering.','Endpoint envelope calculations require strict rendered multi-pose checks, including intermediate angles.','Inherited protected head neighbors and non-owned fixed body receivers remain independent limitations.','No head geometry, lower body, material definition, rig rest or runtime changes.']}
