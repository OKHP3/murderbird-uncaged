"""Actual bow-rooted lower throat construction and independent posterior receiver tongues."""
import bpy,bmesh,math
from mathutils import Vector
LOWER=[f'V33 tapered throat cheek plate {s} 0 {c}'for s in(-1,0,1)for c in range(3)]
GUARDS=[f'V23 cervical 4 directional guard {k}'for k in(7,8,10)]
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def finish(o,verts,faces):
 inv=o.matrix_world.inverted();m=bpy.data.meshes.new(o.name+' V38 constructed supported interface');m.from_pydata([inv@p for p in verts],[],faces);m.update()
 for mat in o.data.materials:m.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),o.name
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 vol=bm.calc_volume(signed=True);assert vol>0;bm.to_mesh(m);bm.free();o.data=m;o.modifiers.clear()
 for f in m.polygons:f.use_smooth=len(f.vertices)==4
 if 'constructionDescription'in o:o['constructionDescriptionHistory']=str(o['constructionDescription'])
 o['constructionDescription']='V38 neck-interface01 finite independently rigid passive interface; actual local support seats explicit, new free overlap clearance remains proposed and separately screened'
 o['v38NeckInterface']='head bow-rooted receiving leaves / separately cervical-upper-owned posterior tongues; no rigid owner bridge, actuators or pivot changes'
 return vol
