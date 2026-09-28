"""Head construction proposal; July controls head only. Loaded-scene patch.

All coordinates are proposed authoring choices (Z up, -Y forward), not
measurements recovered from the perspective reference. No biological skin.
"""
import math
import bpy
import bmesh
from mathutils import Vector


def smooth(t):
    t=max(0,min(1,t)); return t*t*(3-2*t)


def spline(rows,t):
    u=max(0,min(1,t))*(len(rows)-1);i=min(int(u),len(rows)-2);v=u-i
    a,b,c,d=rows[max(0,i-1)],rows[i],rows[i+1],rows[min(i+2,len(rows)-1)]
    return Vector([.5*(2*b[k]+(-a[k]+c[k])*v+(2*a[k]-5*b[k]+4*c[k]-d[k])*v*v+(-a[k]+3*b[k]-3*c[k]+d[k])*v*v*v) for k in range(len(b))])


def world(o): return [o.matrix_world@v.co for v in o.data.vertices]


def install(name,verts,faces,flat=False):
    o=bpy.data.objects[name];old=o.data;inv=o.matrix_world.inverted()
    m=bpy.data.meshes.new(name+' formed v15');m.from_pydata([inv@Vector(p) for p in verts],[],faces);m.update()
    for mat in old.materials:
        if mat:m.materials.append(mat)
    o.data=m
    if not old.users:bpy.data.meshes.remove(old)
    bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free()
    for p in m.polygons:p.use_smooth=not flat


def relocate(name,pts):
    o=bpy.data.objects[name];inv=o.matrix_world.inverted()
    for v,p in zip(o.data.vertices,pts):v.co=inv@p
    o.data.update()


def strip(rows,side,along=48,across=8):
    # centre X/Y/Z, half-width in YZ, finite wall along X.
    pts=[];faces=[];s=across+1;n=(along+1)*s
    for skin in (0,1):
        for j in range(along+1):
            t=j/along;q=spline(rows,t);a=spline(rows,max(0,t-.002));b=spline(rows,min(1,t+.002))
            dy,dz=b.y-a.y,b.z-a.z;length=max(1e-8,math.hypot(dy,dz))
            for k in range(s):
                u=k/across;off=(2*u-1)*q[3]
                x=q.x+(.0018*math.sin(math.pi*u) if skin==0 else -.006)
                pts.append(Vector((side*x,q.y-dz/length*off,q.z+dy/length*off)))
    for j in range(along):
        for k in range(across):
            a=j*s+k;faces.extend([(a,a+1,a+s+1,a+s),(n+a+s,n+a+s+1,n+a+1,n+a)])
        a=j*s;b=a+s;faces.append((a,b,n+b,n+a));a+=across;b+=across;faces.append((b,a,n+a,n+b))
    for k in range(across):
        faces.append((k+1,k,n+k,n+k+1));a=along*s+k;faces.append((a,a+1,n+a+1,n+a))
    return pts,faces


