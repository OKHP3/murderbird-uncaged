from pathlib import Path
import json,hashlib,shutil
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
A=ROOT/'assets/audit/whole-character-v34/attempt-form01';H=A/'head-neck-screen';E=A/'era-integration';T=A/'export/actual-runtime-roundtrip'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
N=ROOT/'assets/models/whole-character-v34/attempt-form01/murderbird-whole-character-v34.blend';G=N.with_suffix('.glb')
assert sha(N)=='3f4c12983feea5e4d45f5609d749c1dfa78ecdafc34936d3e702ffa403fed716';assert sha(G)=='32a53dd3c26209fda81a2a6cfbc6a16080910bdf1ec73ed6b6000fec1251c41d'
for source,target in [(Path('/tmp/v34-final-head-check.log'),H/'head-check.log'),(Path('/tmp/v34-final-neck-check.log'),H/'neck-check.log'),(Path('/tmp/v34-final-era-integration.log'),E/'integration.log')]:
 
 if target.exists():assert sha(source)==sha(target)
 else:shutil.copyfile(source,target)
head=json.loads((H/'screen.json').read_text());neck=json.loads((H/'neck/screen.json').read_text());era=json.loads((E/'integration.json').read_text());trip=json.loads((T/'roundtrip-receipt.json').read_text());export=json.loads((A/'export/export-receipt.json').read_text())
assert head['nativeSHA256']==neck['nativeSHA256']==trip['nativeSHA256']==sha(N)
assert era['input']['sha256']==trip['glbSHA256']==sha(G)
assert len(head['poses'])==len(neck['poses'])==7
assert all(p['strictPairCount']==0 for p in head['poses']);assert all(p['pairCount']==0 for p in neck['poses'])
assert era['summary']['sampleCount']==66 and era['summary']['failures']==era['summary']['fitRisks']==0
for source in era['executedSources']:assert sha(ROOT/source['path'])==source['sha256']==sha(E/source['frozenPath'])
frozen=[]
for p in ['scripts/load-rigid-validation.mjs','src/scene/cervical-articulation.js','node_modules/three/package.json']:
 name='executed-'+Path(p).name;shutil.copyfile(ROOT/p,T/name);frozen.append({'path':p,'sha256':sha(ROOT/p),'frozenPath':name})
(T/'executed-export-input-receipt.json').write_bytes((A/'export/export-receipt.json').read_bytes())
# Native export input is already durable in the parent export directory; no model duplication.
(T/'executed-source-binding.json').write_text(json.dumps({'roundtripSourceSHA256':sha(T/'executed-roundtrip.mjs'),'runtimeSources':frozen,'nativeExportInput':{'path':'../native-export-input.json','sha256':sha(A/'export/native-export-input.json')},'executedCommand':'node assets/audit/whole-character-v34/attempt-form01/export/actual-runtime-roundtrip/executed-roundtrip.mjs','nativeSHA256':sha(N),'glbSHA256':sha(G),'limits':'Actual loader in-memory texture stripping; no WebGL/appearance or armor clearance claim'},indent=2)+'\n')
comparisons={}
for label,path in [('V33Form06',ROOT/'assets/audit/whole-character-v33/attempt-form06/neck-screen/screen.json'),('V34Upper01',ROOT/'assets/audit/whole-character-v34/attempt-upper01/head-neck-screen/neck/screen.json')]:
 if not path.exists():continue
 base=json.loads(path.read_text());rows=[]
 for b,c in zip(base['poses'],neck['poses']):
  def pairids(p):return {tuple(sorted((x.get('guard',x.get('a',x.get('meshA',''))),x.get('neighbor',x.get('b',x.get('meshB','')))))) for x in p['pairs']}
  old,new=pairids(b),pairids(c);rows.append({'pose':c['pose'],'baselineCount':b['pairCount'],'finalCount':c['pairCount'],'introduced':sorted(new-old),'inherited':sorted(new&old),'eliminated':sorted(old-new)})
 comparisons[label]={'baselineReceiptPath':str(path.relative_to(ROOT)),'baselineReceiptSHA256':sha(path),'poses':rows}
(H/'comparison.json').write_text(json.dumps(comparisons,indent=2)+'\n')
result={'status':'PASS bounded exact-composition attachment/era and14strict head-neck pose samples; no artistic/full-motion acceptance','native':{'path':str(N.relative_to(ROOT)),'sha256':sha(N),'bytes':N.stat().st_size},'glb':{'path':str(G.relative_to(ROOT)),'sha256':sha(G),'bytes':G.stat().st_size},'exportReceiptSHA256':sha(A/'export/export-receipt.json'),'compositionReceiptSHA256':sha(A/'receipt.json'),'roundtrip':{'receipt':'../export/actual-runtime-roundtrip/roundtrip-receipt.json','receiptSHA256':sha(T/'roundtrip-receipt.json'),'loadedMeshes':trip['counts']['loadedMeshes'],'worldMatricesCompared':trip['counts']['nativeWorldMatricesCompared'],'maximumWorldMatrixDelta':trip['maximumWorldMatrixDelta'],'runtimeSourceSHA256':trip['runtimeSourceSHA256'],'checks':trip['checks']},'eraIntegration':{'receipt':'../era-integration/integration.json','receiptSHA256':sha(E/'integration.json'),'status':era['status'],'sampleCount':era['summary']['sampleCount'],'failures':era['summary']['failures'],'fitRisks':era['summary']['fitRisks']},'head':{'allHeadMeshCount':head['allHeadMeshes'],'poses':[{'kind':p['pose'],'delta':p['delta'],'pairs':p['strictPairCount']} for p in head['poses']],'kernelSHA256':head['kernelSHA256'],'executedSourceSHA256':head['executedScreenSHA256']},'neck':{'screen':'neck/screen.json','poses':[{'name':p['pose'],'pairs':p['pairCount'],'screenedGuardCount':p['screenedGuards']} for p in neck['poses']],'executedSourceSHA256':neck['sourceSHA256']},'readOnlyInputsUnchanged':True,'limits':['Strict evaluated triangle edge-through-face screens exclude coplanar/tangent/containment and same-owner contacts; seven discrete jaw/cap and seven neck states, not continuous physics or whole-character collision clearance.','66actual runtime mechanism samples validate discrete surfaces/endpoints/visibility/reset, not a full mechanism collision screen or WebGL appearance.','No model, geometry, application, material or default-selection changes in this task.','Full-body/head likeness remains rejected/pending owner review; native/exactGLB availability and technical checks do not confer approval.']}
(H/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
for folder in [H,E,T]:
 files=[{'path':str(p.relative_to(folder)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(folder.rglob('*')) if p.is_file() and p.name!='manifest.json']
 (folder/'manifest.json').write_text(json.dumps({'status':'Frozen exact Form01 bounded validation evidence','nativeSHA256':sha(N),'glbSHA256':sha(G),'files':files},indent=2)+'\n')
 assert all(sha(folder/f['path'])==f['sha256'] for f in files)
 print(folder.name,sha(folder/'manifest.json'))
print('receipt',sha(H/'receipt.json'))
