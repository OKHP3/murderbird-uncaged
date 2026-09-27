"""Local, deterministic reference-informed assembly study. Run with Blender 5.2.

This authors new geometry; it does not reconstruct a certified hidden surface.
Creative output is all rights reserved under NOTICE.md. No network operations.
The editable blend retains separate plates; the GLB batches per moving assembly.
"""
from pathlib import Path
import bpy
import math
import random
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/models/uncaged-study'
OUT.mkdir(parents=True, exist_ok=True)
random.seed(927)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

def material(name, color, metal=.8, rough=.43):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Metallic'].default_value = metal
    bsdf.inputs['Roughness'].default_value = rough
    return mat

bronze = material('Ancient bronze / worn edges', (.30, .19, .083), .78, .43)
patina = material('Bronze / sheltered mineral patina', (.105, .20, .17), .66, .54)
iron = material('Industrial iron repair', (.062, .074, .073), .82, .39)
brass = material('Brass bearing / polished contact', (.51, .36, .16), .82, .32)
dark = material('Recess / blackened bronze', (.019, .026, .023), .55, .48)
ceramic = material('Sealed ceramic cells', (.55, .56, .49), .1, .38)
optic = material('Builder amber optic', (.55, .15, .015), .35, .29)
optic.node_tree.nodes.get('Principled BSDF').inputs['Emission Color'].default_value = (.5, .085, .004, 1)
optic.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value = .7

def group(name, parent=None, pivot=(0,0,0)):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj.location = pivot
    obj.parent = parent
    return obj

root = group('murderbird')
body = group('body', root)
body.scale = (1.08, 1.12, 1)
neck = group('neck', body, (0,-.20,1.35))
head = group('head', neck, (0,-.07,.41))
head.scale = (1.32, 1.32, 1.26)
jaw = group('jaw', head, (0,-.05,-.045))
chest = group('breastplate', body, (-.245,-.225,1.36))
crown = group('cranial-cover', head)
drive = group('winding-drive', body, (0,-.055,1.14))
power = group('power-core', body, (0,-.19,1.19))
mind = group('processing', head, (0,.01,.035))
repair = group('industrial-repairs', body)
optics = group('builder-optics', head)
wing_l = group('left-mantle', body, (.27,.055,1.36))
wing_r = group('right-mantle', body, (-.27,.055,1.36))

def mesh(name, verts, faces, mat, parent):
    data = bpy.data.meshes.new(name)
    data.from_pydata(verts, [], faces)
    data.materials.append(mat)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.parent = parent
    return obj

def bevel(obj, width=.006):
    mod = obj.modifiers.new('Forged plate edge', 'BEVEL')
    mod.width=width; mod.segments=2
    obj.modifiers.new('Weighted corner normals', 'WEIGHTED_NORMAL')
    return obj

def rod(name, a, b, radius, mat, parent, sides=12, end_radius=None):
    a,b=Vector(a),Vector(b); delta=b-a
    rotation=delta.to_track_quat('Z','Y')
    verts=[]
    for center,r in [(a,radius),(b,radius if end_radius is None else end_radius)]:
        for i in range(sides):
            t=i*math.tau/sides
            verts.append(center+rotation@Vector((r*math.cos(t),r*math.sin(t),0)))
    faces=[tuple(reversed(range(sides))),tuple(range(sides,2*sides))]
    for i in range(sides):faces.append((i,(i+1)%sides,(i+1)%sides+sides,i+sides))
    o=mesh(name,verts,faces,mat,parent)
    for poly in o.data.polygons[2:]:poly.use_smooth=True
    return o

def ring(name, center, radius, wire, mat, parent, axis='X', segments=36):
    verts=[]; faces=[]
    for i in range(segments):
        t=i*math.tau/segments
        for j in range(6):
            q=j*math.tau/6
            u=(radius+wire*math.cos(q))*math.cos(t)
            v=(radius+wire*math.cos(q))*math.sin(t)
            w=wire*math.sin(q)
            p=(w,u,v) if axis=='X' else (u,w,v) if axis=='Y' else (u,v,w)
            verts.append(tuple(center[k]+p[k] for k in range(3)))
    for i in range(segments):
        for j in range(6):
            a=i*6+j; b=((i+1)%segments)*6+j
            faces.append((a,b,((i+1)%segments)*6+(j+1)%6,i*6+(j+1)%6))
    o=mesh(name,verts,faces,mat,parent)
    for p in o.data.polygons: p.use_smooth=True
    return o

