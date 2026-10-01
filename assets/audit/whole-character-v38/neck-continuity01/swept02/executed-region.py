"""Sole swept02 correction: lower30 original-exact; upper tips/head throat independently rigid."""
import bpy,bmesh,math
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
GUARDS=[f'V23 cervical 4 directional guard {k}'for k in range(1,11)]
THROAT=[f'V33 tapered throat cheek plate {s} {r} {c}'for s in(-1,0,1)for r in(0,1)for c in range(3)]
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def stock_record(o,old,protected,deltas):
 w=o.matrix_world;half=len(old)//2;o.data.update();assert all(o.data.vertices[i].co==old[i]and o.data.vertices[i+half].co==old[i+half]for i in protected),(o.name,'retained receiving strip differs')
 err=max(((w@o.data.vertices[i+half].co-w@o.data.vertices[i].co)-(w@old[i+half]-w@old[i])).length for i in range(half));assert err<2e-7
 bm=bmesh.new();bm.from_mesh(o.data);closed=all(e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);bm.free();assert closed and vol>0,(o.name,closed,vol)
 o['constructionDescriptionHistory']=str(o.get('constructionDescription','unrecorded'));o['constructionDescription']='V38 neck-continuity01 swept02 finite independently rigid passive upper guard/throat free envelope; exact original receiving band, fit status proposed with bounded actual stock screen'
 o['v38NeckContinuity']='swept02: lower30 original-exact, original guard4 lower seven receiving rows and head upper four receiving rows retained. No joint bridge; paired stock vectors retained; swept clearance not certified.'
 return {'name':o.name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'constructionClass':o.get('constructionClass'),'protectedReceivingVerticesBothSkins':2*len(protected),'pairedDisplacementVectorMaximumErrorM':err,'maximumAuthoredWorldMovementM':max(deltas),'finiteClosed':closed,'positiveVolumeM3':vol,'attachmentQualification':'Source actual receiving strip retained; new free edge/seating is proposal. Actual stock/pose screen separate; parent identity alone is not seating proof.'}
