"""Directional fixed head side volume and compact optic recess; authored study."""
import bpy,bmesh,math,runpy
from mathutils import Vector
REMOVED=[f'V33 diagonal brow receiver {s} {i}'for s in[-1,1]for i in range(3)]+[f'V38 optic cheek shield {s} {i}'for s in[-1,1]for i in range(3)]
# Counter-clockwise native YZ outline: actual volume, not a circular outer bezel.
OUTLINE=[(-.683,1.682,.109),(-.666,1.753,.112),(-.620,1.790,.127),(-.536,1.811,.137),(-.440,1.793,.113),(-.342,1.755,.095),(-.366,1.697,.102),(-.442,1.657,.123),(-.510,1.633,.139),(-.601,1.625,.143),(-.663,1.647,.123)]
CY,CZ=-.5958000421524048,1.6904840469360352

def stock(o):
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 non=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);todo=set(bm.verts);comp=0
 while todo:
  comp+=1;run=[todo.pop()]
  while run:
   for e in run.pop().link_edges:
    for v in e.verts:
     if v in todo:todo.remove(v);run.append(v)
 bm.to_mesh(o.data);bm.free();return {'nonmanifoldEdges':non,'signedVolumeM3':vol,'connectedComponents':comp}
def replace(o,v,f):
 m=bpy.data.meshes.new(o.name+' directional finite stock');m.from_pydata([list(o.matrix_world.inverted()@Vector(p))for p in v],[],f);m.update()
 for mat in o.data.materials:m.materials.append(mat)
 o.data=m
 for p in m.polygons:p.use_smooth=False
 o['constructionDescription']='Reconstructed fixed head-owned directional facial wall/compact optic seat; authored finite stock, assembly fit not certified.';o['v38FacialFit01']='Proposal; lens centre/diameter and all unrelated geometry retained'
 return stock(o)
def boundary(phi):
 dy,dz=math.cos(phi),math.sin(phi);best=None
 for a,b in zip(OUTLINE,OUTLINE[1:]+OUTLINE[:1]):
  ay,az=a[0]-CY,a[1]-CZ;ey,ez=b[0]-a[0],b[1]-a[1];det=dy*(-ez)+dz*ey
  if abs(det)<1e-10:continue
  t=(ay*(-ez)+az*ey)/det;u=(dy*az-dz*ay)/det
  if t>0 and -.00001<=u<=1.00001 and(best is None or t<best[0]):best=(t,a[2]+(b[2]-a[2])*u)
 assert best,phi
 return best

def wall(side):
 o=bpy.data.objects[f'V31 fixed temporal receiving wall {side}'];n,k=96,10;v=[]
 for inner in[False,True]:
  for j in range(k+1):
   t=j/k
   for i in range(n):
    phi=2*math.pi*i/n;r,xend=boundary(phi);rr=.0415+(r-.0415)*t
    # Recess throat locally; sloped broad planes turn inward into skull at outer lands.
    x=.151*(1-t)+xend*t+.006*math.sin(math.pi*t)*max(0,math.sin(phi))
    v.append((side*(x-(.0045 if inner else 0)),CY+rr*math.cos(phi),CZ+rr*math.sin(phi)))
 f=[];h=(k+1)*n
 for j in range(k):
  for i in range(n):a=j*n+i;b=j*n+(i+1)%n;c=(j+1)*n+(i+1)%n;d=(j+1)*n+i;f.extend([(a,b,c,d),(h+d,h+c,h+b,h+a)])
 for j in[0,k]:
  for i in range(n):a=j*n+i;b=j*n+(i+1)%n;f.append((a,h+a,h+b,b))
 return o,replace(o,v,f)
def ring(name,side,inner,outer,x0,x1,sectors=None):
 o=bpy.data.objects[name];v=[];f=[]
 if inner==0:
  n=96
  for x in[x0,x1]:
   for i in range(n):a=2*math.pi*i/n;v.append((side*x,CY+outer*math.cos(a),CZ+outer*math.sin(a)))
  v.extend([(side*x0,CY,CZ),(side*x1,CY,CZ)])
  for i in range(n):j=(i+1)%n;f.extend([(i,j,n+j,n+i),(2*n,j,i),(2*n+1,n+i,n+j)])
  return replace(o,v,f)
 for lo,hi in(sectors or[(0,2*math.pi)]):
  closed=abs(hi-lo-2*math.pi)<1e-6;n=96 if closed else 32;count=n if closed else n+1;base=len(v)
  for x,rad in[(x0,inner),(x0,outer),(x1,outer),(x1,inner)]:
   for i in range(count):a=lo+(hi-lo)*i/n;v.append((side*x,CY+rad*math.cos(a),CZ+rad*math.sin(a)))
  for r in range(4):
   for i in range(n):a=base+r*count+i;b=base+r*count+(i+1)%count;c=base+((r+1)%4)*count+(i+1)%count;d=base+((r+1)%4)*count+i;f.append((a,b,c,d))
  if not closed:f.extend([tuple(base+r*count for r in range(4)),tuple(base+r*count+n for r in reversed(range(4)))])
 return replace(o,v,f)
