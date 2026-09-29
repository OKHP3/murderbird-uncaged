from pathlib import Path
import json,hashlib,shutil
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');PKT=ROOT/'assets/audit/whole-character-v30/regional-studies/breast-form';TMP=Path('/tmp/v30-breast-form/coarse03');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((PKT/'preservation-manifest.json').read_text())
for f in old['files']:assert sha(PKT/f['path'])==f['sha256'],f['path']
source=ROOT/'scripts/regions/whole-character-v30-breast-form.py';assert sha(source)==sha(TMP/'executed-region.py')=='1aa3cde91888ceb4be5a42741c412b7eb3c825c1fd71ead5311f5870b0ccd90a'
assert sha(TMP/'murderbird-v30-breast-form.blend')=='f90d8f9176db62e007f7a578f23f388004f6cdf4b71f49a1016ff2b5cdda9969'
DST=PKT/'coarse03';assert not DST.exists();shutil.copytree(TMP,DST)
for p in ['build-coarse03.log','screen-coarse03.log','render-open-coarse03.log']:shutil.copyfile(TMP.parent/p,DST/p)
shutil.copyfile(Path(__file__),DST/'executed-preservation.py')
receipt=json.loads((DST/'receipt.json').read_text());x=json.loads((DST/'screen/screen.json').read_text());prior=json.loads((PKT/'coarse02/screen/screen.json').read_text())
summary=[]
for a,b,c in zip(x['stages']['baseline'],prior['stages']['body02'],x['stages']['body03']):
 assert c['newExactPairIdentityCount']==0 and c['skinPairCount']==0 and c['hingePairCount']==0
 summary.append({'pose':c['pose'],'basePairs':a['strictPairCount'],'body02Pairs':b['strictPairCount'],'body03Pairs':c['strictPairCount'],'body02NewPairs':b['newExactPairIdentityCount'],'body03NewPairs':c['newExactPairIdentityCount'],'body03CompleteBreastPairs':c['completeBreastPairCount'],'body03InheritedPairs':[{'a':p['a'],'b':p['b'],'owners':p['owners'],'triangleWitnesses':p['triangleWitnesses']} for p in c['pairs']]})
