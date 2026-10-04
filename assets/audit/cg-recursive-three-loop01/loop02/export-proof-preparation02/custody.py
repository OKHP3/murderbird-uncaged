import pathlib,json,hashlib,datetime
ROOT=pathlib.Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');OUT=pathlib.Path('/tmp/cg-recursive-export-proof02')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=ROOT/'assets/audit/cg-recursive-three-loop01/loop01/final-frozen-manifest.json';x=json.load(open(p));bad=[]
for r in x['files']:
 q=ROOT/r['path']
 if not q.exists() or sha(q)!=r['sha256'] or q.stat().st_size!=r['bytes']:bad.append(r['path'])
original=json.load(open(ROOT/'assets/audit/cg-supervised01/attempt09/frozen-manifest.json'));pins={r['path']:r for r in original['files']};checks=[]
for r in json.load(open(OUT/'maximum-trace.json'))['results']:
 for p in [pathlib.Path(r['original09_GLB_path']),ROOT/'assets/models/cg-supervised01/attempt09'/('murderbird-supervised-'+r['era']+'.blend')]:
  rel=str(p.relative_to(ROOT));h=sha(p);checks.append({'path':rel,'sha256':h,'original216_pin_match':h==pins[rel]['sha256']})
p=ROOT/'scripts/cg-supervised-export.py';h=sha(p);receipt=json.load(open(ROOT/'assets/audit/cg-recursive-three-loop01/loop01/delivery/retained02/builder/receipt.json'));checks.append({'path':str(p.relative_to(ROOT)),'sha256':h,'original216_pin_match':h==pins[str(p.relative_to(ROOT))]['sha256'],'final_delivery_receipt_pin_match':h==receipt['helper_pins'][p.name]})
sources=[]
for path,start,end in [('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged/scripts/cg-supervised-export.py',185,263),('/Applications/Blender.app/Contents/Resources/5.2/scripts/addons_core/io_scene_gltf2/blender/exp/primitive_extract.py',1450,1499),('/Applications/Blender.app/Contents/Resources/5.2/scripts/addons_core/io_scene_gltf2/io/com/constants.py',160,160)]:
 p=pathlib.Path(path);lines=p.read_text().splitlines();sources.append({'path':str(p),'sha256':sha(p),'lines':[start,end],'excerpt':'\n'.join(lines[start-1:end])})
(OUT/'source-code-evidence.json').write_text(json.dumps({'sources':sources,'limits':'Producer helper is pinned by original216 and final receipt. Installed glTF source is current local installation evidence, not a historically frozen library snapshot; maximum delta numerical cause is not certified.'},indent=2)+'\n')
r={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'final_manifest_sha256':sha(ROOT/'assets/audit/cg-recursive-three-loop01/loop01/final-frozen-manifest.json'),'expected_final_manifest_sha256':'041678f58cebd5177c1f30e1f717e4763add9d74557789a184fe96792ec70517','count':len(x['files']),'mismatches':bad,'selected_original216_and_helper_checks':checks};(OUT/'custody.json').write_text(json.dumps(r,indent=2)+'\n');print('199custody',len(bad),'selectedoldpins',all(c['original216_pin_match']for c in checks))