def tube(name, points, radii, mat, parent, sides=10):
    verts=[]; faces=[]
    for i,p in enumerate(points):
        tangent=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])
        rot=tangent.to_track_quat('Z','Y')
        for j in range(sides):
            t=j*math.tau/sides
            verts.append(Vector(p)+rot@Vector((radii[i]*math.cos(t),radii[i]*math.sin(t),0)))
    for i in range(len(points)-1):
        for j in range(sides):
            a=i*sides+j;b=i*sides+(j+1)%sides
            faces.append((a,b,b+sides,a+sides))
    faces.extend([tuple(reversed(range(sides))),tuple((len(points)-1)*sides+j for j in range(sides))])
    o=mesh(name,verts,faces,mat,parent)
    for p in o.data.polygons: p.use_smooth=True
    return o

def plate(name, center, width, length, mat, parent, rotation=(0,0,0)):
    # Curved, tapered overlapping metal leaf, with a rolled lip; not flight feathers.
    outline=[(-.5,0),(-.54,.22),(-.43,.61),(-.19,.90),(0,1),(.26,.88),(.48,.53),(.5,.1)]
    verts=[]
    for depth in (0,-.009):
        verts += [(u*width, v*length, depth+.025*math.sin(v*math.pi)-.026*(u*2)**2) for u,v in outline]
    faces=[tuple(range(8)),tuple(reversed(range(8,16)))]
    for i in range(8): faces.append((i,(i+1)%8,(i+1)%8+8,i+8))
    o=bevel(mesh(name,verts,faces,mat,parent),.003)
    o.location=center;o.rotation_euler=rotation
    bpy.context.view_layer.update()
    # Edge outline follows the actual leaf; each rivet belongs to its plate.
    for idx in [0,1,2,3,4,5,6,7]:
        a=Vector(verts[idx]);b=Vector(verts[(idx+1)%8]);a.z+=.002;b.z+=.002
        rod(name+' edge',a,b,.0018,bronze,o,6)
    for u in [-.29,.29]:
        rod(name+' rivet',(u*width,.06*length,.005),(u*width,.06*length,.013),.007,brass,o,8)
    return o

def loft(name, sections, mat, parent, segments=24, start=0, span=math.tau, thickness=0):
    # Z rings with individual center Y and elliptical radii. Nonuniform outline
    # follows selected head/neck/body landmarks, not a scaled bird primitive.
    verts=[];faces=[]
    for z,cy,rx,ry in sections:
        for i in range(segments+1):
            t=start+span*i/segments
            verts.append((math.sin(t)*rx,cy-math.cos(t)*ry,z))
    for j in range(len(sections)-1):
        for i in range(segments):
            k=j*(segments+1)+i;faces.append((k,k+1,k+segments+2,k+segments+1))
    obj=mesh(name,verts,faces,mat,parent)
    if thickness:
        mod=obj.modifiers.new('Plate wall thickness','SOLIDIFY');mod.thickness=thickness
    for p in obj.data.polygons:p.use_smooth=True
    return obj

# Load-bearing pelvic frame and open ribs. Front breastplate is a true cover.
for s in [-1,1]:
    tube('Pelvic rail',[(s*.18,.15,.83),(s*.27,.10,1.0),(s*.25,.07,1.34),(s*.16,-.12,1.46)],[.046,.036,.034,.03],dark,body)
for z,rx,ry in [(1.0,.23,.24),(1.14,.28,.27),(1.30,.26,.22),(1.40,.19,.15)]:
    ring('Transverse rib',(0,.07,z),1,.013,bronze,body,'Z',32).scale=(rx,ry,1)
rod('Spinal transmission housing',(0,.18,.90),(0,.16,1.49),.043,dark,body)
for z in [.94,1.02,1.10,1.18,1.26,1.34,1.42]:
    ring('Spine collar',(0,.17,z),.047,.006,brass,body,'Z')
