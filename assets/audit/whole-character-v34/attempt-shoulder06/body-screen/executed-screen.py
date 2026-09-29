from pathlib import Path
import bpy, json, hashlib, math
from mathutils import Vector, Matrix
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree
ROOT = Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
OUT = Path(__file__).parent
BASE = ROOT / 'assets/models/whole-character-v33/attempt-form06/murderbird-whole-character-v33.blend'
NATIVE = ROOT / 'assets/models/whole-character-v34/attempt-shoulder06/murderbird-whole-character-v34.blend'
RECEIPT = ROOT / 'assets/audit/whole-character-v34/attempt-shoulder06/receipt.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
BASE_SHA = '5fdfe66693db848fcf624b28484c3eaba220a8d7f389248390a4f21a571d108d'
NATIVE_SHA = '1e5f4d93ae2ed4986eb0fff4b10bfa1c4512db9b180b9bff5ce9fab1643aa0eb'
assert sha(BASE) == BASE_SHA and sha(NATIVE) == NATIVE_SHA
receipt = json.loads(RECEIPT.read_text())
assert receipt['base']['sha256'] == BASE_SHA and receipt['native']['sha256'] == NATIVE_SHA
changed = {x['name'] for reg in receipt['regions'] for x in reg['result'].get('changedMeshes', [])}
assert len(changed) == 84
PIVOTS = ['breastplate', 'left-mantle', 'right-mantle', 'left-wing-shield', 'right-wing-shield']
STATES = [
 ('closed-folded',0,0,0,0,0),
 ('opening-25-folded',.275,0,0,0,0),
 ('opening-50-folded',.55,0,0,0,0),
 ('opening-75-folded',.825,0,0,0,0),
 ('opening-100-folded',1.1,0,0,0,0),
 ('closed-guard',0,.065,-.24,.18,.38),
 ('closed-short-shove',0,.07,-.64,.18,.72),
]
def inside(p, tri):
 a,b,c=tri; v0=b-a; v1=c-a; v2=p-a; d00=v0.dot(v0); d01=v0.dot(v1); d11=v1.dot(v1); d20=v2.dot(v0); d21=v2.dot(v1); den=d00*d11-d01*d01
 if abs(den)<1e-18:return False
 u=(d11*d20-d01*d21)/den; v=(d00*d21-d01*d20)/den
 return min(u,v,1-u-v)>1e-6
def edge(p,q,tri):
 n=(tri[1]-tri[0]).cross(tri[2]-tri[0])
 if n.length<1e-12:return False
 n.normalize(); d0=n.dot(p-tri[0]); d1=n.dot(q-tri[0])
 if not(d0*d1<0 and abs(d0)>1e-7 and abs(d1)>1e-7):return False
 direction=q-p; hit=intersect_ray_tri(*tri,direction,p,True)
 if hit is None:return False
 t=(hit-p).dot(direction)/max(direction.length_squared,1e-30)
 return 1e-6<t<1-1e-6 and inside(hit,tri)
def evaluated(obj,dg):
 ev=obj.evaluated_get(dg); mesh=ev.to_mesh(); mesh.calc_loop_triangles()
 verts=[ev.matrix_world@v.co for v in mesh.vertices]; tris=[tuple(t.vertices) for t in mesh.loop_triangles]; ev.to_mesh_clear()
 assert all(math.isfinite(c) for p in verts for c in p),obj.name
 bounds=[[min(p[k] for p in verts),max(p[k] for p in verts)] for k in range(3)]
 return (obj.name,obj.parent.name if obj.parent else '<world>',bounds,verts,tris,BVHTree.FromPolygons(verts,tris,all_triangles=True))
