"""Final upper-course only: finite tapered swept cervical plates from original crown-fit02.
All lower courses, head/cheek/seat, pivots and surrounding objects remain exact.
"""
import bpy,bmesh,math
from mathutils import Vector
ALLOWED=[f'V23 cervical 4 directional guard {k+1}' for k in range(10)]
WALL=.0035
HEIGHTS=[.025,.035,.026,.033,.023,.016,.012,.008,.018,.005]
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def apply():
 bpy.context.view_layer.update();records=[]
 for k,name in enumerate(ALLOWED):
  o=bpy.data.objects[name];assert o.parent.name=='cervical-upper' and len(o.data.vertices)==399
  world=o.matrix_world.copy();inv=world.inverted();source=[world@v.co for v in o.data.vertices];faces=[tuple(f.vertices) for f in o.data.polygons];outer=[];maxmovement=0
  for index,p in enumerate(source):
   row,col=divmod(index,19);u=col/18;tip=smooth(1-row/8);center=source[row*19+9]
   # Each upper end narrows and slopes diagonally. Varied short tips replace
   # the continuous raised rim; lower attachment surface stays source-exact.
   q=p.copy();factor=1-.28*tip
   q.x=center.x+(p.x-center.x)*factor;q.y=center.y+(p.y-center.y)*factor
   handed=u if k%2==0 else 1-u
   q.z+=HEIGHTS[k]*tip*(.18+.82*handed)
   # A small directional crown in the end plane softens square mask corners,
   # while avoiding hanging tips or a complete cap around the head.
   q.z+=.004*tip*math.sin(math.pi*u)
   outer.append(q);maxmovement=max(maxmovement,(q-p).length)
  m=bpy.data.meshes.new(name+' V38 swept finite plate');m.from_pydata(outer,[],faces);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.normal_update();bm.verts.ensure_lookup_table()
  radial=Vector((sum(p.x for p in outer)/399,sum(p.y for p in outer)/399+.345,0))
  if bm.faces[len(bm.faces)//2].normal.dot(radial)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.normal_update()
  normals=[v.normal.copy() for v in bm.verts];outfaces=[tuple(v.index for v in f.verts) for f in bm.faces];bm.free();vertices=outer+[p-WALL*n for p,n in zip(outer,normals)];n=len(outer);closedfaces=outfaces+[tuple(n+i for i in reversed(f)) for f in outfaces];edges={}
  for face in outfaces:
   for a,b in zip(face,face[1:]+face[:1]):edges.setdefault(tuple(sorted((a,b))),[]).append((a,b))
  for values in edges.values():
   if len(values)==1:a,b=values[0];closedfaces.append((b,a,n+a,n+b))
  m.clear_geometry();m.from_pydata([inv@p for p in vertices],[],closedfaces);m.update()
  for mat in o.data.materials:m.materials.append(mat)
  bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));closed=all(e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True)
  if volume<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces));volume=-volume
  assert closed and volume>0,name
  bm.to_mesh(m);bm.free();o.data=m;o.modifiers.clear()
  for face in m.polygons:face.use_smooth=len(face.vertices)==4
  stock=[((world@m.vertices[i].co)-(world@m.vertices[i+399].co)).length for i in range(399)];assert max(abs(t-WALL) for t in stock)<2e-7
  o['v38NeckEnvelope']='neck-study02 tapered diagonally swept upper-course plate; rigid cervical-upper; lower three courses original-exact'
  records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'surfaceRole':o.get('surfaceRole'),'constructionClass':o.get('constructionClass'),'materials':[m.name for m in m.materials],'vertexScope':'Only existing upper-course guard geometry replaced as closed paired finite plate; original outer399-grid connectivity retained, inner399 and end walls explicit. No other objects.','maximumAuthoredOuterMovementM':maxmovement,'tipExtensionM':HEIGHTS[k],'upperTipWidthFraction':.72,'pairedWallM':WALL,'minimumPairedStockM':min(stock),'maximumPairedStockM':max(stock),'finiteClosed':closed,'positiveVolumeM3':volume})
 return {'changedMeshes':ALLOWED,'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'attachmentAndEraMap':records,'lowerThreeCoursesExact':True,'confirmation':'Master03/Mechanic control compact curved mechanical neck; July head-only.','reconstruction':'Ten varied tapered swept guard endings and finite3.5mm construction are authored proposals, not metrology or motion acceptance.','allHeadCrownCheekMaterialsPivotsBreastShouldersBodyLegsExact':True,'limits':['No stretch or owner bridge; each plate remains independently rigid on original cervical-upper.','Targeted seven-pose actual triangle screen required; same-owner/continuous/containment excluded.','No changes to root receiving guards or breast aperture.']}
