from pathlib import Path
import bpy,json,hashlib,shutil,math
from mathutils import Vector,Matrix
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=Path('/tmp/v30-breast-form/coarse03/screen');OUT.mkdir(exist_ok=False);BASE=ROOT/'assets/models/whole-character-v29/attempt-fit01/murderbird-whole-character-v29.blend';NATIVE=OUT.parent/'murderbird-v30-breast-form.blend';REGION=OUT.parent/'executed-region.py';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(BASE)=='04040543c39e98dd3d20da3d51a5ba40fd87151315ef074d328276eed97c63e7';assert sha(NATIVE)=='f90d8f9176db62e007f7a578f23f388004f6cdf4b71f49a1016ff2b5cdda9969';assert sha(REGION)=='1aa3cde91888ceb4be5a42741c412b7eb3c825c1fd71ead5311f5870b0ccd90a';shutil.copyfile(Path(__file__),OUT/'executed-screen.py');shutil.copyfile(ROOT/'assets/audit/whole-character-v29/attempt-fit01/hinge-screen/executed-opening-screen.py',OUT/'preserved-strict-method-source.py');regional=json.loads((OUT.parent/'receipt.json').read_text());NEW=set(regional['result']['added']);OLD=set(regional['result']['removed']);WING=['left-mantle','right-mantle','left-wing-shield','right-wing-shield'];hinge={o for o in ['V23 breast opening captive shaft']};h=json.loads((ROOT/'assets/audit/whole-character-v29/regional-studies/breast-hinge/attempt02/receipt.json').read_text());hinge.update(h['result']['changedMeshes']+h['result']['added'])
def inside(p,tri):
 a,b,c=tri;v0=b-a;v1=c-a;v2=p-a;d00=v0.dot(v0);d01=v0.dot(v1);d11=v1.dot(v1);d20=v2.dot(v0);d21=v2.dot(v1);den=d00*d11-d01*d01
 if abs(den)<1e-18:return False
 u=(d11*d20-d01*d21)/den;v=(d00*d21-d01*d20)/den;return min(u,v,1-u-v)>1e-6
def edge(p,q,tri):
 n=(tri[1]-tri[0]).cross(tri[2]-tri[0])
 if n.length<1e-12:return False
 n.normalize();d0=n.dot(p-tri[0]);d1=n.dot(q-tri[0])
 if not(d0*d1<0 and abs(d0)>1e-7 and abs(d1)>1e-7):return False
 direction=q-p;hit=intersect_ray_tri(*tri,direction,p,True)
 if hit is None:return False
 t=(hit-p).dot(direction)/max(direction.length_squared,1e-30);return 1e-6<t<1-1e-6 and inside(hit,tri)
