"""One supported anterior/side oval backing and directional rigid plate assembly."""
import bpy,bmesh,math,json,bisect
from mathutils import Vector
from mathutils.bvhtree import BVHTree
STOCK={}
LINER='V30 continuous tapered breast liner'
COUNTS=[5,6,7,6,5,4]
PLATES=[f'V34 formed breast course {r} plate {c}'for r,n in enumerate(COUNTS,1)for c in range(1,n+1)]
# Authored model controls, not measurements claimed from raster references.
SECTIONS=[(.685,.095,.140),(.725,.170,.230),(.775,.220,.290),(.85,.247,.335),(.95,.258,.360),(1.05,.258,.355),(1.145,.247,.337),(1.205,.231,.300),(1.248,.210,.248)]
CENTER_Y=-.08;ANGLE=1.09

def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
def component(z,k):
 zs=[p[0]for p in SECTIONS];i=max(0,min(len(zs)-2,bisect.bisect_right(zs,z)-1));h=zs[i+1]-zs[i];t=max(0,min(1,(z-zs[i])/h));v=[p[k]for p in SECTIONS];d=[(v[j+1]-v[j])/(zs[j+1]-zs[j])for j in range(len(zs)-1)]
 def m(j):
  if j==0:return d[0]
  if j==len(zs)-1:return d[-1]
  return 0 if d[j-1]*d[j]<=0 else 2*d[j-1]*d[j]/(d[j-1]+d[j])
 return(2*t**3-3*t*t+1)*v[i]+(t**3-2*t*t+t)*h*m(i)+(-2*t**3+3*t*t)*v[i+1]+(t**3-t*t)*h*m(i+1)
def point(z,a):return Vector((component(z,1)*math.sin(a),CENTER_Y-component(z,2)*math.cos(a),z))
def normal(z,a):
 dz=point(z+.0001,a)-point(z-.0001,a);da=point(z,a+.0001)-point(z,a-.0001);n=dz.cross(da).normalized()
 if n.dot(Vector((math.sin(a),-math.cos(a),0)))<0:n=-n
 return n

def solid(surface,rows,cols,wall):
 outer=[surface(i/rows,j/cols)for i in range(rows+1)for j in range(cols+1)];inner=[];N=len(outer);f=[]
 for i in range(rows+1):
  for j in range(cols+1):
   k=i*(cols+1)+j;du=outer[min(rows,i+1)*(cols+1)+j]-outer[max(0,i-1)*(cols+1)+j];dv=outer[i*(cols+1)+min(cols,j+1)]-outer[i*(cols+1)+max(0,j-1)];n=du.cross(dv).normalized();p=outer[k]
   if n.dot(Vector((p.x,p.y-CENTER_Y,0)))<0:n=-n
   assert n.length>.9;inner.append(p-n*wall)
 for i in range(rows):
  for j in range(cols):
   a=i*(cols+1)+j;b=a+1;c=b+cols+1;d=a+cols+1;f.extend([(a,b,c,d),(N+d,N+c,N+b,N+a)])
 edge=[j for j in range(cols+1)]+[i*(cols+1)+cols for i in range(1,rows+1)]+[rows*(cols+1)+j for j in range(cols-1,-1,-1)]+[i*(cols+1)for i in range(rows-1,0,-1)]
 f.extend((a,N+a,N+b,b)for a,b in zip(edge,edge[1:]+edge[:1]));return outer+inner,f

def install(o,v,f,label):
 old=o.data;mesh=bpy.data.meshes.new(o.name+' '+label);inv=o.matrix_world.inverted();mesh.from_pydata([inv@p for p in v],[],f);mesh.update()
 for m in old.materials:mesh.materials.append(m)
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=2e-7);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));nonmanifold=sum(not e.is_manifold for e in bm.edges)
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 vol=bm.calc_volume(signed=True);STOCK[o.name]={'nonManifoldEdges':nonmanifold,'signedVolumeM3':vol,'status':'HOLD invalid boundary' if nonmanifold or vol<=0 else 'closed positive; self/fit unproven'};print('STOCK',o.name,STOCK[o.name],flush=True);bm.to_mesh(mesh);bm.free();o.data=mesh
 for p in mesh.polygons:p.use_smooth=True
 return vol

def tree(o):
 o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(t.vertices)for t in o.data.loop_triangles],all_triangles=True,epsilon=0)
