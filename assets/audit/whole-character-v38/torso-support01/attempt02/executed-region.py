"""Second/final: four owner-local finite bearing/service reliefs; no exterior forming."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
YOKES=[f'V38 curved-neck formed yoke neck {s}'for s in(-1,1)]
SCAP=[f'V35 scapular receiving plate {s} 0'for s in(-1,1)]
CHAIN=['neck','cervical-mid-a','cervical-mid-b','cervical-upper']
def components(mesh):
 links=[set()for _ in mesh.vertices]
 for e in mesh.edges:a,b=e.vertices;links[a].add(b);links[b].add(a)
 unseen=set(range(len(links)));sizes=[]
 while unseen:
  todo=[unseen.pop()];count=0
  while todo:
   i=todo.pop();count+=1
   for j in links[i]&unseen:unseen.remove(j);todo.append(j)
  sizes.append(count)
 return sorted(sizes,reverse=True)
def stat(o):
 bm=bmesh.new();bm.from_mesh(o.data);r={'components':components(o.data),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'signedVolumeM3':bm.calc_volume(signed=True)};bm.free();return r
def surface(o):
 o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(t.vertices)for t in o.data.loop_triangles],all_triangles=True,epsilon=0)
def apply():
 bpy.context.view_layer.update();saved={o.name:o.matrix_basis.copy()for o in bpy.data.objects if o.type=='EMPTY'};restWorld={o.name:o.matrix_world.copy()for o in bpy.data.objects if o.type=='EMPTY'};sourceContract=json.loads((ROOT/'assets/audit/whole-character-v38/torso-support01/receipt.json').read_text())['contract'];capMap={x['name']:x for x in sourceContract['compactNeckYokeLandings']};records=[]
 def restore():
  for n,m in saved.items():bpy.data.objects[n].matrix_basis=m.copy()
  bpy.context.view_layer.update()
 def tool_geometry(name,pose,target):
  restore()
  if pose=='capturedPitchSlice':
   for n in CHAIN:o=bpy.data.objects[n];o.matrix_basis=o.matrix_basis@Matrix.Rotation(.10675220489501955,4,'X')
   o=bpy.data.objects['head'];o.matrix_basis=o.matrix_basis@Matrix.Rotation(-.5090505059024657,4,'X')
  elif isinstance(pose,tuple):
   o=bpy.data.objects[pose[0]];o.matrix_basis=o.matrix_basis@Matrix.Rotation(pose[1],4,'X')
  bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();source=bpy.data.objects[name];ev=source.evaluated_get(dg);m=ev.to_mesh();normal=ev.matrix_world.to_3x3().inverted().transposed();posedWorld=[ev.matrix_world@v.co for v in m.vertices];posedOffset=[p+.003*(normal@v.normal).normalized()for p,v in zip(posedWorld,m.vertices)];f=[tuple(p.vertices)for p in m.polygons];ev.to_mesh_clear();owner=target.parent.name;posedOwner=bpy.data.objects[owner].matrix_world.copy();change=restWorld[owner]@posedOwner.inverted();v=[change@p for p in posedOffset];restore();return v,f
 def subtract(target,source,pose):
  o=bpy.data.objects[target];v,f=tool_geometry(source,pose,o);m=bpy.data.meshes.new('finite actual source bearing relief tool');m.from_pydata(v,[],f);m.update();temp=bpy.data.objects.new(m.name,m);bpy.context.scene.collection.objects.link(temp);bpy.context.view_layer.update();before=stat(o);original=o.data.copy();q=o.modifiers.new('Actual owner-local finite service relief','BOOLEAN');q.operation='DIFFERENCE';q.solver='EXACT';q.object=temp
  with bpy.context.temp_override(object=o,active_object=o,selected_objects=[o],selected_editable_objects=[o]):bpy.ops.object.modifier_apply(modifier=q.name)
  empty=len(o.data.vertices)==0
  if empty:o.data=original
  after=stat(o);bpy.data.objects.remove(temp,do_unlink=True);return {'source':source,'pose':pose,'toolBoundsM':[[min(p[i]for p in v),max(p[i]for p in v)]for i in range(3)],'toolVertices':len(v),'toolFaces':len(f),'vertexNormalExpansionM':.003,'nominalClearanceNotConstantOffset':True,'beforeStock':before,'afterStock':after,'emptyStockResultRestoredAsFailedCope':empty,'oneDeclaredCopeNoOffsetSearch':True}
 for side,name in zip((-1,1),YOKES):
  o=bpy.data.objects[name];before=stat(o);cuts=[]
  # Actual captive shaft and adjacent rigid stage sampled relative to this
  # neck owner's rest frame, rather than treating them as static world stock.
  for source in ['V23 cervical 1 captive pin',f'V23 cervical 2 load link {side}',f'V38 curved-neck formed yoke cervical-mid-a {side}']:
   for pose in('neutral','capturedPitchSlice'):cuts.append(subtract(name,source,pose))
  cuts.append(subtract(name,f'V23 cervical 1 distal race {side}','neutral'));cap=capMap[name];t=surface(o);anchors=[]
  for label,key in [('frame','actualRootLoopWorld'),('guard','actualEndLoopWorld')]:
   p=[Vector(x)for x in cap[key]];d=[t.find_nearest(x)[3]if t.find_nearest(x)[0]is not None else None for x in p];anchors.append({'cap':label,'originalActualCornersWorld':cap[key],'postReliefSurfaceDistanceM':d,'allOriginalCornersRetainedWithin1Micrometre':all(x is not None and x<1e-6 for x in d),'qualification':'Finite four corner retention, not remaining continuous cap area or physical joint certificate.'})
  records.append({'name':name,'owner':o.parent.name,'beforeStock':before,'afterStock':stat(o),'reliefs':cuts,'sourceAnchorRetention':anchors})
 for side,name in zip((-1,1),SCAP):
  label='right'if side<0 else'left';o=bpy.data.objects[name];before=stat(o);source=label+' oblique shoulder saddle v4';owner=label+'-mantle';angles=[0,-.24,-.64]if side<0 else[0,.07];cuts=[subtract(name,source,(owner,a))for a in angles];records.append({'name':name,'owner':o.parent.name,'beforeStock':before,'afterStock':stat(o),'reliefs':cuts,'sourceAnchorQualification':'All uncut vertices/surfaces remain actual first support source stock; Boolean apertures may reduce original near-seat footprint. No full shoulder anchoring/seating claim.'})
 restore()
 for name in YOKES+SCAP:
  o=bpy.data.objects[name];o['supportReliefHistory']=json.dumps({'constructionDescription':o.get('constructionDescription'),'geometryStatus':o.get('geometryStatus')},separators=(',',':'));o['constructionDescription']='Second bounded owner-local bearing/service relief of first support stock using actual finite shaft/nextjoint/saddle samples.3mm vertex-normal tools are nominal, not constant-offset/swept certificate. Original torso exterior and all unrelated support placements exact; component/anchor losses reported, not waived.';o['geometryStatus']='Torso-support01 attempt02 final finite relief proposal; HOLD if anchor/stock/regression evidence fails';o['torsoSupportRevision']='torso-support01-attempt02'
 return {'changedMeshes':YOKES+SCAP,'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'watchMeshes':YOKES+SCAP,'finiteOwnerLocalReliefs':records,'construction':'Only two compact neck yokes and two scapular receiving plates receive explicit actual-source bearing corridors; no arbitrary member shift, whole-body forming, exterior carve or material change.','protected':'All33 first torso exterior plates, currentbody support placement/receiving unions/guard free laps/returns, every pivot/rest/hierarchy/era/material/profile unchanged.','limits':['One declared finite stock cut sequence per support; no clearance offset search or third attempt.','Vertex-normal tools do not guarantee3mm perpendicular clearance or continuous swept volume.','Connected components and actual source cap-corner retention reported; loss makes HOLD, not inferred seat approval.','Scapular relief uncut source surfaces retained, but complete near-seat cap area not independently validated.','Captured pitch slice applied owner-relative at body rest; not full captured strike with yaw/roll/body/legs.','All fixed sameowner and inherited crossings remain counted; no engineering or owner acceptance.']}
