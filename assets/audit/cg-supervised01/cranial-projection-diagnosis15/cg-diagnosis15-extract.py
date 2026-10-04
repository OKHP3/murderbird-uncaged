import bpy,json,hashlib,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');N=R/'assets/audit/cg-supervised-head13/attempt02/formed-head13.blend';B=R/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend';O=Path('/tmp/cg-diagnosis15-actual-envelope.json')
bpy.ops.wm.open_mainfile(filepath=str(N));s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();inv=s.objects['CG2b head frame'].matrix_world.inverted();vs={}; allv={}
for o in s.objects:
 if o.type!='MESH' or o.get('authoringGuide'):continue
 if not (o.get('cg1cRegion')=='head' or o.get('cg2bRegion')=='head' or o.name.startswith(('CGH05','CGH06','CGH13'))):continue
 e=o.evaluated_get(dg);m=e.to_mesh();v=np.array([list(inv@(o.matrix_world@q.co)) for q in m.vertices]);e.to_mesh_clear()
 if len(v):
  allv[o.name]=v
  if not o.hide_render:vs[o.name]=v
rows=json.loads((R/'assets/audit/cg-supervised-head12/projection-feasibility.json').read_text())['affine_projection_rows']; optics={}
for name,v in allv.items():
 if 'optical glass' in name or 'optic seat' in name:
  optics[name]={'min':v.min(0).tolist(),'max':v.max(0).tolist(),'mid':((v.min(0)+v.max(0))/2).tolist()}
orig=np.concatenate([v for n,v in allv.items() if not n.startswith('CGH13')]); retained=np.concatenate([v for n,v in vs.items() if not n.startswith('CGH13')]);tops={}
for name,rr in rows.items():
 a=np.array(rr['A_pixel_per_head_local_m']);b=np.array(rr['b_pixels']);t=[]
 for n,v in vs.items():
  px=v@a.T+b;i=px[:,1].argmin();t.append({'owner':n,'head_local':v[i].tolist(),'px':px[i].tolist(),'count':len(v)})
 tops[name]=sorted(t,key=lambda q:q['px'][1])[:15]
x={'sha_before':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [N,B]},'frame':list(map(list,s.objects['CG2b head frame'].matrix_world)),'original_all_head_bounds':[orig.min(0).tolist(),orig.max(0).tolist()],'retained_visible_original_head_bounds':[retained.min(0).tolist(),retained.max(0).tolist()],'optics':optics,'tops':tops,'original_evaluated_vertex_count':len(orig),'retained_evaluated_vertex_count':len(retained),'visible_head_vertices':{n:v.tolist() for n,v in vs.items()}}
O.write_text(json.dumps(x));print('BOUNDS',x['original_all_head_bounds'],x['retained_visible_original_head_bounds']);print('OPTICS',json.dumps(optics));print('DONE',O)
