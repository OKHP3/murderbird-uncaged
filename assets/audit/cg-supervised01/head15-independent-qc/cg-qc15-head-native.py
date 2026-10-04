import bpy,numpy as np,hashlib,json,math,time
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');W=Path('/Users/okh/.codex/worktrees/cg-supervised-localized-crown15/murderbird-uncaged');O=W/'assets/audit/cg-supervised-head15';B=R/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend';N=O/'attempt02/localized-head15.blend';receipt=json.loads((R/'assets/audit/cg-supervised-head13/attempt02/receipt.json').read_text())
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

# Fresh reviewer runner. Shared transparent snap/digest primitives are extended
# below; no authored code/API execution and no repository output write occurs.
def extended_snap():
 r=snap()
 for o in bpy.context.scene.objects:
  if o.type not in ['MESH','EMPTY']:continue
  extra=[val(o.matrix_parent_inverse),o.data.name if o.type=='MESH' else None,[(c.name,c.type,rna(c)) for c in o.constraints],[(g.name,g.index) for g in o.vertex_groups]]
  if o.type=='MESH':
   extra.extend([[(p.loop_start,p.loop_total) for p in o.data.polygons],[(l.vertex_index,l.edge_index) for l in o.data.loops],[(x.name,x.domain,x.data_type) for x in o.data.attributes],[(u.name,u.active_render,u.active_clone) for u in o.data.uv_layers]])
  r['objects'][o.name]=hashlib.sha256((r['objects'][o.name]+repr(extra)).encode()).hexdigest()
 for m in bpy.data.materials:
  extra=[rna(m)]
  if m.use_nodes:extra.append([(n.name,n.bl_idname,rna(n),[(i.name,i.identifier,i.bl_idname,rna(i)) for i in n.inputs],[(s.name,s.identifier,s.bl_idname,rna(s)) for s in n.outputs]) for n in m.node_tree.nodes])
  r['materials'][m.name]=hashlib.sha256((r['materials'][m.name]+repr(extra)).encode()).hexdigest()
 for i in bpy.data.images:
  if i.source=='FILE':r['images'][i.name]['additional']=[i.file_format,i.alpha_mode,i.depth,i.channels,i.is_float,i.use_half_precision,[(p.filepath,hashlib.sha256(bytes(p.packed_file.data)).hexdigest()) for p in i.packed_files]]
 return r
views=json.loads((O/'attempt02/diagnostic-cameras.json').read_text())
print('CAMKEYS',list(views),flush=True)
receipt15=json.loads((O/'attempt02/receipt.json').read_text())
views={v:receipt15['cameras']['after-clay-'+v] for v in ['source-full-bird','head-profile','head-grazing','head-front','head-far-profile']}
def setcam(c):
 s=bpy.context.scene;s.camera.matrix_world=Matrix(c['matrix']);s.camera.data.ortho_scale=c['scale'];s.camera.data.shift_x,s.camera.data.shift_y=c['shift'];s.render.resolution_x,s.render.resolution_y=c['resolution'];bpy.context.view_layer.update()
def rays(t,owners,points,d):
 rr=[]
 for q in points:
  h=t.ray_cast(q-d*5,d,5.02);rr.append(owners[h[2]] if h[2] is not None else None)
 return rr
