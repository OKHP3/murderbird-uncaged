"""Read-only named source-seat finite relationships; no engineering certificate."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
a,b,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not out.exists()
def tree(o):
 o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(t.vertices) for t in o.data.loop_triangles],all_triangles=True)
relations=[]
for s in (-1,1):
 cheek=f'V24 rising thoracic receiving cheek {s}';guard=f'V35 oblique thoracic side guard {s} 0'
 relations += [(cheek,f'V24 shoulder lower load fork {s}'),(cheek,f'V35 posterior bay load rail {s}'),(cheek,f'V35 lateral thoracic bay load rail {s}'),(guard,cheek),(f'V35 scapular receiving plate {s} 0',cheek),(f'V35 scapular receiving plate {s} 1',cheek)]
models=[];sourceSeats={};sourceCoords={}
for label,path in [('baseline',a),('candidate',b)]:
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();rows=[]
 for subject,target in relations:
  o=bpy.data.objects[subject];p=bpy.data.objects[target];other=tree(p);v=[o.matrix_world@q.co for q in o.data.vertices];allDistances=[other.find_nearest(q)[3] for q in v];key=subject+' -> '+target
  if label=='baseline':sourceSeats[key]=[i for i,d in enumerate(allDistances) if d<=.0025];sourceCoords[key]=[q.copy() for q in v]
  idx=sourceSeats[key];values=[allDistances[i] for i in idx];rows.append({'subject':subject,'target':target,'owners':[o.parent.name,p.parent.name],'sourceNearSeatVertexIndices':idx,'thresholdM':.0025,'nearestAllVertexDistanceMinM':min(allDistances),'sourceSeatNearestDistanceMinM':min(values) if values else None,'sourceSeatNearestDistanceMaxM':max(values) if values else None,'maximumSourceSeatVertexMovementM':max((v[i]-sourceCoords[key][i]).length for i in idx) if idx else None})
 models.append({'label':label,'nativeSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'relations':rows})
out.write_text(json.dumps({'status':'Named attachment/receiving-seat dispositions, not blanket PASS','models':models,'construction':'V35 source .002m formed receiver relation to V24 cheek; fixed support source near-seat footprint separately measured. Source2.5mm threshold only inventories attachments, never alters strict collision epsilon.','limits':['Vertex-nearest surface metric is not triangle contact/penetration or full joined surface metrology. Same-body actual strict contacts are retained in the separate union40 screen.','No motion, fabrication/weld/load certificate; all pivots/owners exact independently.']},indent=2)+'\n')
