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
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));nonmanifold=sum(not e.is_manifold for e in bm.edges)
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
 shapes=[]
 # Four long pointed shields remain primary, with individually staggered height/ends.
 for name,p in SHAPES[:4]:shapes.append((name,p,.013))
 # Compact shorter interstitial upper shields cover the roots rather than broad diamonds.
 for k,(q,top,bottom)in enumerate([(-.80,1.231,1.142),(-.40,1.244,1.147),(.01,1.240,1.151),(.42,1.237,1.136),(.82,1.211,1.113)]):
  shapes.append((f'upper stagger {k+1}',[(q-.035,top),(q+.035,top-.002),(min(.99,q+.16),top-.032),(q+.105,bottom+.029),(q+.025,bottom),(q-.12,bottom+.029),(max(-.99,q-.16),top-.032)],.013))
 # Narrow side shields, distinct from central broad faces, preserve compact source contour.
 shapes.extend([('left curved flank',[(-.92,1.186),(-.855,1.180),(-.78,1.114),(-.79,1.019),(-.86,.933),(-.97,1.031),(-.99,1.123)],.010),('right curved flank',[(.855,1.174),(.91,1.177),(.99,1.112),(.98,1.019),(.91,.945),(.80,1.018),(.78,1.110)],.010)])
 # Lower small pointed polygons lie UNDER long free ends, breaking open-root gaps.
 for k,(q,top,bottom)in enumerate([(-.395,1.148,.965),(.025,1.139,.944),(.42,1.128,.940)]):
  shapes.append((f'lower interstitial {k+1}',[(q-.035,top),(q+.035,top+.002),(q+.14,top-.058),(q+.13,bottom+.04),(q+.015,bottom),(q-.14,bottom+.039),(q-.15,top-.06)],.0085))
 for label,pairs,freeLevel in shapes:
  polygon=[Vector((q,z))for q,z in pairs];centroid=sum(polygon,Vector((0,0)))/len(polygon);boundary=[]
  for x,y in zip(polygon,polygon[1:]+polygon[:1]):
   for j in range(6):boundary.append(x.lerp(y,j/6))
  C=len(boundary);rings=12;params=[centroid]+[centroid.lerp(p,i/rings)for i in range(1,rings+1)for p in boundary];faces=[]
  faces.extend((0,1+j,1+(j+1)%C)for j in range(C))
  for i in range(rings-1):
   start=1+i*C;nxt=start+C
   faces.extend((start+j,nxt+j,nxt+(j+1)%C,start+(j+1)%C)for j in range(C))
  top=max(p.y for p in polygon);bottom=min(p.y for p in polygon);outer=[];inner=[];rootDistances=[]
  for p in params:
   u=(top-p.y)/(top-bottom);base=point(p.y,ANGLE*p.x);n=normal(p.y,ANGLE*p.x);offset=.004+(freeLevel-.004)*ease((u-.10)/.55);outer.append(base+n*offset)
   if u<=.10:
    seat=btree.find_nearest(base);inner.append(seat[0]);rootDistances.append(seat[3])
   else:inner.append(base+n*(offset-.0035))
  N=len(params);edge=1+(rings-1)*C;allfaces=faces+[tuple(N+k for k in reversed(f))for f in faces]+[(edge+j,N+edge+j,N+edge+(j+1)%C,edge+(j+1)%C)for j in range(C)];name='V38 breast layered shield '+label;o=template.copy();o.name=name;bpy.context.scene.collection.objects.link(o)
  for k in list(o.keys()):
   if k not in ['region','surfaceRole','exteriorEras','constructionClass','constructionOwner','articulatesAcrossJoint','proposal']:del o[k]
  bpy.context.view_layer.update();vol=install(o,outer+inner,allfaces,'direct indexedradialrings3.5mmstock')
  for i,f in enumerate(o.data.polygons):f.use_smooth=i<2*len(faces)
  o['constructionDescription']='Reference-led upper hanging shield or compact interstitial plate. Own explicit outline; deterministic indexed centroid/radialrings and finite paired freewall, no independent trianglecoordinate weld. Narrow integral root samples retained backing; long primary ends over lowerinterstitial and below compact upper rootcovers. Actual stock/receiver/lap fit qualified separately.';o['breastShieldsRevision']='breast-shields01-attempt02';o['wallM']=.0035;added.append(name);records.append({'name':name,'parent':o.parent.name,'exteriorEras':o.get('exteriorEras'),'outlineParameterQZ':pairs,'stockCheck':STOCK[name],'freeStandOffM':freeLevel,'rootStandOffM':.004,'freeWallM':.0035,'rootInnerActualBackingSamples':len(rootDistances),'rootDistanceM':{'min':min(rootDistances),'max':max(rootDistances)},'qualification':'Closedstock not actualseat/self/lap/motionproof; lower interstitial nominallayer order remains unproven byfinite surfaces.'})
 for name in OLD:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
 return {'status':'Final14layered shield uppercluster; visual/stockfit HOLDuntilreview','changedMeshes':[],'addedMeshes':added,'removedMeshes':OLD,'changedNodes':[],'construction':records,'referenceAuthority':'Master03 actual enlarged breastdetail SHA73cab642b1fd598a2e316052d7436f1102c4feab58b140456e269aad37d5e91c; modeldimensions inferred/authored.','mechanism':'4long primary pointed shields +5short staggered upper rootcovers +2narrowcurvedflanks +3smaller lowerinterstitial polygons. Directindexedradialring topology, explicit3.5mm freewall; distinct nominalfree depths13/10/8.5mm. Morecoverage across narrowroots/gaps while pointedlowerends overlap underplaced smaller polygons.','protected':'Lower15sourceplates,actualbacking/frame/receivers/neck/head/limbs/pivots/hierarchy/materials/era exact; source-body analyticfield andmaximum13mm stand-off retained.','limits':['Onefinal secondshape, no further repairs/propagation.','Stockclosedpositive alone not self/overlap/seat/continuousmotion or ownerlikeness acceptance.','Rootvertex sampled triangles not finiteface loadproof.','Parameter grid is not textureUV/finish.','No app/push/production changes.']}
