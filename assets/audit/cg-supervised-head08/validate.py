"""Read-only saved-native material/hierarchy and GLB smoke checks."""
import bpy,json,hashlib,struct,math
from pathlib import Path
R=Path(__file__).resolve().parents[3];A=R/'assets/audit/cg-supervised-head08';I=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged/assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend')
def val(v):
 if isinstance(v,(float,int,bool,str)):return v
 try:return list(v)
 except TypeError:return str(v)
def material(m):
 return {'diffuse':list(m.diffuse_color),'props':dict(m.items()),'nodes':[(n.name,n.type,[(i.identifier,val(i.default_value)) for i in n.inputs if hasattr(i,'default_value')],n.image.name if hasattr(n,'image') and n.image else None) for n in m.node_tree.nodes] if m.use_nodes else [],'links':[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in m.node_tree.links] if m.use_nodes else []}
bpy.ops.wm.open_mainfile(filepath=str(I));s=bpy.context.scene
parents={o.name:o.parent.name if o.parent else None for o in s.objects};mats={m.name:material(m) for m in bpy.data.materials};protected={o.name for o in s.objects if o.type=='MESH' and not o.hide_render and any(x.startswith('protected-') for x in json.loads(o.get('cgSurfaceFamilies','[]')))}
res={'scope':'head-only study, not artistic acceptance','goal_remote_main':'251f2f0243181e97140179c2aff6eb057e165438','attempts':{}}
for attempt in ('attempt01','attempt02'):
 O=A/attempt;receipt=json.loads((O/'receipt.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(O/'formed-head08.blend'));s=bpy.context.scene
 changedmat=[n for n,d in mats.items() if n not in bpy.data.materials or material(bpy.data.materials[n])!=d];changedparent=[n for n,p in parents.items() if n not in s.objects or (s.objects[n].parent.name if s.objects[n].parent else None)!=p]
 missingprotected=[n for n in protected if n not in s.objects or s.objects[n].hide_render]
 glb=(O/'head08-static-smoke.glb').read_bytes();magic,version,length=struct.unpack_from('<4sII',glb);assert magic==b'glTF' and version==2 and length==len(glb)
 jsize,jtype=struct.unpack_from('<II',glb,12);assert jtype==0x4e4f534a;g=json.loads(glb[20:20+jsize]);bsize,btype=struct.unpack_from('<II',glb,20+jsize);assert btype==0x004e4942;binary=glb[28+jsize:28+jsize+bsize];bad=[];count=0
 for mesh in g['meshes']:
  for primitive in mesh['primitives']:
   a=g['accessors'][primitive['attributes']['POSITION']];v=g['bufferViews'][a['bufferView']];assert a['componentType']==5126 and a['type']=='VEC3';offset=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',12)
   for i in range(a['count']):
    xyz=struct.unpack_from('<3f',binary,offset+i*stride);count+=1
    if not all(math.isfinite(q) for q in xyz):bad.append([mesh.get('name'),i])
 r={'original_material_graphs_changed':changedmat,'original_parent_relationships_changed':changedparent,'protected_meshes_hidden_or_missing':missingprotected,'protected_mesh_count':len(protected),'glb_mesh_count':len(g['meshes']),'glb_position_count':count,'glb_nonfinite_positions':bad,'glb_animations':len(g.get('animations',[])),'saved_native_preservation':receipt['saved_native_preservation'],'evaluated_geometry':receipt['evaluated_geometry'],'before_after_camera_equality':all(receipt['cameras'][k]==receipt['cameras'][k.replace('before-','after-',1)] for k in receipt['cameras'] if k.startswith('before-'))}
 (O/'readback-diagnostic.json').write_text(json.dumps(r,indent=2)+'\n')
 assert not changedmat and not changedparent and not missingprotected and not bad and r['glb_mesh_count']==receipt['new_mesh_count'] and not r['glb_animations'] and r['before_after_camera_equality']
 r['status']='PASS';res['attempts'][attempt]=r
res['not_run']=['new local boundary wear reroute','three-era integrated export','browser parity','motion','runtime build','CI/deployment','owner acceptance','engineering']
(A/'validation.json').write_text(json.dumps(res,indent=2)+'\n');print('HEAD08_READBACK_PASS',flush=True)
