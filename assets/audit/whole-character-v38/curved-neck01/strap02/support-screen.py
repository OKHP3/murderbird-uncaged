"""Bounded actual root-cap surface and receiving-strap samples; no support PASS implied."""
import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;ROOT=P.parents[4];R=json.loads((P/'receipt.json').read_text());path=ROOT/R['outputs']['native']['path'];bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update()
def surface(o):
 m=o.data;m.calc_loop_triangles();v=[o.matrix_world@x.co for x in m.vertices];f=[tuple(x.vertices)for x in m.loop_triangles];return BVHTree.FromPolygons(v,f,all_triangles=True),v
records=[];allocation=[]
for a in R['contract']['attachmentAndEraMap']:
 if'sourceFrame'not in a:continue
 o=bpy.data.objects[a['name']];source=bpy.data.objects[a['sourceFrame']];bvh,v=surface(o);sb,sv=surface(source);q=[Vector(p)for p in a['actualSourceQuadWorld']];errors=[]
 for i in range(5):
  for j in range(5):
   u=i/4;t=j/4;p=q[0]*(1-u)*(1-t)+q[1]*u*(1-t)+q[2]*u*t+q[3]*(1-u)*t;errors.append({'u':u,'t':t,'rootCapNearestErrorM':bvh.find_nearest(p)[3],'sourceFrameNearestErrorM':sb.find_nearest(p)[3]})
 actualRootCornerError=max((v[i]-q[i]).length for i in range(4));meshes=[bpy.data.objects[n]for n in R['contract']['changedMeshes']if bpy.data.objects[n].parent==o.parent];skins=[(x.name,surface(x)[0])for x in meshes];contacts=[]
 # Actual finite path corners, after the three loft transition sections.
 for idx,p in enumerate(v[16:],16):
  best=min((b.find_nearest(p)[3],name)for name,b in skins);contacts.append({'vertex':idx,'nearestOwnSkin':best[1],'surfaceDistanceM':best[0]})
 records.append({'name':o.name,'owner':o.parent.name,'sourceFrame':source.name,'sourceFace':a['sourceFaceIndex'],'sourceRootCentroidZ':a['sourceRootCentroidZ'],'intendedReceivingLevelZ':a['intendedReceivingLevelZ'],'rootLevelDistanceM':a['rootLevelDistanceM'],'actualRootCornerCoordinateErrorM':actualRootCornerError,'rootFiniteSamples':errors,'receivingPathActualCornerSamples':contacts,'maximumReceivingCornerSurfaceDistanceM':max(c['surfaceDistanceM']for c in contacts),'minimumReceivingCornerSurfaceDistanceM':min(c['surfaceDistanceM']for c in contacts)})
 allocation.append({'support':o.name,'sourceFrame':source.name,'face':a['sourceFaceIndex'],'quadKey':sorted([list(round(c,8)for c in p)for p in q])})
dups=[(a['support'],b['support'])for i,a in enumerate(allocation)for b in allocation[i+1:]if a['quadKey']==b['quadKey']]
output={'status':'Qualified support proposal only: finite root coincidence and nearest receiving corners do not establish complete supported seating','method':'Actual candidate world mesh BVH; source finite quad5x5bilinear grid sampled against both original frame and new support, actual four root corners compared to recorded original face. Receiving path corners after loft sampled against actual changed own-owner skins; distance includes inner/outside strip corners, intentional3mm stock, and uncovered intervals. No containment, contact-area certificate, normal loading, welding or structural strength.','records':records,'duplicateAllocatedSourceQuadCoordinates':dups,'limits':['Source root cap is one finite existing face, not copied multi-seat Boolean union. Receiving corners alone are insufficient to call support continuous.','Strict new/inherited same-owner and moving-owner crossings are recorded independently; intended support role does not exempt actual intersections.','Finite three poses are not pivot swept-sector construction/clearance proof; final follows authored rest C with overlaps and diagonal free edges.']}
(P/'support-screen.json').write_text(json.dumps(output,indent=2)+'\n');print('SUPPORT',[(x['name'],x['rootLevelDistanceM'],max(s['rootCapNearestErrorM']for s in x['rootFiniteSamples']),x['maximumReceivingCornerSurfaceDistanceM'])for x in records])