def choose_patch(name,target,side,optic):
 o=bpy.data.objects[name];v=[o.matrix_world@p.co for p in o.data.vertices];choices=[]
 for f in o.data.polygons:
  ps=[v[i]for i in f.vertices];n=(ps[1]-ps[0]).cross(ps[2]-ps[0]).normalized();c=sum(ps,Vector())/len(ps)
  if side*c.x<=0:continue
  if name=='V31 frontal cranial cap receiving seat':
   if not(side*n.x>.2 or n.z>.4):continue
  elif 'load bow'in name:
   if side*n.x>-.15:continue
  elif side*n.x<.25:continue
  choices.append(((c-Vector(target)).length,f.index,ps,n))
 assert choices,('No real finite seat patch',name);distance,index,ps,n=min(choices,key=lambda p:p[0]);c=sum(ps,Vector())/len(ps);ps=[c+(p-c)*.70 for p in ps];return{'target':name,'face':index,'receiverCorners':[list(p)for p in ps],'normal':list(n),'desiredToActualFaceCentreM':distance},ps,n
def convex(name,points):
 m=bpy.data.meshes.new(name);bm=bmesh.new();vs=[bm.verts.new(p)for p in points];result=bmesh.ops.convex_hull(bm,input=vs,use_existing_faces=False);bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_edges],context='VERTS');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(m);bm.free();o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o);return o
