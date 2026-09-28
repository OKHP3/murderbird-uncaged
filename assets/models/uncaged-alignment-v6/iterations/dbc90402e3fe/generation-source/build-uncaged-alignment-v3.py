"""Region-profile correction from the preserved, editable Stage B source.

Blender metres, +X anatomical left, -Y forward, +Z up. Profiles are authored
interpretations of perspective artwork, not recovered physical dimensions.
No v2 output is changed. A changed v3 source must be versioned before rebuild.
"""
from pathlib import Path
import ast
import hashlib
import json
import math
import bpy
import bmesh
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/models/uncaged-alignment-v3'
BASE = ROOT / 'assets/models/uncaged-neutral-v2/murderbird-neutral-v2.blend'
BASE_SHA = '64ea6d86504987357eb22c2e3c4036ec87da6432f15354f5d4a07d004fd6dec9'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(BASE) == BASE_SHA, 'Reviewed v2 source has changed; reconcile before continuing.'
OUT.mkdir(parents=True, exist_ok=True)
receipt = OUT / 'alignment-inventory.json'
if receipt.exists():
    for row in json.loads(receipt.read_text())['generatedFiles']:
        p = ROOT / row['path']
        assert not p.exists() or sha(p) == row['sha256'], f'Preserve manually edited output in a new version first: {p}'
bpy.ops.wm.open_mainfile(filepath=str(BASE))
bpy.context.scene.frame_set(1)
for obj in bpy.data.objects:
    obj.animation_data_clear()
for action in list(bpy.data.actions):
    bpy.data.actions.remove(action)

# The inherited head has a 1.2 Z scale. A child jaw rotating beneath that
# scale shears in world space. Bake rest transforms into child vertex data
# and pivot offsets, preserving every rest world vertex and joint centre.
bpy.context.view_layer.update()
rest_world={o:o.matrix_world.copy() for o in bpy.data.objects}
normalized_scales=[{'name':o.name,'sourceScale':list(o.scale)} for o in bpy.data.objects if o.type=='EMPTY' and (o.scale-Vector((1,1,1))).length>1e-7]
def depth(obj):
    value=0
    while obj.parent:value+=1;obj=obj.parent
    return value
for o in sorted([o for o in bpy.data.objects if o.type=='EMPTY'],key=depth):
    loc,rot,scale=rest_world[o].decompose()
    o.matrix_world=Matrix.LocRotScale(loc,rot,Vector((1,1,1)))
    bpy.context.view_layer.update()
max_rest_bake_error=0.0
for o in list(bpy.data.objects):
    if o.type!='MESH':continue
    if o.data.users>1:o.data=o.data.copy()
    target_parent=o.parent.matrix_world if o.parent else Matrix.Identity(4)
    transform=target_parent.inverted()@rest_world[o]
    for vertex in o.data.vertices:
        before=rest_world[o]@vertex.co
        vertex.co=transform@vertex.co
        max_rest_bake_error=max(max_rest_bake_error,(target_parent@vertex.co-before).length)
    o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update()
assert max_rest_bake_error<1e-6,max_rest_bake_error
for o in bpy.data.objects:
    if o.type=='EMPTY':assert (o.matrix_world.translation-rest_world[o].translation).length<1e-6,o.name

# Reuse only small geometry primitives, never execute the v2 generation body.
primitive_names = {'material', 'group', 'mesh', 'bevel', 'rod', 'ring', 'tube'}
source = ast.parse((ROOT / 'scripts/build-uncaged-presence-study.py').read_text())
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n, ast.FunctionDef) and n.name in primitive_names], type_ignores=[]), '<preserved-primitives>', 'exec'))
helper_names = {'under', 'tag', 'wm', 'wr', 'wt', 'mix', 'sample', 'envelope', 'polygon_surface', 'patch', 'shell', 'fastener', 'curve'}
ALL = 'maker,mechanic,builder'
source = ast.parse((ROOT / 'scripts/build-uncaged-neutral-v2.py').read_text())
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n, ast.FunctionDef) and n.name in helper_names], type_ignores=[]), '<preserved-profile-helpers>', 'exec'))
ALL = 'maker,mechanic,builder'
mat = {name: bpy.data.materials['Neutral / ' + name] for name in ['plate', 'edge', 'frame', 'recess', 'bearing', 'repair', 'optic', 'inner']}
parts = []
head = bpy.data.objects['head']
crown = bpy.data.objects['cranial-cover']
bill = bpy.data.objects['upper-bill']
jaw = bpy.data.objects['jaw']
neck = bpy.data.objects['neck']
breast = bpy.data.objects['breastplate']
body = bpy.data.objects['body']
original_pivots = {o.name: list(o.location) for o in bpy.data.objects if o.type == 'EMPTY'}

