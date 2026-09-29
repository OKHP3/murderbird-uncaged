from pathlib import Path
import bpy,runpy,json,hashlib,shutil,math
from mathutils import Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=ROOT/'assets/audit/whole-character-v28/attempt-form01/wing-screen';OUT.mkdir(exist_ok=False);NATIVE=ROOT/'assets/models/whole-character-v28/attempt-form01/murderbird-whole-character-v28.blend';SRC=ROOT/'assets/audit/whole-character-v28/attempt-form01/executed-whole-character-v28-wing-terminal.py';HELPER=Path('/tmp/v28-wing-terminal/coarse03/cross-owner-helper.py');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();nativehash=sha(NATIVE);sourcehash=sha(SRC);assert nativehash=='a956aa9982d3e32c79433fb68b673f0d4f23a06b4c1f70838dbe835459c0c978';assert sourcehash=='5090db2fed9e2d0569b456ddcc1593a15f65fb52ffac2646d1d27e2395dadbc7'
for p,n in [(Path(__file__),'executed-wing-screen.py'),(HELPER,'executed-cross-owner-helper.py'),(SRC,'executed-wing-region.py')]:shutil.copyfile(p,OUT/n)
tools=runpy.run_path(str(OUT/'executed-cross-owner-helper.py'),run_name='tooling');OWNERS=['left-mantle','right-mantle','left-wing-shield','right-wing-shield'];regional=json.loads(Path('/tmp/v28-wing-terminal/coarse03/receipt.json').read_text());fresh=set(regional['result']['added']+regional['result']['changedMeshes']);prior=json.loads(Path('/tmp/v28-wing-terminal/coarse03/fit-summary.json').read_text());priorposes={p['pose']:p for p in prior['poses']}
bpy.ops.wm.open_mainfile(filepath=str(NATIVE));bpy.context.scene.frame_set(1);bpy.context.view_layer.update();rest={n:bpy.data.objects[n].matrix_local.copy() for n in OWNERS}
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
def screen(state):
 for n,a in zip(OWNERS,state[1:]):bpy.data.objects[n].matrix_local=rest[n]@Matrix.Rotation(a,4,'X')
 bpy.context.view_layer.update();items=[]
 for o in bpy.data.objects:
  if o.type!='MESH' or 'builder' not in o.get('exteriorEras','maker,mechanic,builder').split(','):continue
  ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@p.co for p in m.vertices];t=[tuple(p.vertices) for p in m.loop_triangles];ev.to_mesh_clear();assert all(math.isfinite(c) for p in v for c in p),o.name;items.append((o.name,o.parent.name if o.parent else '<world>',tools['bounds'](v),v,t,BVHTree.FromPolygons(v,t,all_triangles=True)))
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
   if hits:pairs.append({'a':a[0],'b':b[0],'owners':[a[1],b[1]],'strictTriangleWitnesses':hits,'wing03ChangedGeometryInvolved':a[0] in fresh or b[0] in fresh,'firstWitness':first})
 groups={}
 for p in pairs:
  k=' / '.join(sorted(p['owners']));groups[k]=groups.get(k,0)+1
 old={tuple(sorted((p['a'],p['b']))) for p in priorposes[state[0]]['allPairs']};now={tuple(sorted((p['a'],p['b']))) for p in pairs}
 return {'pose':state[0],'wingAnglesRad':dict(zip(OWNERS,state[1:])),'strictPairCount':len(pairs),'pairs':pairs,'allEvaluatedMeshesFinite':True,'eraEligibleMeshCount':len(items),'wingMeshCount':len(wingnames),'ownerPairCounts':groups,'wing03ChangedGeometryPairCount':sum(p['wing03ChangedGeometryInvolved'] for p in pairs),'priorWing03OnV27PairCount':priorposes[state[0]]['candidateWholeWingPairCount'],'pairIdentitiesAbsentFromPriorWing03OnV27':[list(k) for k in sorted(now-old)],'priorPairIdentitiesAbsentFromComposite':[list(k) for k in sorted(old-now)],'identityComparisonLimit':'Names alone do not establish inherited geometry/witnesses; torso and proportions differ from prior wing03-on-V27 study.'}
