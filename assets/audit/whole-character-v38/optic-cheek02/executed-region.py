"""Actual recessed optic + formed cheek envelope, bounded proposal02."""
import bpy,bmesh,math,runpy
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
PAIRS=runpy.run_path(str(ROOT/'assets/audit/whole-character-v38/bill-identity01/executed-region.py'))['finite_pairs']
ALLOWED=[f'V31 Advanced optical aperture {s}' for s in (-1,1)]+[f'V31 fixed temporal receiving wall {s}' for s in (-1,1)]+[f'V31 optic recessed receiving cup {s}' for s in (-1,1)]+[f'V33 recessed optic retaining lip {s}' for s in (-1,1)]+[f'V33 diagonal brow receiver {s} {i}' for s in (-1,1) for i in range(3)]+[f'V33 formed lower cheek receiver {s} {i}' for s in (-1,1) for i in range(2)]+[f'V31 passive temporal fitting {s} {i}' for s in (-1,1) for i in range(3)]+[f'V31 temporal fitting root {s} {i}' for s in (-1,1) for i in range(3)]
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def solid(o):
 bm=bmesh.new();bm.from_mesh(o.data);closed=all(e.is_manifold for e in bm.edges);volume=abs(bm.calc_volume(signed=True));bm.free();assert closed and volume>0,o.name;return closed,volume
