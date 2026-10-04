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

bpy.ops.wm.open_mainfile(filepath=str(B));s=bpy.context.scene;qs={}
for o in s.objects:
 if 'recessed optical glass' in o.name and not o.hide_render:
  e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();m.calc_loop_triangles();points=[o.matrix_world@v.co for v in m.vertices];points.extend(sum((o.matrix_world@m.vertices[i].co for i in f.vertices),Vector())/3 for f in m.loop_triangles);qs[o.name]=points[::max(1,len(points)//800)];e.to_mesh_clear()
t,owners=tree();setcam(views['head-grazing']);d=s.camera.matrix_world.to_quaternion()@Vector((0,0,-1));base={n:hits(t,owners,p,d) for n,p in qs.items()}
bpy.ops.wm.open_mainfile(filepath=str(N));t,owners=tree();r=[]
for n,p in qs.items():
 cand=hits(t,owners,p,d)
 for i,q in enumerate(p):
  if base[n][i]==n and cand[i]!=n:
   hit=t.ray_cast(q-d*5,d,5.02);loc=bpy.context.scene.objects[cand[i]].matrix_world.inverted()@hit[0];r.append({'glass':n,'index':i,'owner':cand[i],'point':list(q),'hitlocal':list(loc),'source_xy':[(.005-loc.y)/.0012+788,(.020-loc.z)/.0012+188]})
print('LOSSES',r,flush=True);(O/'attempt02/optic-loss-details.json').write_text(json.dumps(r,indent=2))