result={'status':'exact V28 composite bounded wing-neighbor strict surface-crossing diagnostic; unresolved fit, no art or full-motion pass','nativePath':str(NATIVE.relative_to(ROOT)),'nativeSha256':nativehash,'wingSourcePath':str(SRC.relative_to(ROOT)),'wingSourceSha256':sourcehash,'screenSourceSha256':sha(OUT/'executed-wing-screen.py'),'helperSha256':sha(OUT/'executed-cross-owner-helper.py'),'poseScope':'Three actual native rest-relative wing-owner Rx poses; composite torso/head/neck/legs remain neutral rest. No full controller body action executed.','neighborScope':'Every builder-era eligible evaluated mesh is included, regardless of saved display hiding; strict cross-owner tests require at least one actual mantle or short-shield owner. Thus adjacent body/head/neck/legs are checked wherever bounds overlap.','limitations':['Three static samples do not prove continuous collision clearance or detect all fully contained-solid overlap.','Same-owner overlaps intentionally excluded; no physics or complete attachment acceptance.','Counts include retained machinery contacts and later industrial-repair hardware; no all-pairs engineering pass inferred.','Prior wing03 comparison is by exact pair identities only on a different native, not a proof of inherited intersection geometry.'],'poses':[]}
for state in [('folded',0,0,0,0),('guard',.065,-.24,.18,.38),('short-shove',.07,-.64,.18,.72)]:
 p=screen(state);result['poses'].append(p);(OUT/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print('POSE_READY',p['pose'],p['strictPairCount'],p['ownerPairCounts'],flush=True)
assert sha(NATIVE)==nativehash;assert sha(SRC)==sourcehash;result['nativeAndWingSourceUnchanged']=True;(OUT/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
lines=['# Exact V28 Form01 wing-neighbor screen','','This bounded diagnostic evaluates the exact combined native, not the earlier wing03-on-V27 study. No geometry or runtime source was edited; the native and frozen wing source hashes were checked before and after.','','Three native rest-relative wing poses were sampled with the composed torso/head/neck/legs at neutral rest. Every builder-era eligible evaluated mesh was included regardless of saved display hiding; tests require different rigid owners and at least one mantle/shield owner. This covers adjacent body/head/neck/legs wherever bounds overlap.','','| Pose | Strict owner-pair contacts | Involving wing03 changed geometry |','|---|---:|---:|']
for p in result['poses']:lines.append(f"| {p['pose']} | {p['strictPairCount']} | {p['wing03ChangedGeometryPairCount']} |")
lines+=['','## Actual identities','']
for p in result['poses']:
 lines += [f"### {p['pose']}",'', '| Part A | Part B | Triangle witnesses |','|---|---|---:|']
 for pair in p['pairs']:lines.append(f"| {pair['a']} | {pair['b']} | {pair['strictTriangleWitnesses']} |")
 lines.append('')
lines+=['## Limits','','These are strict triangle surface crossing witnesses, not collision-clearance or full-motion acceptance. Retained machinery and repaired hardware contacts remain in the report. No physical simulation, continuous sweep, complete attachment verification or likeness acceptance is claimed. No wholly contained-overlap guarantee; same-owner overlaps excluded. Exact coordinates and owner groups are in `receipt.json`.','','Native SHA256: `'+nativehash+'`','','Wing source SHA256: `'+sourcehash+'`']
(OUT/'handoff.md').write_text('\n'.join(lines)+'\n');manifest={p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='manifest.json'};(OUT/'manifest.json').write_text(json.dumps({'nativeSha256':nativehash,'wingSourceSha256':sourcehash,'files':manifest},indent=2)+'\n')
print('FROZEN',str(OUT),flush=True)
