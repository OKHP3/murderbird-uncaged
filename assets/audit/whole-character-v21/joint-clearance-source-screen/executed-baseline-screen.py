import bpy,math,json,hashlib
from mathutils.bvhtree import BVHTree
root='/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged';source=root+'/scripts/regions/whole-character-v21-joint-clearance.py'
assert hashlib.sha256(open(source,'rb').read()).hexdigest()=='8aa7aadb8a1be71d65b073cc366a1aa9a1cc3128567ed7e3e5b614d409e1b6ac'
bpy.ops.wm.open_mainfile(filepath=root+'/assets/models/whole-character-v21/attempt-envelope03/murderbird-whole-character-v21.blend')
s={};exec(compile(open(source).read(),source,'exec'),s);receipt={}
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
bpy.context.scene.frame_set(1)
neckowners={'neck','cervical-upper','cervical-joint-cover'};adjacent={'head','jaw','upper-bill','body','breastplate'}
results=[];identities={}
for pitch in (-.65,-.4875,-.325,-.1625,0,.1625,.325,.4875,.65):
 for name,value in [('neck',.35*pitch),('cervical-upper',.65*pitch),('head',-pitch)]:bpy.data.objects[name].rotation_euler=(value,0,0)
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();groups={'neck':[],'adjacent':[]}
 for o in bpy.data.objects:
  if o.type!='MESH' or not o.parent:continue
  owner=o.parent.name
  if owner not in neckowners|adjacent:continue
  ev=o.evaluated_get(dg);mesh=ev.to_mesh();mesh.calc_loop_triangles();pts=[ev.matrix_world@v.co for v in mesh.vertices]
  tree=BVHTree.FromPolygons(pts,[tuple(t.vertices) for t in mesh.loop_triangles],all_triangles=True)
  lo=tuple(min(p[i] for p in pts) for i in range(3));hi=tuple(max(p[i] for p in pts) for i in range(3))
  groups['neck' if owner in neckowners else 'adjacent'].append((o.name,owner,tree,lo,hi))
  ev.to_mesh_clear()
 pairs=[]
 for a in groups['neck']:
  for b in groups['adjacent']:
   if a[1]==b[1] or any(a[4][i]<b[3][i] or b[4][i]<a[3][i] for i in range(3)):continue
   hits=a[2].overlap(b[2])
   if hits:
    key=(a[0],b[0]);row={'neckSurface':a[0],'neckOwner':a[1],'adjacentSurface':b[0],'adjacentOwner':b[1],'trianglePairs':len(hits)}
    pairs.append(row);identities.setdefault(key,[]).append([pitch,len(hits)])
 results.append({'pitch':pitch,'neckMeshCount':len(groups['neck']),'adjacentMeshCount':len(groups['adjacent']),'crossingPairCount':len(pairs),'summedTrianglePairs':sum(p['trianglePairs'] for p in pairs),'pairs':pairs})
packet={'sourceSHA256':hashlib.sha256(open(source,'rb').read()).hexdigest(),'screen':'evaluated triangulated BVH surface overlap; no exclusions or intentional-mating exemptions; no containment/penetration-depth/continuous guarantee','owners':{'neck':sorted(neckowners),'adjacent':sorted(adjacent)},'poses':results,'uniquePairs':[{'neckSurface':k[0],'adjacentSurface':k[1],'samples':v} for k,v in identities.items()]}
open('/tmp/v21-joint-baseline-result.json','w').write(json.dumps(packet,indent=2))
print('BASELINE_JOINT_SCREEN',json.dumps({'sourceSHA256':packet['sourceSHA256'],'poseCounts':[{'pitch':r['pitch'],'neckMeshes':r['neckMeshCount'],'adjacentMeshes':r['adjacentMeshCount'],'pairs':r['crossingPairCount'],'trianglePairs':r['summedTrianglePairs']} for r in results],'uniquePairs':packet['uniquePairs']}))
