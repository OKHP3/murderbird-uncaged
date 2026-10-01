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

NEW_COUNTS=[4,5,5,5,5]
PARTITIONS=[[-1,-.58,-.05,.46,1],[-1,-.82,-.42,.06,.64,1],[-1,-.65,-.19,.31,.79,1],[-1,-.83,-.37,.16,.67,1],[-1,-.70,-.26,.28,.82,1]]
def boundary(k,q):
 return [1.246-.018*abs(q),1.118-.072*abs(q)+.019*math.sin(1.3*math.pi*q),1.008-.048*abs(q)+.022*math.sin(1.7*math.pi*q+.35),.900-.030*abs(q)+.022*math.sin(1.35*math.pi*q-.60),.793-.008*abs(q)+.015*math.sin(1.7*math.pi*q),.694+.023*abs(q)][k]
def apply():
 bpy.context.view_layer.update();template=bpy.data.objects[PLATES[2]];new=[];records=[]
 for row,count in enumerate(NEW_COUNTS):
  bins=PARTITIONS[row]
  for col in range(count):
   lo,hi=bins[col:col+2];center=(lo+hi)/2;w=hi-lo
   def surface(u,v):
    # Swept side edges and a hard clipped free end are directly authored, not beveled old stock.
    corner=.055*(1-u/.065) if u<.065 else(.075*(u-.93)/.07 if u>.93 else 0)
    left=lo+w*(.018+corner);right=hi-w*(.018+corner)
    sweep=(.034 if center>0 else -.025)*math.sin(math.pi*u)*(1 if row%2 else -.55)
    q=left+(right-left)*v+sweep
    top=boundary(row,q)+(.013 if row else 0);bottom=boundary(row+1,q)-(.008 if row<4 else 0)
    # Different lower edge obliquity, not circumferential repeated rings or pillow bulges.
    slant=(.018 if (row+col)%2 else -.016)*(v-.5)*math.sin(math.pi*u*.5)
    z=top+(bottom-top)*u+slant;a=ANGLE*q
    return point(z,a)+normal(z,a)*(.005+.008*ease(u))
   rows,cols=28,16;outer=[surface(i/rows,j/cols)for i in range(rows+1)for j in range(cols+1)];inner=[]
   for p in outer:
    ang=math.atan2(p.x/component(p.z,1),-(p.y-CENTER_Y)/component(p.z,2));inner.append(p-normal(p.z,ang)*.0035)
   N=len(outer);faces=[]
   for i in range(rows):
    for j in range(cols):
     x=i*(cols+1)+j;y=x+1;z=y+cols+1;t=x+cols+1;faces.extend([(x,y,z,t),(N+t,N+z,N+y,N+x)])
   loop=list(range(cols+1))+[i*(cols+1)+cols for i in range(1,rows+1)]+[rows*(cols+1)+j for j in range(cols-1,-1,-1)]+[i*(cols+1)for i in range(rows-1,0,-1)]
   faces.extend((x,N+x,N+y,y)for x,y in zip(loop,loop[1:]+loop[:1]));name=f'V38 breast-courses hard plate course {row+1} panel {col+1}';o=template.copy();o.name=name;bpy.context.scene.collection.objects.link(o)
   for k in list(o.keys()):
    if k not in ['region','surfaceRole','exteriorEras','constructionClass','constructionOwner','articulatesAcrossJoint','proposal']:del o[k]
   bpy.context.view_layer.update();vol=install(o,outer+inner,faces,'staggered hard closed plate3.5mm stock')
   for i,p in enumerate(o.data.polygons):p.use_smooth=i<2*rows*cols
   o['constructionDescription']='New independent broad directional breast/flank access plate, compact source-body field, explicit closed3.5mm wall. Staggered asymmetric column partitions and varying swept/course boundaries; flat stock edges, no bevel/rolled allface smoothing. Actual support/finite fit remains unaccepted.';o['breastCoursesRevision']='breast-courses01-attempt02';new.append(name);records.append({'name':name,'parent':o.parent.name,'exteriorEras':o.get('exteriorEras'),'course':row+1,'columnPartition':[lo,hi],'wallM':.0035,'closedPositiveSignedVolumeM3':vol,'supportQualification':'Source liner/frame/receiver exact; inherited5mm root stand-off, no new receiver engagement claimed.'})
 for name in PLATES:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
 return {'status':'Final24plate5course breast layout proposal; await visualgate','changedMeshes':[],'removedMeshes':PLATES,'addedMeshes':new,'changedNodes':[],'construction':records,'mechanism':'24 broad hard directional plates replace33gridskins:4upper longitudinal transitions +5/5/5/5 broadcentral/narrowflank access plates; unequal column partitions and sloping curved course edges, varied hard free edges. Sourcebody analytic supporting field retained.','protected':'Backing/receivers/frame and allsurviving geometry, joints/hierarchy/transforms/era/material records exact.','limits':['Authored boundaries not raster measurements.','Parameter grid not newtextureUV/finish.','Newplate edge silhouette differs; supporting body envelope field is source exact.','Closedpositive stock not finiteclearance/rootseating/physicalassembly/owneracceptance.','No app/production changes.']}
