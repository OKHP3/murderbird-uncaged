"""Rebuild lower cervical guards as a finite continuous neck/breast underlap.

Local reconstruction from visible references; dimensions are authored choices.
Retains rigid owners, rig/driver transforms, era tags and neutral materials.
"""
import math
import bpy,bmesh
from mathutils import Vector

# Curved front/side contour: native world Z, anterior Y, posterior Y, halfwidth.
PROFILE=((1.275,-.312,-.108,.142),(1.305,-.350,-.143,.134),
 (1.335,-.381,-.173,.129),(1.370,-.387,-.180,.119),
 (1.395,-.358,-.180,.111))


def sample(z,col):
    if z<=PROFILE[0][0]:return PROFILE[0][col]
    if z>=PROFILE[-1][0]:return PROFILE[-1][col]
    for a,b in zip(PROFILE,PROFILE[1:]):
        if a[0]<=z<=b[0]:
            t=(z-a[0])/(b[0]-a[0]);t=t*t*(3-2*t)
            return a[col]*(1-t)+b[col]*t


def point(z,angle,offset):
    front,rear,width=[sample(z,k) for k in (1,2,3)]
    return Vector(((width+offset)*math.sin(angle),(front+rear)/2-((rear-front)/2+offset)*math.cos(angle),z))


def install(obj,top,bottom,center,half,offset=.004):
    """Closed evaluated formed wall from a broad rounded-tongue patch."""
    rows=16;cols=16;verts=[];faces=[];inverse=obj.matrix_world.inverted()
    for j in range(rows+1):
        t=j/rows;e=t*t*(3-2*t)
        for k in range(cols+1):
            u=2*k/cols-1
            # A gentle free-edge crown replaces isolated long pointed tongues.
            z=top+(bottom-top)*t-.0035*(1-u*u)*e
            angle=center+half*u*(1-.10*e)
            p=point(z,angle,offset+.002*(1-u*u)*math.sin(math.pi*t))
            verts.append(inverse@p)
    for j in range(rows):
        for k in range(cols):
            i=j*(cols+1)+k;faces.append((i,i+cols+1,i+cols+2,i+1))
    old=obj.data;mesh=bpy.data.meshes.new(obj.name+' V18 reconstructed curved guard')
    mesh.from_pydata(verts,[],faces);mesh.update()
    for m in old.materials:mesh.materials.append(m)
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    # Orient the center of the front sheet toward -Y before solidification.
    mid=mesh.polygons[len(mesh.polygons)//2]
    normal=obj.matrix_world.to_3x3()@mid.normal
    radial=Vector((math.sin(center),-math.cos(center),0))
    if normal.dot(radial)<0:
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    obj.data=mesh
    if not old.users:bpy.data.meshes.remove(old)
    obj.modifiers.clear();wall=obj.modifiers.new('Reconstructed finite formed wall','SOLIDIFY')
    wall.thickness=.005;wall.offset=-1;wall.use_even_offset=True
    bevel=obj.modifiers.new('Small formed edge','BEVEL');bevel.width=.0008;bevel.segments=2
    for p in mesh.polygons:p.use_smooth=True
    return {'name':obj.name,'owner':obj.parent.name,'topWorldZ':top,'bottomWorldZ':bottom,
      'centerAngle':center,'halfAngle':half,'wallM':.005,'outerStandOffM':offset,'grid':[17,17]}


def apply():
    changed=[];guards=[]
    upper=bpy.data.objects['Throat formed lamina 3'];inv=upper.matrix_world.inverted()
    assert len(upper.data.vertices)==169
    # Preserve the attachment/upper rows, easing only the hanging lower rows
    # onto the new lower guard rather than leaving a known disconnected tongue.
    for v in upper.data.vertices:
        row=v.index//13;t=max(0.,min(1.,(row-7)/5));t=t*t*(3-2*t)
        if t:
            p=upper.matrix_world@v.co;p.y+=.065*t;p.z+=.040*t
            v.co=inv@p
    upper.data.update();changed.append(upper.name)
    for n,top,bottom,half in [(4,1.380,1.340,.65),(5,1.347,1.313,.70),(6,1.320,1.289,.71)]:
        obj=bpy.data.objects[f'Throat formed lamina {n}'];guards.append(install(obj,top,bottom,0,half));changed.append(obj.name)
    for side in (-1,1):
        for n,top,bottom in [(5,1.354,1.321),(6,1.328,1.293)]:
            obj=bpy.data.objects[f'Cervical flank lamina {side} {n}']
            guards.append(install(obj,top,bottom,side*1.13,.43));changed.append(obj.name)
    backing=bpy.data.objects['Lower cervical open backing']
    guards.append(install(backing,1.346,1.292,0,1.13,offset=-.009));changed.append(backing.name)
    # Shape the opening edge and its armor together into a descending front
    # shoulder rather than leave a horizontal tank rim around the new neck.
    breast_names=['Breast inner access shell','V17 breast captive overlap fasteners',
      'V17 breast center keel return left','V17 breast center keel return right']
    breast_names += [o.name for o in bpy.data.objects if o.name.startswith('V17 breast directional lamina 1 ')]
    breast_reports=[]
    for name in breast_names:
        obj=bpy.data.objects[name];inv=obj.matrix_world.inverted();count=0
        for vertex in obj.data.vertices:
            p=obj.matrix_world@vertex.co
            upper=max(0.,min(1.,(p.z-1.220)/.105));upper=upper*upper*(3-2*upper)
            front=max(0.,min(1.,(-p.y-.200)/.200));front=front*front*(3-2*front)
            if upper*front>1e-8:
                lateral=min(1.,abs(p.x)/.32)
                p.z-=upper*front*(.040+.021*lateral*lateral)
                p.y+=upper*front*.015
                vertex.co=inv@p;count+=1
        obj.data.update()
        if count:changed.append(name);breast_reports.append({'name':name,'verticesReprofiled':count})
    bpy.context.view_layer.update()
    return {'status':'finite lower-neck reconstruction proposal; visual and sampled movement fit pending',
      'region':'neck','changed':changed,'added':[],'removed':[],'newPivots':[],
      'construction':'Three short curved throat lames and two staggered flank lames per side replace the forward cup and long hanging points; finite close backing and eased third-lame lower edge join the existing upper neck. Lower returns are rigid underlaps behind the breast cover.',
      'profileWorld':PROFILE,'guards':guards,'upperBreastCurve':{'objects':breast_reports,'maximumDropM':.061,'maximumRearwardM':.015,'blendLowerZ':1.220},'upperThirdLameLowerRows':{'firstBlendedRow':8,'maximumRearwardM':.065,'maximumRiseM':.040},
      'preserved':['all rigid owners and transforms','all52pivots and drivers','materials and alleraeligibility','historical guides','breast below the upper-shoulder blend','all non-target meshes'],
      'limits':['Qualitative reference-based shape with proposed dimensions and unseen support.','Rigid overlapping lames are not flexible or driven independently.','Discrete movement, containment and interface fit require independent checks; no physical or owner acceptance.']}
