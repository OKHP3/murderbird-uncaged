import bpy,bmesh,json,math
from mathutils import Vector
NAMES=[f'V31 passive cranial load bow {s}'for s in [-1,1]]
# New monotonic fork stations in native world coordinates: x is absolute side centre,
# y,z define route; w is halfwidth inY, thickness6mm inX. Dimensions are proposals.
STATIONS=[(0,.024915,-.391116,1.522750,.0135),(8,.004,-.392,1.545,.004),(12,.004,-.392,1.554,.004),(17,.004,-.392,1.565,.004),(20,.004,-.392,1.576,.004),(25,.040,-.397,1.586,.008),(30,.080,-.402,1.601,.012)]
def station(row):
 for a,b in zip(STATIONS,STATIONS[1:]):
  if row<=b[0]:
   t=(row-a[0])/(b[0]-a[0]);return [a[i]+(b[i]-a[i])*t for i in range(1,5)]
 return list(STATIONS[-1][1:])
def apply():
 bpy.context.view_layer.update();records=[]
 for side in [-1,1]:
  o=bpy.data.objects[f'V31 passive cranial load bow {side}'];old=[o.matrix_world@v.co for v in o.data.vertices];assert len(old)==1122;half=561;inv=o.matrix_world.inverted();new=old.copy()
  cap=[old[j]for j in range(11)]+[old[half+j]for j in range(11)];root=sum(cap,Vector())/22
  end=[old[35*11+j]for j in range(11)]+[old[half+35*11+j]for j in range(11)];ec=sum(end,Vector())/22
  for row in range(1,35):
   if row<=30:x,y,z,w=station(row);center=Vector((side*x,y,z))
   else:
    t=(row-30)/5;center=Vector((side*.080,-.402,1.601)).lerp(ec,t);w=.012+(max(abs(p.y-ec.y)for p in end)-.012)*t
   for layer in [0,1]:
    for j in range(11):
     q=2*j/10-1;offset=Vector((side*(.003 if layer==0 else-.003),q*w,0))
     if row<4:
      t=row/4;idx=layer*half+j;sourceOffset=old[idx]-root;offset=sourceOffset.lerp(offset,t)
     if row>30:
      t=(row-30)/5;idx=layer*half+35*11+j;offset=offset.lerp(old[idx]-ec,t)
     new[layer*half+row*11+j]=center+offset
  # Root cap and upper skull rows are actual source surfaces, byte exact locally.
  for row in [0]+list(range(35,51)):
   for layer in [0,1]:
    for j in range(11):idx=layer*half+row*11+j;assert new[idx]==old[idx]
  mesh=bpy.data.meshes.new(o.name+' fork through actual socket polar opening');mesh.from_pydata([inv@p for p in new],[],[list(f.vertices)for f in o.data.polygons]);mesh.update()
  for mat in o.data.materials:mesh.materials.append(mat)
  bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges)
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  volume=bm.calc_volume(signed=True);assert volume>0;bm.to_mesh(mesh);bm.free()
  for f in mesh.polygons:f.use_smooth=True
  # Avoid roundtrip float drift on all protected vertex coordinates, not just approximate world match.
  for row in [0]+list(range(35,51)):
   for layer in [0,1]:
    for j in range(11):idx=layer*half+row*11+j;mesh.vertices[idx].co=o.data.vertices[idx].co.copy()
  o.data=mesh;o['constructionDescription']='Rigid passive head-owned paired fork: original seat cap, converging stock inside own ball, narrow stems through upper socket polar aperture, fan into exact upper cranial bow rows35-50. Actual finite sample fit remains qualified.';o['v38CranialRoute01']=json.dumps({'rootCapRowExact':0,'upperRowsExact':[35,50],'stemCentreAbsX':.004,'stemXThickness':.006,'stemYWidth':.008,'socketOpeningPolarDegrees':50,'stations':STATIONS,'status':'Proposal, actual pose/surface screen separate'})
  records.append({'name':o.name,'owner':o.parent.name,'rootCapRowExact':0,'upperRowsExact':[35,50],'upperRow35NativeCenter':list(ec),'retainedRootCenterNative':list(root),'nominalStemFiniteSectionM':[.006,.008],'nominalPairedStemGapM':.002,'volumeM3':volume,'receivingRoute':'Retained own shaftseat cap plus intentional engagement into own head ball/stem; no stock fixed to upper-owned socket','actualFiniteContact':'Pending targeted Boolean commonstock, not corner-only witness'})
 return {'status':'Passive cranial fork/stem route PROPOSAL; no silhouette/armor/owneracceptance','changedMeshes':NAMES,'construction':records,'stationsNative':STATIONS,'protected':'Exactly allother geometry,5shells,head/bodyworldrest,allpivots/parents/owners/materials/eraeligibility','limits':['Small nominal stem section is reconstruction, not certified load/strength.','Only captured seven real trajectory samples screened, not continuousyaw/pitch/physicalfit.','Current inherited10mm head stem/socket compatibility evaluated read-only.','Frozen old bow route annotations are history; current constructionDescription and v38CranialRoute01 govern changedtwo meshes.']}
