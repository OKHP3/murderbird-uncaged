import bpy,numpy as np,hashlib,json,math,time
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');W=Path('/Users/okh/.codex/worktrees/cg-supervised-head-contrast16/murderbird-uncaged');O=W/'assets/audit/cg-supervised-bill18';B=Path('/Users/okh/.codex/worktrees/cg-supervised-layered-crown17/murderbird-uncaged/assets/audit/cg-supervised-head17/attempt02/layered-head17.blend');N=O/'attempt02/formed-bill18.blend';receipt=json.loads((O/'attempt02/receipt.json').read_text())
def val(x):
 if isinstance(x,(str,int,float,bool,type(None))):return x
 if hasattr(x,'name'):return {'id_name':x.name}
 if hasattr(x,'to_dict'):return x.to_dict()
 if hasattr(x,'to_list'):return x.to_list()
 try:return [val(v) for v in x]
 except:return str(x)
def properties(x):return {k:val(v) for k,v in sorted(x.items())}
def rna(x):
 r={}
 for p in x.bl_rna.properties:
  if not p.is_readonly and p.identifier not in ['rna_type','name']:
   try:r[p.identifier]=val(getattr(x,p.identifier))
   except:pass
 return r
def digest(o):
 h=hashlib.sha256();h.update(repr([o.type,val(o.matrix_world),val(o.matrix_local),o.parent.name if o.parent else None,properties(o),[(m.name,m.type,rna(m)) for m in o.modifiers]]).encode())
 if o.type=='MESH':
  m=o.data;h.update(repr([properties(m),[s.name if s else None for s in m.materials],[(tuple(f.vertices),f.material_index,f.use_smooth) for f in m.polygons],[(tuple(e.vertices),e.use_edge_sharp) for e in m.edges]]).encode())
  a=np.empty(len(m.vertices)*3,dtype=np.float32);m.vertices.foreach_get('co',a);h.update(a.tobytes())
  for a in m.attributes:
   h.update(repr([a.name,a.domain,a.data_type]).encode());field={'FLOAT':'value','INT':'value','BOOLEAN':'value','FLOAT_VECTOR':'vector','FLOAT_COLOR':'color','BYTE_COLOR':'color','FLOAT2':'vector'}.get(a.data_type)
   if field:h.update(repr([val(getattr(d,field)) for d in a.data]).encode())
 return h.hexdigest()
def snap():
 s=bpy.context.scene
 return {'objects':{o.name:digest(o) for o in s.objects if o.type in ['MESH','EMPTY']},'images':{i.name:{'file':i.filepath,'size':list(i.size),'source':i.source,'colorspace':i.colorspace_settings.name,'props':properties(i),'fake_user':i.use_fake_user,'packed':hashlib.sha256(bytes(i.packed_file.data)).hexdigest() if i.packed_file else None} for i in bpy.data.images},'materials':{m.name:hashlib.sha256(repr([properties(m),m.diffuse_color[:],m.use_nodes,[(n.name,n.type,[(i.name,val(i.default_value)) for i in n.inputs if hasattr(i,'default_value')],n.image.name if n.type=='TEX_IMAGE' and n.image else None,properties(n)) for n in m.node_tree.nodes] if m.use_nodes else [],[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links] if m.use_nodes else []]).encode()).hexdigest() for m in bpy.data.materials},'visibility':{o.name:[o.hide_render,o.hide_get()] for o in s.objects if o.type in ['MESH','EMPTY']}}
def tree():
 s=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();vs=[];fs=[];owners=[]
 for o in s.objects:
  if o.type!='MESH' or o.hide_render or o.get('authoringGuide') or max((o.matrix_world@Vector(c)).z for c in o.bound_box)<1.3:continue
  e=o.evaluated_get(dg);m=e.to_mesh();off=len(vs);vs.extend(o.matrix_world@v.co for v in m.vertices);fs.extend(tuple(off+i for i in f.vertices) for f in m.polygons);owners.extend([o.name]*len(m.polygons));e.to_mesh_clear()
 return BVHTree.FromPolygons(vs,fs),owners
fixed=json.loads((R/'assets/audit/cg-supervised-head13/attempt02/receipt.json').read_text())
views={v:fixed['cameras']['after-clay-'+v] for v in ['source-full-bird','head-profile','head-grazing','head-front','head-far-profile']}
def setcam(c):
 s=bpy.context.scene;s.camera.matrix_world=Matrix(c['matrix']);s.camera.data.ortho_scale=c['scale'];s.camera.data.shift_x,s.camera.data.shift_y=c['shift'];s.render.resolution_x,s.render.resolution_y=c['resolution'];bpy.context.view_layer.update()
def hits(t,owners,qs,d):
 result=[]
 for q in qs:
  hit=t.ray_cast(q-d*5,d,5.02);result.append(None if hit[2] is None else owners[hit[2]])
 return result
