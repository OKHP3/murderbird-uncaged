import bpy,hashlib,json,math,statistics,os
from pathlib import Path
from collections import Counter,defaultdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
source=root/'assets/models/uncaged-alignment-v7/murderbird-alignment-v7.blend'; partial=root/'assets/models/uncaged-head-construction-study-v2/iterations/attempt-05/murderbird-head-construction-study-v2-partial.blend'; audit=root/'assets/audit/head-construction-study-v2/iterations/attempt-05/partial-review'
script=root/'scripts/study-v7-head-construction.py'; code=script.read_text(); cutoff=code.index('if os.environ.get("HEAD_STUDY_DIAG") == "1":'); scope={'__file__':str(script)}; exec(compile(code[:cutoff],str(script),'exec'),scope)
snapshot=scope['snapshot'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Open source and capture full source contract.
bpy.ops.wm.open_mainfile(filepath=str(source)); base=snapshot(); base_bill={n:[tuple(v.co) for v in bpy.data.objects[n].data.vertices] for n in ['Profiled upper bill blade 0','Profiled upper bill blade 1']}
# Capture named protected structures.
protected=[n for n in base['objects'] if n.startswith(('Jaw','Seated Advanced optic','Recessed orbital bearing','Rounded swept crown lamina'))]
protected_sig={n:base['objects'][n] for n in protected}
bpy.ops.wm.open_mainfile(filepath=str(partial)); cand=snapshot(); names=['Forged orbital brow -1','Forged orbital brow 1','Cere root transition -1','Cere root transition 1','Broad swept cheek band -1','Broad swept cheek band 1']
changed=sorted(n for n in set(base['objects'])|set(cand['objects']) if base['objects'].get(n)!=cand['objects'].get(n))
outside=sorted(set(changed)-set(['Forged orbital brow -1','Forged orbital brow 1','Cere root transition -1','Cere root transition 1','Broad swept cheek band -1','Broad swept cheek band 1','Overlapping nasal hood','Profiled upper bill blade 0','Profiled upper bill blade 1']))
metadata_diffs={}
for n in names:
 a,b=base['objects'][n],cand['objects'][n]; metadata_diffs[n]=[k for k in a if k!='data' and a[k]!=b[k]]
protected_unchanged=all(cand['objects'].get(n)==s for n,s in protected_sig.items())
# Bill region checks.
bill_checks={}
for n in base_bill:
 old=base_bill[n]; new=[tuple(v.co) for v in bpy.data.objects[n].data.vertices]; yz_changed=sum(a[1:]!=b[1:] for a,b in zip(old,new)); distal=[]; roots=[]
 for j in range(57):
  t=.245*j/56 if n.endswith('0') else .25+.75*j/56
  rows=range(j*40,(j+1)*40)
  if n.endswith('1') and t>=.88: distal.extend(rows)
  if n.endswith('0') and t<.34: roots.extend(rows)
 distal_changed=sum(old[i]!=new[i] for i in distal) if distal else None
 bill_checks[n]={'yzChangedVertexCount':yz_changed,'vertexCount':len(new),'preservedContactApexVertexCount':len(distal),'changedPreservedContactApexVertices':distal_changed,'rootChangedVertices':sum(old[i]!=new[i] for i in roots)}
# Material comparison.
base_m={x[0]:x for x in base['materials']}; cand_m={x[0]:x for x in cand['materials']}; missing=sorted(set(base_m)-set(cand_m)); shared_diffs=sorted(n for n in set(base_m)&set(cand_m) if base_m[n]!=cand_m[n])
# Geometry metrics.
mesh_metrics=[]
for n in names:
 o=bpy.data.objects[n]; m=o.data; coords=[tuple(v.co) for v in m.vertices]; faces=[tuple(p.vertices) for p in m.polygons]
 inc=Counter(); dirs=defaultdict(list); edge_lengths=[]; areas=[]
 for face in faces:
  for q,a in enumerate(face):
   b=face[(q+1)%len(face)]; key=tuple(sorted((a,b)));inc[key]+=1;dirs[key].append((a,b))
 for e in m.edges: edge_lengths.append((e.vertices[0],e.vertices[1],math.dist(coords[e.vertices[0]],coords[e.vertices[1]])))
 for f in faces:
  if len(f)<3:continue
  p0=coords[f[0]]
  for q in range(1,len(f)-1):
   p1,p2=coords[f[q]],coords[f[q+1]];x=[p1[i]-p0[i] for i in range(3)];y=[p2[i]-p0[i] for i in range(3)];cross=[x[1]*y[2]-x[2]*y[1],x[2]*y[0]-x[0]*y[2],x[0]*y[1]-x[1]*y[0]];areas.append(.5*math.sqrt(sum(v*v for v in cross)))
 zero=[];edge_rows={k:[] for k in ['alongOuter','acrossOuter','alongInner','acrossInner','thickness']};N=57*13
 for skin in (0,1):
  base_i=skin*N
  for j in range(57):
   for k in range(13):
    i=base_i+j*13+k
    if j<56:edge_rows['alongOuter' if skin==0 else 'alongInner'].append((i,i+13,j,k))
    if k<12:edge_rows['acrossOuter' if skin==0 else 'acrossInner'].append((i,i+1,j,k))
    if skin==0:edge_rows['thickness'].append((i,i+N,j,k))
 for label,eds in edge_rows.items():
  vals=[(math.dist(coords[i],coords[j]),row,col) for i,j,row,col in eds]
  zero.append({'direction':label,'edgeCount':len(vals),'zeroUnder1e-7':sum(v[0]<1e-7 for v in vals),'under1e-5':sum(v[0]<1e-5 for v in vals),'maxM':max(v[0] for v in vals),'maxAtRowColumn':list(max(vals)[1:])})
 mesh_metrics.append({'name':n,'vertices':len(m.vertices),'faces':len(m.polygons),'boundaryEdges':sum(v==1 for v in inc.values()),'nonmanifoldEdges':sum(v>2 for v in inc.values()),'inconsistentSharedEdgeWinding':sum(1 for e,d in dirs.items() if len(d)==2 and d[0]==d[1]),'degenerateTrianglesUnder1e-10m2':sum(v<1e-10 for v in areas),'triangleCount':len(areas),'triangleAreaP01M2':sorted(areas)[int(.01*len(areas))],'minTriangleAreaM2':min(areas),'zeroLengthMeshEdges':sum(v[2]<1e-7 for v in edge_lengths),'maxMeshEdgeM':max(v[2] for v in edge_lengths),'maxGridEdgeByDirection':zero})
# Consistent final-host unions: exactly those present during fit, including unchanged hood for brow.
fit=[]
for kind in ('brow','cheek','cere'):
 for side in (-1,1):
  bn={'brow':f'Forged orbital brow {side}','cheek':f'Broad swept cheek band {side}','cere':f'Cere root transition {side}'}[kind]
  hosts=([f'Rounded swept crown lamina {i}' for i in range(4)]+[f'Swept temporal lamina {side} 0 0',f'Swept temporal lamina {side} 0 1',f'Forged orbital mounting plate {side}','Overlapping nasal hood'] if kind=='brow' else [f'Forged orbital mounting plate {side}'] if kind=='cheek' else ['Overlapping nasal hood','Profiled upper bill blade 0','Profiled upper bill blade 1'])
  vs=[];fs=[];off=0
  for hn in hosts:
   o=bpy.data.objects[hn]; vv=[o.matrix_world@v.co for v in o.data.vertices]; ff=[tuple(off+i for i in p.vertices) for p in o.data.polygons];vs.extend(vv);fs.extend(ff);off+=len(vv)
  tree=BVHTree.FromPolygons(vs,fs); o=bpy.data.objects[bn]; ps=[o.matrix_world@v.co for v in o.data.vertices[:741]]; hits=[tree.find_nearest(p) for p in ps];ds=[h[3] for h in hits];dots=[side*h[1].normalized().x if h[1] else None for h in hits]; good=[v for v in dots if v is not None]
  fit.append({'band':bn,'consistentSourceFitHosts':hosts,'outerSkinVertexCount':len(ds),'nearestFinalHostGapMeters':{'min':min(ds),'median':statistics.median(ds),'p90':sorted(ds)[int(.9*len(ds))],'max':max(ds)},'surfaceNormalTowardSideDot':{'min':min(good),'p10':sorted(good)[int(.1*len(good))],'median':statistics.median(good),'fractionNonpositive':sum(x<=0 for x in good)/len(good)}})
report={'title':'Attempt05 partial native read-only diagnostic','status':'held partial; not integrated, no final validation receipt, no acceptance','source':{'path':str(source.relative_to(root)),'sha256':sha(source)},'partial':{'path':str(partial.relative_to(root)),'sha256':sha(partial),'bytes':partial.stat().st_size},'changedObjects':changed,'outOfAllowlistChangedObjects':outside,'allowlist':['Forged orbital brow -1','Forged orbital brow 1','Cere root transition -1','Cere root transition 1','Broad swept cheek band -1','Broad swept cheek band 1','Overlapping nasal hood','Profiled upper bill blade 0','Profiled upper bill blade 1'],'unchangedTargetMetadataDifferences':metadata_diffs,'protectedJawOpticBearingCrownExact':protected_unchanged,'billChecks':bill_checks,'materials':{'missingZeroUserSourceMaterials':missing,'sharedMaterialSignatureDifferences':shared_diffs,'note':'The two authorized fake-user retention flags were applied after the early partial save, so these unused source datablocks are absent in the partial. No object material assignments changed.'},'finalHostDiagnostics':fit,'plateTopologyAndProjectionDiagnostics':mesh_metrics,'visualReview':{'receiptPath':'assets/audit/head-construction-study-v2/iterations/attempt-05/partial-review/receipt.json','observed':'Three-quarter/front/profile were actually inspected. Optic remains visible; brow/cere/cheek outlines contain visible folds/crumpling and uneven fit. Candidate is held and rejected for integration; bill retains a smooth hooked profile impression.'},'limits':['Original target meshes have 738 vertices for brows/cheeks and 284 for cere, versus 1482 in fitted output; source vertex indices are not correspondable. Grid edge diagnostics use the generated 57x13x2 adjacency, and quantify projection collapse/jumps instead of pretending a source-index displacement map.','No formal self-intersection/mesh collision validator was run beyond the documented optic precheck.','No final save/reload/material-retention check occurred; no GLB/runtime/pose validation or art acceptance.']}
out=audit/'attempt05-partial-geometry-diagnostic.json';out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out),'changed':changed,'fit':fit,'meshMetrics':mesh_metrics},indent=2))
