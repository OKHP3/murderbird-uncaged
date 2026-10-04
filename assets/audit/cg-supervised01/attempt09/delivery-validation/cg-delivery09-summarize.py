import json,hashlib,struct,datetime,re
from pathlib import Path
R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');T=Path('/tmp');eras=('builder','maker','mechanic');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
selection=R/'assets/audit/cg-supervised01/attempt09/selected-modules.json';result={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS','scope':'Three-era final09 native renders and static GLB technical delivery; no likeness judgment','artistic_acceptance':False,'checks':{},'era_results':{},'owned_output_paths':[],'proof_pins':{},'not_run':['Browser rendering/parity','Application build/dist','Engineering','Owner artistic acceptance','Git commit/push/deploy']}
if selection.exists():
 result['proof_pins'][str(selection.relative_to(R))]=sha(selection);selectiondoc=json.loads(selection.read_text())
 for name in ['build-cg-supervised09.py','cg-supervised-export.py','cg-supervised-preservation.py','cg-supervised-body12.py']+selectiondoc['selected_module_names']:result['proof_pins']['scripts/'+name]=sha(R/'scripts'/name)
 for item in selectiondoc['review_inputs']:result['proof_pins'][item['path']]=sha(R/item['path'])
expected=['canon-neutral','canon-workshop','head-neck','side-profile','body-detail','feet-detail','hero']+[f'{profile}-{deg:03d}' for profile in ('neutral','workshop') for deg in range(0,360,45)]
allrenders=0;readbacks={}
for era in eras:
 out=R/f'assets/audit/cg-supervised01/attempt09/{era}';asset=R/'assets/models/cg-supervised01/attempt09';r={'checks':{},'renders':{},'proof_pins':{}}
 log=T/f'cg-delivery09-render-{era}.log';logtext=log.read_text() if log.exists() else '';r['process_log']=str(log);r['completion_marker']='SUPERVISED09_COMPLETE' in logtext;r['error_lines']=[l for l in logtext.splitlines() if re.search(r'Traceback|RuntimeError:|AssertionError|Python: Error|\bException:',l)];r['checks']['process']='PASS' if r['completion_marker'] and not r['error_lines'] else 'FAIL'
 receiptpath=out/'receipt.json'
 if receiptpath.exists():
  receipt=json.loads(receiptpath.read_text());r['proof_pins'][str(receiptpath.relative_to(R))]=sha(receiptpath)
  checks=[receipt.get('receiving_preservation',{}).get('mesh_and_anchor_count')==7424,receipt.get('early_receiving_save_readback',{}).get('mesh_empty_payloads')==7424,receipt.get('early_receiving_save_readback',{}).get('original_material_graphs')==56,receipt.get('receiving_save_readback',{}).get('mesh_empty_payloads')==7424,receipt.get('receiving_material_graph_preservation',{}).get('graphs')==56]
  for key in ('receiving_preservation','early_receiving_save_readback','receiving_save_readback','receiving_material_graph_preservation'):checks.append(receipt.get(key,{}).get('changed')==[])
  for key in ('early_packed_history_save_readback','packed_history_save_readback'):checks.extend([receipt.get(key,{}).get('receiving_images')==160,receipt.get(key,{}).get('missing')==[],receipt.get(key,{}).get('changed')==[]])
  r['checks']['early_final_receipt_preservation']='PASS' if all(checks) else 'FAIL'
  r['checks']['native_export']='PASS' if receipt.get('browser_export',{}).get('native_meshes_unchanged') and receipt.get('browser_export',{}).get('temporary_datablocks_removed') and not receipt.get('browser_export_failure') else 'FAIL'
  for name in expected:
   p=out/(name+'.png')
   if not p.exists():r['renders'][name]={'status':'FAIL','missing':True};continue
   data=p.read_bytes();dims=struct.unpack_from('>II',data,16);want=(960,1280) if name=='hero' else (1280,1280) if name in ('head-neck','body-detail','feet-detail') else (1280,853);h=sha(p);ok=data[:8]==b'\x89PNG\r\n\x1a\n' and dims==want and receipt.get('image_hashes',{}).get(p.name)==h;r['renders'][name]={'status':'PASS' if ok else 'FAIL','sha256':h,'bytes':len(data),'resolution':dims};allrenders+=ok;r['proof_pins'][str(p.relative_to(R))]=h
  r['checks']['23_render_hashes_dimensions']='PASS' if len(receipt.get('image_hashes',{}))==23 and all(v['status']=='PASS' for v in r['renders'].values()) else 'FAIL'
 else:r['checks']['receipt']='FAIL'
 for kind in ('preflight','early','native','glb'):
  p=T/f'cg-delivery09-{kind}-{era}.json'
  if p.exists():
   d=json.loads(p.read_text());r[kind+'_check_path']=str(p);r['checks'][kind]='PASS' if d.get('status')=='PASS' else 'FAIL'
   if kind=='native':readbacks[era]=d
  else:r['checks'][kind]='NOT RUN'
 for extension in ('blend','glb'):
  p=asset/f'murderbird-supervised-{era}.{extension}'
  if p.exists():r['proof_pins'][str(p.relative_to(R))]=sha(p)
 r['status']='PASS' if all(v=='PASS' for v in r['checks'].values()) else 'FAIL';result['era_results'][era]=r;result['proof_pins'].update(r['proof_pins']);result['owned_output_paths'].extend([str(out.relative_to(R)),str((asset/f'murderbird-supervised-{era}.blend').relative_to(R)),str((asset/f'murderbird-supervised-{era}.glb').relative_to(R))])
result['native_render_count']=allrenders;result['checks']['all69_native_renders']='PASS' if allrenders==69 else 'FAIL'
if len(readbacks)==3:
 names={era:set(d['new_evaluated_meshes']) for era,d in readbacks.items()};reference=readbacks['builder']['new_evaluated_meshes'];mismatch={};slot_records={}
 for era,d in readbacks.items():
  local=d['new_evaluated_meshes'];mismatch[era]=[n for n in reference if n not in local or reference[n]['position_sha256']!=local[n]['position_sha256'] or reference[n]['topology_sha256']!=local[n]['topology_sha256'] or reference[n]['matrix_world']!=local[n]['matrix_world'] or reference[n]['determinant']!=local[n]['determinant'] or reference[n]['face_slots']!=local[n]['face_slots']];slot_records[era]={n:v['slots'] for n,v in local.items()}
 result['cross_era_geometry']={'same_new_mesh_names':all(v==names['builder'] for v in names.values()),'mismatches':mismatch,'new_mesh_count':len(reference),'era_material_slots':slot_records,'method':'Evaluated position and topology hashes, exact world transforms, determinants and face-slot sets compared. Era material names retained. UV differences recorded separately.'};result['checks']['cross_era_geometry']='PASS' if result['cross_era_geometry']['same_new_mesh_names'] and not any(mismatch.values()) else 'FAIL'
 result['cross_era_geometry']['uv_digest_differences']={era:[n for n in reference if n in d['new_evaluated_meshes'] and reference[n]['uv']!=d['new_evaluated_meshes'][n]['uv']] for era,d in readbacks.items()}
 result['evaluated_uv_overshoots']={era:{n:v['uv'] for n,v in d['new_evaluated_meshes'].items() if any(q['evaluated_overshoot'] for q in v['uv'])} for era,d in readbacks.items()}
 result['evaluated_uv_interpolation_note']='Controls remain normalized within1e-6; evaluated normalized bound1e-4 per explicit root adjudication. BILL18 distal evaluated max1.000024676322937, BEVEL-only cause independently confirmed; all other overshoots1float32ULP.'
 for p in (T/'cg-delivery09-early-snapshot-pins.json',T/'cg-delivery09-bill-cross-era.json'):
  if p.exists():result[p.stem]=json.loads(p.read_text())
else:result['checks']['cross_era_geometry']='NOT RUN'
result['status']='PASS' if all(v=='PASS' for v in result['checks'].values()) and all(v['status']=='PASS' for v in result['era_results'].values()) else 'FAIL'
(T/'cg-delivery09-summary.json').write_text(json.dumps(result,indent=2));print(json.dumps({'status':result['status'],'render_count':allrenders,'checks':result['checks'],'era_checks':{k:v['checks'] for k,v in result['era_results'].items()}},indent=2))
