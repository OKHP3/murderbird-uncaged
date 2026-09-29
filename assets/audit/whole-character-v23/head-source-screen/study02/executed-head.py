"""V23 reference-built head blockout on exact V22 Frame04.

July is HEAD ONLY and open-jaw identity; the owner target controls closed rest.
Native metres/Z-up/-Y-forward. All hidden seats are proposed construction.
No pivot, material definition, outside-region, runtime or export mutation.
"""
import bpy,bmesh,math,json
from mathutils import Vector
OWNERS={'head','jaw','upper-bill','cranial-cover','builder-optics'}

def smooth(t):
 t=max(0.,min(1.,t));return t*t*(3-2*t)

def sample(rows,t):
 u=max(0.,min(1.,t))*(len(rows)-1);i=min(int(u),len(rows)-2);s=u-i
 # C1 interpolant; all authored profiles retain finite terminal dimensions.
 a,b,c,d=rows[max(0,i-1)],rows[i],rows[i+1],rows[min(i+2,len(rows)-1)]
 return [(.5*(2*b[k]+(-a[k]+c[k])*s+(2*a[k]-5*b[k]+4*c[k]-d[k])*s*s+(-a[k]+3*b[k]-3*c[k]+d[k])*s*s*s)) for k in range(len(b))]

def mesh_snapshot(o):
 return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(f.vertices) for f in o.data.polygons),tuple(m.name if m else None for m in o.data.materials),json.dumps(dict(o.items()),default=lambda x:list(x),sort_keys=True),o.hide_render,o.hide_viewport)

def install(name,pts,faces,wall=None,section_centers=None):
 o=bpy.data.objects[name];assert o.parent and o.parent.name in OWNERS
 old=o.data;inv=o.matrix_world.inverted();m=bpy.data.meshes.new(name+' V23 authored form');m.from_pydata([inv@Vector(p) for p in pts],[],faces);m.update()
 for mat in old.materials:m.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.verts.ensure_lookup_table()
 if wall is None:
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 else:
  # Each connected open loft patch is oriented against its section centre,
  # including top/bottom patches whose X mean is zero.
  remaining=set(bm.faces);normal=o.matrix_world.to_3x3().inverted().transposed()
  while remaining:
   seed=remaining.pop();group={seed};stack=[seed]
   while stack:
    for e in stack.pop().edges:
     for f in e.link_faces:
      if f in remaining:remaining.remove(f);group.add(f);stack.append(f)
   score=0
   for f in group:
    p=o.matrix_world@f.calc_center_median();c=sum((Vector(section_centers[v.index]) for v in f.verts),Vector())/len(f.verts)
    score+=(normal@f.normal).dot(p-c)*f.calc_area()
   if score<0:bmesh.ops.reverse_faces(bm,faces=list(group))
 bm.to_mesh(m);bm.free();o.data=m;o.modifiers.clear()
 if wall:
  q=o.modifiers.new('V23 finite formed wall','SOLIDIFY');q.thickness=wall;q.offset=-1;q.use_even_offset=True
 for p in m.polygons:p.use_smooth=True
 o['v23Construction']='reference-built finite rigid head form; proposed hidden seating'
 return name

def ribbon(side,rows,along=30,across=8,wall=.005):
 # rows: radial X, Y, Z, half-width in local side-profile normal.
 pts=[];faces=[];n=(along+1)*(across+1)
 for inner in (0,1):
  for j in range(along+1):
   t=j/along;q=sample(rows,t);a=sample(rows,max(0,t-.002));b=sample(rows,min(1,t+.002));dy=b[1]-a[1];dz=b[2]-a[2];L=max(1e-10,math.hypot(dy,dz))
   for k in range(across+1):
    s=2*k/across-1;w=q[3]*s
    pts.append((side*(q[0]+.004*(1-s*s)-inner*wall),q[1]-dz/L*w,q[2]+dy/L*w))
 stride=across+1
 for j in range(along):
  for k in range(across):
   a=j*stride+k;b=a+stride;faces.extend([(a,a+1,b+1,b),(n+b,n+b+1,n+a+1,n+a)])
  a=j*stride;b=a+stride;faces.append((b,a,n+a,n+b));a+=across;b+=across;faces.append((a,b,n+b,n+a))
 for k in range(across):
  faces.append((k,k+1,n+k+1,n+k));a=along*stride+k;faces.append((a+1,a,n+a,n+a+1))
 return pts,faces

