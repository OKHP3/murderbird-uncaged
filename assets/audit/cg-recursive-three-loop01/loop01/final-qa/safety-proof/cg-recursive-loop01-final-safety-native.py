import bpy, json, hashlib, array, importlib.util, sys
sys.dont_write_bytecode=True
from pathlib import Path
R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
P=R/'assets/audit/cg-recursive-three-loop01/loop01'
OUT=Path('/tmp/cg-recursive-loop01-safety-native-checks.json')
def plain(x):
 if x is None or isinstance(x,(str,int,float,bool)):return x
 if hasattr(x,'name'):return {'id':x.name}
 if hasattr(x,'to_dict'):return {k:plain(v) for k,v in x.to_dict().items()}
 if hasattr(x,'bl_rna'):
  d={'rna_type':x.bl_rna.identifier}
  for pr in x.bl_rna.properties:
   if pr.identifier=='rna_type' or pr.type in ('POINTER','COLLECTION'):continue
   try:d[pr.identifier]=plain(getattr(x,pr.identifier))
   except:pass
  if hasattr(x,'points'):d['points']=[plain(v) for v in x.points]
  return d
 try:return [plain(v) for v in x]
 except:return str(x)
def props(o):return {k:plain(v) for k,v in sorted(o.items())}
def hashj(o):return hashlib.sha256(json.dumps(o,sort_keys=True,default=str).encode()).hexdigest()
def field(seq,attr,n,t='f'):
 a=array.array(t,[0])*n
 if n:seq.foreach_get(attr,a)
 return hashlib.sha256(a.tobytes()).hexdigest()
def obj(o):
 d={'type':o.type,'matrix':plain(o.matrix_world),'parent':o.parent.name if o.parent else None,'props':props(o),'modifiers':[]}
 for m in o.modifiers:
  z={}
  for pr in m.bl_rna.properties:
   if pr.identifier in ('rna_type','execution_time') or pr.type=='COLLECTION':continue
   try:z[pr.identifier]=plain(getattr(m,pr.identifier))
   except:pass
  d['modifiers'].append(z)
 if o.type=='MESH':
  x=o.data;d['mesh']={'vertices':field(x.vertices,'co',len(x.vertices)*3),'edges':field(x.edges,'vertices',len(x.edges)*2,'i'),'loops':field(x.loops,'vertex_index',len(x.loops),'i'),'poly_offsets':field(x.polygons,'loop_start',len(x.polygons),'i'),'poly_totals':field(x.polygons,'loop_total',len(x.polygons),'i'),'material_indices':field(x.polygons,'material_index',len(x.polygons),'i'),'smooth':field(x.polygons,'use_smooth',len(x.polygons),'i'),'materials':[m.name if m else None for m in x.materials],'uvs':{u.name:field(u.data,'uv',len(u.data)*2) for u in x.uv_layers},'attrs':{}}
  for a in x.attributes:
   spec={'FLOAT':('value',1,'f'),'INT':('value',1,'i'),'BOOLEAN':('value',1,'i'),'FLOAT_VECTOR':('vector',3,'f'),'FLOAT2':('vector',2,'f'),'FLOAT_COLOR':('color',4,'f'),'BYTE_COLOR':('color',4,'f')}.get(a.data_type)
   if spec:
    try:d['mesh']['attrs'][a.name]=[a.data_type,a.domain,field(a.data,spec[0],len(a.data)*spec[1],spec[2])]
    except:d['mesh']['attrs'][a.name]='NOT_CAPTURED'
  if x.shape_keys:d['mesh']['shape_keys']={k.name:field(k.data,'co',len(k.data)*3) for k in x.shape_keys.key_blocks}
 return hashj(d)
