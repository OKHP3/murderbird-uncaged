import bpy,numpy as np,pathlib,json,struct,hashlib,collections,datetime
ROOT=pathlib.Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged'); BASE=ROOT/'assets/audit/cg-recursive-three-loop01/loop01/delivery/retained02'
def decode(path):
 raw=path.read_bytes();magic,version,total=struct.unpack_from('<III',raw);assert(magic,version,total)==(0x46546c67,2,len(raw));n,t=struct.unpack_from('<II',raw,12);assert t==0x4e4f534a;d=json.loads(raw[20:20+n]);off=20+n;z,t=struct.unpack_from('<II',raw,off);assert t==0x004e4942;blob=raw[off+8:off+8+z];return d,blob
DT={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'};N={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
def acc(d,blob,i):
 a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];n=N[a['type']];dtype=np.dtype(DT[a['componentType']]);start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',n*dtype.itemsize);assert start+(a['count']-1)*stride+n*dtype.itemsize<=v.get('byteOffset',0)+v['byteLength'];return np.ndarray((a['count'],n),dtype=dtype,buffer=blob,offset=start,strides=(stride,dtype.itemsize)).copy()
def finger(rows):
 a=np.round(rows.astype('float64'),5);a[a==0]=0;a=a[np.lexsort(tuple(a[:,i] for i in range(a.shape[1]-1,-1,-1)))];return hashlib.sha256(a.astype('<f8').tobytes()).hexdigest()
results=[]
for era in ['builder','maker','mechanic']:
 path=BASE/era/('murderbird-recursive-'+era+'.blend');bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);dg=bpy.context.evaluated_depsgraph_get();groups=collections.defaultdict(list);uvgroups=collections.defaultdict(list);counts=collections.Counter();finite=True
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or o.hide_render or o.get('authoringGuide'):continue
  ev=o.evaluated_get(dg);m=ev.to_mesh(preserve_all_data_layers=True,depsgraph=dg)
  try:
   m.calc_loop_triangles();p=np.array([tuple(ev.matrix_world @ v.co) for v in m.vertices],dtype=np.float32);p=p[:,[0,2,1]];p[:,2]*=-1
   ts=np.array([list(t.vertices) for t in m.loop_triangles],np.int32);mi=np.array([t.material_index for t in m.loop_triangles],np.int32);finite=finite and bool(np.isfinite(p).all())
   for index in set(mi.tolist()):
    mat=m.materials[index];assert mat is not None;ix=mi==index;groups[mat.name].append(p[ts[ix]].reshape(-1,3));counts[mat.name]+=int(ix.sum())
   for u in m.uv_layers:
    a=np.empty(len(u.data)*2,np.float32);u.data.foreach_get('uv',a);finite=finite and bool(np.isfinite(a).all())
  finally:ev.to_mesh_clear()
 d,blob=decode(BASE/era/('murderbird-recursive-'+era+'.glb'));gcounts=collections.Counter();ggroups=collections.defaultdict(list);pr=[]
 for mesh in d['meshes']:
  for q in mesh['primitives']:
   assert q.get('mode',4)==4;idx=acc(d,blob,q['indices']).ravel();pos=acc(d,blob,q['attributes']['POSITION']);name=d['materials'][q['material']]['name'];assert idx.max()<len(pos);assert len(idx)%3==0;gcounts[name]+=len(idx)//3;ggroups[name].append(pos[idx]);channels=[]
   for label,ai in q['attributes'].items():
    a=acc(d,blob,ai);assert np.isfinite(a).all();assert len(a)==len(pos)
    if label.startswith('TEXCOORD'):channels.append(int(label.split('_')[1]))
   mat=d['materials'][q['material']];textures=[mat.get(k) for k in ['normalTexture','occlusionTexture','emissiveTexture']]+[mat.get('pbrMetallicRoughness',{}).get(k) for k in ['baseColorTexture','metallicRoughnessTexture']]
   for tex in [x for x in textures if x]:
    assert tex.get('texCoord',0) in channels;assert d['textures'][tex['index']]['source']<len(d['images'])
   pr.append({'material':name,'triangles':len(idx)//3,'UV_channels':channels})
 mismatches=[name for name in groups if name not in ggroups or finger(np.concatenate(groups[name]))!=finger(np.concatenate(ggroups[name]))]
 packed={hashlib.sha256(bytes(i.packed_file.data)).hexdigest():i.name for i in bpy.data.images if i.source=='FILE' and i.packed_file};images=[]
 for im in d['images']:
  v=d['bufferViews'][im['bufferView']];raw=blob[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];h=hashlib.sha256(raw).hexdigest();images.append({'name':im['name'],'sha256':h,'native_packed_name':packed.get(h),'native_packed_exact':h in packed})
 results.append({'era':era,'native_visible_triangle_counts':dict(counts),'glb_triangle_counts':dict(gcounts),'triangle_material_count_matches':counts==gcounts,'world_triangle_corner_position_multiset_rounded1e5_mismatches':mismatches,'native_positions_and_all_UVs_finite':finite,'GLB_attributes_indices_material_UV_texture_binding_bounds':'PASS','primitives':pr,'images':images,'skins':len(d.get('skins',[])),'animations':len(d.get('animations',[])),'external_URIs':sum('uri' in z for k in ['images','buffers'] for z in d.get(k,[]))})
 print('BINDING_ERA_COMPLETE',era,counts==gcounts,mismatches,flush=True)
pathlib.Path('/tmp/cg-recursive-loop01-final-evidence-bindings.json').write_text(json.dumps({'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Independently evaluated visible native meshes/slots/face triangle counts, finite all UVs and world-space triangle-corner positions compared per exact material name with independently decoded GLB at1e-5 rounding. GLB finite accessors/index/buffer/UV-to-material-texture reference bounds, embedded image hashes compared with all native packed FILE bytes. No producer helper import, saves, render or exports.','limits':'Position multiset/material association, not vertex-order proof; normals and UV corner value equivalence or complete shader graph/renderer equivalence not established. Unmatched embedded image bytes may reflect exporter-generated channel packing; explicitly report those instead of assuming faithfulness.','results':results},indent=2)+'\n')
