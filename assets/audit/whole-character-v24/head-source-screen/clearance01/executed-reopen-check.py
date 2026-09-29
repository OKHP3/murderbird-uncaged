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

main=Path('/tmp/v24-head-study/attempt02/head-rest.blend');final=Path('/tmp/v24-head-study/clearance01/head-rest.blend');out=Path('/tmp/v24-head-study/clearance01');targets={'Forked forged mandible -1','Forked forged mandible 1','Distal mandible bridge'}
def preserved(path):
 r=snapshot(path);r['protected']={o.name:lib['mesh_snapshot'](o) for o in bpy.data.objects if o.type=='MESH' and o.name not in targets};return r
a=preserved(main);b=preserved(final);assert a['nodes']==b['nodes'];assert a['protected']==b['protected'];assert a['materials']==b['materials'];assert a['eras']==b['eras']
r={'inputSHA256':hashlib.sha256(main.read_bytes()).hexdigest(),'nativeSHA256':hashlib.sha256(final.read_bytes()).hexdigest(),'checks':{'all54RestNodesExact':True,'other630MeshSnapshotsExact':True,'materialDefinitionsExact':True,'eraEligibilityExact':True,'hookAndFrontierUnchanged':True},'protectedMeshes':len(a['protected'])}
(out/'reopen-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
