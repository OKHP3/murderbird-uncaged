"""Witness-based finite local return on upper4/10 only; visible neck02 exact elsewhere."""
import bpy,bmesh,json
from mathutils import Vector,Matrix
from pathlib import Path
NAME='V23 cervical 4 directional guard 10'
OUTER=[row*19+col for row in (19,20) for col in range(6,15)]
ALLOWED=OUTER+[i+399 for i in OUTER]
def apply():
 bpy.context.view_layer.update();o=bpy.data.objects[NAME];assert o.parent.name=='cervical-upper' and len(o.data.vertices)==798
 original=[v.co.copy() for v in o.data.vertices];world=o.matrix_world.copy();inv=world.inverted();diagnosis=Path(__file__).resolve().parents[2]/'assets/audit/whole-character-v38/neck-clearance01/witness-diagnosis/diagnosis.json';data=json.loads(diagnosis.read_text());assert data['actualStrictTrianglePairs']==8
 maker=Matrix(data['upperMakerMatrixWorld']);direction=(world.to_3x3()@maker.to_3x3().inverted()@Vector((0,0,1))).normalized()
 # Shorten only the witnessed free receiving end: source top-face signed
 # deficits0.34..0.415mm justify a1.8mm formed return, not screen relaxation.
 before_stock=[((world@original[i])-(world@original[i+399])).length for i in range(399)];assert max(abs(t-.0035) for t in before_stock)<2e-7
 o.data=o.data.copy();rows=[]
 for i in OUTER:
  row,col=divmod(i,19);fade={6:.25,7:.8,8:1,9:1,10:1,11:1,12:1,13:.8,14:.25}[col];lift=.0018*fade*(1 if row==20 else .25)
  delta=direction*lift
  for index in (i,i+399):o.data.vertices[index].co=inv@((world@original[index])+delta)
  rows.append({'outerVertex':i,'innerVertex':i+399,'liftM':lift})
 o.data.update();assert all(v.co==original[v.index] for v in o.data.vertices if v.index not in ALLOWED)
 stock=[((world@o.data.vertices[i].co)-(world@o.data.vertices[i+399].co)).length for i in range(399)];assert max(abs(t-.0035) for t in stock)<2e-7
 bm=bmesh.new();bm.from_mesh(o.data);closed=all(e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free();assert closed and volume>0
 o['v38NeckClearance']='neck-clearance01 local finite lower-edge return against measured Maker receiver; visible neck02 tips and all excluded vertices exact'
 return {'changedMeshes':[NAME],'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'attachmentAndEraMap':[{'name':NAME,'owner':o.parent.name,'eras':o.get('exteriorEras'),'surfaceRole':o.get('surfaceRole'),'constructionClass':o.get('constructionClass'),'materials':[m.name for m in o.data.materials],'exactVertexAllowlist':ALLOWED,'changedVertices':len(ALLOWED),'pairedOffsets':rows,'sourceStrictFootprint':data['upperVertexFootprint'],'makerUpDirectionMappedToNativeRest':list(direction),'maximumAuthoredMovementM':.0018,'finiteClosed':closed,'positiveVolumeM3':volume,'minimumPairedStockM':min(stock),'maximumPairedStockM':max(stock),'allExcludedVerticesExact':True}],'allOtherNeckHeadBodyGeometryPivotsMaterialsEraRolesExact':True,'confirmation':'Actual unchanged Maker strict-screen footprint locates a free-end interface on upper4/10 only. Master03/Mechanic neck direction retained; July head-only.','reconstruction':'Finite1.8mm local return with smooth grid fade is authored clearance geometry; same strict screen governs checkpoint status.','limits':['Paired3.5mm stock retained; no stripping or part deletion.','No full containment, continuous-sweep, load or tolerance proof.','No head contact extrema, owner, attachment or runtime change.']}
