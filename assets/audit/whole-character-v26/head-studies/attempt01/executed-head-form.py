"""V26 major head-form proposal, retaining V25's enlarged head attachment.

July controls HEAD identity/open cheek; owner whole-bird controls closed rest.
Native authoring coordinates below retain the V24 reference frame, then bake
V25's1.30 head mass about the actual fixed head pivot. No runtime scale.
"""
import bpy,bmesh,math,json
from mathutils import Vector
OWNERS={'head','jaw','upper-bill','cranial-cover','builder-optics'}
BOUNDARY={'V21 head captive shaft','V23 cervical 4 captive pin'}
BILL=[(-.526,1.846,-.537,1.703,.083),(-.558,1.835,-.570,1.681,.093),(-.601,1.792,-.595,1.659,.085),(-.638,1.735,-.610,1.642,.069),(-.656,1.662,-.617,1.619,.049),(-.655,1.585,-.622,1.565,.025),(-.638,1.520,-.633,1.516,.007),(-.605,1.486,-.609,1.482,.002)]

def sample(rows,t):
 u=max(0,min(1,t))*(len(rows)-1);i=min(int(u),len(rows)-2);s=u-i
 a,b,c,d=rows[max(0,i-1)],rows[i],rows[i+1],rows[min(i+2,len(rows)-1)]
 return [.5*(2*b[k]+(-a[k]+c[k])*s+(2*a[k]-5*b[k]+4*c[k]-d[k])*s*s+(-a[k]+3*b[k]-3*c[k]+d[k])*s*s*s) for k in range(len(b))]
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def props(o):return json.dumps(dict(o.items()),default=lambda x:list(x),sort_keys=True)
def snap(o):return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(f.vertices) for f in o.data.polygons),tuple(m.name if m else None for m in o.data.materials),props(o),o.hide_render,o.hide_viewport)
def node(o):return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),props(o))
def ribbon(side,rows,wall=.004,along=30,across=8):
 verts=[];faces=[];n=(along+1)*(across+1)
 for inner in (0,1):
  for j in range(along+1):
   t=j/along;q=sample(rows,t);a=sample(rows,max(0,t-.002));b=sample(rows,min(1,t+.002));dy=b[1]-a[1];dz=b[2]-a[2];L=max(1e-10,math.hypot(dy,dz))
   for k in range(across+1):
    s=2*k/across-1;w=q[3]*s;verts.append((side*(q[0]+.001*(1-s*s)-inner*wall),q[1]-dz/L*w,q[2]+dy/L*w))
 stride=across+1
 for j in range(along):
  for k in range(across):
   a=j*stride+k;b=a+stride;faces.extend([(a,a+1,b+1,b),(n+b,n+b+1,n+a+1,n+a)])
  a=j*stride;b=a+stride;faces.append((b,a,n+a,n+b));a+=across;b+=across;faces.append((a,b,n+b,n+a))
 for k in range(across):
  faces.append((k,k+1,n+k+1,n+k));a=along*stride+k;faces.append((a+1,a,n+a,n+a+1))
 return verts,faces

def polygon(side,outline,x=.148,wall=.005):
 n=len(outline);v=[(side*xx,y,z) for xx in (x,x-wall) for y,z in outline];f=[tuple(range(n)),tuple(reversed(range(n,2*n)))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];return v,f

