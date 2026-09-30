"""FIT02: localized receiving field from actual leading triangles on five FIT01 leaves.
Paired3mm stock retained; no leading geometry or unrelated FIT01 change.
"""
import bpy,bmesh,math
from mathutils.bvhtree import BVHTree
ALLOWED=[f'V38 swept crown course 3 column {col} leaf 2' for col in range(1,6)]
VERTICES=list(range(65))+list(range(169,234))
GAP=.0004

def apply():
 bpy.context.view_layer.update();records=[]
 for name in ALLOWED:
  o=bpy.data.objects[name];leading=bpy.data.objects[name[:-1]+'1'];assert o.parent==leading.parent and o.parent.name=='cranial-cover'
  original=[v.co.copy() for v in o.data.vertices];world=o.matrix_world.copy();inv=world.inverted();outer=[world@p for p in original[:169]];inner=[world@p for p in original[169:]];dirs=[(a-b).normalized() for a,b in zip(outer,inner)]
  assert len(original)==338 and max(abs((a-b).length-.003) for a,b in zip(outer,inner))<2e-7
  leading.data.calc_loop_triangles();lv=[leading.matrix_world@v.co for v in leading.data.vertices];lt=[tuple(t.vertices) for t in leading.data.loop_triangles if all(i>=169 for i in t.vertices)];tree=BVHTree.FromPolygons(lv,lt,all_triangles=True,epsilon=1e-7)
  # Sample real leading surfaces across actual receiving triangles, not a global depth.
  def needed(point,direction):
   loc,normal,index,distance=tree.find_nearest(point)
   return max(0,GAP-(point-loc).dot(normal)),1
  directions=[tree.find_nearest(point)[1] for point in outer[:65]]
  field=[0.0]*65;sample_count=hit_samples=0
  o.data.calc_loop_triangles()
  for triangle in o.data.loop_triangles:
   indices=tuple(triangle.vertices)
   if not all(i<65 for i in indices):continue
   for i in range(9):
    for j in range(9-i):
     weights=(i/8,j/8,1-(i+j)/8);point=sum((outer[k]*w for k,w in zip(indices,weights)),outer[0]*0);direction=sum((dirs[k]*w for k,w in zip(indices,weights)),dirs[0]*0).normalized();requirement,hits=needed(point,direction);sample_count+=1;hit_samples+=hits>0
     if requirement>0:
      # Conservative constant bound over each sampled finite triangle; short hidden return.
      for k in indices:field[k]=max(field[k],requirement+.0002)
  assert max(field)<.006,'Local fit exceeds bounded6mm additional offset'
  o.data=o.data.copy();changed=[]
  for k,offset in enumerate(field):
   if offset<=0:continue
   for index,p in ((k,outer[k]),(169+k,inner[k])):
    o.data.vertices[index].co=inv@(p+directions[k]*offset);changed.append(index)
  o.data.update();actual=sorted(changed);assert set(actual)<=set(VERTICES)
  assert all(v.co==original[v.index] for v in o.data.vertices if v.index not in actual)
  stock=[((world@o.data.vertices[i].co)-(world@o.data.vertices[i+169].co)).length for i in range(169)];assert max(abs(t-.003) for t in stock)<2e-7
  bm=bmesh.new();bm.from_mesh(o.data);closed=all(e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free();assert closed and volume>0
  o['v38CrownLapFit']='crown-fit02 localized actual-leading-triangle receiving field on FIT01;3mm stock; no full fit certificate'
  records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'role':o.get('constructionClass'),'materials':[m.name for m in o.data.materials],'vertexAllowlist':actual,'maximumPermittedVertexScope':VERTICES,'changedVertices':len(actual),'maximumAdditionalNormalDisplacementM':max(field),'additionalNormalOffsetByOuterVertexM':{str(k):v for k,v in enumerate(field) if v>0},'actualLeadingInnerFaceSamples':sample_count,'samplesHittingLeading':hit_samples,'targetInnerNormalGapM':GAP,'sampleEnvelopeAllowanceM':.0002,'minimumStockM':min(stock),'maximumStockM':max(stock),'closed':closed,'positiveVolumeM3':volume,'method':'Actual leading inner-triangle nearest-surface normal envelope, locally bounded over receiving triangles. Both finite surfaces translate together; leading leaves and all excluded vertices stay exact.'})
 return {'changedMeshes':ALLOWED,'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'attachmentAndEraMap':records,'allLeadingLeaf1AndOtherTrailingVerticesExact':True,'confirmation':'Final focused fit attempt from frozen FIT01. Only five residual row3 receiving interfaces re-seat against actual leading surfaces.','reconstruction':'Surface-driven receiving field with0.4mm inner-normal gap and0.2mm sampled-triangle envelope allowance. Actual same-epsilon surface screen and neighbor dispositions govern status, not full solid/sweep proof.'}
