from pathlib import Path
import hashlib,json,runpy
import bpy
R=Path(__file__).resolve().parents[3]
hp=R/'scripts/build-uncaged-alignment-v7.py'
assert hashlib.sha256(hp.read_bytes()).hexdigest()=='39b6ee2285d8c49df3a902f8fac0a07589da3d41f48ae24df1e06515c839033a'
H=runpy.run_path(str(hp),run_name='leg_supervisor_comparison')
paths=[R/'assets/models/uncaged-cervical-construction-study-v1/attempt-14/murderbird-cervical-construction-study-v1.blend',R/'assets/models/uncaged-cervical-joint-drive-study-v1/iterations/attempt-02/murderbird-cervical-joint-drive-study-v1.blend']
expected=['ef9e28ddbce9d62aabc8181a058640ea1e8b7a339b673df37b913d96699f9440','dff9cf74e0b10819f86efed1bdf5c292ae38619d962d18afeba2b2cca291b9d1']
s=[];m=[]
for p,h in zip(paths,expected):
 assert hashlib.sha256(p.read_bytes()).hexdigest()==h
 bpy.ops.wm.open_mainfile(filepath=str(p));s.append(H['scene_snapshot']());m.append({x.name:H['material_signature'](x) for x in bpy.data.materials})
assert s[0]['empties']==s[1]['empties'] and s[0]['curves']==s[1]['curves'] and m[0]==m[1]
assert set(s[0]['meshes'])<=set(s[1]['meshes'])
for n,a in s[0]['meshes'].items():assert a==s[1]['meshes'][n],n
added=sorted(set(s[1]['meshes'])-set(s[0]['meshes']));assert len(added)==7
for n in added:
 o=bpy.data.objects[n];assert o.parent.name in ('neck','cervical-upper')
 assert o['exteriorEras'] in ('maker,mechanic,builder','maker','mechanic','builder')
out=Path(__file__).with_name('supervisor-native-comparison.json');assert not out.exists()
out.write_text(json.dumps({'status':'exact inherited-record preservation confirmed; no movement or attachment-clearance claim','sources':[{'path':str(p.relative_to(R)),'sha256':h} for p,h in zip(paths,expected)],'addedMeshes':added,'unchangedMeshCount':len(s[0]['meshes']),'pivotsExact':len(s[0]['empties']),'guidesExact':len(s[0]['curves']),'materialSignaturesExact':True,'newOwners':'rigid additions under neck or cervical-upper','newEraEligibility':{n:bpy.data.objects[n]['exteriorEras'] for n in added}},indent=2)+'\n')
print(out.read_text())