bpy.ops.wm.open_mainfile(filepath=str(B));bpy.context.scene.cycles.device='CPU';bpy.context.scene.render.threads_mode='FIXED';bpy.context.scene.render.threads=2
before=extended_snap();print('BASE_SNAPSHOT',len(before['objects']),len(before['materials']),flush=True)
qs={};dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.context.scene.objects:
 if 'recessed optical glass' in o.name and not o.hide_render:
  e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();pp=[o.matrix_world@v.co for v in m.vertices];pp.extend(sum((o.matrix_world@m.vertices[i].co for i in f.vertices),Vector())/3 for f in m.loop_triangles);qs[o.name]=pp[::max(1,len(pp)//800)];e.to_mesh_clear()
t,owners=tree();windows={}
for v,c in views.items():
 setcam(c);d=bpy.context.scene.camera.matrix_world.to_quaternion()@Vector((0,0,-1));windows[v]={n:rays(t,owners,pp,d) for n,pp in qs.items()}
print('BASE_RAYS_DONE',flush=True)
bpy.ops.wm.open_mainfile(filepath=str(N));bpy.context.scene.cycles.device='CPU';bpy.context.scene.render.threads_mode='FIXED';bpy.context.scene.render.threads=2
after=extended_snap();s=bpy.context.scene
r={'blender_version':bpy.app.version_string,'cpu_threads':2,'source_native_sha256':hashlib.sha256(B.read_bytes()).hexdigest(),'candidate_native_sha256':hashlib.sha256(N.read_bytes()).hexdigest(),'objects_count':len(before['objects']),'payload_changed':[n for n,h in before['objects'].items() if after['objects'].get(n)!=h],'material_count':len(before['materials']),'material_changed':[n for n,h in before['materials'].items() if after['materials'].get(n)!=h],'file_images_count':sum(i['source']=='FILE' for i in before['images'].values()),'packed_images_count':sum(i['source']=='FILE' and i['packed'] is not None for i in before['images'].values()),'file_images_changed':[n for n,h in before['images'].items() if h['source']=='FILE' and after['images'].get(n)!=h],'visibility_changes':[n for n,h in before['visibility'].items() if after['visibility'].get(n)!=h]}
r['visibility_exact_whitelist']=set(r['visibility_changes'])==set(receipt15['hidden_originals']);r['visibility_candidate_hidden']=all(after['visibility'][n]==[True,True] for n in r['visibility_changes'])
r['new_meshes']={};dg=bpy.context.evaluated_depsgraph_get();vv={}
for o in s.objects:
 if o.name in receipt15['new_objects']:
  e=o.evaluated_get(dg);m=e.to_mesh();uv=[x for d in m.uv_layers.active.data for x in d.uv];r['new_meshes'][o.name]={'finite':all(math.isfinite(x) for v in m.vertices for x in v.co) and all(math.isfinite(x) for x in uv),'uv_range':[min(uv),max(uv)],'normalized_float32_tolerance_1_2e_7':min(uv)>=-1.2e-7 and max(uv)<=1+1.2e-7};e.to_mesh_clear()
 if o.type=='MESH' and not o.hide_render and not o.get('authoringGuide') and max((o.matrix_world@Vector(c)).z for c in o.bound_box)>=1.3:
  e=o.evaluated_get(dg);m=e.to_mesh();vv[o.name]=[o.matrix_world@v.co for v in m.vertices];e.to_mesh_clear()
r['visible_upper_meshes']=len(vv);r['visible_upper_vertices']=sum(map(len,vv.values()));r['world_z_highest']=max(((p.z,n,list(p)) for n,pp in vv.items() for p in pp),key=lambda x:x[0]);r['projection_highest']={};r['optic_first_hit']={};t,owners=tree()
for v,c in views.items():
 setcam(c);d=s.camera.matrix_world.to_quaternion()@Vector((0,0,-1));r['optic_first_hit'][v]={}
 for n,pp in qs.items():
  hits=rays(t,owners,pp,d);wi=[i for i,h in enumerate(windows[v][n]) if h==n];r['optic_first_hit'][v][n]={'samples':len(pp),'baseline_actual_window':len(wi),'first_hit_changes':sum(hits[i]!=n for i in wi),'new_head15_first_hits':sum(hits[i] is not None and hits[i].startswith('CGH15') for i in wi)}
 def py(p):return world_to_camera_view(s,s.camera,p).y
 top=max(((py(p),n,list(p)) for n,pp in vv.items() for p in pp),key=lambda x:x[0]);blade=max(((py(p),list(p)) for p in vv['CGH15 independent swept crest blade near']),key=lambda x:x[0]);r['projection_highest'][v]={'owner':top[1],'world':top[2],'screen_y':top[0],'near_blade_screen_y':blade[0],'near_blade_is_highest':abs(top[0]-blade[0])<1e-6};print('VIEW',v,r['optic_first_hit'][v],r['projection_highest'][v],flush=True)
r['method_limits']=['Shared repository snapshot/digest and BVH primitives, independently extended and rerun; correlated method weakness remains.','BVH upper objects selected by visible mesh bbox max world z>=1.3; authoringGuide meshes excluded.','Discrete original curved lens vertices plus triangle centroids, not continuous coverage.','Front baseline glass window zero, clearance cannot be inferred.','No render performed by reviewer; inspected frozen authored renders.']
Path('/tmp/cg-qc15-head-native.json').write_text(json.dumps(r,indent=2));print('QC15_DONE',{k:v for k,v in r.items() if k not in ['new_meshes','optic_first_hit','projection_highest','visibility_changes']},flush=True)