bpy.ops.wm.open_mainfile(filepath=str(B));before=snap();print('INDEPENDENT_BASE',len(before['objects']),len(before['images']),flush=True)
qs={}
for o in bpy.context.scene.objects:
 if 'recessed optical glass' in o.name and not o.hide_render:
  e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();m.calc_loop_triangles();points=[o.matrix_world@v.co for v in m.vertices]
  points.extend(sum((o.matrix_world@m.vertices[i].co for i in f.vertices),Vector())/3 for f in m.loop_triangles)
  stride=max(1,len(points)//800);qs[o.name]=points[::stride];e.to_mesh_clear()
t,owners=tree();baseline={}
for v,c in views.items():
 setcam(c);d=bpy.context.scene.camera.matrix_world.to_quaternion()@Vector((0,0,-1));baseline[v]={n:hits(t,owners,p,d) for n,p in qs.items()}
print('INDEPENDENT_BASE_RAYS', {n:len(p) for n,p in qs.items()},flush=True)
bpy.ops.wm.open_mainfile(filepath=str(N));after=snap();s=bpy.context.scene
result={'input_sha256':hashlib.sha256(B.read_bytes()).hexdigest(),'native_sha256':hashlib.sha256(N.read_bytes()).hexdigest(),'original_count':len(before['objects']),'original_payload_changes':[n for n,h in before['objects'].items() if after['objects'].get(n)!=h],'original_image_count':len(before['images']),'original_packed_count':sum(i['packed'] is not None for i in before['images'].values()),'original_file_image_changes':[n for n,h in before['images'].items() if h['source']=='FILE' and after['images'].get(n)!=h],'original_material_count':len(before['materials']),'original_material_changes':[n for n,h in before['materials'].items() if after['materials'].get(n)!=h],'visibility_changes':[n for n,h in before['visibility'].items() if after['visibility'].get(n)!=h]}
result['visibility_exact_allowlist']=set(result['visibility_changes'])==set(receipt['hidden_originals']);result['original_head_frame_optic_pose_payloads_preserved']=all(after['objects'].get(n)==h for n,h in before['objects'].items() if any(k in n.lower() for k in ['head frame','optic','glass','hip','knee','hock','foot']))
print('INDEPENDENT_PRESERVATION',result,flush=True)
t,owners=tree();result['curved_lens_first_hit']={};result['highest_and_named']={};dg=bpy.context.evaluated_depsgraph_get();verts={}
for o in s.objects:
 if o.type=='MESH' and not o.hide_render and not o.get('authoringGuide') and max((o.matrix_world@Vector(c)).z for c in o.bound_box)>=1.3:
  e=o.evaluated_get(dg);m=e.to_mesh();verts[o.name]=[o.matrix_world@v.co for v in m.vertices];e.to_mesh_clear()
highest_world=max(((p,n) for n,ps in verts.items() for p in ps),key=lambda x:x[0].z);named=highest_world[0];result['true_highest_world_vertex']={'owner':highest_world[1],'xyz':list(named)}
result['all_upper_evaluated_mesh_count']=len(verts);result['all_upper_evaluated_vertex_count']=sum(map(len,verts.values()))
for v,c in views.items():
 setcam(c);d=s.camera.matrix_world.to_quaternion()@Vector((0,0,-1));r={}
 for n,p in qs.items():
  cand=hits(t,owners,p,d);window=[i for i,h in enumerate(baseline[v][n]) if h==n];r[n]={'samples':len(p),'baseline_actual_glass_window':len(window),'new_guide_blocks':sum(cand[i] is not None and cand[i].startswith('CGH18') for i in window),'window_first_hit_changed_count':sum(cand[i]!=n for i in window)}
 result['curved_lens_first_hit'][v]=r
 def proj(q):
  a=world_to_camera_view(s,s.camera,q);return [a.x*c['resolution'][0],(1-a.y)*c['resolution'][1]]
 top=min(((proj(p),n) for n,ps in verts.items() for p in ps),key=lambda x:x[0][1]);result['highest_and_named'][v]={'whole_visible_highest_owner':top[1],'whole_visible_highest_px':top[0],'named_nearest_evaluated_crest_px':proj(named)}
 ref=json.loads((R/'assets/audit/cg-supervised-head13/attempt02/curved-optic-landmark-receipt.json').read_text())['cameras']['after-clay-'+v];E=ref['actual_optic_center_px'];D=ref['evaluated_seat_major_diameter_px'];result['highest_and_named'][v]['normalization_from_preserved13_seat_D']=D;result['highest_and_named'][v]['physical_crest_ratios_posterior_height']=[(E[a]-proj(named)[a])/D for a in range(2)];result['highest_and_named'][v]['whole_highest_ratios_posterior_height']=[(E[a]-top[0][a])/D for a in range(2)]
 print('INDEPENDENT_VIEW',v,r,result['highest_and_named'][v],flush=True)
(O/'attempt02/native-check.json').write_text(json.dumps(result,indent=2));print('INDEPENDENT_DONE',flush=True)
