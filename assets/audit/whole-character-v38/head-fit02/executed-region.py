"""Head-fit02 from exact HELD cheek-nape02.65 actualmeshchanges,
83 watchscope; constant fitted crown extrusion, fulltriangle feet, local relief.
No additions/reparents; truehardwareandoutercrown exact."""
import bpy,bmesh,math
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
from mathutils.bvhtree import BVHTree
BROWS=[f'V33 diagonal brow receiver {s} {i}'for s in(-1,1)for i in range(3)]
SHIELDS=[f'V38 optic cheek shield {s} {i}'for s in(-1,1)for i in range(3)]
LEAVES=[f'V33 swept temporal leaf {s} {i}'for s in(-1,1)for i in range(7)]
ROOTS=[f'V31 temporal fitting root {s} {i}'for s in(-1,1)for i in range(3)]
FITTINGS=[f'V31 passive temporal fitting {s} {i}'for s in(-1,1)for i in range(3)]
WALLS=[f'V31 fixed temporal receiving wall {s}'for s in(-1,1)]
CROWN=[f'V38 swept crown course {row} column {col} leaf {leaf}'for row,cols in [(0,range(7)),(1,range(7)),(2,range(7)),(3,range(1,6)),(4,range(2,5))]for col in cols for leaf in (1,2)]
NAMES=WALLS+BROWS+SHIELDS+LEAVES+ROOTS+FITTINGS+CROWN+['V31 frontal cranial cap receiving seat']
ADDED=['V38 compact cranial inner shell','V38 fixed occipital closure plate']

def install(name,verts,faces,kind,records,smooth_cap_count=0):
 o=bpy.data.objects[name];m=bpy.data.meshes.new(name+' direct clean finite shell');inv=o.matrix_world.inverted();m.from_pydata([inv@p for p in verts],[],faces);m.update()
 for mat in o.data.materials:m.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 volume=bm.calc_volume(signed=True);assert volume>0;bm.to_mesh(m);bm.free();o.data=m
 for i,f in enumerate(m.polygons):f.use_smooth=i<smooth_cap_count
 o['v38HeadFit']='Direct compound-curved finite passive head assembly proposal'
 records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'role':kind,'closedEdges':True,'positiveVolumeM3':volume,'materials':[q.name if q else None for q in m.materials]})

def grid(name,fn,nu,nv,stock,kind,records,normal_axis=None):
 p=[fn(i/nu,j/nv)for i in range(nu+1)for j in range(nv+1)];normals=[]
 for i in range(nu+1):
  for j in range(nv+1):
   if normal_axis is not None:n=normal_axis(i/nu,j/nv) if callable(normal_axis) else normal_axis
   else:
    du=fn(min(1,i/nu+.0001),j/nv)-fn(max(0,i/nu-.0001),j/nv);dv=fn(i/nu,min(1,j/nv+.0001))-fn(i/nu,max(0,j/nv-.0001));n=du.cross(dv).normalized()
    if n.z<0:n=-n
   normals.append(n)
 n=len(p);verts=p+[q-stock*k for q,k in zip(p,normals)];faces=[];stride=nv+1
 for i in range(nu):
  for j in range(nv):
   k=i*stride+j;faces.extend([(k,k+stride,k+stride+1,k+1),(n+k+1,n+k+stride+1,n+k+stride,n+k)])
 border=list(range(stride))+[i*stride+nv for i in range(1,nu+1)]+[nu*stride+j for j in range(nv-1,-1,-1)]+[i*stride for i in range(nu-1,0,-1)]
 for i,a in enumerate(border):b=border[(i+1)%len(border)];faces.append((a,b,n+b,n+a))
 install(name,verts,faces,kind,records,2*nu*nv);return p,normals

def rounded(poly):
 for it in range(1):
  poly=[q for a,b in zip(poly,poly[1:]+poly[:1])for q in ([.88*a[k]+.12*b[k]for k in range(2)],[.12*a[k]+.88*b[k]for k in range(2)])]
 return poly

