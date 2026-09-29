import bpy,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[4];base=root/'assets/models/whole-character-v19/attempt-02/murderbird-whole-character-v19.blend';expected='d98c46770101ad608fe2c50212a7b307ca66d5389f93ce7d43b79b9c7d41dded';assert hashlib.sha256(base.read_bytes()).hexdigest()==expected
bpy.ops.wm.open_mainfile(filepath=str(base));nodes=[];bounds={};dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
 if o.type=='EMPTY':nodes.append({'name':o.name,'parent':o.parent.name if o.parent else None,'world':[list(r) for r in o.matrix_world],'local':[list(r) for r in o.matrix_local]})
 if o.type=='MESH' and o.parent:
  key=o.parent.name;e=o.evaluated_get(dg);m=e.to_mesh();p=[e.matrix_world@v.co for v in m.vertices];e.to_mesh_clear()
  b=bounds.setdefault(key,{'min':[1e9]*3,'max':[-1e9]*3,'names':[]});b['names'].append(o.name)
  for i in range(3):b['min'][i]=min(b['min'][i],min(v[i] for v in p));b['max'][i]=max(b['max'][i],max(v[i] for v in p))
j={'native':str(base.relative_to(root)),'sha256':expected,'nodes':nodes,'meshBoundsByOwner':bounds};out=root/'assets/audit/whole-character-v20/input/inventory.json';assert not out.exists();out.write_text(json.dumps(j,indent=2));print(json.dumps({'nodes':[(n['name'],n['parent'],[n['world'][i][3] for i in range(3)]) for n in nodes]},indent=2))