def intersect_volume(a,b):
 o=a.copy();o.data=a.data.copy();bpy.context.scene.collection.objects.link(o);mod=o.modifiers.new('Finite commonstock diagnostic','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=b;bpy.context.view_layer.objects.active=o
 try:
  bpy.ops.object.modifier_apply(modifier=mod.name);r=stock(o);r['boundedByParticipatingVolumes']=0<r['signedVolumeM3']<=min(stock(a)['signedVolumeM3'],stock(b)['signedVolumeM3'])*1.001
 except Exception as error:r={'error':str(error)}
 bpy.data.objects.remove(o,do_unlink=True);return r


def union(a,b):
 mod=a.modifiers.new('Integral passive finite union','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=b;bpy.context.view_layer.objects.active=a;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(b,do_unlink=True)
def new_obj(name,v,f,materials):
 m=bpy.data.meshes.new(name+' authored stock');m.from_pydata(v,[],f);m.update();o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o)
 for mat in materials:
  if mat:m.materials.append(mat)
 return o
def swap(dst,tmp):
 tmp.data.transform(dst.matrix_world.inverted()@tmp.matrix_world);dst.data=tmp.data;bpy.data.objects.remove(tmp,do_unlink=True)
 dst['constructionDescription']='Facial-fit01: formed passive plate/peripheral optic return with finite receiving routes; static fit evidence qualified.';dst['v38FacialFit01']='Bounded construction proposal; not engineering or owner likeness acceptance'
 return stock(dst)
def round_return(dst,side):
 # Disk remains behind lens; only peripheral radial stock bridges12.7mm axial gap.
 n=96;v=[];f=[];cy,cz=CY,CZ
 for x,r in[(.1208,.0395),(.1208,.041),(.1355,.041),(.1355,.0395)]:
  for i in range(n):a=2*math.pi*i/n;v.append((side*x,cy+r*math.cos(a),cz+r*math.sin(a)))
 for row in range(4):
  for i in range(n):j=(i+1)%n;a=row*n+i;b=row*n+j;c=((row+1)%4)*n+j;d=((row+1)%4)*n+i;f.append((a,b,c,d))
 tmp=new_obj('temporary peripheral passive floor return',v,f,list(dst.data.materials));stock(tmp)
 # Floor native world transform is compensated before union.
 tmp.parent=dst.parent;bpy.context.view_layer.update();tmp.matrix_world=__import__('mathutils').Matrix.Identity(4)
 union(dst,tmp);stock(dst);dst['constructionDescription']='Passive rear cavity floor with integral peripheral turned return into compact head-owned cup; clear lens optical radius preserved.';dst['v38FacialFit01']='39.5mm inner return outside38.28mm aperture; authored clearance, actual screen separate'
 return {'name':dst.name,'stock':stock(dst),'returnInnerOuterRadiusM':[.0395,.041],'returnNativeAbsX':[.1208,.1355],'commonStockToCup':intersect_volume(dst,bpy.data.objects[f'V31 optic recessed receiving cup {side}'])}
def route(shield,side,target,desired,end,elbow=None):
 rec,patch,n=choose_patch(target,desired,side,(CY,CZ));pts=[p-n*.0008 for p in patch]+[p+n*.002 for p in patch];e=Vector(end)
 def box(p):return[p+Vector((side*x,y,z))for x in[-.002,.002]for y in[-.002,.002]for z in[-.002,.002]]
 if elbow:
  mid=Vector(elbow);a=convex('temporary inboard root segment',pts+box(mid));b=convex('temporary free receiving segment',box(mid)+box(e));stock(a);stock(b);union(a,b)
 else:a=convex('temporary compact receiving route',pts+box(e))
 stock(a);rec['routeStock']=stock(a);rec['commonStockToReceiver']=intersect_volume(a,bpy.data.objects[target]);rec['commonStockToPlate']=intersect_volume(a,shield);rec['endNativeXYZ']=end;rec['inboardElbowNativeXYZ']=elbow;union(shield,a);return rec

def apply(second=False):
 bpy.context.view_layer.update();profiles={'brow':[(-.485,1.785,1.763,.128),(-.520,1.791,1.751,.144),(-.558,1.788,1.746,.154),(-.605,1.776,1.744,.151),(-.641,1.773,1.731,.130),(-.675,1.743,1.731,.108)],'cheek':[(-.460,1.696,1.675,.110),(-.485,1.677,1.650,.138),(-.515,1.667,1.638,.151),(-.550,1.657,1.626,.155),(-.601,1.650,1.622,.155),(-.645,1.664,1.638,.148),(-.677,1.653,1.644,.122)]};records=[];changed=[]
 for side in[-1,1]:
  floor=bpy.data.objects[f'V31 passive optic cavity floor {side}'];records.append(round_return(floor,side));changed.append(floor.name)
  for kind,rows in profiles.items():
   name=f'V38 facial-shell {"brow roof"if kind=="brow"else"cheek bridge"} {side}';dst=bpy.data.objects[name];nu,nv=48,8;v=[]
   for i in range(nu+1):
    u=i/nu;y=rows[0][0]+(rows[-1][0]-rows[0][0])*u
    for aa,bb in zip(rows,rows[1:]):
     if aa[0]>=y>=bb[0]:t=(y-aa[0])/(bb[0]-aa[0]);top=aa[1]+(bb[1]-aa[1])*t;bottom=aa[2]+(bb[2]-aa[2])*t;x=aa[3]+(bb[3]-aa[3])*t;break
    dy=y-CY
    if abs(dy)<.0432:
     edge=math.sqrt(.0432**2-dy**2)
     if kind=='brow':bottom=max(bottom,CZ+edge+.001)
     else:top=min(top,CZ-edge-.001)
    assert top>bottom,(name,i)
    for j in range(nv+1):q=j/nv;v.append(Vector((side*(x+.003*math.sin(math.pi*q)*math.sin(math.pi*u)),y,bottom+(top-bottom)*q)))
   h=len(v);v +=[p-Vector((side*.0045,0,0))for p in v];f=[];st=nv+1
   for i in range(nu):
    for j in range(nv):a=i*st+j;b=a+st;f.extend([(a,a+1,b+1,b),(h+b,h+b+1,h+a+1,h+a)])
   edge=list(range(st))+[i*st+nv for i in range(1,nu+1)]+[nu*st+j for j in range(nv-1,-1,-1)]+[i*st for i in range(nu-1,0,-1)]
   for a,b in zip(edge,edge[1:]+edge[:1]):f.append((a,b,b+h,a+h))
   tmp=new_obj(name+' temporary forming',v,f,list(dst.data.materials));stock(tmp);tmp.parent=dst.parent;bpy.context.view_layer.update();tmp.matrix_world=__import__('mathutils').Matrix.Identity(4)
   routes=[]
   if kind=='brow':
    routes.append(route(tmp,side,f'V31 passive cranial load bow {side}',(side*.120,-.450,1.701),(side*.141,-.520,1.775),(side*.116,-.506,1.752)))
    routes.append(route(tmp,side,f'V31 optic recessed receiving cup {side}',(side*.150,-.607,1.733),(side*.149,-.607,1.744)))
   else:
    routes.append(route(tmp,side,f'V31 passive cranial load bow {side}',(side*.118,-.437,1.692),(side*.146,-.510,1.651),(side*.114,-.486,1.660)))
    routes.append(route(tmp,side,f'V33 formed lower cheek receiver {side} 0',(side*.148,-.660,1.635),(side*.146,-.646,1.650)))
   swap(dst,tmp);changed.append(name);records.append({'name':name,'stock':stock(dst),'longitudinalYZXControls':rows,'nominalWallM':.0045,'routes':routes})
 return {'changedMeshes':changed,'added':{},'removed':[],'changedNodes':[],'construction':records,'preserved':'Lens/aperture, bill/contact/jaw, crown opening geometry/ownership, all transforms/materials/eras and other body/neck meshes exact','limits':['Peripheral passive support and plate stock are authored proposals; finite contacts and opening samples qualified separately.','No broad movement/manufacturing/likeness acceptance.','Intended receiving stock identities listed; strict same-owner crossings remain counted.']}
