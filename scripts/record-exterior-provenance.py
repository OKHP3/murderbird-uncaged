"""Record local v1 production provenance without modifying source material."""
from pathlib import Path
import hashlib,json,datetime
ROOT=Path(__file__).resolve().parents[1]
def record(p):
 return {'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
refs=[
 'assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png',
 'assets/img/library/murderbird-unified-maker-clean-candidate-2026-09-06.png',
 'assets/img/library/murderbird-unified-mechanic-candidate-2026-09-06.png',
 'assets/img/library/murderbird-unified-heart-candidate-2026-09-06.png',
 'context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png',
 'assets/murderbird/production/video/murderbird-first-choice-controlled-pilot-03.mp4','content/story/index.main.html',
 'assets/models/uncaged-structure-v1/murderbird-structure-v1.blend',
]
for rel in refs:assert not (ROOT/rel).read_bytes().startswith(b'version https://git-lfs'),rel
video_alias=ROOT/'assets/video/murderbird-first-choice-635f0e15.mp4'
video_binary=ROOT/'assets/murderbird/production/video/murderbird-first-choice-controlled-pilot-03.mp4'
alias_bytes=video_alias.read_bytes()
if alias_bytes.startswith(b'version https://git-lfs'):
 expected=next(line.split('sha256:')[1] for line in alias_bytes.decode().splitlines() if line.startswith('oid sha256:'))
 assert hashlib.sha256(video_binary.read_bytes()).hexdigest()==expected
files=[]
for folder in ['assets/models/uncaged-exterior-v1','assets/audit/exterior-v1']:
 files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file())
for pattern in ['scripts/*exterior*','docs/exterior-*.md']:
 files.extend(p for p in ROOT.glob(pattern) if p.is_file())
files.extend(ROOT/p for p in ['src/scene/presence-exhibit.js','src/scene/era-mechanisms.js','src/scene/fallback.js','src/main.js','scripts/load-rigid-validation.mjs','scripts/verify-era-motion.mjs','scripts/verify-advanced-power-moves.mjs','scripts/verify-structural-motion.mjs','scripts/verify-structural-mechanisms.mjs','docs/production-handoff.md','docs/creative-authority.md','README.md','assets/README.md'])
receipt={'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'Implemented local review version; owner artistic acceptance pending','startingCommit':'21ac417','worktree':str(ROOT),'localExhibit':'http://127.0.0.1:5174/','localBuildPreview':'http://127.0.0.1:4176/','publication':'None; no remote CI, LFS retrieval or deployment claim','rights':'MurderBird creative content all rights reserved under NOTICE.md; code MIT','authority':'docs/creative-authority.md; docs/structural-reference-audit.md; docs/exterior-stage-record.md','videoAlias':{'requestedPath':str(video_alias.relative_to(ROOT)),'status':'LFS pointer with SHA-matched preserved binary' if alias_bytes.startswith(b'version https://git-lfs') else 'binary','verifiedBinary':record(video_binary)},'historicalSources':[record(ROOT/p) for p in refs],'productionFiles':[record(p) for p in sorted(set(files))],'runtimeBuild':[record(p) for p in sorted((ROOT/'dist').rglob('*')) if p.is_file()]}
p=ROOT/'provenance/exterior-construction-v1-2026-09-27.json';p.write_text(json.dumps(receipt,indent=2)+'\n');print(p)
