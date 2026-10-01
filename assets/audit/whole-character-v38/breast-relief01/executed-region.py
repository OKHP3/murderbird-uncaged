"""One supported anterior/side oval backing and directional rigid plate assembly."""
import bpy,bmesh,math,json,bisect
from mathutils import Vector
from mathutils.bvhtree import BVHTree
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
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),o.name
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 vol=bm.calc_volume(signed=True);assert vol>0;bm.to_mesh(mesh);bm.free();o.data=mesh
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

TARGETS=[f'V34 formed breast course 3 plate {c}'for c in(3,4,5)]
def apply():
 bpy.context.view_layer.update();backing=bpy.data.objects[LINER];btree=tree(backing);records=[]
 for col,name in zip((2,3,4),TARGETS):
  o=bpy.data.objects[name];center=-1+(col+.5)*2/7;step=2/7;rows,cols=28,16;outer=[];inner=[];rootGaps=[];rootTris=[]
  for i in range(rows+1):
   u=i/rows
   for j in range(cols+1):
    v=j/cols;q=center+step*.5*.95*(2*v-1);top,bottom=bounds(3,q)
    # Restrained hard oblique termination, not a puffed-face or uniform scallop.
    bottom+=.009*(v-.5)*(1 if col%2 else -1)+.004*(v-.5)**2
    z=top+(bottom-top)*u;a=ANGLE*q;base=point(z,a);n=normal(z,a)
    # Broad integral root land reaches the actual retained backing triangles.
    near=btree.find_nearest(base);seat=near[0];rootGaps.append((base-seat).length)if i<=4 else None
    if i<=4:rootTris.append(near[2])
    free=ease((u-.16)/.65);stand=.004+.009*free
    outer.append(base+n*stand)
    if i<=4:inner.append(seat)
    else:inner.append(base+n*(stand-.004))
  N=len(outer);faces=[]
  for i in range(rows):
   for j in range(cols):
    a=i*(cols+1)+j;b=a+1;c=b+cols+1;d=a+cols+1;faces.extend([(a,b,c,d),(N+d,N+c,N+b,N+a)])
  loop=list(range(cols+1))+[i*(cols+1)+cols for i in range(1,rows+1)]+[rows*(cols+1)+j for j in range(cols-1,-1,-1)]+[i*(cols+1)for i in range(rows-1,0,-1)]
  faces.extend((a,N+a,N+b,b)for a,b in zip(loop,loop[1:]+loop[:1]));vol=install(o,outer+inner,faces,'integral seatedroot/hard4mmfreewall relief prototype')
  for i,f in enumerate(o.data.polygons):f.use_smooth=i<2*rows*cols
  original=o.get('constructionDescription','unknown');o['previousBreastReliefConstruction']=original;o['constructionDescription']='Rigid breast relief prototype: broad integral rootland inner vertices sample actual retained backing triangles; outer root4mm grows to13mm source maximum freeedge stand-off.4mm ordered freewall with hard side/cap edges, restrained oblique termination. Same breastplate owner; actual finite rootfaces/laps still qualified.';o['breastReliefRevision']='breast-relief01';o['geometryStatus']='Threeplate construction-depth diagnostic, not fullbreast or acceptedstyle.'
  records.append({'name':name,'parent':o.parent.name,'exteriorEras':o.get('exteriorEras'),'rootLandRows':[0,4],'rootInnerSamples':85,'actualBackingObject':LINER,'actualRootBackingTriangleIndices':sorted(set(rootTris)),'analyticBaseToActualBackingDistanceM':{'min':min(rootGaps),'max':max(rootGaps)},'freeWallM':.004,'rootOuterStandOffM':.004,'freeOuterStandOffMaximumM':.013,'closedPositiveSignedVolumeM3':vol,'rootQualification':'Actual sampled backing triangles used, but quadfaces interpolate across triangles; finite seating/contact/load acceptance unresolved. No corner-only physicalfit claim.','lapQualification':'Above course2 overlies prototype root; prototype freeedge overlies untouched course4 roots by declared layer order. Real finite collision/clearance not yet screened.'})
 return {'status':'First threeplate breast relief prototype awaiting root visualgate','changedMeshes':TARGETS,'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'construction':records,'mechanism':'Independent closed curved finite solids with broad integral lowroot,4mmwall and raised hardfree edges. Same source-body field/max13mm exterior; no new general panelgrid. Geometry vs lighting compared with identical neutral castshadow rendering.','protected':'Allsource frame/liner/receivers/joints/neck/head/limbs/remaining30breastplates/pivots/hierarchy/era/materials exact; onlythreecentral course3 plate geometries and scoped construction annotations change.','limits':['Threepart local diagnostic, not fullbodylikeness or materialfinish.','Parameter grid not textureUV.','Rootvertex correspondence is not finitearea loadproof.','Closedpositive stock is not self/neighbor/sweptmotion acceptance.','No silhouette expansion beyond sourceanalytic maximum stand-off intended; actual local edge envelope differs.']}