loft('Rear armor',[(.85,.12,.14,.17),(.98,.10,.26,.26),(1.19,.08,.29,.28),(1.37,.02,.24,.20),(1.45,-.03,.13,.13)],dark,body,24,math.pi/2,math.pi,.015)
sections=[(.91,.08,.14,.20),(1.02,.06,.23,.27),(1.19,.01,.26,.29),(1.34,-.04,.21,.23),(1.44,-.09,.12,.14)]
cover=loft('Formed breast shell',sections,bronze,chest,24,-math.pi/2,math.pi,.012)
cover.location=(.245,.225,-1.36)
for row in range(5):
    z=1.37-row*.085
    width=.19+math.sin(row/4*math.pi)*.26
    for col in range(3):
        x=(col-1)*width/3
        y=-.27-.014*math.sin(row*.8)+abs(x)*.21
        plate('Breast overlapping armor',(x+.245,y+.225,z-1.36),width/2.6,.125,patina if (row+col)%3 else bronze,chest,(-math.pi/2,0,(col-1)*-.12))

# Broad hips, articulated legs, supported three-toed feet and hooked claws.
for s,label in [(1,'left'),(-1,'right')]:
    hip=(s*.20,.085,.91); knee=(s*.255,-.07,.61); ankle=(s*.255,.035,.30);foot=(s*.255,-.035,.095)
    for p,rad in [(hip,.08),(knee,.07),(ankle,.057)]:
        rod(label+' joint axle',(p[0]-.055,p[1],p[2]),(p[0]+.055,p[1],p[2]),rad,iron,body,24)
        ring(label+' bearing',(p[0]+s*.062,p[1],p[2]),rad*.78,.010,brass,body)
        rod(label+' joint pin',(p[0]+s*.06,p[1],p[2]),(p[0]+s*.073,p[1],p[2]),rad*.35,bronze,body)
    tube(label+' thigh',[hip,(s*.255,.02,.77),knee],[.082,.071,.055],iron,body)
    for d in [-.035,.035]:
        rod(label+' actuator body',(hip[0]+d,hip[1]-.025,hip[2]-.03),(knee[0]+d,knee[1]-.035,knee[2]+.05),.024,bronze,body)
        rod(label+' shin piston',(knee[0]+d,knee[1],knee[2]),(ankle[0]+d,ankle[1],ankle[2]),.019,brass,body)
    tube(label+' tarsus',[ankle,(s*.255,-.015,.15),foot],[.048,.041,.058],iron,body)
    for k in range(4):
        ring(label+' ankle cuff',(s*.255,.026-k*.016,.27-k*.046),.047,.005,bronze,body,'Z')
    for j in [-1,0,1]:
        x=foot[0]+j*.08; tipy=-.38+(abs(j)*.034)
        toe=[foot,(x,-.13,.067),(x+j*.023,-.23,.059),(x+j*.025,tipy+.045,.042)]
        tube(label+' segmented toe',toe,[.034,.032,.027,.022],dark,body)
        for k in [1,2]:ring(label+' toe cuff',toe[k],.032 if k==1 else .027,.006,bronze,body,'Y',20)
        tube(label+' curved talon',[toe[-1],(x+j*.03,tipy,.058),(x+j*.04,tipy-.050,.038),(x+j*.04,tipy-.065,.008)],[.026,.024,.015,.0006],iron,body)
    tube(label+' rear toe',[foot,(s*.28,.105,.055),(s*.31,.16,.011)],[.033,.023,.001],bronze,body)

