from pathlib import Path
import bpy,bmesh,json,math,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');A=Path(__file__).parent;rec=json.loads((A/'receipt.json').read_text());N=R/rec['native']['path'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(N)==rec['native']['sha256'];assert sha(R/'scripts/regions/whole-character-v36-face-construction.py')==rec['sourceSHA256'];bpy.ops.wm.open_mainfile(filepath=str(N));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();rows=[]
for name in rec['result']['changedMeshes']+rec['result']['added']:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);todo=set(bm.verts);count=0
 while todo:
  count+=1;q=[todo.pop()]
  while q:
   v=q.pop()
   for e in v.link_edges:
    p=e.other_vert(v)
    if p in todo:todo.remove(p);q.append(p)
 raw={'connectedComponents':count,'closed':all(e.is_manifold for e in bm.edges),'positiveVolumeM3':bm.calc_volume(signed=True)};bm.free();ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();p=[ev.matrix_world@v.co for v in m.vertices];assert all(math.isfinite(c) for v in p for c in v);zero=sum((p[t.vertices[1]]-p[t.vertices[0]]).cross(p[t.vertices[2]]-p[t.vertices[0]]).length*.5<=1e-14 for t in m.loop_triangles);ev.to_mesh_clear();assert raw['closed'] and raw['positiveVolumeM3']>0
 rows.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'passive':o.get('constructionClass'),'raw':raw,'evaluatedFinite':True,'evaluatedTinyTriangleAreaLE1e14M2':zero})
lens=[]
for side in (-1,1):
 o=bpy.data.objects[f'V31 Advanced optical aperture {side}'];lens.append({'name':o.name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'absentMakerMechanic':o.get('exteriorEras')=='builder'});assert o.get('exteriorEras')=='builder'
assert all(r['eras']=='maker,mechanic,builder' for r in rows)
jaw=bpy.data.objects['jaw'];socket=json.loads(jaw['makerControlSocketV1']);p=socket['point'];local=Vector((p[0],-p[2],p[1]));world=jaw.matrix_world@local;o=bpy.data.objects[socket['surfaceObject']];ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();ps=[ev.matrix_world@v.co for v in m.vertices];tree=BVHTree.FromPolygons(ps,[tuple(t.vertices) for t in m.loop_triangles],all_triangles=True);nearest=tree.find_nearest(world);distance=nearest[3];ev.to_mesh_clear()
result={'status':'Bounded finite/owner/era/contact metadata evidence; no artistic or engineering acceptance','native':rec['native'],'moduleSHA256':rec['sourceSHA256'],'executedCheckSHA256':sha(Path(__file__)),'changedAndAddedMeshes':rows,'advancedOpticalApertures':lens,'makerJawSocket':{'record':socket,'nativeWorld':list(world),'nearestEvaluatedSurfaceDistanceM':distance,'receivingSurface':o.name,'note':'Read-only existing socket evaluated against actual changed mandibular surface; surface distance is not a load/force or motion-clearance proof.'},'newBillContactProposal':rec['result']['billContactNativeWorld'],'nativeUnchanged':sha(N)==rec['native']['sha256']};(A/'technical-check.json').write_text(json.dumps(result,indent=2)+'\n');assert result['nativeUnchanged'];print('TECHNICAL',len(rows),[(r['name'],r['raw']['connectedComponents'],r['evaluatedTinyTriangleAreaLE1e14M2']) for r in rows if r['raw']['connectedComponents']!=1 or r['evaluatedTinyTriangleAreaLE1e14M2']]);print('SOCKET',distance)
