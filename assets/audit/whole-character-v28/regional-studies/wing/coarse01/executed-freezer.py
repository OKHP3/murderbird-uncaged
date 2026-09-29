from pathlib import Path
import bpy,bmesh,runpy,json,hashlib,shutil
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=Path('/tmp/v28-wing-terminal/coarse01');BASE=ROOT/'assets/models/whole-character-v27/attempt-form01/murderbird-whole-character-v27.blend';native=OUT/'murderbird-v28-wing-terminal.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();mod=runpy.run_path(str(OUT/'executed-region.py'));tools=runpy.run_path(str(OUT/'triangle-screen-helper.py'),run_name='tooling');r=json.loads((OUT/'receipt.json').read_text());changed=r['result']['changedMeshes'];beforedata={};volume={}
bpy.ops.wm.open_mainfile(filepath=str(BASE));bpy.context.view_layer.update()
for entry in r['finiteSolids']:
 n=entry['name'];o=bpy.data.objects[n];side=1 if o.parent.name.startswith('left') else -1;label='left' if side==1 else 'right';joint=bpy.data.objects[label+'-wing-shield'].matrix_world.translation.copy();pts=[o.matrix_world@v.co for v in o.data.vertices];bounds=(min(p.z for p in pts),max(p.z for p in pts));kind='shield' if o.parent.name.endswith('wing-shield') else 'mantle'
 beforedata[n]={'x':[p.x for p in pts],'seats':[(i,tuple(v.co)) for i,v in enumerate(o.data.vertices) if mod['warp'](pts[i],side,joint,kind,n,bounds)[1]<=1e-9]}
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();bm=bmesh.new();bm.from_mesh(m);volume[n]=bm.calc_volume(signed=True);bm.free();ev.to_mesh_clear()
bpy.ops.wm.open_mainfile(filepath=str(native));bpy.context.view_layer.update();seatcounts=[];xerror=0
for n,s in beforedata.items():
 o=bpy.data.objects[n];assert all(tuple(o.data.vertices[i].co)==p for i,p in s['seats']),n;seatcounts.append({'name':n,'exactRootHousingVertices':len(s['seats'])});xerror=max(xerror,max(abs((o.matrix_world@v.co).x-x) for v,x in zip(o.data.vertices,s['x'])))
assert xerror<1e-6
rest={n:bpy.data.objects[n].matrix_local.copy() for n in ['left-mantle','right-mantle','left-wing-shield','right-wing-shield']}
def pose(angles):
 for n,a in zip(rest,angles):bpy.data.objects[n].matrix_local=rest[n]@Matrix.Rotation(a,4,'X')
 bpy.context.view_layer.update()
def item(name):
 o=bpy.data.objects[name];ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@p.co for p in m.vertices];t=[tuple(p.vertices) for p in m.loop_triangles];ev.to_mesh_clear();return v,t,BVHTree.FromPolygons(v,t,all_triangles=True)
comparison=[];witnesses=[]
for before,after in zip(r['poses']['before'],r['poses']['after']):
 old={tuple(sorted((p['a'],p['b']))) for p in before['pairs']};new={tuple(sorted((p['a'],p['b']))) for p in after['pairs']};introduced=[p for p in after['pairs'] if tuple(sorted((p['a'],p['b']))) not in old];comparison.append({'pose':after['pose'],'angles':after['wingAnglesRad'],'beforePairs':len(old),'afterPairs':len(new),'introducedPairs':introduced,'removedPairs':[list(p) for p in sorted(old-new)]})
 if after['pose'] not in ['folded','maker-wing','guard','short-shove']:continue
 pose(after['wingAnglesRad'])
 for pair in introduced[:4]:
  a=item(pair['a']);b=item(pair['b']);owner=next(o for o in pair['owners'] if 'wing-shield' in o);inv=bpy.data.objects[owner].matrix_world.inverted();points=[];first=None
  for i,j in a[2].overlap(b[2]):
   A=[a[0][n] for n in a[1][i]];B=[b[0][n] for n in b[1][j]]
   if tools['straddle'](A,B) and tools['straddle'](B,A):
    points.extend(inv@p for p in A+B)
    if first is None:first=[[list(inv@p) for p in A],[list(inv@p) for p in B]]
  witnesses.append({'pose':after['pose'],**pair,'relativeToElbow':owner,'triangleVertexBoundsLocalM':tools['bounds'](points),'firstStrictTrianglesLocal':first})
(OUT/'comparison.json').write_text(json.dumps(comparison,indent=2)+'\n');(OUT/'introduced-contact-witnesses.json').write_text(json.dumps({'method':'Evaluated mutual plane-straddle triangles epsilon1e-7m. Bounds are witness triangle-vertex bounds, not penetration depths.','witnesses':witnesses},indent=2)+'\n');r['exactSeatVertexCheck']=seatcounts;r['maximumNativeXCoordinateDifferenceM']=xerror;r['evaluatedVolumeRatios']=[{'name':p['name'],'beforeVolumeM3':volume[p['name']],'afterVolumeM3':p['signedVolumeM3'],'ratio':p['signedVolumeM3']/volume[p['name']]} for p in r['finiteSolids']];r['decision']={'status':'HOLD recommendation; one candidate complete; awaiting root visual gate; not integrated','visualObservation':'Compact aft-down terminal preserved. Upper receiving course is recessed and uneven, but still a distinct sleeve cue; whole folded guard hierarchy remains unresolved.','motionRegression':'Expanded wing scope: folded2→6 (4 introduced), Maker1→4 (3 introduced), guard6→5 (1 introduced/2 removed), short shove24→27 (4 introduced/1 removed).','exactNewRestPairs':'Each anatomical side: V21 refined mantle course6 plates6/7 versus same-side profiled mantle backing v4 wing-shield. Recessing/reshaping the YZ field introduces these pairs despite unchanged X section.','attachments':'Existing machinery, pivots and receiving-seat vertices exact. Root-to-liner gap comparison maximum new increase3.154mm; fastening/engineering continuity is not proven.','baselineScope':'Mantle forms plus shield forms are screened here. Do not compare raw counts to the older shield-only screen.','limits':'Finite native wing-angle sampling, triangle witnesses and qualitative renders only; no continuous clearance/physics or owner likeness acceptance.'};(OUT/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');shutil.copyfile(__file__,OUT/'executed-freezer.py');(OUT/'manifest.json').write_text(json.dumps({'status':'HOLD recommendation; not integrated','files':{p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='manifest.json'}},indent=2)+'\n');print(json.dumps({'source':sha(OUT/'executed-region.py'),'native':sha(native),'seatsExact':sum(p['exactRootHousingVertices'] for p in seatcounts),'nativeXMaxDifferenceM':xerror,'maxAttachmentIncrease':max(p['maxGapDeltaM'] for p in r['attachmentDeltas'])}))