# Compact mantles: three scalloped rows and a short rear contour, no long train.
for s,wing in [(1,wing_l),(-1,wing_r)]:
    loft('Mantle understructure',[(-.40,.17,.05,.10),(-.25,.12,.105,.20),(-.08,.04,.14,.23),(.02,0,.06,.16)],dark,wing,20,0,math.tau,.009)
    for row in range(4):
        for col in range(4):
            plate('Compact mantle plate',(s*(.09+math.sin((col+1)/5*math.pi)*.09),-.13+col*.095,-row*.070),.12,.22-row*.014,patina if (row+col)%4 else bronze,wing,(-.67,s*.72,s*-.15))
    rod('Shoulder axle',(-.045,0,0),(.045,0,0),.085,iron,wing,28)
    ring('Shoulder bearing',(s*.055,0,0),.061,.010,brass,wing)
    # Shoulder cap is segmented, not a giant decorative gear.
    for i in range(5):
        t=i*math.tau/5
        rod('Shoulder fastener',(s*.062,math.sin(t)*.070,math.cos(t)*.070),(s*.073,math.sin(t)*.070,math.cos(t)*.070),.007,bronze,wing,8)
for row in range(3):
    for j in [-1,0,1]:plate('Rear overlap',(j*.08,.14+row*.067,1.40-row*.075),.11,.20,patina,body,(-.3,j*.2,j*.15))

# Anatomical left: inherited limited-travel shoulder repair; topology is proposal.
for z in [1.33,1.40]:
    rod('Left shoulder repair strap',(.315,-.065,z),(.34,.15,z-.035),.015,iron,repair)
    for y in [-.04,.115]:rod('Repair peened pin',(.32,y,z-.014),(.358,y,z-.014),.012,brass,repair)

# S-shaped strong neck: open articulation at rear, overlapping front armor.
tube('Neck load path',[(0,.025,0),(0,-.065,.16),(0,-.03,.29),(0,-.07,.41)],[.078,.071,.07,.061],dark,neck)
for row in range(5):
    z=.06+row*.07;cy=-.015-.055*math.sin(row/4*math.pi)
    ring('Neck collar',(0,cy,z),.093,.014,bronze,neck,'Z')
    for side in [-1,0,1]:
        plate('Neck armor',(side*.065,cy-.09,z+.07),.085,.13,patina if row%3 else bronze,neck,(-math.pi/2,0,side*-.24))
    for s in [-1,1]:rod('Neck tendon',(s*.065,cy+.035,z-.025),(s*.062,cy+.035,z+.05),.009,brass,neck)

# Cranial shell has a removed roof in inspection mode, leaving a real cavity.
loft('Cranial lower shell',[(-.10,.025,.08,.12),(-.04,.008,.14,.16),(.04,0,.145,.18),(.115,.006,.102,.14)],dark,head,24,0,math.tau,.008)
for row in range(3):
    for j in [-1,0,1]:
        plate('Crown segment',(j*.065,-.105+row*.067,.125-row*.013),.09,.17,patina,crown,(.35,j*.42,j*-.1))
for s in [-1,1]:
    # Eye axis is lateral. Bronze housing, dark recess, amber Builder lens only.
    center=(s*.142,-.091,.043)
    rod('Optic recess',(s*.134,-.091,.043),(s*.155,-.091,.043),.068,dark,head,40)
    ring('Optic outer housing',(s*.164,-.091,.043),.068,.011,bronze,head)
    ring('Optic contact ring',(s*.176,-.091,.043),.048,.007,brass,head)
    rod('Amber optical element',(s*.159,-.091,.043),(s*.174,-.091,.043),.038,optic,optics,32)
    for i in range(8):
        t=i*math.tau/8
        rod('Optic fastener',(s*.166,-.091+.077*math.sin(t),.043+.077*math.cos(t)),(s*.177,-.091+.077*math.sin(t),.043+.077*math.cos(t)),.005,brass,head,8)
    for row in range(3):
        plate('Cheek guard',(s*.118,.02+row*.038,.060-row*.038),.095,.115,bronze if row==0 else patina,head,(-.4,s*1.05,.1))

# Swept cheek/occipital scales and broad collar cover the side silhouette.
for s in [-1,1]:
    for row in range(4):
        plate('Swept occipital armor',(s*(.092+row*.008),.085+row*.02,.12-row*.038),.095,.16,patina,head,(-.65,s*1.07,0))
    for row in range(5):
        plate('Lateral neck armor',(s*.087,-.015,.35-row*.067),.105,.14,patina,neck,(-1.05,s*.85,s*.12))
    wing=wing_l if s==1 else wing_r
    for row in range(4):
        plate('Mantle leading edge',(s*.10,-.15,-row*.075),.14,.17,patina,wing,(-1.0,s*.65,s*-.35))