def apply():
 bpy.context.view_layer.update();records=[]
 for name in GUARDS:
  o=bpy.data.objects[name];old=[v.co.copy()for v in o.data.vertices];w=o.matrix_world.copy();inv=w.inverted();src=[w@p for p in old];assert len(src)==798;o.data=o.data.copy();deltas=[];k=int(name.split()[-1])
  for i in range(399):
   row,col=divmod(i,19);u=col/18;free=smooth((14-row)/14);p=src[i];q=p.copy();hand=u if k%2 else 1-u
   # Keep original finite lower receiving band. Free upper course ends are
   # short diagonal descending sweeps, not a raised continuous neck collar.
   drop=(.027+.014*hand)*free;q.z-=drop
   q.x*=1-.035*free;q.y=o.parent.matrix_world.translation.y+(q.y-o.parent.matrix_world.translation.y)*(1-.02*free)
   delta=q-p;deltas.append(delta.length)
   if delta.length>0:o.data.vertices[i].co=inv@q;o.data.vertices[i+399].co=inv@(src[i+399]+delta)
  records.append(stock_record(o,old,list(range(14*19,399)),deltas))
 bpy.context.view_layer.update()
 # Actual new finite upper guard sweep is mapped into fixed head-rest space,
 # sampling relative headpitch only: the guard and head share all cervical
 # ancestor transforms, so rootbend/yaw cancel at this interface.
 head=bpy.data.objects['head'];hw=head.matrix_world.copy();origin=hw.translation.copy();verts=[];faces=[];angles=[-.65+i*.65/16 for i in range(17)]
 for angle in angles:
  torest=hw@(hw@Matrix.Rotation(angle,4,'X')).inverted()
  for name in GUARDS:
   o=bpy.data.objects[name];m=o.data;m.calc_loop_triangles();start=len(verts);verts.extend(torest@(o.matrix_world@v.co)for v in m.vertices);faces.extend(tuple(start+i for i in t.vertices)for t in m.loop_triangles)
 sweep=BVHTree.FromPolygons(verts,faces,all_triangles=True,epsilon=0);fit=[]
 for name in THROAT:
  o=bpy.data.objects[name];old=[v.co.copy()for v in o.data.vertices];w=o.matrix_world.copy();inv=w.inverted();src=[w@p for p in old];assert len(src)==990;o.data=o.data.copy();outer=[];required=[];axes=[];side,rowCourse,colCourse=map(int,name.split()[-3:])
  for i in range(495):
   row,col=divmod(i,15);free=smooth((29-row)/29);p=src[i];q=p.copy();front=smooth((-.28-p.y)/.14);q.x*=1+.27*free;q.y-=.046*free*front
   # Longer oblique side leaves descend toward the rear cradle while
   # leaving the separate head/cervical movement seam legible.
   if side and rowCourse==0:
    rear=smooth((p.y+.40)/.17);q.z-=.020*free*rear*(.45+.55*col/14)
   direction=q-origin;r=direction.length;direction.normalize();advance=0
   # Find finite stock lying at/near this new free boundary. The last
   # sweep hit on the radial segment governs outward receiving clearance.
   at=origin.copy();travel=0
   for it in range(40):
    hit=sweep.ray_cast(at,direction,r+.040-travel)
    if hit[0] is None:break
    travel+=(hit[0]-at).length
    if travel>r-.015 and row<29:advance=max(advance,travel+.008-r)
    at=hit[0]+direction*.00005;travel+=.00005
    if travel>=r+.040:break
   outer.append(q);required.append(max(0,advance));axes.append(direction)
  # Smooth conservative outward receiving forming only on free material;
  # protected head-mounted rows29–32 stay byte exact, never reclassified.
  for it in range(2):
   oldreq=required.copy()
   for row in range(29):
    for col in range(15):
     i=row*15+col;neighbours=[oldreq[rr*15+cc]for rr,cc in((row-1,col),(row+1,col),(row,col-1),(row,col+1))if 0<=rr<29 and 0<=cc<15];required[i]=max(oldreq[i],.75*max(neighbours,default=0))
  deltas=[]
  for i,q in enumerate(outer):
   if i//15>=29:q=src[i]
   else:q=q+required[i]*axes[i]
   delta=q-src[i];deltas.append(delta.length)
   if delta.length>0:o.data.vertices[i].co=inv@q;o.data.vertices[i+495].co=inv@(src[i+495]+delta)
  rec=stock_record(o,old,list(range(29*15,495)),deltas);rec['actualSweepFreeReceivingAdvanceM']=max(required);records.append(rec);fit.append({'name':name,'maximumReceivingAdvanceM':max(required),'shiftedFreeSamples':sum(x>0 for x in required)})
 return {'changedMeshes':GUARDS+THROAT,'watchMeshes':GUARDS+THROAT+[f'V23 cervical {r} directional guard {k}'for r in(1,2,3)for k in range(1,11)],'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'attachmentAndEraMap':records,'lower30CervicalGuardsOriginalExact':True,'relativeHeadGuardReceivingProposal':{'source':'Actual final ten upper-course finite stocks','sampleHeadPitchRad':angles,'authoredRadialReceivingStandM':.008,'counts':fit,'qualification':'Finite ray-sampled free receiving shaping, not whole surface clearance/containment or continuous swept-fit certificate.'},'protected':'Crown/optic/bill/jaw/head journals, original cranial bows/frame, named pivots and rig/control endpoints, source lower30 guards/root underlaps/receiving cheeks, all body/wing/leg/foot/material/era profiles exact. Upper guard lowerseven rows and head throat upperfour actual receiving rows exact.','reconstruction':'Sole second proposal retains fuller throat direction with short diagonal upper-guard edges and longer swept rear cheek leaves. Uses actual stock receiving sweep; no organic tissue, rigid bridge or actuation.','limits':['Normal wall after forming remains qualified despite source paired vectors retained.','Actual finite triangle screen required; original inherited warnings distinguished from new skin interfaces.','No owner likeness, continuous motion, containment, load or fabrication acceptance.']}