def apply():
 bpy.context.view_layer.update();origin=bpy.data.objects['head'].matrix_world.translation.copy();records=[];headSeats=[]
 for name in LOWER:
  o=bpy.data.objects[name];side,col=map(int,(name.split()[-3],name.split()[-1]));supportside=side if side else(-1 if col<2 else 1);bow=bpy.data.objects[f'V31 passive cranial load bow {supportside}'];bow.data.calc_loop_triangles();bv=[bow.matrix_world@v.co for v in bow.data.vertices];assert len(bv)==1122;start=20+col;nu=20;nv=6;outer=[];inner=[];mapping={}
  root=[bv[start*11+2+j]for j in range(7)];top=sum(p.z for p in root)/7;wall=.0035
  def face(u,t):
   if side==0:
    lo,hi=[(-.105,-.031),(-.034,.034),(.031,.105)][col];x=lo+(hi-lo)*u;R=.167-.017*(abs(x)/.12)**2;theta=math.radians(144+21*t+4*(u-.5));y=origin.y+R*math.cos(theta);z=origin.z+R*math.sin(theta)
   else:
    lo,hi=[(.70,1.48),(1.50,2.26),(2.28,3.02)][col];a=lo+(hi-lo)*u;rx=.133-.012*t;ry=.143-.010*t;x=side*rx*math.sin(a);y=origin.y-ry*math.cos(a);rear=max(0,y-origin.y);lower=origin.z+.047+.45*rear;z=top*(1-t)+lower*t-.005*t*(u-.5)
   return Vector((x,y,z))
  for i in range(nu+1):
   for j in range(7):
    u=j/6
    if i<=2:
     src=(start+2-i)*11+2+j;q=bv[src].copy();mapping[src]=i*7+j;normal=(q-bv[src+561]).normalized()
    elif i<=6:
     t=smooth((i-2)/4);q=root[j].lerp(face(u,0),t);normal=Vector((q.x,q.y-origin.y,0)).normalized()
    else:
     q=face(u,(i-6)/(nu-6));normal=Vector((q.x,q.y-origin.y,0)).normalized()
    inner.append(q);outer.append(q+wall*normal)
  n=len(outer);faces=[];seat=[]
  for tri in bow.data.loop_triangles:
   if all(k in mapping for k in tri.vertices):
    f=tuple(mapping[k]for k in tri.vertices);faces.extend([f,tuple(n+k for k in reversed(f))]);seat.append({'actualBowTriangle':tri.index,'sourceBowVertexIndices':list(tri.vertices),'plateInnerVertexIndices':[n+k for k in f]})
  assert len(seat)==24,(name,len(seat))
  for i in range(2,nu):
   for j in range(6):
    k=i*7+j;l=k+7;faces.extend([(k,k+1,l+1,l),(n+l,n+l+1,n+k+1,n+k)])
  border=list(range(7))+[i*7+6 for i in range(1,nu+1)]+[nu*7+j for j in range(5,-1,-1)]+[i*7 for i in range(nu-1,0,-1)]
  for i,k in enumerate(border):q=border[(i+1)%len(border)];faces.append((k,q,n+q,n+k))
  volume=finish(o,outer+inner,faces);maxerr=max(((o.matrix_world@o.data.vertices[entry['plateInnerVertexIndices'][j]].co)-bv[entry['sourceBowVertexIndices'][j]]).length for entry in seat for j in range(3));assert maxerr<1e-7
  records.append({'name':name,'owner':'head','eras':o.get('exteriorEras'),'constructionClass':'inherited-passive','role':'Actual bow-rooted finite rigid descending throat leaf; independently moving relative to cervical receiver','support':bow.name,'supportRows':[start,start+2],'supportColumns':[2,8],'exactActualReceivingTriangles':seat,'maximumCopiedSeatErrorM':maxerr,'wallNominalM':wall,'closedEdgeManifold':True,'positiveVolumeM3':volume,'seatingMeaning':'Plate inner root surface shares24 actual bow triangles, outgoing wall follows actual source outward stock direction. Finite surface contact proof, not fabricated/welded joint or full root clearance acceptance.'});headSeats.append(name)
 for name in GUARDS:
  o=bpy.data.objects[name];w=o.matrix_world.copy();inv=w.inverted();old=[v.co.copy()for v in o.data.vertices];src=[w@p for p in old];assert len(src)==798;o.data=o.data.copy();maximum=0
  for i in range(399):
   row,col=divmod(i,19);free=smooth((14-row)/14);p=src[i];theta=math.radians(51+13*(col/18-.5));R=.094-.023*(abs(p.x)/.12)**2;target=Vector((p.x,origin.y+R*math.cos(theta),origin.z+R*math.sin(theta)));q=p.lerp(target,free);delta=q-p;maximum=max(maximum,delta.length)
   if free>0:o.data.vertices[i].co=inv@q;o.data.vertices[i+399].co=inv@(src[i+399]+delta)
  o.data.update();protected=list(range(14*19,399));assert all(o.data.vertices[i].co==old[i]and o.data.vertices[i+399].co==old[i+399]for i in protected);bm=bmesh.new();bm.from_mesh(o.data);closed=all(e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free();assert closed and volume>0
  o['constructionDescriptionHistory']=str(o.get('constructionDescription','unrecorded'));o['constructionDescription']='V38 neck-interface01 separately cervical-upper-owned partial posterior sliding receiver tongue; lowerseven original receiving rows/pin/link interfaces exact; free headlap and neighbor clearance proposed'
  o['v38NeckInterface']='Partial posterior head-pivot-centered receiver profile, no complete collar or rigid joint bridge; original finite paired stock vectors retained'
  records.append({'name':name,'owner':'cervical-upper','eras':o.get('exteriorEras'),'constructionClass':o.get('constructionClass'),'role':'Independent finite partial posterior receiving tongue; original guard lowerseven stock rows exact','sourceExactReceivingVerticesBothSkins':266,'maximumAuthoredMovementM':maximum,'closedEdgeManifold':closed,'positiveVolumeM3':volume,'attachmentQualification':'Retained guard attachment/root strip and full original linked hardware, shafts/races. Source receiving membership retained; not inferred engineering acceptance.'})
 return {'changedMeshes':LOWER+GUARDS,'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'watchMeshes':LOWER+GUARDS,'attachmentAndEraMap':records,'supportConstruction':'Nine reconstructed lower-throat leaves genuinely rooted on actual cranial bow stock; three independent upper-cervical posterior receiver tongues. Two identified rear side leaves are reconstructed within connected lower-throat system to retain fuller target without importing failed lower-course expansion.','headSupportSeatTrianglesPerLeaf':24,'protected':'All lower30 and otherseven upper-course guards, original uppernine throat leaves, bows/journals/shaftseats/pivots/rig/runtimeendpoints, crown/bill/optic/jaw/head identity, body/wing/leg/foot/materials/era profiles exact.','proposalDimensions':'Head-owned free contour x up to133mm from center; forward partial envelope up to167mm from headpivot; rearward descending ellipse; three separate receiver tongues nominal94mm headpivot profile with lateral taper. Authored dimensions, not reference metrology.','limits':['Actual root seat surface contact is not a welded/solid union or clearance certificate; same-owner root and adjacent seams included in strict screen.','Source paired wall preserved on receivers; headleaves explicit3.5mm paired stock, perpendicular normal quality and load capacity unvalidated.','No rigid bridge, new motion/era role, continuous-sweep/containment or owner likeness acceptance.']}
