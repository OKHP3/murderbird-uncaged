"""Strict saved-native receiving payload readback; visibility changes restricted to head04."""
import bpy,hashlib,json,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'assets/audit/cg-supervised-head05';I=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged/assets/models/cg-supervised01/integration04/murderbird-supervised-builder.blend')
def digest(o):
 h=hashlib.sha256()
 for v in o.data.vertices:h.update(np.asarray(v.co[:],dtype='<f4').tobytes())
 for p in o.data.polygons:h.update(np.asarray(p.vertices[:],dtype='<i4').tobytes());h.update(p.material_index.to_bytes(4,'little'))
 for uv in o.data.uv_layers:
  h.update(uv.name.encode())
  for d in uv.data:h.update(np.asarray(d.uv[:],dtype='<f4').tobytes())
 h.update(np.asarray(o.matrix_world,dtype='<f8').tobytes());h.update(str((o.parent.name if o.parent else None,[m.name if m else None for m in o.data.materials])).encode())
 return h.hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(I));s=bpy.context.scene
meshes={o.name:digest(o) for o in s.objects if o.type=='MESH'};anchors={o.name:[list(r) for r in o.matrix_world] for o in s.objects if o.type=='EMPTY'};vis={o.name:(o.hide_render,bool(o.get('cgSupervisedHead04')),o.get('cg1cRegion')) for o in s.objects if o.type=='MESH'}
result={}
for a in ('attempt01','attempt02'):
 bpy.ops.wm.open_mainfile(filepath=str(O/a/'connected-head05.blend'));s=bpy.context.scene
 changed=[n for n,h in meshes.items() if digest(s.objects[n])!=h];moved=[n for n,h in anchors.items() if [list(r) for r in s.objects[n].matrix_world]!=h]
 hide=[n for n,(v,_,_) in vis.items() if v!=s.objects[n].hide_render]
 badhide=[n for n in hide if not vis[n][1] or vis[n][2]!='head']
 result[a]={'original_mesh_count':len(meshes),'mesh_geometry_faces_indices_uv_names_values_slots_parents_transforms_changed':changed,'anchor_transforms_changed':moved,'visibility_changed':hide,'visibility_changes_outside_head04':badhide,'pass':not changed and not moved and not badhide}
 assert result[a]['pass']
(O/'preservation.json').write_text(json.dumps(result,indent=2)+'\n')
print('HEAD05_PRESERVATION_PASS',flush=True)
