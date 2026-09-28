from pathlib import Path
import hashlib,json,runpy
import bpy
R=Path(__file__).resolve().parents[3]
H=runpy.run_path(str(R/'scripts/build-uncaged-alignment-v7.py'),run_name='v9_comparison_helpers')
paths=[R/'assets/models/uncaged-alignment-v8/murderbird-alignment-v8.blend',R/'assets/models/uncaged-bill-root-fixing-study-v1/murderbird-bill-root-fixing-study-v1.blend']
expected=['b12c442e2f517b676cdd1fae1612730cc0ba83251d34f363285b08f2cd482478','4d7568d1c2ba7cab716876f57a6c20cb6a788d4daeef1d5d34f85c1910ed2bbe']
s=[];m=[]
for p,h in zip(paths,expected):
 assert hashlib.sha256(p.read_bytes()).hexdigest()==h
 bpy.ops.wm.open_mainfile(filepath=str(p));s.append(H['scene_snapshot']());m.append({x.name:H['material_signature'](x) for x in bpy.data.materials})
assert s[0]['empties']==s[1]['empties'] and s[0]['curves']==s[1]['curves'] and m[0]==m[1]
assert set(s[0]['meshes'])==set(s[1]['meshes'])
changes=[]
for n,a in s[0]['meshes'].items():
 b=s[1]['meshes'][n]
 if a!=b:changes.append({'name':n,'changedFields':[k for k in a if a[k]!=b[k]]})
p=Path(__file__).with_name('v8-native-comparison.json');assert not p.exists()
p.write_text(json.dumps({'sources':[{'path':str(p.relative_to(R)),'sha256':h} for p,h in zip(paths,expected)],'changedMeshes':changes,'unchangedMeshCount':len(s[0]['meshes'])-len(changes),'pivotsExact':len(s[0]['empties']),'guidesExact':len(s[0]['curves']),'materialSignaturesExact':True},indent=2)+'\n')
print(json.dumps(changes))
