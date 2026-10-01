import bpy,json,runpy,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];A=Path(__file__).resolve().parent;names=[s+' metatarsal passive rail'+suffix for s in ('left','right')for suffix in ('','.001')]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/models/whole-character-v38/upper-contour01/murderbird-v38-upper-contour01.blend'));source={n:{'vertices':[list(v.co)for v in bpy.data.objects[n].data.vertices],'faces':[list(p.vertices)for p in bpy.data.objects[n].data.polygons]}for n in names}
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/models/whole-character-v38/lower-support02/murderbird-v38-lower-support02.blend'));out=[]
for n in names:
 o=bpy.data.objects[n];v=[list(p.co)for p in o.data.vertices[:8]];f=[list(p.vertices)for p in o.data.polygons[:6]];assert v==source[n]['vertices'];assert f==source[n]['faces'];out.append({'name':n,'original8LocalVerticesByteValuesExact':True,'original6FaceIndicesAndWindingExact':True,'currentNativeVertices':len(o.data.vertices),'sourceStockSha256':hashlib.sha256(json.dumps(source[n],sort_keys=True).encode()).hexdigest()})
(A/'post-export-end-proof.json').write_text(json.dumps({'status':'PASS source end/core stock exact after native save/reopen; additional midspan jacket stock is separate fixed fabrication proposal','rails':out},indent=2)+'\n');print(json.dumps(out))
