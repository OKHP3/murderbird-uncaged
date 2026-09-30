"""Eight-piece bill identity01: actual inherited head01, never replay rejected02."""
import bpy,bmesh,math
from mathutils import Vector
from mathutils.kdtree import KDTree
ALLOWED=[f'V32 returned upper bill course {i}' for i in range(3)]+[f'V33 formed lower cheek receiver {s} {i}' for s in (-1,1) for i in range(2)]+['V32 formed mandibular bowl']
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def contact():
 dg=bpy.context.evaluated_depsgraph_get();pts=[]
 for o in bpy.data.objects:
  if o.type=='MESH' and o.parent and o.parent.name=='upper-bill':
   e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();pts.extend((o.name,e.matrix_world@m.vertices[i].co) for t in m.loop_triangles for i in t.vertices);e.to_mesh_clear()
 leading=min(pts,key=lambda r:r[1].y);return {'triangleVertexExtremaNativeXYZ':{'min':[min(p[k] for _,p in pts) for k in range(3)],'max':[max(p[k] for _,p in pts) for k in range(3)]},'leadingObject':leading[0],'leadingPointNativeXYZ':list(leading[1]),'method':'Actual evaluated upper-bill triangle vertices, no fixed contact landmark'}
def finite_pairs(o,pts,world):
 normal=world.to_3x3().inverted().transposed();normals=[(normal@v.normal).normalized() for v in o.data.vertices];tree=KDTree(len(pts))
 for i,p in enumerate(pts):tree.insert(p,i)
 tree.balance();candidates=[]
 for i,p in enumerate(pts):
  for q,j,d in tree.find_range(p,.010):
   if j>i and d>.0015 and normals[i].dot(normals[j])<-.25:candidates.append((d,i,j))
 used=set();pairs=[]
 for _,i,j in sorted(candidates):
  if i not in used and j not in used:used.update((i,j));pairs.append((i,j))
 return pairs
def apply():
 bpy.context.view_layer.update();before=contact();records=[];eye=Vector((0,-.578800007,1.725484034));jaw=bpy.data.objects['jaw'].matrix_world.translation.copy()
 for name in ALLOWED:
  o=bpy.data.objects[name];world=o.matrix_world.copy();inv=world.inverted();original=[v.co.copy() for v in o.data.vertices];pts=[world@p for p in original];moves={};fixed=set();pairs=[]
  if name.startswith('V32 returned upper bill'):
   course=int(name[-1]);count=len(pts)//2 if course<2 else len(pts);assert count%10==0;rings=count//10
   for row in range(rings):
    q=(course+row/(rings-1))/3;weight=math.sin(math.pi*q)**2
    for k in range(10):
     i=row*10+k;p=pts[i];relief={3:.2,4:.7,5:1,6:.7,7:.2}.get(k,0)
     d=Vector((-p.x*.28*weight,-.022*weight-.040*weight*relief,-.065*ease((q-.33)/.67)))
     if course==0 and row==0:fixed.add(i);d=Vector()
     moves[i]=d
     if course<2:moves[i+count]=d;pairs.append((i,i+count))
     if course==0 and row==0 and course<2:fixed.add(i+count)
   method='Narrowed finite hard bill side lands, forward cutting return exposes mouth cavity; swept hook down65mm with original root section exact.'
  else:
   for i,p in enumerate(pts):
    if name=='V32 formed mandibular bowl':
     w=ease((-.535-p.y)/.195);moves[i]=Vector((-p.x*.85*w,.035*w,-.025*w+.027*ease((-.665-p.y)/.066)))
     if p.y>=-.535:fixed.add(i)
    else:
     r=math.hypot(p.y-eye.y,p.z-eye.z);jr=math.hypot(p.y-jaw.y,p.z-jaw.z);w=ease((r-.075)/.035)*ease((eye.z-p.z-.030)/.05)*ease((jr-.035)/.035);moves[i]=Vector((-(1 if p.x>0 else -1)*.003*w,.010*w,.012*w))
     if r<=.075 or jr<=.035:fixed.add(i)
   pairs=finite_pairs(o,pts,world)
   for i,j in pairs:
    d=Vector() if i in fixed or j in fixed else (moves[i]+moves[j])*.5;moves[i]=moves[j]=d
   method='Distal rigid mandible shortened35mm, tapered85%, restrained25mm downsweep with27mm distal upturn, root/socket/journal neighborhood exact.' if name=='V32 formed mandibular bowl' else 'Fixed cheek opening return raised/receded gently; exact optic-seat75mm and jaw-journal35mm protected neighborhoods.'
  o.data=o.data.copy()
  for i,p in enumerate(pts):
   if moves[i].length:o.data.vertices[i].co=inv@(p+moves[i])
  o.data.update();assert all(o.data.vertices[i].co==original[i] for i in fixed);after=[world@v.co for v in o.data.vertices];error=max(((after[i]-after[j])-(pts[i]-pts[j])).length for i,j in pairs) if pairs else 0;assert error<3e-7
  bm=bmesh.new();bm.from_mesh(o.data);closed=all(e.is_manifold for e in bm.edges);volume=abs(bm.calc_volume(signed=True));bm.free();assert closed and volume>0,name
  o['v38BillIdentity']='bill-identity02 finite hooked bill and open swept mandible proposal; no final likeness/fit acceptance'
  records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'constructionClass':o.get('constructionClass'),'materials':[m.name if m else None for m in o.data.materials],'method':method,'changedVertexIndices':[i for i,p in enumerate(original) if o.data.vertices[i].co!=p],'protectedVertexIndices':sorted(fixed),'maximumMovementM':max(d.length for d in moves.values()),'recoveredFiniteStockPairs':pairs,'maximumStockVectorErrorM':error,'closedEdgeManifold':closed,'positiveVolumeM3':volume})
 bpy.context.view_layer.update();after=contact()
 return {'changedMeshes':ALLOWED,'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'attachmentAndEraMap':records,'contactBefore':before,'contactAfter':after,'contactDeltaNativeXYZ':[a-b for a,b in zip(after['leadingPointNativeXYZ'],before['leadingPointNativeXYZ'])],'contactLandmarksChanged':True,'confirmation':'Actual ownerJuly head-only controls deep assembled hook/open cheek/mandible; master03 cross-checks wholebird. Existing head01 is input, no rejected02 recipe replay.','reconstruction':'Authored finite curve/land dimensions, no exact reference metrology or mechanical certification.','limits':['Jaw pivot/socket/axle/caps and all crown/optic/cervical geometry exact; distal exterior change does not certify continuous jaw fit.','Recovered stock vectors exact; unmatched trimmed vertices use smoothfinite morph, no all-wall certificate.','Leading triangle extrema changed explicitly; root must evaluate actual exported contact solver.']}