def run_stage(path,stage):
 bpy.ops.wm.open_mainfile(filepath=str(path)); scene=bpy.context.scene; scene.frame_set(1)
 for obj in bpy.data.objects:
  if obj.animation_data:obj.animation_data_clear()
 bpy.context.view_layer.update()
 missing=sorted(changed-set(bpy.data.objects.keys()))
 assert not missing, f'{stage}: changed mesh names missing: {missing}'
 for pivot in PIVOTS: assert pivot in bpy.data.objects, f'{stage}: missing pivot {pivot}'
 eligible=sorted([o for o in bpy.data.objects if o.type=='MESH' and 'builder' in o.get('exteriorEras','maker,mechanic,builder').split(',')],key=lambda o:o.name)
 assert len(eligible)>=500, (stage,len(eligible))
 rest={n:bpy.data.objects[n].matrix_local.copy() for n in PIVOTS}
 poses=[]
 for state in STATES:
  name=state[0]
  for pivot,angle in zip(PIVOTS,state[1:]):bpy.data.objects[pivot].matrix_local=rest[pivot]@Matrix.Rotation(angle,4,'X')
  bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get(); items=[evaluated(o,dg) for o in eligible]
  pairs=[]; candidate_mesh_pair_count=0; strict_triangle_pair_total=0; same_owner_pair_count=0; different_owner_pair_count=0
  for i,a in enumerate(items):
   for b in items[i+1:]:
    if a[0] not in changed and b[0] not in changed:continue
    if any(a[2][k][1]<b[2][k][0] or b[2][k][1]<a[2][k][0] for k in range(3)):continue
    hits=0; first=None; candidates=a[5].overlap(b[5])
    if candidates:candidate_mesh_pair_count+=1
    for ia,ib in candidates:
     A=[a[3][n] for n in a[4][ia]];B=[b[3][n] for n in b[4][ib]]
     if any(edge(A[k],A[(k+1)%3],B) or edge(B[k],B[(k+1)%3],A) for k in range(3)):
      hits+=1
      if first is None:first={'triangleIndices':[ia,ib],'aTriangleWorld':[[round(c,7) for c in p] for p in A],'bTriangleWorld':[[round(c,7) for c in p] for p in B],'combinedCentroidWorld':[round(c,7) for c in sum(A+B,Vector())/6]}
    if hits:
     strict_triangle_pair_total+=hits
     same=a[1]==b[1]
     if same:same_owner_pair_count+=1
     else:different_owner_pair_count+=1
     pairs.append({'meshA':a[0],'meshB':b[0],'owners':[a[1],b[1]],'changedMeshA':a[0] in changed,'changedMeshB':b[0] in changed,'ownerRelation':'same-owner' if same else 'different-owner','strictTrianglePairs':hits,'firstWitness':first})
  poses.append({'pose':name,'breastplateLocalXRad':state[1],'mantleAndWingAnglesRad':dict(zip(PIVOTS[1:],state[2:])),'eligibleMeshCount':len(items),'changedMeshCount':len(changed),'bvhCandidateMeshPairCount':candidate_mesh_pair_count,'strictPairCount':len(pairs),'strictTrianglePairCount':strict_triangle_pair_total,'sameOwnerPairCount':same_owner_pair_count,'differentOwnerPairCount':different_owner_pair_count,'pairs':pairs})
  print(stage,name,len(pairs),same_owner_pair_count,different_owner_pair_count,flush=True)
 return {'nativeSHA256':sha(path),'stage':stage,'changedMeshNames':sorted(changed),'poses':poses}
base_result=run_stage(BASE,'V33-Form06-base')
candidate_result=run_stage(NATIVE,'V34-shoulder06')
for base_pose,candidate_pose in zip(base_result['poses'],candidate_result['poses']):
 old={tuple(sorted((p['meshA'],p['meshB']))) for p in base_pose['pairs']}
 new={tuple(sorted((p['meshA'],p['meshB']))) for p in candidate_pose['pairs']}
 for p in candidate_pose['pairs']:p['pairIdentityInBase']=tuple(sorted((p['meshA'],p['meshB']))) in old
 candidate_pose['inheritedPairIdentityCount']=len(old&new)
 candidate_pose['newPairIdentityCount']=len(new-old)
 candidate_pose['resolvedPairIdentityCount']=len(old-new)
result={'status':'Read-only seven-pose changed-region/adjacent-neighbor strict crossing screen','baseNativePath':str(BASE.relative_to(ROOT)),'baseNativeSHA256':BASE_SHA,'candidateNativePath':str(NATIVE.relative_to(ROOT)),'candidateNativeSHA256':NATIVE_SHA,'compositionReceiptPath':str(RECEIPT.relative_to(ROOT)),'compositionReceiptSHA256':sha(RECEIPT),'executedScreenSHA256':sha(Path(__file__)),'strictMethodSourceSHA256':sha(OUT/'strict-method-source.py'),'method':'Copied V30 body-screen strict edge-through-face kernel: evaluated world-space BVH candidates followed by strict triangle edge crossing through triangle interior; plane epsilon 1e-7 m, barycentric/edge margin 1e-6. Bounds used only to prune disjoint objects. Same-owner pairs are reported separately, not suppressed. Same discrete breast opening, guard and shove angles as V30 body-screen.', 'scope':'All builder-era eligible meshes in each exact native; every pair with at least one of the 90 changed mesh names tested against all other eligible mesh names. Same-owner distinct meshes included and categorized. The exact V33 Form06 baseline is run at the same seven states for inherited/new/resolved pair identity comparison. Does not test intra-mesh self-intersection, containment, coplanar/tangent contacts, continuous motion, or whole-controller actions.', 'base':base_result,'candidate':candidate_result,'nativeUnchanged':sha(BASE)==BASE_SHA and sha(NATIVE)==NATIVE_SHA}
assert result['nativeUnchanged']
(OUT/'screen.json').write_text(json.dumps(result,indent=2)+'\n')
print('COMPLETE',[(p['pose'],p['strictPairCount'],p['newPairIdentityCount'],p['inheritedPairIdentityCount'],p['resolvedPairIdentityCount']) for p in candidate_result['poses']],flush=True)
