"""Write-once actual-triangle delta screen; Blender --python FILE -- BASE CANDIDATE OUTPUT.
Read-only native models. Shared-owner support/lapped plates excluded deliberately.
"""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Matrix
from mathutils.bvhtree import BVHTree

base,candidate,output=map(Path,sys.argv[sys.argv.index('--')+1:])
if output.exists():raise RuntimeError('Write-once screen output already exists')
POSES={'rest':{},'tucked':{'right-mantle':-.12,'right-wing-shield':.10},'thrust':{'right-mantle':-.64,'right-wing-shield':.72,'left-mantle':.07,'left-wing-shield':.18},'restricted-left':{'left-mantle':.07,'left-wing-shield':.18}}
SHELLS={f'V37 {s} {k} silhouette shell' for s in ('left','right') for k in ('shoulder','tucked elbow')}
def record(o):
 mesh=o.data;mesh.calc_loop_triangles();points=[o.matrix_world@v.co for v in mesh.vertices]
 lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)]
 tris=[tuple(t.vertices) for t in mesh.loop_triangles]
 return {'name':o.name,'group':o.get('sourceEnvelope',o.name),'owner':o.parent.name if o.parent else None,'lo':lo,'hi':hi,'points':points,'tris':tris,'bvh':None}
def overlaps(a,b):
 if any(a['hi'][i]<b['lo'][i] or b['hi'][i]<a['lo'][i] for i in range(3)):return 0
 for x in (a,b):
  if x['bvh'] is None:x['bvh']=BVHTree.FromPolygons(x['points'],x['tris'],all_triangles=True,epsilon=1e-7)
 return len(a['bvh'].overlap(b['bvh']))
def screen(path):
 result={}
 for label,angles in POSES.items():
  bpy.ops.wm.open_mainfile(filepath=str(path))
  for owner,angle in angles.items():o=bpy.data.objects[owner];o.matrix_basis=o.matrix_basis@Matrix.Rotation(angle,4,'X')
  bpy.context.view_layer.update()
  rows=[record(o) for o in bpy.data.objects if o.type=='MESH' and len(o.data.vertices) and o.get('authoringGuide') is not True and 'builder' in str(o.get('exteriorEras','maker,mechanic,builder')).split(',')]
  selected=[r for r in rows if r['group'] in SHELLS];pairs={};actual=[];tested=0
  for a in selected:
   for b in rows:
    if a['name']==b['name'] or a['owner']==b['owner']:continue
    if b['group'] in SHELLS and a['name']>b['name']:continue
    tested+=1;n=overlaps(a,b)
    if n:
     key=' | '.join(sorted((a['group'],b['group'])));pairs[key]=pairs.get(key,0)+n
     actual.append({'a':a['name'],'b':b['name'],'trianglePairs':n})
  result[label]={'testedObjectPairs':tested,'aggregatePairTriangleCounts':pairs,'actualCrossOwnerIntersections':actual}
 return result

before=screen(base);after=screen(candidate);deltas={}
for pose in POSES:
 old=before[pose]['aggregatePairTriangleCounts'];new=after[pose]['aggregatePairTriangleCounts']
 deltas[pose]={'newAggregatePairs':sorted(set(new)-set(old)),'inheritedAggregatePairs':sorted(set(new)&set(old)),'removedAggregatePairs':sorted(set(old)-set(new)),'baselinePairCount':len(old),'candidatePairCount':len(new)}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'status':'DIAGNOSTIC; inspect introduced and inherited triangle crossings before motion acceptance','inputs':{'base':str(base),'baseSha256':sha(base),'candidate':str(candidate),'candidateSha256':sha(candidate)},'scriptSha256':sha(Path(__file__)),'poses':POSES,'baseline':before,'candidate':after,'delta':deltas,'limits':['Actual triangulated mesh surface crossings at four authored native local-X states, epsilon 0.1 micrometre. AABB only filters candidates; BVH actual triangles decide crossings.','Includes changed plate/shell groups against builder-eligible rigid meshes with different direct owners and against the other changed groups. Excludes same-owner overlaps, curves and authoring guides.','Intentional receiving overlaps, fasteners and inherited joint/support intersections are not certified as clearance. Triangle counts differ with tessellation and are not penetration depth.','Surface test misses containment without triangle crossings, does not sweep between states, and does not model forces, soft tissue, hidden hardware or runtime motion. No full collision PASS is claimed.']}
output.write_text(json.dumps(report,indent=2)+'\n')
print('SHOULDER_TRIANGLE_DELTA',json.dumps(deltas),flush=True)
