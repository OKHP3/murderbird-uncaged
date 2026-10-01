"""Swept-cranium02 from jaw-fit02. Direct clean swept dome panels and closures.
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
 o['v38SweptCranium']='Direct compound-curved finite passive head assembly proposal'
 records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'role':kind,'closedEdges':True,'positiveVolumeM3':volume,'materials':[q.name if q else None for q in m.materials]})

def grid(name,fn,nu,nv,stock,kind,records,normal_axis=None):
 p=[fn(i/nu,j/nv)for i in range(nu+1)for j in range(nv+1)];normals=[]
 for i in range(nu+1):
  for j in range(nv+1):
   if normal_axis is not None:n=normal_axis
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

def apply():
 records=[];lands=[];bounds=[]
 # Global regular cap field: monotone longitudinalY and monotone lateralX
 # for theta in(-1.34,+1.34); no inherited warped outer/inner topology.
 def dome(t,v):
  theta=(2*v-1)*1.34;s=math.sin(math.pi*t);r=max(0,min(1,(t-.46)/.54));rear=r*r*(3-2*r)
  return Vector((.123*(.84+.16*s)*math.sin(theta)*(1-.11*rear),-.6532+.4062*t,1.812+.0818*s-.130*rear-(.024+.053*s)*math.sin(theta)**2))
 for name,template in [(ADDED[0],CROWN[3]),(ADDED[1],WALLS[0])]:
  o=bpy.data.objects[template].copy();o.name=name;bpy.context.scene.collection.objects.link(o);bpy.context.view_layer.update();o['constructionClass']='inherited-passive';o['constructionRole']='recessed skull support'if name==ADDED[0]else'fixed occipital closure';o['exteriorEras']='maker,mechanic,builder'
 grid(ADDED[0],lambda t,v:dome(t,v)-Vector((0,0,.004)),40,28,.004,'Recessed finite continuous cranial-cover-owned support beneath separate58 plates; same upward opening group',records)
 # Each dominant leaf has an explicit tapered swept footprint; companion
 # leaf is a separate finite receiving/lap plate. No old outer grid warp.
 def crown_patch(name,poly,lift,kind):
  uv=[Vector((t,v,0)) for t,v in poly];tri=tessellate_polygon([uv]);idx=lambda q:q if isinstance(q,int)else next(i for i,p in enumerate(uv)if(p-q).length<1e-8);fs=[tuple(idx(q)for q in t)for t in tri]
  for it in range(2):
   cache={};new=[]
   def midpoint(a,b):
    key=tuple(sorted((a,b)))
    if key not in cache:cache[key]=len(uv);uv.append((uv[a]+uv[b])*.5)
    return cache[key]
   for a,b,c in fs:ab,bc,ca=midpoint(a,b),midpoint(b,c),midpoint(c,a);new +=[(a,ab,ca),(ab,b,bc),(ca,bc,c),(ab,bc,ca)]
   fs=new
  from collections import Counter
  ta=min(q.x for q in uv);tb=max(q.x for q in uv);p=[]
  for q in uv:
   u=(q.x-ta)/(tb-ta);free=max(0,(u-.50)/.50);free=free*free*(3-2*free)
   p.append(dome(q.x+.027*free,q.y)+Vector((0,0,lift+.013*free)));n=len(p);verts=p+[q-Vector((0,0,.003))for q in p];faces=fs+[tuple(n+k for k in reversed(t))for t in fs];edges=Counter(tuple(sorted((f[j],f[(j+1)%3])))for f in fs for j in range(3))
  for t in fs:
   for j in range(3):
    a,b=t[j],t[(j+1)%3]
    if edges[tuple(sorted((a,b)))]==1:faces.append((a,b,n+b,n+a))
  install(name,verts,faces,kind,records,2*len(fs));return p
 ranges=[(0,.28),(.18,.48),(.37,.68),(.56,.88),(.74,1)]
 for name in CROWN:
  bits=name.split();row=int(bits[4]);col=int(bits[6]);leaf=int(bits[8]);lo,hi=ranges[row];cols=[range(7),range(7),range(7),range(1,6),range(2,5)][row];count=len(cols);rank=list(cols).index(col);centre=(rank+.5)/count;half=.59/count
  # Distinct lance-like tips alternate a small rearward progression. The
  # support is hidden beneath these named outlines, not a visible dome seam.
  lo=max(0,lo+.009*(rank%2));hi=min(1,hi-.012*((rank+row)%2))
  if leaf==1:shape=[(0,-.62),(.04,.63),(.25,.87),(.48,.78),(.75,.43),(1,-.18),(.73,-.45),(.38,-.76),(.15,-.88)]
  else:shape=[(.02,-.68),(.03,.62),(.30,.83),(.59,.54),(.68,-.11),(.45,-.64),(.16,-.84)]
  sweep=(-1 if centre<.5 else 1)*.014
  poly=[(lo+(hi-lo)*u,max(0,min(1,centre+half*w+sweep*u)))for u,w in shape]
  # Fixed-Z stock remains a single-valued graph even at the nape downturn.
  lift=.006+row*.0015 if leaf==1 else .0025+row*.0015
  bounds+=crown_patch(name,poly,lift,'Individually outlined swept crown leaf'if leaf==1 else'Finite narrower receiving/lap plate underneath swept leaf; independent passive part')
 # Shaped fixed rearclosure follows headcrosssection and stays below independentcover.
 grid(ADDED[1],lambda u,v:Vector((.102*(2*u-1)*(1-.12*v),-.252-.026*(1-v)**2-.010*(2*u-1)**2,1.585+.103*v-.022*(2*u-1)**2)),20,16,.004,'Shaped fixed-head occipital closure below movablecap rim; narrow vertical withdrawal overlap, not flat visible slab',records,Vector((0,1,0)))
 def lateral(y,z):return .092+.014*math.exp(-((y+.51)/.16)**2-((z-1.73)/.14)**2)
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
  # Fixed posterior enclosure with actual opticbore; recessed below armor.
  cy,cz=-.5778,1.725484;ey,ez=-.455,1.715;ry,rz=.197,.130
  def sidewall(u,v):
   angle=2*math.pi*u;dy,dz=math.cos(angle),math.sin(angle);b=2*((cy-ey)*dy/ry**2+(cz-ez)*dz/rz**2);aa=dy*dy/ry**2+dz*dz/rz**2;c=(cy-ey)**2/ry**2+(cz-ez)**2/rz**2-1;outer=(-b+math.sqrt(b*b-4*aa*c))/(2*aa);inner=.064;assert outer>inner
   rr=inner+(outer-inner)*v;y,z=cy+rr*dy,cz+rr*dz;return Vector((side*lateral(y,z),y,z))
  # closed seam is explicit duplicatedparameter edge welded before topologyguard
  pts=[sidewall(i/72,j/20)for i in range(72)for j in range(21)];n=len(pts);verts=pts+[p-Vector((side*.0045,0,0))for p in pts];faces=[]
  for i in range(72):
   for j in range(20):a=i*21+j;b=((i+1)%72)*21+j;faces.extend([(a,a+1,b+1,b),(n+b,n+b+1,n+a+1,n+a)])
   for j in (0,20):a=i*21+j;b=((i+1)%72)*21+j;faces.append((a,b,n+b,n+a))
  install(f'V31 fixed temporal receiving wall {side}',verts,faces,'Recessed shaped skullside support with true opticbore, continuous rearclosure interface; armor covers broad field, no exposed truss',records,2*72*20)
  brows=[[[ -.649,1.797],[-.621,1.833],[-.572,1.842],[-.540,1.816],[-.581,1.802],[-.630,1.784]],
   [[-.584,1.839],[-.520,1.851],[-.452,1.820],[-.454,1.790],[-.520,1.819],[-.583,1.817]],
   [[-.471,1.825],[-.390,1.813],[-.328,1.763],[-.343,1.739],[-.404,1.777],[-.482,1.797]]]
  for i,p in enumerate(brows):patch(f'V33 diagonal brow receiver {side} {i}',p,.0045,.012+i*.002,'Compact swept receivingbrow under newcap side; actual fixedhead owner and unobstructedeye retained')
  cheeks=[[[ -.632,1.672],[-.581,1.650],[-.530,1.657],[-.483,1.691],[-.460,1.743],[-.443,1.785],[-.420,1.777],[-.440,1.719],[-.474,1.674],[-.530,1.641],[-.589,1.640],[-.632,1.657]],
   [[-.455,1.807],[-.384,1.796],[-.287,1.722],[-.353,1.738],[-.380,1.765],[-.447,1.786]],
   [[-.443,1.702],[-.375,1.704],[-.344,1.682],[-.280,1.627],[-.350,1.645],[-.399,1.670],[-.460,1.681]]]
  for i,p in enumerate(cheeks):patch(f'V38 optic cheek shield {side} {i}',p,.0045,.016+i*.003,'Distinct compound-curved cheekmember/guard spanning actual skullvolume, tapering to rear/jaw; narrow machineryreveal')
  leaves=[[[ -.431,1.810],[-.370,1.792],[-.321,1.748],[-.337,1.728],[-.388,1.764],[-.445,1.786]],
   [[-.360,1.770],[-.304,1.734],[-.266,1.685],[-.283,1.669],[-.327,1.706],[-.376,1.744]],
   [[-.325,1.709],[-.269,1.662],[-.289,1.625],[-.333,1.657],[-.353,1.689]],
   [[-.352,1.657],[-.308,1.622],[-.337,1.595],[-.378,1.637]],
   [[-.431,1.687],[-.387,1.668],[-.359,1.630],[-.386,1.610],[-.443,1.656]],
   [[-.475,1.779],[-.446,1.752],[-.426,1.718],[-.442,1.697],[-.481,1.743]],
   [[-.443,1.803],[-.398,1.782],[-.356,1.749],[-.375,1.728],[-.419,1.764],[-.453,1.779]]]
  for i,p in enumerate(leaves):patch(f'V33 swept temporal leaf {side} {i}',p,.0035,.023+(i%2)*.003,'Short independently formed sweptguard covering rear skull, narrow deliberate overlap/seam; passive allera')
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
 # Fixed frontal receivingseat reconstructed to compact forehead envelope,
 # retains headparent/rest, never opticalcup or upperbill ownership.
 grid('V31 frontal cranial cap receiving seat',lambda u,v:Vector((.113*(2*v-1),-.641+.091*u,1.795+.040*u-.027*(2*v-1)**2)),18,18,.004,'Compact fixed frontal receivingseat below independent crown, truebill/optic geometry unchanged',records)
 return {'changedMeshes':NAMES,'changedNodes':[],'addedMeshes':ADDED,'removedMeshes':[],'attachmentAndEraMap':records,'pairedFittingSeats':lands,'actualNewCrownBoundsNative':[[min(p[k]for p in bounds),max(p[k]for p in bounds)]for k in range(3)],'construction':'Individually designed asymmetric tapered plate footprints over a recessed compact support; companion receiving plates stay finite. No inherited crown warp or broad rectangular grid exterior. Fixed temporal support recedes beneath shaped cheek guards. Stock/lap/support fit remains proposal.','openingAttachment':'Cranial-cover withdraws vertically nativeZ/runtimeY +.08m open +.14m separation; fixedhead closure never reparented or rigidlybridged.','rigidVsFlexible':'99 existing passive+2 closure meshes;58+inner shell on cranial-cover,41+occipital on head; all Maker/Mechanic/Builder, no poweredhardware.','confirmation':'ActualJuly HEADONLY +Master03/Makerclean; sourcephotos jawfit02 viewed beforegeneration.','reconstruction':'Compactvolume/crowncourses/receivingmembers and unseenclosures are authored proposal, not exactart dimensions.','protected':'Trueoptic/bill/contact/jaw/socket/journals/body andall originalownerframes/pivots exact.','limits':['Clean manifoldpositive shells are not a fullfit certificate.','Fullannularbase and actualnewpanelself checks separate aftervisualgate.','Receiverface pointseating doesnot establish compatible fulltriangulation or loadacceptance.']}
