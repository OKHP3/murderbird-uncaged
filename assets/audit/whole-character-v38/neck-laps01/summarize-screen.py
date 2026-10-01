"""Compact summary of the preserved executed finite screen; no geometry/test rerun."""
import json,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent
x=json.loads((P/'finite-screen.json').read_text());out={'method':x['method'],'poseInterpretation':x['poseInterpretation'],'sourceSHA256':x['sourceSHA256'],'candidateSHA256':x['candidateSHA256'],'rawEvidenceSHA256':hashlib.sha256((P/'finite-screen.json').read_bytes()).hexdigest(),'poses':{}}
def brief(v):return {k:v[k]for k in ['changed','other','owners','sameOwner','strictTrianglePairs','changedTriangles','otherTriangles']}
for label,d in x['poses'].items():
 c=d['comparison'];new=c['newPairs'];increase=[p for p in c['inheritedCountChanges']if p['candidateStrictTrianglePairs']>p['sourceStrictTrianglePairs']]
 out['poses'][label]={'angles':d['candidate']['pose'],'sourcePairs':c['sourcePairs'],'candidatePairs':c['candidatePairs'],'newPairs':len(new),'newSkinsOnlyPairs':sum(not any('V38 neck-lap' in p[k]for k in ['changed','other'])for p in new),'newSupportPairs':sum(any('V38 neck-lap'in p[k]for k in ['changed','other'])for p in new),'newSameOwnerPairs':sum(p['sameOwner']for p in new),'inheritedIncreaseCount':len(increase),'newPairDetails':[brief(p)for p in new],'inheritedIncreases':increase,'sourcePairCounts':[brief(p)for p in d['source']['pairs']],'candidatePairCounts':[brief(p)for p in d['candidate']['pairs']],'individualStock':d['candidate']['stocks']}
(P/'finite-compact.json').write_text(json.dumps(out,indent=2)+'\n')
