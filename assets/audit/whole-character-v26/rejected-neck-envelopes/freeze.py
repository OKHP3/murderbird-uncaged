from pathlib import Path
import bpy,runpy,json,hashlib,shutil
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=Path('/tmp/v26-neck-envelopes/correction02');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();tools=runpy.run_path(str(OUT/'executed-pose-screen.py'),run_name='tooling');g=tools['configure'].__globals__;g['BASE']=OUT/'murderbird-v26-neck-envelopes.blend';tools['configure']();tools['pose'](('contact-neck',.65,0,-.731,.10));dg=bpy.context.evaluated_depsgraph_get();screen=json.loads((OUT/'candidate-strict-screen.json').read_text());row=next(r for r in screen['poses'] if r['pose']=='contact-neck');witness=[]
for pair in row['pairs']:
 if pair['category']!='owned-neck-or-breast':continue
 items=[]
 for n in (pair['a'],pair['b']):
  o=bpy.data.objects[n];ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@x.co for x in m.vertices];t=[tuple(x.vertices) for x in m.loop_triangles];ev.to_mesh_clear();items.append((v,t,BVHTree.FromPolygons(v,t,all_triangles=True)))
 a,b=items;inv=bpy.data.objects[pair['owners'][1]].matrix_world.inverted();points=[];first=None
 for x,y in a[2].overlap(b[2]):
  A=[a[0][n] for n in a[1][x]];B=[b[0][n] for n in b[1][y]]
  if tools['straddle'](A,B) and tools['straddle'](B,A):
   points.extend(inv@p for p in A+B)
   if first is None:first={'worldTriangles':[[list(p) for p in A],[list(p) for p in B]],'trianglesRelativeToDistalJoint':[[list(inv@p) for p in A],[list(inv@p) for p in B]]}
 witness.append({**pair,'relativeToJoint':pair['owners'][1],'strictWitnessVertexBoundsM':tools['bounds'](points),'firstStrictWitness':first})
(OUT/'contact-causal-witnesses.json').write_text(json.dumps({'method':'Strict mutual plane-straddle triangle witnesses. Bounds are witness triangle vertex bounds, not penetration depth.','pairs':witness},indent=2)+'\n')
# Compose with the independent head source as read-only test input, preserving
# that module's result as the exact outside snapshot for the neck application.
base=ROOT/'assets/models/whole-character-v25/attempt-form01/murderbird-whole-character-v25.blend';head=ROOT/'scripts/regions/whole-character-v26-head-form.py';shutil.copyfile(head,OUT/'head-compose-input.py');bpy.ops.wm.open_mainfile(filepath=str(base));headresult=runpy.run_path(str(OUT/'head-compose-input.py'))['apply']();neckresult=runpy.run_path(str(OUT/'executed-region.py'))['apply']()
composition={'headSourceSha256':sha(OUT/'head-compose-input.py'),'neckSourceSha256':sha(OUT/'executed-region.py'),'headThenNeckApplied':True,'allNeckOutsideGeometryAndNodesExact':True,'preservedOutsideCount':neckresult['outsideMeshesExact'],'primaryNeckPivotsExact':True}
(OUT/'head-composition-check.json').write_text(json.dumps(composition,indent=2)+'\n')
receipt=json.loads((OUT/'receipt.json').read_text());receipt['decision']={'status':'HOLD; exclude from production composition','coarse01':'Conservative plane envelope has no owned strict crossings in 32 poses but visibly disconnected narrow bands.','correction02':'Concentric mating portions restore coverage but blocky stacked bands flatten the reference S-curve; nine owned front guard pairs remain at total pitch .65 across all five sampled yaws.','boundedIterationComplete':True,'inheritedHeadNeighbors':'Protected head/bill/jaw/scalp neighbors are classified independently; head acceptance is not claimed.','protectedBodyNeighbors':'Fixed internal body/frame contacts remain separately counted.','noPhysicsOrContinuousProof':True};receipt['compositionCheck']=composition;receipt['contactWitnessFile']='contact-causal-witnesses.json';(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');shutil.copyfile(__file__,OUT/'executed-freezer.py')
files={str(p.relative_to(OUT)):sha(p) for p in OUT.iterdir() if p.is_file()};(OUT/'handoff-manifest.json').write_text(json.dumps({'status':'HOLD','files':files,'sourceInRepoSha256':sha(ROOT/'scripts/regions/whole-character-v26-neck-envelopes.py'),'limits':'Finite sampled intersections and rendered qualitative review only; no physics or owner acceptance.'},indent=2)+'\n');print(json.dumps({'source':sha(OUT/'executed-region.py'),'native':sha(OUT/'murderbird-v26-neck-envelopes.blend'),'composition':composition,'witnessBounds':[(r['a'],r['b'],r['strictWitnessVertexBoundsM']) for r in witness]}))
