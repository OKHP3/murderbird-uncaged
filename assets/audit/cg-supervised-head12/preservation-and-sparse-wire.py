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
bpy.ops.wm.open_mainfile(filepath=str(BASE));s=bpy.context.scene;originals={o.name:payload(o) for o in s.objects if o.type in ('MESH','EMPTY')};vis={o.name:[o.hide_render,o.hide_get()] for o in s.objects if o.name in originals};matbase=mats();mapbase=maps();frame=list(map(list,s.objects['CG2b head frame'].matrix_world));reports={}
for attempt in ('attempt01','attempt02'):
 out=OUT/attempt;native=out/'formed-head12.blend';native_sha=sha(native);bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene
 matnow=mats();mapnow=maps()
 changed=[n for n,h in originals.items() if n not in s.objects or payload(s.objects[n])!=h];mc=[n for n,h in matbase.items() if matnow.get(n)!=h];ic=[n for n,h in mapbase.items() if mapnow.get(n)!=h]
 r=json.loads((out/'receipt.json').read_text());actualvis={n:{'before':v,'after':[s.objects[n].hide_render,s.objects[n].hide_get()]} for n,v in vis.items() if [s.objects[n].hide_render,s.objects[n].hide_get()]!=v};report={'original_mesh_anchor_count':len(originals),'changed_original_payloads':changed,'changed_original_material_graphs':mc,'changed_original_image_maps':ic,'frame_matrix_unchanged':list(map(list,s.objects['CG2b head frame'].matrix_world))==frame,'visibility_allowlist_exact':set(actualvis)==set(r['hidden_originals']),'visibility_changes':actualvis,'payload_scope':'world/local transform,parent,original object+mesh metadata,modifier RNA,vertex positions,face indices+material indices+smooth state,UVs,all supported numeric mesh/color attributes,material slots,original node inputs+links+image bindings,original image path/size/colorspace+packed-byte hash','native_loaded_sha256':native_sha}
 (OUT/(attempt+'-preservation-interim.json')).write_text(json.dumps(report,indent=2));print('HEAD12_PRESERVATION_COUNTS',len(changed),mc,ic,report['frame_matrix_unchanged'],report['visibility_allowlist_exact'],flush=True)
 assert not changed and not mc and not ic and report['frame_matrix_unchanged'] and report['visibility_allowlist_exact']
 new=[o for o in s.objects if o.get('cgSupervisedHead12')]
 for o in new:
  for m in o.modifiers:
   if m.type=='SUBSURF':m.show_render=False
  w=o.modifiers.new('transient sparse control cage wire','WIREFRAME');w.thickness=.0012;w.use_replace=True
 clay=bpy.data.materials.new('HEAD12 sparse wire diagnostic clay');clay.use_nodes=True;p=clay.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.42,.42,.42,1);p.inputs['Roughness'].default_value=.75;s.view_layers[0].material_override=clay;s.cycles.samples=8;s.cycles.use_denoising=True
 for name,camname in [('wire-head-oblique','after-clay-head-oblique'),('wire-source-full-bird','after-clay-source-full-bird')]:
  c=r['cameras'][camname];s.camera.matrix_world=Matrix(c['matrix']);s.camera.data.ortho_scale=c['scale'];s.camera.data.shift_x,s.camera.data.shift_y=c['shift'];s.render.resolution_x,s.render.resolution_y=c['resolution'];s.render.resolution_percentage=100;s.render.filepath=str(out/(name+'.png'));bpy.context.view_layer.update();bpy.ops.render.render(write_still=True);r['cameras'][name]=c.copy()
 assert sha(native)==native_sha
 report['native_unchanged_after_transient_wire_readback']=True;reports[attempt]=report;r['image_hashes']={p.name:sha(p) for p in out.glob('*.png')};(out/'receipt.json').write_text(json.dumps(r,indent=2));print('HEAD12_PRESERVATION_READBACK_COMPLETE',attempt,flush=True)
(OUT/'preservation-readback.json').write_text(json.dumps(reports,indent=2))
