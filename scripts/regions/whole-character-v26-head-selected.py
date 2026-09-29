"""V26 selected bill/jaw/orbit proposal; V25 crown exactly retained, retaining V25's enlarged head attachment.

July controls HEAD identity/open cheek; owner whole-bird controls closed rest.
Native authoring coordinates below retain the V24 reference frame, then bake
V25's1.30 head mass about the actual fixed head pivot. No runtime scale.
"""
import bpy,bmesh,math,json
from mathutils import Vector
OWNERS={'head','jaw','upper-bill','cranial-cover','builder-optics'}
BOUNDARY={'V21 head captive shaft','V23 cervical 4 captive pin'}
BILL=[(-.526,1.846,-.533,1.715,.086),(-.576,1.828,-.560,1.697,.098),(-.635,1.786,-.589,1.679,.090),(-.672,1.726,-.613,1.657,.073),(-.681,1.658,-.629,1.629,.055),(-.664,1.604,-.639,1.596,.031),(-.638,1.570,-.628,1.567,.012),(-.612,1.554,-.614,1.551,.0025)]

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

def orbital_facade(side):
 # Formed asymmetric receiver follows the actual optic aperture, with a
 # broad posterior cranium seat. The finite receiver backs the brow/cheek,
 # rather than leaving a detached arch above an exposed full retaining disk.
 n=64;v=[];f=[];cy=-.5055;cz=1.756
 for innerwall in (0,1):
  for outer in (0,1):
   for k in range(n):
    a=2*math.pi*k/n;co=math.cos(a);si=math.sin(a)
    r=.048 if not outer else .070+.013*max(0,co)+.013*max(0,si)-.006*max(0,-co)
    y=cy+r*co;z=cz+r*si;x=.126+.005*si-.012*innerwall
    if outer:y+=.014*max(0,co)**3
    v.append((side*x,y,z))
 for k in range(n):
  j=(k+1)%n
  f.extend([(k,j,n+j,n+k),(2*n+k,3*n+k,3*n+j,2*n+j),(k,2*n+k,2*n+j,j),(n+k,n+j,3*n+j,3*n+k)])
 return v,f

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
 crown={o.name:snap(o) for o in bpy.data.objects if o.type=='MESH' and (o.name.startswith(('Rounded swept crown lamina','Swept temporal lamina','Continuous temporal shell')) or o.name=='V4 cranial inner shell')};changed=[];added=[];removed=[];errors=[]
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
 for n,a,b,hollow in [('Profiled upper bill blade 0',0,.345,True),('Overlapping nasal hood',.349,.715,True),('Profiled upper bill blade 1',.719,1,False)]:
  v,f=bill(a,b,hollow);install(n,v,f)
 for side in (-1,1):
  v,f=ribbon(side,[(.092,-.531,1.807,.014),(.100,-.565,1.773,.019),(.091,-.593,1.726,.019),(.067,-.618,1.676,.009)],wall=.0045);install(f'Cere root transition {side}',v,f)
  # Upper closed cutting curve tucks beneath the posterior bill seat. The
  # open impression derives only from the unchanged jaw hinge rotation.
  v,f=ribbon(side,[(.119,-.432,1.663,.020),(.100,-.470,1.670,.015),(.079,-.514,1.682,.012),(.069,-.557,1.684,.010),(.061,-.588,1.668,.008),(.039,-.609,1.646,.005),(.026,-.621,1.626,.0025)],wall=.005,along=40);install(f'Forked forged mandible {side}',v,f)
 v,f=crown_sheet([(-.612,1.634,.033),(-.620,1.628,.027),(-.624,1.625,.022)]);install('Distal mandible bridge',v,f)
 for side in (-1,1):
  outline=[(-.353,1.824),(-.395,1.860),(-.449,1.870),(-.501,1.846),(-.548,1.811),(-.556,1.784),(-.548,1.789),(-.538,1.800),(-.523,1.806),(-.505,1.810),(-.486,1.806),(-.468,1.796),(-.442,1.805),(-.416,1.811),(-.393,1.796),(-.374,1.793)]
  v,f=polygon(side,outline,.140,.0055);install(f'Forged orbital brow {side}',v,f)
  outline=[(-.402,1.794),(-.424,1.753),(-.455,1.716),(-.483,1.705),(-.509,1.700),(-.535,1.708),(-.558,1.725),(-.581,1.737),(-.596,1.713),(-.574,1.693),(-.532,1.683),(-.490,1.684),(-.451,1.702),(-.421,1.735),(-.394,1.781)]
  v,f=polygon(side,outline,.137,.006);install(f'Broad swept cheek band {side}',v,f)
  v,f=orbital_facade(side);install(f'Forged orbital mounting plate {side}',v,f)
  outline=[(-.547,1.800),(-.565,1.812),(-.582,1.784),(-.588,1.729),(-.576,1.710),(-.561,1.725),(-.559,1.765)]
  v,f=polygon(side,outline,.121,.006);install(f'V24 anterior orbital root receiver {side}',v,f)
  # Seat the complete true optic/functional race into this face; no lenses or
  # historical passive fittings acquire new era eligibility.
  for prefix in ('Seated Advanced optic','Seated passive optic housing','Recessed orbital bearing','Orbital passive retaining race'):
   n=f'{prefix} {side}';o=bpy.data.objects[n];inv=o.matrix_world.inverted();o.data=o.data.copy()
   for vert in o.data.vertices:
    p=o.matrix_world@vert.co;p.x-=side*.016*1.30;vert.co=inv@p
   o.data.update();changed.append(n)
 # Exact V25 crown/scalp/temporal shells retained: rejected experiment omitted.
 assert crown=={n:snap(bpy.data.objects[n]) for n in crown}
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
 return {'region':'head-selected-bill-jaw-orbit','status':'reference-led major-form proposal; visual/motion acceptance pending','changedMeshes':changed,'added':added,'removed':removed,'stagedOut':removed,'changedNodes':['bill-contact','anchor-beak'],'primaryPivotChanges':[],'preservedNodesExact':len(allnodes)-2,'outsideMeshSnapshotsExact':len(outside),'boundaryShaftsExact':sorted(BOUNDARY),'materialDefinitionsChanged':False,'eraTagsChanged':False,'billContactNativeWorld':list(front),'contactObject':front_object,'contactMethod':'minimum nativeY evaluated formed upper-bill surface vertex','maximumAuthoredWorldPointErrorM':max(errors),'parameters':{'headMassRetained':1.30,'billProfile':BILL,'opticMeshRecessM':.0208,'crownNewPlateCount':0,'originalCrownScalpTemporalMeshesExact':len(crown),'mandibleReceiverRepair':'Posterior jaw routes inboard below optic; distal closed cutting seam and fixed hinge retained','jawHingeUnchanged':True},'limits':['Closed/open neutral visual comparison only; surface/movement clearance remains to be checked.','New hidden receivers and scalp seating are construction proposals; no final finish or owner likeness acceptance.']}
