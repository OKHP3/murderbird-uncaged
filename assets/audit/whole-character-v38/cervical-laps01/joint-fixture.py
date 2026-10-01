import bpy,math,json,hashlib,bmesh
from pathlib import Path
from mathutils import Vector,Matrix
P=Path(__file__).resolve().parent
SRC=P.parents[3]/'assets/models/whole-character-v38/neck-envelope01/murderbird-v38-neck-envelope01.blend'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()=='081337aa8e7c12f657f5f18dcdf27462491bf89d52b344fcbae52702770022a0'
bpy.ops.wm.open_mainfile(filepath=str(SRC));bpy.context.view_layer.update()
c=bpy.data.objects['cervical-mid-b'].matrix_world.translation.copy()
# True X-axis surface of revolution: R depends ONLY on axial coordinate x.
# Fixture slimmer contour proposal, not reference dimensions. Parent underlap/child root separated stock.
def radius(x):return .173*math.sqrt(1-(x/.166)**2)
def stock(outer,lo,hi):
 v=[];nx=17;na=33
 for layer in(0,1):
  for i in range(nx):
   x=-.07+.14*i/(nx-1);r=radius(x)+outer-.0035*layer
   for j in range(na):
    a=lo+(hi-lo)*j/(na-1);v.append(c+Vector((x,-r*math.cos(a),r*math.sin(a))))
 n=nx*na;f=[]
 for i in range(nx-1):
  for j in range(na-1):k=i*na+j;f.append((k,k+1,k+na+1,k+na))
 f+=[tuple(k+n for k in reversed(q))for q in f.copy()]
 bd=list(range(na))+[i*na+na-1 for i in range(1,nx)]+[(nx-1)*na+j for j in range(na-2,-1,-1)]+[i*na for i in range(nx-2,0,-1)]
 for i,a in enumerate(bd):b=bd[(i+1)%len(bd)];f.append((a,b,b+n,a+n))
 m=bpy.data.meshes.new('fixture');m.from_pydata(v,[],f);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));vol=abs(bm.calc_volume());nm=sum(not e.is_manifold for e in bm.edges);bm.free();m.calc_loop_triangles()
 return v,[tuple(t.vertices)for t in m.loop_triangles],{'vertices':len(v),'nonManifoldEdges':nm,'volumeM3':vol}
a,af,ar=stock(-.007,-.19,.12);b,bf,br=stock(0,-.12,.16)
code=(P.parents[0]/'neck-envelope01/finite-screen.py').read_text().split('def load(')[0]
code=code[code.index('def inside('):];exec(code)
from mathutils.bvhtree import BVHTree
ra=BVHTree.FromPolygons(a,af,all_triangles=True);rows=[]
for pitch in(-.034764171855032014,0,.10675220489501955,.1625):
 rot=Matrix.Rotation(pitch,3,'X');bv=[c+rot@(p-c)for p in b];rb=BVHTree.FromPolygons(bv,bf,all_triangles=True);cross=0
 for ia,ib in ra.overlap(rb):
  ta=[a[i]for i in af[ia]];tb=[bv[i]for i in bf[ib]]
  if any(edge(ta[k],ta[(k+1)%3],tb)or edge(tb[k],tb[(k+1)%3],ta)for k in range(3)):cross+=1
 overlap=min(.12,.16-pitch)-max(-.19,-.12-pitch)
 rows.append({'relativePitchRad':pitch,'strictCrossingTrianglePairs':cross,'commonAngularCoverageRad':max(0,overlap),'minimumAnalyticRadialStockSeparationM':.0035})
frames=[]
for side in(-1,1):
 o=bpy.data.objects[f'V23 cervical 3 distal race {side}'];face=o.data.polygons[60 if side<0 else 61];frames.append({'name':o.name,'face':face.index,'quadNative':[list(o.matrix_world@o.data.vertices[i].co)for i in face.vertices]})
(P/'joint-fixture.json').write_text(json.dumps({'sourceNativeSHA256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'joint':'cervical-mid-b','actualCentreNative':list(c),'parentOwner':'cervical-mid-a','childOwner':'cervical-mid-b','sourceOwnFiniteRootFaces':frames,'parentUnderlap':ar,'childReceiver':br,'samples':rows,'construction':'Direct monotonic axial-X/circular-angle topology; no sector blending, axis clamp or normal flips to rescue self-intersection. Separate radial mating layers.','limits':['Narrow anterior 140mm axial fixture only, not whole skin/support seating or whole-character silhouette proof.','Both parts revolve around exact shared local-X bearing. Analytic radius function independent of angle establishes layer invariance under ideal relative pitch; discrete finite checks remain sampled.','173mm centre radius is slimmer authored proposal, not reference measurement. Other joints and head-counterrotation NOT certified.','Selected unchanged bearing face is a future anchor, not an attached or seated carrier in this fixture.']},indent=2)+'\n');print('FIXTURE',json.dumps(rows),flush=True)
