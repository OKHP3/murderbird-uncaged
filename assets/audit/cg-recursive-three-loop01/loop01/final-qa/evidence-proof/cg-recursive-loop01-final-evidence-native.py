import bpy, numpy as np, json,hashlib,pathlib,datetime
ROOT=pathlib.Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
BASE=ROOT/'assets/audit/cg-recursive-three-loop01/loop01'
def val(v):
 if isinstance(v,(str,int,float,bool,type(None))):return v
 if isinstance(v,bpy.types.ID):return [v.bl_rna.identifier,v.name]
 if hasattr(v,'bl_rna'):return {'struct_type':v.bl_rna.identifier}
 try:return [val(x) for x in v]
 except:return str(v)
def rna(o):
 d={}
 for p in o.bl_rna.properties:
  if p.identifier in ['rna_type','name','location','dimensions','select','parent','session_uid','users'] or p.type=='COLLECTION':continue
  try:d[p.identifier]=val(getattr(o,p.identifier))
  except:pass
 return d
def digest(o):
 h=hashlib.sha256()
 def add(x):h.update(json.dumps(x,sort_keys=True,default=str).encode())
 add([o.type,list(o.matrix_local),list(o.matrix_world),o.parent.name if o.parent else None,o.parent_type,o.parent_bone,sorted((k,val(v)) for k,v in o.items()),[(m.name,m.type,rna(m)) for m in o.modifiers],[(s.link,s.material.name if s.material else None) for s in o.material_slots]])
 if o.type=='MESH':
  m=o.data;add([m.name,m.use_fake_user,[(k,val(v)) for k,v in m.items()]])
  for coll,field,n,dtype in [(m.vertices,'co',3,'float32'),(m.edges,'vertices',2,'int32'),(m.loops,'vertex_index',1,'int32'),(m.polygons,'loop_start',1,'int32'),(m.polygons,'loop_total',1,'int32'),(m.polygons,'material_index',1,'int32'),(m.polygons,'use_smooth',1,'bool')]:
   a=np.empty(len(coll)*n,dtype=dtype);coll.foreach_get(field,a);h.update(a.tobytes())
  for u in m.uv_layers:
   add(u.name);a=np.empty(len(u.data)*2,dtype='float32');u.data.foreach_get('uv',a);h.update(a.tobytes())
  for a in m.attributes:
   add([a.name,a.domain,a.data_type]);field,n,dtype={'FLOAT':('value',1,'float32'),'INT':('value',1,'int32'),'BOOLEAN':('value',1,'bool'),'FLOAT_VECTOR':('vector',3,'float32'),'FLOAT_COLOR':('color',4,'float32'),'BYTE_COLOR':('color',4,'float32'),'FLOAT2':('vector',2,'float32')}.get(a.data_type,(None,None,None))
   if field:
    z=np.empty(len(a.data)*n,dtype=dtype)
    try:a.data.foreach_get(field,z);h.update(z.tobytes())
    except:pass
  add([g.name for g in o.vertex_groups]);add([[(g.group,g.weight) for g in v.groups] for v in m.vertices])
 return h.hexdigest()
def snap(path):
 bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 objs={o.name:digest(o) for o in bpy.context.scene.objects if o.type in ['MESH','EMPTY']}
 vis={o.name:[o.hide_render,o.hide_viewport,o.hide_get()] for o in bpy.context.scene.objects if o.type in ['MESH','EMPTY']}
 mats={}
 for m in bpy.data.materials:
  data={'rna':rna(m),'props':[(k,val(v)) for k,v in m.items()]}
  if m.node_tree:
   data['nodes']={n.name:{'rna':rna(n),'inputs':[(s.name,val(s.default_value) if hasattr(s,'default_value') else None) for s in n.inputs]} for n in m.node_tree.nodes}
   data['links']=sorted((l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links)
  mats[m.name]=hashlib.sha256(json.dumps(data,sort_keys=True,default=str).encode()).hexdigest()
 imgs={i.name:{'source':i.source,'filepath':i.filepath,'size':list(i.size),'colorspace':i.colorspace_settings.name,'alpha':i.alpha_mode,'fake_user':i.use_fake_user,'props':[(k,val(v)) for k,v in i.items()],'packed_sha':hashlib.sha256(bytes(i.packed_file.data)).hexdigest() if i.packed_file else None} for i in bpy.data.images if i.source=='FILE'}
 return {'objects':objs,'visibility':vis,'materials':mats,'images':imgs,'counts':{'mesh_empty':len(objs),'materials':len(mats),'FILE_images':len(imgs),'packed_FILE_images':sum(v['packed_sha'] is not None for v in imgs.values())},'mesh_names':sorted(o.name for o in bpy.context.scene.objects if o.type=='MESH')}
results=[]
selection=json.loads((BASE/'retained-selection01.json').read_text());declare={x['name']:x for m in selection['modules'] for x in m['declared_superseded_render_hides']}
for era in ['builder','maker','mechanic']:
 original=ROOT/('assets/models/cg-supervised01/attempt09/murderbird-supervised-'+era+'.blend');a=snap(original)
 for kind in ['matched02','retained02']:
  path=BASE/('delivery/'+kind+'/'+era+'/murderbird-recursive-'+era+'.blend');b=snap(path)
  changes={k:[n for n,v in a[k].items() if b[k].get(n)!=v] for k in ['objects','materials','images']};vis={n:{'before':v,'after':b['visibility'].get(n)} for n,v in a['visibility'].items() if b['visibility'].get(n)!=v};new=sorted(set(b['mesh_names'])-set(a['mesh_names']))
  result={'era':era,'kind':kind,'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'original_counts':a['counts'],'counts':b['counts'],'receiving_changes':changes,'visibility_changes':vis,'new_mesh_names':new,'new_mesh_count':len(new)}
  if kind=='retained02':
   result['visibility_matches_declared']=set(vis)==set(declare) and all(x['after']==[True,x['before'][1],True] for x in vis.values());result['declared_count']=len(declare)
  results.append(result)
out={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'results':results,'method':'Independent read-only Blender factory-startup disable-autoexec; original mesh/empty topology/coordinates/UV/face assignments/slots/attributes/groups/transforms/parents/modifier RNA/custom fields, material graph node RNA/input/link hashes and FILE packed bytes/metadata snapshots. No producer helper imports, saves or rendering. Not every Blender RNA or evaluated modifier output is certified; transient session_uid and reference-count users excluded and non-ID pointer substructures typed rather than pointer-address compared.'}
pathlib.Path('/tmp/cg-recursive-loop01-final-evidence-native.json').write_text(json.dumps(out,indent=2,default=str)+'\n')
print('EVIDENCE_NATIVE_PROBE_COMPLETE',[(r['era'],r['kind'],r['new_mesh_count'],{k:len(v) for k,v in r['receiving_changes'].items()}) for r in results])
