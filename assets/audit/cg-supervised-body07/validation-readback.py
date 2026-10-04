import bpy, hashlib, json, math
from pathlib import Path
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[3]
SOURCE=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged/assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend')
OUT=ROOT/'assets/audit/cg-supervised-body07'
def digest(o):
 data={'type':o.type,'parent':o.parent.name if o.parent else None,'matrix_world':[list(r) for r in o.matrix_world],'matrix_local':[list(r) for r in o.matrix_local],'metadata':{k:repr(o[k]) for k in sorted(o.keys())}}
 if o.type=='MESH':
  d=o.data;data.update(vertices=[list(v.co) for v in d.vertices],edges=[list(e.vertices) for e in d.edges],polygons=[list(p.vertices) for p in d.polygons],uvs=[(u.name,[list(x.uv) for x in u.data]) for u in d.uv_layers],slots=[m.name if m else None for m in d.materials],indices=[p.material_index for p in d.polygons],colors=[(a.name,a.domain,a.data_type,[list(x.color) for x in a.data]) for a in d.color_attributes])
 return hashlib.sha256(repr(data).encode()).hexdigest()
def materials():
 rows={}
 for m in bpy.data.materials:
  if not m.use_nodes:continue
  rows[m.name]={'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links],'images':[(n.name,n.image.name if n.image else None,hashlib.sha256(bytes(n.image.packed_file.data)).hexdigest() if n.image and n.image.packed_file else None) for n in m.node_tree.nodes if n.type=='TEX_IMAGE']}
 return rows
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));frozen={o.name:digest(o) for o in bpy.context.scene.objects if o.type in ('MESH','EMPTY')};graphs=materials()
result={}
for attempt in ('attempt01','attempt02'):
 native=OUT/attempt/'murderbird-body07.blend';bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene
 changes=[n for n,h in frozen.items() if n not in s.objects or digest(s.objects[n])!=h];gm=materials();graphchanges=[n for n,v in graphs.items() if gm.get(n)!=v]
 rows=[]
 for o in s.objects:
  if not o.get('cgSupervisedBody07'):continue
  ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());md=ev.to_mesh();finite=all(math.isfinite(c) for v in md.vertices for c in v.co);ev.to_mesh_clear()
  rows.append({'name':o.name,'finiteEvaluated':finite,'uvEquivalent':o.data.uv_layers[0].name=='body05-local-curved-uv','normalizedUV':all(math.isfinite(c) and 0<=c<=1 for u in o.data.uv_layers for d in u.data for c in d.uv),'materialMetal05':[bool(m.get('cgMetal05Family')) for m in o.data.materials]})
 assert not changes and not graphchanges,(changes,graphchanges)
 assert all(r['finiteEvaluated'] and r['uvEquivalent'] and r['normalizedUV'] and all(r['materialMetal05']) for r in rows)
 result[attempt]={'nativeSHA256':hashlib.sha256(native.read_bytes()).hexdigest(),'preservedOriginalObjects':len(frozen),'originalDataUVSlotsIndicesTransformsParentsMetadataChanges':changes,'originalMaterialGraphsPackedTextureChanges':graphchanges,'proposedSheets':rows,'status':'Failed visual proposal; retain body05'}
(OUT/'validation-readback.json').write_text(json.dumps(result,indent=2)+'\n');print('INDEPENDENT_READBACK_PASS')