WATCH=CROWN+WALLS+SHIELDS+[f'V33 formed lower cheek receiver {s} {i}'for s in(-1,1)for i in range(2)]+ROOTS+FITTINGS+['V38 fixed occipital closure plate']
NAMES=CROWN+[f'V38 optic cheek shield {s} {i}'for s in(-1,1)for i in (0,2)]+[f'V31 temporal fitting root {s} 0'for s in(-1,1)]+['V38 fixed occipital closure plate']
ADDED=[]
def apply():
 records=[];stock=[];lands=[]
 for name in CROWN:
  o=bpy.data.objects[name];m=o.data;n=len(m.vertices)//2;m.calc_loop_triangles();outer=[v.co.copy()for v in m.vertices[:n]];tri=[];norm=[]
  for t in m.loop_triangles:
   if all(k<n for k in t.vertices):
    a,b,c=[outer[k]for k in t.vertices];q=(b-a).cross(c-a).normalized();q=-q if q.z<0 else q
    if q.length:tri.append(tuple(t.vertices));norm.append(q)
  candidates=[Vector((0,0,1)),sum(norm,Vector()).normalized()]+norm;direction=max(candidates,key=lambda q:min(q.dot(v)for v in norm));score=min(direction.dot(q)for q in norm)
  for step in range(50):
   worst=min(norm,key=lambda q:direction.dot(q));trial=(direction+worst*.2).normalized();value=min(trial.dot(q)for q in norm)
   if value>score:direction,score=trial,value
  assert score>0,name;centre=sum(outer,Vector())/n;bevel=.02;floor=.001
  length=max((floor-bevel*(outer[k]-centre).dot(normal))/normal.dot(direction)for t,normal in zip(tri,norm)for k in t)
  assert length<.009,(name,length)
  for i,q in enumerate(outer):m.vertices[i+n].co=centre+(q-centre)*(1-bevel)-direction*length
  m.update();assert all((m.vertices[i].co-q).length==0 for i,q in enumerate(outer));o['v38HeadFit']='Coherent perleaf constant finite extrusion with inset innerperimeter; outercoordinates exact'
  stock.append({'name':name,'outerExact':True,'directionLocal':list(direction),'minimumOuterFaceDirectionalDot':score,'extrusionLengthM':length,'innerPerimeterInsetFraction':bevel,'targetMinimumMatchedOuterFaceProjectionM':floor})
  records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'role':'Coherent finite innercap/sideclosures, exact outercrown'})
 def lateral(y,z):return .115+.020*math.exp(-((y+.54)/.15)**2-((z-1.70)/.12)**2)
 for side in(-1,1):
  def patch(name,poly,stock,lift,kind):
   yz=rounded(poly);p=[Vector((side*(lateral(y,z)+lift),y,z))for y,z in yz];tri=tessellate_polygon([p]);idx=lambda v:v if isinstance(v,int)else next(i for i,q in enumerate(p)if(q-v).length<1e-8);fs=[tuple(idx(v)for v in t)for t in tri]
   for iteration in range(2):
    cache={};new=[]
    def mid(a,b):
     key=tuple(sorted((a,b)))
     if key not in cache:q=(p[a]+p[b])*.5;q.x=side*(lateral(q.y,q.z)+lift);cache[key]=len(p);p.append(q)
     return cache[key]
    for a,b,c in fs:ab,bc,ca=mid(a,b),mid(b,c),mid(c,a);new.extend([(a,ab,ca),(ab,b,bc),(ca,bc,c),(ab,bc,ca)])
    fs=new
   from collections import Counter
   ec=Counter(tuple(sorted((f[j],f[(j+1)%3])))for f in fs for j in range(3));n=len(p);verts=p+[q-Vector((side*stock,0,0))for q in p];faces=fs+[tuple(n+k for k in reversed(t))for t in fs]
   for t in fs:
    for j in range(3):
     a,b=t[j],t[(j+1)%3]
     if ec[tuple(sorted((a,b)))]==1:faces.append((a,b,b+n,a+n))
   install(name,verts,faces,kind,records,2*len(fs))


  patch(f'V38 optic cheek shield {side} 0',[[ -.635,1.672],[-.582,1.675],[-.530,1.690],[-.488,1.701],[-.453,1.758],[-.426,1.786],[-.410,1.771],[-.435,1.724],[-.466,1.690],[-.509,1.682],[-.542,1.669],[-.588,1.652],[-.635,1.659]],.0045,.009,'Local tapered rear cheekreturn rises above actualprotectedbowl witness; orbital channel retained')
  patch(f'V38 optic cheek shield {side} 2',[[-.413,1.698],[-.375,1.696],[-.339,1.681],[-.326,1.629],[-.357,1.652],[-.392,1.669],[-.423,1.678]],.0045,.015,'Shorter finite lowerrear tip clears named fixedthroat witness instead ofmovingprotectedthroat')
  # Fullroot0 foot uses clipped actual receiver triangles, not nine rayhits.
  target=bpy.data.objects[f'V31 fixed temporal receiving wall {side}'];m=target.data;m.calc_loop_triangles();points=[target.matrix_world@v.co for v in m.vertices];n=len(points)//2;polys=[]
  def clip(poly,axis,value,keep):
   result=[]
   for a,b in zip(poly,poly[1:]+poly[:1]):
    aa=(a[axis]-value)*keep>=-1e-10;bb=(b[axis]-value)*keep>=-1e-10
    if aa:result.append(a)
    if aa!=bb:result.append(a+(b-a)*((value-a[axis])/(b[axis]-a[axis])))
   return result
  for t in m.loop_triangles:
   if not all(k<n for k in t.vertices):continue
   poly=[points[k]for k in t.vertices]
   for axis,limit,keep in [(1,-.346,1),(1,-.334,-1),(2,1.709,1),(2,1.721,-1)]:
    if poly:poly=clip(poly,axis,limit,keep)
   if len(poly)>2:polys.append(poly)
  assert polys;foot=[];index={};faces=[]
  for poly in polys:
   row=[]
   for q in poly:
    key=tuple(round(v,7)for v in q)
    if key not in index:index[key]=len(foot);foot.append(q)
    row.append(index[key])
   for j in range(1,len(row)-1):
    t=(row[0],row[j],row[j+1])
    if len(set(t))==3 and (foot[t[1]]-foot[t[0]]).cross(foot[t[2]]-foot[t[0]]).length>1e-12:faces.append(t)
  from collections import Counter
  counts=Counter(tuple(sorted((t[j],t[(j+1)%3])))for t in faces for j in range(3));root=bpy.data.objects[f'V31 temporal fitting root {side} 0'];plane=max(abs((root.matrix_world@v.co).x)for v in root.data.vertices);n=len(foot);verts=foot+[Vector((side*plane,q.y,q.z))for q in foot];fs=faces+[tuple(n+k for k in reversed(t))for t in faces]
  for t in faces:
   for j in range(3):
    a,b=t[j],t[(j+1)%3]
    if counts[tuple(sorted((a,b)))]==1:fs.append((a,b,n+b,n+a))
  install(root.name,verts,fs,'Complete12mm foot tessellates actualclipped temporalreceiver faces; finiteouterpad retained for8mm fitting',records)
  lands.append({'root':root.name,'fitting':f'V31 passive temporal fitting {side} 0','receiver':target.name,'actualFullPatchYZExtentsM':[.012,.012],'fittingFootDiameterM':.008,'returnOuterNativeSignedX':side*plane,'actualClippedReceiverTriangles':len(faces)})
 # Inboard shapedskirt ends retain shortnape silhouette with deliberate
 # radial clearance behind actualtemporalwall; no fixedneck motion.
 grid('V38 fixed occipital closure plate',lambda u,v:Vector((.080*math.sin((2*u-1)*1.45)*(.82+.18*v),-.365+.104*math.cos((2*u-1)*1.45),1.578+.108*v-.012*math.sin((2*u-1)*1.45)**2)),28,18,.004,'Shortinboard curved napeskirt with deliberate finitewall lapgap; no rigidneckbridge',records,lambda u,v:Vector((math.sin((2*u-1)*1.45),math.cos((2*u-1)*1.45),0)))
 return {'changedMeshes':NAMES,'watchMeshes':WATCH,'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'attachmentAndEraMap':records,'pairedFittingSeats':lands,'crownFiniteStock':stock,'construction':'65 actualchanged83 watch: coherentconstant crowninnerextrusions, clipped finitefootfaces and localcheek/nape interface relief.','openingAttachment':'Sourceframesexact; coververticalnativeZ/runtimeY+.08open+.14separation; headownedskirtnotneckbridge.','rigidVsFlexible':'Passive rigid all3inheritederas; truebill/jaw/optic/bodyexact.','confirmation':'Actualsource self/contact witnesses drive boundedrepair; JulyHEADONLY silhouette retained.','reconstruction':'1mm faceprojectedstock target isexhibitproposal, notengineeringgauge approval.','protected':'Outer58 crownarrays/truejaw/socket/bill/optic/frames/materialsexact.','limits':['Matchedtriangleprojectedstock isnot minimumsolidrim thickness.','Actualstrictself/interpart checks mustdisclose everynew/residualpair; no attachmentapprovalfrom ownership.']}
