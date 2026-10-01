# Read-only saved finite topology, receiver faces, paired stock and protected lands.
import bpy,bmesh,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
r=Path(__file__).resolve().parents[4];a=Path(__file__).resolve().parent;receipt=json.loads((a/'receipt.json').read_text());base=r/receipt['inputs']['native']['path'];candidate=r/receipt['outputs']['native']['path'];out=a/'geometry-seat-check.json';assert not out.exists();names=receipt['contract']['changedMeshes']
def geom(o):return [list(v.co)for v in o.data.vertices],[list(p.vertices)for p in o.data.polygons]
bpy.ops.wm.open_mainfile(filepath=str(base));sourceCrown={o.name:geom(o)for o in bpy.data.objects if o.name.startswith('V38 swept crown course')};sourceWalls={n:geom(bpy.data.objects[n])for n in names if n.startswith('V31 fixed temporal')}
bpy.ops.wm.open_mainfile(filepath=str(candidate));assert all(geom(bpy.data.objects[n])==g for n,g in sourceCrown.items());rows=[];lands=[]
for n in names:
 o=bpy.data.objects[n];bm=bmesh.new();bm.from_mesh(o.data);remaining=set(bm.verts);components=0
 while remaining:
  components+=1;stack=[remaining.pop()]
  while stack:
   v=stack.pop()
   for e in v.link_edges:
    w=e.other_vert(v)
    if w in remaining:remaining.remove(w);stack.append(w)
 rows.append({'name':n,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'components':components,'nonmanifoldEdges':sum(not e.is_manifold for e in bm.edges),'signedVolumeM3':bm.calc_volume(signed=True)});bm.free()
 if n.startswith('V33 swept temporal'):
  side=int(n.split()[-2]);wall=bpy.data.objects[f'V31 fixed temporal receiving wall {side}'];wall.data.calc_loop_triangles();wv=[wall.matrix_world@v.co for v in wall.data.vertices];wt=[tuple(t.vertices)for t in wall.data.loop_triangles];tree=BVHTree.FromPolygons(wv,wt,all_triangles=True);v=[o.matrix_world@q.co for q in o.data.vertices];half=len(v)//2;stock=[(v[k]-v[k+half]).length for k in range(half)];gap=max(tree.find_nearest(q)[3]for q in v[half:]);o.data.calc_loop_triangles();areas=[(v[t.vertices[1]]-v[t.vertices[0]]).cross(v[t.vertices[2]]-v[t.vertices[0]]).length/2 for t in o.data.loop_triangles if all(k>=half for k in t.vertices)];lands.append({'plate':n,'receiver':wall.name,'fullInnerFootprintTriangles':len(areas),'fullFiniteInnerFootprintAreaM2':sum(areas),'savedInnerVertexMaxReceiverGapM':gap,'actualPairedAxialStockM':[min(stock),max(stock)],'disposition':'Full inner face field was clipped from named receiver triangles; nearest-vertex confirmation is supplementary, strict interpart crossings remain HOLD. Axial stock is not minimum normal wall thickness or manufacturing approval.'})
protected=[]
for row in receipt['contract']['protectedWallLands']:
 n=row['wall'];old=sourceWalls[n][0];actual=geom(bpy.data.objects[n])[0];delta=max((Vector(old[i])-Vector(actual[i])).length for i in row['protectedSourceVertexIndices']);protected.append({'wall':n,'protectedSourceVertices':len(row['protectedSourceVertexIndices']),'maxLocalMovementM':delta});assert delta<1e-7
out.write_text(json.dumps({'status':'Topology/stock/land observation; assembly fit HOLD separately','newGeometry':rows,'finiteReceivingFaces':lands,'protectedWallLandVertices':protected,'front58CrownAllVertexFaceCoordinatesExact':len(sourceCrown),'limits':['Closed/manifold positive volume does not establish absence of interpart penetration.','Actual paired stock axial3.5–6mm may have smaller normal thickness on steep faces.','Head-owned skirt and separately moving neck remain distinct; sampled screen only, no sweep proof.']},indent=2)+'\n');print('geometry-seat-check saved',flush=True)
