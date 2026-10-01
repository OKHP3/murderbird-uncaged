import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/models/whole-character-v38/breast-envelope02/murderbird-v38-breast-envelope02.blend'))
names=['V23 breast moving return -1','V23 breast moving return 1','V28 sternal to hip load bow -1','V28 sternal to hip load bow 1','Power retaining strap','V30 continuous tapered breast liner'];records={}
for n in names:
 o=bpy.data.objects[n];v=[o.matrix_world@p.co for p in o.data.vertices];records[n]={'owner':o.parent.name,'nativeVertexCount':len(v),'bounds':[(min(p[i]for p in v),max(p[i]for p in v))for i in range(3)],'sections':[{'z':z,'count':len(q),'x':[(min(p.x for p in q),max(p.x for p in q))],'y':[(min(p.y for p in q),max(p.y for p in q))]}for z in(.72,.76,.80,.84,.88,.92,.96)if(q:=[p for p in v if abs(p.z-z)<.015])]}
 if len(v)==248:records[n]['ringCenters']=[{'ring':r,'centerWorld':list(sum(v[r*8:r*8+8],Vector())/8)}for r in range(31)]
(Path(__file__).parent/'source-stock-inspection.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(records))
