import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils.bvhtree import BVHTree
root=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
source=root/'scripts/regions/whole-character-v22-neck-guards.py';base=root/'assets/models/whole-character-v22/attempt-frame04/murderbird-whole-character-v22.blend'
assert hashlib.sha256(base.read_bytes()).hexdigest()=='b3ac4677d2e76a0e08544323306c07f2ed7e61cd381d274a944d8e5b87031d1f'
bpy.ops.wm.open_mainfile(filepath=str(base));s={};exec(compile(source.read_text(),str(source),'exec'),s)
receipt=s['apply']();rest={n:bpy.data.objects[n].rotation_euler.copy() for n in ('neck','cervical-upper','head','cervical-joint-cover')}
# Remove incoming head action in memory only so specified counterpitch is actually applied.
for n in rest:
 o=bpy.data.objects[n]
 if o.animation_data:o.animation_data_clear()
solids=[];dg=bpy.context.evaluated_depsgraph_get()
for n in receipt['changed']:
 o=bpy.data.objects[n];ev=o.evaluated_get(dg);m=ev.to_mesh();clone=m.copy();assert not clone.validate(verbose=False),n;bpy.data.meshes.remove(clone)
 assert all(math.isfinite(c) for v in m.vertices for c in v.co),n
 bm=bmesh.new();bm.from_mesh(m);assert all(e.is_manifold for e in bm.edges),n;volume=bm.calc_volume(signed=True);assert volume>0,n;bm.free();ev.to_mesh_clear();solids.append({'name':n,'volumeM3':volume,'owner':o.parent.name})
poses=[];owners=('neck','cervical-upper','cervical-joint-cover','head','jaw','upper-bill','cranial-cover','builder-optics','breastplate','body')
for pitch in (-.65,-.4875,-.325,-.1625,0,.1625,.325,.4875,.65):
 for n,fraction in (('neck',.35),('cervical-upper',.65),('head',-1),('cervical-joint-cover',.325)):
  bpy.data.objects[n].rotation_euler=rest[n];bpy.data.objects[n].rotation_euler.x+=pitch*fraction
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();parts={}
 for o in bpy.data.objects:
  if o.type!='MESH' or not o.parent or o.parent.name not in owners:continue
  ev=o.evaluated_get(dg);m=ev.to_mesh();pts=[ev.matrix_world@v.co for v in m.vertices];m.calc_loop_triangles();tris=[tuple(t.vertices) for t in m.loop_triangles]
  parts[o.name]=(o.parent.name,BVHTree.FromPolygons(pts,tris,all_triangles=True),[min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]);ev.to_mesh_clear()
 pairs=[]
 for name in receipt['changed']:
  a=parts[name]
  for name2,b in parts.items():
   if a[0]==b[0] or(name2 in receipt['changed'] and name2<name):continue
   if any(a[3][i]<b[2][i] or b[3][i]<a[2][i] for i in range(3)):continue
   hits=a[1].overlap(b[1])
   if hits:pairs.append([name,name2,len(hits)])
 poses.append({'pitch':pitch,'pairs':pairs});print('POSE',pitch,json.dumps(pairs))
result={'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'baseSHA256':hashlib.sha256(base.read_bytes()).hexdigest(),'applyReceipt':receipt,'closedPositiveSolids':solids,'poses':poses,'limits':['Only changed12guards against direct scoped neighbors; evaluated triangle BVH, not containment/depth/continuous proof.','No native/save/export/render.','Same-owner interfaces excluded.']}
Path('/tmp/v22-neck-guard-smoke.json').write_text(json.dumps(result,indent=2)+'\n');print('SOURCE',result['sourceSHA256'])
