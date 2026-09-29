"""Four discrete actual runtime-angle shoulder samples; no pair exemptions."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree
R=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');A=Path(__file__).resolve().parent
BASE=R/'assets/models/whole-character-v35/attempt-form01/murderbird-whole-character-v35.blend';NEW=R/'assets/models/whole-character-v37/regional-studies/shoulder-assembly/attempt02/murderbird-shoulder-assembly.blend'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert sha(BASE)=='d2c704ccf89f3f0e7dbeb3613dcdbdd964c4ba69991783783830803eecf59cb0';assert sha(NEW)=='b81a783070bf05d915443425a312aa7bcb86732e61de53d3a94673034c2ae51a'
receipt=json.loads((A.parent/'receipt.json').read_text());REMOVED=set(receipt['result']['removedMeshes']);ADDED=set(receipt['result']['addedMeshes']);OWNERS={'left-mantle','right-mantle','left-wing-shield','right-wing-shield'}
# Native X angle deltas match runtime local X; yaw is runtime Y/native Z.
NAMES=['breastplate','left-mantle','right-mantle','left-wing-shield','right-wing-shield'];CHAIN=['neck','cervical-mid-a','cervical-mid-b','cervical-upper']
STATES=[('rest',(0,0,0,0,0),(0,0,0,0)),('maker-wing-neck-jaw',(0,0,-.38,0,.16),(-.14,-.45,0,.32)),('guard',(0,.065,-.24,.18,.38),(0,0,0,0)),('thrust-short-shove',(0,.07,-.64,.18,.72),(-.07,0,-.035,0))]
def inside(point,tri):
    a,b,c=tri;v0=b-a;v1=c-a;v2=point-a;d00=v0.dot(v0);d01=v0.dot(v1);d11=v1.dot(v1);d20=v2.dot(v0);d21=v2.dot(v1);den=d00*d11-d01*d01
    if abs(den)<1e-18:return False
    u=(d11*d20-d01*d21)/den;v=(d00*d21-d01*d20)/den
    return min(u,v,1-u-v)>1e-6

def edge_cross(p,q,tri):
    n=(tri[1]-tri[0]).cross(tri[2]-tri[0])
    if n.length<1e-12:return False
    n.normalize();d0=n.dot(p-tri[0]);d1=n.dot(q-tri[0])
    if not(d0*d1<0 and abs(d0)>1e-7 and abs(d1)>1e-7):return False
    direction=q-p;hit=intersect_ray_tri(*tri,direction,p,True)
    if hit is None:return False
    t=(hit-p).dot(direction)/max(direction.length_squared,1e-30)
    return 1e-6<t<1-1e-6 and inside(hit,tri)


def run(path,label):
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.scene.frame_set(1)
 for o in bpy.data.objects:
  if o.animation_data:o.animation_data_clear()
 bpy.context.view_layer.update();REST={o.name:o.matrix_local.copy() for o in bpy.data.objects if o.type=='EMPTY' and not o.get('authoringGuide')}
 scope=REMOVED if label=='V35-baseline' else ADDED;rows=[]
 for state,angles,neck in STATES:
  for n,M in REST.items():bpy.data.objects[n].matrix_local=M
  for n,a in zip(NAMES,angles):bpy.data.objects[n].matrix_local=REST[n]@Matrix.Rotation(a,4,'X')
  for i,n in enumerate(CHAIN):bpy.data.objects[n].matrix_local=REST[n]@Matrix.Rotation(neck[0]*.25,4,'X')@(Matrix.Rotation(neck[1],4,'Z') if i==0 else Matrix.Identity(4))
  bpy.data.objects['head'].matrix_local=REST['head']@Matrix.Rotation(neck[2],4,'X');bpy.data.objects['jaw'].matrix_local=REST['jaw']@Matrix.Rotation(neck[3],4,'X');bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();items=[]
  for o in sorted(bpy.data.objects,key=lambda x:x.name):
   if o.type!='MESH' or o.get('authoringGuide') or not o.parent or 'builder' not in o.get('exteriorEras','maker,mechanic,builder').split(','):continue
   ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@x.co for x in m.vertices];t=[tuple(x.vertices) for x in m.loop_triangles];ev.to_mesh_clear();assert all(math.isfinite(c) for p in v for c in p),o.name
   box=[[min(p[k] for p in v),max(p[k] for p in v)] for k in range(3)];items.append((o.name,o.parent.name,o.name in scope,v,t,box,BVHTree.FromPolygons(v,t,all_triangles=True)))
  pairs=[];tested=0
  for i,a in enumerate(items):
   for b in items[i+1:]:
    if not(a[2] or b[2]):continue
    tested+=1
    if any(a[5][k][1]<b[5][k][0] or b[5][k][1]<a[5][k][0] for k in range(3)):continue
    for ai,bi in a[6].overlap(b[6]):
     av=[a[3][j] for j in a[4][ai]];bv=[b[3][j] for j in b[4][bi]]
     if any(edge_cross(av[k],av[(k+1)%3],bv) or edge_cross(bv[k],bv[(k+1)%3],av) for k in range(3)):
      pairs.append({'a':a[0],'b':b[0],'owners':[a[1],b[1]],'sameOwner':a[1]==b[1],'triangleIndices':[ai,bi],'witnessTriangles':[[list(p) for p in av],[list(p) for p in bv]],'centroid':list(sum(av+bv,Vector())/6),'overlapBounds':[[max(a[5][k][0],b[5][k][0]),min(a[5][k][1],b[5][k][1])] for k in range(3)]});break
  row={'pose':state,'nativeLocalXAngles':dict(zip(NAMES,angles)),'neckPitchYawHeadJaw':neck,'scopeMeshes':sum(a[2] for a in items),'visibleMeshes':len(items),'testedCombinations':tested,'strictPairCount':len(pairs),'interownerPairCount':sum(not p['sameOwner'] for p in pairs),'pairs':pairs};rows.append(row);print(label,state,len(pairs),row['interownerPairCount'],flush=True)
 return {'nativeSHA256':sha(path),'rows':rows}
result={'status':'Bounded proposed-surface interference screen; no whole-art or clearance acceptance','sourceSHA256':sha(__file__),'base':run(BASE,'V35-baseline'),'candidate':run(NEW,'V37-attempt02'),'method':'Unchanged frozen strict edge-through-face kernel: plane epsilon1e-7m, barycentric/edge1e-6. First witness per identity; all same/interowner pairs included, no exemptions.','scope':'All removed124 V35 source shoulder/scapular meshes vs all builder-visible meshes; all added V37 construction meshes vs all builder-visible meshes. Distinct geometry sets have distinct names: baseline/candidate counts are not direct defect-count deltas.','limits':['Four discrete runtime-angle poses only; no continuous movement/physics claim.','New geometry identities are explicitly new, even where functions replace prior parts; no automatic inherited-contact attribution from counts.','No intramesh self-intersection, containment/tangent/coplanar or force/load proof.']}
(A/'screen.json').write_text(json.dumps(result,indent=2)+'\n')
