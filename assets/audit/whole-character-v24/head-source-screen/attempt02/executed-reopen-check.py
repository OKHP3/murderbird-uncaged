import bpy,json,hashlib,math,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=Path('/tmp/v24-head-study/attempt02');base=ROOT/'assets/models/whole-character-v23/attempt-form03/murderbird-whole-character-v23.blend';native=OUT/'head-rest.blend';lib=runpy.run_path(str(OUT/'executed-head.py'))
def props(o):return json.dumps(dict(o.items()),default=lambda x:list(x),sort_keys=True)
def material(m):
 def value(x):
  if x is None or isinstance(x,(float,int,bool,str)):return x
  if hasattr(x,'name'):return x.name
  return list(x)
 return (m.name,list(m.diffuse_color),m.metallic,m.roughness,[(n.name,n.bl_idname,[(s.name,value(s.default_value)) for s in n.inputs if hasattr(s,'default_value')]) for n in m.node_tree.nodes] if m.node_tree else [],[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links] if m.node_tree else [])
def snapshot(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update()
 return {'nodes':{o.name:([list(r) for r in o.matrix_world],o.parent.name if o.parent else None,props(o)) for o in bpy.data.objects if o.type=='EMPTY'},'outside':{o.name:lib['mesh_snapshot'](o) for o in bpy.data.objects if o.type=='MESH' and (not o.parent or o.parent.name not in lib['OWNERS'])},'materials':[material(m) for m in bpy.data.materials],'eras':{o.name:o.get('exteriorEras') for o in bpy.data.objects if o.type=='MESH'}}
a=snapshot(base);b=snapshot(native);assert a['nodes']==b['nodes'];assert a['outside']==b['outside'];assert a['materials']==b['materials'];assert all(b['eras'][n]==v for n,v in a['eras'].items())
finite=0;dg=bpy.context.evaluated_depsgraph_get();parts={}
for o in bpy.data.objects:
 if o.type!='MESH':continue
 ev=o.evaluated_get(dg);m=ev.to_mesh();assert all(math.isfinite(c) for v in m.vertices for c in v.co),o.name;finite+=1
 if o.parent and o.parent.name in {'jaw','upper-bill'}:
  m.calc_loop_triangles();p=[ev.matrix_world@v.co for v in m.vertices];tris=[tuple(t.vertices) for t in m.loop_triangles];parts[o.name]=(BVHTree.FromPolygons(p,tris,all_triangles=True),p,tris,o.parent.name)
 ev.to_mesh_clear()
def straddle(points,plane):
 n=(plane[1]-plane[0]).cross(plane[2]-plane[0]);n.normalize();d=[n.dot(p-plane[0]) for p in points];return min(d)<-1e-7 and max(d)>1e-7
pairs=[]
for name,a in parts.items():
 if a[3]!='jaw':continue
 for name2,b in parts.items():
  if b[3]!='upper-bill':continue
  hits=a[0].overlap(b[0]);strict=[]
  for i,j in hits:
   ta=[a[1][k] for k in a[2][i]];tb=[b[1][k] for k in b[2][j]]
   if straddle(ta,tb) and straddle(tb,ta):strict.append((i,j))
  if hits:pairs.append({'jaw':name,'bill':name2,'bvhTrianglePairs':len(hits),'noncoplanarInteriorStraddlePairs':len(strict),'toleranceM':1e-7})
r={'nativeSHA256':hashlib.sha256(native.read_bytes()).hexdigest(),'baseSHA256':hashlib.sha256(base.read_bytes()).hexdigest(),'checks':{'saveReopenOriginal54NodesExact':True,'outside562MeshSnapshotsExact':True,'materialDefinitionsExact':True,'originalEraEligibilityExact':True,'allEvaluatedMeshesFinite':finite},'restJawBillPairs':pairs,'limits':['BVH candidate pairs narrowed to mutual noncoplanar plane-straddles; no penetration-depth/continuous/whole-model clearance claim.']}
(OUT/'reopen-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
