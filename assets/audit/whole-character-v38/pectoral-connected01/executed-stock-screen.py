"""Read-only actual finite ring and rootland stock measurements; no engineering PASS."""
import bpy,json,sys,math,runpy,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
from mathutils.geometry import intersect_point_line
ROOT=Path(__file__).resolve().parents[4];native,receipt,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not out.exists();d=json.loads(receipt.read_text());bpy.ops.wm.open_mainfile(filepath=str(native));o=bpy.data.objects['V30 continuous tapered breast liner'];points=[o.matrix_world@v.co for v in o.data.vertices];tree=KDTree(len(points))
for i,p in enumerate(points):tree.insert(p,i)
tree.balance();base=[Vector(p)for p in d['contract']['sharedBoundary']['exactSourceBoundaryWorldVertices']];h=runpy.run_path(str(Path(__file__).parent/'executed-region.py'));section=h['section'];top=h['top'];lo=min(range(len(base)),key=lambda i:base[i].x);hi=max(range(len(base)),key=lambda i:base[i].x)
def path(step):
 r=[];j=lo
 while True:
  r.append(j)
  if j==hi:break
  j=(j+step)%len(base)
 return r
paths=[path(1),path(-1)];outer=min(paths,key=lambda r:sum(base[i].y for i in r)/len(r));inner=paths[1]if outer==paths[0]else paths[0];rows=[]
for u in[0,.25,.5,.75,1]:
 expected=[]
 for p in base:
  a=math.asin(max(-1,min(1,p.x/.303)));z=1.11+(top(a)-1.11)*u;rx,y=section(z);expected.append(Vector((p.x*rx/.303,p.y+(y+.39048)*math.cos(a),z)))
 actual=[tree.find(p)[0]for p in expected];error=max((p-q).length for p,q in zip(expected,actual));thickness=[]
 for a,b in zip(outer,outer[1:]):
  p=(actual[a]+actual[b])*.5
  if abs(p.x)>max(q.x for q in actual)*.80:continue
  candidates=[]
  for c,e in zip(inner,inner[1:]):
   q,t=intersect_point_line(p,actual[c],actual[e]);q=actual[c].lerp(actual[e],max(0,min(1,t)));candidates.append((p-q).length)
  thickness.append(min(candidates))
 rows.append({'extrusionFraction':u,'actualRingVertexMatches':len(actual),'maxExpectedToActualVertexDistanceM':error,'outerSegmentMidpointToOppositeInnerFiniteSegmentDistancesM':thickness,'minimumSampledStockM':min(thickness),'maximumSampledStockM':max(thickness)})
roots=[]
for item in d['contract']['panelRootLandings']:
 foot=item['finiteRootLand42CornerPerimeterGridSamples'];roots.append({'name':item['name'],'actualFiniteReceivingSamples':len(foot),'maximumFiniteFootVertexGapM':max(p['nearestFiniteSurfaceDistanceM']for p in foot),'rootStockMinimumM':min(p['rootStockDistanceM']for p in foot),'rootStockMaximumM':max(p['rootStockDistanceM']for p in foot)})
out.write_text(json.dumps({'status':'Actual sampled finite stock/receiving geometry; engineering and full fit not accepted','nativeSha256':hashlib.sha256(native.read_bytes()).hexdigest(),'linerStockRings':rows,'connectedRootLandStock':roots,'limits':['Five actual38vertex loft crosssections, middle80% anterior arc sampled; side returns/end caps and inter-ring interiors not universalstockcertified.','Rootland corner/perimeter grid samples meet actual named backing surfaces. Strict same-owner triangle crossings are separately reported, not excused as attachment.','Closure/component assertions and these dimensions do not certify selfintersection, loading, fabrication or continuous motion.']},indent=2)+'\n')
