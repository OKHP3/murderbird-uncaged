"""Export one saved, hash-bound whole-body candidate without changing native."""
from pathlib import Path
import bpy,hashlib,json,runpy,shutil,argparse,sys
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--attempt',default='01');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
AUDIT=ROOT/f'assets/audit/whole-body-v10/attempt-{a.attempt}'
receipt=json.loads((AUDIT/'receipt.json').read_text())
native=ROOT/receipt['native']['path'];glb=native.with_suffix('.glb')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
assert sha(native)==receipt['native']['sha256'] and not glb.exists()
helper=ROOT/receipt['helper']['path'];assert sha(helper)==receipt['helper']['sha256']
shutil.copy2(__file__,AUDIT/'executed-export.py')
h=runpy.run_path(str(helper),run_name='whole_body_export_helpers')
bpy.ops.wm.open_mainfile(filepath=str(native));snapshot=h['scene_snapshot']()
mods={o.name:h['modifier_signature'](o) for o in bpy.data.objects if o.type=='MESH' and o.modifiers}
h['export_from_reopened_native'](native,glb,snapshot,mods)
assert sha(native)==receipt['native']['sha256']
out={'status':'diagnostic runtime derivative; not selected','native':receipt['native'],
 'glb':{'path':str(glb.relative_to(ROOT)),'sha256':sha(glb),'bytes':glb.stat().st_size},
 'exporter':{'path':str((AUDIT/'executed-export.py').relative_to(ROOT)),'sha256':sha(AUDIT/'executed-export.py')},
 'helper':receipt['helper'],'pivots':len(snapshot['empties']),
 'checks':{'nativeSaveReopenSnapshotExact':True,'editableNativeUnmodified':True,'pivotWorldMatricesUnchangedByExport':True},
 'limits':['Runtime behavior, native/export surface parity and strict intersections require separate verification.','Grouping retains rigid owner, era, region and surface role. No deformation or texture changes.']}
(AUDIT/'export-receipt.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out))
