import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/models/whole-character-v38/lower-support02/murderbird-v38-lower-support02.blend'));bpy.context.view_layer.update();out={}
for side in(-1,1):
 n=f'V31 passive cranial load bow {side}';o=bpy.data.objects[n];v=[o.matrix_world@v.co for v in o.data.vertices];out[n]={'verts':len(v),'firstFaces':[list(f.vertices)for f in list(o.data.polygons)[:4]],'centers':[[sum(p[k]for p in v[i*11:(i+1)*11])/11 for k in range(3)]for i in range(51)],'world':[list(p)for p in v]};print(n,len(v),out[n]['firstFaces']);print('ROWS',[(i,out[n]['centers'][i])for i in range(0,51,5)])
(OUT/'source-bow-stock.json').write_text(json.dumps(out,indent=2)+'\n')
