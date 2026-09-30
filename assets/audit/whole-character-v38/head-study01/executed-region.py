"""Seven-piece constructed bill/cheek proposal from frozen shoulder-study01.
Actual rigid finite mesh edits; no optic, crown, jaw, pivot or cervical change.
"""
import bpy,bmesh,math
from mathutils import Vector
ALLOWED=[f'V32 returned upper bill course {i}' for i in range(3)]+[f'V33 formed lower cheek receiver {side} {i}' for side in (-1,1) for i in range(2)]
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def solid(o):
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 volume=bm.calc_volume(signed=True);closed=all(e.is_manifold for e in bm.edges)
 if not closed or volume<=0:raise RuntimeError('Invalid finite solid '+o.name)
 bm.to_mesh(o.data);bm.free();return {'name':o.name,'closed':closed,'positiveVolumeM3':volume}
def contact():
 bpy.context.view_layer.update();points=[];dg=bpy.context.evaluated_depsgraph_get()
 for o in bpy.data.objects:
  if o.type=='MESH' and o.parent and o.parent.name=='upper-bill':
   ev=o.evaluated_get(dg);mesh=ev.to_mesh();mesh.calc_loop_triangles()
   for tri in mesh.loop_triangles:
    for i in tri.vertices:points.append((o.name,ev.matrix_world@mesh.vertices[i].co))
   ev.to_mesh_clear()
 front=min(points,key=lambda row:row[1].y)
 return {'triangleVertexExtremaNativeXYZ':{'min':[min(p[k] for _,p in points) for k in range(3)],'max':[max(p[k] for _,p in points) for k in range(3)]},'leadingObject':front[0],'leadingPointNativeXYZ':list(front[1]),'triangleVertexSamples':len(points),'method':'Actual evaluated upper-bill triangle vertices; native negativeY is forward. No fixed landmark substituted.'}
def apply():
 bpy.context.view_layer.update();before_contact=contact();records=[];jaw=bpy.data.objects['jaw'].matrix_world.translation.copy();eye=Vector((0,-.578800007,1.725484034))
 for name in ALLOWED:
  o=bpy.data.objects[name];world=o.matrix_world.copy();inv=world.inverted();old=[world@v.co for v in o.data.vertices]
  if 'upper bill' in name:
   course=int(name[-1]);hollow=course<2;assert len(old)==(700 if hollow else 350)
   # Keep leading profile extrema among the chosen constructed stations.
   # Fewer purposeful longitudinal lands replace a smoothly rounded cap.
   rows=set([0,34,*range(0,35,4)])
   for axis in range(3):
    rows.add(min(range(350),key=lambda i:old[i][axis])//10);rows.add(max(range(350),key=lambda i:old[i][axis])//10)
   rows=sorted(rows);points=[]
   for layer in range(2 if hollow else 1):
    for row in rows:
     original=old[layer*350+row*10:layer*350+row*10+10];width=max(abs(p.x) for p in original)
     for k,p in enumerate(original):
      p=p.copy()
      # Broad hard cheek plane spans three ring corners. Root and hook
      # silhouette remain source-led; cutting returns pull forward to
      # expose the actual mouth cavity behind the armored bill.
      if k in (2,3,4,6,7,8):p.x=(-1 if k>=6 else 1)*width*.96
      q=(course+row/34)/3;weight=math.sin(math.pi*q)**2
      relief={3:.18,4:.65,5:1,6:.65,7:.18}.get(k,0)
      p.y-=.024*weight*relief
      points.append(inv@p)
   n=len(rows)*10;faces=[]
   for j in range(len(rows)-1):
    for k in range(10):a=j*10+k;b=j*10+(k+1)%10;faces.append((a,b,b+10,a+10))
    if hollow:
     for k in range(10):a=n+j*10+k;b=n+j*10+(k+1)%10;faces.append((a+10,b+10,b,a))
   if hollow:
    for k in range(10):q=(k+1)%10;faces.extend([(q,k,n+k,n+q),((len(rows)-1)*10+k,(len(rows)-1)*10+q,n+(len(rows)-1)*10+q,n+(len(rows)-1)*10+k)])
   else:faces.extend([tuple(reversed(range(10))),tuple((len(rows)-1)*10+k for k in range(10))])
   mesh=bpy.data.meshes.new(name+' V38 constructed plane mesh');mesh.from_pydata(points,[],faces);mesh.update()
   for material in o.data.materials:mesh.materials.append(material)
   o.data=mesh;method='Finite broader hard side lands, fewer authored profile stations,24mm maximum posterior cutting relief; leading nativeY extrema retained as stations.'
  else:
   o.data=o.data.copy()
   for vertex,p in zip(o.data.vertices,old):
    r=math.hypot(p.y-eye.y,p.z-eye.z);jr=math.hypot(p.y-jaw.y,p.z-jaw.z)
    weight=ease((r-.068)/.038)*ease((eye.z-p.z-.012)/.060)*ease((jr-.026)/.027)
    p=p+Vector((0,-.007*weight,.026*weight));vertex.co=inv@p
   method='Outer lower cheek rim lifts26mm/follows anterior7mm to frame opening; fixed inner optic seat and jaw bore vicinity protected by zero-weight zones.'
  o.data.update();finite=solid(o)
  for face in o.data.polygons:face.use_smooth=False
  o['v38HeadProfile']='Constructed bill planes and cheek opening proposal; no likeness or motion acceptance'
  records.append({**finite,'owner':o.parent.name,'eras':o.get('exteriorEras'),'materialRoles':[m.name if m else None for m in o.data.materials],'method':method})
 after_contact=contact()
 return {'changedMeshes':ALLOWED,'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'attachmentAndEraMap':records,'contactBefore':before_contact,'contactAfter':after_contact,'contactDeltaNativeXYZ':[a-b for a,b in zip(after_contact['leadingPointNativeXYZ'],before_contact['leadingPointNativeXYZ'])],'contactLandmarksChanged':False,'confirmation':'July controls head identity only: deep assembled hooked bill with framed cheek opening; master03 cross-checks full-bird continuity.','reconstruction':'Exact plate stationing, section lands and relieved cavity dimensions are authored proposals, not recovered CAD or engineering fits.'}
