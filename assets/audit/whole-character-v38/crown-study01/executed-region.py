"""Compact finite crown courses from actual retained-owner native leaf paths.
Only 29 cranial-cover meshes; all other head/body/rig/material data untouched.
"""
import bpy,bmesh,math
from mathutils import Vector
ALLOWED=[f'V33 swept cranial leaf {row} {col}' for row,cols in [(0,range(7)),(1,range(7)),(2,range(7)),(3,range(1,6)),(4,range(2,5))] for col in cols]
def apply():
 bpy.context.view_layer.update();records=[];origin=bpy.data.objects['head'].matrix_world.translation.copy()
 for name in ALLOWED:
  obj=bpy.data.objects[name];assert obj.parent.name=='cranial-cover' and len(obj.data.vertices)==930
  row,col=map(int,name.split()[-2:]);source=[obj.matrix_world@v.co for v in obj.data.vertices[:465]]
  def sample(t,j):
   pos=max(0,min(1,t))*30;i=min(int(pos),29);f=pos-i;return source[i*15+j].lerp(source[(i+1)*15+j],f)
  start=0 if row==0 else .014+.007*(col%2)
  end=[.70,.71,.80,.97,1][row]-.015*(col%2)
  half=.025 if col not in (0,6) else .019
  if row==3:half=.024 if col in (2,3,4) else .021
  if row==4:half=.018 if col==3 else .016
  nr,nc=18,12;points=[];normals=[]
  for i in range(nr+1):
   u=i/nr
   for j in range(nc+1):
    a=2*j/nc-1
    # Finite broad receiving root and gently tapered rounded free margin,
    # replacing the source's long 91-percent narrowing comb tooth.
    t=start+(end-start)*u-.022*a*a*u*u
    center=sample(t,7);tangent=(sample(t,14)-sample(t,0)).normalized()
    axis=Vector((center.x,0,center.z-(origin.z+.27))).normalized()
    if axis.z<0:axis=Vector((center.x,0,.06)).normalized()
    width=half*(.89+.11*math.sin(math.pi*min(1,u/.30)))*(1-.28*u*u)
    # A small circumferential fall follows the actual skull; no tall crest.
    p=center+tangent*(a*width)-axis*(.002*a*a)
    points.append(p);normals.append(axis)
  count=len(points);wall=.003
  points += [p-wall*n for p,n in zip(points.copy(),normals)];faces=[];stride=nc+1
  for i in range(nr):
   for j in range(nc):
    k=i*stride+j;faces.extend([(k,k+1,k+stride+1,k+stride),(count+k+stride,count+k+stride+1,count+k+1,count+k)])
  border=list(range(stride))+[i*stride+nc for i in range(1,nr+1)]+[nr*stride+j for j in range(nc-1,-1,-1)]+[i*stride for i in range(nr-1,0,-1)]
  for i,a in enumerate(border):b=border[(i+1)%len(border)];faces.append((a,b,count+b,count+a))
  inv=obj.matrix_world.inverted();mesh=bpy.data.meshes.new(name+' V38 compact finite course');mesh.from_pydata([inv@p for p in points],[],faces);mesh.update()
  for material in obj.data.materials:mesh.materials.append(material)
  obj.data=mesh;bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  volume=bm.calc_volume(signed=True);assert all(e.is_manifold for e in bm.edges) and volume>0,name
  bm.to_mesh(mesh);bm.free()
  for face in mesh.polygons:face.use_smooth=True
  obj['v38CrownConstruction']='crown-study01 compact staggered finite swept metal course; appearance and motion unaccepted'
  records.append({'name':name,'owner':obj.parent.name,'eras':obj.get('exteriorEras'),'role':obj.get('constructionClass'),'sourceOuterGrid':[31,15],'sourceLongitudinalRange':[start,end],'rootHalfWidthM':half,'radialWallM':wall,'positiveVolumeM3':volume,'closed':True,'materials':[m.name for m in mesh.materials],'beforeBounds':[[min(p[k] for p in source) for k in range(3)],[max(p[k] for p in source) for k in range(3)]],'afterBounds':[[min(p[k] for p in points) for k in range(3)],[max(p[k] for p in points) for k in range(3)]]})
 return {'changedMeshes':ALLOWED,'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'attachmentAndEraMap':records,'confirmation':'July head-only/master03/selected Mechanic support compact swept overlapping crown armor, not a comb or tall crest.','reconstruction':'Exact finite stock, course count/outline and hidden receiving topology are proposals. Actual source center paths and cranial-cover ownership retained; no head-owner bridge.','openingAttachment':'All29 remain children of existing cranial-cover, itself under head; exact owner rest/matrices, fixed frontal seat and temporal leaves retained.'}
