import bpy,json,hashlib
from pathlib import Path
r=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
out=Path('/Users/okh/.codex/worktrees/cg-supervised-export01/murderbird-uncaged/assets/audit/cg-recursive-delivery01/era-receiving-counts.json')
manifest=json.loads((r/'assets/audit/cg-supervised01/attempt09/frozen-manifest.json').read_text());pins={f['path']:f['sha256'] for f in manifest['files']};result={}
for era in ('builder','maker','mechanic'):
 rel=f'assets/models/cg-supervised01/attempt09/murderbird-supervised-{era}.blend';p=r/rel;actual=hashlib.sha256(p.read_bytes()).hexdigest();assert actual==pins[rel]
 bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene
 result[era]={'source':str(p),'sha256':actual,'mesh_empty':sum(o.type in ('MESH','EMPTY') for o in s.objects),'meshes':sum(o.type=='MESH' for o in s.objects),'empties':sum(o.type=='EMPTY' for o in s.objects),'materials':len(bpy.data.materials),'file_images':sum(i.source=='FILE' for i in bpy.data.images),'packed_images':sum(bool(i.packed_file) for i in bpy.data.images)}
 print('DELIVERY_SAVED09_COUNTS',era,result[era],flush=True)
out.write_text(json.dumps(result,indent=2)+'\n');print('DELIVERY_SAVED09_COUNTS_COMPLETE',flush=True)
