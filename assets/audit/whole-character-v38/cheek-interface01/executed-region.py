"""Cheek-interface01: smooth shared lateral field and true multi-triangle lands.
Repair input cheek-supported02,28 passive meshes only; source wall exact.
"""
import bpy,bmesh,math,numpy as np
from mathutils import Vector
BROWS=[f'V33 diagonal brow receiver {s} {i}'for s in(-1,1)for i in range(3)]
SHIELDS=[f'V38 optic cheek shield {s} {i}'for s in(-1,1)for i in range(3)]
LEAVES=[f'V33 swept temporal leaf {s} {i}'for s in(-1,1)for i in range(2)]
ROOTS=[f'V31 temporal fitting root {s} {i}'for s in(-1,1)for i in range(3)]
FITTINGS=[f'V31 passive temporal fitting {s} {i}'for s in(-1,1)for i in range(3)]
NAMES=BROWS+SHIELDS+LEAVES+ROOTS+FITTINGS

def install(name,world,faces,kind,records):
 o=bpy.data.objects[name];mesh=bpy.data.meshes.new(name+' compatible finite interface');inv=o.matrix_world.inverted();mesh.from_pydata([inv@p for p in world],[],faces);mesh.update()
 for mat in o.data.materials:mesh.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 volume=bm.calc_volume(signed=True);assert volume>0;bm.to_mesh(mesh);bm.free();o.data=mesh
 for f in mesh.polygons:f.use_smooth=True
 o['v38CheekInterface']='Passive smooth finite surface/receiving interface repair proposal'
 records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'kind':kind,'closedEdges':True,'positiveVolumeM3':volume,'materials':[m.name if m else None for m in mesh.materials]})

