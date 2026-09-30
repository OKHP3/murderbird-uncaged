"""Finite hidden underlap rebate; preserves leading leaves and3mm stock.
Only paired outer/inner first five rows on29 trailing leaf2 meshes may move.
"""
import bpy,bmesh,math
from mathutils import Vector
ALLOWED=[f'V38 swept crown course {row} column {col} leaf 2' for row,cols in [(0,range(7)),(1,range(7)),(2,range(7)),(3,range(1,6)),(4,range(2,5))] for col in cols]
VERTICES=list(range(65))+list(range(169,234))
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def apply():
 bpy.context.view_layer.update();records=[]
 for name in ALLOWED:
  o=bpy.data.objects[name];assert o.parent.name=='cranial-cover' and len(o.data.vertices)==338,name
  original=[v.co.copy() for v in o.data.vertices];world=o.matrix_world.copy();inv=world.inverted();outer=[world@p for p in original[:169]];inner=[world@p for p in original[169:]]
  old_stock=[(a-b).length for a,b in zip(outer,inner)];assert max(abs(t-.003) for t in old_stock)<2e-7,name
  o.data=o.data.copy();changed=[];displacements=[]
  for k in range(65):
   row=k//13;u=row/12;rebate=.002*(1-ease((u-.22)/.18));assert rebate>0
   direction=(outer[k]-inner[k]).normalized();delta=direction*rebate
   for index,p in ((k,outer[k]),(169+k,inner[k])):
    o.data.vertices[index].co=inv@(p-delta);changed.append(index);displacements.append(rebate)
  o.data.update();assert changed==VERTICES
  assert all(v.co==original[v.index] for v in o.data.vertices if v.index not in VERTICES)
  bm=bmesh.new();bm.from_mesh(o.data);closed=all(e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free();assert closed and volume>0,name
  stock=[((world@o.data.vertices[i].co)-(world@o.data.vertices[i+169].co)).length for i in range(169)];assert max(abs(t-.003) for t in stock)<2e-7,name
  o['v38CrownLapFit']='crown-fit01 paired3mmstock hidden trailing receiving rebate; surface diagnostic required, no full fit certification'
  records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'role':o.get('constructionClass'),'materials':[m.name for m in o.data.materials],'vertexAllowlist':VERTICES,'changedVertices':len(changed),'maximumInwardDisplacementM':max(displacements),'minimumStockM':min(stock),'maximumStockM':max(stock),'closed':closed,'positiveVolumeM3':volume,'method':'Translate both paired finite surfaces along their exact source radial stock vectors;2mm receiving rebate through covered interval, smooth return by trailingu0.40. No thinning or disconnected part.'})
 return {'changedMeshes':ALLOWED,'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'attachmentAndEraMap':records,'exactVertexAllowlistPerMesh':VERTICES,'allLeadingLeaf1AndOtherTrailingVerticesExact':True,'confirmation':'Fit correction to visually preferred crown02. Existing source lap offset is smaller than finite3mmstock over part of paired overlap.','reconstruction':'Finite receiving rebate and intended running gap are authored proposals; actual surface diagnostics and adjacent effects govern checkpoint status.'}
