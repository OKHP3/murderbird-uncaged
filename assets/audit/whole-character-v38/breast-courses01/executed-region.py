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

def edge_height(k,q):
 edges=[1.246-.018*abs(q),1.152-.065*abs(q)+.020*math.sin(1.7*math.pi*q+.30),1.052-.062*abs(q)+.024*math.sin(1.35*math.pi*q-.20),.952-.047*abs(q)+.022*math.sin(1.8*math.pi*q+.15),.851-.030*abs(q)+.019*math.sin(1.55*math.pi*q-.50),.759-.008*abs(q)+.012*math.sin(1.4*math.pi*q),.694+.023*abs(q)]
 return edges[k]
def apply():
 bpy.context.view_layer.update();records=[]
 for row,count in enumerate(COUNTS,1):
  for col in range(count):
   o=bpy.data.objects[f'V34 formed breast course {row} plate {col+1}'];center=-1+(col+.5)*2/count;step=2/count;original=o.get('constructionDescription','unknown')
   def surface(u,v):
    # A monotonic closed parameter patch on the unchanged analytic body envelope.
    # Blunt swept ends; individual lateral taper varies by plate instead of repeated scallops.
    corner=(.075*(1-ease(u/.075)) if u<.075 else 0)+(.09*ease((u-.90)/.10) if u>.90 else 0)
    taper=(.06+.02*((row+col)%3))*u
    side=step*.5*.968*(1-corner-taper)
    sweep=.025*math.sin(math.pi*u)*(1 if center>0 else -1)*(1 if row%2 else .65)
    q=center+side*(2*v-1)+sweep
    top=edge_height(row-1,q)+(.012 if row>1 else 0);bottom=edge_height(row,q)-(.007 if row<6 else 0)
    z=top+(bottom-top)*u;a=ANGLE*q;offset=.005+.008*ease(u)
    return point(z,a)+normal(z,a)*offset
   # Corresponding inner face uses the analytic backing normal, never noisy inset signs.
   rows,cols=28,16;outer=[surface(i/rows,j/cols)for i in range(rows+1)for j in range(cols+1)];inner=[]
   for p in outer:
    a=math.atan2(p.x/component(p.z,1),-(p.y-CENTER_Y)/component(p.z,2));inner.append(p-normal(p.z,a)*.0035)
   N=len(outer);faces=[]
   for i in range(rows):
    for j in range(cols):
     a=i*(cols+1)+j;b=a+1;c=b+cols+1;d=a+cols+1;faces.extend([(a,b,c,d),(N+d,N+c,N+b,N+a)])
   boundary=list(range(cols+1))+[i*(cols+1)+cols for i in range(1,rows+1)]+[rows*(cols+1)+j for j in range(cols-1,-1,-1)]+[i*(cols+1)for i in range(rows-1,0,-1)]
   faces.extend((a,N+a,N+b,b)for a,b in zip(boundary,boundary[1:]+boundary[:1]));vol=install(o,outer+inner,faces,'new breast-courses closed analytic-normal3.5mm stock')
   o['previousBreastCourseConstruction']=original;o['constructionDescription']='New staggered swept breast/flank plate on unchanged supporting oval field. Varied shared oblique boundaries, longer upper transitions and wider lower access identities. Monotonic patch with corresponding3.5mm analytic-normal inner face and explicit closed edges; actual finite seating/clearance qualified separately.';o['breastCoursesRevision']='breast-courses01';o['geometryStatus']='Breast-courses01 proposal; visual and finite gate pending';o['courseTopM']=max(p.z for p in outer);o['courseBottomM']=min(p.z for p in outer)
   records.append({'name':o.name,'parent':o.parent.name,'exteriorEras':o.get('exteriorEras'),'course':row,'panel':col+1,'wallM':.0035,'closedPositiveSignedVolumeM3':vol,'envelopeBasis':'source torso-coherent01 analytic field; backing exact','supportQualification':'Existing liner/receiver route preserved. Root stand-off5mm inherited; new stock seating not certified.'})
 return {'status':'First breast-courses01 visual proposal; awaiting rootgate before finite','changedMeshes':PLATES,'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'construction':records,'sourceBasis':'jaw-stock01 native507a58f5670677276f8f06d3769deb9eb6cbd178a20f20a2993986d02374f63a','mechanism':'33 independent plate identities retain5/6/7/6/5/4 rhythm, curved staggered shared height boundaries with varied lateral taper and directional oblique sweep. Same supporting analytic oval field and5→13mm root/free stand-off. No backing/frame/joint/owner/material changes.','limits':['Reference authority Master03 body; authored boundaries are proposals, not extracted raster dimensions.','Parameter grid is not a newtextureUV or finish pipeline.','Liner/frame/pivots exact; plate edge coverage and derived exterior can differ locally.','Closed positive stock is not actual collision/support/engineering or ownerlikeness acceptance.','No app/runtime changes or production promotion.']}