def bill(start,end,hollow=True):
 # Twelve-point formed section: dorsal ridge, broad planar side and a thinner
 # posterior cutting seat, unlike the old inflated elliptical nasal cells.
 ring=[(0,0),(.45,.07),(.90,.18),(1,.43),(.95,.75),(.63,.94),(0,1),(-.63,.94),(-.95,.75),(-1,.43),(-.90,.18),(-.45,.07)]
 rows=32;n=len(ring);v=[];f=[];sets=2 if hollow else 1
 for inner in range(sets):
  for j in range(rows+1):
   dY,dZ,pY,pZ,w=sample(BILL,start+(end-start)*j/rows);cy=(dY+pY)/2;cz=(dZ+pZ)/2
   for x,t in ring:
    yy=dY*(1-t)+pY*t;zz=dZ*(1-t)+pZ*t
    if inner:
     w=max(.001,w-.0045);L=max(.010,math.hypot(dY-pY,dZ-pZ));scale=max(.2,1-.009/L);yy=cy+(yy-cy)*scale;zz=cz+(zz-cz)*scale
    v.append((w*x,yy,zz))
 m=(rows+1)*n
 for j in range(rows):
  for k in range(n):
   a=j*n+k;b=j*n+(k+1)%n;f.append((a,b,b+n,a+n))
   if hollow:f.append((m+a+n,m+b+n,m+b,m+a))
 if hollow:
  for k in range(n):
   a=k;b=(k+1)%n;f.append((b,a,m+a,m+b));a=rows*n+k;b=rows*n+(k+1)%n;f.append((a,b,m+b,m+a))
 else:f.extend([tuple(reversed(range(n))),tuple(rows*n+k for k in range(n))])
 return v,f

def crown_sheet(rows):
 # Narrow swept sagittal crest with a finite closed skin.
 along=28;across=10;v=[];f=[];n=(along+1)*(across+1)
 for inner in (0,1):
  for j in range(along+1):
   y,z,w=sample(rows,j/along)
   for k in range(across+1):
    s=2*k/across-1;v.append((w*s,y+.002*s*s,z-.004*s*s-inner*.004))
 stride=across+1
 for j in range(along):
  for k in range(across):
   a=j*stride+k;b=a+stride;f.extend([(a,a+1,b+1,b),(n+b,n+b+1,n+a+1,n+a)])
  a=j*stride;b=a+stride;f.append((b,a,n+a,n+b));a+=across;b+=across;f.append((a,b,n+b,n+a))
 for k in range(across):
  f.append((k,k+1,n+k+1,n+k));a=along*stride+k;f.append((a+1,a,n+a,n+a+1))
 return v,f

