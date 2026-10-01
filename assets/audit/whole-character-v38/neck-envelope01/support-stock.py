"""Companion finite common-stock diagnostic for existing10 yoke roots and chosen receiver guards."""
import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Matrix
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
MODEL=ROOT/'assets/models/whole-character-v38/neck-envelope01/murderbird-v38-neck-envelope01.blend'
bpy.ops.wm.open_mainfile(filepath=str(MODEL));bpy.context.view_layer.update();receipt=json.loads((OUT/'receipt.json').read_text());dg=bpy.context.evaluated_depsgraph_get()
def common(a,b):
 copies=[]
 try:
  for source in(a,b):
   ev=source.evaluated_get(dg);m=bpy.data.meshes.new_from_object(ev,depsgraph=dg);o=bpy.data.objects.new('temporary finite stock',m);bpy.context.scene.collection.objects.link(o);o.matrix_world=source.matrix_world.copy();copies.append(o)
  x,y=copies;modifier=x.modifiers.new('finite common stock','BOOLEAN');modifier.operation='INTERSECT';modifier.solver='EXACT';modifier.object=y;bpy.context.view_layer.update();ev=x.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();bm=bmesh.new();bm.from_mesh(m);volume=abs(bm.calc_volume(signed=True));count=len(bm.verts);edges=sum(not e.is_manifold for e in bm.edges);bm.free();ev.to_mesh_clear();return {'volumeM3':volume,'vertices':count,'nonManifoldIntersectionEdges':edges,'qualifier':'Diagnostic exact Boolean common stock, not welding/load or physical/swept fit certification.'}
 except Exception as e:return {'error':str(e)}
 finally:
  for o in copies:m=o.data;bpy.data.objects.remove(o,do_unlink=True);bpy.data.meshes.remove(m)
rows=[]
for rec in receipt['contract']['attachmentAndEraMap']:
 if 'sourceFrame'not in rec:continue
 owner=rec['owner'];side=-1 if rec['name'].endswith('-1')else 1
 end=(f'V33 tapered throat cheek plate {side} 1 0'if owner=='head'else f'V23 cervical {1+["neck","cervical-mid-a","cervical-mid-b","cervical-upper"].index(owner)} directional guard {1 if side<0 else 5}')
 a=bpy.data.objects[rec['name']];row={'name':a.name,'owner':owner,'sourceFrame':rec['sourceFrame'],'sourceFaceIndex':rec['sourceFaceIndex'],'selectedReceiver':end,'rootCommonStock':common(a,bpy.data.objects[rec['sourceFrame']]),'selectedReceiverCommonStock':common(a,bpy.data.objects[end])};rows.append(row);print(row,flush=True)
(OUT/'support-stock.json').write_text(json.dumps({'nativeSHA256':hashlib.sha256(MODEL.read_bytes()).hexdigest(),'rows':rows,'limits':['Only actual finite root frame and one selected side receiver per yoke; other guard lands not certified.','Closed connected positive yoke with original-frame face root does not imply all receiver skins seated.','Diagnostic Boolean of sampled neutral solids cannot establish swept clearance or mechanical attachment strength.']},indent=2)+'\n')
