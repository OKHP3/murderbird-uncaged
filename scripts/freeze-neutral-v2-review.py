"""Freeze the bounded Stage B evidence identity without touching older packets."""
from pathlib import Path
import json,hashlib,datetime,subprocess
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assets/audit/neutral-v2'
def row(p):
 raw=p.read_bytes();return {'path':str(p.relative_to(ROOT)),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
model=ROOT/'assets/models/uncaged-neutral-v2/murderbird-neutral-v2.glb';identity=row(model)
assert identity['sha256']=='48229ba5526ccd7a227db56d225ef88643eb6b3388eb07662452cc2c67636ac7','Use a new reviewed identity for a different model.'
receipts=[]
for name in ['asset-validation.json','motion-validation.json','structural-motion-validation.json','power-move-validation.json','mechanism-validation.json','browser-validation.json','label-validation.json','frozen-extrema.json','motion-demonstration.json','contact-view.json']:
 p=OUT/name;value=json.loads(p.read_text());assert value.get('status')=='passed',(name,value.get('status'))
 if value.get('modelSha256'):assert value['modelSha256']==identity['sha256'],name
 if value.get('modelIdentity'):assert value['modelIdentity']['sha256']==identity['sha256'],name
 receipts.append(row(p))
source_paths=[ROOT/'src',ROOT/'scripts',ROOT/'tests']
sources=[]
for folder in source_paths:
 for p in sorted(folder.rglob('*')):
  if p.is_file() and p.suffix in ['.js','.mjs','.css','.py','.json'] and '__pycache__' not in p.parts:sources.append(row(p))
for name in ['package.json','package-lock.json','vite.config.js']:
 p=ROOT/name
 if p.exists():sources.append(row(p))
report={'generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stage':'B review candidate','assessment':'REVISION REQUIRED in all eras; no full score or owner acceptance','baseRevision':'4b1c726f5d9bbd1ba1048f89049a5b422001c506','branch':'codex/neutral-correction-v2','model':identity,'editableSource':row(ROOT/'assets/models/uncaged-neutral-v2/murderbird-neutral-v2.blend'),'referencePacket':row(ROOT/'assets/models/uncaged-neutral-v2/reference-packet.json'),'runtimeAndToolSources':sources,'receipts':receipts,'reviewMedia':[row(OUT/n) for n in ['neutral-motion-demonstration.webm','neutral-motion-demonstration.mp4','authoring-views.json','screenshot-manifest.json']],'findings':{**{f'F{i:02}':'open, partial geometry progress' for i in range(1,5)},'F05':'gated; regional finish incomplete','F06':'gated; no final materials','F07':'open; no purposeful claw action','F08':'open; controller variation only, gesture and 120-second evidence pending','F09':'corrected within separately retested desktop/narrow layouts and keyboard activation','F10':'resolved in local dynamic-inventory and negative-fixture scope'},'ownersDecisionsPending':['Stage B proportion direction','V10 left shoulder chronology/topology','V12 early-era motion scope'],'limits':['Initial browser narrow-label assertions were vacuous because CSS hid the container; label-validation.json supersedes that subset.','Short rolling desktop frame samples only; no physical mobile or sustained thermal/network result.','No complete PRD score, continuous human acting, screen reader, audible theme review or publication.','Prior inspector packet and historical receipts remain unchanged.']}
(OUT/'candidate-assessment.json').write_text(json.dumps(report,indent=2)+'\n')
print('Frozen',len(sources),'source files and',len(receipts),'bounded receipts for',identity['sha256'])
