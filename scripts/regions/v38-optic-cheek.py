"""Connection-only projection repair: six existing shields, fixed wall only."""
import bpy,bmesh,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ALLOWED=[f'V38 optic cheek shield {s} {i}' for s in (-1,1) for i in range(3)]
def apply():
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();records=[]
 for side in (-1,1):
  wall=bpy.data.objects[f'V31 fixed temporal receiving wall {side}'];e=wall.evaluated_get(dg);m=e.to_mesh();tree=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);e.to_mesh_clear()
  for course in range(3):
   o=bpy.data.objects[f'V38 optic cheek shield {side} {course}'];world=o.matrix_world.copy();assert all(abs(world[0][k])<1e-8 for k in (1,2));old=[v.co.copy() for v in o.data.vertices];pts=[world@v for v in old];count=len(pts)//2;assert count==91;o.data=o.data.copy();seats=[]
   for i,p in enumerate(pts[:count]):
    v=(i%7)/6;hit=tree.ray_cast(Vector((side*.8,p.y,p.z)),Vector((-side,0,0)));assert hit[0] is not None,(o.name,i,p);seat=abs(hit[0].x);x=side*(seat+.0065+.004*math.sin(math.pi*v)**2+course*.006);delta=x-p.x
    for j in (i,i+count):o.data.vertices[j].co.x=old[j].x+delta/world[0][0]
    seats.append({'outerVertex':i,'receiver':wall.name,'finiteWallSurfacePoint':list(hit[0]),'sourceShieldWorldX':p.x,'candidateShieldWorldX':x,'baseStandOffM':.0065,'courseStandOffM':course*.006})
   o.data.update();assert all(v.co.y==old[i].y and v.co.z==old[i].z for i,v in enumerate(o.data.vertices));stock=max(((world@o.data.vertices[i].co-world@o.data.vertices[i+count].co)-(pts[i]-pts[i+count])).length for i in range(count));assert stock<3e-7
   bm=bmesh.new();bm.from_mesh(o.data);closed=all(e.is_manifold for e in bm.edges);volume=abs(bm.calc_volume(signed=True));bm.free();assert closed and volume>0;o['v38OpticCheekSeatFit']='Functional X projection repair to actual fixed temporal wall only; no third artisticattempt'
   records.append({'name':o.name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'constructionClass':o.get('constructionClass'),'materials':[m.name for m in o.data.materials],'changedVertexIndices':[i for i,v in enumerate(o.data.vertices) if v.co!=old[i]],'onlyNativeLocalXChanged':True,'allYZVerticesExact':True,'sameSourceTopology':True,'pairedAxialStockVectorErrorM':stock,'finiteReceivingSamples':seats,'maximumMovementM':max((v.co-old[i]).length for i,v in enumerate(o.data.vertices)),'closedEdgeManifold':closed,'positiveVolumeM3':volume,'method':'Same02 six shields YZ outline/topology/4.5mm pairedstock/courseoffset; X projection nowactual same-side temporal receiving wall only, excludes raised fittings/brow/lens.'})
 return {'changedMeshes':ALLOWED,'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'attachmentAndEraMap':records,'confirmation':'Authorized functional attachment repair of observed all-head-pool projection mistake; original01/02 held visual proposals frozen.','reconstruction':'Existing base stand-off/stock/course stagger retained, not a new likeness shape.','limits':['Ray-standoff records are actual finite source receiver samples, not fitted fasteners/load acceptance.','Minimum wall-normal thickness and continuous sweep not certified; strict samecoverage surface diagnostic separate.','All30 changed02 originalparts including2 optic relief/root48 preserved exactly; only sixshieldX surface seating changes.']}
