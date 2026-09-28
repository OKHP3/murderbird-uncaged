"""Focus the actual Mechanic pose on the liner/brace same-owner pair."""
from pathlib import Path
import hashlib,json,runpy
import bpy
ROOT=Path(__file__).resolve().parents[5]
NATIVE=ROOT/'assets/models/uncaged-cervical-joint-drive-study-v1/iterations/attempt-02/murderbird-cervical-joint-drive-study-v1.blend';NSHA='dff9cf74e0b10819f86efed1bdf5c292ae38619d962d18afeba2b2cca291b9d1'
PACKET=ROOT/'assets/audit/cervical-runtime-study-v1/expanded-runtime-poses/pose-snapshot.json';PSHA='1cb4a2f75ecae625a44c768ba543e9b99e1caa9791a3056e20f5d88bd73d2f26'
OUT=Path(__file__).resolve().parent/'mechanic-interface-review.json'; SRC=ROOT/'assets/audit/cervical-construction-study-v1/attempt-14/all-cervical-roles-source13-baseline/executed-review.py';GEOM=ROOT/'scripts/diagnose-native-regional-clearance.py'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(NATIVE)==NSHA and sha(PACKET)==PSHA and not OUT.exists()
h=runpy.run_path(str(SRC),run_name='focused_mech_helpers');g=runpy.run_path(str(GEOM),run_name='focused_mech_geometry')
bpy.ops.wm.open_mainfile(filepath=str(NATIVE));pivots={o.name:o for o in bpy.data.objects if o.type=='EMPTY'};packet=json.loads(PACKET.read_text())
liner=bpy.data.objects['Joint-drive fixed bearing liner +1'];brace=bpy.data.objects['Mechanic passive cervical lock brace +X'];rows=[]
for pose in packet['poses']:
 h['set_pose'](pose,pivots);dg=bpy.context.evaluated_depsgraph_get();a=g['surface'](liner,dg);b=g['surface'](brace,dg)
 pairs=a['tree'].overlap(b['tree']) if a and b and g['bounds_overlap'](a,b) else []
 rows.append({'pose':pose['id'],'triangleCandidates':len(pairs)})
OUT.write_text(json.dumps({'nativeSha256':NSHA,'packetSha256':PSHA,'pair':['Joint-drive fixed bearing liner +1','Mechanic passive cervical lock brace +X'],'poses':rows},indent=2)+'\n');print(json.dumps(rows,indent=2))
