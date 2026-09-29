import bpy,json,hashlib
from pathlib import Path
R=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');P=R/'assets/models/whole-character-v35/attempt-form01/murderbird-whole-character-v35.blend';assert hashlib.sha256(P.read_bytes()).hexdigest()=='d2c704ccf89f3f0e7dbeb3613dcdbdd964c4ba69991783783830803eecf59cb0'
bpy.ops.wm.open_mainfile(filepath=str(P));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();out={'nodes':{},'meshes':[]}
for o in bpy.data.objects:
 if o.type=='EMPTY' and o.name in ['body','left-mantle','right-mantle','left-wing-shield','right-wing-shield']:
  out['nodes'][o.name]={'parent':o.parent.name if o.parent else None,'world':[list(r) for r in o.matrix_world],'local':[list(r) for r in o.matrix_local]}
 if o.type!='MESH' or not o.parent:continue
 if o.parent.name not in ['left-mantle','right-mantle','left-wing-shield','right-wing-shield'] and not ('scapular' in o.name or 'oblique shoulder' in o.name or 'shoulder journal' in o.name):continue
 ev=o.evaluated_get(dg);m=ev.to_mesh();pts=[ev.matrix_world@v.co for v in m.vertices];ev.to_mesh_clear()
 out['meshes'].append({'name':o.name,'owner':o.parent.name,'role':o.get('surfaceRole'),'bounds':[[min(p[k] for p in pts),max(p[k] for p in pts)] for k in range(3)],'material':[m.name for m in o.data.materials],'eras':o.get('exteriorEras')})
a=R/'assets/audit/whole-character-v37/regional-studies/shoulder-assembly/input/inventory.json';a.write_text(json.dumps(out,indent=2)+'\n');print('NODES',out['nodes'])
for o in out['meshes']:print(o['name'],o['owner'],o['role'],o['bounds'])
