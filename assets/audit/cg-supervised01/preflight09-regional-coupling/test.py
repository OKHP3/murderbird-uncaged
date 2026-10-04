import bpy,json,hashlib,importlib.util,math,time,traceback,struct
from pathlib import Path
R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');O=Path('/tmp/cg-preflight09');REPORT=Path('/tmp/cg-preflight09.json');start=time.time()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mod(n):
 s=importlib.util.spec_from_file_location('preflight_'+n,R/'scripts'/('cg-supervised-'+n+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=mod('body12');p=mod('preservation');optic=mod('optic13');body=mod('body15');feet=mod('feet14');ex=mod('export')
# Only generated gradient pathname is redirected; frozen implementation bytes and API remain intact.
optic.__file__=str(O/'scripts/cg-supervised-optic13.py')
def packed():
 return {i.name:dict(items=dict(i.items()),size=list(i.size),channels=i.channels,alphaMode=i.alpha_mode,colorSpace=i.colorspace_settings.name,fileFormat=i.file_format,source=i.source,filepath=i.filepath,filepathRaw=i.filepath_raw,fakeUser=i.use_fake_user,packedSHA256=hashlib.sha256(bytes(i.packed_file.data)).hexdigest()) for i in bpy.data.images if i.packed_file}
def snap():
 s=bpy.context.scene
 return dict(payload={o.name:m.digest(o) for o in s.objects if o.type in ('MESH','EMPTY')},graphs=m.material_digest(),packed=packed(),visibility={o.name:[o.hide_render,o.hide_viewport,o.hide_get()] for o in s.objects},materialIDs=[x.name for x in bpy.data.materials])
def geometry(o):
 # Material names excluded; face slot assignments and every loop UV retained.
 return ex._digest_mesh(o.data)
def save_report():
 report['elapsedSeconds']=time.time()-start;REPORT.write_text(json.dumps(report,indent=2,default=str))
report=dict(scope='HYPOTHETICAL regional coupling ONLY: optic13 + body15 lower26 + feet14 applied sequentially to immutable receiving06; head17 not included; no source QC/promotion/owner acceptance',startedUTC=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),blenderVersion=bpy.app.version_string,threads=2,authorityGoalSHA256=sha(R/'goal.md'),eras={},moduleSHA256={n:sha(R/'scripts'/('cg-supervised-'+n+'.py')) for n in ['optic13','body15','feet14','body12','body13','body11','preservation','export']},moduleReturnRecords={},blockingIssues=[],checksNotRun=['Integrated final head17 scene/natives','Matched source likeness or rendered whole/crops','Browser WebGL/fallback parity','Maker/Mechanic GLB export','npm/build/dist/CI/deployment','Owner artistic acceptance','Animation/engineering'],limits=['Shared transparent body12 payload/material digest and explicit packed-ID helper used; not exhaustive RNA/modifier/animation equivalence','Temporary Builder export tests static material/UV/normal coverage only, not rendered browser appearance','Only gradient output pathname was redirected under /tmp; no implementation edits'])
pins=dict(builder='72e7e53daf40b7128cdf9b173006c639bcf123952547a2576fb2de29130f06d4',maker='bda040ce03f1f628850da1744f6ca3359bd6a8f0e496a910347becb5216c622a',mechanic='9b6006f035896490dab43301ddfde96aee26ec0dcbeca18848d3e43189794acb')
newgeometry={}
try:
 for era in ['builder','maker','mechanic']:
  src=R/f'assets/models/cg-supervised01/attempt06/murderbird-supervised-{era}.blend';assert sha(src)==pins[era],f'INPUT PIN {era}'
  bpy.ops.wm.open_mainfile(filepath=str(src),use_scripts=False);s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=2;s.cycles.device='CPU';a=snap();assert len(a['payload'])==7424 and len(a['graphs'])==56 and len(a['packed'])==160
  (O/f'{era}-receiving-snapshot.json').write_text(json.dumps(a,indent=2))
  frame=[list(v) for v in s.objects['CG2b head frame'].matrix_world]
  retopt=optic.apply(s,R,era);retbody=body.apply(s,R,era,design=1);retfeet=feet.apply(s,R,era)
  report['moduleReturnRecords'][era]=dict(optic13=retopt,body15=retbody,feet14=retfeet)
  p.retain_packed_image_ids(s);bpy.context.view_layer.update();inmemory=snap();native=O/f'hypothetical-{era}.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),relative_remap=False);bpy.ops.wm.open_mainfile(filepath=str(native),use_scripts=False);s=bpy.context.scene;b=snap()
  allow=set(retopt['hidden_originals'])|set(retbody['hiddenLegacyManifest'])|set(retfeet['hiddenOriginals'])
  # Returned body authoring guide is new, hence outside original allowlist.
  guides=[n for n in a['visibility'] if any(k in n.lower() for k in ['guide','ground']) and a['visibility'][n]!=b['visibility'].get(n)]
  originalchanges=[n for n,h in a['payload'].items() if b['payload'].get(n)!=h];graphchanges=[n for n,h in a['graphs'].items() if b['graphs'].get(n)!=h];imagechanges=[n for n,h in a['packed'].items() if b['packed'].get(n)!=h];vischanged=[n for n,v in a['visibility'].items() if b['visibility'].get(n)!=v];unexpected=set(vischanged)-allow;expectedChanged={n for n in allow if n in a['visibility'] and a['visibility'][n]!=b['visibility'].get(n)}
  missinghides=[n for n in allow if n not in s.objects or not s.objects[n].hide_render]
  new=[o for o in s.objects if o.type=='MESH' and o.name not in a['payload']];badgeo=[];baduv=[];missinguv=[];normbad=[];dg=bpy.context.evaluated_depsgraph_get();geo={}
  for ob in new:
   ev=ob.evaluated_get(dg);md=ev.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
   if any(not math.isfinite(q) for v in md.vertices for q in v.co):badgeo.append(ob.name)
   if not md.uv_layers:missinguv.append(ob.name)
   if any(not math.isfinite(q) or q<-.000001 or q>1.000001 for l in md.uv_layers for v in l.data for q in v.uv):baduv.append(ob.name)
   if any(not all(math.isfinite(q) for q in n.vector) for n in md.corner_normals):normbad.append(ob.name)
   ev.to_mesh_clear()
   if ob.get('cgSupervisedBody12') or ob.get('cgSupervisedBody15') or ob.get(feet.TAG):geo[ob.name]=geometry(ob)
  newgeometry[era]=geo
  opt=[ob for ob in new if ob.get('cgSupervisedOptic13')];deltas={ob.name:max(abs(ob.matrix_world[i][j]-frame[i][j]) for i in range(4) for j in range(4)) for ob in opt};radius=max(math.sqrt((v.co.y-.005)**2+(v.co.z-.020)**2)/.0012 for ob in opt for v in ob.data.vertices)
  emissions={mat.name:next((float(n.inputs['Emission Strength'].default_value) for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None) for mat in bpy.data.materials if mat.name.startswith('CGO13 protected')}
  sameSaved=[k for k in ['payload','graphs','packed','visibility'] if inmemory[k]!=b[k]]
  eraresult=dict(inputPath=str(src),inputSHA256=pins[era],nativePath=str(native),nativeSHA256=sha(native),originalPayloads=len(a['payload']),originalMaterialGraphs=len(a['graphs']),originalPackedFILEImages=len(a['packed']),changedPayloads=originalchanges,changedMaterialGraphs=graphchanges,changedPackedBytesOrMetadata=imagechanges,materialIDNamesRetained=all(n in b['materialIDs'] for n in a['materialIDs']),nativeSaveReopenChangedFields=sameSaved,combinedOriginalVisibilityAllowlist=sorted(allow),visibilityChanged=vischanged,unexpectedVisibility=sorted(unexpected),exactChangedAllowlist=set(vischanged)==expectedChanged,missingHides=missinghides,explicitOriginalGuideGroundChanges=guides,newMeshes=len(new),nonfiniteGeometry=badgeo,missingUV=missinguv,nonfiniteOrNonNormalizedCornerUV=baduv,nonfiniteCornerNormals=normbad,opticFrameMaxDelta=max(deltas.values()),opticMaximumSeatRadiusSourceUnits=radius,optic42SeatPass=radius<=42.00001,opticFramePass=max(deltas.values())<1e-6,emissions=emissions,eraOpticEmissionPass=all(v==0 for v in emissions.values()) if era!='builder' else all(v==(5 if ' core ' in n else 0) for n,v in emissions.items()),approvedPosePreserved=not originalchanges,bodyFeetNewGeometry=geo)
  report['eras'][era]=eraresult
  checks=[not originalchanges,not graphchanges,not imagechanges,not sameSaved,not unexpected,not missinghides,not badgeo,not baduv,not missinguv,not normbad,eraresult['optic42SeatPass'],eraresult['opticFramePass'],eraresult['eraOpticEmissionPass']]
  eraresult['pass']=all(checks)
  if not eraresult['pass']:report['blockingIssues'].append(f'{era}: inspect failed era checks')
  save_report();print('PREFLIGHT ERA COMPLETE',era,'PASS',eraresult['pass'],'new',len(new),'changedVisibility',len(vischanged),flush=True)
 report['bodyFeetGeometryCrossEraDeterministic']=newgeometry['builder']==newgeometry['maker']==newgeometry['mechanic']
 if not report['bodyFeetGeometryCrossEraDeterministic']:report['blockingIssues'].append('Body/feet raw geometry/UV/face-slot fingerprints differ across eras')
 save_report()
 # Reopen disposable Builder only; export is written solely under the disposable directory.
 bpy.ops.wm.open_mainfile(filepath=str(O/'hypothetical-builder.blend'),use_scripts=False);s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=2;s.cycles.device='CPU';report['builderExport']=dict(status='RUNNING');save_report();print('PREFLIGHT EXPORT START',flush=True)
 exp=ex.export(s,O/'hypothetical-builder.glb',batched=True);(O/'builder-export-receipt.json').write_text(json.dumps(exp,indent=2));raw=(O/'hypothetical-builder.glb').read_bytes();jslen=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+jslen]);(O/'builder-glb-json.json').write_text(json.dumps(doc,indent=2))
 attrs=[q['attributes'] for x in doc['meshes'] for q in x['primitives']]
 checks=dict(allImagesEmbedded=all('bufferView' in x and 'uri' not in x for x in doc.get('images',[])),noBufferURI=all('uri' not in x for x in doc.get('buffers',[])),noSkins=not doc.get('skins'),noAnimations=not doc.get('animations'),allPrimitivesPositionNormalUV=all({'POSITION','NORMAL','TEXCOORD_0'}<=set(x) for x in attrs),faceMaterialParity=exp['face_material_parity'],nativeMeshesUnchanged=exp['native_meshes_unchanged'],temporaryDatablocksRemoved=exp['temporary_datablocks_removed'],uvCornerReadback=exp['uv_corner_readback'])
 report['builderExport']=dict(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,glbPath=str(O/'hypothetical-builder.glb'),sha256=sha(O/'hypothetical-builder.glb'),bytes=len(raw),images=len(doc.get('images',[])),primitiveCount=len(attrs),receiptPath=str(O/'builder-export-receipt.json'))
 if not all(checks.values()):report['blockingIssues'].append('Builder GLB static export checks failed')
except Exception as e:
 report['blockingIssues'].append(str(e));report['exception']=traceback.format_exc();print(report['exception'],flush=True)
finally:
 before=json.loads((O/'before-file-hashes.json').read_text());after={n:dict(sha256=sha(n),bytes=Path(n).stat().st_size) for n in before};(O/'after-file-hashes.json').write_text(json.dumps(after,indent=2));report['trackedInputSourceScriptCustody']=dict(pathsChecked=len(before),changed=[n for n in before if before[n]!=after[n]],beforeProof=str(O/'before-file-hashes.json'),afterProof=str(O/'after-file-hashes.json'));report['decision']='PASS_WITH_LIMITS' if not report['blockingIssues'] and len(report['eras'])==3 and report.get('builderExport',{}).get('status')=='PASS' and before==after else 'BLOCKING_ISSUE';save_report();print('PREFLIGHT FINAL',report['decision'],time.time()-start,flush=True)
