import bpy,json,hashlib,math,sys
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
OUT=Path(__file__).resolve().parent
BASE=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged/assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend')
ATTEMPT=sys.argv[-1] if sys.argv[-1] in ('attempt01','attempt02') else 'attempt01'
R=json.loads((OUT/ATTEMPT/'receipt.json').read_text())
CAMS={k:v for k,v in R['cameras'].items() if k.startswith('after-') and ('wire' not in k)}
def setcam(scene,c):
 scene.camera.matrix_world=Matrix(c['matrix']);scene.camera.data.ortho_scale=c['scale'];scene.camera.data.shift_x,scene.camera.data.shift_y=c['shift'];scene.render.resolution_x,scene.render.resolution_y=c['resolution'];bpy.context.view_layer.update()
def geometry(scene):
 dg=bpy.context.evaluated_depsgraph_get();vs=[];fs=[];owners=[];counts={}
 for o in scene.objects:
  if o.type!='MESH' or o.hide_render or o.get('authoringGuide'):continue
  # All prior-to-lens rays are horizontal or descending from higher cameras;
  # no object entirely below z1.30 can become the first hit at a z>1.5 lens.
  if max((o.matrix_world@Vector(c)).z for c in o.bound_box)<1.30:continue
  e=o.evaluated_get(dg);m=e.to_mesh();off=len(vs);vs.extend(o.matrix_world@v.co for v in m.vertices);fs.extend(tuple(off+i for i in f.vertices) for f in m.polygons);owners.extend([o.name]*len(m.polygons));counts[o.name]=len(m.polygons);e.to_mesh_clear()
 return BVHTree.FromPolygons(vs,fs),owners,counts
def targets(scene):
 dg=bpy.context.evaluated_depsgraph_get();out={}
 for o in scene.objects:
  if 'recessed optical glass' not in o.name or o.hide_render:continue
  e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();points={tuple(round(c,7) for c in o.matrix_world@v.co) for v in m.vertices}
  for tri in m.loop_triangles:
   a,b,c=[o.matrix_world@m.vertices[i].co for i in tri.vertices]
   for weights in [(1/3,1/3,1/3),(.6,.2,.2),(.2,.6,.2),(.2,.2,.6)]:points.add(tuple(round(v,7) for v in a*weights[0]+b*weights[1]+c*weights[2]))
  out[o.name]=[Vector(q) for q in sorted(points)];e.to_mesh_clear()
 return out
def hits(tree,owners,qs,d):
 out=[]
 for q in qs:
  hit=tree.ray_cast(q-d*5,d,5.01);out.append(None if hit[0] is None else {'object':owners[hit[2]],'distance':hit[3]})
 return out
bpy.ops.wm.open_mainfile(filepath=str(BASE));scene=bpy.context.scene
qs=targets(scene);tree,owners,counts=geometry(scene);baseline={}
for n,c in CAMS.items():
 setcam(scene,c);d=scene.camera.matrix_world.to_quaternion()@Vector((0,0,-1));baseline[n]={lens:hits(tree,owners,points,d) for lens,points in qs.items()}
 print('HEAD13_BASELINE_RAYS',n,flush=True)
bpy.ops.wm.open_mainfile(filepath=str(OUT/ATTEMPT/'formed-head13.blend'));scene=bpy.context.scene;tree,owners,counts2=geometry(scene);result={};frame=scene.objects['CG2b head frame'].matrix_world
p=lambda x,y,d:Vector((d,(788-x)*.0012+.005,(188-y)*.0012+.020))
named={'posterior_crest':('CGH13 physical posterior crest cage',Vector(R['numerical_fit']['named_control_head_local'])),'near_brow':('CGH13 physical near localized diagonal brow',p(780,135,-.141)),'far_brow':('CGH13 physical far localized diagonal brow',p(780,144,.141)),'foredeck_bill_root':('CGH13 physical compact foredeck bill root',p(862,174,-.084))}
new_eval={};head_eval={};seat_points=[];optic_center=None
for o in scene.objects:
 if o.type!='MESH' or o.hide_render:continue
 if max((o.matrix_world@Vector(c)).z for c in o.bound_box)>=1.30:
  e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();points=[o.matrix_world@v.co for v in m.vertices];head_eval[o.name]=points
  if o.get('cgSupervisedHead13'):new_eval[o.name]=points
  if o.name=='CGH05 integrated optical seat L':seat_points=points
  if o.name=='CGH05 recessed optical glass L':optic_center=sum(points,Vector())/len(points)
  e.to_mesh_clear()