# Keep inherited internal mechanisms, source rig, longitudinal frame and digits.
# Replace visibly generic exterior regions, while each moving part keeps one owner.
for o in list(bpy.data.objects):
    if o.type != 'MESH' or under(o, bpy.data.objects['processing']) or under(o, bpy.data.objects['power-core']):
        continue
    reg = o.get('region', '')
    replace = reg in {'head', 'optic', 'shoulder', 'wing', 'leg'}
    replace |= reg in {'breast', 'neck'} and o.get('surfaceRole') in {'plate', 'bearing'}
    replace |= reg == 'foot' and ('ankle instep' in o.name or 'knuckle guard' in o.name)
    if replace:
        bpy.data.objects.remove(o, do_unlink=True)

controls = bpy.data.collections.new('Editable region profile controls')
bpy.context.scene.collection.children.link(controls)
control_records = []
def control(name, points, owner, kind='profile', closed=False):
    """Preserve inspectable profile curves in native source, exclude from runtime."""
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions = '3D'
    spline = data.splines.new('POLY')
    spline.points.add(len(points)-1)
    inv = owner.matrix_world.inverted()
    for dest, point in zip(spline.points, points):
        dest.co = (* (inv @ Vector(point)), 1)
    spline.use_cyclic_u = closed
    obj = bpy.data.objects.new(name, data)
    controls.objects.link(obj)
    obj.parent = owner
    obj.hide_render = True
    obj.hide_set(True)
    obj['controlRole'] = kind
    obj['dimensionsStatus'] = 'authored proposal; not source metrology'
    control_records.append({'name': name, 'owner': owner.name, 'kind': kind, 'worldPoints': [list(p) for p in points]})
    return obj

