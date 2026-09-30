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
  wall=bpy.data.objects[f'V31 fixed temporal receiving wall {side}'];e=wall.evaluated_get(dg);m=e.to_mesh();tree=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);e.to_mesh_clear()
  for course,(a,b,inner,outer) in enumerate(profiles):
   name=f'V38 optic cheek shield {side} {course}';o=bpy.data.objects[name];world=o.matrix_world.copy();inv=world.inverted();before=[v.co.copy() for v in o.data.vertices];assert len(before)==182;verts=[];witness=[]
   for layer in (0,1):
    for i in range(13):
     u=i/12;t=a+(b-a)*u
     for j in range(7):
      v=j/6;r=inner+(outer-inner)*v;# Uneven swept outer return, taper to formed end seats.
      r+=(.006*math.sin(math.pi*u)-.008*u*u)*v;taper=.90-.22*u*u;r=inner+(r-inner)*taper
      y=eye.y+r*math.cos(t);z=eye.z+r*math.sin(t);x=side*(outer0+course*.007+.0015*math.sin(math.pi*v)**2-layer*.0045);p=Vector((x,y,z));verts.append(inv@p)
      if layer==0 and j in (0,6) and i in (0,6,12):hit=tree.find_nearest(p);witness.append({'vertex':i*7+j,'receiver':wall.name,'actualShieldWorld':list(p),'nearestFiniteReceivingPoint':list(hit[0]),'distanceM':hit[3]})
   o.data=o.data.copy()
   for v,p in zip(o.data.vertices,verts):v.co=p
   o.data.update();closed,volume=solid(o);stock=[(world@o.data.vertices[i].co-world@o.data.vertices[i+91].co).length for i in range(91)];assert max(abs(s-.0045) for s in stock)<3e-7;o['v38CheekEnvelope']='Curved orbital receiving course with finite separated underlap, passive head-owned allera'
   records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'constructionClass':o.get('constructionClass'),'materials':[m.name if m else None for m in o.data.materials],'method':'Curved staggered orbital sector follows optic toward actual jaw-root, no straight bands/projection onto raised mounts. Separate finite axial layers retain4.5mm stock with7mm course spacing.','angularIntervalRadians':[a,b],'radialInnerOuterM':[inner,outer],'wholeFixedHeadFrontmostM':front,'firstCourseOuterXAbsM':outer0,'courseSpacingM':.007,'nativeXStockM':.0045,'stockMinMaxM':[min(stock),max(stock)],'changedVertexIndices':[i for i,v in enumerate(o.data.vertices) if v.co!=before[i]],'sameSourceTopology':True,'finiteReceivingWitnesses':witness,'maximumMovementM':max((v.co-before[i]).length for i,v in enumerate(o.data.vertices)),'closedEdgeManifold':closed,'positiveVolumeM3':volume})
 return {'changedMeshes':ALLOWED,'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'attachmentAndEraMap':records,'confirmation':'Actual ownerJuly HEAD ONLY curved orbital cheek/brow framing and open mandible; actualmaster03 checkswholebird.','reconstruction':'Authored sector/radial boundaries/stagger; no perspective dimensions recovered. Independent rigid removable head armor, not anatomical tissue or proven engineered seats.','limits':['All concentric optic faces/rear48, bill/jaw397/hinge/crown/neck/body source exact.','Finite nearest receiving distances disclosed; interlayer gap does not prove mounting/fabrication or continuous clearance.','4.5mm is native-X stock, not minimum wall-normal metrology; strict union36 screen separate.']}