def mat(m):
 d={'props':props(m),'use_nodes':m.use_nodes,'nodes':[],'links':[]}
 if m.node_tree:
  for n in m.node_tree.nodes:
   q={'name':n.name,'type':n.bl_idname,'props':props(n),'inputs':[(x.name,plain(x.default_value) if hasattr(x,'default_value') else None) for x in n.inputs]}
   for k in ['operation','blend_type','extension','interpolation','projection','vector_type','space','uv_map','attribute_name','data_type','normalize','mapping','texture_mapping','image','node_tree']:
    if hasattr(n,k):q[k]=plain(getattr(n,k))
   if hasattr(n,'color_ramp'):q['color_ramp']=[n.color_ramp.interpolation,[(e.position,plain(e.color)) for e in n.color_ramp.elements]]
   d['nodes'].append(q)
  d['links']=sorted((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links)
 return hashj(d)
def snap():
 s=bpy.context.scene
 return {'objects':{o.name:obj(o) for o in s.objects if o.type in ('MESH','EMPTY')},'vis':{o.name:[o.hide_render,o.hide_viewport,o.hide_get()] for o in s.objects if o.type in ('MESH','EMPTY')},'materials':{m.name:mat(m) for m in bpy.data.materials},'images':{i.name:hashj({'packed':hashlib.sha256(bytes(i.packed_file.data)).hexdigest() if i.packed_file else None,'filepath':i.filepath,'raw':i.filepath_raw,'source':i.source,'size':plain(i.size),'fake_user':i.use_fake_user,'props':props(i)}) for i in bpy.data.images if i.packed_file or i.source=='FILE'},'counts':{'mesh_empty':sum(o.type in ('MESH','EMPTY') for o in s.objects),'materials':len(bpy.data.materials),'packed':sum(i.packed_file is not None for i in bpy.data.images)}}
def openp(p):bpy.ops.wm.open_mainfile(filepath=str(p))

rep={'algorithm':'Independent rawmesh/RNA/material/packedimage fingerprint; no producerdigest helper','sources':{},'comparisons':{},'rigs':{},'imports':{}}
def rig():
 s=bpy.context.scene;d={'camera':s.camera.name if s.camera else None,'scenes':[v.name for v in bpy.data.scenes],'clay':[v.material_override.name if v.material_override else None for v in s.view_layers],'lights_cameras':{}}
 for o in s.objects:
  if o.type=='CAMERA':q=[o.data.type,o.data.lens,o.data.ortho_scale,o.data.shift_x,o.data.shift_y]
  elif o.type=='LIGHT':q=[o.data.type,o.data.energy,list(o.data.color),o.data.size]
  else:continue
  d['lights_cameras'][o.name]={'matrix':plain(o.matrix_world),'data':q}
 b=s.world.node_tree.nodes.get('Background');d['world']=[list(b.inputs[0].default_value),b.inputs[1].default_value];d['render']=[s.render.engine,s.cycles.samples,s.render.resolution_x,s.render.resolution_y,s.view_settings.view_transform,s.view_settings.look,s.view_settings.exposure,s.view_settings.gamma];return d
for era in ['builder','maker','mechanic']:
 openp(R/f'assets/models/cg-supervised01/attempt09/murderbird-supervised-{era}.blend');bpy.context.view_layer.update();before=snap();before_rig=rig();rep['sources'][era]={'counts':before['counts']}
 for kind in ['matched02','retained02']:
  openp(P/f'delivery/{kind}/{era}/murderbird-recursive-{era}.blend');bpy.context.view_layer.update();a=snap();rep['rigs'][kind+'-'+era]={'exact_original_rig':rig()==before_rig,'no_clay':all(v is None for v in rig()['clay']),'scene_names':rig()['scenes']}
  changes={k:[n for n,v in before[k].items() if a[k].get(n)!=v] for k in ['objects','materials','images']};vis={n:{'before':v,'after':a['vis'].get(n)} for n,v in before['vis'].items() if a['vis'].get(n)!=v}
  declared={e['name']:e for m in json.loads((P/'body-only-selection.json').read_text())['modules'] for e in m['declared_superseded_render_hides']} if kind=='retained02' else {}
  badvis={n:v for n,v in vis.items() if n not in declared or v['after'] != [True,v['before'][1],True if declared[n].get('hide_set') else v['before'][2]]};added=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name not in before['objects']];bindings=[]
  for o in added:
   families=['breast-armor','black-iron']
   for j,m in enumerate(o.data.materials):
    if not m or m.get('cgMetal05Era')!=era or m.get('cgMetal05Family')!=families[j]:bindings.append({'object':o.name,'slot':j,'material':m.name if m else None})
  rep['comparisons'][kind+'-'+era]={'counts':a['counts'],'receiving_changes':changes,'declared_hides':len(declared),'actual_hides':len(vis),'hide_errors':badvis,'added_meshes':len(added),'added_material_role_errors':bindings}
counts=(len(bpy.data.objects),len(bpy.data.materials),len(bpy.data.images))
for n in ['cg-recursive-body01.py','cg-recursive-delivery02.py']:
 sp=importlib.util.spec_from_file_location('final_safety_'+n.replace('-','_'),R/'scripts'/n);mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);rep['imports'][n]={'inert':counts==(len(bpy.data.objects),len(bpy.data.materials),len(bpy.data.images))}
Path('/tmp/cg-recursive-loop01-final-safety-native.json').write_text(json.dumps(rep,indent=2));print('FINAL_NATIVE_SAFETY_COMPLETE',json.dumps({k:v for k,v in rep.items() if k!='comparisons'}));print('FINAL_NATIVE_COMPARE_COUNTS',json.dumps({k:{'receiving_change_counts':{x:len(y) for x,y in v['receiving_changes'].items()},'counts':v['counts'],'declared_hides':v['declared_hides'],'actual_hides':v['actual_hides'],'added_meshes':v['added_meshes'],'hide_errors':v['hide_errors'],'role_errors':v['added_material_role_errors']} for k,v in rep['comparisons'].items()}))