def apply():
    changed=[]
    # The round eye belongs inside a broad forged socket that returns into the
    # forehead, bill root and rear cheek. It must not sit on a projecting tube.
    for side in (-1,1):
        verts=[];faces=[];segments=64;columns=7;n=segments*columns
        cy,cz=-.43575,1.7494
        # An enclosing skull plate, not a circular enlarged washer. Stations
        # run from rear cheek over forehead to bill root and lower return.
        outline=[(-.288,1.754),(-.328,1.837),(-.433,1.869),(-.521,1.839),(-.579,1.755),(-.522,1.676),(-.423,1.649),(-.337,1.666),(-.288,1.754)]
        def socket_point(a,f):
            ca,sa=math.cos(a),math.sin(a);outer=spline(outline,(a%math.tau)/math.tau)
            yy=(cy+.073*ca)*(1-f)+outer.x*f
            zz=(cz+.072*sa)*(1-f)+outer.y*f
            edge_x=.157-.34*max(0,-yy-.45)+.035*max(0,yy+.42)
            xx=.149*(1-f)+edge_x*f
            return Vector((side*xx,yy,zz))
        for skin in (0,1):
            for k in range(segments):
                a=math.tau*k/segments
                for j in range(columns):
                    f=j/(columns-1)
                    p=socket_point(a,f);p.x-=side*.006*skin;verts.append(p)
        for k in range(segments):
            nxt=(k+1)%segments
            for j in range(columns-1):
                a=k*columns+j;b=nxt*columns+j
                faces.extend([(a,b,b+1,a+1),(n+a+1,n+b+1,n+b,n+a)])
            a=k*columns;b=nxt*columns;faces.append((b,a,n+a,n+b))
            a+=columns-1;b+=columns-1;faces.append((a,b,n+b,n+a))
        name=f'Forged orbital mounting plate {side}';install(name,verts,faces);changed.append(name)
        rows=[(.143,-.337,1.677,.014),(.155,-.382,1.643,.022),(.141,-.443,1.642,.019),(.116,-.501,1.658,.016),(.098,-.546,1.678,.010)]
        pts,faces=strip(rows,side)
        name=f'Broad swept cheek band {side}';install(name,pts,faces);changed.append(name)
        # Retained six fixings reseated to this actual supporting plate.
        pins=[]
        for o in bpy.data.objects:
            if o.type=='MESH' and o.name.startswith('Recessed cheek fixing'):
                p=world(o);c=sum(p,Vector())/len(p)
                if c.x*side>0:pins.append((c.y,o,p,c))
        targets=[pts[j*9+4] for j in (8,24,40)]
        for (_,o,p,c),target in zip(sorted(pins,key=lambda x:x[0]),sorted(targets,key=lambda x:x.y)):
            delta=Vector((side*(side*target.x-.001-min(side*v.x for v in p)),target.y-c.y,target.z-c.z))
            relocate(o.name,[v+delta for v in p]);changed.append(o.name)
        # Orbital pins now follow the broad support, not empty space.
        pins=sorted([o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(f'Orbital mounting fixing {side} ')],key=lambda o:o.name)
        for o,a in zip(pins,[.18,.78,1.6,2.42,3.72]):
            target=socket_point(a,.74)
            p=world(o);c=sum(p,Vector())/len(p);delta=Vector((side*(side*target.x-.001-min(side*v.x for v in p)),target.y-c.y,target.z-c.z))
            relocate(o.name,[v+delta for v in p]);changed.append(o.name)
        # Deliberate swept forehead seam above the socket; same fixed owner.
        rows=[(.154,-.318,1.819,.013),(.155,-.366,1.855,.017),(.136,-.429,1.858,.020),(.109,-.493,1.823,.021),(.083,-.546,1.777,.015)]
        pts,faces=strip(rows,side);name=f'Forged orbital brow {side}';install(name,pts,faces);changed.append(name)

    # Deep hooked upper blade with a broad flattened side; a separate distal
    # cutting plate and a real seam survive in changing light.
    outer=[(-.494,1.795),(-.572,1.778),(-.654,1.725),(-.708,1.651),(-.735,1.550),(-.725,1.458),(-.688,1.395)]
    inner=[(-.494,1.640),(-.550,1.623),(-.593,1.586),(-.626,1.551),(-.653,1.514),(-.675,1.452),(-.688,1.395)]
    widths=[(.083,0),(.090,0),(.077,0),(.058,0),(.038,0),(.020,0),(.0008,0)]
    for part,(start,end) in enumerate([(0,.54),(.548,1)]):
        pts=[];faces=[];rows=42;segments=48
        for j in range(rows+1):
            t=start+(end-start)*j/rows;o=spline(outer,t);i=spline(inner,t);w=spline(widths,t)[0]
            for k in range(segments):
                a=math.tau*k/segments;cross=1-2*abs((a+math.pi)%math.tau-math.pi)/math.pi;s=math.sin(a)
                # Squared side walls with a bevel into dorsal/cutting ridges.
                x=w*math.copysign(min(1,abs(s)*1.75),s)
                pts.append(Vector((x,(o.x+i.x)/2+(o.x-i.x)*cross/2,(o.y+i.y)/2+(o.y-i.y)*cross/2)))
        for j in range(rows):
            for k in range(segments):
                a=j*segments+k;b=j*segments+(k+1)%segments;faces.append((a,b,b+segments,a+segments))
        faces.extend([tuple(reversed(range(segments))),tuple(rows*segments+k for k in range(segments))])
        name=f'Profiled upper bill blade {part}';install(name,pts,faces);changed.append(name)

    # Forked lower cutting jaw: a downward curved rear arm returns upward at
    # the distal tip. The existing journal and jaw owner are retained.
    # The July head reference is open in action. Neutral rests closer to the
    # owner target: keep the curved jaw, reserve the large gape for its pivot.
    rows=[(.126,-.350,1.661,.012),(.117,-.394,1.614,.025),(.105,-.462,1.575,.025),(.082,-.526,1.536,.021),(.059,-.590,1.515,.015),(.042,-.632,1.523,.008)]
    for side in (-1,1):
        pts,faces=strip(rows,side);name=f'Forked forged mandible {side}';install(name,pts,faces);changed.append(name)
    # Closed distal bridge, follows the same jaw and meets both forged arms.
    pts=[];faces=[];segments=24
    for y,z,w,d in [(-.610,1.519,.052,.004),(-.632,1.523,.043,.005),(-.639,1.526,.040,.003)]:
        for k in range(segments):
            a=math.tau*k/segments;pts.append(Vector((w*math.cos(a),y,z+d*math.sin(a))))
    for j in range(2):
        for k in range(segments):
            a=j*segments+k;b=j*segments+(k+1)%segments;faces.append((a,b,b+segments,a+segments))
    faces.extend([tuple(reversed(range(segments))),tuple(2*segments+k for k in range(segments))])
    install('Distal mandible bridge',pts,faces);changed.append('Distal mandible bridge')

    # Compact the complete crown, including support and fasteners. The nape
    # remains rounded; no long feathers or wing geometry are imported.
    def crown(p):
        q=p.copy();rear=smooth((p.y+.36)/.45)
        q.x*=1-.12*rear;q.y-=.072*rear
        q.z+=.045*rear*smooth((1.76-p.z)/.28)
        return q
    for o in list(bpy.data.objects):
        if o.type!='MESH' or not o.parent or o.parent.name!='cranial-cover':continue
        old=world(o)
        if 'pin' in o.name.lower():
            c=sum(old,Vector())/len(old);delta=crown(c)-c;new=[p+delta for p in old]
        else:new=[crown(p) for p in old]
        if o.name.startswith('Swept temporal lamina'):
            # Narrow only the trailing tongue, retaining the covered root.
            half=len(new)//2;rows=half//9
            for skin in (0,1):
                for j in range(rows):
                    start=skin*half+j*9;c=sum(new[start:start+9],Vector())/9
                    factor=1-.24*smooth((j/(rows-1)-.44)/.56)
                    for k in range(9):new[start+k]=c+(new[start+k]-c)*factor
        relocate(o.name,new);changed.append(o.name)
    bpy.context.view_layer.update()
    # This is a diagnostic contact landmark, not an articulation pivot. Keep
    # it on the actual leading blade after reshaping rather than in mid-air.
    bill_points=[p for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name=='upper-bill' for p in world(o)]
    contact=min(bill_points,key=lambda p:p.y)
    landmark=bpy.data.objects['bill-contact'];m=landmark.matrix_world.copy();m.translation=contact;landmark.matrix_world=m
    bpy.context.view_layer.update()
    return {'region':'head','changed':changed,'new':[],
            'controllingReference':'July head only; owner supplied target for recognition',
            'construction':'Deep formed bill, upturned forked mandible, integrated orbital field, compact rigid crown',
            'rigidOwners':['head','upper-bill','jaw','cranial-cover'],
            'eraEligibility':'Inherited passive plates and bearings; all existing advanced-only optic tags unchanged',
            'contactLandmark':{'name':'bill-contact','worldPosition':list(contact),'method':'leading upper-bill world vertex; runtime contact independently solves the actual triangle surface'},
            'limits':['Clearance must be reviewed after composition.','Dimensions and hidden connections remain proposals.','No era material finishing or likeness acceptance.']}
