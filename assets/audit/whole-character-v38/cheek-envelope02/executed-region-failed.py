"""Finite independent curved cheek receiving courses; no optic/bill/jaw edits."""
import bpy,bmesh,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'assets/models/whole-character-v38/bill-identity01-socket-fit01/murderbird-v38-bill-identity01-socket-fit01.blend'
CHEEKS=[f'V33 formed lower cheek receiver {s} {i}' for s in (-1,1) for i in range(2)]
SHIELDS=[f'V38 optic cheek shield {s} {i}' for s in (-1,1) for i in range(3)]
ALLOWED=CHEEKS+SHIELDS
def solid(o):
 bm=bmesh.new();bm.from_mesh(o.data);closed=all(e.is_manifold for e in bm.edges);volume=abs(bm.calc_volume(signed=True));bm.free();assert closed and volume>0,o.name;return closed,volume
def apply():
 actual_input=bpy.data.filepath;assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='073bdc678ea2911392b084981b1d2eaa42ce44e53e262b42b4ff14d4b266d665';bpy.ops.wm.open_mainfile(filepath=str(SOURCE));reference={n:[v.co.copy() for v in bpy.data.objects[n].data.vertices] for n in CHEEKS};bpy.ops.wm.open_mainfile(filepath=actual_input);bpy.context.view_layer.update();records=[]
 for name in CHEEKS:
  o=bpy.data.objects[name];before=[v.co.copy() for v in o.data.vertices];assert len(before)==len(reference[name]);o.data=o.data.copy()
  for i,p in enumerate(reference[name]):o.data.vertices[i].co=p
  o.data.update();closed,volume=solid(o);o['v38CheekEnvelope']='Source finite receiving/journal contour restored; avoids contracted optic lip intrusion'
  records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'constructionClass':o.get('constructionClass'),'materials':[m.name if m else None for m in o.data.materials],'method':'Exact selected bill/socket baseline finite cheek contour/axle receiving bore restored, never the rejected head02 recipe.','changedVertexIndices':[i for i,v in enumerate(o.data.vertices) if v.co!=before[i]],'restoredSourceSignature':hashlib.sha256(json.dumps([list(p) for p in reference[name]]).encode()).hexdigest(),'maximumMovementM':max((v.co-before[i]).length for i,v in enumerate(o.data.vertices)),'closedEdgeManifold':closed,'positiveVolumeM3':volume})
 dg=bpy.context.evaluated_depsgraph_get();fixed=[o for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name=='head' and o.name not in SHIELDS];front=max(abs((o.matrix_world@v.co).x) for o in fixed for v in o.data.vertices);outer0=front+.007;eye=Vector((0,-.577800006,1.725484014));profiles=[(.02,1.15,.074,.112),(-.70,.09,.076,.116),(-1.50,-.63,.074,.109)]
 for side in (-1,1):
  wall=bpy.data.objects[f'V31 fixed temporal receiving wall {side}'];e=wall.evaluated_get(dg);m=e.to_mesh();tree=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);e.to_mesh_clear();targets={}
  for name in [wall.name,f'V33 diagonal brow receiver {side} 0',f'V33 diagonal brow receiver {side} 1',f'V33 formed lower cheek receiver {side} 0',f'V33 formed lower cheek receiver {side} 1']:
   target=bpy.data.objects[name];ev=target.evaluated_get(dg);mesh=ev.to_mesh();targets[name]=BVHTree.FromPolygons([ev.matrix_world@v.co for v in mesh.vertices],[tuple(p.vertices) for p in mesh.polygons]);ev.to_mesh_clear()
  for course,(a,b,inner,outer) in enumerate(profiles):
   name=f'V38 optic cheek shield {side} {course}';o=bpy.data.objects[name];world=o.matrix_world.copy();inv=world.inverted();before=[v.co.copy() for v in o.data.vertices];assert len(before)==182;verts=[];witness=[]
   # Two short temple receivers taper rearwards; a third returns forward/down to bill root.
   def point(u,v,layer):
    widths=[.038,.032,.033];width=widths[course]*(1-.60*u*u);offset=(v-.5)*width
    if course==0:y=-.510+.154*u;z=1.794+.011*math.sin(math.pi*u)-.008*u+offset
    elif course==1:y=-.515+.112*u;z=1.714-.030*u+.009*math.sin(math.pi*u)+offset
    else:y=-.515-.117*u;z=1.668+.035*u-.012*math.sin(math.pi*u)+offset
    chosen=[]
    for name,target in targets.items():
     if course==2 and 'lower cheek' not in name:continue
     if course==0 and 'lower cheek' in name:continue
     hit=target.ray_cast(Vector((side*.8,y,z)),Vector((-side,0,0)))
     if hit[0] is not None:chosen.append((abs(hit[0].x),name,hit))
    assert chosen,(o.name,u,v,y,z);seat,name,hit=max(chosen,key=lambda q:q[0]);end=max(0,1-min(u,1-u)/.19);end=end*end*(3-2*end);free=outer0+course*.007+.0015*math.sin(math.pi*v)**2;x=free*(1-end)+(seat+.006)*end-layer*.0045;p=Vector((side*x,y,z))
    if layer==0 and u in (0,.5,1) and v in (0,.5,1):
     nearest=targets[name].find_nearest(p);witness.append({'u':u,'v':v,'receiver':name,'actualShieldWorld':list(p),'rayReceivingPoint':list(hit[0]),'receiverNormal':list(hit[1]),'nearestFiniteReceivingPoint':list(nearest[0]),'nearestSurfaceNormal':list(nearest[1]),'distanceM':nearest[3],'axialOuterSeatGapM':abs(x)-seat,'axialInnerStockSeatGapM':abs(x)-seat-.0045,'method':'Specific finite wall/brow receiving surfaces, lower cheek only for forward return; no fittings/arbitrarypool. Ends are connected finite return lands.'})
    return inv@p
   for layer in (0,1):
    for i in range(13):
     for j in range(7):verts.append(point(i/12,j/6,layer))
   o.data=o.data.copy()
   for v,p in zip(o.data.vertices,verts):v.co=p
   o.data.update();bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();closed,volume=solid(o);stock=[(world@o.data.vertices[i].co-world@o.data.vertices[i+91].co).length for i in range(91)];assert max(abs(s-.0045) for s in stock)<3e-7;o['v38CheekEnvelope']='Asymmetric curved temple/bill-root receiving course with connected finite end lands, passive head-owned allera'
   records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'constructionClass':o.get('constructionClass'),'materials':[m.name if m else None for m in o.data.materials],'method':'Asymmetric curved tapered temple courses plus forward/down bill-root return; connected end lands at declared finite brow/wall/cheek receiving surface+6mm outer gap,1.5mm inner axialgap.4.5mm pairedstock retained; free central courses7mm stagger. No arbitrary mount projection.','angularIntervalRadians':[a,b],'radialInnerOuterM':[inner,outer],'wholeFixedHeadFrontmostM':front,'firstCourseOuterXAbsM':outer0,'courseSpacingM':.007,'nativeXStockM':.0045,'stockMinMaxM':[min(stock),max(stock)],'changedVertexIndices':[i for i,v in enumerate(o.data.vertices) if v.co!=before[i]],'sameSourceTopology':True,'finiteReceivingWitnesses':witness,'maximumMovementM':max((v.co-before[i]).length for i,v in enumerate(o.data.vertices)),'closedEdgeManifold':closed,'positiveVolumeM3':volume})
 return {'changedMeshes':ALLOWED,'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'attachmentAndEraMap':records,'confirmation':'Actual ownerJuly HEAD ONLY curved orbital cheek/brow framing and open mandible; actualmaster03 checkswholebird.','reconstruction':'Authored sector/radial boundaries/stagger; no perspective dimensions recovered. Independent rigid removable head armor, not anatomical tissue or proven engineered seats.','limits':['All concentric optic faces/rear48, bill/jaw397/hinge/crown/neck/body source exact.','Finite nearest receiving distances disclosed; interlayer gap does not prove mounting/fabrication or continuous clearance.','4.5mm is native-X stock, not minimum wall-normal metrology; strict union36 screen separate.']}