# Deep recurved bill: tailored profile with elliptical transverse sections.

def bill(name, profile, parent, mat):
    verts=[];faces=[];n=12
    for y,z,width,depth in profile:
        for i in range(n):
            t=math.tau*i/n;verts.append((math.cos(t)*width,y+math.sin(t)*depth,z))
    for k in range(len(profile)-1):
        for i in range(n):faces.append((k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i))
    faces+=[tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))]
    o=bevel(mesh(name,verts,faces,mat,parent),.003)
    for p in o.data.polygons:p.use_smooth=True
    return o
bill('Hooked upper bill',[(-.15,.118,.082,.06),(-.22,.095,.09,.077),(-.30,.020,.075,.079),(-.349,-.074,.050,.050),(-.350,-.151,.027,.027),(-.322,-.215,.001,.001)],head,bronze)
bill('Lower mandible',[(-.085,-.003,.072,.045),(-.19,-.071,.068,.034),(-.245,-.085,.038,.02),(-.289,-.078,.003,.001)],jaw,iron)
for s in [-1,1]:
    for y,z in [(-.19,.10),(-.267,.043),(-.32,-.055)]:
        rod('Bill peened fastener',(s*.066,y,z),(s*.076,y,z),.007,brass,head,8)
    ring('Jaw hinge',(s*.128,-.042,-.043),.039,.009,brass,head)

# Mechanic winding concept: a spring drum, arbor, worm transmission and take-offs.
rod('Spring drum',(-.10,0,0),(.10,0,0),.117,iron,drive,40)
for x in [-.11,.11]:
    ring('Drum rim',(x,0,0),.119,.012,brass,drive)
    for r in [.045,.065,.083,.099]:ring('Visible wound spring',(x,0,0),r,.004,bronze,drive)
rod('Winding arbor',(-.23,0,0),(.22,0,0),.023,brass,drive)
rod('Crank',(.22,0,0),(.22,-.055,-.065),.012,iron,drive)
rod('Crank handle',(.22,-.055,-.065),(.27,-.055,-.065),.012,bronze,drive)
for i in range(13):
    t=i*math.tau/13
    rod('Drive tooth',(.11,math.cos(t)*.113,math.sin(t)*.113),(.11,math.cos(t)*.130,math.sin(t)*.130),.008,brass,drive,6)
for s in [-1,1]:
    tube('Tendon take-off',[(s*.12,.09,1.12),(s*.19,.13,.97),(s*.21,.10,.91)],[.012,.012,.009],brass,body)

# Separate onboard power and cranial processing. No glowing chest reactor.
for x in [-.052,0,.052]:
    rod('Ceramic cell',(x,0,-.095),(x,0,.095),.036,ceramic,power,16)
for z in [-.077,.077]:rod('Power retaining strap',(-.10,-.03,z),(.10,-.03,z),.008,iron,power)
for s in [-1,1]:
    rod('Surge capacitor',(s*.088,.022,-.045),(s*.088,.022,.055),.019,dark,power)
    tube('Insulated power route',[(s*.083,.018,-.02),(s*.10,.085,-.07),(s*.095,.12,-.10)],[.007,.007,.007],iron,power)
for layer in range(4):
    for x in [-.065,0,.065]:rod('Processing lattice rail',(x,-.03,-.01+layer*.019),(x,.085,-.01+layer*.019),.008,ceramic,mind,6)
    for y in [-.025,.025,.078]:rod('Processing crosspiece',(-.069,y,-.01+layer*.019),(.069,y,-.01+layer*.019),.007,bronze,mind,6)

# Conforming armor fields follow each load-bearing volume. The plate seams
# establish construction without exposing a naked primitive torso/neck.
for obj in list(bpy.context.scene.objects):
    if obj.type == 'MESH' and any(obj.name.startswith(prefix) for prefix in [
        'Breast overlapping armor','Compact mantle plate','Mantle leading edge',
        'Lateral neck armor','Neck armor']):
        bpy.data.objects.remove(obj, do_unlink=True)

