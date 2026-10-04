import bpy,json,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');J=Path('/tmp/cg-cranial-projection-diagnosis15.json');d=json.loads(J.read_text());bpy.ops.wm.open_mainfile(filepath=str(R/'assets/audit/cg-supervised-head13/attempt02/formed-head13.blend'));s=bpy.context.scene;inv=s.objects['CG2b head frame'].matrix_world.inverted();dg=bpy.context.evaluated_depsgraph_get();A=np.array(d['matrix']);b=np.array(d['offset']);tops=[[],[]];count=0;objects=0
for o in s.objects:
 if o.type!='MESH' or o.hide_render or o.get('authoringGuide') or o.get('cgSupervisedHead13') or max((o.matrix_world@Vector(c)).z for c in o.bound_box)<1.3:continue
 e=o.evaluated_get(dg);me=e.to_mesh();v=np.array([list(inv@(o.matrix_world@q.co)) for q in me.vertices]);e.to_mesh_clear()
 if len(v)==0:continue
 count+=len(v);objects+=1
 for j in range(2):
  px=v@A[2*j:2*j+2].T+b[2*j:2*j+2];i=px[:,1].argmin();tops[j].append({'owner':o.name,'px':px[i].tolist(),'head_local':v[i].tolist()})
d['all_original_upper_visible_vertices_check']={'selection':'all retained original render-visible meshes with max world boundbox z>=1.3m, authoringGuide excluded','mesh_count':objects,'evaluated_vertex_count':count,'highest_per_projection':[min(t,key=lambda v:v['px'][1]) for t in tops],'proposed_apex_px':[d['hypothetical_projections'][n]['near_crest_apex']['px'] for n in d['hypothetical_projections']]};d['all_original_upper_visible_vertices_check']['apex_wins_both']=all(d['all_original_upper_visible_vertices_check']['proposed_apex_px'][j][1]<d['all_original_upper_visible_vertices_check']['highest_per_projection'][j]['px'][1] for j in range(2))
Path('/tmp/cg-diagnosis15-upper-proof.json').write_text(json.dumps(d['all_original_upper_visible_vertices_check'],indent=2));J.write_text(json.dumps(d,indent=2));print('UPPER',d['all_original_upper_visible_vertices_check'])