def apply():
 bpy.context.view_layer.update();records=[];lands=[];fields=[]
 # Low order continuous lateral support field fitted only to actual outer
 # skull backing, not changing a projection target at an optic/cap edge.
 def basis(y,z):
  a=(y+.42)/.20;b=(z-1.75)/.16;return [1,a,b,a*a,a*b,b*b,a*a*a,a*a*b,a*b*b,b*b*b]
 for side in(-1,1):
  wall=bpy.data.objects[f'V31 fixed temporal receiving wall {side}'];wall.data.calc_loop_triangles();wp=[wall.matrix_world@v.co for v in wall.data.vertices];points=[]
  for t in wall.data.loop_triangles:
   p=[wp[i]for i in t.vertices];n=(p[1]-p[0]).cross(p[2]-p[0]).normalized();q=sum(p,Vector())/3
   if n.x*side>.40 and 1.60<q.z<1.885 and -.59<q.y<-.22:points.append(q)
  coeff=np.linalg.lstsq(np.array([basis(q.y,q.z)for q in points]),np.array([abs(q.x)for q in points]),rcond=None)[0]
  field=lambda y,z:float(np.dot(coeff,basis(y,z)))
  errs=[abs(field(q.y,q.z)-abs(q.x))for q in points];fields.append({'side':side,'actualBackingFaceSamples':len(points),'continuousCubicLateralCoefficients':list(coeff),'sampleResidualMinMaxM':[min(errs),max(errs)],'basisNative':'a=(Y+.42)/.20,b=(Z−1.75)/.16; [1,a,b,a²,ab,b²,a³,a²b,ab²,b³]','limits':'Smooth reconstructed exterior field fitted to finite receiver; residual/gap is measurement, not actual attachment proof.'})
  plate_names=[f'V33 diagonal brow receiver {side} {i}'for i in range(3)]+[f'V38 optic cheek shield {side} {i}'for i in range(3)]+[f'V33 swept temporal leaf {side} {i}'for i in range(2)]
  ranks=[0,1,0,0,1,0,0,1]
  for name,rank in zip(plate_names,ranks):
   o=bpy.data.objects[name];old=[o.matrix_world@v.co for v in o.data.vertices];half=len(old)//2;stock=.0045;outer=[]
   for p in old[:half]:
    x=field(p.y,p.z)+.009+rank*.006;assert .07<x<.21,(name,x);outer.append(Vector((side*x,p.y,p.z)))
   world=outer+[p-Vector((side*stock,0,0))for p in outer];install(name,world,[tuple(f.vertices)for f in o.data.polygons],'Retained smooth YZ contour, one continuous shared lateral field; controlled6mm overlap ordering and4.5mm axial stock',records)
  for i,(target,yy,zz)in enumerate([(f'V38 optic cheek shield {side} 1',-.358,1.735),(f'V38 optic cheek shield {side} 2',-.338,1.682),(f'V33 swept temporal leaf {side} 1',-.254,1.614)]):
   o=bpy.data.objects[target];o.data.calc_loop_triangles();pts=[o.matrix_world@v.co for v in o.data.vertices];half=len(pts)//2;nu,nv=40,10;stride=11
   center=min(range(half),key=lambda k:(pts[k].y-yy)**2+(pts[k].z-zz)**2);rr,cc=divmod(center,stride);rr=max(3,min(nu-3,rr));cc=max(3,min(nv-3,cc));r0,r1=rr-3,rr+3;c0,c1=cc-3,cc+3
   ids={row*stride+col for row in range(r0,r1+1)for col in range(c0,c1+1)};actual=[tuple(t.vertices)for t in o.data.loop_triangles if set(t.vertices)<=ids];assert len(actual)==72,(target,len(actual))
   used=sorted(ids);mapping={k:j for j,k in enumerate(used)};base=[pts[k]for k in used];front=[tuple(mapping[k]for k in t)for t in actual];count=len(base);plane=max(abs(p.x)for p in base)+.004;verts=base+[Vector((side*plane,p.y,p.z))for p in base];faces=[tuple(reversed(t))for t in front]+[tuple(count+k for k in t)for t in front]
   from collections import Counter
   ec=Counter(tuple(sorted((t[j],t[(j+1)%3])))for t in front for j in range(3));boundary=[]
   for t in front:
    for j in range(3):
     a,b=t[j],t[(j+1)%3]
     if ec[tuple(sorted((a,b)))]==1:faces.append((a,b,b+count,a+count));boundary.append((a,b))
   root=f'V31 temporal fitting root {side} {i}';install(root,verts,faces,'Actual72 receiver triangles as complete finite return innerland,4mm minimum to planar outer mounting land',records)
   # Reconstruct round passive fitting with an exact planar annular foot,
   # rather than assuming the old deformed cylinder had one flat base.
   cy,cz=pts[rr*stride+cc].y,pts[rr*stride+cc].z;radius=.0055;inner=.0022;n=48;profile=[(plane,radius),(plane+.001,radius),(plane+.004,.0050),(plane+.004,inner),(plane,inner)]
   fv=[Vector((side*x,cy+rad*math.cos(2*math.pi*j/n),cz+rad*math.sin(2*math.pi*j/n)))for x,rad in profile for j in range(n)];ff=[]
   for row in range(len(profile)):
    nextrow=(row+1)%len(profile)
    for j in range(n):k=(j+1)%n;ff.append((row*n+j,row*n+k,nextrow*n+k,nextrow*n+j))
   fit=f'V31 passive temporal fitting {side} {i}';install(fit,fv,ff,'Finite11mm round passive fitting with complete planar annular base matching actual return outer field',records)
   lands.append({'root':root,'fitting':fit,'receiver':target,'receiverActualOuterTriangleIndices':[list(t)for t in actual],'rootInnerTriangles':len(actual),'receiverGridRows':[r0,r1],'receiverGridColumns':[c0,c1],'actualFullPatchYZExtentsM':[max(p.y for p in base)-min(p.y for p in base),max(p.z for p in base)-min(p.z for p in base)],'actualInnerTriangleCoordinates':[list(map(list,[pts[k]for k in actual[0]]))],'fittingFootDiameterM':radius*2,'returnOuterNativeSignedX':side*plane,'minimumAxialReturnDepthM':.004,'method':'Actual entire receiving72triangle patch retained as innerland, shared triangulation—not polygon through perimeter hits. Planar outerland and full annular fittingbase constructed in same plane; finite underside containment independently checked.','limits':'Coincident full receiving triangles are intended contact; strict actualinterobject screen not waived; geometry is kinematic proposal, not manufacture/load certification.'})
 return {'changedMeshes':NAMES,'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'attachmentAndEraMap':records,'actualFootlands':lands,'pairedFittingSeats':lands,'continuousLateralFields':fields,'construction':'Retain every plate YZoutline/head silhouette, replace discontinuous lateral projection with shared continuous field and shallow finite depth order. Full72triangle roots and matching planar11mm annular fittingbases. Source walls and trueinterfaces exact.','rigidVsFlexible':'All28 existing meshes rigidhead-owned passiveMaker/Mechanic/Builder, no powered additions.','confirmation':'ActualJuly HEADONLY +Master03/Makerclean; repair sourcecheeksupported02 noadoption.','reconstruction':'Exact smooth lateral field/overlap order/mount interfaces proposal.','protected':'Sourcewalls plus improvedbill/jaw283socket/optic/cranial andbody unchanged.','limits':['Full30 watchscope unchanged; residualintroduced contacts get explicitHOLD, not lowercount acceptance.','Field fits backing but is not itself a conforming full backing attachment; actual mountinterfaces separately constructed andchecked.']}