def shell_scales(name, profiles, rows, cols, theta_start, theta_span, parent, pivot=(0,0,0), x_center=0):
    profiles=sorted(profiles)
    def surface(z,t,offset):
        z=max(profiles[0][0],min(profiles[-1][0],z))
        a,b=profiles[0],profiles[-1]
        for k in range(len(profiles)-1):
            if profiles[k][0]<=z<=profiles[k+1][0]:a,b=profiles[k],profiles[k+1];break
        f=(z-a[0])/(b[0]-a[0]) if a[0]!=b[0] else 0
        cy,rx,ry=[a[k]+(b[k]-a[k])*f for k in range(1,4)]
        return (x_center+math.sin(t)*(rx+offset)-pivot[0],cy-math.cos(t)*(ry+offset)-pivot[1],z-pivot[2])
    top,bottom=profiles[-1][0],profiles[0][0]
    step=(top-bottom)/rows
    for row in range(rows):
        z=top-row*step
        for col in range(cols):
            t=theta_start+(col+.5+(row%2)*.21)*theta_span/cols
            outline=[(-.5,0),(-.55,.30),(-.43,.83),(0,1.10),(.43,.83),(.55,.30),(.5,0)]
            verts=[]
            for offset in [.018,.008]:
                verts += [surface(z-v*step,t+u*theta_span/cols,offset) for u,v in outline]
            n=len(outline);faces=[tuple(range(n)),tuple(reversed(range(n,2*n)))]
            for k in range(n):faces.append((k,(k+1)%n,(k+1)%n+n,k+n))
            mat=patina if (col+row)%6 else bronze
            mesh(name,verts,faces,mat,parent)
            for k in range(n):rod(name+' edge',verts[k],verts[(k+1)%n],.0016,bronze,parent,6)
            for u in [-.30,.30]:
                a=surface(z-step*.14,t+u*theta_span/cols,.021)
                b=surface(z-step*.14,t+u*theta_span/cols,.026)
                rod(name+' pin',a,b,.004,brass,parent,6)

shell_scales('Curved breast scale',sections,7,9,-math.pi/2,math.pi,chest,(-.245,-.225,1.36))
shell_scales('Rear fitted scale',[(.85,.12,.14,.17),(.98,.10,.26,.26),(1.19,.08,.29,.28),(1.37,.02,.24,.20),(1.45,-.03,.13,.13)],7,8,math.pi/2,math.pi,body)
for side,wing in [(1,wing_l),(-1,wing_r)]:
    shell_scales('Mantle overlapping scale',[(-.46,.16,.03,.08),(-.35,.16,.10,.17),(-.16,.07,.16,.26),(.015,0,.07,.16)],6,6,0 if side==1 else math.pi,math.pi,wing)
shell_scales('Cervical overlapping scale',[(0,.025,.105,.12),(.11,-.055,.103,.12),(.23,-.040,.11,.125),(.39,-.065,.085,.115)],6,9,-math.pi,math.tau,neck)

# Proportion revision after owner review: shorter exposed legs, deeper torso,
# broader compact neck and a larger skull profile. This is a new study, not approval.
# Named anatomical landmarks export with the geometry, avoiding stale app offsets.
for name,parent,pos in [
    ('bill-contact',head,(0,-.322,-.215)),
    ('anchor-beak',head,(0,-.28,-.035)),
    ('anchor-joint',body,(.28,-.07,.60)),
    ('anchor-shell',chest,(.245,-.01,-.19)),
    ('anchor-drive',drive,(.13,0,0)),
    ('anchor-power',power,(0,-.055,0)),
    ('anchor-mind',mind,(0,0,.04))]:
    group(name,parent,pos)
bpy.context.view_layer.update()
old_neck=neck.matrix_world.translation.copy()
old_head=head.matrix_world.translation.copy()
new_neck=Vector((0,-.28,1.39))
new_head=Vector((0,-.38,1.70))

def domain(obj):
    cursor=obj
    while cursor:
        if cursor==head:return 'head'
        cursor=cursor.parent
    cursor=obj
    while cursor:
        if cursor==neck:return 'neck'
        cursor=cursor.parent
    return 'body'