record={'status':'Coarse03 frozen provisional contour proposal; zero introduced identities in seven sampled poses, remaining inherited failures retained','baseNativeSha256':x['baseNativeSha256'],'candidateNativeSha256':x['candidateNativeSha256'],'sourceSha256':x['sourceSha256'],'scope':x['scope'],'limits':x['limits']+['Root neck directional-guard sweep is authored receiving geometry, not a separate measured neck-motion screen.','Root composition with head03 is not in this native and requires exact composite checking.'],'comparison':summary,'attachments':receipt['result']['attachments'],'exactPreservation':{'namedNodes':54,'outsideMeshes':546,'materialsExact':True,'saveReopenExact':True},'priorAttemptsAndPriorManifestUnchanged':True}
(PKT/'coarse03-inheritance-and-fit-limits.json').write_text(json.dumps(record,indent=2)+'\n')
rows='\n'.join('| '+p['pose']+' | '+str(p['basePairs'])+' | '+str(p['body02Pairs'])+' | '+str(p['body03Pairs'])+' | '+str(p['body03NewPairs'])+' |' for p in summary)
text='''# V30 breast form coarse03 frozen handoff

Coarse03 preserves the materially different continuous, substantial upper breast/shoulder contour, lower taper and longitudinal plate hierarchy from coarse02. It adds actual receiving spaces around the root-neck guards, moving returns, shoulder saddles and fixed lower sternal/root members. The silhouette is not globally reduced, and no neighboring machinery is hidden or altered. Actual closed whole/front/side and full-open whole/front/side/closeup views are in `coarse03/`; these remain an editable inferred construction proposal pending root visual and owner review.

Eighteen original skins are replaced with twelve formed skins and two finite C-section receiving tabs. Original V29 breast seats/forks/shaft, moving returns, named pivot transforms, original era machinery and outside geometry remain exact. Tabs connect actual preserved rear webs to actual evaluated liner surfaces; post-relief endpoint-to-surface distances are approximately 7.45e-9 m and 0 m. This is geometric seating, not an engineering or physics claim. All fourteen evaluated new solids have finite coordinates, closed manifold edges, positive signed volume and no loose vertices. Fifty-four named nodes and 546 outside mesh records, original material definitions and save/reopen snapshot remain exact.

## Same bounded screen

Exact V29 Fit01 and body03 use the preserved strict evaluated triangle-edge/interior checker, checking all eligible builder-era neighbors regardless saved display hiding. Five complete breast openings (0, .275, .55, .825, 1.1 radians), closed breast with guard, and closed breast with short shove are the same seven states used for body02. Neck/head/legs remain the original V29 neutral rest; no rejected stance or concurrent head study is composed.

| Pose | V29 pairs | Body02 pairs | Body03 pairs | Body03 new identities |
|---|---:|---:|---:|---:|
'''+rows+'''

New-skin, complete-breast and preserved-hinge pair counts are zero in every sample. The remaining 38 identities (37 at short shove) are exact unchanged inherited shoulder/elbow load-chain/strap/canopy witnesses, not exempted or cleared by this change. Their exact names, owners and witness counts are in `coarse03-inheritance-and-fit-limits.json`; triangle coordinates and checker parameters are in `coarse03/screen/screen.json`. Every body02 introduced identity is absent in these body03 samples.

Seven discrete poses do not prove continuous collision, contained-overlap clearance, physics or whole-controller behavior. Same-owner crossings are excluded. The root-neck sweep is authored receiving space derived from actual evaluated guards and scoped pitch/yaw samples; moving-neck behavior was not independently screened here. The composed head03/body03 model is a different native and needs its own exact input binding. No art or engineering acceptance is asserted.

## Preservation and integration

Coarse01 and coarse02, their evidence and the original preservation manifest remain byte-exact. `coarse03-preservation-manifest.json` binds the new continuation package with relative paths and checked SHA256 values. Original reference binaries remain under source-relative `references/` paths; exact V29 input remains hash-referenced at its canonical path, not duplicated. No private files are included and no commit was made.

Frozen source: `scripts/regions/whole-character-v30-breast-form.py` SHA256 `1aa3cde91888ceb4be5a42741c412b7eb3c825c1fd71ead5311f5870b0ccd90a`.
Frozen native: `coarse03/murderbird-v30-breast-form.blend` SHA256 `f90d8f9176db62e007f7a578f23f388004f6cdf4b71f49a1016ff2b5cdda9969`.
Base V29 Fit01 SHA256 `04040543c39e98dd3d20da3d51a5ba40fd87151315ef074d328276eed97c63e7`.

This continuation supersedes the old coarse02 handoff's final-source pointer; that historical handoff is intentionally preserved unchanged. Root should apply this module on original V29 rest before any separately approved composition changes. The module returns exact removed/added names, receiving-envelope construction records, attachment endpoints and structural limits; it does not edit head, neck, wings, journals, legs, feet, runtime or root builder.
'''
(PKT/'coarse03-handoff.md').write_text(text)
files=[]
for p in sorted(DST.rglob('*')):
 if p.is_file():files.append({'path':p.relative_to(PKT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size})
for n in ['coarse03-inheritance-and-fit-limits.json','coarse03-handoff.md']:p=PKT/n;files.append({'path':n,'sha256':sha(p),'bytes':p.stat().st_size})
manifest={'status':'Frozen body03 provisional construction; zero introduced pairs in scoped seven-pose diagnostic, unchanged inherited failures retained','sourceModulePath':source.relative_to(ROOT).as_posix(),'sourceModuleSha256':sha(source),'nativePath':'coarse03/murderbird-v30-breast-form.blend','nativeSha256':sha(DST/'murderbird-v30-breast-form.blend'),'baseNativeReference':old['baseNativeReference'],'priorManifestSha256':sha(PKT/'preservation-manifest.json'),'priorManifestFilesRechecked':len(old['files']),'files':files,'relativePathsChecked':True,'rootCompositionNotIncluded':True}
(PKT/'coarse03-preservation-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
for f in files:assert sha(PKT/f['path'])==f['sha256']
for f in old['files']:assert sha(PKT/f['path'])==f['sha256']
print('FROZEN',len(files),'new files;',len(old['files']),'prior hashes rechecked; manifest',sha(PKT/'coarse03-preservation-manifest.json'))
