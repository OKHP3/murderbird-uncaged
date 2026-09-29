from pathlib import Path
import bpy,runpy,json,hashlib,shutil,math
from mathutils import Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=Path('/tmp/v29-wing-interface/coarse01');NATIVE=OUT/'murderbird-v29-wing-interface.blend';SRC=OUT/'executed-region.py';HELPER=ROOT/'assets/audit/whole-character-v28/attempt-v28V29coarse01/wing-screen/executed-cross-owner-helper.py';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();nativehash=sha(NATIVE);sourcehash=sha(SRC);assert nativehash=='043c9510f03d87327cc14ab69ec5953e3ee8d6b7b383673f293f0b0fa7a84f0e';assert sourcehash=='e628450f303597f14435132dc3b5afa93069c1437db8f57b2e358f53d5941341'
for p,n in [(Path(__file__),'executed-fit-screen.py'),(HELPER,'executed-cross-owner-helper.py'),(SRC,'executed-interface-screen-region.py')]:shutil.copyfile(p,OUT/n)
tools=runpy.run_path(str(OUT/'executed-cross-owner-helper.py'),run_name='tooling');OWNERS=['left-mantle','right-mantle','left-wing-shield','right-wing-shield'];regional=json.loads((OUT/'receipt.json').read_text());fresh=set(regional['result']['added']+regional['result']['changedMeshes']);PRIOR=ROOT/'assets/audit/whole-character-v28/attempt-form02/wing-screen/receipt.json';prior=json.loads(PRIOR.read_text());priorposes={p['pose']:p for p in prior['poses']}
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
   if hits:pairs.append({'a':a[0],'b':b[0],'owners':[a[1],b[1]],'strictTriangleWitnesses':hits,'interfaceChangedGeometryInvolved':a[0] in fresh or b[0] in fresh,'firstWitness':first})
 groups={}
 for p in pairs:
  k=' / '.join(sorted(p['owners']));groups[k]=groups.get(k,0)+1
 old={tuple(sorted((p['a'],p['b']))) for p in priorposes[state[0]]['pairs']};now={tuple(sorted((p['a'],p['b']))) for p in pairs}
 return {'pose':state[0],'wingAnglesRad':dict(zip(OWNERS,state[1:])),'strictPairCount':len(pairs),'pairs':pairs,'allEvaluatedMeshesFinite':True,'eraEligibleMeshCount':len(items),'wingMeshCount':len(wingnames),'ownerPairCounts':groups,'interfaceChangedGeometryPairCount':sum(p['interfaceChangedGeometryInvolved'] for p in pairs),'priorV28Form02PairCount':priorposes[state[0]]['strictPairCount'],'pairIdentitiesAbsentFromV28Form02':[list(k) for k in sorted(now-old)],'v28V29coarse01PairIdentitiesAbsentFromV29coarse01':[list(k) for k in sorted(old-now)],'identityComparisonLimit':'Names alone do not establish identical crossing witnesses; coverage geometry changed from V28Form02 to V29coarse01.'}
