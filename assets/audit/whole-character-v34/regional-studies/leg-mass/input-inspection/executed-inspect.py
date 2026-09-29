import bpy,json,hashlib
from pathlib import Path
R=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
p=R/'assets/models/whole-character-v33/attempt-form06/murderbird-whole-character-v33.blend'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='5fdfe66693db848fcf624b28484c3eaba220a8d7f389248390a4f21a571d108d'
bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.view_layer.update()
r={'baseSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'pivots':{},'meshes':[]}
for s in ('left','right'):
 for k in ('thigh','shin','foot'):
  o=bpy.data.objects[s+'-'+k];r['pivots'][o.name]={'world':[list(x) for x in o.matrix_world],'parent':o.parent.name}
for o in bpy.data.objects:
 if o.type=='MESH' and o.parent and o.parent.name in ('left-thigh','left-shin','right-thigh','right-shin'):
  pts=[o.matrix_world@v.co for v in o.data.vertices];r['meshes'].append({'name':o.name,'owner':o.parent.name,'role':o.get('surfaceRole'),'props':dict(o.items()),'materials':[m.name for m in o.data.materials],'vertices':len(pts),'min':[min(p[k] for p in pts) for k in range(3)],'max':[max(p[k] for p in pts) for k in range(3)]})
(R/'assets/audit/whole-character-v34/regional-studies/leg-mass/input-inspection/inventory.json').write_text(json.dumps(r,indent=2,default=lambda x:list(x)))
print(json.dumps({'pivots':r['pivots'],'meshes':len(r['meshes'])}))