def body_height(z):
    keys=[(0,0),(.30,.24),(.61,.48),(.91,.72),(1.35,1.39),(1.45,1.51),(2,2.06)]
    for (a,b),(c,d) in zip(keys,keys[1:]):
        if z<=c:return b+(z-a)*(d-b)/(c-a)
    return z+.06

def reshape(p,kind):
    if kind=='head':
        q=p-old_head
        value=new_head+Vector((q.x*1.16,q.y*1.03,q.z*1.15))
    elif kind=='neck':
        fraction=(p.z-old_neck.z)/(old_head.z-old_neck.z)
        center=old_neck.lerp(old_head,fraction)
        newcenter=new_neck.lerp(new_head,fraction)
        value=newcenter+Vector(((p.x-center.x)*1.48,(p.y-center.y)*1.28,0))
    else:value=Vector((p.x*1.10,p.y*1.18,body_height(p.z)))
    return value*1.045

objects=list(bpy.context.scene.objects)
origins={o:reshape(o.matrix_world.translation,domain(o)) for o in objects}
vertices={o:[reshape(o.matrix_world@v.co,domain(o)) for v in o.data.vertices] for o in objects if o.type=='MESH'}
def depth(o):return 0 if not o.parent else 1+depth(o.parent)
for o in sorted(objects,key=depth):
    o.matrix_world=Matrix.Translation(origins[o])
    if o.type=='MESH':
        for v,p in zip(o.data.vertices,vertices[o]):v.co=p-origins[o]
        o.data.update()
bpy.context.view_layer.update()

# Vertex color weathering travels into glTF. Positional variation is bounded;
# shiny contact metals remain distinct from mineral-coated panels.
for obj in list(bpy.context.scene.objects):
    if obj.type!='MESH':continue
    mat=obj.data.materials[0]
    if mat not in [bronze,patina,iron]:continue
    colors=obj.data.color_attributes.new(name='Color',type='BYTE_COLOR',domain='CORNER')
    for i,loop in enumerate(obj.data.loops):
        p=obj.data.vertices[loop.vertex_index].co
        f=.75+.22*(.5+.5*math.sin(p.x*247+p.y*103+p.z*173+len(obj.name)))
        colors.data[i].color=tuple(c*f for c in mat.diffuse_color[:3])+(1,)
    if not mat.node_tree.nodes.get('Vertex wear'):
        attr=mat.node_tree.nodes.new('ShaderNodeVertexColor');attr.name='Vertex wear';attr.layer_name='Color'
        mat.node_tree.links.new(attr.outputs['Color'],mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])

root['status']='Reference-informed assembly study; owner likeness review pending'
root['reference']='assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png'
root['rights']='MurderBird creative content all rights reserved; see NOTICE.md'
root['units']='metres; about 2 m crown height is a production convention, not a story measurement'
for obj in [drive,power,mind]:obj['provenance']='Illustrative reconstruction; internal topology is proposed'
bpy.context.scene.unit_settings.system='METRIC'
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'murderbird-study.blend'))

# Apply modifiers and batch render meshes per named articulated assembly/material.
# The saved .blend above preserves every separately editable plate and fastener.
bpy.context.view_layer.update()
groups=[o for o in bpy.context.scene.objects if o.type=='EMPTY']
for parent in groups:
    descendants=[]
    for o in list(bpy.context.scene.objects):
        if o.type!='MESH':continue
        p=o.parent
        while p and p.type!='EMPTY':p=p.parent
        if p==parent:descendants.append(o)
    if not descendants:continue
    bpy.ops.object.select_all(action='DESELECT')
    for o in descendants:
        world=o.matrix_world.copy();o.parent=parent;o.matrix_world=world
        o.select_set(True)
    bpy.context.view_layer.objects.active=descendants[0]
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.join()
    o=bpy.context.object;o.name=parent.name+'-geometry'
bpy.ops.export_scene.gltf(filepath=str(OUT/'murderbird-study.glb'),export_format='GLB',export_yup=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False)
print('UNCAGED_EXPORT',OUT)