BILL=[(-.548,1.847,-.551,1.695,.100),(-.590,1.830,-.584,1.676,.106),(-.639,1.793,-.624,1.652,.102),(-.680,1.730,-.656,1.632,.084),(-.708,1.657,-.681,1.602,.059),(-.716,1.580,-.698,1.562,.034),(-.698,1.514,-.697,1.509,.002)]

def bill_piece(start,end,indices=None,cap=False):
 pts=[];centers=[];faces=[];n=48;rows=36
 for j in range(rows+1):
  q=sample(BILL,start+(end-start)*j/rows);cy=(q[0]+q[2])/2;cz=(q[1]+q[3])/2
  for k in range(n):
   a=math.tau*k/n;s=math.sin(a);c=math.cos(a);pts.append((q[4]*math.copysign(abs(s)**.65,s),cy+(q[0]-q[2])*c/2,cz+(q[1]-q[3])*c/2));centers.append((0,cy,cz))
 for j in range(rows):
  for k in range(n):
   if indices is None or k in indices:
    a=j*n+k;b=j*n+(k+1)%n;faces.append((a,b,b+n,a+n))
 if cap:faces.extend([tuple(reversed(range(n))),tuple(rows*n+k for k in range(n))])
 ids=sorted({i for f in faces for i in f});ix={a:i for i,a in enumerate(ids)}
 return [pts[i] for i in ids],[tuple(ix[a] for a in f) for f in faces],[centers[i] for i in ids]

def crown_patch(rows,along=24,across=12,wall=.004):
 # centre Y/Z, half X width. A finite sagittal formed plate swept aft.
 pts=[];faces=[];n=(along+1)*(across+1)
 for inner in (0,1):
  for j in range(along+1):
   y,z,w=sample(rows,j/along)
   for k in range(across+1):
    s=2*k/across-1;pts.append((w*s,y+.008*s*s,z-.018*s*s-inner*wall))
 stride=across+1
 for j in range(along):
  for k in range(across):
   a=j*stride+k;b=a+stride;faces.extend([(a,a+1,b+1,b),(n+b,n+b+1,n+a+1,n+a)])
  a=j*stride;b=a+stride;faces.append((b,a,n+a,n+b));a+=across;b+=across;faces.append((a,b,n+b,n+a))
 for k in range(across):
  faces.append((k,k+1,n+k+1,n+k));a=along*stride+k;faces.append((a+1,a,n+a,n+a+1))
 return pts,faces

def deform(o,fn):
 inv=o.matrix_world.inverted();o.data=o.data.copy()
 for v in o.data.vertices:v.co=inv@fn(o.matrix_world@v.co)
 o.data.update();o['v23Construction']='reseated retained optic/frame interface'

