import bpy,json,hashlib,pathlib,sys,collections
root=pathlib.Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');out=[]
for era in ('builder','maker','mechanic'):
 f=root/f'assets/audit/cg-recursive-three-loop01/loop02/delivery/retained03/{era}/murderbird-recursive-{era}.blend';bpy.ops.wm.open_mainfile(filepath=str(f));deps=bpy.context.evaluated_depsgraph_get();row={'era':era,'native_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'mesh_empty':sum(o.type in ('MESH','EMPTY') for o in bpy.data.objects),'meshes':sum(o.type=='MESH' for o in bpy.data.objects),'empties':sum(o.type=='EMPTY' for o in bpy.data.objects),'material_count':len(bpy.data.materials),'packed_FILE_count':sum(im.source=='FILE' and bool(im.packed_file) for im in bpy.data.images),'targets':[],'protected_optics':[]}
 for name in ('CGH17 frontal crown root','CGH18 formed dorsal bill root cuff','CGH18 formed distal hooked bill plate'):
  o=bpy.data.objects[name];e=o.evaluated_get(deps);m=e.to_mesh(preserve_all_data_layers=True,depsgraph=deps);uv=o.data.uv_layers.active;rec={'object':name,'hide_render':o.hide_render,'hide_set':o.hide_get(),'hide_viewport':o.hide_viewport,'original_faces':len(o.data.polygons),'original_slot_face_counts':dict(collections.Counter(p.material_index for p in o.data.polygons)),'evaluated_faces':len(m.polygons),'evaluated_slot_face_counts':dict(collections.Counter(p.material_index for p in m.polygons)),'uv_layers':[u.name for u in o.data.uv_layers],'uv_active':uv.name,'uv_bounds':[[min(v.uv[i] for v in uv.data),max(v.uv[i] for v in uv.data)] for i in (0,1)],'modifiers':[{'name':z.name,'type':z.type,**({'material':z.material} if z.type=='BEVEL' else {})} for z in o.modifiers],'slots':[],'chart_landmarks':[]}
  for i,mat in enumerate(m.materials):
   rec['slots'].append({'index':i,'name':mat.name if mat else None,'images':[{'node':n.name,'image':n.image.name,'source':n.image.source,'packed':bool(n.image.packed_file),'bytes_sha256':hashlib.sha256(n.image.packed_file.data).hexdigest() if n.image.packed_file else None,'size':list(n.image.size),'colorspace':n.image.colorspace_settings.name} for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] if mat else []})
  # Native UV-to-local positions only; no geometry or UV mutation.
  for axis in (0,1):
   for val in (0.0,.25,.5,.75,1.):
    candidates=[(abs(float(v.uv[axis])-val),idx) for idx,v in enumerate(uv.data)];idx=min(candidates)[1];li=o.data.loops[idx];rec['chart_landmarks'].append({'axis':axis,'target':val,'loop':idx,'UV':list(uv.data[idx].uv),'local_position':list(o.data.vertices[li.vertex_index].co)})
  row['targets'].append(rec);e.to_mesh_clear()
 for o in bpy.data.objects:
  if o.type=='MESH' and o.name.startswith('CGO13'):
   row['protected_optics'].append({'object':o.name,'slots':[m.name if m else None for m in o.data.materials],'hide_render':o.hide_render,'hide_set':o.hide_get(),'hide_viewport':o.hide_viewport})
 out.append(row)
pathlib.Path('/tmp/cg-finish04-entry-inventory.json').write_text(json.dumps({'scope':'READONLY exact retained03 native targets/UV landmarks/evaluated material bindings and protected optics; no scene save/render/export/model mutation','eras':out},indent=2)+'\n');print('ENTRY_INVENTORY_COMPLETE')
