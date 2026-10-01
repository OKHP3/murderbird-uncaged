import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[4];A=Path(__file__).resolve().parent;P=R/'assets/models/whole-character-v38/throat-construction02/murderbird-v38-throat-construction02.blend';pin=hashlib.sha256(P.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(P));bpy.context.view_layer.update()
def data(o):
 m=o.data;m.calc_loop_triangles();v=[o.matrix_world@x.co for x in m.vertices];t=[tuple(x.vertices)for x in m.loop_triangles];return v,t,BVHTree.FromPolygons(v,t,all_triangles=True)
def coverage(points,tree):
 rows=[]
 for p in points:
  hit,n,face,d=tree.find_nearest(p)
  rows.append({'point':list(p),'nearestFinitePoint':list(hit),'normal':list(n),'triangle':face,'distanceM':d,'signedNormalSeparationM':(p-hit).dot(n)})
 return {'samples':len(rows),'minDistanceM':min(x['distanceM']for x in rows),'maxDistanceM':max(x['distanceM']for x in rows),'minSignedSeparationM':min(x['signedNormalSeparationM']for x in rows),'maxSignedSeparationM':max(x['signedNormalSeparationM']for x in rows),'worstWitness':max(rows,key=lambda x:x['distanceM']),'firstWitness':rows[0]}
def patchpoints(v,faces):
 points=[];area=0
 for f in faces:
  p=[v[i]for i in f];area+=(p[1]-p[0]).cross(p[2]-p[0]).length/2;points+=p+[(p[i]+p[(i+1)%3])/2 for i in range(3)]+[sum(p,Vector())/3]
 return points,area
arches=['V38 lower cranial throat receiving arch','V38 upper cranial throat receiving arch'];feet=[];roots=[];stocks=[]
for row,name in enumerate(arches):
 o=bpy.data.objects[name];v,t,tree=data(o)
 for side in(-1,1):
  # Actual finite receiving land on arch outer sheet:18 angular intervals1.10..1.40rad, full12mm height.
  # Records every selected triangle/corner/edge midpoint/center, not a centroid proxy.
  triangles=[]
  for ids in t:
   if max(ids)>=339:continue
   p=[v[i]for i in ids];c=sum(p,Vector())/3;a=math.atan2(c.x,c.y*0+(-c.y-.344))
   if side*a>1.10 and side*a<1.40:triangles.append(ids)
  assert triangles;points,area=patchpoints(v,triangles);bow=bpy.data.objects[f'V31 passive cranial load bow {side}'];_,_,bt=data(bow)
  feet.append({'arch':name,'receiver':bow.name,'finiteArchTriangles':len(triangles),'finiteLandAreaM2':area,'coverage':coverage(points,bt),'attachmentDisposition':'HOLD: actual finite land samples measured; any strict arch-to-bow crossing in surface-screen remains insertion/interference needing compatible receiving design, not an accepted weld/bolted seat.'})
for side in(-1,0,1):
 for row in(0,1):
  _,_,tree=data(bpy.data.objects[arches[row]])
  for col in range(3):
   name=f'V33 tapered throat cheek plate {side} {row} {col}';o=bpy.data.objects[name];v,t,_=data(o);half=375
   # Full first longitudinal inner-strip triangle patch, not sampled outer rootline alone.
   faces=[ids for ids in t if min(ids)>=half and max(ids)<half+30];assert faces;points,area=patchpoints(v,faces);roots.append({'plate':name,'receiver':arches[row],'fullRootLandTriangles':len(faces),'finiteLandAreaM2':area,'coverage':coverage(points,tree),'attachmentDisposition':'HOLD pending full strictroot/arch triangles. Shared analytic field at root vertices alone does not prove finite-face compatibility.'})
   minimum=10;maximum=0
   for ids in t:
    if max(ids)>=half:continue
    p=[v[i]for i in ids];n=(p[1]-p[0]).cross(p[2]-p[0]).normalized();d=sum(abs((v[i]-v[i+half]).dot(n))for i in ids)/3;minimum=min(minimum,d);maximum=max(maximum,d)
   stocks.append({'name':name,'outerTriangleMeanPairedProjectedStockMinM':minimum,'outerTriangleMeanPairedProjectedStockMaxM':maximum,'limit':'Paired vertex projection onto actual outer triangle normal; not global closest inner-wall thickness or rimstock fabrication certificate.'})
assert hashlib.sha256(P.read_bytes()).hexdigest()==pin
(A/'support-check.json').write_text(json.dumps({'nativeSha256':pin,'actualArchToBowFiniteLands':feet,'actualPlateToArchFullRootLands':roots,'finiteTriangleProjectedStock':stocks,'limits':['Strict crossings are separately evaluated, no automatic accepted insertion contact.','Land area is geometric selected surface; nearest sample coincidence does not prove continuous contact/stock/engineering.','All20 new constructions head-owned, so receiving relations fixed under sampled neck/jaw motion; separate joint-owned guards move relative and remain screened.','No lower-neck rigidbridge, trueframe/pivots/sourcehardware preserved.']},indent=2)+'\n')
print('ARCH',[(x['arch'],x['receiver'],x['coverage']['minDistanceM'],x['coverage']['maxDistanceM'])for x in feet]);print('ROOT',[(x['plate'],x['coverage']['maxDistanceM'])for x in roots]);print('STOCK',min(x['outerTriangleMeanPairedProjectedStockMinM']for x in stocks))
