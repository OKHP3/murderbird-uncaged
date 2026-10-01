import bpy,json,sys,hashlib
from pathlib import Path
model,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(model));rows=[]
for o in bpy.data.objects:
 if o.type!='MESH' or not any(x in o.name for x in['fixed temporal receiving wall','swept temporal leaf','compact cranial inner shell','fixed occipital closure','swept crown course']):continue
 p=[o.matrix_world@v.co for v in o.data.vertices];rows.append({'name':o.name,'owner':o.parent.name,'vertices':len(p),'eras':o.get('exteriorEras'),'materials':[m.name if m else None for m in o.data.materials],'bounds':[[min(v[k]for v in p),max(v[k]for v in p)]for k in range(3)]})
out.write_text(json.dumps({'nativeSha256':hashlib.sha256(model.read_bytes()).hexdigest(),'regionalObjects':rows},indent=2)+'\n');print(json.dumps([q for q in rows if not'swept crown'in q['name']],indent=1))
