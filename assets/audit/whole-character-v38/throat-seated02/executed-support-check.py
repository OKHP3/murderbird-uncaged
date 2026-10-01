import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
native,receipt,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(native));r=json.loads(receipt.read_text());rows=[]
def finite(o,ids):
 o.data.calc_loop_triangles();v=[o.matrix_world@p.co for p in o.data.vertices];t=[tuple(q.vertices)for q in o.data.loop_triangles if all(k in ids for k in q.vertices)];return v,t
for land,pad in zip(r['contract']['fullFiniteRootLands'],r['contract']['fullFiniteCoverPads']):
 support=bpy.data.objects[land['support']];bow=bpy.data.objects[land['receiver']];cover=bpy.data.objects[pad['receivingCover']];sv,st=finite(support,set(pad['supportOuterVertexIndices']));cv,ct=finite(cover,set(pad['coverInnerVertexIndices']));assert len(st)==len(ct)==24
 tree=BVHTree.FromPolygons(cv,ct,all_triangles=True);errors=[];area=0
 for tri in st:
  a,b,c=[sv[k]for k in tri];area+=(b-a).cross(c-a).length/2
  for p in (a,b,c,(a+b)/2,(b+c)/2,(c+a)/2,(a+b+c)/3):errors.append(tree.find_nearest(p)[3])
 roots=[];bv=[bow.matrix_world@p.co for p in bow.data.vertices]
 for tri in land['complete24TriangleRootCorrespondence']:
  for src,dest in zip(tri['sourceIndices'],tri['supportInnerIndices']):roots.append((support.matrix_world@support.data.vertices[dest].co-bv[src]).length)
 # Actual finite paired lateral wall stock projection, excludes closing side walls.
 stocks=[]
 for o in (support,cover):
  o.data.calc_loop_triangles();n=len(o.data.vertices)//2;v=[o.matrix_world@p.co for p in o.data.vertices]
  for tri in o.data.loop_triangles:
   if all(k<n for k in tri.vertices):
    a,b,c=[v[k]for k in tri.vertices];normal=(b-a).cross(c-a).normalized();stocks.append(abs(sum((v[k+n]-v[k]).dot(normal)for k in tri.vertices)/3))
 rows.append({'support':support.name,'bow':bow.name,'cover':cover.name,'rootMaxCopiedTriangleVertexErrorM':max(roots),'coverPadActualTriangles':len(st),'receiverCoverTriangleIndices':ct,'supportTriangleIndices':st,'fullFinitePadAreaM2':area,'fullTriangleCornersEdgeMidpointsCentersMaxGapM':max(errors),'actualPairedFaceProjectedStockMinimumM':min(stocks),'state':'Finite footprint correspondence measured, not universal attachment/stock or engineering acceptance; outgoing return and neighboring rigid surfaces retain independent diagnostics.'})
out.write_text(json.dumps({'status':'Measured full finite support correspondence; assembly HOLD pending strict contacts and likeness','rows':rows,'limits':['Finite constant lateral extrusion may yield very thin normal-projected stock where surfaces steepen.','Root copied finite triangles do not certify external load capacity or clearance to other surfaces.','Only rest geometry inspected; owners/bows/pivots are unchanged and head-owned.']},indent=2)+'\n')
