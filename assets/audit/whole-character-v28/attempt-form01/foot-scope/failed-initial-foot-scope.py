"""Read-only recursive foot scope check of exact V27 and V28 saved natives."""
from pathlib import Path
import bpy,json,runpy,hashlib,math
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=Path(__file__).parent
BASE=ROOT/'assets/models/whole-character-v27/attempt-form01/murderbird-whole-character-v27.blend';NEW=ROOT/'assets/models/whole-character-v28/attempt-form01/murderbird-whole-character-v28.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(BASE)=='3014ae3156f552716fcd34437b9ace9d567092ff4b99d3a3ded2e6f8bde66ceb';assert sha(NEW)=='a956aa9982d3e32c79433fb68b673f0d4f23a06b4c1f70838dbe835459c0c978'
builderReceipt=ROOT/'assets/audit/whole-character-v28/attempt-form01/receipt.json';builderSHA=sha(builderReceipt);r=json.loads(builderReceipt.read_text());footregion=next(a for a in r['regions'] if 'foot-presence' in a['source']['path']);declared=footregion['result']['changedObjects'];assert len(declared)==18
h=runpy.run_path(str(ROOT/'scripts/build-uncaged-alignment-v7.py'))
def descendant(o):
 while o:
  if o.name in ['left-foot','right-foot']:return True
  o=o.parent
 return False