def bounds(row,q):
 # Directional shoulder-to-hip sweeps, shared boundaries across course identities.
 edges=[1.246-.018*abs(q),1.15-.036*abs(q)+.010*q,1.052-.033*abs(q)-.009*math.sin(math.pi*q),.956-.026*abs(q)+.009*math.sin(math.pi*q),.86-.017*abs(q)-.009*math.sin(math.pi*q),.767-.011*abs(q)+.008*q,.694+.023*abs(q)]
 return edges[row-1]+(.015 if row>1 else 0),edges[row]-(.005 if row<6 else 0)
def annotation(o,role):
 old={k:json.loads(json.dumps(v,default=lambda x:list(x)))for k,v in o.items()if k in('constructionDescription','geometryStatus','wallM','railEndpointWorld','courseTopM','courseBottomM','courseIndex','lateralSpanRadians','panelKind','authoringRole')or k.endswith('Revision')}
 o['historicalConstructionBeforeTorsoCoherent01']=json.dumps(old,separators=(',',':'));o['constructionDescription']=role;o['geometryStatus']='Torso-coherent01 construction proposal; finite interfaces/owner acceptance unresolved';o['torsoCoherentRevision']='torso-coherent01'

def receiving_channel(points):
 w=.025;d=.016;wall=.004;cross=[(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(w/2-wall,d/2),(w/2-wall,-d/2+wall),(-w/2+wall,-d/2+wall),(-w/2+wall,d/2),(-w/2,d/2)];v=[];f=[]
 axis=(points[-1]-points[0]).normalized();a=Vector((1,0,0));a=(a-axis*a.dot(axis)).normalized();b=axis.cross(a).normalized()
 for p in points:v.extend(p+a*x+b*y for x,y in cross)
 for i in range(len(points)-1):
  for j in range(8):a=i*8+j;b=i*8+(j+1)%8;f.append((a,b,b+8,a+8))
 f.extend([tuple(reversed(range(8))),tuple(range((len(points)-1)*8,len(points)*8))]);return v,f

def measure(o):
 v=[o.matrix_world@p.co for p in o.data.vertices];return {'boundsM':[[min(p[i]for p in v),max(p[i]for p in v)]for i in range(3)],'sections':[{'z':z,'samples':len(p),'widthM':max(q.x for q in p)-min(q.x for q in p),'frontY':min(q.y for q in p)}for z in(.725,.775,.85,.95,1.05,1.145)if(p:=[q for q in v if abs(q.z-z)<.009])]}

from mathutils.geometry import tessellate_polygon
from collections import Counter
OLD=[f'V34 formed breast course {row} plate {col}'for row,n in enumerate(COUNTS[:3],1)for col in range(1,n+1)]
# Individually authored(q,z) outlines. Not measured raster dimensions; no repeated column/coursegrid.
SHAPES=[
 ('central left', [(-.64,1.218),(-.54,1.221),(-.40,1.150),(-.42,1.058),(-.55,.984),(-.69,1.058),(-.77,1.146)]),
 ('central left inner',[(-.25,1.228),(-.15,1.225),(-.01,1.147),(-.04,1.054),(-.19,.971),(-.34,1.052),(-.39,1.143)]),
 ('central right inner',[(.16,1.211),(.25,1.216),(.39,1.134),(.36,1.048),(.23,.958),(.08,1.043),(.02,1.129)]),
 ('central right',[(.56,1.198),(.65,1.205),(.77,1.123),(.74,1.043),(.62,.968),(.47,1.045),(.42,1.130)]),
 ('upper left transition',[(-.50,1.244),(-.43,1.241),(-.29,1.195),(-.30,1.154),(-.39,1.116),(-.55,1.169),(-.63,1.207)]),
 ('upper right transition',[(.36,1.238),(.43,1.240),(.57,1.200),(.54,1.152),(.45,1.104),(.30,1.162),(.25,1.208)]),
 ('left flank',[(-.91,1.186),(-.84,1.180),(-.71,1.114),(-.73,1.022),(-.83,.933),(-.97,1.031),(-.99,1.123)]),
 ('right flank',[(.83,1.174),(.89,1.177),(.99,1.112),(.98,1.019),(.91,.945),(.78,1.018),(.70,1.110)])]
def apply():
 bpy.context.view_layer.update();template=bpy.data.objects[OLD[2]];btree=tree(bpy.data.objects[LINER]);added=[];records=[]
 for label,pairs in SHAPES:
  poly=[Vector((q,z,0))for q,z in pairs];tris=tessellate_polygon([poly]);points=[];ids={};faces=[];steps=14
  def vid(p):
   key=(round(p.x,6),round(p.y,6))
   if key not in ids:ids[key]=len(points);points.append(p)
   return ids[key]
  for tri in tris:
   aa,bb,cc=[poly[k]for k in tri];grid={}
   for i in range(steps+1):
    for j in range(steps-i+1):grid[i,j]=vid(aa+(bb-aa)*(i/steps)+(cc-aa)*(j/steps))
   for i in range(steps):
    for j in range(steps-i):
     faces.append((grid[i,j],grid[i+1,j],grid[i,j+1]))
     if i+j<steps-1:faces.append((grid[i+1,j],grid[i+1,j+1],grid[i,j+1]))
  top=max(p.y for p in poly);bottom=min(p.y for p in poly);outer=[];inner=[];rootDistances=[];rootTris=[]
  for p in points:
   u=(top-p.y)/(top-bottom);a=ANGLE*p.x;base=point(p.y,a);n=normal(p.y,a);offset=.004+.009*ease((u-.12)/.65);outer.append(base+n*offset)
   if u<=.12:
    seat=btree.find_nearest(base);inner.append(seat[0]);rootDistances.append(seat[3]);rootTris.append(seat[2])
   else:inner.append(base+n*(offset-.0035))
  N=len(points);walls=[];counts=Counter(tuple(sorted((f[j],f[(j+1)%3])))for f in faces for j in range(3))
  for f in faces:
   for j in range(3):
    x,y=f[j],f[(j+1)%3]
    if counts[tuple(sorted((x,y)))]==1:walls.append((x,y,N+y,N+x))
  allfaces=faces+[tuple(N+i for i in reversed(f))for f in faces]+walls;name='V38 breast hanging shield '+label;o=template.copy();o.name=name;bpy.context.scene.collection.objects.link(o)
  for k in list(o.keys()):
   if k not in ['region','surfaceRole','exteriorEras','constructionClass','constructionOwner','articulatesAcrossJoint','proposal']:del o[k]
  bpy.context.view_layer.update();vol=install(o,outer+inner,allfaces,'individualoutline3.5mmfreewall/narrowintegralroot')
  for i,f in enumerate(o.data.polygons):f.use_smooth=i<2*len(faces)
  o['constructionDescription']='Individually authored upper breast hanging shield: narrow root, broad curved face and finite pointed taper. No shared rectangular course grid; explicit ownoutline triangulation/closed stock with flat sideedges. Root inner vertices sample actual retained backing, freewall3.5mm, maximum13mm source field offset. Seating/lap/physical fit still qualified.';o['breastShieldsRevision']='breast-shields01';o['wallM']=.0035;added.append(name);records.append({'name':name,'parent':o.parent.name,'exteriorEras':o.get('exteriorEras'),'outlineParameterQZ':pairs,'topology':'Uniform triangulation subdivision of individual outline; not triangleclipping backing or newtextureUV','stockCheck':STOCK[name],'freeWallM':.0035,'rootInnerBackingVertexSamples':len(rootDistances),'rootBackingDistanceM':{'min':min(rootDistances),'max':max(rootDistances)},'rootActualBackingTriangles':sorted(set(rootTris)),'supportQualification':'Rootvertices correspondence only; triangulatedface seating/loadpath and real movingclearance unproven.'})
 for name in OLD:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
 return {'status':'One8shield uppercluster visual study; STOCK HOLD, awaiting visualgate','changedMeshes':[],'addedMeshes':added,'removedMeshes':OLD,'changedNodes':[],'construction':records,'referenceAuthority':'Actual Master03 enlarged breastdetail SHA73cab642b1fd598a2e316052d7436f1102c4feab58b140456e269aad37d5e91c; dimensions/tips/hiddenattachment choices authored proposals. Julyhead not bodyauthority.','mechanism':'4long pointed hanging shields,2short staggered uppertransitions,2narrowcurvedflanks replace18upper tiles. Lower15 identities and body supportingfield remain exact. Ownoutlined topology with rigid stock and integral narrowed root; no polished finish or regular grid propagation.','protected':'Allsurviving body liner/frame/receiver/neck/head/wing/legs/joints/hierarchy/material/era exactly preserved by source builder checks; newplate edge contours can vary locally.','limits':['Closedpositive manifold is not support/seating/self/neighbor/fullmotion acceptance.','Rootvertex samples not exact finiteface area proof.','Nominal3.5mm freewall does not describe root gauge exactly.','All silhouettes/outlinechoices are proposals awaiting visual/owneracceptance.','No app,production,textureUV or finish changes.']}
