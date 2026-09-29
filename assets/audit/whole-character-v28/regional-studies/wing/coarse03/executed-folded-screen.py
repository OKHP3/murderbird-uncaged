from pathlib import Path
import bpy,runpy,json,hashlib,shutil,time
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=Path('/tmp/v28-wing-terminal/coarse03');BASE=ROOT/'assets/models/whole-character-v27/attempt-form01/murderbird-whole-character-v27.blend';NATIVE=OUT/'murderbird-v28-wing-canopy-smooth.blend';helper=ROOT/'assets/audit/whole-character-v25/rejected-neck-source-screen/baseline.py';shutil.copyfile(Path(__file__),OUT/'executed-folded-screen.py');tools=runpy.run_path(str(helper),run_name='tooling');OWNERS=['left-mantle','right-mantle','left-wing-shield','right-wing-shield'];receipt=json.loads((OUT/'receipt.json').read_text());fresh=set(receipt['result']['added']+receipt['result']['changedMeshes']);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def screen(state,rest):
 for n,a in zip(OWNERS,state[1:]):bpy.data.objects[n].matrix_local=rest[n]@Matrix.Rotation(a,4,'X')
 bpy.context.view_layer.update();items=[]
 for o in bpy.data.objects:
  if o.type!='MESH' or not o.parent or 'builder' not in o.get('exteriorEras','maker,mechanic,builder').split(','):continue
  ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@p.co for p in m.vertices];t=[tuple(p.vertices) for p in m.loop_triangles];ev.to_mesh_clear();items.append((o.name,o.parent.name,tools['bounds'](v),v,t,BVHTree.FromPolygons(v,t,all_triangles=True)))
 pairs=[];wingnames={p[0] for p in items if p[1] in OWNERS}
 for i,a in enumerate(items):
  for b in items[i+1:]:
   if a[1]==b[1] or not(a[0] in wingnames or b[0] in wingnames) or any(a[2][1][k]<b[2][0][k] or b[2][1][k]<a[2][0][k] for k in range(3)):continue
   hits=0;first=None
   for x,y in a[5].overlap(b[5]):
    A=[a[3][n] for n in a[4][x]];B=[b[3][n] for n in b[4][y]]
    if tools['straddle'](A,B) and tools['straddle'](B,A):
     hits+=1
     if first is None:first={'aTriangle':[[round(c,6) for c in p] for p in A],'bTriangle':[[round(c,6) for c in p] for p in B]}
   if hits:pairs.append({'a':a[0],'b':b[0],'owners':[a[1],b[1]],'strictTriangleWitnesses':hits,'changedGeometryInvolved':a[0] in fresh or b[0] in fresh,'firstWitness':first})
 print('POSE_READY',state[0],len(pairs),flush=True);return {'pose':state[0],'wingAnglesRad':list(state[1:]),'strictPairCount':len(pairs),'pairs':pairs,'builderVisibleMeshCount':len(items),'wingMeshCount':len(wingnames)}
result={'status':'bounded strict cross-owner sampled geometry diagnostic; not clearance/physics approval','sourceSha256':receipt['sourceSha256'],'nativeSha256':sha(NATIVE),'baseSha256':sha(BASE),'poseScope':'Native rest-relative wing angles, neutral body; all builder-visible mesh neighbors including body/breastplate/legs checked; one additional folded sample.','limitations':['Strict surface triangle crossing diagnostic does not prove continuous clearance or wholly contained-solid overlap.','No engineering motion/attachment acceptance or full runtime body action claimed.'],'stages':{}}
for stage,p in [('before',BASE),('after',NATIVE)]:
 bpy.ops.wm.open_mainfile(filepath=str(p));rest={n:bpy.data.objects[n].matrix_local.copy() for n in OWNERS}
 for o in bpy.data.objects:
  if o.animation_data:o.animation_data_clear()
 result['stages'][stage]=[screen(s,rest) for s in [('folded',0,0,0,0)]]
 (OUT/'folded-cross-owner-screen.json').write_text(json.dumps(result,indent=2)+'\n')
for before,after in zip(result['stages']['before'],result['stages']['after']):
 old={tuple(sorted((p['a'],p['b']))) for p in before['pairs']};after['retainedInheritedPairCount']=sum(tuple(sorted((p['a'],p['b']))) in old for p in after['pairs']);after['changedGeometryPairCount']=sum(p['changedGeometryInvolved'] for p in after['pairs']);groups={}
 for p in after['pairs']:
  k=' / '.join(sorted(p['owners']));groups[k]=groups.get(k,0)+1
 after['ownerPairCounts']=groups
(OUT/'folded-cross-owner-screen.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps([{'pose':p['pose'],'pairs':p['strictPairCount'],'changedGeometryPairs':p['changedGeometryPairCount'],'ownerPairs':p['ownerPairCounts']} for p in result['stages']['after']]),flush=True)
