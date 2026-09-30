"""Breast-course01: directional free shield shapes on exact compact-mantle02.
Preserves upper receiving bands, topology and recovered finite stock vectors;
changes neither continuous liner nor hidden attachment construction.
"""
from pathlib import Path
import bpy,bmesh,math,runpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
NAMES=[f'V34 formed breast course {r} plate {c}'for r,n in[(1,5),(2,6)]for c in range(1,n+1)]
ROOT_BAND=.021

def ease(u):u=max(0,min(1,u));return u*u*(3-2*u)
def meshfacts(o):
 bm=bmesh.new();bm.from_mesh(o.data);d={'closedEdgeManifold':all(e.is_manifold for e in bm.edges),'positiveVolumeM3':abs(bm.calc_volume(signed=True))};bm.free();return d

def apply():
 bpy.context.view_layer.update();pairer=runpy.run_path(str(ROOT/'scripts/regions/v38-breast-envelope.py'))['pairs'];records=[]
 for name in NAMES:
  o=bpy.data.objects[name];assert o.parent.name=='breastplate';row=int(name.split()[4]);col=int(name.split()[-1]);world=o.matrix_world.copy();inv=world.inverted();local=[v.co.copy()for v in o.data.vertices];points=[world@p for p in local];normal=world.to_3x3().inverted().transposed();normals=[(normal@v.normal).normalized()for v in o.data.vertices];pairs=pairer(points,normals);before=meshfacts(o)
  top=max(p.z for p in points);bottom=min(p.z for p in points);lo=min(p.x for p in points);hi=max(p.x for p in points);center=(lo+hi)*.5;half=(hi-lo)*.5;side=1 if center>.025 else -1 if center<-.025 else 0
  fixed={i for i,p in enumerate(points)if p.z>=top-ROOT_BAND}
  # Paired stock partners remain exact together at receiving bands.
  for i,j in pairs:
   if i in fixed or j in fixed:fixed.update([i,j])
  def displacement(p):
   if p.z>=top-ROOT_BAND:return Vector()
   u=max(0,min(1,(top-ROOT_BAND-p.z)/max(.001,top-ROOT_BAND-bottom)));w=ease(u);t=max(-1,min(1,(p.x-center)/max(.001,half)))
   # Each root is exact. Free course sweeps diagonally out/down and its
   # terminal shoulder-side edge narrows. Root stock never scales.
   sweep=(.035 if row==1 else .026)*side*w
   taper=.22*ease((u-.55)/.45)
   dx=sweep-(p.x-center)*taper
   # Alternating lengths and oblique boundaries follow plate hierarchy,
   # avoiding a continuous horizontal shelf or repeated same-length row.
   length=(.010 if side==0 else (.006 if col%2 else -.003))if row==1 else(.010 if col%2 else -.002)
   dz=(-length+.021*side*t)*w
   # Tangential plan-section mapping keeps source radius; no radial bulk.
   # Authored ellipse is a local interpolation guide, not art metrology.
   radius2=(p.x/.30)**2+(p.y/.43)**2;newx=p.x+dx
   newy=-.43*math.sqrt(max(.0001,radius2-(newx/.30)**2))
   return Vector((dx,newy-p.y,dz))
  moves={i:displacement(p)for i,p in enumerate(points)}
  for i,j in pairs:
   common=Vector()if i in fixed or j in fixed else displacement((points[i]+points[j])*.5);moves[i]=moves[j]=common
  o.data=o.data.copy()
  for i,p in enumerate(points):o.data.vertices[i].co=local[i]if i in fixed or moves[i].length==0 else inv@(p+moves[i])
  o.data.update();after=[world@v.co for v in o.data.vertices];error=max((((after[i]-after[j])-(points[i]-points[j])).length for i,j in pairs),default=0);assert error<3e-7,name
  assert all(o.data.vertices[i].co==local[i]for i in fixed),name
  facts=meshfacts(o);assert facts['closedEdgeManifold']==before['closedEdgeManifold']and facts['positiveVolumeM3']>0,name
  o['v38BreastCourse']='breast-course01 directional tangential exposed shields; true receiving bands exact; proposal'
  records.append({'name':name,'owner':'breastplate','eras':o.get('exteriorEras'),'surfaceRole':o.get('surfaceRole'),'constructionClass':o.get('constructionClass'),'materials':[m.name if m else None for m in o.data.materials],'sourceVertexCount':len(points),'topologyExact':True,'protectedReceivingVertexIndices':sorted(fixed),'receivingBandWorldZMinimumM':top-ROOT_BAND,'recoveredStockPairs':len(pairs),'unpairedTrimmedVertices':len(points)-len(pairs)*2,'maximumStockVectorErrorM':error,'maximumMovementM':max(q.length for q in moves.values()),'sourceBoundsNative':[[min(p[k]for p in points),max(p[k]for p in points)]for k in range(3)],'candidateBoundsNative':[[min(p[k]for p in after),max(p[k]for p in after)]for k in range(3)],'sourceTopology':before,'candidateTopology':facts,'nominalSourceWallM':o.get('wallM')})
 return {'changedMeshes':NAMES,'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'attachmentAndEraMap':records,'visibleMethod':'Source rounded plate surfaces retained; tangential free-edge sweep, varying length, terminal taper. Top21mm actual receiving bands and paired partners exact. Existing finite topology preserved, no liner/backing adaptation.','rigidVsFlexible':'Eleven rigid passive formed shields, one unchanged breastplate cover owner; no flexible skin or powered addition.','supportContract':'Source receiving vertex bands retained exactly. Continuous liner, tabs, V23 returns/shaft, V29 seats and fixed frame exact. Exact roots do not establish wholeplate support/fit.','inspection':'Body-child breastplate transforms, localX+1.1rad inspection,[-.70,-.12,+.18] separation exact; all eleven travel with original cover.','confirmed':'Actual Master03/Maker-clean/Mechanic directional curved down/out breast armor; July head-only excluded.','reconstruction':'Authored free plate outlines/tangential guide and far-side interpretation, not art metrology/engineering acceptance.','limits':['Recovered finite stock pair vectors exact; unmatched Boolean-trimmed vertices use smooth tangent displacement, no universal wall-thickness certificate.','All source envelope/liner/neck gap and receiving16.25mmWARN retained; no implicit source fit improvement.','Actual strict changed11/fullpool and sameowner adjacency diagnostics separate; no continuous collision or owner acceptance.']}
