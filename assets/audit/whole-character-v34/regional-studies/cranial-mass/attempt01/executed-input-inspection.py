from pathlib import Path
import bpy,json,hashlib
p=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/models/whole-character-v33/attempt-form06/murderbird-whole-character-v33.blend');assert hashlib.sha256(p.read_bytes()).hexdigest()=='5fdfe66693db848fcf624b28484c3eaba220a8d7f389248390a4f21a571d108d';bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();owners=['head','cranial-cover','builder-optics','upper-bill','jaw'];nodes=[];meshes=[]
for name in owners:
 o=bpy.data.objects[name];nodes.append({'name':name,'parent':o.parent.name if o.parent else None,'world':[list(r) for r in o.matrix_world],'local':[list(r) for r in o.matrix_local],'props':dict(o.items())})
for o in bpy.data.objects:
 if o.type!='MESH' or not o.parent or o.parent.name not in owners:continue
 e=o.evaluated_get(dg);m=e.to_mesh();v=[e.matrix_world@q.co for q in m.vertices];e.to_mesh_clear();meshes.append({'name':o.name,'owner':o.parent.name,'role':o.get('surfaceRole'),'region':o.get('region'),'eras':o.get('exteriorEras'),'bounds':[[min(q[k] for q in v) for k in range(3)],[max(q[k] for q in v) for k in range(3)]]})
Path('/tmp/v34-cranial-mass/input.json').write_text(json.dumps({'nativeSHA256':hashlib.sha256(p.read_bytes()).hexdigest(),'nodes':nodes,'meshes':meshes},indent=2,default=lambda x:list(x))+'\n');print('READONLY COMPLETE')
