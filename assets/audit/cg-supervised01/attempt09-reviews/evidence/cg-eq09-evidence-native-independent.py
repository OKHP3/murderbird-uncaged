import sys
sys.dont_write_bytecode=True
import bpy,numpy as np,json,hashlib
from pathlib import Path
R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
def value(x):
 if isinstance(x,(str,int,float,bool,type(None))):return x
 if hasattr(x,'name'):return {'id':x.name}
 if hasattr(x,'to_dict'):return {k:value(v) for k,v in x.to_dict().items()}
 try:return [value(v) for v in x]
 except:return repr(x)
def props(x):return {k:value(v) for k,v in sorted(x.items())}
def rna(x):
 out={}
 for p in x.bl_rna.properties:
  if p.identifier!='rna_type' and not p.is_readonly:
   try:out[p.identifier]=value(getattr(x,p.identifier))
   except:pass
 return out
def digest(x):return hashlib.sha256(repr(x).encode()).hexdigest()
def object_hash(o):
 h=hashlib.sha256(repr([o.type,value(o.matrix_world),value(o.matrix_local),o.parent.name if o.parent else None,props(o),[(m.type,rna(m)) for m in o.modifiers]]).encode())
 if o.type=='MESH':
  m=o.data;h.update(repr([props(m),[s.name if s else None for s in m.materials],[(tuple(p.vertices),p.material_index,p.use_smooth) for p in m.polygons],[(tuple(e.vertices),e.use_edge_sharp) for e in m.edges],[[tuple((g.group,g.weight) for g in v.groups)] for v in m.vertices]]).encode());coords=np.empty(len(m.vertices)*3,np.float32);m.vertices.foreach_get('co',coords);h.update(coords.tobytes())
  for uv in m.uv_layers:
   coords=np.empty(len(uv.data)*2,np.float32);uv.data.foreach_get('uv',coords);h.update(repr([uv.name,uv.active_render]).encode());h.update(coords.tobytes())
  for attr in m.attributes:
   field={'FLOAT':'value','INT':'value','BOOLEAN':'value','FLOAT_VECTOR':'vector','FLOAT_COLOR':'color','BYTE_COLOR':'color','FLOAT2':'vector'}.get(attr.data_type);h.update(repr([attr.name,attr.domain,attr.data_type]).encode())
   if field:h.update(repr([value(getattr(d,field)) for d in attr.data]).encode())
 return h.hexdigest()
def snapshot():
 s=bpy.context.scene;objects={o.name:object_hash(o) for o in s.objects if o.type in ('MESH','EMPTY')};graphs={}
 for m in bpy.data.materials:
  graphs[m.name]=digest([props(m),m.diffuse_color[:],m.use_nodes,[(n.name,n.type,rna(n),props(n),[(i.identifier,value(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in m.node_tree.nodes] if m.use_nodes else [],[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links] if m.use_nodes else []])
 images={i.name:digest([i.source,i.filepath,i.filepath_raw,list(i.size),i.channels,i.file_format,i.colorspace_settings.name,i.alpha_mode,i.use_fake_user,props(i),hashlib.sha256(bytes(i.packed_file.data)).hexdigest() if i.packed_file else None]) for i in bpy.data.images if i.source=='FILE'}
 return {'objects':objects,'graphs':graphs,'images':images,'visibility':{o.name:[o.hide_render,o.hide_viewport,o.hide_get()] for o in s.objects if o.type in ('MESH','EMPTY')}}
results=[]
for era in ['builder','maker','mechanic']:
 paths=[R/f'assets/models/cg-supervised01/{attempt}/murderbird-supervised-{era}.blend' for attempt in ['attempt06','attempt09']];snapshots=[]
 for p in paths:
  bpy.ops.wm.open_mainfile(filepath=str(p));snapshots.append(snapshot());print('EVIDENCE09_SNAPSHOT',era,p.parent.name,flush=True)
 before,after=snapshots;changes={k:[n for n,v in before[k].items() if after[k].get(n)!=v] for k in ['objects','graphs','images']};actual={n:v for n,v in after['visibility'].items() if n in before['visibility'] and v!=before['visibility'][n]};declared=json.loads((R/f'assets/audit/cg-supervised01/attempt09/delivery-validation/cg-delivery09-native-{era}.json').read_text())['declared_visibility'];result={'era':era,'paths':[str(p.relative_to(R)) for p in paths],'sha256':[hashlib.sha256(p.read_bytes()).hexdigest() for p in paths],'counts':{k:len(before[k]) for k in ['objects','graphs','images']},'differences':changes,'visibility_matches_final_native_declaration':actual==declared,'visibility_changed_count':len(actual),'visibility_declaration_differences':sorted(set(actual)^set(declared)),'status':'PASS' if not any(changes.values()) and actual==declared else 'FAIL'};results.append(result);Path('/tmp/cg-eq09-evidence-native-independent.json').write_text(json.dumps({'results':results,'method':'Evidence-role independently authored six-file readback; coordinates, topology, attributes, UVs, groups, slots, transforms, parents, properties, modifiers; graph RNA/node defaults/links; packed FILE metadata/bytes. No saves/render or repository imports; CPU2.'},indent=2));print('EVIDENCE09_ERA_RESULT',result['status'],era,flush=True)
