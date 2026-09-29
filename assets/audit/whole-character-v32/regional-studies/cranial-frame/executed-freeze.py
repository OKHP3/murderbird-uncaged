from pathlib import Path
import hashlib,json,shutil
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=ROOT/'assets/audit/whole-character-v32/regional-studies/cranial-frame';C=OUT/'coarse01';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def art(p):return {'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
assert not (OUT/'manifest.json').exists();shutil.copy2(__file__,OUT/'executed-freeze.py')
I=OUT/'input-envelope-witness';I.mkdir()
for src,dest in [('inspect-envelope.py','executed-inspect-envelope.py'),('envelope-inventory.json','envelope-inventory.json'),('inventory.log','inspection.log')]:shutil.copy2(Path('/tmp/v32-cranial-frame')/src,I/dest)
for src,dest in [('build-candidate.log','coarse01/initial-driver.log'),('build-candidate-run01.log','coarse01/native-run01/driver.log'),('build-candidate-run02.log','coarse01/native-run02/driver.log'),('neck-screen.log','coarse01/neck-screen/screen.log'),('attachment-witness.log','coarse01/attachment-witness/witness.log')]:shutil.copy2(Path('/tmp/v32-cranial-frame')/src,OUT/dest)
for version,path in [('v30','assets/audit/whole-character-v30/attempt-form02/neck-screen'),('v31','assets/audit/whole-character-v31/attempt-form02/neck-screen')]:
 src=ROOT/path;shutil.copy2(src/'screen.json',C/f'{version}-baseline-screen.json');shutil.copy2(src/'executed-screen.py',C/f'{version}-baseline-validator.py')
n=json.loads((C/'neck-screen/screen.json').read_text());comparisons={}
for version in ['v30','v31']:
 b=json.loads((C/f'{version}-baseline-screen.json').read_text());rows=[]
 assert sha(C/f'{version}-baseline-validator.py')==sha(C/'neck-screen/executed-screen.py')
 for old,new in zip(b['poses'],n['poses']):
  assert old['pose']==new['pose'] and old['angles']==new['angles'];op={tuple(sorted((x['a'],x['b']))) for x in old['pairs']};np={tuple(sorted((x['a'],x['b']))) for x in new['pairs']}
  rows.append({'pose':new['pose'],'angles':new['angles'],'baselineCount':old['pairCount'],'candidateCount':new['pairCount'],'inherited':sorted(op&np),'introduced':sorted(np-op),'eliminated':sorted(op-np)})
 assert not any(row['introduced'] for row in rows)
 comparisons[version]={'baselineNativeSHA256':b['nativeSHA256'],'baselineScreenSHA256':sha(C/f'{version}-baseline-screen.json'),'sameValidatorBytes':True,'poses':rows}
comparison={'status':'Zero introduced tested identities versus V30 and V31; inherited failures remain','candidateNativeSHA256':n['nativeSHA256'],'validatorSHA256':n['sourceSHA256'],'method':n['method'],'comparisons':comparisons,'limits':['Seven discrete finite surface-crossing screens, not continuous clearance or collision proof.','Inherited neck/body and adjacent guard crossings remain actual failures, not exemptions.','Same-owner structural contacts are outside this cross-owner validator.']}
(C/'comparison.json').write_text(json.dumps(comparison,indent=2)+'\n')
build=json.loads((C/'native-run02/receipt.json').read_text());native=ROOT/build['native']['path'];region=ROOT/'scripts/regions/whole-character-v32-cranial-frame.py';assert sha(native)==n['nativeSHA256'];assert sha(region)==build['sourceSHA256'];assert sha(region)==sha(C/'executed-region.py')==sha(C/'native-run01/executed-region.py')==sha(C/'native-run02/executed-region.py')
base=ROOT/build['base']['path'];assert sha(base)==build['base']['sha256']
receipt={'status':comparison['status'],'base':art(base),'native':art(native),'regionSource':art(region),'executedRegionSource':art(C/'native-run02/executed-region.py'),'buildProof':art(C/'native-run02/receipt.json'),'attachmentProof':art(C/'attachment-witness/proof.json'),'comparison':art(C/'comparison.json'),'checks':build['checks'],'changedMeshes':build['result']['changedMeshes'],'result':{'poses':[p['pose'] for p in n['poses']],'candidatePairCounts':[p['pairCount'] for p in n['poses']],'v30PairCounts':[p['baselineCount'] for p in comparisons['v30']['poses']],'v31PairCounts':[p['baselineCount'] for p in comparisons['v31']['poses']],'introducedVsV30':0,'introducedVsV31':0,'removedFromV31':[['V23 cervical 4 directional guard 7','V31 passive cranial load bow 1'],['V23 cervical 4 directional guard 8','V31 passive cranial load bow -1']]},'limits':comparison['limits']+['One geometry candidate; no correction. The initial two proof-driver runs failed on snapshot field assumptions before native save; their exact sources/logs are preserved.','Bow upper receiving stations retained; inherited 2mm shaft-bore radial allowance and skull fastening are proposals, not engineering acceptance.','Only diagnostic frame renders omit surrounding shells. Full posed renders and saved native retain all geometry.','No runtime, app, material-definition, guard, shaft or named-rest edit; no commits.']}
(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
readme='''# V32 passive cranial frame — one bounded candidate

Reconstructed construction proposal; no owner likeness or engineering acceptance.

The V31 lower bow legs at |X|≈.10m crossed distal cervical guards7/8 only in the sampled contact pose. The new finite legs start at |X|.068m inside the side guards, move anterior to the posterior guard, and flare back to the original upper two skull receiving stations. Four existing head-owned meshes retain names, owners, transforms, properties, material slots and era tags. Seats move along the unchanged captive shaft to |X|.058–.070m, retaining .010m bore and .017m outer radius. Eight of22 sampled root-section vertices lie inside each actual annular seat; this establishes finite overlap, not a fastening/load-capacity design.

All575 outside meshes, empty-node rests and material definitions are exact. The candidate is saved/reopened exactly. Rest, Maker and contact full views were inspected; diagnostic frame-only views show the bow/shaft/guard route without changing the saved model.

Seven-pose strict counts (rest, Maker, attention, contact, thrust, yaw−, yaw+): V30 2/15/2/7/4/1/1; V31 2/14/2/9/4/1/1; V32 2/14/2/7/4/1/1. No introduced identities versus either exact baseline. Contact removes only bow1↔guard7 and bow−1↔guard8. The14 Maker and7 contact inherited pairs remain explicit in coarse01/comparison.json; this is not a neck motion pass. The one Maker identity already eliminated by V31 was guard3-10↔guard4-10 and is not credited to this frame correction.

One geometry candidate and no correction. Initial proof drivers made two incorrect assumptions about the historical snapshot helper's field shape, stopped before native saving, and are preserved with logs. `coarse01/native-run02` is the sole saved candidate. No base native duplicate, runtime/app edit or commit. `receipt.json` and `manifest.json` bind preserved sources, inputs, proof, exact native and renders; file entries use packet-relative paths.
'''
(OUT/'handoff.md').write_text(readme)
files=[{'path':p.relative_to(OUT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(OUT.rglob('*')) if p.is_file()]
manifest={'schema':1,'status':receipt['status'],'native':receipt['native'],'base':receipt['base'],'externalSource':receipt['regionSource'],'files':files,'relativePathHashesChecked':True}
assert all(sha(OUT/e['path'])==e['sha256'] for e in files);(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'sourceSHA256':sha(region),'nativeSHA256':sha(native),'receiptSHA256':sha(OUT/'receipt.json'),'manifestSHA256':sha(OUT/'manifest.json'),'fileCount':len(files),'candidateCounts':receipt['result']['candidatePairCounts']}))
