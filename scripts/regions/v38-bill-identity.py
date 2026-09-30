"""Functional connection repair only; frozen artistic01/02 preserved."""
import bpy,json,hashlib,math,bmesh
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'assets/models/whole-character-v38/breast-clearance02/murderbird-v38-breast-clearance02.blend'
NAME='V32 formed mandibular bowl'
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def apply():
 assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='a57898797d040ed2ea52aa1b8b30749d77a8c49ebc3ba785ed3169ada587aad8'
 input_path=bpy.data.filepath;bpy.ops.wm.open_mainfile(filepath=str(SOURCE));pts=[v.co.copy() for v in bpy.data.objects[NAME].data.vertices];bpy.ops.wm.open_mainfile(filepath=input_path);o=bpy.data.objects[NAME];original=[v.co.copy() for v in o.data.vertices];assert len(pts)==len(original);metadata=json.loads(bpy.data.objects['jaw']['makerControlSocketV1']);q=metadata['point'];seat=Vector((q[0],-q[2],q[1]));index=min(range(len(pts)),key=lambda i:(pts[i]-seat).length);assert index==397
 stock=json.loads((ROOT/'assets/audit/whole-character-v38/bill-identity01/receipt.json').read_text())['contract']['attachmentAndEraMap'][-1]['recoveredFiniteStockPairs'];weights={i:1-ease(((p-seat).length-.020)/.030) for i,p in enumerate(pts)}
 for i,j in stock:weights[i]=weights[j]=max(weights[i],weights[j])
 o.data=o.data.copy()
 for i,p in enumerate(original):
  w=weights[i]
  if w==1:o.data.vertices[i].co=pts[i]
  elif w>0:o.data.vertices[i].co=p+(pts[i]-p)*w
 o.data.update();assert o.data.vertices[397].co==pts[397];error=max(((o.data.vertices[i].co-o.data.vertices[j].co)-(original[i]-original[j])).length for i,j in stock);assert error<3e-7
 changed=[i for i,p in enumerate(original) if o.data.vertices[i].co!=p];distal=[i for i,p in enumerate(pts) if p.y<-.155];assert all(o.data.vertices[i].co==original[i] for i in distal)
 bm=bmesh.new();bm.from_mesh(o.data);closed=all(e.is_manifold for e in bm.edges);volume=abs(bm.calc_volume(signed=True));bm.free();assert closed and volume>0
 o['v38BillSocketFit']='Functional source-seat restoration only; artistic01 contour retained, no third artistic attempt'
 return {'changedMeshes':[NAME],'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'attachmentAndEraMap':[{'name':NAME,'owner':o.parent.name,'eras':o.get('exteriorEras'),'constructionClass':o.get('constructionClass'),'materials':[m.name for m in o.data.materials],'changedVertexIndices':changed,'method':'Restore actual original socket397 and20mm source seat with smooth fade to50mm; recovered opposing stock pairs share max seat restoration weight.','actualSocketSourceVertexIndex':397,'actualSocketSourceLocal':list(pts[397]),'actualSocketCandidateLocal':list(o.data.vertices[397].co),'socketMetadata':metadata,'protectedDistalLocalYBelow':-.155,'protectedDistalIndices':distal,'maximumMovementM':max((o.data.vertices[i].co-p).length for i,p in enumerate(original)),'recoveredFiniteStockPairs':stock,'maximumStockVectorErrorM':error,'closedEdgeManifold':closed,'positiveVolumeM3':volume}],'confirmation':'Functional Maker source-seat restoration authorized after two frozen artistic proposals; all other01 geometry exact.','reconstruction':'20mm receiving seat/50mm smooth fade is authored local finite repair, not third likeness pass.','contactLandmarksChanged':False,'limits':['Same upper-bill contact extrema as01; integrator owns solver.','Discrete same-predicate jaw/socket evidence separate; no continuous sweep or construction acceptance.']}
