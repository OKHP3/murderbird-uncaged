import bpy,runpy,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[4];h=runpy.run_path(str(root/'scripts/build-uncaged-alignment-v7.py'));native=root/'assets/models/whole-character-v19/attempt-torso04/murderbird-whole-character-v19.blend';source=root/'scripts/regions/whole-character-v19-torso-neck.py'
bpy.ops.wm.open_mainfile(filepath=str(native));old=h['scene_snapshot']()
bpy.ops.wm.open_mainfile(filepath=str(root/'assets/models/whole-character-v18/attempt-01/murderbird-whole-character-v18.blend'));runpy.run_path(str(source))['apply']();new=h['scene_snapshot']()
differences=[]
for name,o in old['meshes'].items():
 n=new['meshes'][name]
 if o!=n:differences.append({'name':name,'keys':[k for k in o if o[k]!=n[k]]})
assert set(old['meshes'])==set(new['meshes'])
assert all(d['keys']==['props'] and 'fasteners' in d['name'] for d in differences),differences
assert old['empties']==new['empties'] and old['curves']==new['curves']
heads={o.name:int(o['anchorHeadCount']) for o in bpy.data.objects if o.type=='MESH' and 'fasteners' in o.name and 'breast' in o.name}
assert sum(heads.values())==78
j={'status':'PASS','preservedNativeSHA256':hashlib.sha256(native.read_bytes()).hexdigest(),'correctedSourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'geometryModifiersMatricesOwnersAndGuidesExactToNative04':True,'metadataOnlyDifferences':differences,'wholeFastenerIslandCounts':heads,'sourceTotalHeads':78,'note':'current source applied in memory; no native rewrite or new geometry candidate'}
(root/'assets/audit/whole-character-v19/torso-work/torso04-metadata-correction.json').write_text(json.dumps(j,indent=2));print(json.dumps(j,indent=2))