def apply():
 bpy.context.view_layer.update();pivot=bpy.data.objects['head'].matrix_world.translation.copy();assert (pivot-Vector((0,-.3226,1.6028))).length<1e-6
 allnodes={o.name:node(o) for o in bpy.data.objects if o.type=='EMPTY'};outside={o.name:snap(o) for o in bpy.data.objects if o.type=='MESH' and (not o.parent or o.parent.name not in OWNERS or o.name in BOUNDARY)}
 changed=[];added=[];removed=[];errors=[]
 def mapped(p):return pivot+1.30*(Vector(p)-pivot)
 def install(name,verts,faces,new=False,owner=None,template=None):
  if new:
   t=bpy.data.objects[template];o=bpy.data.objects.new(name,t.data.copy());bpy.context.scene.collection.objects.link(o);o.parent=bpy.data.objects[owner]
   for k in t.keys():o[k]=t[k]
   o['region']='head';o['surfaceRole']='plate';o['exteriorEras']='maker,mechanic,builder';o['constructionClass']='inherited-passive';added.append(name)
  else:o=bpy.data.objects[name];changed.append(name)
  assert o.parent.name in OWNERS
  bpy.context.view_layer.update();inv=o.matrix_world.inverted();world=[mapped(p) for p in verts];m=bpy.data.meshes.new(name+' V26 formed rigid solid');m.from_pydata([inv@p for p in world],[],faces);m.update()
  for mat in o.data.materials:m.materials.append(mat)
  bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  bm.to_mesh(m);bm.free();o.data=m;o.modifiers.clear()
  for p in m.polygons:p.use_smooth=False
  err=max((o.matrix_world@v.co-p).length for v,p in zip(m.vertices,world));assert err<1e-6;errors.append(err)
  return o
 # Replace the old inflated nasal cells with three actual formed blade units.
 oldbill=[o.name for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name=='upper-bill']
 keep={'Profiled upper bill blade 0','Profiled upper bill blade 1','Overlapping nasal hood','Cere root transition -1','Cere root transition 1'}
 for n in oldbill:
  if n not in keep:removed.append(n);bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
 for n,a,b,hollow in [('Profiled upper bill blade 0',0,.305,True),('Overlapping nasal hood',.316,.625,True),('Profiled upper bill blade 1',.636,1,False)]:
  v,f=bill(a,b,hollow);install(n,v,f)
 for side in (-1,1):
  v,f=ribbon(side,[(.091,-.531,1.800,.014),(.095,-.566,1.763,.019),(.085,-.594,1.711,.017),(.060,-.615,1.658,.007)],wall=.0045);install(f'Cere root transition {side}',v,f)
  # Upper closed cutting curve tucks beneath the posterior bill seat. The
  # open impression derives only from the unchanged jaw hinge rotation.
  v,f=ribbon(side,[(.119,-.432,1.654,.022),(.116,-.475,1.638,.025),(.101,-.521,1.640,.020),(.080,-.560,1.650,.015),(.057,-.590,1.642,.011),(.032,-.609,1.628,.006),(.021,-.615,1.612,.0025)],wall=.005,along=40);install(f'Forked forged mandible {side}',v,f)
 v,f=crown_sheet([(-.606,1.620,.031),(-.614,1.614,.021),(-.617,1.611,.018)]);install('Distal mandible bridge',v,f)
 for side in (-1,1):
  outline=[(-.353,1.832),(-.403,1.882),(-.462,1.892),(-.520,1.856),(-.560,1.804),(-.548,1.788),(-.533,1.802),(-.521,1.820),(-.501,1.830),(-.475,1.830),(-.443,1.815),(-.404,1.818),(-.380,1.794),(-.367,1.805)]
  v,f=polygon(side,outline,.151,.0055);install(f'Forged orbital brow {side}',v,f)
  outline=[(-.412,1.799),(-.434,1.751),(-.457,1.720),(-.506,1.696),(-.563,1.717),(-.589,1.698),(-.568,1.674),(-.520,1.674),(-.477,1.687),(-.442,1.719),(-.418,1.751),(-.397,1.787)]
  v,f=polygon(side,outline,.145,.006);install(f'Broad swept cheek band {side}',v,f)
  outline=[(-.374,1.804),(-.390,1.783),(-.397,1.746),(-.421,1.716),(-.436,1.700),(-.444,1.711),(-.423,1.741),(-.411,1.787),(-.397,1.812)]
  v,f=polygon(side,outline,.142,.006);install(f'Forged orbital mounting plate {side}',v,f)
  outline=[(-.547,1.800),(-.565,1.812),(-.582,1.784),(-.588,1.729),(-.576,1.710),(-.561,1.725),(-.559,1.765)]
  v,f=polygon(side,outline,.121,.006);install(f'V24 anterior orbital root receiver {side}',v,f)
  # Seat the complete true optic/functional race into this face; no lenses or
  # historical passive fittings acquire new era eligibility.
  for prefix in ('Seated Advanced optic','Seated passive optic housing','Recessed orbital bearing','Orbital passive retaining race'):
   n=f'{prefix} {side}';o=bpy.data.objects[n];inv=o.matrix_world.inverted();o.data=o.data.copy()
   for vert in o.data.vertices:
    p=o.matrix_world@vert.co;p.x-=side*.016*1.30;vert.co=inv@p
   o.data.update();changed.append(n)
 # Remove the regular oval curtain and author a much shorter hierarchy of
 # genuinely longer swept blades, each on the independent cranial cover.
 for o in list(bpy.data.objects):
  if o.type=='MESH' and (o.name.startswith('Swept temporal lamina ') or o.name.startswith('Rounded swept crown lamina ')):
   removed.append(o.name);bpy.data.objects.remove(o,do_unlink=True)
 CREST=[(-.535,1.853,.047,.125),(-.466,1.887,.063,.156),(-.396,1.890,.052,.149),(-.333,1.858,.030,.117)]
 for i,(y,z,w,run) in enumerate(CREST):
  v,f=crown_sheet([(y,z,w*.82),(y+.035,z+.003,w),(y+run*.72,z-.012,w*.54),(y+run,z-.025,.003)])
  install(f'V26 swept sagittal crown {i}',v,f,True,'cranial-cover','Forged orbital brow -1')
 PLUMES=[(.123,-.450,1.861,.092,-.289,1.847,.026),(.145,-.431,1.830,.115,-.278,1.796,.029),(.143,-.437,1.785,.101,-.289,1.716,.031),(.135,-.412,1.739,.074,-.258,1.658,.025),(.101,-.379,1.857,.076,-.245,1.824,.021),(.107,-.355,1.808,.065,-.226,1.748,.025),(.100,-.341,1.756,.052,-.224,1.677,.023),(.071,-.315,1.825,.044,-.208,1.779,.018),(.079,-.298,1.774,.040,-.205,1.704,.019)]
 for side in (-1,1):
  for i,(x,y,z,ex,ey,ez,w) in enumerate(PLUMES):
   v,f=ribbon(side,[(x,y,z,w*.44),(x+.003,y+.033,z-.008,w),(x*.6+ex*.4,y*.45+ey*.55,z*.40+ez*.60,w*.74),(ex,ey,ez,.0025)],wall=.0045,along=30)
   install(f'V26 swept temporal guard {side} {i}',v,f,True,'cranial-cover',f'Broad swept cheek band {side}')
  v,f=ribbon(side,[(.080,-.381,1.826,.024),(.089,-.325,1.783,.026),(.072,-.275,1.717,.024),(.044,-.266,1.665,.013)],wall=.004);install(f'Continuous temporal shell {side}',v,f)
 # Locally recess the old inner aft scalp beneath the shortened cover field.
 o=bpy.data.objects['V4 cranial inner shell'];o.data=o.data.copy();inv=o.matrix_world.inverted()
 for v in o.data.vertices:
  p=(o.matrix_world@v.co-pivot)/1.30+pivot;weight=smooth((p.y+.40)/.15);p.x*=1-.12*weight;p.y-=.014*weight;v.co=inv@mapped(p)
 o.data.update();changed.append(o.name)
 bpy.context.view_layer.update();front=None;front_object=None;dg=bpy.context.evaluated_depsgraph_get()
 for o in bpy.data.objects:
  if o.type=='MESH' and o.parent and o.parent.name=='upper-bill':
   ev=o.evaluated_get(dg);m=ev.to_mesh()
   for v in m.vertices:
    p=ev.matrix_world@v.co
    if front is None or p.y<front.y:front=p.copy();front_object=o.name
   ev.to_mesh_clear()
 for n in ('bill-contact','anchor-beak'):
  o=bpy.data.objects[n];m=o.matrix_world.copy();m.translation=front;o.matrix_world=m
 bpy.context.view_layer.update()
 for o in bpy.data.objects:
  if o.type=='EMPTY' and o.name not in ('bill-contact','anchor-beak'):assert node(o)==allnodes[o.name],o.name
 assert outside=={n:snap(bpy.data.objects[n]) for n in outside}
 return {'region':'head-major-form','status':'reference-led major-form proposal; visual/motion acceptance pending','changedMeshes':changed,'added':added,'removed':removed,'stagedOut':removed,'changedNodes':['bill-contact','anchor-beak'],'primaryPivotChanges':[],'preservedNodesExact':len(allnodes)-2,'outsideMeshSnapshotsExact':len(outside),'boundaryShaftsExact':sorted(BOUNDARY),'materialDefinitionsChanged':False,'eraTagsChanged':False,'billContactNativeWorld':list(front),'contactObject':front_object,'contactMethod':'minimum nativeY evaluated formed upper-bill surface vertex','maximumAuthoredWorldPointErrorM':max(errors),'parameters':{'headMassRetained':1.30,'billProfile':BILL,'opticMeshRecessM':.0208,'crownNewPlateCount':22,'jawHingeUnchanged':True},'limits':['Closed/open neutral visual comparison only; surface/movement clearance remains to be checked.','New hidden receivers and scalp seating are construction proposals; no final finish or owner likeness acceptance.']}
