import json,hashlib,math
from pathlib import Path
A=Path(__file__).resolve().parent;R=Path.cwd();screen=json.loads((A/'strict-foot-motion-screen.json').read_text());receipt=json.loads((A/'receipt.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=R/'assets/audit/whole-character-v36/attempt-form01/foot-motion-screen/executed-strict-foot-motion-screen.py';new=A/'executed-strict-foot-motion-screen.py'
kernel=lambda p:p.read_text().split('def inside(')[1].split('def screen(')[0]
assert kernel(old)==kernel(new)
endpoints={x['toeRootReceivingJournal']:x for x in receipt['result']['endpoints'] if 'toeRootReceivingJournal' in x}
introduced=[]
for p in screen['poses']:
 for pair in p['introduced']:
  ident=(pair['a'],pair['b'])
  if any(tuple(q['pair'])==ident for q in introduced):continue
  if not pair['sameOwner']:
   c=endpoints[pair['owners'][0]]['journalCentreWorldXYZ'];rad=[math.hypot(v[1]-c[1],v[2]-c[2]) for v in pair['witnessTriangles'][1]]
   cause='Moving proximal load web crosses the forward sector of its stationary foot-owned proximal receiving journal. The pin bore exists and clears the inherited pin in all three samples, but the web has no rotation pocket / axial seat clearance. Witness is at the intended joint, not unrelated leg or body structure.'
  else:
   rad=None;cause='Unplanned stationary fit conflict: the instep guard rear lip enters the retained ankle receiver lower/front slope. Same foot owner; not an intended fabrication join and not exempted.'
  introduced.append({'pair':list(ident),'owners':pair['owners'],'sameOwner':pair['sameOwner'],'cause':cause,'restWitnessRadialDistancesAboutJournalAxisM':rad,'restWitness':pair,'allThreeStates':True})
# Every distinct same-owner pair remains present, with an explicit proposed
# fabrication role only where authored as a fixed join; conflicts stay FAIL.
fixed=[]
for pair in screen['poses'][0]['candidate']['pairs']:
 if not pair['sameOwner']:continue
 a,b=pair['a'],pair['b'];names=a+' '+b
 if 'V21' in names:desc='Unplanned instep-guard/retained ankle-receiver conflict; FAIL, not a fabrication seat.'
 elif 'captive toe-bearing flanges' in names:desc='Unplanned distal load-bar/collar conflict; FAIL. Same-owner classification does not establish acceptable fabrication.'
 elif 'metatarsal passive rail' in names and 'hallux' in names:desc='Unplanned rail/hallux-member material conflict; FAIL. A welded junction was not established by this design.'
 elif 'tapered claw sheath' in names:desc='Proposed fixed distal talon root seated in its load-bar socket. Specific same-owner fabrication lap; unvalidated fabrication, no screen exemption.'
 elif 'rear hallux sheath' in names:desc='Proposed fixed hallux sheath root seated in rear load-bar socket. Specific same-owner fabrication lap; unvalidated fabrication, no screen exemption.'
 elif 'Toe hinge' in names:desc='Proposed fixed proximal web attachment at its own bearing housing. Specific fabrication seat; not acceptable across moving owners, unvalidated fabrication.'
 elif 'curved instep guard' in names:desc='Proposed fixed instep guard mounting overlap on channel shoulders. Distinct component retained; fabrication/mounting detail is unvalidated.'
 elif 'rear hallux load link' in names:desc='Proposed fixed hallux load-bar attachment to toe-root crossmember/channel; unvalidated fabrication.'
 else:desc='Proposed fixed metatarsal rail/channel structural connection; separate members retained, fabrication unvalidated.'
 fixed.append({'pair':[a,b],'owner':pair['owners'][0],'classification':desc,'exempted':False,'allThreeStates':True})
rows=[]
for p in screen['poses']:
 rows.append({'pose':p['pose'],'baselinePairIdentities':p['baseline']['pairCount'],'candidatePairIdentities':p['candidate']['pairCount'],'introducedPairIdentities':len(p['introduced']),'introducedMovingOwnerPairs':sum(not q['sameOwner'] for q in p['introduced']),'introducedSameOwnerPairs':sum(q['sameOwner'] for q in p['introduced']),'candidateMovingOwnerPairs':sum(not q['sameOwner'] for q in p['candidate']['pairs']),'candidateSameOwnerPairs':sum(q['sameOwner'] for q in p['candidate']['pairs']),'finiteClosedChangedMeshes':all(q['finite'] and q['boundaryEdges']==0 and q['nonmanifoldEdges']==0 and q['degenerateTrianglesLe1e14']==0 for q in p['candidate']['geometry']),'actualNodeMatrixInstallationMaxErrorM':p['candidate']['matrixInstallationMaxErrorM'],'restParityMaxError':p['candidate']['exportedRestParityMaxError']})
summary={'status':'FAIL — preserve regional visual study; do not compose/select/export for application','native':receipt['native'],'module':receipt['module'],'base':receipt['base'],'checks':receipt['checks'],'footEnvelope':receipt['result']['footEnvelope'],'poseResults':rows,'introducedCauseAttribution':introduced,'allDistinctSameOwnerCrossings':fixed,'strictKernelByteExactToV36':True,'strictKernelSHA256':hashlib.sha256(kernel(new).encode()).hexdigest(),'pairExemptions':[],'limitations':['Totals are pair identities, not penetration depth; fewer total crossings is not a pass.','Six additional moving-owner identities retain V35 pair names but involve rebuilt geometry: proximal load-web approach crosses relocated distal pins/flanges. They are unresolved fit failures, not grandfathered acceptance.','Only three discrete samples; no swept clearance, containment, tangent/coplanar, within-mesh self-intersection, forces, balance, human likeness or publication claim.','Maker/Mechanic/Advanced era hardware remains external procedural geometry and was not included.','Initial design and one correction only; provisional attempt02 is preserved between initial and completed correction, not a further motion-based adjustment.','No app edits, application export, commit, push or deployment. Evaluation GLB is only a fresh node-pose sampling input.'], 'artifacts':[{'path':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size} for p in [A/'receipt.json',A/'strict-foot-motion-screen.json',A/'v35-pose-matrices.json',A/'v37-pose-matrices.json',A/'matched-pose-views.json',A/'neutral/receipt.json',old,new]]}
with (A/'validation-summary.json').open('x') as f:json.dump(summary,f,indent=2);f.write('\n')
print(json.dumps(rows,indent=2))