def evaluated(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();m.calc_loop_triangles();v=[e.matrix_world@p.co for p in m.vertices];t=[tuple(f.vertices) for f in m.loop_triangles];e.to_mesh_clear();assert all(math.isfinite(c) for p in v for c in p);return (o.name,o.parent.name if o.parent else '<world>',[[min(p[k] for p in v),max(p[k] for p in v)] for k in range(3)],v,t,BVHTree.FromPolygons(v,t,all_triangles=True))
STATES=[('closed-folded',0,0,0,0,0),('opening-25-folded',.275,0,0,0,0),('opening-50-folded',.55,0,0,0,0),('opening-75-folded',.825,0,0,0,0),('opening-100-folded',1.1,0,0,0,0),('closed-guard',0,.065,-.24,.18,.38),('closed-short-shove',0,.07,-.64,.18,.72)]
def screen(state,rest,skins):
 for n,a in zip(['breastplate']+WING,state[1:]):bpy.data.objects[n].matrix_local=rest[n]@Matrix.Rotation(a,4,'X')
 bpy.context.view_layer.update();items=[evaluated(o) for o in bpy.data.objects if o.type=='MESH' and 'builder' in o.get('exteriorEras','maker,mechanic,builder').split(',')];pairs=[]
 for i,a in enumerate(items):
  for b in items[i+1:]:
   if a[1]==b[1] or not(a[1]=='breastplate' or b[1]=='breastplate' or a[1] in WING or b[1] in WING or a[0] in skins or b[0] in skins) or any(a[2][k][1]<b[2][k][0] or b[2][k][1]<a[2][k][0] for k in range(3)):continue
   hits=0;first=None
   for x,y in a[5].overlap(b[5]):
    A=[a[3][n] for n in a[4][x]];B=[b[3][n] for n in b[4][y]]
    if any(edge(A[k],A[(k+1)%3],B) or edge(B[k],B[(k+1)%3],A) for k in range(3)):
     hits+=1
     if first is None:first={'aTriangle':[[round(c,6) for c in p] for p in A],'bTriangle':[[round(c,6) for c in p] for p in B]}
   if hits:pairs.append({'a':a[0],'b':b[0],'owners':[a[1],b[1]],'triangleWitnesses':hits,'skinInvolved':a[0] in skins or b[0] in skins,'hingeInvolved':a[0] in hinge or b[0] in hinge,'breastInvolved':a[1]=='breastplate' or b[1]=='breastplate','firstWitness':first})
 print('POSE_READY',state[0],len(pairs),sum(p['skinInvolved'] for p in pairs),flush=True);return {'pose':state[0],'breastOpeningRad':state[1],'wingAnglesRad':dict(zip(WING,state[2:])),'strictPairCount':len(pairs),'skinPairCount':sum(p['skinInvolved'] for p in pairs),'hingePairCount':sum(p['hingeInvolved'] for p in pairs),'completeBreastPairCount':sum(p['breastInvolved'] for p in pairs),'pairs':pairs,'evaluatedEligibleMeshCount':len(items)}
result={'status':'V30 body03 bounded discrete breast/wing/body neighbor diagnostic; provisional macroform, fit remains subject to witnesses','baseNativeSha256':sha(BASE),'candidateNativeSha256':sha(NATIVE),'sourceSha256':sha(REGION),'checkerSha256':sha(OUT/'executed-screen.py'),'strictMethod':'Evaluated triangle edge through strict triangle interior, copied from final V29 complete opening check; plane epsilon1e-7m,barycentric1e-6. Same-owner pairs excluded.','scope':'Five complete breast-opening angles0,.275,.55,.825,1.1 with wings folded plus closed-breast guard/shove. Complete breast and wing geometry plus body skin against all builder-era eligible mesh neighbors. Neck/head/legs at original V29 neutral rest; no excluded stance/head02 composition.','limits':['Seven discrete native poses, not continuous collision/contained overlap/physics proof or full controller body action.','Changed skin identities differ by reconstruction: classify exact inherited unchanged pairs separately from new geometry; inherited neighbor signature is context, not proof of same failure.','No automatic exemptions, likeness or engineering pass.'],'stages':{}}
for stage,path,skins in [('baseline',BASE,OLD),('body03',NATIVE,NEW)]:
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.scene.frame_set(1)
 for o in bpy.data.objects:
  if o.animation_data:o.animation_data_clear()
 bpy.context.view_layer.update();rest={n:bpy.data.objects[n].matrix_local.copy() for n in ['breastplate']+WING};result['stages'][stage]=[screen(s,rest,skins) for s in STATES];(OUT/'screen.json').write_text(json.dumps(result,indent=2)+'\n')
for bef,aft in zip(result['stages']['baseline'],result['stages']['body03']):
 old={tuple(sorted((p['a'],p['b']))) for p in bef['pairs']};base_neighbor=set()
 for p in bef['pairs']:
  for i,n in enumerate([p['a'],p['b']]):
   if n in OLD:base_neighbor.add((p['owners'][i],p['owners'][1-i],[p['b'],p['a']][i]))
 for p in aft['pairs']:
  p['exactPairIdentityInherited']=tuple(sorted((p['a'],p['b']))) in old;p['newSkinNeighborSignaturesPresentInBaseline']=[]
  for i,n in enumerate([p['a'],p['b']]):
   if n in NEW:
    signature=(p['owners'][i],p['owners'][1-i],[p['b'],p['a']][i]);p['newSkinNeighborSignaturesPresentInBaseline'].append({'signature':list(signature),'present':signature in base_neighbor})
 aft['exactInheritedPairIdentityCount']=sum(p['exactPairIdentityInherited'] for p in aft['pairs']);aft['newExactPairIdentityCount']=sum(not p['exactPairIdentityInherited'] for p in aft['pairs'])
assert sha(BASE)==result['baseNativeSha256'] and sha(NATIVE)==result['candidateNativeSha256'] and sha(REGION)==result['sourceSha256'];result['nativeSourcesUnchanged']=True;(OUT/'screen.json').write_text(json.dumps(result,indent=2)+'\n');print('COMPLETE',[(p['pose'],p['strictPairCount'],p['skinPairCount'],p['hingePairCount'],p['newExactPairIdentityCount']) for p in result['stages']['body03']],flush=True)
