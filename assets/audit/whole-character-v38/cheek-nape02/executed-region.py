"""Cheek-nape02 from jaw-fit02. Direct clean swept dome panels and closures.
99 existing passive meshes +2 justified closure/support additions. No joint warp.
"""
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
 o['v38CheekNape']='Direct compound-curved finite passive head assembly proposal'
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

LOWER=[f'V33 formed lower cheek receiver {s} {i}'for s in(-1,1)for i in range(2)]
NAMES=CROWN+WALLS+SHIELDS+LOWER+ROOTS+FITTINGS+['V38 fixed occipital closure plate']
ADDED=[]
def apply():
 records=[];lands=[];outer_checks=[]
 for name in CROWN:
  o=bpy.data.objects[name];m=o.data;n=len(m.vertices)//2;before=[list(v.co)for v in m.vertices[:n]];m.calc_loop_triangles();normals=[Vector()for _ in range(n)]
  for t in m.loop_triangles:
   if all(k<n for k in t.vertices):
    a,b,c=[m.vertices[k].co for k in t.vertices];area=(b-a).cross(c-a)
    if area.z<0:area=-area
    for k in t.vertices:normals[k]+=area
  for i in range(n):assert normals[i].length>0;normal=normals[i].normalized();m.vertices[i+n].co=m.vertices[i].co-normal*.003
  m.update();assert [list(v.co)for v in m.vertices[:n]]==before
  o['v38CheekNape']='Only crown inner surface changed to3mm area-weighted outer normal; all outervertices exact'
  outer_checks.append({'name':name,'outerVertexCount':n,'outerCoordinatesExact':True,'normalOffsetM':.003})
  records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'role':'Inner stock correction, outer crown immutable'})
 for side in(-1,1):
  o=bpy.data.objects[f'V31 fixed temporal receiving wall {side}'];v=[o.matrix_world@q.co for q in o.data.vertices]
  for index,q in enumerate(v):
   # The oldwall has72×21 outervertices and mirrored innervertices.
   # A smooth narrow rearward orbital channel opens onto actual passive
   # structure; outer enclosure/boundary remains finite and continuous.
   i=(index%(72*21))//21;j=index%21;angle=2*math.pi*i/72;wrapped=math.atan2(math.sin(angle+.37),math.cos(angle+.37));reveal=.095*math.exp(-(wrapped/.26)**4);delta=reveal*(1-j/20)
   q.y+=delta*math.cos(angle);q.z+=delta*math.sin(angle)
   q.x-=side*.010*math.exp(-((q.y+.47)/.12)**2-((q.z-1.70)/.13)**2)

  install(o.name,v,[tuple(p.vertices)for p in o.data.polygons],'Recessed retained skull enclosure beneath narrow curved armor; no new brain-box opening',records,len(o.data.polygons)-144)
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

  cheeks=[[[ -.635,1.672],[-.582,1.651],[-.530,1.661],[-.486,1.700],[-.453,1.758],[-.426,1.786],[-.410,1.771],[-.435,1.711],[-.466,1.667],[-.512,1.629],[-.542,1.636],[-.588,1.640],[-.635,1.659]],
   [[-.439,1.780],[-.397,1.782],[-.340,1.774],[-.306,1.698],[-.358,1.738],[-.387,1.762],[-.432,1.756]],
   [[-.413,1.698],[-.375,1.696],[-.339,1.681],[-.318,1.588],[-.357,1.632],[-.392,1.669],[-.423,1.678]]]
  for i,p in enumerate(cheeks):patch(f'V38 optic cheek shield {side} {i}',p,.0045,.009+i*.003,'Narrow curved structural cheekband or short sweptrear plate; purposeful recessed machinerychannel')
  patch(f'V33 formed lower cheek receiver {side} 0',[[-.681,1.692],[-.631,1.686],[-.582,1.660],[-.537,1.664],[-.530,1.650],[-.583,1.642],[-.635,1.669],[-.680,1.674]],.0045,.021,'Narrow finite lowerorbital return, trueoptic andbillroot untouched')
  # A real finite annular receivingplate with explicit11.5mm bore centred
  # on truejawjournal, replacing the old broad triangular receiver sheet.
  cy,cz=-.4792,1.615284;count=64;verts=[]
  for x,rad in [(side*.161,.0115),(side*.161,.024),(side*.1655,.0115),(side*.1655,.024)]:
   verts.extend(Vector((x,cy+rad*math.cos(2*math.pi*j/count),cz+rad*math.sin(2*math.pi*j/count)))for j in range(count))
  faces=[]
  for j in range(count):k=(j+1)%count;faces.extend([(j,k,count+k,count+j),(2*count+j,3*count+j,3*count+k,2*count+k),(j,2*count+j,2*count+k,k),(count+j,count+k,3*count+k,3*count+j)])
  install(f'V33 formed lower cheek receiver {side} 1',verts,faces,'Finite11.5mm explicit jawreceivingbore,24mm outerrim; actualjournal/clevis/axle untouched',records,4*count)
  for i,target in enumerate([f'V31 fixed temporal receiving wall {side}',f'V38 optic cheek shield {side} 1',f'V38 optic cheek shield {side} 2']):
   o=bpy.data.objects[target];o.data.calc_loop_triangles();pp=[o.matrix_world@v.co for v in o.data.vertices];tree=BVHTree.FromPolygons(pp,[tuple(t.vertices)for t in o.data.loop_triangles],all_triangles=True);cy0,cz0=[(-.340,1.715),(-.363,1.764),(-.357,1.667)][i];base=[]
   for row in range(3):
    for col in range(3):hit,normal,idx,dist=tree.ray_cast(Vector((side*.5,cy0+(row-1)*.006,cz0+(col-1)*.006)),Vector((-side,0,0)));assert hit is not None,(target,'full12mmfoot corner');base.append(hit)
   ff=[(0,1,4),(0,4,3),(1,2,5),(1,5,4),(3,4,7),(3,7,6),(4,5,8),(4,8,7)];n=9;plane=max(abs(p.x)for p in base)+.004;v=base+[Vector((side*plane,p.y,p.z))for p in base];faces=[tuple(reversed(t))for t in ff]+[tuple(n+k for k in t)for t in ff];border=[0,1,2,5,8,7,6,3]
   for j,a in enumerate(border):b=border[(j+1)%8];faces.append((a,b,n+b,n+a))
   name=f'V31 temporal fitting root {side} {i}';install(name,v,faces,'Full12mm finite receivingpad over named actualreceiver; facecompatibilitycheck separate',records)
   count=48;profile=[(plane,.004),(plane+.001,.004),(plane+.003,.0035),(plane+.003,.0018),(plane,.0018)];fv=[Vector((side*x,cy0+rad*math.cos(2*math.pi*j/count),cz0+rad*math.sin(2*math.pi*j/count)))for x,rad in profile for j in range(count)];faces=[]
   for row in range(5):
    for j in range(count):k=(j+1)%count;nextrow=(row+1)%5;faces.append((row*count+j,row*count+k,nextrow*count+k,nextrow*count+j))
   fit=f'V31 passive temporal fitting {side} {i}';install(fit,fv,faces,'Passive8mm annulus on finite12mm receivingpad, no sensing or motor',records);lands.append({'root':name,'fitting':fit,'receiver':target,'actualInnerTriangles':8,'actualFullPatchYZExtentsM':[.012,.012],'fittingFootDiameterM':.008,'returnOuterNativeSignedX':side*plane,'minimumAxialReturnDepthM':.004})

 grid('V38 fixed occipital closure plate',lambda u,v:Vector((.096*math.sin((2*u-1)*1.45)*(.82+.18*v),-.365+.104*math.cos((2*u-1)*1.45),1.578+.108*v-.012*math.sin((2*u-1)*1.45)**2)),28,18,.004,'Short curved fixedhead-owned napeskirt; separate sliding upperneck interface, not rigidjointbridge',records,lambda u,v:Vector((math.sin((2*u-1)*1.45),math.cos((2*u-1)*1.45),0)))
 return {'changedMeshes':NAMES,'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'attachmentAndEraMap':records,'pairedFittingSeats':lands,'crownOuterPreservation':outer_checks,'construction':'83 existing passive meshes: narrow curved cheek/jawreceivingplates, short napeskirt and crown innerstock only. Exact outercrown/bill/optic/jaw mechanism preserved.','openingAttachment':'Cranial-cover upward nativeZ/runtimeY+.08open+.14separation; fixedhead nape doesnotjoin movingneck.','rigidVsFlexible':'All finite rigid inheritedpassive Maker/Mechanic/Builder; no addedobjects orpoweredhardware.','confirmation':'JulyHEADONLY controls; sourceactual83 surveyed andprotectedjournal verified separately.','reconstruction':'Plate footprints/napeandhiddenreceivingstock are proposal, notartmetrology orloadcertificate.','protected':'Crownoutercoordinates,trueoptic,billcontact,jaw/socket/journals/clevis/axle,allownerframes/pivots/neck/body exact.','limits':['3mm normal vertexpairs require actualself/stockchecks; no acceptedsolidfit.','11.5mm receivingbore alone doesnotprove clearanceof neighboring realjournalgeometry.','Actualfixednape/neckscreen aftervisualgate is scoped sampled evidence, notfullsweep.']}
