from pathlib import Path
import hashlib,json,runpy
import bpy
R=Path(__file__).resolve().parents[3]
hp=R/'scripts/build-uncaged-alignment-v7.py'
assert hashlib.sha256(hp.read_bytes()).hexdigest()=='39b6ee2285d8c49df3a902f8fac0a07589da3d41f48ae24df1e06515c839033a'
H=runpy.run_path(str(hp),run_name='leg_supervisor_comparison')
paths=[R/'assets/models/uncaged-alignment-v8/murderbird-alignment-v8.blend',R/'assets/models/uncaged-lower-leg-construction-study-v1/murderbird-lower-leg-construction-study-v1.blend']
expected=['b12c442e2f517b676cdd1fae1612730cc0ba83251d34f363285b08f2cd482478','415a3aa7976c271c28187eb4ee1440dbcd858f4dfb5b84cb6ed69e381def982f']
s=[];m=[]
for p,h in zip(paths,expected):
 assert hashlib.sha256(p.read_bytes()).hexdigest()==h
 bpy.ops.wm.open_mainfile(filepath=str(p));s.append(H['scene_snapshot']());m.append({x.name:H['material_signature'](x) for x in bpy.data.materials})
assert s[0]['empties']==s[1]['empties'] and s[0]['curves']==s[1]['curves'] and m[0]==m[1]
assert set(s[0]['meshes'])<=set(s[1]['meshes'])
for n,a in s[0]['meshes'].items():assert a==s[1]['meshes'][n],n
added=sorted(set(s[1]['meshes'])-set(s[0]['meshes']));assert len(added)==10
for n in added:
 o=bpy.data.objects[n];assert o.parent.name==('left-shin' if n.startswith('left ') else 'right-shin')
 assert o['exteriorEras']=='maker,mechanic,builder'
out=Path(__file__).with_name('supervisor-native-comparison.json');assert not out.exists()
out.write_text(json.dumps({'status':'exact inherited-record preservation confirmed; no movement or attachment-clearance claim','sources':[{'path':str(p.relative_to(R)),'sha256':h} for p,h in zip(paths,expected)],'addedMeshes':added,'unchangedMeshCount':len(s[0]['meshes']),'pivotsExact':len(s[0]['empties']),'guidesExact':len(s[0]['curves']),'materialSignaturesExact':True,'newOwners':'five rigid additions under each shin','newEraEligibility':'all three eras, passive geometry'},indent=2)+'\n')
print(out.read_text())
