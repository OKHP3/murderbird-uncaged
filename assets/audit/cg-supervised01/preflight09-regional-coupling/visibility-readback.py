import bpy,json,hashlib,time
from pathlib import Path
O=Path('/tmp/cg-preflight09');P=Path('/tmp/cg-preflight09.json');r=json.loads(P.read_text());out={}
for e in ['builder','maker','mechanic']:
 a=json.loads((O/f'{e}-receiving-snapshot.json').read_text());ret=r['moduleReturnRecords'][e];oph=set(ret['optic13']['hidden_originals']);bo=set(ret['body15']['hiddenLegacyManifest']);fh=set(ret['feet14']['hiddenOriginals']);bpy.ops.wm.open_mainfile(filepath=str(O/f'hypothetical-{e}.blend'),use_scripts=False);s=bpy.context.scene;bad=[]
 for n,v in a['visibility'].items():
  expected=list(v)
  if n in oph|bo:expected[0]=True;expected[2]=True
  if n in fh:expected[0]=True
  actual=[s.objects[n].hide_render,s.objects[n].hide_viewport,s.objects[n].hide_get()] if n in s.objects else None
  if actual!=expected:bad.append(dict(name=n,expected=expected,actual=actual))
 out[e]=dict(originalVisibilityRecordsChecked=len(a['visibility']),opticOriginalNames=len(oph),bodyOriginalNames=len(bo),feetOriginalNames=len(fh),combinedNames=len(oph|bo|fh),allModuleHideFlagsAndOutsideFlagsExact=not bad,failures=bad)
r['exactModuleFlagReadback']=out
if any(v['failures'] for v in out.values()):r['blockingIssues'].append('Exact module visibility flags fail');r['decision']='BLOCKING_ISSUE'
r['proofPaths']=dict(script=str(O/'test.py'),log=str(O/'blender.log'),visibilitySupplementScript=str(O/'visibility-readback.py'),originalSnapshots=[str(O/f'{e}-receiving-snapshot.json') for e in ['builder','maker','mechanic']],receipts=str(O/'receipt-pins.json'))
r['selectedReceiptIdentity']=json.loads((O/'receipt-pins.json').read_text());P.write_text(json.dumps(r,indent=2));print('EXACT MODULE FLAGS',json.dumps(out),flush=True)
