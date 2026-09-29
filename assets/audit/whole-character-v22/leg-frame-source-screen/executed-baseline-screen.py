import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
root=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
base=root/'assets/models/whole-character-v21/attempt-construction06/murderbird-whole-character-v21.blend'
source=Path(__file__).with_name('executed-leg-frame.py')
assert hashlib.sha256(base.read_bytes()).hexdigest()=='79ad3e368e7b75edbbc758b1264a1ccaf34f284c6ca185ee8441875576a6f54c'
bpy.ops.wm.open_mainfile(filepath=str(base));s={};exec(compile(source.read_text(),str(source),'exec'),s);receipt={'changed':[o.name for o in bpy.data.objects if o.type=='MESH' and 'tapered passive load rail' in o.name and o.parent and o.parent.name in s['OWNERS']], 'added':[], 'removed':[], 'status':'unaltered Construction06 baseline'}
dg=bpy.context.evaluated_depsgraph_get();changed=set(receipt['changed']+receipt['added']);finite=0;repairs=[];solids=[];parts={}
for o in bpy.data.objects:
 if o.type!='MESH':continue
 ev=o.evaluated_get(dg);m=ev.to_mesh();pts=[ev.matrix_world@v.co for v in m.vertices]
 assert all(math.isfinite(c) for p in pts for c in p),o.name;finite+=1
 if o.name in changed:
  cp=m.copy()
  if cp.validate(verbose=False):repairs.append(o.name)
  bpy.data.meshes.remove(cp)
  bm=bmesh.new();bm.from_mesh(m)
  assert all(e.is_manifold for e in bm.edges),o.name
  volume=bm.calc_volume(signed=True);assert volume>0,o.name;bm.free()
  assert o.parent.name in s['OWNERS'] and o['exteriorEras']==s['ERAS'] and o['constructionClass']=='inherited-passive'
  solids.append({'name':o.name,'owner':o.parent.name,'signedVolumeM3':volume})
 if o.parent and o.parent.name in s['OWNERS']+('left-foot','right-foot','body','left-mantle','right-mantle'):
  m.calc_loop_triangles();faces=[tuple(t.vertices) for t in m.loop_triangles]
  parts[o.name]=(o.parent.name,BVHTree.FromPolygons(pts,faces,all_triangles=True),[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)])
 ev.to_mesh_clear()
pairs=[]
for name in sorted(changed):
 a=parts[name]
 for other,b in parts.items():
  if b[0]==a[0] or (other in changed and other<name):continue
  if any(a[3][i]<b[2][i] or b[3][i]<a[2][i] for i in range(3)):continue
  hits=a[1].overlap(b[1])
  if hits:pairs.append([name,other,len(hits)])
result={'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'baseSHA256':hashlib.sha256(base.read_bytes()).hexdigest(),'finiteEvaluatedMeshes':finite,'validationRepairs':repairs,'closedPositiveChangedMeshes':len(solids),'solids':solids,'applyReceipt':receipt,'restAdjacentInterownerPairs':pairs,'limitations':['Rest-only evaluated triangulated BVH screen, not motion clearance.','Same-owner attached parts excluded.','No containment/depth/whole-character proof.','No native save, render, export or runtime modification.']}
Path(__file__).with_name('baseline-result.json').write_text(json.dumps(result,indent=2)+'\n')
print('V22_BASELINE',json.dumps({k:v for k,v in result.items() if k not in ('solids','applyReceipt')}))