def bounds(pp):return [[min(p[i] for p in pp),max(p[i] for p in pp)] for i in range(3)]
def collect(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();snap=h['scene_snapshot']();dg=bpy.context.evaluated_depsgraph_get();m={};n={}
 for o in bpy.data.objects:
  if not descendant(o):continue
  if o.type=='EMPTY':n[o.name]={'snapshot':snap['empties'][o.name],'props':h['id_properties'](o),'localMatrix':[list(x) for x in o.matrix_local]}
  if o.type=='MESH':
   ev=o.evaluated_get(dg);me=ev.to_mesh();pp=[list(ev.matrix_world@v.co) for v in me.vertices];assert all(math.isfinite(c) for p in pp for c in p),o.name;ev.to_mesh_clear()
   m[o.name]={'snapshot':snap['meshes'][o.name],'raw':[list(v.co) for v in o.data.vertices],'world':[list(o.matrix_world@v.co) for v in o.data.vertices],'evaluatedBounds':bounds(pp),'finiteEvaluatedVertexCount':len(pp)}
 return m,n,{mat.name:h['material_signature'](mat) for mat in bpy.data.materials}
a,an,am=collect(BASE);b,bn,bm=collect(NEW);assert a.keys()==b.keys();assert an==bn;assert am==bm
changed=[name for name in a if a[name]['raw']!=b[name]['raw']];assert set(changed)==set(declared),(changed,declared)
protected=[];targets=[];claws=[];guards=[]
for name in sorted(a):
 old,new=a[name],b[name]
 if name not in declared:
  assert old==new,name;protected.append(name);continue
 os,ns=old['snapshot'],new['snapshot'];assert os['parent']==ns['parent'] and os['matrix']==ns['matrix'] and os['modifiers']==ns['modifiers'] and os['visibility']==ns['visibility'],name
 # Preserve topology/material/era/rests; one declared revision-property added.
 op=dict(os['props']);np=dict(ns['props']);np.pop('footPresenceRevision');assert op==np,name
 oldobj=old['raw'];newobj=new['raw'];assert len(oldobj)==len(newobj);targets.append(name)
 # mesh_signature includes vertices, polygons and material assignment. Check
 # unchanged material slots from the native object's actual data directly.
 o=bpy.data.objects[name];assert o.get('exteriorEras')=='maker,mechanic,builder';assert o.parent and descendant(o.parent)
 if 'tapered claw sheath' in name:
  dx=max(abs(p[0]-q[0]) for p,q in zip(old['world'],new['world']));dz=max(abs(p[2]-q[2]) for p,q in zip(old['world'],new['world']));assert dx<=1e-7 and dz<=1e-7,name
  ob=bounds(old['world']);nb=bounds(new['world']);ol=ob[1][1]-ob[1][0];nl=nb[1][1]-nb[1][0];assert abs(nl/ol-.8)<2e-6;assert ob[2][0]==nb[2][0]
  claws.append({'name':name,'owner':ns['parent'],'maxWorldXDeltaM':dx,'maxWorldZDeltaM':dz,'worldXZVertexProfilesExactlyEqual':all(p[0]==q[0] and p[2]==q[2] for p,q in zip(old['world'],new['world'])),'beforeYLengthM':ol,'afterYLengthM':nl,'ratio':nl/ol,'minimumWorldZBeforeM':ob[2][0],'minimumWorldZAfterM':nb[2][0],'minimumWorldZExactlyEqual':True})
 else:
  # Independently recompute the declared ring-centered guard reprofile.
  ys=sorted(p[1] for p in oldobj);stations=[]
  for y in ys:
   if not stations or abs(y-stations[-1])>.0007:stations.append(y)
  centers=[]
  for y in stations:
   ring=[p for p in oldobj if abs(p[1]-y)<=.0007];centers.append((sum(p[0] for p in ring)/len(ring),sum(p[2] for p in ring)/len(ring)))
  errors=[]
  for p,q in zip(oldobj,newobj):
   k=min(range(len(stations)),key=lambda i:abs(stations[i]-p[1]));cx,cz=centers[k];expect=[cx+(p[0]-cx)*1.18,p[1],cz+.002+(p[2]-cz)*1.58];errors.append(max(abs(v-w) for v,w in zip(expect,q)))
  assert max(errors)<1e-7,name
  guards.append({'name':name,'owner':ns['parent'],'maxDeclaredProfileDeltaM':max(errors),'beforeEvaluatedWorldBounds':old['evaluatedBounds'],'afterEvaluatedWorldBounds':new['evaluatedBounds'],'finiteEvaluatedVertexCount':new['finiteEvaluatedVertexCount'],'longitudinalStationsExact':all(p[1]==q[1] for p,q in zip(oldobj,newobj)),'sectionContract':'Station-centered X1.18; Z1.58 plus2mm; Y unchanged'})
# Exact target material slots/indices and topology using fresh independently
# read source records; remove only raw coordinate contribution from snapshots.
for name in targets:
 oldmesh=a[name]['snapshot']['mesh'];newmesh=b[name]['snapshot']['mesh']
 assert oldmesh.keys()==newmesh.keys()
 for k in oldmesh:
  if k not in ['vertices','vertexPositions']:
   assert oldmesh[k]==newmesh[k],(name,k)
assert len(claws)==6 and len(guards)==12;assert sha(BASE)=='3014ae3156f552716fcd34437b9ace9d567092ff4b99d3a3ded2e6f8bde66ceb';assert sha(NEW)=='a956aa9982d3e32c79433fb68b673f0d4f23a06b4c1f70838dbe835459c0c978';assert sha(builderReceipt)==builderSHA
out={'status':'PASS narrowly scoped recursive foot geometry preservation/reprofile check; no movement or collision clearance acceptance','base':{'path':str(BASE),'sha256':sha(BASE)},'candidate':{'path':str(NEW),'sha256':sha(NEW)},'executedSourceSHA256':sha(Path(__file__)),'frozenBuilderReceiptSHA256':builderSHA,'footModule':footregion['source'],'scopeCorrection':{'recursiveFootDescendantMeshes':len(a),'changedDeclaredDigitMeshes':len(changed),'otherFootMeshesExactlyPreserved':len(protected),'footRelatedNodeRestsParentsPropsExactlyPreserved':len(an),'builderLimitedFootPredicateProtectedCount':40,'builderLimitedFootPredicateRevisedCount':0,'explanation':'The builder historical name predicate covers foot/toe owners but omits digit descendants. Its40protected/0revised count is incomplete scope evidence; this independent recursive walk finds18declareddigit changes and40unchanged foot meshes. Frozen builder receipt not rewritten.'},'changedMeshes':sorted(changed),'protectedMeshes':protected,'footNodes':sorted(an),'materialsDefinitionsExact':True,'targetTopologyMaterialSlotsEraTagsParentingTransformsExact':True,'claws':claws,'guards':guards,'limits':['Saved-rest geometry/profile check only; no collision, continuous travel, grounded motion or physics approval.','World X/Z profiles and minimum floor height verify curved claw cross-section preservation; shortening Y changes the full3D fore-aft shape deliberately.']}
(OUT/'receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out['scopeCorrection']))
