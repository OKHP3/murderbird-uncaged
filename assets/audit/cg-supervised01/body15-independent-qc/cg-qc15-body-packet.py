import hashlib,json,subprocess,ast
from pathlib import Path
WT=Path('/Users/okh/.codex/worktrees/cg-supervised-oblique-breast15/murderbird-uncaged');ROOT=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');P=WT/'assets/audit/cg-supervised-body15/attempt01';Q=ROOT/'assets/audit/cg-supervised-body13/attempt01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((P/'receipt.json').read_text());prior=json.loads((Q/'receipt.json').read_text());manifest=json.loads((P/'frozen-manifest.json').read_text());verified=[];bad=[]
for rel,entry in manifest['files'].items():
 p=WT/rel;a={'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size};verified.append(a)
 if a['sha256']!=entry['sha256'] or a['bytes']!=entry['bytes']:bad.append(a)
cams=[]
for n,q in r['cameras'].items():
 pn=n.replace('final15-','final13-');cams.append(dict(candidate=n,base=pn,exact=q==prior['cameras'][pn]))
cache=json.loads((P/'cached-render-provenance.json').read_text());print('CACHED_ENTRY_SAMPLE',cache[:1])
cachechecks=[]
for n in [x.name for x in P.glob('before13-*.png')]:
 orig=Q/(n.replace('before13-','final13-'));cachechecks.append(dict(candidate=n,rootOriginal=str(orig),exact=orig.exists() and sha(P/n)==sha(orig)))
refs={}
for rel in ['goal.md','scripts/cg-supervised-body12.py','scripts/cg-supervised-body13.py','assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend','assets/audit/cg-supervised-body13/attempt01/murderbird-body13.blend','assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg','assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png','assets/video/murderbird-first-choice-635f0e15.mp4']:
 p=ROOT/rel;refs[rel]=dict(path=str(p),sha256=sha(p))
source=json.loads((ROOT/'assets/audit/cg-supervised01/source-frames/receipt.json').read_text());frames=[]
for x in source['frames']:
 p=ROOT/x['path'];frames.append(dict(path=str(p),time_seconds=x['time_seconds'],sha256=sha(p),receiptHashExact=sha(p)==x['sha256']))
ast.parse((WT/'scripts/cg-supervised-body15.py').read_text())
out=dict(worktree=str(WT),commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=WT,text=True).strip(),status=subprocess.check_output(['git','status','--short'],cwd=WT,text=True),manifestEntries=len(verified),manifestFailures=bad,manifestVerified=verified,cameraRecords=len(cams),cameraComparisons=cams,before13PNGChecks=cachechecks,sourceIdentities=refs,sourceFrames=frames,scriptAST='PASS')
Path('/tmp/cg-qc15-body-packet.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k not in ['manifestVerified','sourceIdentities']},indent=2))
