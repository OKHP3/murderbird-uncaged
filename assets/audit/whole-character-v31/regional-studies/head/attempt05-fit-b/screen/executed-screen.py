from pathlib import Path
import bpy,bmesh,json,hashlib,math
from mathutils import Vector
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=Path('/tmp/v31-head-reconstruction/attempt05-fit-b/screen');BASE=ROOT/'assets/models/whole-character-v30/attempt-form02/murderbird-whole-character-v30.blend';NEW=OUT.parent/'head-reconstruction.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=(OUT/'executed-strict-kernel.py').read_text();exec(s[s.index('def inside'):s.index('poses=[]')])
headowners={'head','jaw','upper-bill','cranial-cover','builder-optics','processing'};neckowners={'neck','cervical-mid-a','cervical-mid-b','cervical-upper'};datasets={};finite=[];eras=[]
for label,path in [('base',BASE),('candidate',NEW)]:
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update()
 for o in bpy.data.objects:
  if o.animation_data:o.animation_data_clear()
 rest={n:bpy.data.objects[n].matrix_basis.copy() for n in ('jaw','cranial-cover')};rows=[]
 for kind,delta in [('jaw',0),('jaw',.08),('jaw',.16),('jaw',.24),('jaw',.32),('cap',0),('cap',.08),('lower-head-neighbors',0)]:
  for n,m in rest.items():bpy.data.objects[n].matrix_basis=m
  if kind=='jaw':bpy.data.objects['jaw'].rotation_euler.x+=delta
  elif kind=='cap':bpy.data.objects['cranial-cover'].location.z+=delta
  bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();os=[o for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name in headowners|neckowners];items=[mesh(o,dg) for o in os];owners={o.name:o.parent.name for o in os}
  if kind=='lower-head-neighbors':active={o.name for o in os if (o.name.startswith('V31 formed throat receiving guard') if label=='candidate' else o.parent.name=='head')};neighbors={o.name for o in os if o.parent.name in neckowners}
  else:active={o.name for o in os if o.parent.name==('jaw' if kind=='jaw' else 'cranial-cover')};neighbors={o.name for o in os if o.parent.name in headowners and o.name not in active}
  pairs=[]
  for a in items:
   if a[0] not in active:continue
   for b in items:
    if b[0] not in neighbors or owners[a[0]]==owners[b[0]]:continue
    hits=0;first=None
    for ia,ib in a[3].overlap(b[3]):
     A=[a[1][i] for i in a[2][ia]];B=[b[1][i] for i in b[2][ib]]
     if any(edge(A[k],A[(k+1)%3],B) or edge(B[k],B[(k+1)%3],A) for k in range(3)):
      hits+=1
      if first is None:first={'indices':[ia,ib],'activeTriangle':[list(x) for x in A],'neighborTriangle':[list(x) for x in B],'centroid':list(sum(A+B,Vector())/6)}
    if hits:pairs.append({'active':a[0],'neighbor':b[0],'owners':[owners[a[0]],owners[b[0]]],'strictTrianglePairs':hits,'firstWitness':first})
  row={'pose':kind,'delta':delta,'strictPairCount':len(pairs),'pairs':pairs};rows.append(row);print(label,kind,delta,len(pairs),flush=True)
 datasets[label]=rows
 if label=='candidate':
  bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
  for o in os:
   if o.parent.name not in headowners or not (o.name.startswith('V31') or o.parent.name=='processing'):continue
   ev=o.evaluated_get(dg);m=ev.to_mesh();bm=bmesh.new();bm.from_mesh(m);m.calc_loop_triangles();bad=sum(not math.isfinite(c) for v in m.vertices for c in v.co);deg=sum((m.vertices[t.vertices[1]].co-m.vertices[t.vertices[0]].co).cross(m.vertices[t.vertices[2]].co-m.vertices[t.vertices[0]].co).length<1e-12 for t in m.loop_triangles);finite.append({'name':o.name,'owner':o.parent.name,'vertices':len(m.vertices),'triangles':len(m.loop_triangles),'nonFinite':bad,'degenerateTriangles':deg,'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'positiveVolumeM3':bm.calc_volume(signed=True)});bm.free();ev.to_mesh_clear();eras.append({'name':o.name,'owner':o.parent.name,'exteriorEras':o.get('exteriorEras'),'constructionClass':o.get('constructionClass'),'surfaceRole':o.get('surfaceRole')})
pack={'baseSHA256':sha(BASE),'nativeSHA256':sha(NEW),'moduleSHA256':sha(OUT.parent/'executed-head-reconstruction.py'),'executedScreenSHA256':sha(Path(__file__)),'kernelSHA256':sha(OUT/'executed-strict-kernel.py'),'method':'Evaluated BVH candidates; edge-through-face strict interior crossings. Interowner only. Discrete jaw/cap samples; lower head receiving guards versus cervical meshes at rest only. Coplanar/tangent/contained contacts not detected; no physics or continuous clearance. Exact pair attribution changes with complete reconstruction.','poses':datasets,'finite':finite,'eraEvidence':eras,'comparisons':[]}
for a,b in zip(datasets['base'],datasets['candidate']):
 old={(p['active'],p['neighbor']) for p in a['pairs']};new={(p['active'],p['neighbor']) for p in b['pairs']};pack['comparisons'].append({'pose':a['pose'],'delta':a['delta'],'inherited':sorted(old&new),'newIdentityPairs':sorted(new-old),'eliminatedIdentities':sorted(old-new)})
(OUT/'scoped-screen.json').write_text(json.dumps(pack,indent=2)+'\n');print(json.dumps({'counts':{k:[r['strictPairCount'] for r in v] for k,v in datasets.items()},'finiteBad':[v for v in finite if v['nonFinite'] or v['degenerateTriangles'] or v['nonManifoldEdges'] or v['positiveVolumeM3']<=0]}))