result={'status':'V29 coarse01 interface on exact V28 Form02 bounded wing-neighbor strict surface-crossing diagnostic; unresolved fit, no art or full-motion pass','nativePath':str(NATIVE),'nativeSha256':nativehash,'wingSourcePath':str(SRC),'wingSourceSha256':sourcehash,'comparisonV28Form02ReceiptSha256':sha(PRIOR),'comparisonV28Form02NativeSha256':prior['nativeSha256'],'screenSourceSha256':sha(OUT/'executed-fit-screen.py'),'helperSha256':sha(OUT/'executed-cross-owner-helper.py'),'poseScope':'Three actual native rest-relative wing-owner Rx poses; composite torso/head/neck/legs remain neutral rest. No full controller body action executed.','neighborScope':'Every builder-era eligible evaluated mesh is included, regardless of saved display hiding; strict cross-owner tests require at least one actual mantle or short-shield owner. Thus adjacent body/head/neck/legs are checked wherever bounds overlap.','limitations':['Three static samples do not prove continuous collision clearance or detect all fully contained-solid overlap.','Same-owner overlaps intentionally excluded; no physics or complete attachment acceptance.','Counts include retained machinery contacts and later industrial-repair hardware; no all-pairs engineering pass inferred.','V28Form02 comparison is by exact pair identities on a different native, not a proof of identical intersection geometry.'],'poses':[]}
for state in [('folded',0,0,0,0),('guard',.065,-.24,.18,.38),('short-shove',.07,-.64,.18,.72)]:
 p=screen(state);result['poses'].append(p);(OUT/'fit-screen.json').write_text(json.dumps(result,indent=2)+'\n');print('POSE_READY',p['pose'],p['strictPairCount'],p['ownerPairCounts'],flush=True)
assert sha(NATIVE)==nativehash;assert sha(SRC)==sourcehash;result['nativeAndWingSourceUnchanged']=True;(OUT/'fit-screen.json').write_text(json.dumps(result,indent=2)+'\n')
lines=['# V29 coarse01 interface fit screen on V28 Form02','','This bounded diagnostic evaluates the exact V29coarse01 combined native and compares pair identities with exact V28Form02. No geometry or runtime source was edited; the native and frozen wing source hashes were checked before and after.','','Three native rest-relative wing poses were sampled with the composed torso/head/neck/legs at neutral rest. Every builder-era eligible evaluated mesh was included regardless of saved display hiding; tests require different rigid owners and at least one mantle/shield owner. This covers adjacent body/head/neck/legs wherever bounds overlap.','','| Pose | Strict owner-pair contacts | Involving changed V29 interface geometry |','|---|---:|---:|']
for p in result['poses']:lines.append(f"| {p['pose']} | {p['strictPairCount']} | {p['interfaceChangedGeometryPairCount']} |")
lines+=['','## V28Form02 comparison','']
for p in result['poses']:
 lines += [p['pose']+': '+str(p['priorV28Form02PairCount'])+' → '+str(p['strictPairCount'])+' strict pairs; '+str(len(p['pairIdentitiesAbsentFromV28Form02']))+' new identities and '+str(len(p['v28V29coarse01PairIdentitiesAbsentFromV29coarse01']))+' removed identities.','']
 for names in p['pairIdentitiesAbsentFromV28Form02']:lines.append('- New: `'+names[0]+'` versus `'+names[1]+'`')
 for names in p['v28V29coarse01PairIdentitiesAbsentFromV29coarse01']:lines.append('- Removed: `'+names[0]+'` versus `'+names[1]+'`')
 lines.append('')
lines+=['','## Actual identities','']
for p in result['poses']:
 lines += [f"### {p['pose']}",'', '| Part A | Part B | Triangle witnesses |','|---|---|---:|']
 for pair in p['pairs']:lines.append(f"| {pair['a']} | {pair['b']} | {pair['strictTriangleWitnesses']} |")
 lines.append('')
lines+=['## Limits','','These are strict triangle surface crossing witnesses, not collision-clearance or full-motion acceptance. Retained machinery and repaired hardware contacts remain in the report. No physical simulation, continuous sweep, complete attachment verification or likeness acceptance is claimed. No wholly contained-overlap guarantee; same-owner overlaps excluded. Exact coordinates and owner groups are in `receipt.json`.','','Native SHA256: `'+nativehash+'`','','Wing source SHA256: `'+sourcehash+'`']
(OUT/'fit-handoff.md').write_text('\n'.join(lines)+'\n');manifest={p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='fit-manifest.json'};(OUT/'fit-manifest.json').write_text(json.dumps({'nativeSha256':nativehash,'wingSourceSha256':sourcehash,'files':manifest},indent=2)+'\n')
print('FROZEN',str(OUT),flush=True)
