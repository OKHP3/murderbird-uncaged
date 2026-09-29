import bpy,math,json,hashlib,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root='/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged';source=root+'/scripts/regions/whole-character-v21-joint-clearance.py'
bpy.ops.wm.open_mainfile(filepath=root+'/assets/models/whole-character-v21/attempt-envelope03/murderbird-whole-character-v21.blend')
old={o.name:(o.parent.name if o.parent else None,tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(r) for r in o.matrix_world)) for o in bpy.data.objects if o.type=='MESH'}
s={};exec(compile(open(source).read(),source,'exec'),s);receipt=s['apply']()
changed=set(receipt['changed']);exact=sum(old[n]==(bpy.data.objects[n].parent.name,tuple(tuple(v.co) for v in bpy.data.objects[n].data.vertices),tuple(tuple(r) for r in bpy.data.objects[n].matrix_world)) for n in old if n not in changed)
assert exact==len(old)-len(changed)
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
bpy.context.scene.frame_set(1)
results=[]
for pitch in (0,.65,-.65):
 for name,value in [('neck',.35*pitch),('cervical-upper',.65*pitch),('head',-pitch),('cervical-joint-cover',.325*pitch)]:bpy.data.objects[name].rotation_euler=(value,0,0)
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();parts=[];finite=0;invalid=[]
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  ev=o.evaluated_get(dg);mesh=ev.to_mesh();mesh.calc_loop_triangles();pts=[ev.matrix_world@v.co for v in mesh.vertices]
  assert all(math.isfinite(v) for p in pts for v in p),o.name
  finite+=1
  if o.name in changed or o.name in receipt['added']:
   clone=mesh.copy()
   if clone.validate(verbose=False):invalid.append(o.name)
   bpy.data.meshes.remove(clone)
  if o.parent and o.parent.name in ('neck','cervical-upper','cervical-joint-cover'):
   tree=BVHTree.FromPolygons(pts,[tuple(t.vertices) for t in mesh.loop_triangles],all_triangles=True)
   parts.append((o.name,o.parent.name,tree))
  ev.to_mesh_clear()
 pairs=[]
 for i,a in enumerate(parts):
  for b in parts[i+1:]:
   if a[1]==b[1]:continue
   hits=a[2].overlap(b[2])
   if hits:pairs.append([a[0],b[0],len(hits)])
 results.append({'pitch':pitch,'finiteMeshes':finite,'validationRepairs':invalid,'screenedMeshes':len(parts),'crossingPairs':pairs})
print('JOINT_SMOKE',json.dumps({'sourceSHA256':hashlib.sha256(open(source,'rb').read()).hexdigest(),'unchangedOtherMeshes':exact,'changed':receipt['changed'],'added':receipt['added'],'poses':results}))
