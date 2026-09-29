from pathlib import Path
import bpy,bmesh,runpy,json,hashlib,shutil,math
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=Path('/tmp/v27-wing-terminal/coarse01');BASE=ROOT/'assets/models/whole-character-v26/attempt-form01/murderbird-whole-character-v26.blend';native=OUT/'murderbird-v27-wing-terminal.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();mod=runpy.run_path(str(OUT/'executed-region.py'));tools=runpy.run_path(str(OUT/'triangle-screen-helper.py'),run_name='tooling');r=json.loads((OUT/'receipt.json').read_text());changed=r['result']['changedMeshes'];beforedata={};volume={}
bpy.ops.wm.open_mainfile(filepath=str(BASE));bpy.context.view_layer.update()
for n in changed:
 o=bpy.data.objects[n];side=1 if o.parent.name.startswith('left') else -1;joint=o.parent.matrix_world.translation.copy();beforedata[n]=[(i,tuple(v.co)) for i,v in enumerate(o.data.vertices) if mod['warp'](o.matrix_world@v.co,side,joint)[1]==0]
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();bm=bmesh.new();bm.from_mesh(m);volume[n]=bm.calc_volume(signed=True);bm.free();ev.to_mesh_clear()
bpy.ops.wm.open_mainfile(filepath=str(native));bpy.context.view_layer.update();seatcounts=[]
for n,verts in beforedata.items():
 o=bpy.data.objects[n];assert all(tuple(o.data.vertices[i].co)==p for i,p in verts),n;seatcounts.append({'name':n,'exactRootHousingVertices':len(verts)})
rest={n:bpy.data.objects[n].matrix_local.copy() for n in ['left-mantle','right-mantle','left-wing-shield','right-wing-shield']}
def pose(angles):
 for n,a in zip(rest,angles):bpy.data.objects[n].matrix_local=rest[n]@Matrix.Rotation(a,4,'X')
 bpy.context.view_layer.update()
def item(name):
 o=bpy.data.objects[name];ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@p.co for p in m.vertices];t=[tuple(p.vertices) for p in m.loop_triangles];ev.to_mesh_clear();return v,t,BVHTree.FromPolygons(v,t,all_triangles=True)
comparison=[];witnesses=[]
for before,after in zip(r['poses']['before'],r['poses']['after']):
 old={tuple(sorted((p['a'],p['b']))) for p in before['pairs']};new={tuple(sorted((p['a'],p['b']))) for p in after['pairs']};introduced=[p for p in after['pairs'] if tuple(sorted((p['a'],p['b']))) not in old];comparison.append({'pose':after['pose'],'angles':after['wingAnglesRad'],'beforePairs':len(old),'afterPairs':len(new),'introducedPairs':introduced,'removedPairs':[list(p) for p in sorted(old-new)]})
 if after['pose'] not in ['maker-wing','short-shove']:continue
 pose(after['wingAnglesRad'])
 for pair in introduced[:3]:
  a=item(pair['a']);b=item(pair['b']);owner=next(o for o in pair['owners'] if 'wing-shield' in o);inv=bpy.data.objects[owner].matrix_world.inverted();points=[];first=None
  for i,j in a[2].overlap(b[2]):
   A=[a[0][n] for n in a[1][i]];B=[b[0][n] for n in b[1][j]]
   if tools['straddle'](A,B) and tools['straddle'](B,A):
    points.extend(inv@p for p in A+B)
    if first is None:first=[[list(inv@p) for p in A],[list(inv@p) for p in B]]
  witnesses.append({'pose':after['pose'],**pair,'relativeToElbow':owner,'triangleVertexBoundsLocalM':tools['bounds'](points),'firstStrictTrianglesLocal':first})
(OUT/'comparison.json').write_text(json.dumps(comparison,indent=2)+'\n');(OUT/'introduced-contact-witnesses.json').write_text(json.dumps({'method':'Evaluated mutual plane-straddle triangles epsilon1e-7m. Bounds are witness triangle-vertex bounds, not penetration depths.','witnesses':witnesses},indent=2)+'\n');r['exactSeatVertexCheck']=seatcounts;r['evaluatedVolumeRatios']=[{'name':p['name'],'beforeVolumeM3':volume[p['name']],'afterVolumeM3':p['signedVolumeM3'],'ratio':p['signedVolumeM3']/volume[p['name']]} for p in r['finiteSolids']];r['decision']={'status':'HOLD for new motion crossings; one coarse visual gate only; not integrated','visualObservation':'Shorter fore edge, tapered lower section and layered aft-down outline retain the compact flightless guard. Inherited horizontal upper shoulder/shield overlap remains.','motionRegression':'Folded0→0; Maker0→2; guard5→21; short shove23→35 (14 introduced,2 removed). Lifting/tapering the terminal liner/returns places them in the mantle lower-course swept space.','attachments':'Actual bearing/load-frame meshes and named rests exact; authored root/housing vertices exactly retained. Root-to-liner gaps are comparisons, not fastening proof: inherited maximum40.7mm; maximum new increase0.130mm.','controlPolicy':'Native rest-relative localX proof uses current controller angles: Maker right mantle-.38/shield+.16; short shove right-.64/+.72, restricted anatomical left+.07/+.18. No src edits.','limits':'Finite discrete pose screen, finite closed positive solid validation and qualitative renders only; no continuous collision/physics or owner likeness acceptance.'};(OUT/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');shutil.copyfile(__file__,OUT/'executed-freezer.py');(OUT/'manifest.json').write_text(json.dumps({'status':'HOLD; not integrated','files':{p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='manifest.json'}},indent=2)+'\n');print(json.dumps({'source':sha(OUT/'executed-region.py'),'native':sha(native),'seatsExact':sum(p['exactRootHousingVertices'] for p in seatcounts),'volumeRatioRange':[min(p['ratio'] for p in r['evaluatedVolumeRatios']),max(p['ratio'] for p in r['evaluatedVolumeRatios'])]}))