def smooth_profile(points, steps=5):
    """Closed Catmull outline through deliberately placed profile corners."""
    out = []
    for i, p1 in enumerate(points):
        p0, p2, p3 = points[(i-1) % len(points)], points[(i+1) % len(points)], points[(i+2) % len(points)]
        for j in range(steps):
            t = j / steps
            out.append(tuple(.5*(2*p1[k]+(-p0[k]+p2[k])*t+(2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*t*t+(-p0[k]+3*p1[k]-3*p2[k]+p3[k])*t*t*t) for k in range(2)))
    return out

def side_plate(name, outline, width_at, owner, reg='head', thickness=.008, smooth=True, role='plate'):
    line = smooth_profile(outline, 3) if smooth else outline
    for side in [-1, 1]:
        projection = lambda y,z: (side*width_at(y,z), y, z)
        patch(f'{name} {side}', line, projection, owner, reg, role, thickness=thickness, sub=3)
        control(f'{name} boundary {side}', [projection(y,z) for y,z in outline], owner, closed=True)

# HEAD. Actual pivot centres are the authority for bearings and swept clearance.
eye_y, eye_z = -.369, 1.786
jp = jaw.matrix_world.translation.copy()
head_sections = [(1.575,-.15,.065,.10), (1.65,-.20,.123,.185), (1.74,-.25,.149,.22), (1.825,-.265,.153,.20), (1.915,-.24,.119,.175), (1.955,-.17,.025,.075)]
shell('Profiled cranial backing', head_sections, crown, 'head', 1.75, math.tau-1.75, 'recess')
for z, cy, rx, ry in head_sections:
    control(f'Skull section {z:.3f}', [envelope(head_sections,z,math.tau*k/24) for k in range(24)], crown, 'cross-section', True)

# Broad uneven temporal/cere arch, narrowing beneath the recessed optic and
# joining the fixed cheek to the real mandible bearing. Preserve the open throat.
cheek = [(-.225,1.796),(-.258,1.841),(-.329,1.829),(-.403,1.849),(-.445,1.818),(-.459,1.738),(-.418,1.702),(-.380,1.706),(-.350,1.660),(-.319,1.607),(-.278,1.635),(-.267,1.697),(-.225,1.733)]
for side in [-1,1]:
    # A polygon with an actual socket hole, cut only against this rigid owner.
    project = lambda y,z: (side*(.138-.20*max(0,-y-.40)+.010*math.sin((z-1.6)*8)), y,z)
    # Build a real annular plate directly; no Boolean against an open sheet.
    socket_outline=[(-.071,.045),(-.033,.078),(.043,.063),(.086,.031),(.077,-.025),(.061,-.085),(.034,-.130),(0,-.112),(-.018,-.079),(-.041,-.064),(-.078,-.043)]
    socket_outline=smooth_profile(socket_outline,5)
    verts=[];faces=[];n=len(socket_outline)
    for dy,dz in socket_outline:
        verts.append(project(eye_y+dy,eye_z+dz))
    for dy,dz in socket_outline:
        length=math.hypot(dy,dz);verts.append(project(eye_y+dy/length*.052,eye_z+dz/length*.052))
    for k in range(n):faces.append((k,(k+1)%n,n+(k+1)%n,n+k))
    o=wm(f'Continuous temporal cheek arch {side}',verts,faces,head,'head');m=o.modifiers.new('Cheek arch wall','SOLIDIFY');m.thickness=.011;bevel(o,.0015)
    control(f'Temporal cheek profile {side}',verts[:n],head,closed=True)
    arm=[(-.288,1.811),(-.251,1.778),(-.262,1.723),(-.281,1.683),(-.306,1.627),(-.321,1.595),(-.355,1.574),(-.371,1.613),(-.351,1.671),(-.346,1.726)]
    patch('Descending fixed cheek arm '+str(side),smooth_profile(arm,3),project,head,'head',thickness=.012,sub=4)
    wr('Inset passive optic housing',(side*.108,eye_y,eye_z),(side*.123,eye_y,eye_z),.050,head,'optic','recess',sides=48)
    # Fine recessed lip; its exterior stays behind the cheek surface.
    verts=[];faces=[];n=48
    for x,r in [(.127,.052),(.133,.052),(.133,.045),(.127,.045)]:
        for k in range(n):t=k*math.tau/n;verts.append((side*x,eye_y+r*math.cos(t),eye_z+r*math.sin(t)))
    for layer in range(4):
        for k in range(n):faces.append((layer*n+k,layer*n+(k+1)%n,((layer+1)%4)*n+(k+1)%n,((layer+1)%4)*n+k))
    wm('Recessed optic lip '+str(side),verts,faces,head,'optic','bearing')
    wr('Seated Advanced optic',(side*.119,eye_y,eye_z),(side*.125,eye_y,eye_z),.036,bpy.data.objects['builder-optics'],'optic','optic','builder',sides=40)
    wr('Coaxial mandible journal',jp+Vector((side*.075,0,0)),jp+Vector((side*.119,0,0)),.032,head,'head','bearing',sides=32)
    wr('Mandible journal cap',jp+Vector((side*.120,0,0)),jp+Vector((side*.126,0,0)),.023,jaw,'head','edge',sides=24)
    for y,z in [(-.253,1.767),(-.303,1.673),(-.425,1.725)]:fastener('Temporal arch recessed fixing',project(y,z),(side,0,0),head,'head',.004)

# Bill: two broad side faces, a dorsal ridge and a tight terminal hook.
# Profile sections have independent depth and breadth instead of a tube sweep.
outer=[(-.421,1.853),(-.493,1.837),(-.571,1.789),(-.638,1.716),(-.674,1.634),(-.678,1.560),(-.657,1.495),(-.622,1.463)]
inner=[(-.420,1.706),(-.482,1.694),(-.538,1.674),(-.585,1.643),(-.620,1.602),(-.641,1.554),(-.642,1.503),(-.622,1.463)]
control('Upper bill convex dorsal profile', [(0,y,z) for y,z in outer], bill)
control('Upper bill cutting profile', [(0,y,z) for y,z in inner], bill)
def blade(t,a):
    oy,oz=curve(outer,t);iy,iz=curve(inner,t)
    # Broad forged root and deep face, thinning more quickly at the hook.
    width=curve([(0.071,),(.075,),(.067,),(.052,),(.037,),(.022,),(.010,),(.0008,)],t)[0]
    cross=1-2*abs((a+math.pi)%math.tau-math.pi)/math.pi
    return (width*math.sin(a),(oy+iy)/2+(oy-iy)/2*cross,(oz+iz)/2+(oz-iz)/2*cross)
for index,(start,end) in enumerate([(0,.245),(.25,1)]):
    vertices=[];faces=[];rows=56;n=40
    for j in range(rows+1):
        for k in range(n):vertices.append(blade(start+(end-start)*j/rows,k*math.tau/n))
    for j in range(rows):
        for k in range(n):a=j*n+k;b=j*n+(k+1)%n;faces.append((a,b,b+n,a+n))
    faces += [tuple(reversed(range(n))),tuple(rows*n+k for k in range(n))]
    o=wm('Profiled upper bill blade '+str(index),vertices,faces,bill,'head')
    for f in o.data.polygons:f.use_smooth=True
for side in [-1,1]:
    side_plate_name='Cere root transition'
    # Connects the cheek arch into the broad bill root, without a rectangular bridge.
    outline=[(-.434,1.832),(-.463,1.842),(-.493,1.824),(-.498,1.772),(-.464,1.731),(-.438,1.747)]
    project=lambda y,z:(side*(.129-.75*max(0,-y-.425)),y,z)
    patch(side_plate_name+' '+str(side),smooth_profile(outline,3),project,bill,'head',thickness=.011,sub=3)
    for t in [.07,.17]:fastener('Bill root fixing',blade(t,side*1.28),(side,0,0),bill,'head',.004)

# Mandible is a closed, broad crescent carried entirely by the jaw. Its rear
# bearing is concentric with the preserved pivot; +X rotation opens downward.
mandible=[(-.339,1.617),(-.392,1.629),(-.445,1.631),(-.496,1.612),(-.551,1.575),(-.592,1.553),(-.627,1.562),(-.607,1.531),(-.561,1.513),(-.517,1.520),(-.466,1.547),(-.414,1.570),(-.365,1.568),(-.325,1.586)]
def jaw_width(y,z):return max(.015,.103-.33*max(0,-y-.37))
side_plate('Crescent mandible',mandible,jaw_width,jaw,thickness=.014)
# Cross-sections make a real lower keel rather than a round wire frame.
mandible_sections=[(-.354,1.576,.094),(-.415,1.574,.089),(-.475,1.551,.071),(-.535,1.526,.050),(-.591,1.534,.028),(-.618,1.550,.012)]
verts=[];faces=[];n=16
for y,z,w in mandible_sections:
    section=[]
    for k in range(n+1):
        a=math.pi*k/n;p=(math.cos(a)*w,y,z-.020*math.sin(a));verts.append(p);section.append(p)
    control(f'Mandible section {y:.3f}',section,jaw,'cross-section')
for j in range(len(mandible_sections)-1):
    for k in range(n):a=j*(n+1)+k;faces.append((a,a+1,a+n+2,a+n+1))
o=wm('Mandible shaped keel',verts,faces,jaw,'head','edge');m=o.modifiers.new('Keel thickness','SOLIDIFY');m.thickness=.008

# Crown roof spans the centreline. Cross-sections are domed laterally rather
# than two vertical side rails; each cap has an explicit backswept boundary.
roof=[(-.454,1.860,.065),(-.370,1.931,.111),(-.272,1.965,.123),(-.161,1.960,.114),(-.049,1.914,.081),(.015,1.852,.031)]
def roof_point(x,y):
    z,w=sample([(p[0],p[1],p[2]) for p in roof],y)
    return (x,y,z-.034*(x/max(.025,w))**2)
for i,(y0,y1,w0,w1) in enumerate([(-.449,-.287,.068,.116),(-.305,-.129,.119,.109),(-.150,.012,.112,.029)]):
    outline=[(-w0,y0),(w0,y0),(w1,y1-.025),(w1*.28,y1),(-w1*.77,y1-.018)]
    patch('Broad swept crown roof '+str(i),outline,roof_point,crown,'head',thickness=.007,sub=7)
    control('Crown roof boundary '+str(i),[roof_point(x,y) for x,y in outline],crown,closed=True)
    for x in [-w0*.64,w0*.64]:fastener('Crown cap fixing',roof_point(x,y0+.03),(0,0,1),crown,'head',.003)
temporal=[(-.25,1.924),(-.14,1.949),(-.035,1.903),(.023,1.818),(.014,1.704),(-.045,1.606),(-.136,1.604),(-.217,1.671),(-.272,1.751),(-.298,1.836)]
def temporal_width(y,z):
    cy,rx,ry=sample(head_sections,z);q=(y-cy)/max(.05,ry)
    return rx*math.sqrt(max(.15,1-q*q))+.004
side_plate('Temporal shaped backing',temporal,temporal_width,crown,thickness=.005,role='frame')
for index,brow in enumerate([
    [(-.450,1.834),(-.399,1.904),(-.345,1.932),(-.326,1.908),(-.378,1.884),(-.409,1.835)],
    [(-.353,1.934),(-.291,1.945),(-.232,1.935),(-.213,1.910),(-.284,1.906),(-.330,1.902)],
    [(-.237,1.936),(-.188,1.910),(-.165,1.879),(-.210,1.872),(-.241,1.903)],
]):
    side_plate('Segmented supraorbital brow '+str(index),brow,lambda y,z:.151-.28*max(0,z-1.82),crown,thickness=.006,smooth=False)
for side in [-1,1]:
    # Deliberate rows have different counts, sweeps and exposed lengths.
    for row,(z,centres,length) in enumerate([(1.913,[-.28,-.22,-.16,-.10,-.04],.086),(1.849,[-.25,-.19,-.13,-.07,-.01],.096),(1.775,[-.205,-.15,-.09,-.03],.109),(1.691,[-.15,-.095,-.04],.096)]):
        for col,y in enumerate(centres):
            outline=[(y-.029,z),(y+.025,z+.003),(y+.041,z-.030),(y+.069,z-length*.80),(y+.033,z-length),(y-.011,z-.050)]
            def project(yy,zz):
                cy,rx,ry=sample(head_sections,zz);q=(yy-cy)/max(.05,ry)
                # Successive roots sit under the preceding free edge. Without
                # this cross-section relief, coplanar blades read as long straps.
                lift=.010+.018*max(0,min(1,(z-zz)/length))
                return (side*(rx*math.sqrt(max(.12,1-q*q))+lift),yy,zz)
            patch(f'Temporal swept blade {side} {row} {col}',outline,project,crown,'head',thickness=.005,sub=4)
            control(f'Temporal blade outline {side} {row} {col}',[project(y,z) for y,z in outline],crown,closed=True)
            fastener('Temporal blade root pin',project(y-.014,z-.014),(side,0,.12),crown,'head',.003)

# Cervical guards follow bowed sections and terminate beneath the head. Large
# throat shields contrast with narrow lateral links; no circumferential rows.
neck_sections=[(1.25,-.095,.205,.208),(1.325,-.15,.177,.19),(1.41,-.23,.147,.17),(1.48,-.283,.127,.148),(1.55,-.296,.12,.14),(1.60,-.276,.123,.143),(1.65,-.25,.121,.144)]
for z,cy,rx,ry in neck_sections:control(f'Cervical section {z:.3f}',[envelope(neck_sections,z,-1.8+3.6*k/18) for k in range(19)],neck,'cross-section')
for i,(z,length,width) in enumerate([(1.648,.121,.68),(1.548,.146,.73),(1.433,.157,.83),(1.315,.112,.92)]):
    outline=[(-width/2,z),(.31*width,z+.004),(.51*width,z-.047),(.18*width,z-length),(-.16*width,z-length*.94),(-.51*width,z-.054)]
    patch('Central cervical shield '+str(i),outline,lambda a,zz:envelope(neck_sections,zz,a,.014),neck,'neck',thickness=.006,sub=4)
    for side in [-1,1]:
        a=side*.89
        shape=[(a-.24,z-.018),(a+.24,z-.005),(a+.27,z-.075),(a+side*.14,z-length*.93),(a-.22,z-length*.74)]
        patch(f'Lateral cervical guard {side} {i}',shape,lambda aa,zz:envelope(neck_sections,zz,aa,.007+.017*max(0,(z-zz)/length)),neck,'neck',thickness=.005,sub=4)
        a=side*1.68
        shape=[(a-.40,z+.003),(a+.40,z-.009),(a+.43,z-length*.54),(a+side*.14,z-length*.91),(a-.33,z-length*.68)]
        patch(f'Cervical side transition {side} {i}',shape,lambda aa,zz:envelope(neck_sections,zz,aa,.006+.017*max(0,(z-zz)/length)),neck,'neck',thickness=.005,sub=4)
        a=side*2.35
        shape=[(a-.34,z-.013),(a+.31,z-.008),(a+.29,z-length*.52),(a+side*.08,z-length*.89),(a-.31,z-length*.73)]
        patch(f'Cervical rear quarter guard {side} {i}',shape,lambda aa,zz:envelope(neck_sections,zz,aa,.007+.014*max(0,(z-zz)/length)),neck,'neck',thickness=.005,sub=4)

# Breast follows the retained envelope but uses a central keel and differently
# sized lateral fields. Explicit boundaries replace evenly repeated shingles.
body_sections=[(.68,.09,.11,.13),(.76,.075,.18,.20),(.88,.045,.255,.265),(1.02,.005,.305,.305),(1.16,-.04,.325,.305),(1.28,-.09,.282,.255),(1.37,-.125,.22,.205)]
fields=[(1.368,.17,.56),(1.226,.19,.64),(1.064,.19,.74),(.901,.16,.78),(.777,.096,.64)]
for row,(z,length,width) in enumerate(fields):
    outline=[(-width*.48,z),(width*.43,z+.004),(width*.52,z-length*.44),(width*.19,z-length*.91),(-.06,z-length),(-width*.5,z-length*.61)]
    project=lambda aa,zz:envelope(body_sections,max(.681,zz),aa,.013+.009*(z-zz)/length)
    patch('Breast central field '+str(row),outline,project,breast,'breast',thickness=.007,sub=5)
    control('Breast central boundary '+str(row),[project(a,b) for a,b in outline],breast,closed=True)
    for side in [-1,1]:
        for column,(centre,w,stagger) in enumerate([(.51,.56,-.011),(1.03,.62,.023)]):
            a=side*centre;top=z+stagger
            outline=[(a-w*.51,top),(a+w*.49,top-.015),(a+w*.52,top-length*.45),(a+side*.05,top-length*.92),(a-w*.48,top-length*.64)]
            proj=lambda aa,zz:envelope(body_sections,max(.681,zz),aa,.010+.021*max(0,(top-zz)/length))
            patch(f'Breast oblique field {side} {row} {column}',outline,proj,breast,'breast',thickness=.006,sub=5)
            for angle in [a-.15,a+.15]:fastener('Breast field fixing',proj(angle,top-.025),(math.sin(angle),-math.cos(angle),.1),breast,'breast',.0035)

# Mantle cross-sections flatten the shoulder into a tapered folded contour.
# Upper and distal shells share overlap but never share deforming vertices.
wing_sections=[(.765,.29,.008,.02),(.81,.27,.035,.075),(.88,.245,.075,.16),(1.015,.17,.136,.235),(1.16,.095,.164,.266),(1.29,.035,.153,.228),(1.39,.02,.098,.155),(1.445,.025,.016,.055)]
def wing_point(side,a,z,lift=0):
    cy,rx,ry=sample(wing_sections,z)
    return (side*(.315+math.cos(a)*(rx+lift)),cy+math.sin(a)*(ry+lift),z)
for side,label in [(1,'left'),(-1,'right')]:
    upper=bpy.data.objects[label+'-mantle'];lower=bpy.data.objects[label+'-wing-shield']
    for z,cy,rx,ry in wing_sections:control(label+f' mantle section {z:.3f}',[wing_point(side,math.tau*k/24,z) for k in range(24)],upper if z>1.08 else lower,'cross-section',True)
    for top,bottom,owner in [(1.444,1.066,upper),(1.10,.791,lower)]:
        vertices=[];faces=[];n=28
        for j in range(15):
            z=top+(bottom-top)*j/14
            for k in range(n+1):vertices.append(wing_point(side,-math.pi+math.tau*k/n,z,-.018))
        for j in range(14):
            for k in range(n):a=j*(n+1)+k;faces.append((a,a+1,a+n+2,a+n+1))
        o=wm(label+' profiled mantle backing '+owner.name,vertices,faces,owner,'shoulder' if owner==upper else 'wing','frame');m=o.modifiers.new('Shell thickness','SOLIDIFY');m.thickness=.005
        for f in o.data.polygons:f.use_smooth=True
    rows=[(1.423,.102,5,upper),(1.351,.13,6,upper),(1.249,.157,5,upper),(1.133,.166,4,upper),(1.038,.202,4,lower),(.931,.156,3,lower)]
    for row,(z,length,count,owner) in enumerate(rows):
        for col in range(count):
            a=-1.32+2.64*(col+.5)/count
            width=2.70/count
            swept=.12+.04*row
            outline=[(a-width*.49,z),(a+width*.44,z+.01*math.sin(col)),(a+width*.45+swept,z-length*.49),(a+swept,z-length),(a-width*.29+swept*.6,z-length*.81),(a-width*.48,z-length*.35)]
            outline=[(aa,max(.766,zz)) for aa,zz in outline]
            project=lambda aa,zz:wing_point(side,aa,zz,.010+.016*(z-zz)/length)
            reg='shoulder' if owner==upper else 'wing'
            patch(f'{label} graduated mantle plate {row} {col}',outline,project,owner,reg,thickness=.005,sub=4)
            fastener('Mantle plate root pin',project(a,z-.017),(side,0,.15),owner,reg,.003)
    # An oblique saddle fills the visible shoulder/neck transition on the moving side.
    saddle=[(-1.68,1.285),(-.88,1.391),(-.28,1.445),(.31,1.443),(.75,1.393),(.43,1.356),(-.25,1.389),(-1.04,1.288)]
    patch(label+' oblique shoulder saddle',saddle,lambda a,z:wing_point(side,a,z,.012),upper,'shoulder',thickness=.007,sub=5)
    a=upper.matrix_world.translation.copy();b=lower.matrix_world.translation.copy()
    wr(label+' coaxial shoulder journal',a-Vector((.027,0,0)),a+Vector((.033,0,0)),.044,upper,'shoulder','bearing',sides=28)
    wt(label+' swept upper wing load member',[a,a.lerp(b,.45)+Vector((0,.014,.012)),b],[.023,.022,.024],upper,'shoulder')
    wr(label+' coaxial elbow journal',b-Vector((.011,0,0)),b+Vector((.011,0,0)),.035,lower,'wing','bearing',sides=28)
    if side==1:
        wr('Original anatomical-left travel stop',a+Vector((.007,-.063,-.010)),a+Vector((.044,-.063,-.010)),.016,upper,'shoulder','frame')
        # Preserve v2 proposed chronology without promoting it to accepted source fact.
        wt('Proposed later left bearing strap',[a+Vector((.035,-.02,.055)),a+Vector((.043,-.035,0)),a+Vector((.028,-.015,-.070))],[.011,.012,.011],bpy.data.objects['industrial-repairs'],'shoulder','repair','mechanic,builder')

# LIMBS. Tapered crowned channel cross-sections are aligned to actual links;
# bearing rings stay centred on their rigid transverse hinge axes.
for side,label in [(1,'left'),(-1,'right')]:
    thigh=bpy.data.objects[label+'-thigh'];shin=bpy.data.objects[label+'-shin'];foot=bpy.data.objects[label+'-foot']
    hip=thigh.matrix_world.translation.copy();knee=shin.matrix_world.translation.copy();ankle=foot.matrix_world.translation.copy()
    for centre,owner,radius in [(hip,thigh,.051),(knee,shin,.049),(ankle,foot,.039)]:
        wr(label+' transverse bearing core',centre-Vector((.034,0,0)),centre+Vector((.034,0,0)),radius,owner,'leg','frame',sides=32)
        for sign in [-1,1]:
            wr(label+' concentric bearing lip',centre+Vector((sign*.034,0,0)),centre+Vector((sign*.041,0,0)),radius*.86,owner,'leg','bearing',sides=32)
            wr(label+' recessed axle cap',centre+Vector((sign*.041,0,0)),centre+Vector((sign*.044,0,0)),radius*.34,owner,'leg','edge',sides=24)
    for a,b,owner,width in [(hip,knee,thigh,.051),(knee,ankle,shin,.043)]:
        axis=(b-a).normalized();front=Vector((0,-1,0));front=(front-axis*front.dot(axis)).normalized();across=axis.cross(front).normalized()
        for sign in [-1,1]:
            wt(label+' tapered passive load rail',[a.lerp(b,.13)+across*sign*width,a.lerp(b,.50)+across*sign*width*.80,b.lerp(a,.14)+across*sign*width*.68],[.017,.015,.013],owner,'leg','frame')
        # Three distinct overlapping shells follow the link, with returned side flanges.
        for piece,(start,end,w0,w1) in enumerate([(.12,.39,1.10,.91),(.35,.66,.97,.80),(.62,.88,.84,.62)]):
            vertices=[];faces=[];n=12
            for j in range(6):
                t=j/5;centre=a.lerp(b,start+(end-start)*t);ww=width*(w0+(w1-w0)*t)
                section=[]
                for k in range(n+1):
                    angle=-1.78+3.56*k/n
                    p=centre+across*(math.sin(angle)*ww)+front*(.015+math.cos(angle)*(.030-.005*t))
                    vertices.append(p);section.append(p)
                if j in [0,5]:control(f'{label} {owner.name} guard {piece} section {j}',section,owner,'cross-section')
            for j in range(5):
                for k in range(n):idx=j*(n+1)+k;faces.append((idx,idx+1,idx+n+2,idx+n+1))
            o=wm(label+' crowned limb guard '+owner.name+str(piece),vertices,faces,owner,'leg');m=o.modifiers.new('Forged returned guard wall','SOLIDIFY');m.thickness=.005;bevel(o,.0018)
            for f in o.data.polygons:f.use_smooth=True
            for sign in [-1,1]:fastener('Crowned guard fixing',a.lerp(b,start+.05)+across*sign*width*.62+front*.039,front,owner,'leg',.003)
    # A curved instep shield follows the foot link instead of five flat shingles.
    instep=[(ankle.y-.025,ankle.z-.027),(-.041,.159),(-.096,.104),(-.142,.076)]
    vertices=[];faces=[];n=12
    for i,(y,z) in enumerate(instep):
        width=[.043,.041,.048,.058][i]
        for k in range(n+1):angle=-1.5+3*k/n;vertices.append((ankle.x+math.sin(angle)*width,y-.012*math.cos(angle),z+.016*math.cos(angle)))
    for i in range(3):
        for k in range(n):a=i*(n+1)+k;faces.append((a,a+1,a+n+2,a+n+1))
    o=wm(label+' curved instep shield',vertices,faces,foot,'foot');m=o.modifiers.new('Instep wall','SOLIDIFY');m.thickness=.005
    for face in o.data.polygons:face.use_smooth=True
    for digit in [1,2,3]:
        proximal=bpy.data.objects[f'{label}-digit-{digit}-proximal'];distal=bpy.data.objects[f'{label}-digit-{digit}-distal']
        root=proximal.matrix_world.translation.copy();mid=distal.matrix_world.translation.copy()
        length=[.235,.28,.215][digit-1];spread=[-.083,0,.09][digit-1]
        end=Vector((ankle.x+spread*1.45,-.13-length,.039))
        for aa,bb,owner,width in [(root,mid,proximal,.035),(mid,end,distal,.028)]:
            for piece,(start,finish) in enumerate([(0,.57),(.48,.96)]):
                vertices=[];faces=[];n=12
                for j in range(5):
                    t=j/4;p=aa.lerp(bb,start+(finish-start)*t);w=width*(1-.23*(start+(finish-start)*t))
                    for k in range(n+1):ang=-1.43+2.86*k/n;vertices.append((p.x+math.sin(ang)*w,p.y,p.z+math.cos(ang)*w*.77))
                for j in range(4):
                    for k in range(n):a=j*(n+1)+k;faces.append((a,a+1,a+n+2,a+n+1))
                o=wm(f'{label} digit {digit} shaped knuckle {owner.name} {piece}',vertices,faces,owner,'foot');m=o.modifiers.new('Knuckle wall','SOLIDIFY');m.thickness=.004

# Contact landmark records an actual bill vertex before export transformations.
bpy.context.view_layer.update()
vertices=[o.matrix_world@v.co for o in bpy.data.objects if o.type=='MESH' and under(o,bill) for v in o.data.vertices]
contact=bpy.data.objects['bill-contact'];point=min(vertices,key=lambda p:p.y)
contact.parent=bill;contact.matrix_parent_inverse=Matrix.Identity(4);contact.location=bill.matrix_world.inverted()@point
bpy.context.view_layer.update()
contact_world=list(contact.matrix_world.translation)
for o in bpy.data.objects:
    if o.type=='EMPTY' and o.name in original_pivots and o.name!='bill-contact':
        assert (o.location-Vector(original_pivots[o.name])).length<1e-7,o.name

# Preserve actual independent mesh pieces in native source; batch only export.
for o in list(bpy.context.scene.objects):
    if o.type!='MESH':continue
    bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
    bm=bmesh.new();bm.from_mesh(o.data)
    bad=[f for f in bm.faces if f.calc_area()<1e-12]
    if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    for attr in list(o.data.color_attributes):o.data.color_attributes.remove(attr)
parts=[{'name':o.name,'parent':o.parent.name,'region':o.get('region','back'),'role':o.get('surfaceRole','frame'),'eras':o.get('exteriorEras',ALL).split(','),'class':o.get('constructionClass','inherited-passive')} for o in bpy.context.scene.objects if o.type=='MESH']
pivots=[{'name':o.name,'parent':o.parent.name if o.parent else None,'local':list(o.location),'world':list(o.matrix_world.translation),'scale':list(o.scale)} for o in bpy.context.scene.objects if o.type=='EMPTY']
root=bpy.data.objects['murderbird'];root['status']='alignment-v3 geometry and articulation candidate; owner likeness review pending'
head.rotation_euler.z=0
for frame,angle in [(1,0),(16,.12),(31,0)]:head.rotation_euler.z=angle;head.keyframe_insert(data_path='rotation_euler',frame=frame)
head.animation_data.action.name='attention-export-proof';bpy.context.scene.frame_set(1)
bpy.context.preferences.filepaths.save_version=0
blend=OUT/'murderbird-alignment-v3.blend';pending=OUT/'.building-alignment.blend';bpy.ops.wm.save_as_mainfile(filepath=str(pending));pending.replace(blend)
groups={}
for o in list(bpy.context.scene.objects):
    if o.type=='MESH':groups.setdefault((o.parent,o.get('exteriorEras',ALL),o.get('region','back'),o.get('surfaceRole','frame')),[]).append(o)
for (parent,eras,reg,role),objects in groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=f'{parent.name}-{reg}-{role}';o['exteriorEras']=eras;o['region']=reg;o['surfaceRole']=role
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
    if o.type in {'MESH','EMPTY'}:o.select_set(True)
model=OUT/'murderbird-alignment-v3.glb';pending=OUT/'.building-alignment.glb'
bpy.ops.export_scene.gltf(filepath=str(pending),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False,export_animations=True,export_animation_mode='ACTIONS',export_frame_range=True);pending.replace(model)
manifest={'status':'neutral geometry proposal awaiting owner review','startingRevision':'3e3bcc03dbf7635e06cc805cfcd29d31c2aabdc7','base':{'path':str(BASE.relative_to(ROOT)),'sha256':BASE_SHA},'conventions':'metres; X anatomical left, -Y forward, Z up; authored dimensions, not source metrology','parts':parts,'pivots':pivots,'billContact':contact_world,'billContactSpace':'Blender world at rest before export axis conversion','controls':control_records,'sourceReferences':json.loads((ROOT/'assets/models/uncaged-neutral-v2/reference-packet.json').read_text()),'restTransformNormalization':{'normalizedEmptyScales':normalized_scales,'maximumRestVertexError':max_rest_bake_error,'allRestJointWorldPositionsPreserved':True},'jointContract':'V2 rest WORLD joint centres preserved except bill-contact surface landmark. Inherited head scale baked into descendant offsets/vertices so articulations remain rigid; +X opens mandible downward. Local coordinates are recorded here and are not asserted equal to v2.','limits':['Hidden construction remains proposed','V10 chronology retained provisionally, not owner-approved','No purposeful supported claw grip or physical simulation established','No final surface or likeness acceptance'],'generatedFiles':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in [blend,model]]}
receipt.write_text(json.dumps(manifest,indent=2)+'\n')
print('ALIGNMENT_V3_SAVED',len(parts),'pieces',len(control_records),'editable curves',sha(model))
