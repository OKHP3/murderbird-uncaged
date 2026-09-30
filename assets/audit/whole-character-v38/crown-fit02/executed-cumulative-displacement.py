"""Read-only actual vertex displacement from frozen crown02 through both fit steps."""
import bpy,json,sys,hashlib
from pathlib import Path
base,first,final,output=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not output.exists()
def read(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update()
 return {o.name:[o.matrix_world@v.co for v in o.data.vertices] for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('V38 swept crown course ')}
a,b,c=[read(p) for p in [base,first,final]];assert set(a)==set(b)==set(c) and len(c)==58
rows=[]
for name in sorted(c):
 rows.append({'name':name,'fromSourceM':max((p-q).length for p,q in zip(a[name],c[name])),'fromFit01M':max((p-q).length for p,q in zip(b[name],c[name]))})
report={'status':'actual discrete vertex displacement; no sweep claim','inputs':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [base,first,final]],'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'maximumFromSourceM':max(r['fromSourceM'] for r in rows),'maximumFromFit01M':max(r['fromFit01M'] for r in rows),'meshes':rows}
output.write_text(json.dumps(report,indent=2)+'\n');print(report['maximumFromSourceM'],report['maximumFromFit01M'])
