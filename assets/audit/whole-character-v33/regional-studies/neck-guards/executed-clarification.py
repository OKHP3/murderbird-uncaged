from pathlib import Path
import json,hashlib
OUT=Path(__file__).parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((OUT/'coarse01/receipt.json').read_text());records=r['result']['records'];moves=sorted([(x.get('maximumInwardReceivingDisplacementM',0),x['name']) for x in records],reverse=True);assert not(OUT/'measurement-and-coverage-clarification.md').exists()
text='''# Frozen V33 measurement and coverage clarification

This note supersedes the largest-displacement estimate in `handoff.md` and the first preview message. The authoritative numeric receipt already records the correct maximum: **33.219741mm**, on `V23 cervical 3 directional guard 10` (posterior course). The other guards peak at11.261434mm. The earlier≈10.94mm estimate described the largest first-course value, not the full candidate.

The actual contact render exposes a structure gap between the distal neck and the lower head hood. Head-owned throat plates, head/eyes/frame and all named rests remain exact. This candidate corrects discrete finite surface crossings; it does **not** establish continuous protective coverage, visible head-to-neck support, full pose fit, attachment load capacity or artistic acceptance. Root observed the gap and will review head-owned throat changes in composition.

Geometry is frozen: one candidate, no correction. Source SHA256 `de8f3854b3e631be5829505cb51836816e22d9166cf07e7f6cc6e4513b807f18`; native SHA256 `403550c2f90705692a1c159112a334dd89dc6537869b644ad57b63c4965fdb89`. Thirty guards and two receiving cheeks are finite/closed/positive;559 outside meshes remain exact. Seven strict screen counts are0/0/0/0/0/0/0, eliminating31 baseline observations across22 unique identities. No continuous collision or same-owner screen is claimed.

The initial manifest and narrative are preserved as written; `manifest-final.json` includes this explicit correction alongside them. No new geometry, tests, runtime edits or commits.
'''
(OUT/'measurement-and-coverage-clarification.md').write_text(text)
files=[{'path':p.relative_to(OUT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(OUT.rglob('*')) if p.is_file()];assert all(sha(OUT/x['path'])==x['sha256'] for x in files);original=json.loads((OUT/'manifest.json').read_text());final={k:v for k,v in original.items() if k!='files'};final['files']=files;final['clarification']='measurement-and-coverage-clarification.md supersedes earlier narrative maximum and explicitly records contact coverage gap';final['priorManifestSHA256']=sha(OUT/'manifest.json');(OUT/'manifest-final.json').write_text(json.dumps(final,indent=2)+'\n');print(json.dumps({'finalManifestSHA256':sha(OUT/'manifest-final.json'),'clarificationSHA256':sha(OUT/'measurement-and-coverage-clarification.md'),'maxGuard':moves[0],'sourceSHA256':r['sourceSHA256']}))
