import bpy,json,hashlib
from pathlib import Path
R=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');N=R/'assets/models/whole-character-v35/attempt-form01/murderbird-whole-character-v35.blend';assert hashlib.sha256(N.read_bytes()).hexdigest()=='d2c704ccf89f3f0e7dbeb3613dcdbdd964c4ba69991783783830803eecf59cb0';bpy.ops.wm.open_mainfile(filepath=str(N));bpy.context.view_layer.update();H=bpy.data.objects['head'];origin=H.matrix_world.translation;rows=[]
for o in H.children_recursive:
 if o.type=='MESH':
  p=[o.matrix_world@v.co-origin for v in o.data.vertices];rows.append({'name':o.name,'owner':o.parent.name,'vertices':len(p),'offsetBounds':[[min(v[k] for v in p),max(v[k] for v in p)] for k in range(3)],'eras':o.get('exteriorEras'),'role':o.get('surfaceRole')})
Path(__file__).with_name('inventory.json').write_text(json.dumps({'origin':list(origin),'nodes':{o.name:[list(row) for row in o.matrix_world] for o in [H]+[o for o in H.children_recursive if o.type=='EMPTY']},'meshes':rows},indent=2)+'\n')
print('origin',list(origin));print('\n'.join(str(row) for row in rows if row['name'].startswith(('V32 returned','V32 formed mandibular','V33 diagonal','V33 formed lower','V31 optic','V31 jaw'))))
