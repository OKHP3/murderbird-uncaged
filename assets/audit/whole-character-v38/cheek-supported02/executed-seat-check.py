import bpy,bmesh,json,sys,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
model,receipt,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not out.exists();d=json.loads(receipt.read_text());bpy.ops.wm.open_mainfile(filepath=str(model));rows=[];topology=[]
def tree(name):
 o=bpy.data.objects[name];o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(t.vertices)for t in o.data.loop_triangles],all_triangles=True)
def points(name):
 o=bpy.data.objects[name];return [o.matrix_world@v.co for v in o.data.vertices]
for row in d['contract']['pairedFittingSeats']:
 root=row['root'];fit=row['fitting'];receiver=row['receiver'];rt=tree(root);target=tree(receiver);p=points(fit);side=1 if ' 1 'in root else -1;lo=min(abs(v.x)for v in p);foot=[q for q in p if abs(abs(q.x)-lo)<1e-6];gap=[rt.find_nearest(q)[3]for q in foot];rp=points(root);n=len(rp)//2;actual=rp[:n];tg=[target.find_nearest(q)[3]for q in actual];samples=[]
 for q,w in zip(actual,actual[1:]+actual[:1]):samples.append((q+w)*.5)
 mg=[target.find_nearest(q)[3]for q in samples]
 rows.append({'root':root,'fitting':fit,'receiver':receiver,'actualFittingBaseVertices':len(foot),'actualFittingBaseToFullReturnSurfaceGapMinMaxM':[min(gap),max(gap)],'actualReturnFootVertices':len(actual),'returnFootToFullReceiverSurfaceGapMinMaxM':[min(tg),max(tg)],'returnPerimeterMidpointToReceiverGapMinMaxM':[min(mg),max(mg)],'returnActualYZExtentM':[max(q.y for q in actual)-min(q.y for q in actual),max(q.z for q in actual)-min(q.z for q in actual)],'fittingActualYZFootprintM':[max(q.y for q in foot)-min(q.y for q in foot),max(q.z for q in foot)-min(q.z for q in foot)],'rootActualThicknessBoundsM':[min(abs(q.x)for q in rp),max(abs(q.x)for q in rp)],'limits':'Saved finite fitting base and return perimeter versus actual saved BVH triangles. Polygon interpolation/full volume may cross despite sampled gaps; strict full neighbor/self diagnostics take precedence, no support/load/manufacture approval.'})
for name in d['contract']['changedMeshes']:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);pending=set(bm.verts);components=[]
 while pending:
  visited={pending.pop()};todo=list(visited)
  while todo:
   v=todo.pop()
   for e in v.link_edges:
    q=e.other_vert(v)
    if q in pending:pending.remove(q);visited.add(q);todo.append(q)
  components.append(len(visited))
 topology.append({'name':name,'connectedVertexComponents':len(components),'componentVertexCounts':sorted(components,reverse=True),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'signedVolumeM3':bm.calc_volume(signed=True),'usedMaterialSlotsValid':all(o.data.materials[f.material_index]is not None for f in o.data.polygons)});bm.free()
out.write_text(json.dumps({'source':str(model),'status':'Bounded actual finite footprint/topology evidence; not seating certification','pairedFittingRecords':rows,'topology':topology,'limits':['01tiny triangle return is not the full fitting circular footprint.','02full13mm perimeter is a declared finite footprint but actual intervening polygon faces can interpolate through receiving triangles.','No continuous swept motion, physics or load-path acceptance.']},indent=2)+'\n')