def apply():
 bpy.context.view_layer.update()
 nodes={o.name:(tuple(tuple(r) for r in o.matrix_world),o.parent.name if o.parent else None,dict(o.items())) for o in bpy.data.objects if o.type=='EMPTY'}
 outside={o.name:mesh_snapshot(o) for o in bpy.data.objects if o.type=='MESH' and (not o.parent or o.parent.name not in OWNERS)}
 changed=[];removed=[];added=[]
 # Actual new convex bill cells, separated by construction seams, not seam paint.
 for name,indices in [('Profiled upper bill blade 0',list(range(0,7))+list(range(18,31))+list(range(42,48))),('V19 fitted proximal bill cheek plate right',list(range(7,18))),('V19 fitted proximal bill cheek plate left',list(range(31,42)))]:
  p,f,c=bill_piece(0,.66,indices);changed.append(install(name,p,f,.004,c))
 p,f,c=bill_piece(.665,1,cap=True);changed.append(install('Profiled upper bill blade 1',p,f))
 p,f=crown_patch([(-.548,1.854,.031),(-.575,1.847,.036),(-.609,1.826,.032),(-.641,1.799,.024)]);changed.append(install('Overlapping nasal hood',p,f))
 # Fixed cere roots share bill sections, narrower than the hook-facing cheeks.
 for side in (-1,1):
  p,f=ribbon(side,[(.105,-.548,1.805,.019),(.111,-.576,1.763,.025),(.105,-.605,1.718,.019),(.096,-.633,1.679,.012)])
  changed.append(install(f'Cere root transition {side}',p,f))
  # Curved mandible edge descends from journal then runs forward under the
  # closed cutting line. No broad upturned smiling distal paddle.
  p,f=ribbon(side,[(.119,-.429,1.666,.021),(.123,-.475,1.636,.029),(.111,-.543,1.625,.023),(.091,-.607,1.621,.020),(.062,-.661,1.607,.014),(.038,-.686,1.594,.007)])
  changed.append(install(f'Forked forged mandible {side}',p,f))
  # Cheek opens behind and below optic, with a descending root shoulder;
  # root/bill surface is outside, journal seat inside and mechanically visible.
  p,f=ribbon(side,[(.134,-.408,1.709,.014),(.140,-.450,1.688,.018),(.136,-.502,1.684,.014),(.118,-.553,1.701,.020),(.103,-.600,1.713,.019)])
  changed.append(install(f'Broad swept cheek band {side}',p,f))
  cy=-.5055;cz=1.7532
  # Brow follows the circular receiving edge while retaining broad diagonal
  # root-to-nape mass. Its lower free edge remains above the readable port.
  p,f=ribbon(side,[(.151,-.383,1.835,.026),(.154,-.438,1.844,.027),(.151,-.497,1.840,.022),(.143,-.548,1.817,.020),(.123,-.588,1.784,.020)])
  changed.append(install(f'Forged orbital brow {side}',p,f))
  p,f=ribbon(side,[(.144,-.388,1.835,.020),(.147,-.409,1.786,.023),(.140,-.414,1.737,.019),(.131,-.429,1.702,.016)])
  changed.append(install(f'Forged orbital mounting plate {side}',p,f))
  # Outer retaining lip sits within formed brow/cheek instead of projecting as
  # an independent goggle; circular lens and era tags are preserved.
  for name in (f'Orbital passive retaining race {side}',f'Recessed orbital bearing {side}',f'Seated passive optic housing {side}',f'Seated Advanced optic {side}'):
   o=bpy.data.objects[name];deform(o,lambda p:p+Vector((-side*.005,0,0)));changed.append(name)
  # Shorter aft inner support shell; curtain replaced by authored plate field.
  o=bpy.data.objects[f'Continuous temporal shell {side}']
  def compact(p):
   q=p.copy();rear=smooth((p.y+.38)/.20);q.y-=.042*rear;q.z+=.060*rear*smooth((1.73-p.z)/.15);q.x*=1-.10*rear;return q
  deform(o,compact);changed.append(o.name)
 # Closed finite tip joining the two narrowed mandible roots; not a wide lip.
 p,f=crown_patch([(-.667,1.604,.057),(-.680,1.599,.045),(-.691,1.591,.036)],along=12,across=12,wall=.006);changed.append(install('Distal mandible bridge',p,f))
 # Crown is a compact swept cascade. Rear scalp and lower temporal curtains
 # are replaced intentionally rather than preserved for old mesh counts.
 for j in range(5):
  rows=[(-.561+.064*j,1.872+.010*math.sin(j*.7),.057+.012*math.sin(j*.65)),(-.528+.064*j,1.889+.014*math.sin(j*.7),.066+.014*math.sin(j*.65)),(-.472+.064*j,1.888-.007*j,.040+.009*math.sin(j*.65)),(-.430+.060*j,1.858-.013*j,.011)]
  p,f=crown_patch(rows);changed.append(install(f'Rounded swept crown lamina {j}',p,f))
 for side in (-1,1):
  for row in range(5):
   count=3 if row<4 else 2
   for col in range(count):
    name=f'Swept temporal lamina {side} {row} {col}'
    if row==4:
     removed.append({'name':name,'owner':'cranial-cover','reason':'overlong rear curtain replaced by compact sweep above neck seat'});bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True);continue
    # Root order exposes journal/fitting cluster between shorter cascades;
    # breadth is deliberate, free ends rounded/tapered rather than needles.
    y=-.433+.064*col+.027*row;z=1.843-.051*row+.009*col;x=.134-.026*col+.002*row
    rows=[(x,y,z,.016),(x+.006,y+.027,z-.016,.024),(x-.006,y+.078,z-.054,.019),(max(.044,x-.025),y+.120,z-.087,.005)]
    p,f=ribbon(side,rows,along=24,wall=.004);changed.append(install(name,p,f))
 # Old surface fixings belonged to the replaced panels; leaving them floating
 # would misrepresent attachment. Journal caps and actual passive fittings stay.
 prefixes=('Crown lamina root pin','Temporal lamina root pin','Nasal hood fixing','Bill root fixing','Recessed cheek fixing','Orbital mounting fixing','Orbital support bridge')
 for o in list(bpy.data.objects):
  if o.type=='MESH' and o.parent and o.parent.name in OWNERS and o.name.startswith(prefixes):
   removed.append({'name':o.name,'owner':o.parent.name,'reason':'old skin attachment replaced; new hidden fastening is a proposal'});bpy.data.objects.remove(o,do_unlink=True)
 bpy.context.view_layer.update()
 assert nodes=={o.name:(tuple(tuple(r) for r in o.matrix_world),o.parent.name if o.parent else None,dict(o.items())) for o in bpy.data.objects if o.type=='EMPTY'},'Rigid interfaces changed'
 assert outside=={o.name:mesh_snapshot(o) for o in bpy.data.objects if o.type=='MESH' and (not o.parent or o.parent.name not in OWNERS)},'Outside head changed'
 contact=None;name=None;dg=bpy.context.evaluated_depsgraph_get()
 for o in bpy.data.objects:
  if o.type!='MESH' or not o.parent or o.parent.name!='upper-bill':continue
  ev=o.evaluated_get(dg);m=ev.to_mesh()
  for v in m.vertices:
   p=ev.matrix_world@v.co
   if contact is None or p.y<contact.y:contact=p;name=o.name
  ev.to_mesh_clear()
 return {'region':'head','status':'coarse proposed head reconstruction; no likeness/articulation acceptance','changed':changed,'added':added,'removed':removed,'stagedOut':removed,'primaryPivotChanges':[],'preservedOriginalNodes':len(nodes),'preservedOutsideMeshes':len(outside),'materialDefinitionsChanged':False,'billContactNativeWorld':list(contact),'contactMethod':'minimum nativeY evaluated upper-bill vertex including finite wall; triangle surface extremum','contactObject':name,'construction':'Deep compact convex segmented bill; narrowed closed-edge mandible; formed cheek opening and diagonal brow around readable recessed optic; compact staggered aft crown cascade replaces long curtains. Existing journals/passive fittings retained. All hidden seats are proposals.','limits':['Closed/open jaw native study required; no continuous motion or clearance proof.','New skin attachment fixings are intentionally staged out pending fitted attachment design.','No texture, material definition, exterior outside head, runtime or export change.']}
