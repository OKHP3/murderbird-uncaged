import bpy,json,hashlib,math,numpy as np
from pathlib import Path
from mathutils import Matrix
OUT=Path(__file__).resolve().parent
BASE=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged/assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def prop(v):
 if hasattr(v,'to_list'):return v.to_list()
 if hasattr(v,'name'):return {'id':v.name}
 try:return list(v) if not isinstance(v,(str,int,float,bool,dict)) else v
 except:return str(v)
def payload(o):
 h=hashlib.sha256();h.update(repr((o.type,list(map(list,o.matrix_world)),list(map(list,o.matrix_local)),o.parent.name if o.parent else None,[(k,prop(v)) for k,v in sorted(o.items())],[(m.name,m.type,[(p.identifier,prop(getattr(m,p.identifier))) for p in m.bl_rna.properties if not p.is_readonly and p.identifier not in ('name','rna_type')]) for m in o.modifiers])).encode())
 if o.type=='MESH':
  me=o.data;a=np.empty(len(me.vertices)*3,dtype='<f4');me.vertices.foreach_get('co',a);h.update(a.tobytes());h.update(repr([(tuple(p.vertices),p.material_index,p.use_smooth) for p in me.polygons]).encode());h.update(repr([m.name if m else None for m in me.materials]).encode())
  for uv in me.uv_layers:
   a=np.empty(len(uv.data)*2,dtype='<f4');uv.data.foreach_get('uv',a);h.update(uv.name.encode());h.update(a.tobytes())
  for attr in me.attributes:
   h.update(repr((attr.name,attr.domain,attr.data_type)).encode());field={'FLOAT':'value','INT':'value','BOOLEAN':'value','FLOAT_VECTOR':'vector','FLOAT_COLOR':'color','BYTE_COLOR':'color','FLOAT2':'vector'}.get(attr.data_type)
   if field:
    for item in attr.data:h.update(repr(prop(getattr(item,field))).encode())
  h.update(repr([(k,prop(v)) for k,v in sorted(me.items())]).encode())
 return h.hexdigest()
def mats():
 out={}
 for m in bpy.data.materials:
  if m.use_nodes:
   graph=[(n.name,n.type,[(i.name,prop(i.default_value)) for i in n.inputs if hasattr(i,'default_value')],n.image.name if n.type=='TEX_IMAGE' and n.image else None) for n in m.node_tree.nodes];links=[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links];out[m.name]=hashlib.sha256(repr((graph,links,[(k,prop(v)) for k,v in sorted(m.items())])).encode()).hexdigest()
 return out
def maps():
 return {i.name:{'path':i.filepath,'size':list(i.size),'colorspace':i.colorspace_settings.name,'packed_bytes':hashlib.sha256(bytes(i.packed_file.data)).hexdigest() if i.packed_file else None} for i in bpy.data.images}
bpy.ops.wm.open_mainfile(filepath=str(BASE));s=bpy.context.scene;originals={o.name:payload(o) for o in s.objects if o.type in ('MESH','EMPTY')};matbase=mats();mapbase=maps();frame=list(map(list,s.objects['CG2b head frame'].matrix_world));vis={o.name:[o.hide_render,o.hide_get()] for o in s.objects if o.name in originals}
native=OUT/'attempt02/formed-head13.blend';bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;matnow=mats();mapnow=maps();r=json.loads((OUT/'attempt02/receipt.json').read_text());vnow={n for n,v in vis.items() if [s.objects[n].hide_render,s.objects[n].hide_get()]!=v}
report={'original_mesh_anchor_count':len(originals),'changed_original_payloads':[n for n,h in originals.items() if n not in s.objects or payload(s.objects[n])!=h],'changed_original_material_graphs':[n for n,h in matbase.items() if matnow.get(n)!=h],'changed_original_image_maps':[n for n,h in mapbase.items() if mapnow.get(n)!=h],'frame_unchanged':frame==list(map(list,s.objects['CG2b head frame'].matrix_world)),'visibility_allowlist_exact':vnow==set(r['hidden_originals']),'native_sha256':sha(native),'input_sha256':sha(BASE)}
(OUT/'preservation-readback.json').write_text(json.dumps(report,indent=2));print('HEAD13_PRESERVATION',report,flush=True)
