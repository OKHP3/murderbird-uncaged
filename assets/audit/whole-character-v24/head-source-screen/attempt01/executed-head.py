"""V24 steep compact reference-built head on exact V23 Form03.

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
 old=o.data;inv=o.matrix_world.inverted();m=bpy.data.meshes.new(name+' V24 authored form');m.from_pydata([inv@Vector(p) for p in pts],[],faces);m.update()
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
  q=o.modifiers.new('V24 finite formed wall','SOLIDIFY');q.thickness=wall;q.offset=-1;q.use_even_offset=True
 for p in m.polygons:p.use_smooth=True
 o['v24Construction']='reference-built finite rigid head form; proposed hidden seating'
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

BILL=[(-.521,1.850,-.532,1.704,.099),(-.554,1.837,-.558,1.677,.104),(-.597,1.803,-.582,1.650,.105),(-.632,1.735,-.608,1.626,.090),(-.652,1.650,-.632,1.600,.066),(-.653,1.555,-.639,1.551,.034),(-.628,1.477,-.627,1.471,.002)]

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
 o.data.update();o['v24Construction']='reseated retained optic/frame interface'


def formed_polygon(side,outline,x=.149,wall=.005):
 # An actual finite, perimeter-shaped receiver instead of a uniform ribbon.
 # A slight radial crown is a purposeful formed flange, not soft tile bulge.
 n=len(outline);pts=[(side*x,y,z) for y,z in outline]+[(side*(x-wall),y,z) for y,z in outline]
 faces=[tuple(range(n)),tuple(reversed(range(n,2*n)))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return pts,faces

def new_form(name,owner,template,pts,faces,changed,added):
 t=bpy.data.objects[template];o=bpy.data.objects.new(name,t.data.copy());bpy.context.scene.collection.objects.link(o);o.parent=bpy.data.objects[owner]
 for k in t.keys():o[k]=t[k]
 o['region']='head';o['surfaceRole']='plate';o['exteriorEras']='maker,mechanic,builder';o['constructionClass']='inherited-passive'
 install(name,pts,faces);added.append(name)


def keeper(side,cy,cz,inner=.050,outer=.062,face_x=.139,back_x=.133):
 # Stepped turned seat: circular receiver and circular optic are functional.
 # The external broad outline belongs to the formed brow/cheek plates.
 pts=[];faces=[];n=64
 for x,r in [(face_x,inner),(face_x,outer),(back_x,outer),(back_x,inner)]:
  for k in range(n):
   a=math.tau*k/n;pts.append((side*x,cy+r*math.cos(a),cz+r*math.sin(a)))
 for j in range(4):
  for k in range(n):
   a=j*n+k;b=j*n+(k+1)%n;c=((j+1)%4)*n+(k+1)%n;d=((j+1)%4)*n+k;faces.append((a,b,c,d))
 return pts,faces


def apply():
 bpy.context.view_layer.update()
 nodes={o.name:(tuple(tuple(r) for r in o.matrix_world),o.parent.name if o.parent else None,json.dumps(dict(o.items()),default=lambda x:list(x),sort_keys=True)) for o in bpy.data.objects if o.type=='EMPTY'}
 outside={o.name:mesh_snapshot(o) for o in bpy.data.objects if o.type=='MESH' and (not o.parent or o.parent.name not in OWNERS)}
 changed=[];removed=[];added=[]
 cells=[('Profiled upper bill blade 0',list(range(0,7))+list(range(18,31))+list(range(42,48))),('V19 fitted proximal bill cheek plate right',list(range(7,18))),('V19 fitted proximal bill cheek plate left',list(range(31,42)))]
 for name,indices in cells:
  for part,start,end in [(name,0,.315),('V23 distal bill root cell '+name,.323,.66)]:
   p,f,c=bill_piece(start,end,indices);changed.append(install(part,p,f,.004,c))
 p,f,c=bill_piece(.667,1,cap=True);changed.append(install('Profiled upper bill blade 1',p,f))
 p,f=crown_patch([(-.522,1.856,.033),(-.542,1.853,.036),(-.570,1.837,.030),(-.599,1.807,.019)],wall=.004);changed.append(install('Overlapping nasal hood',p,f))
 for side in (-1,1):
  # Short formed root buttress meets the steeper bill immediately anterior to
  # the port; no long empty span or balloon nasal shell is retained.
  p,f=ribbon(side,[(.105,-.533,1.805,.015),(.111,-.560,1.765,.023),(.105,-.589,1.712,.021),(.096,-.614,1.665,.012)])
  changed.append(install(f'Cere root transition {side}',p,f))
  # The closed cutting curve is short and bowed downward, tucked under the
  # upper cutting root. July's open pose is not baked into the rest geometry.
  p,f=ribbon(side,[(.119,-.429,1.666,.019),(.124,-.461,1.641,.025),(.111,-.505,1.625,.020),(.088,-.553,1.608,.019),(.060,-.592,1.592,.014),(.038,-.617,1.592,.006)],wall=.006)
  changed.append(install(f'Forked forged mandible {side}',p,f))
  # Perimeter-authored receiver plaques: swept root bridge above the port,
  # diagonal anterior root plaque, and a short formed suborbital shoulder.
  outline=[(-.388,1.850),(-.416,1.873),(-.468,1.873),(-.506,1.855),(-.550,1.828),(-.566,1.808),(-.546,1.791),(-.521,1.807),(-.493,1.817),(-.455,1.822),(-.415,1.831)]
  p,f=formed_polygon(side,outline,.153,.006);changed.append(install(f'Forged orbital brow {side}',p,f))
  outline=[(-.408,1.806),(-.393,1.811),(-.394,1.750),(-.416,1.711),(-.436,1.700),(-.451,1.715),(-.435,1.739),(-.427,1.784)]
  p,f=formed_polygon(side,outline,.148,.006);changed.append(install(f'Forged orbital mounting plate {side}',p,f))
  outline=[(-.435,1.712),(-.455,1.708),(-.473,1.689),(-.516,1.687),(-.539,1.703),(-.567,1.718),(-.582,1.704),(-.565,1.673),(-.539,1.668),(-.512,1.678),(-.472,1.670),(-.444,1.689)]
  p,f=formed_polygon(side,outline,.151,.005);changed.append(install(f'Broad swept cheek band {side}',p,f))
  # A separate anterior receiver links the port/root sheet to the compact
  # cere; its lap is real finite geometry, no painted segmentation.
  outline=[(-.549,1.806),(-.571,1.818),(-.589,1.790),(-.594,1.733),(-.582,1.704),(-.564,1.714),(-.563,1.763)]
  p,f=formed_polygon(side,outline,.125,.005);new_form(f'V24 anterior orbital root receiver {side}','head',f'Broad swept cheek band {side}',p,f,changed,added)
  cy=-.50552;cz=1.75317
  p,f=keeper(side,cy,cz);changed.append(install(f'Orbital passive retaining race {side}',p,f))
  p,f=keeper(side,cy,cz,.0465,.054,.132,.124);changed.append(install(f'Recessed orbital bearing {side}',p,f))
  # Existing true lens/housing eligibility remains unchanged; external rim
  # now has a stepped bearing seat rather than a second broad eyeliner bar.
  o=bpy.data.objects[f'Continuous temporal shell {side}']
  # Reconstruct the actual aft shell under the crown; shorter/wider above the
  # head seat, finite and mechanically distinct from overlapping cover plates.
  rows=[(.115,-.366,1.829,.045),(.143,-.315,1.798,.056),(.126,-.265,1.740,.045),(.089,-.242,1.672,.035),(.070,-.251,1.624,.019)]
  p,f=ribbon(side,rows,along=32,wall=.004);changed.append(install(o.name,p,f))
 # Narrow closed mandible tip; its actual open state comes from unchanged jawX.
 p,f=crown_patch([(-.598,1.592,.057),(-.612,1.591,.043),(-.622,1.593,.035)],along=12,wall=.006);changed.append(install('Distal mandible bridge',p,f))
 top=[(-.532,1.849,.055),(-.463,1.874,.073),(-.401,1.885,.068),(-.347,1.872,.050),(-.301,1.844,.036)]
 for j,(y,z,w) in enumerate(top):
  p,f=crown_patch([(y,z,w*.80),(y+.021,z+.008,w),(y+.063,z-.012,w*.68),(y+.092,z-.034,.012)],wall=.004)
  changed.append(install(f'Rounded swept crown lamina {j}',p,f))
 for side in (-1,1):
  for row in range(4):
   for col in range(3):
    name=f'Swept temporal lamina {side} {row} {col}'
    y=-.431+.051*col+.031*row;z=1.839-.052*row+.008*col;x=.133-.023*col+.002*row
    # A compact directional field with varied but broad free ends. Aft courses
    # turn down around the seat instead of making a regular hanging curtain.
    run=.077+.010*((row+col)%3);drop=.063+.009*((row+2*col)%3)
    p,f=ribbon(side,[(x,y,z,.013),(x+.004,y+.023,z-.015,.024),(x-.004,y+run*.72,z-drop*.65,.019),(max(.048,x-.023),y+run,z-drop,.008)],along=24,wall=.004)
    changed.append(install(name,p,f))
 bpy.context.view_layer.update()
 assert nodes=={o.name:(tuple(tuple(r) for r in o.matrix_world),o.parent.name if o.parent else None,json.dumps(dict(o.items()),default=lambda x:list(x),sort_keys=True)) for o in bpy.data.objects if o.type=='EMPTY'},'Rigid interfaces changed'
 assert outside=={o.name:mesh_snapshot(o) for o in bpy.data.objects if o.type=='MESH' and (not o.parent or o.parent.name not in OWNERS)},'Outside head changed'
 contact=None;source=None;dg=bpy.context.evaluated_depsgraph_get()
 for o in bpy.data.objects:
  if o.type!='MESH' or not o.parent or o.parent.name!='upper-bill':continue
  ev=o.evaluated_get(dg);m=ev.to_mesh()
  for v in m.vertices:
   p=ev.matrix_world@v.co
   if contact is None or p.y<contact.y:contact=p.copy();source=o.name
  ev.to_mesh_clear()
 return {'region':'head','status':'coarse steep compact head proposal; no likeness/motion acceptance','changed':changed,'added':added,'removed':removed,'stagedOut':removed,'primaryPivotChanges':[],'preservedOriginalNodes':len(nodes),'preservedOutsideMeshes':len(outside),'materialDefinitionsChanged':False,'billContactNativeWorld':list(contact),'contactMethod':'minimum nativeY evaluated upper-bill vertex, including finite wall','contactObject':source,'billProfile':BILL,'construction':'Steep close-set root/hook; short bowed mandible; perimeter-shaped layered orbital receivers and concentric stepped keeper; compact varied swept crown with reconstructed aft shell. Existing optic housing/lens and journal interfaces retained.','limits':['Actual closed/open jaw review only; no continuous or armor-clearance proof.','Receiver/rim attachments and hidden aft support are reconstruction proposals.','Outside head, node rests, era tags and material definitions preserved.']}
