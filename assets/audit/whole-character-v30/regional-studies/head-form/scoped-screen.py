from pathlib import Path
import bpy,json,hashlib,runpy,math,bmesh
from mathutils import Vector
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=Path('/tmp/v30-head-form/attempt02');BASE=ROOT/'assets/models/whole-character-v29/attempt-fit01/murderbird-whole-character-v29.blend';NEW=OUT/'head-form.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Same strict native kernel frozen with its exact evaluated witness triangles.
s=(OUT/'executed-jaw-screen.py').read_text();exec(s[s.index('def inside'):s.index('poses=[]')])
changed=json.loads((OUT/'receipt.json').read_text())['result']['changedMeshes'];pack={'baseSHA256':sha(BASE),'nativeSHA256':sha(NEW),'sourceSHA256':sha(OUT/'executed-head-form.py'),'executedScreenSHA256':sha(Path(__file__)),'method':'Evaluated BVH candidates followed by edge-through-face strict interior crossing; planeepsilon1e-7m/barycentric1e-6. Interowner only. Discrete poses; coplanar/tangent/contained contacts excluded; not physical or continuous clearance.'}
propsets={};datasets={}
for label,path in [('base',BASE),('candidate',NEW)]:
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update()
 for o in bpy.data.objects:
  if o.animation_data:o.animation_data_clear()
 owners={'head','jaw','upper-bill','cranial-cover','builder-optics'};rest={n:bpy.data.objects[n].matrix_basis.copy() for n in ('jaw','cranial-cover')};rows=[]
 for kind,delta in [('jaw',0),('jaw',.16),('jaw',.32),('cap',0),('cap',.08)]:
  for n,m in rest.items():bpy.data.objects[n].matrix_basis=m
  if kind=='jaw':bpy.data.objects['jaw'].rotation_euler.x+=delta
  else:bpy.data.objects['cranial-cover'].location.z+=delta
  bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();items=[mesh(o,dg) for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name in owners];active={o.name for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name==('jaw' if kind=='jaw' else 'cranial-cover')};pairs=[]
  for a in items:
   if a[0] not in active:continue
   for b in items:
    if b[0] in active:continue
    strict=[];first=None
    for ia,ib in a[3].overlap(b[3]):
     A=[a[1][i] for i in a[2][ia]];B=[b[1][i] for i in b[2][ib]]
     if any(edge(A[k],A[(k+1)%3],B) or edge(B[k],B[(k+1)%3],A) for k in range(3)):
      strict.append((ia,ib))
      if first is None:first={'indices':[ia,ib],'activeTriangle':[list(x) for x in A],'neighborTriangle':[list(x) for x in B],'centroid':list(sum(A+B,Vector())/6)}
    if strict:pairs.append({'active':a[0],'neighbor':b[0],'trianglePairs':len(strict),'firstWitness':first})
  rows.append({'pose':kind,'delta':delta,'strictPairCount':len(pairs),'pairs':pairs})
 propsets[label]={n:json.loads(json.dumps(dict(bpy.data.objects[n].items()),default=lambda x:list(x))) for n in changed}
 datasets[label]=rows
pack['poses']=datasets;pack['eraPropsExactAllChanged']=propsets['base']==propsets['candidate'];pack['opticEraEvidence']={n:{k:v for k,v in propsets['candidate'][n].items() if k in ('region','surfaceRole','exteriorEras','minEra','maxEra','constructionClass','era','partRole')} for n in changed if any(p in n for p in ('optic','orbital bearing','retaining race'))};pack['visibilityContract']='Existing era tags preserved exactly; Maker/Mechanic filter excludes Advanced optic according to exteriorEras. No emission/material changes; actual browser illumination not tested.'
pack['comparisons']=[]
for a,b in zip(datasets['base'],datasets['candidate']):
 old={(p['active'],p['neighbor']) for p in a['pairs']};new={(p['active'],p['neighbor']) for p in b['pairs']};pack['comparisons'].append({'pose':a['pose'],'delta':a['delta'],'introduced':[list(x) for x in sorted(new-old)],'eliminated':[list(x) for x in sorted(old-new)],'inherited':[list(x) for x in sorted(old&new)]})
assert sha(BASE)==pack['baseSHA256'] and sha(NEW)==pack['nativeSHA256'];(OUT/'scoped-screen.json').write_text(json.dumps(pack,indent=2)+'\n');print(json.dumps({'comparisons':pack['comparisons'],'eraPropsExact':pack['eraPropsExactAllChanged'],'opticEraEvidence':pack['opticEraEvidence']}))