def apply():
 bpy.context.view_layer.update();eye=Vector((0,-.577800006,1.725484014));records=[];added=[];head=bpy.data.objects['head'];jaw=bpy.data.objects['jaw'].matrix_world.translation.copy()
 for name in ALLOWED:
  o=bpy.data.objects[name];world=o.matrix_world.copy();inv=world.inverted();pts=[world@v.co for v in o.data.vertices];old=[v.co.copy() for v in o.data.vertices];moves={};pairs=[];fixed=set();side=-1 if '-1' in name else 1
  if 'Advanced optical aperture' in name:
   # Preserve actual back-seat48 source vertices; concentric finite front relief.
   verts=old[:48];cy=eye.y;cz=eye.z;profiles=[(.03828,.138040006),(.0355,.142),(.032,.142),(.029,.1355),(.024,.1353),(.018,.1380),(.010,.1388)];faces=[]
   for radius,x in profiles:
    for k in range(48):angle=math.tau*k/48;verts.append(inv@Vector((side*x,cy+radius*math.cos(angle),cz+radius*math.sin(angle))))
   for row in range(len(profiles)):
    for k in range(48):a=row*48+k;b=row*48+(k+1)%48;faces.append((a,b,b+48,a+48))
   faces.extend([tuple(range(47,-1,-1)),tuple(range(len(verts)-48,len(verts)))])
   mesh=bpy.data.meshes.new(name+' concentric finite relief');mesh.from_pydata(verts,[],faces);mesh.update()
   for mat in o.data.materials:mesh.materials.append(mat)
   o.data=mesh;bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();assert all(o.data.vertices[i].co==old[i] for i in range(48));closed,volume=solid(o);o['v38OpticCheek']='Existing Builder-only optical aperture, concentric finite relief; source48-root exact'
   records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'constructionClass':o.get('constructionClass'),'materials':[m.name for m in mesh.materials],'method':'Concentric relieved front annuli and recessed finite optical center; unchanged48 actual rear attachment vertices/owner/transform. No new earlier-era powered optic.','retainedActualSeatVertexIndices':list(range(48)),'sourceSeatVerticesLocal':[list(p) for p in old[:48]],'candidateSeatVerticesLocal':[list(v.co) for v in mesh.vertices[:48]],'authoredFrontRadialProfileM':profiles,'closedEdgeManifold':closed,'positiveVolumeM3':volume});continue
  elif 'passive temporal fitting ' in name:
   center=sum(pts,Vector())/len(pts)
   for i,p in enumerate(pts):moves[i]=Vector((-side*.009,-(p.y-center.y)*.54,-(p.z-center.z)*.54))
   method='Same passive mount center,46% radial size and9mm inset; no true jaw articulation changed.'
  elif 'temporal fitting root' in name:
   lo=min(abs(p.x) for p in pts);hi=max(abs(p.x) for p in pts)
   for i,p in enumerate(pts):w=(abs(p.x)-lo)/(hi-lo);moves[i]=Vector((-side*.009*w,0,0));fixed.add(i) if w<1e-5 else None
   method='Exact source return-side root footprint; receiving end follows smaller inset superficial mount.'
  elif 'optic recessed receiving cup' in name:
   lo=min(abs(p.x) for p in pts);hi=max(abs(p.x) for p in pts)
   for i,p in enumerate(pts):w=ease((abs(p.x)-lo)/(hi-lo));moves[i]=Vector((-side*.013*w,0,0));fixed.add(i) if w==0 else None
   method='Original lens/floor geometry and cup back-seat exact; cup outer receiving contour recessed13mm. Finite profile reconstructed, no wall-metrology claim.'
  elif 'optic retaining lip' in name:
   moves={i:Vector((-side*.013,0,0)) for i in range(len(pts))};method='Rigid13mm inward seating of finite retaining lip, source thickness and radial aperture exact.'
  elif 'diagonal brow' in name:
   count=len(pts)//2;assert count==363
   for i,p in enumerate(pts[:count]):u=(i//11)/32;v=(i%11)/10;rad=Vector((0,p.y-eye.y,p.z-eye.z));rad.normalize();d=Vector((side*.010*math.sin(math.pi*v)**2*math.sin(math.pi*u)**2,0,0))-rad*.009*(1-v)**2;moves[i]=moves[i+count]=d;pairs.append((i,i+count));fixed.update((i,i+count)) if v==1 else None
   method='Actual finite brow land formed8mm over original receiving boundaries; outer lap boundaries exact, inner receiving lands shelter passive circular rim, opposing stock vectors paired.'
  else:
   for i,p in enumerate(pts):
    radius=math.hypot(p.y-eye.y,p.z-eye.z);jr=math.hypot(p.y-jaw.y,p.z-jaw.z)
    if 'fixed temporal' in name:
     w=ease((radius-.09)/.05)*ease((p.z-1.64)/.055)*ease((1.88-p.z)/.05)*ease((p.y+.48)/.045)*ease((-.19-p.y)/.045)
     # finite receiving planes have a diagonal valley and an intentional return
     line=(p.z-1.73)+.45*(p.y+.40);crease=max(0,1-abs(line)/.065);moves[i]=Vector((-side*(.009+.010*crease)*w,0,0))
     if w==0:fixed.add(i)
    else:
     w=ease((radius-.065)/.025)*ease((jr-.050)/.025)*ease((1.74-p.z)/.05);moves[i]=Vector((side*.006*w,0,.004*w));rad=Vector((0,p.y-eye.y,p.z-eye.z));rad.normalize();inner=ease((.082-radius)/.018)*ease((jr-.050)/.025);moves[i]-=rad*.008*inner
     if jr<=.05:fixed.add(i)
   pairs=PAIRS(o,pts,world)
   for i,j in pairs:d=Vector() if i in fixed or j in fixed else (moves[i]+moves[j])*.5;moves[i]=moves[j]=d
   method='Broad temporal wall forms a diagonal receiving valley9–19mm inward, source bore/upper/lower envelope exact.' if 'fixed temporal' in name else 'Finite cheek land raised6mm/4mm upward away from protected optic lip and actual jaw-journal bore.'
  o.data=o.data.copy()
  for i,p in enumerate(pts):
   if moves[i].length:o.data.vertices[i].co=inv@(p+moves[i])
  o.data.update();assert all(o.data.vertices[i].co==old[i] for i in fixed);after=[world@v.co for v in o.data.vertices];error=max(((after[i]-after[j])-(pts[i]-pts[j])).length for i,j in pairs) if pairs else None
  if pairs:assert error<3e-7
  closed,volume=solid(o);o['v38OpticCheek']='Passive constructed recessed optic/cheek02; no new sensing in earlier eras'
  records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'constructionClass':o.get('constructionClass'),'materials':[m.name if m else None for m in o.data.materials],'method':method,'changedVertexIndices':[i for i,p in enumerate(old) if o.data.vertices[i].co!=p],'protectedVertexIndices':sorted(fixed),'maximumMovementM':max(d.length for d in moves.values()),'recoveredFiniteStockPairs':pairs,'maximumStockVectorErrorM':error,'closedEdgeManifold':closed,'positiveVolumeM3':volume})
 # Three short diagonal courses receive the broad fixed temple into the orbital flow.
 # Each independently removable plate is rigid to head; none touches cranial-cover owner.
 template=bpy.data.objects['V33 diagonal brow receiver 1 0'];dg=bpy.context.evaluated_depsgraph_get();poolv=[];poolf=[]
 for part in bpy.data.objects:
  if part.type!='MESH' or not part.parent or part.parent.name!='head':continue
  ev=part.evaluated_get(dg);mesh=ev.to_mesh();offset=len(poolv);poolv.extend(ev.matrix_world@v.co for v in mesh.vertices);poolf.extend(tuple(offset+i for i in face.vertices) for face in mesh.polygons);ev.to_mesh_clear()
 receiving=BVHTree.FromPolygons(poolv,poolf)

 for side in (-1,1):
  for course in range(3):
   name=f'V38 optic cheek shield {side} {course}';center_y=-.475+course*.032;center_z=1.797-course*.035;verts=[];faces=[];nu=12;nv=6
   for layer in (0,1):
    for i in range(nu+1):
     u=i/nu
     for j in range(nv+1):
      v=j/nv;length=[.115,.125,.105][course];width=[.044,.040,.034][course];sweep=u*u*(3-2*u);taper=1-.64*sweep;y=center_y+(u-.5)*length+(v-.5)*.018*taper;z=center_z-(u-.5)*(.045+.008*course)+.012*math.sin(math.pi*u)+(v-.5)*width*taper
      hit=receiving.ray_cast(Vector((side*.8,y,z)),Vector((-side,0,0)));seat=abs(hit[0].x) if hit[0] else .145;x=seat+.0065+.004*math.sin(math.pi*v)**2+course*.006-layer*.0045;verts.append(Vector((side*x,y,z)))
   count=(nu+1)*(nv+1);stride=nv+1
   for i in range(nu):
    for j in range(nv):a=i*stride+j;b=a+stride;faces.extend([(a,a+1,b+1,b),(count+b,count+b+1,count+a+1,count+a)])
   boundary=list(range(stride))+[i*stride+nv for i in range(1,nu+1)]+[nu*stride+j for j in range(nv-1,-1,-1)]+[i*stride for i in range(nu-1,0,-1)]
   for i,a in enumerate(boundary):b=boundary[(i+1)%len(boundary)];faces.append((a,b,count+b,count+a))
   mesh=bpy.data.meshes.new(name+' finite mesh');o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.parent=head;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Identity(4);bpy.context.view_layer.update();inv=o.matrix_world.inverted();mesh.from_pydata([inv@p for p in verts],[],faces);mesh.update()
   for m in template.data.materials:mesh.materials.append(m)
   for k,v in template.items():o[k]=v
   o['v38OpticCheek']='Independently removable passive temple receiving course';o['constructionOwner']='head';o['constructionClass']='inherited-passive';o['exteriorEras']='maker,mechanic,builder';o['surfaceRole']='receiving-plate'
   bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();closed,volume=solid(o);added.append(name);records.append({'name':name,'owner':'head','eras':'maker,mechanic,builder','constructionClass':'inherited-passive','materials':[m.name for m in mesh.materials],'method':'Finite4.5mm curved tapered temple receiving course; actual finite head-pool directional ray seat +6.5mm base stand-off,6mm stagger between courses, independently head-owned/removable; proposed seating not engineering fit.','closedEdgeManifold':closed,'positiveVolumeM3':volume,'nominalStockM':.0045})
 bpy.context.view_layer.update()
 return {'changedMeshes':ALLOWED,'addedMeshes':added,'removedMeshes':[],'changedNodes':[],'attachmentAndEraMap':records,'actualEyeCenterNativeYZ':[eye.y,eye.z],'confirmation':'July HEAD ONLY controls recessed optic/brow/cheek flow; actual master03 checks wholebird.','reconstruction':'Authored finite receiving contours/course count and small superficial mounts; no perspective metrology or hidden mechanism claim.','limits':['Actual Advanced lens surfaces/owner/gating unchanged; all altered/additional housing passive allera.','Same-owner seating, cup/lens aperture and cranial inspection samples checked separately, no universal or engineering clearance.']}
