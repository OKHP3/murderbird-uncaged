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
 o['constructionDescription']='Reconstructed fixed head-owned directional facial wall/compact optic seat; authored finite stock, assembly fit not certified.';o['v38FacialShell01']='Proposal; lens centre/diameter and all unrelated geometry retained'
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
 for lo,hi in(sectors or[(0,2*math.pi)]):
  closed=abs(hi-lo-2*math.pi)<1e-6;n=96 if closed else32;count=n if closed else n+1;base=len(v)
  for x,rad in[(x0,inner),(x0,outer),(x1,outer),(x1,inner)]:
   for i in range(count):a=lo+(hi-lo)*i/n;v.append((side*x,CY+rad*math.cos(a),CZ+rad*math.sin(a)))
  for r in range(4):
   for i in range(n):a=base+r*count+i;b=base+r*count+(i+1)%count;c=base+((r+1)%4)*count+(i+1)%count;d=base+((r+1)%4)*count+i;f.append((a,b,c,d))
  if not closed:f.extend([tuple(base+r*count for r in range(4)),tuple(base+r*count+n for r in reversed(range(4)))])
 return replace(o,v,f)
def apply(second=False):
 bpy.context.view_layer.update();changed=[];records=[]
 for n in REMOVED:bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
 for side in[-1,1]:
  o,s=wall(side);changed.append(o.name);records.append({'name':o.name,'role':'One tapered temple/brow/cheek wall with lens-sized cutout and axial finite thickness','outlineNativeYZX':OUTLINE,'stock':s})
  for name,ri,ro,x0,x1,sec in[(f'V31 optic recessed receiving cup {side}',.0388,.0445,.1345,.1505,None),(f'V31 passive optic cavity floor {side}',0,.0400,.11832,.1218,None),(f'V33 recessed optic retaining lip {side}',.0395,.0422,.1490,.1520,[(math.radians(12),math.radians(160)),(math.radians(195),math.radians(337))])]:
   s=ring(name,side,ri,ro,x0,x1,sec);changed.append(name);records.append({'name':name,'stock':s,'radiiM':[ri,ro],'nativeAbsX':[x0,x1],'role':'Passive compact optic recess/retention; actual lens unchanged'})
 return {'changedMeshes':changed,'removed':REMOVED,'added':{},'changedNodes':[],'construction':records,'opticCentreNativeYZ':[CY,CZ],'preserved':'All node transforms/owners, lens aperture/cognition material/era, bill/contact, jaw/root/socket, crown and opening cranial shell, neck/body exact','limits':['Topology/positive volume not self/neighbor clearance acceptance.','Fixed wall and optic stock form one authored side-volume arrangement; true finite receiver contact still requires targeted checking.','Two segmented lip solids remain one same-owner identity; not a continuous outer bezel.','No head-to-opening-cranial-cover rigid bridge.','July head-only controls visible form; hidden support dimensions are proposals.']}
