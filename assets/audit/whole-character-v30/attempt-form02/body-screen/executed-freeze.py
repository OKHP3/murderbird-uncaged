from pathlib import Path
import hashlib,json,shutil
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');P=ROOT/'assets/audit/whole-character-v30/attempt-form02/body-screen';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();x=json.loads((P/'screen.json').read_text());native=ROOT/'assets/models/whole-character-v30/attempt-form02/murderbird-whole-character-v30.blend';assert sha(native)==x['candidateNativeSha256']=='207e32fe640fcc5cc9d3bef7bea4e07d302ec5bc06cc6642075df144d295e275'
assert sha(P.parent/'executed-whole-character-v30-breast-form.py')==x['sourceSha256']=='1aa3cde91888ceb4be5a42741c412b7eb3c825c1fd71ead5311f5870b0ccd90a'
shutil.copyfile(P.parent/'executed-whole-character-v30-breast-form.py',P/'preserved-body03-source.py');shutil.copyfile('/tmp/v30-breast-form/screen-final-form02.log',P/'execution.log');shutil.copyfile(Path(__file__),P/'executed-freeze.py')
summary=[]
for p in x['stages']['form02']:
 assert p['newExactPairIdentityCount']==0 and p['skinPairCount']==0 and p['hingePairCount']==0 and p['completeBreastPairCount']==0
 summary.append({k:p[k] for k in ['pose','strictPairCount','skinPairCount','hingePairCount','completeBreastPairCount','exactInheritedPairIdentityCount','newExactPairIdentityCount','evaluatedEligibleMeshCount']})
bindings=[{'path':f'assets/audit/whole-character-v30/attempt-form02/{n}','sha256':sha(P.parent/n)} for n in ['receipt.json','executed-builder.py','executed-whole-character-v30-breast-form.py','executed-whole-character-v30-head-form.py','executed-whole-character-v30-support-proportion.py','executed-envelope-helper.py','executed-snapshot-helper.py']]
receipt={'status':'Exact Form02 bounded body/breast/wing-neighbor screen complete; zero introduced sampled identities, inherited witnesses retained','nativePath':native.relative_to(ROOT).as_posix(),'nativeSha256':sha(native),'baseNativePath':'assets/models/whole-character-v29/attempt-fit01/murderbird-whole-character-v29.blend','baseNativeSha256':x['baseNativeSha256'],'checkerSha256':sha(P/'executed-screen.py'),'strictHelperSha256':sha(P/'preserved-strict-method-source.py'),'bodySourceSha256':x['sourceSha256'],'sourceBindings':bindings,'scope':x['scope'],'poseSummary':summary,'limits':x['limits']+['Exact composite head03/body03/support01; rigid rest owner values are used directly from this native.','No moving-neck/head/leg or full GLB controller proof; root owns the GLB/browser diagnostic.'],'nativeAndSourcesUnchanged':True,'newLegNeighborWitnesses':0,'geometryEdits':False}
(P/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
(P/'remaining-pairs.json').write_text(json.dumps({'nativeSha256':sha(native),'poses':[{'pose':p['pose'],'pairs':[{'a':q['a'],'b':q['b'],'owners':q['owners'],'triangleWitnesses':q['triangleWitnesses'],'exactPairIdentityInherited':q['exactPairIdentityInherited']} for q in p['pairs']]} for p in x['stages']['form02']]},indent=2)+'\n')
(P/'handoff.md').write_text('''# Exact V30 Form02 body-neighbor screen

The seven-pose strict evaluated triangle-edge/interior check ran on exact head03 + body03 + support01 Form02 native SHA256 `207e32fe640fcc5cc9d3bef7bea4e07d302ec5bc06cc6642075df144d295e275`. Five full breast openings (0, .275, .55, .825, 1.1 radians), closed guard and closed short shove use actual original rigid owner rests from this native. All builder-era eligible adjacent geometry, including changed leg supports, is included regardless display hiding.

No introduced exact identities, new breast-skin pairs, complete-breast pairs, hinge-assembly pairs or new leg-neighbor witnesses appear in any of the seven samples. Total remaining pairs are 38 in the first six poses and 37 at short shove; all exact unchanged inherited identities from V29 Fit01. The body/support translation and changed leg supports introduced no tested neighbor failures. `remaining-pairs.json` lists names/owners/counts; `screen.json` retains exact triangle witnesses, source hashes and baseline results.

This is a bounded discrete native diagnostic, not continuous collision, contained-overlap clearance, full controller action, physics or art acceptance. Same-owner pairs are excluded. Neck/head/legs remain at the actual composite neutral rest while breast and wings move. Root owns actual GLB motion and browser verification. No geometry or source was edited. All three regional body trials were preserved before this test; original trial records remain unchanged.

`receipt.json` binds exact native, checker, method helper and composition source hashes. `manifest.json` binds every local screen file by checked relative path. Sources and native were rechecked unchanged after execution.
''')
files=[{'path':p.relative_to(P).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(P.rglob('*')) if p.is_file() and p.name!='manifest.json'];manifest={'status':receipt['status'],'nativeSha256':sha(native),'sourceSha256':x['sourceSha256'],'files':files,'relativePathsChecked':True};(P/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
for f in files:assert sha(P/f['path'])==f['sha256']
assert sha(native)==receipt['nativeSha256']
for f in bindings:assert sha(ROOT/f['path'])==f['sha256']
print('FROZEN',len(files),'files',sha(P/'manifest.json'));print(summary)
