"""Single bounded seam01 correction from frozen pure-restored breast-support02.
Original15 lower stock identities and upper-course roots remain exact.
"""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
UPPER=[f'V34 formed breast course 3 plate {i}'for i in range(1,8)]
LOWER=[f'V34 formed breast course 4 plate {i}'for i in range(1,7)]
def bvh(names):
 v=[];f=[]
 for n in names:
  o=bpy.data.objects[n];o.data.calc_loop_triangles();offset=len(v);v.extend(o.matrix_world@p.co for p in o.data.vertices);f.extend(tuple(offset+i for i in t.vertices)for t in o.data.loop_triangles)
 return BVHTree.FromPolygons(v,f,all_triangles=True,epsilon=0)
def apply():
 bpy.context.view_layer.update();receiving=bvh(LOWER);records=[]
 for n in UPPER:
  o=bpy.data.objects[n];before=[p.co.copy()for p in o.data.vertices];world=[o.matrix_world@p for p in before];assert len(world)==750,n;half=375;R=24;C=14;required={};hits=[]
  for i in range(13,25):
   for j in range(15):
    index=i*15+j;p=world[index];d=Vector((p.x,p.y,0)).normalized();hit=receiving.ray_cast(p+.14*d,-d,.28)
    if hit[0]is None:continue
    normal=hit[1]
    if normal.dot(d)<0:normal=-normal
    desired=hit[0]+.008*normal+.004*d;move=desired-p
    if move.dot(d)<=0:continue
    # Move along the existing angular ordinate;8mm normalstand plus4mm
    # radialstand supplies finite free stock outside the actual receiver.
    amount=move.dot(d);required[(i,j)]=amount;hits.append({'index':index,'actualReceiverTriangle':hit[2],'actualReceiverPoint':list(hit[0]),'requiredRadialAdvanceM':amount})
  advances=[];inv=o.matrix_world.inverted()
  for i in range(11,25):
   for j in range(15):
    # Conservative smooth envelope carries a receiving lap across its
    # local footprint while bending into the retained upper course.
    amount=max((value*math.exp(-((i-ri)/3.5)**2-((j-rj)/1.6)**2)for (ri,rj),value in required.items()),default=0)
    amount*=min(1,max(0,(i-11)/4));index=i*15+j;p=world[index];d=Vector((p.x,p.y,0)).normalized();shift=amount*d
    o.data.vertices[index].co=inv@(world[index]+shift);o.data.vertices[half+index].co=inv@(world[half+index]+shift);advances.append({'index':index,'radialAdvanceM':amount})
  o.data.update();bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),n;volume=bm.calc_volume(signed=True);assert volume>0,n;bm.to_mesh(o.data);bm.free()
  protected=list(range(11*15))+list(range(half,half+11*15));assert all(o.data.vertices[i].co==before[i]for i in protected),(n,'protected upper/root changed')
  o['historicalConstructionBeforeBreastSupport02Seam01']=json.dumps({k:o[k]for k in('constructionDescription','geometryStatus','breastSupportRevision')if k in o});o['constructionDescription']='Original fuller upper course with source-exact upper/root165 outer+165 inner vertices; lower free lap radially formed outside actual original row4 receiver stock via finite surface rays and rounded local advance envelope';o['geometryStatus']='Breast-support02-seam01 proposed finite receiving lap; actual affected-surface screen remains required, no union or continuous swept certification';o['breastSupportRevision']='breast-support02-seam01'
  records.append({'name':n,'owner':o.parent.name,'eras':o.get('exteriorEras'),'sourceExactUpperAndRootVertexCount':len(protected),'actualFiniteReceiverSamples':hits[::max(1,len(hits)//8)],'maximumActualRadialAdvanceM':max(a['radialAdvanceM']for a in advances),'nominalRequestedNormalAndRadialStandM':[.008,.004],'stockQualification':'Existing paired outer/inner displacement vectors preserved; deformation changes normal thickness direction.3.5mm is original nominal stock, not proof of uniform perpendicular section after forming.','closedPositiveVolumeM3':volume})
 return {'changedMeshes':UPPER,'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'watchMeshes':UPPER+LOWER+['V30 continuous tapered breast liner','V23 breast moving return -1','V23 breast moving return 1'],'attachmentAndEraMap':records,'preserved':'Exact original15 lower plates from pure-restored02; full upper courses1–2 and backing; all row3 roots/upper165+165 vertices; original support/endpoints and named rig, head/neck/wings/pelvis/feet, material profiles/era eligibility. Single bounded correction only to row3 free lap.','limits':['Actual finite receiving rays construct a proposed lap; triangle/stock screen, not stand-alone vertex spacing, decides intersection status.','Paired stock spacing preserved but formed perpendicular thickness/union/load capacity not certified.','No owner acceptance or full sweep/engineering proof.']}
