"""Cheek-assembly01: shared curved receiving scaffold and descending armor.
Actual frozen breast-course02 input. Fourteen declared passive identities;
no optic/jaw/cranial-cover/bill or body modification. Finite head-owned solids.
"""
import bpy,bmesh,math
from mathutils import Vector
EYE=Vector((0,-.577800006,1.725484014))
BROWS=[f'V33 diagonal brow receiver {s} {i}' for s in(-1,1)for i in range(3)]
SHIELDS=[f'V38 optic cheek shield {s} {i}'for s in(-1,1)for i in range(3)]
WALLS=[f'V31 fixed temporal receiving wall {s}'for s in(-1,1)]
NAMES=WALLS+BROWS+SHIELDS
RAIL=[(-.644,1.766,.020),(-.610,1.802,.026),(-.550,1.829,.033),(-.470,1.835,.034),(-.398,1.825,.029),(-.355,1.801,.022)]
def ease(u):u=max(0,min(1,u));return u*u*(3-2*u)
def sample(rows,t):
 u=max(0,min(1,t))*(len(rows)-1);i=min(int(u),len(rows)-2);s=u-i;a,b,c,d=rows[max(0,i-1)],rows[i],rows[i+1],rows[min(i+2,len(rows)-1)]
 return [.5*(2*b[k]+(-a[k]+c[k])*s+(2*a[k]-5*b[k]+4*c[k]-d[k])*s*s+(-a[k]+3*b[k]-3*c[k]+d[k])*s*s*s)for k in range(len(b))]
def wall_x(y,z):
 # One explicit receiving/exterior coordinate family, not a nearest fitting pool.
 t=max(0,min(1,(y+.54)/.22));return .146-.035*t*t+.006*math.sin(math.pi*t)*math.exp(-((z-1.74)/.11)**2)
def reach(theta):
 c,s=math.cos(theta),math.sin(theta);limits=[.265]
 if c>1e-6:limits.append((-.319-EYE.y)/c)
 if s>1e-6:limits.append((1.824-EYE.z)/s)
 if s< -1e-6:limits.append((1.644-EYE.z)/s)
 return min(limits)
def world(side,r,theta,lift=0):
 y=EYE.y+r*math.cos(theta);z=EYE.z+r*math.sin(theta);return Vector((side*(wall_x(y,z)+lift),y,z))
def sheet(points,nu,nv,stock,side):
 half=len(points);v=points+[p-Vector((side*stock,0,0))for p in points];f=[];stride=nv+1
 for row in range(nu):
  for col in range(nv):a=row*stride+col;b=a+stride;f.extend([(a,a+1,b+1,b),(half+b,half+b+1,half+a+1,half+a)])
 edge=list(range(stride))+[i*stride+nv for i in range(1,nu+1)]+[nu*stride+j for j in range(nv-1,-1,-1)]+[i*stride for i in range(nu-1,0,-1)]
 for a,b in zip(edge,edge[1:]+edge[:1]):f.append((a,b,b+half,a+half))
 return v,f
