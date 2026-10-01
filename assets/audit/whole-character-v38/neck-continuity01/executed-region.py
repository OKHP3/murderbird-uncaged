"""Independently rigid cheek/throat to cervical free-envelope forming; receiving bands exact."""
import bpy,bmesh,math,json
from mathutils import Vector
GUARDS=[f'V23 cervical {course} directional guard {k}'for course in range(1,5)for k in range(1,11)]
THROAT=[f'V33 tapered throat cheek plate {s} {r} {c}'for s in(-1,0,1)for r in(0,1)for c in range(3)]
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def apply():
 bpy.context.view_layer.update();records=[]
 for name in GUARDS+THROAT:
  o=bpy.data.objects[name];w=o.matrix_world.copy();inv=w.inverted();old=[v.co.copy()for v in o.data.vertices];src=[w@p for p in old];half=len(old)//2;assert half in(399,495);o.data=o.data.copy();deltas=[];protected=[]
  for i in range(half):
   p=src[i];q=p.copy()
   if name in GUARDS:
    row,col=divmod(i,19);course=int(name.split()[2]);cy=o.parent.matrix_world.translation.y
    if course==1:
     free=smooth((16-row)/16);q.x*=1-.18*free;q.y=cy+(p.y-cy)*(1-.10*free);q.z-=.012*free
    elif course in(2,3):
     free=math.sin(math.pi*max(0,min(1,(row-3)/13)))**2 if 3<row<16 else 0;front=smooth((cy-p.y)/.12);q.x*=1+.09*free;q.y-=.018*free*front
    else:
     free=smooth((18-row)/18);q.x*=1+.12*free;front=smooth((cy-p.y)/.12);q.y-=.015*free*front
    if row>=18 or (course in(2,3)and(row<=3 or row>=16)):protected.append(i)
   else:
    row,col=divmod(i,15);free=smooth((29-row)/29);front=smooth((-.28-p.y)/.14);q.x*=1+.27*free;q.y-=.046*free*front
    if row>=29:protected.append(i)
   delta=q-p;deltas.append(delta.length)
   if delta.length>0:
    o.data.vertices[i].co=inv@q;o.data.vertices[i+half].co=inv@(src[i+half]+delta)
  o.data.update();assert all(o.data.vertices[i].co==old[i]and o.data.vertices[i+half].co==old[i+half]for i in protected),(name,'protected receiver changed')
  stock=max(((w@o.data.vertices[i+half].co-w@o.data.vertices[i].co)-(src[i+half]-src[i])).length for i in range(half));assert stock<2e-7
  bm=bmesh.new();bm.from_mesh(o.data);closed=all(e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free();assert closed and volume>0,(name,volume,closed)
  if 'constructionDescription' in o:o['constructionDescriptionHistory']=str(o['constructionDescription'])
  o['constructionDescription']='V38 neck-continuity01 independently rigid formed passive throat/cervical guard; original finite receiving band retained; altered free-envelope fit remains proposed and screened separately'
  o['v38NeckContinuity']='No joint bridge; original owner, root/upper receiving vertices, paired stock vectors retained. Free mid/end forming proposal; normal wall and swept fit not certified.'
  records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'constructionClass':o.get('constructionClass'),'protectedReceivingVerticesBothSkins':2*len(protected),'protectedReceivingVertexIndices':protected,'pairedDisplacementVectorMaximumErrorM':stock,'maximumAuthoredWorldMovementM':max(deltas),'finiteClosed':closed,'positiveVolumeM3':volume,'role':'Inherited passive finite rigid guard/receiving plate; original support frame and journals exact; no actuation added','attachmentQualification':'Original actual receiving surface strip unchanged; free-course adjacency/seating requires separate finite diagnostic, not parenting-only pass.'})
 return {'changedMeshes':GUARDS+THROAT,'watchMeshes':GUARDS+THROAT,'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'attachmentAndEraMap':records,'protected':'All named cervical/head/jaw pivots, head crown/optics/bill/jaw/socket identity, cranial load bows/journals, throat upper receiving bands, base root rows/underlaps, fixed body receiving cheeks, all torso/wing/leg/foot geometry and materials/era profiles exact.','method':'Source finite stock free-envelope forming: base raised lip18% lateral/10% sagittal contraction and12mm tip lowering; middle two courses9% lateral+18mm forward convexity away from receiving ends; upper course12% lateral+15mm forward free-end forming; head-throat free envelope27% lateral+46mm forward, blended into exact upper four receiving rows.','reconstruction':'Authored dimensioned proposal selected from actual Master03 whole-bird and July head-only. No reference metrology or owner likeness acceptance.','limits':['Original paired outer-inner vectors preserved; after forming normal stock thickness and support load path remain unvalidated.','Receiving surfaces preserved does not establish continuous fit or absence of solid containment; actual surface/pose evidence separate.','No rigid joint bridge, organic tissue, changed actuation/era role, runtime or production change.']}