def hull(points):
 q=sorted(set(map(tuple,points)))
 def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
 lower=[]
 for x in q:
  while len(lower)>=2 and cross(lower[-2],lower[-1],x)<=0:lower.pop()
  lower.append(x)
 upper=[]
 for x in reversed(q):
  while len(upper)>=2 and cross(upper[-2],upper[-1],x)<=0:upper.pop()
  upper.append(x)
 return lower[:-1]+upper[:-1]
for n,c in CAMS.items():
 setcam(scene,c);d=scene.camera.matrix_world.to_quaternion()@Vector((0,0,-1));checks={}
 for lens,points in qs.items():
  candidate=hits(tree,owners,points,d);b=baseline[n][lens];window=[i for i,h in enumerate(b) if h and h['object']==lens]
  blocked=[{'sample':i,'actual_curved_target_world':list(points[i]),'baseline_first_hit':b[i],'candidate_first_hit':candidate[i]} for i in window if candidate[i] and candidate[i]['object'].startswith('CGH13')]
  checks[lens]={'actual_curved_surface_samples':len(points),'baseline_window_samples':len(window),'new_roof_brow_interceptions':len(blocked),'interceptions':blocked}
 def proj(q):
  v=world_to_camera_view(scene,scene.camera,q);return [v.x*c['resolution'][0],(1-v.y)*c['resolution'][1]]
 physical={key:{'owner':owner,'declared_control_world':list(frame@q),'nearest_evaluated_surface_world':list(min(new_eval[owner],key=lambda v:(v-frame@q).length_squared)),'projected_px':proj(min(new_eval[owner],key=lambda v:(v-frame@q).length_squared))} for key,(owner,q) in named.items()}
 allv=[(proj(v),name) for name,vs in new_eval.items() for v in vs];headv=[(proj(v),name) for name,vs in head_eval.items() for v in vs];top=min(allv,key=lambda t:t[0][1]);headtop=min(headv,key=lambda t:t[0][1]);E=proj(optic_center);seat_hull=hull([proj(v) for v in seat_points]);D=max(math.dist(a,b) for a in seat_hull for b in seat_hull);bounds=[min(v[0] for v,name in allv),min(v[1] for v,name in allv),max(v[0] for v,name in allv),max(v[1] for v,name in allv)]
 result[n]={'curved_lens_first_hit_checks':checks,'named_physical_landmarks':physical,'whole_evaluated_new_envelope_px':bounds,'highest_envelope_owner':top[1],'highest_envelope_px':top[0],'all_render_visible_evaluated_head_highest_owner':headtop[1],'all_render_visible_evaluated_head_highest_px':headtop[0],'actual_optic_center_px':E,'evaluated_seat_major_diameter_px':D,'named_crest_posterior_in_D':(E[0]-physical['posterior_crest']['projected_px'][0])/D,'whole_head_highest_posterior_in_D':(E[0]-headtop[0][0])/D,'named_crest_above_eye_in_D':(E[1]-physical['posterior_crest']['projected_px'][1])/D,'foredeck_root_anterior_in_D':(physical['foredeck_bill_root']['projected_px'][0]-E[0])/D,'ratio_warning':'Image+x diagnostic only; front/far views do not share anterior direction, and source landmarks are approximate','named_crest_is_not_max_all_vertices':True}
 print('HEAD13_CANDIDATE_RAYS',n,{k:(v['baseline_window_samples'],v['new_roof_brow_interceptions']) for k,v in checks.items()},flush=True)
report={'native_sha256_readback':hashlib.sha256((OUT/ATTEMPT/'formed-head13.blend').read_bytes()).hexdigest(),'method':'Dense actual evaluated curved-lens vertices and triangle barycentric targets; orthographic parallel rays from each actual review camera. Baseline first-hit glass identity defines window. Candidate may add ZERO CGH13 first interceptions inside that window. No flat-plane assumption. Finite samples, not continuous proof.','geometry_selection':'All render-visible mesh evaluated faces with max boundbox z>=1.30; every camera origin prior to lens is horizontal or above lens. Original hidden visibility states respected.','baseline_mesh_count':len(counts),'candidate_mesh_count':len(counts2),'cameras':result,'pass_zero_new_interception':all(v['new_roof_brow_interceptions']==0 for c in result.values() for v in c['curved_lens_first_hit_checks'].values()),'source_landmarks':'Approximate manual image reads, inferred; July perspective is not exact ortho metrology','completion':'HEAD13_CURVED_OPTIC_COMPLETE'}
(OUT/ATTEMPT/'curved-optic-landmark-receipt.json').write_text(json.dumps(report,indent=2));print('HEAD13_CURVED_OPTIC_COMPLETE',report['pass_zero_new_interception'],flush=True)