def apply():
 bpy.context.view_layer.update();records=[]
 def replace(name,side,fn,stock,kind,nu=48,nv=16):
  o=bpy.data.objects[name];points=[fn(i/nu,j/nv)for i in range(nu+1)for j in range(nv+1)];assert all(.075<abs(p.x)<.23 and -.70<p.y<-.28 and 1.62<p.z<1.91 for p in points),(name,'head bounds')
  verts,faces=sheet(points,nu,nv,stock,side);m=bpy.data.meshes.new(name+' shared curved assembly mesh');inv=o.matrix_world.inverted();m.from_pydata([inv@p for p in verts],[],faces);m.update()
  for mat in o.data.materials:m.materials.append(mat)
  bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  vol=bm.calc_volume(signed=True);assert vol>0;bm.to_mesh(m);bm.free();o.data=m
  for f in m.polygons:f.use_smooth=True
  o['v38CheekAssembly']='Reconstructed curved temporal scaffold with staggered descending orbital armor; passive proposal'
  actual=[o.matrix_world@v.co for v in m.vertices];n=len(points);records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'materials':[m.name if m else None for m in o.data.materials],'constructionClass':o.get('constructionClass'),'kind':kind,'newVertices':len(m.vertices),'newFaces':len(m.polygons),'closedEdgeManifold':True,'positiveVolumeM3':vol,'axialStockM':stock,'actualStockMinMaxM':[min((actual[i]-actual[i+n]).length for i in range(n)),max((actual[i]-actual[i+n]).length for i in range(n))],'actualWorldBounds':[[min(p[k]for p in actual),max(p[k]for p in actual)]for k in range(3)]})
 for side in(-1,1):
  # Actual scaffold is a formed annular sector, leaving optic bore and lower jaw open.
  def backing(u,v):
   th=-1.15+2.62*v;r=.064+(reach(th)-.064)*u;return world(side,r,th)
  replace(f'V31 fixed temporal receiving wall {side}',side,backing,.004,'direct single-component receiving wall with open orbital/jaw boundary',48,64)
  for course,(lo,hi)in enumerate([(.64,1),(.31,.70),(0,.35)]):
   def rail(u,v):
    t=lo+(hi-lo)*u;y,z,width=sample(RAIL,t);a=sample(RAIL,max(0,t-.001));b=sample(RAIL,min(1,t+.001));dy,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dy,dz);y-=dz/length*(v-.5)*width*(1-.18*ease(u));z+=dy/length*(v-.5)*width*(1-.18*ease(u));x=wall_x(y,z)+.013+course*.006+.002*math.sin(math.pi*v)**2
    return Vector((side*x,y,z))
   replace(f'V33 diagonal brow receiver {side} {course}',side,rail,.0045,'three separately rigid rearward orbital rail laps')
  for course,(first,last,width)in enumerate([(1.02,.43,.38),(.15,-.28,.35),(-.77,-.51,.28)]):
   def cheek(u,v):
    # Curved tapering YZ courses, varied spans; finite supporting returns use the same wall.
    theta=first+(last-first)*ease(u)+(v-.5)*width*(.76+.24*math.sin(math.pi*u));r=.073+(.225-.073)*u
    r=min(r,reach(theta)-.007);lift=.012+course*.006+.002*math.sin(math.pi*v)**2
    # Integral narrow endlands descend to nominal1.5mm inner clearance above scaffold.
    root=(1-ease(u/.12)) if u<.12 else ease((u-.88)/.12)if u>.88 else 0
    lift=lift*(1-root)+(.0015+.0045)*root
    return world(side,r,theta,lift)
   replace(f'V38 optic cheek shield {side} {course}',side,cheek,.0045,'short curved diagonal temple/jaw-root plate with integral wall-facing endlands')
 return {'changedMeshes':NAMES,'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'attachmentAndEraMap':records,'construction':'Direct continuous annular-sector scaffold and shaped plates share explicit curved wall coordinate family. No Boolean fragments or all-head ray projection. Narrow integral receiving returns approach same scaffold with nominal1.5mm inner gap.','rigidVsFlexible':'All14 finite rigid head-owned passive parts; independent jaw/cover untouched.','confirmation':'ActualJuly HEAD ONLY swept brow/descending layered cheek, Master03/Maker-clean wholebird crosscheck.','reconstruction':'Exact field, hidden receiving lands/stock and plate layout authored; not art metrology, fastener/load acceptance.','protected':'Opticcup/floor/lip/aperture/centers,jaw/bowl397/socket/axis,billtriangles/extrema,crown/cover/neck/body/pivots/materials exact.','limits':['Common field and positive finite stock are not full triangle/sweep clearance; surface screen separate.','Wall replaces unapproved broad slab; formal connection to retained frame is inferred proposal, not proved load path.','Nominal endland gap is actual paired axial construction, not whole-foot distance/engineering certificate.']}
