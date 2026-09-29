from pathlib import Path
import json,hashlib,shutil
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=ROOT/'assets/audit/whole-character-v32/attempt-form01/neck-screen';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not(OUT/'manifest.json').exists();shutil.copy2(__file__,OUT/'executed-comparison.py');shutil.copy2('/tmp/v32-form01-neck-screen.log',OUT/'screen.log')
n=json.loads((OUT/'screen.json').read_text());comparisons={}
for version,path in [('v30','assets/audit/whole-character-v30/attempt-form02/neck-screen'),('v31','assets/audit/whole-character-v31/attempt-form02/neck-screen')]:
 src=ROOT/path;shutil.copy2(src/'screen.json',OUT/f'executed-{version}-baseline-screen.json');shutil.copy2(src/'executed-screen.py',OUT/f'executed-{version}-baseline-validator.py');b=json.loads((src/'screen.json').read_text());rows=[]
 assert sha(src/'executed-screen.py')==sha(OUT/'executed-screen.py')
 for old,new in zip(b['poses'],n['poses']):
  assert old['pose']==new['pose'] and old['angles']==new['angles'];op={tuple(sorted((x['a'],x['b']))) for x in old['pairs']};np={tuple(sorted((x['a'],x['b']))) for x in new['pairs']}
  rows.append({'pose':new['pose'],'angles':new['angles'],'baselineCount':old['pairCount'],'combinedCount':new['pairCount'],'inherited':sorted(op&np),'introduced':sorted(np-op),'eliminated':sorted(op-np)})
 comparisons[version]={'baselineNativeSHA256':b['nativeSHA256'],'baselineScreenSHA256':sha(src/'screen.json'),'sameValidatorBytes':True,'poses':rows}
introduced=sum(len(p['introduced']) for c in comparisons.values() for p in c['poses'])
composition=ROOT/'assets/audit/whole-character-v32/attempt-form01/receipt.json';shutil.copy2(composition,OUT/'executed-composition-receipt.json');c=json.loads(composition.read_text());native=ROOT/c['native']['path'];assert sha(native)==n['nativeSHA256']=='676c7226c57d492c6f63e1ce873c1d89e6222fdd46d4ec954aa4ec0db26bc26f'
result={'status':'Zero introduced tested identities; inherited neck crossings remain' if introduced==0 else 'FAIL: introduced tested identities','native':c['native'],'composedRegionSources':[r['source'] for r in c['regions']],'screenSHA256':sha(OUT/'screen.json'),'validatorSHA256':sha(OUT/'executed-screen.py'),'method':n['method'],'comparisons':comparisons,'limits':['Seven discrete evaluated finite surface-crossing samples; no continuous collision, engineering or artistic acceptance.','Inherited failures remain explicit, including fourteen Maker and seven contact pairs; no exemptions or whole-neck motion pass.','Same-owner overlaps are not examined by this cross-owner validator.']}
(OUT/'comparison.json').write_text(json.dumps(result,indent=2)+'\n');(OUT/'executed-check-arguments.json').write_text(json.dumps({'model':c['native']['path'],'sha':n['nativeSHA256'],'output':str(OUT.relative_to(ROOT)),'render':False},indent=2)+'\n')
files=[{'path':p.relative_to(OUT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(OUT.rglob('*')) if p.is_file()];assert all(sha(OUT/f['path'])==f['sha256'] for f in files)
for row in result['composedRegionSources']:assert sha(ROOT/row['path'])==row['sha256']
(OUT/'manifest.json').write_text(json.dumps({'status':result['status'],'native':c['native'],'composedRegionSources':result['composedRegionSources'],'relativePathHashesChecked':True,'files':files},indent=2)+'\n');print(json.dumps({'introduced':introduced,'comparisonSHA256':sha(OUT/'comparison.json'),'manifestSHA256':sha(OUT/'manifest.json'),'counts':[p['pairCount'] for p in n['poses']]}))
