import bpy,bmesh,json,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
model,receipt,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not out.exists();d=json.loads(receipt.read_text());bpy.ops.wm.open_mainfile(filepath=str(model));rows=[]
def points(o):return [o.matrix_world@v.co for v in o.data.vertices]
def tree(o):
 o.data.calc_loop_triangles();return BVHTree.FromPolygons(points(o),[tuple(t.vertices)for t in o.data.loop_triangles],all_triangles=True)
def key(t):return tuple(sorted(tuple(round(v,6)for v in p)for p in t))
for record in d['contract']['pairedFittingSeats']:
 root=bpy.data.objects[record['root']];fit=bpy.data.objects[record['fitting']];receiver=bpy.data.objects[record['receiver']];rt=tree(root);ft=tree(fit);target=tree(receiver);rp=points(root);fp=points(fit);pp=points(receiver);receiver.data.calc_loop_triangles();keys={key([pp[k]for k in t.vertices])for t in receiver.data.loop_triangles};root.data.calc_loop_triangles();fit.data.calc_loop_triangles();n=len(rp)//2;matches=0;tritotal=0;rootgaps=[];fitgaps=[];normals=[]
 for t in root.data.loop_triangles:
  if all(k<n for k in t.vertices):
   tri=[rp[k]for k in t.vertices];tritotal+=1;matches+=key(tri)in keys
   samples=tri+[sum(tri,Vector())/3]+[(tri[j]+tri[(j+1)%3])*.5 for j in range(3)];rootgaps.extend(target.find_nearest(p)[3]for p in samples)
 plane=record['returnOuterNativeSignedX'];base_tri=[]
 for t in fit.data.loop_triangles:
  tri=[fp[k]for k in t.vertices]
  if all(abs(p.x-plane)<1e-6 for p in tri):
   base_tri.append(list(t.vertices));samples=tri+[sum(tri,Vector())/3]+[(tri[j]+tri[(j+1)%3])*.5 for j in range(3)];fitgaps.extend(rt.find_nearest(p)[3]for p in samples)
 rows.append({'root':root.name,'fitting':fit.name,'receiver':receiver.name,'actualReturnInnerTriangles':tritotal,'actualSharedReceiverTriangleKeysAt1Micrometre':matches,'fullReturnTriangleVertexEdgeCentroidSamples':len(rootgaps),'rootInnerSampleToActualReceiverGapMinMaxM':[min(rootgaps),max(rootgaps)],'actualFullAnnularFittingBaseTriangles':len(base_tri),'fullAnnularTriangleVertexEdgeCentroidSamples':len(fitgaps),'fittingFullBaseSampleToActualReturnGapMinMaxM':[min(fitgaps),max(fitgaps)],'rootFootPatchYZExtentM':record['actualFullPatchYZExtentsM'],'fittingFootDiameterM':record['fittingFootDiameterM'],'limits':'Finite full face correspondence plus vertex/edge/centroid distances. This does not waive actual strict crossing, containment or continuous sweep; planar underside within finite return is checked geometrically, not engineering accepted.'})
out.write_text(json.dumps({'model':str(model),'actualFiniteMountFaces':rows,'status':'Bounded actual complete-face interface evidence, not load/manufacture acceptance'},indent=2)+'\n')
