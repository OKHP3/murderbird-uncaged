import bpy,json,hashlib
from pathlib import Path
r=Path(__file__).resolve().parents[4];a=Path(__file__).resolve().parent;base=r/'assets/models/whole-character-v38/bill-relationship02/murderbird-v38-bill-relationship02.blend';assert hashlib.sha256(base.read_bytes()).hexdigest()=='e5e7feb29582b6f3f85d0b767038220b7b29e332729b178938e4292ee5b2d329';bpy.ops.wm.open_mainfile(filepath=str(base));names=[o.name for o in bpy.data.objects if o.type=='MESH' and o.parent and (o.parent.name in ['neck','cervical-mid-a','cervical-mid-b','cervical-upper']or o.name.startswith('V29 neck root recessed underlap'))];rows=[]
for n in sorted(names):
 o=bpy.data.objects[n];p=[o.matrix_world@v.co for v in o.data.vertices];d={'name':n,'owner':o.parent.name,'vertices':len(p),'boundsNativeXYZ':[[min(q[k]for q in p),max(q[k]for q in p)]for k in range(3)],'eras':o.get('exteriorEras'),'materials':[m.name if m else None for m in o.data.materials]}
 if n.startswith('V23 cervical') and 'directional guard' in n:
  d['firstRowMedianNative']=[sum(q[k]for q in p[:19])/19 for k in range(3)];d['lastOuterRowMedianNative']=[sum(q[k]for q in p[380:399])/19 for k in range(3)]
 rows.append(d)
frames={n:{'parent':bpy.data.objects[n].parent.name,'originNative':list(bpy.data.objects[n].matrix_world.translation),'restLocalMatrix':[list(t)for t in bpy.data.objects[n].matrix_local]}for n in['neck','cervical-mid-a','cervical-mid-b','cervical-upper','head']};out=a/'source-inventory.json';assert not out.exists();out.write_text(json.dumps({'sourceNativeSha256':hashlib.sha256(base.read_bytes()).hexdigest(),'frames':frames,'objects':rows},indent=2)+'\n');print('GUARDS',json.dumps([q for q in rows if q['name'].startswith('V23 cervical')]),flush=True);print('FRAMES',json.dumps(frames),flush=True)
