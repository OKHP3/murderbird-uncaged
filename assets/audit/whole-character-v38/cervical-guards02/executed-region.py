"""Cervical-guards02: compact directional rigid four-course neck armor.
Pinned bill-relationship02; source lower root strips and articulated owners retained.
"""
import bpy,bmesh,math
from mathutils import Vector
GUARDS=[f'V23 cervical 4 directional guard {i}' for i in range(1,11)]
THROAT=[f'V33 tapered throat cheek plate {side} {row} {col}' for side in(-1,0,1)for row in(0,1)for col in range(3)]
NAMES=GUARDS+THROAT
WATCH=[f'V23 cervical {course} directional guard {i}'for course in range(1,5)for i in range(1,11)]+THROAT
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def apply():
 records=[];centers={}
 for course in [4]:
  vertices=[bpy.data.objects[n].matrix_world@v.co for n in GUARDS if n.startswith(f'V23 cervical {course} ')for v in list(bpy.data.objects[n].data.vertices)[:399]];centers[course]=sum(vertices,Vector())/len(vertices)
 for course in [4]:
  for guard in range(1,11):
   name=f'V23 cervical {course} directional guard {guard}';o=bpy.data.objects[name];world=o.matrix_world.copy();inv=world.inverted();old=[v.co.copy()for v in o.data.vertices];source=[world@p for p in old];assert len(old)in[399,798];half=399
   def sample(row,col):
    row=max(0,min(20,row));col=max(0,min(18,col));i=min(int(row),19);j=min(int(col),17);a=row-i;b=col-j
    return source[i*19+j]*(1-a)*(1-b)+source[(i+1)*19+j]*a*(1-b)+source[i*19+j+1]*(1-a)*b+source[(i+1)*19+j+1]*a*b
   outer=[];target=(1.470 if guard in[1,2,3,4,5] else 1.457 if guard in[7,8,10] else 1.459);top=sum(p.z for p in source[:19])/19
   for row in range(21):
    free=smooth((18-row)/18)
    for col in range(19):
     u=col/18;direction=1 if guard%2 else-1;uc=.5+(u-.5)*(1-.05*free)+direction*.025*free
     q=sample(row,uc*18)
     if course==4:
      q.x=centers[course].x+(q.x-centers[course].x)*(1-.10*free);q.y=centers[course].y+(q.y-centers[course].y)*(1-.10*free)
      # Uneven continuous short throat/nape ends, diagonal course direction;
      # receiving root strips stay exact rather than translating a collar.
      q.z+=(target-top+direction*.012*(u-.5)-.004*math.sin(math.pi*u))*free
     else:
      q.z+=(-.007 if course==1 else-.003 if course==2 else.004)*free+direction*.012*(u-.5)*free
      q.x=centers[course].x+(q.x-centers[course].x)*(1-.045*free);q.y=centers[course].y+(q.y-centers[course].y)*(1-.045*free)
     outer.append(q)
   radial=sum(outer,Vector())/399-centers[course];radial.z=0;radial.normalize();inner=[]
   for row in range(21):
    free=smooth((18-row)/18)
    for col in range(19):
     i=row*19+col
     if len(old)==798:
      source_stock=source[i+399]-source[i];stock=source_stock*(1-free)+(-radial*.0035)*free
     else:stock=-radial*.0035
     assert stock.length>.001;inner.append(outer[i]+stock)
   faces=[];capfaces=[]
   for row in range(20):
    for col in range(18):
     k=row*19+col;capfaces.append((k,k+1,k+20,k+19))
   faces=capfaces+[tuple(399+i for i in reversed(f))for f in capfaces];border=list(range(19))+[row*19+18 for row in range(1,21)]+[380+col for col in range(17,-1,-1)]+[row*19 for row in range(19,0,-1)]
   for i,k in enumerate(border):q=border[(i+1)%len(border)];faces.append((q,k,399+k,399+q))
   mesh=bpy.data.meshes.new(name+' reconstructed short swept rigid course');mesh.from_pydata([inv@p for p in outer+inner],[],faces);mesh.update()
   for mat in o.data.materials:mesh.materials.append(mat)
   o.data=mesh;o.modifiers.clear();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges)
   if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
   volume=bm.calc_volume(signed=True);assert volume>0;bm.to_mesh(mesh);bm.free()
   for i,f in enumerate(mesh.polygons):f.use_smooth=i<720
   rootindices=list(range(18*19,399));error=max((mesh.vertices[i].co-old[i]).length for i in rootindices);assert error<1e-7
   if len(old)==798:assert max((mesh.vertices[i+399].co-old[i+399]).length for i in rootindices)<1e-7
   o['v38CervicalGuards']='Source articulated owner/root band; compact staggered diagonal rigid guard, no collar/node bridge'
   records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'materials':[m.name if m else None for m in o.data.materials],'sourceOuterRows18to20Preserved':True,'sourceExplicitInnerRows18to20Preserved':len(old)==798,'sourceRootMaxErrorM':error,'finiteStock':'3.5mm constant fitted lateral extrusion on freeplate, blending exact uppercourse source rootstock; projected normal thickness separately unproven','closedEdgeManifold':True,'positiveVolumeM3':volume,'rootAttachment':'Actual source receiving band retained, owner link/race/pin frame exact; no complete source fastener/land interface acceptance inferred from parenting.'})
 for name in THROAT:
  o=bpy.data.objects[name];world=o.matrix_world.copy();inv=world.inverted();old=[v.co.copy()for v in o.data.vertices];source=[world@p for p in old];assert len(old)==990,(name,len(old));half=495
  o.data=o.data.copy();maximum=0
  for i in range(half):
   row=i//15;col=i%15;free=smooth((29-row)/29);p=source[i];q=p.copy()
   # Upper four rows remain the original head-side receiving band.
   # Lower free mouth of collar rises and draws toward the existing load bow,
   # removing projecting skirt rather than replacing it with a taller neck cuff.
   q.x*=1-.18*free;q.y=-.323+(q.y+.323)*(1-.13*free)
   q.z+=.016*free-.006*free*math.sin(math.pi*col/14)
   delta=q-p;maximum=max(maximum,delta.length)
   o.data.vertices[i].co=inv@q;o.data.vertices[i+half].co=inv@(source[i+half]+delta)
  o.data.update();assert all((o.data.vertices[i].co-old[i]).length<1e-7 for i in list(range(29*15,495))+list(range(495+29*15,990)))
  o['v38CervicalGuards']='Head-owned source receiving upper band/stock retained; short inboard oblique throat skirt, no cervical joint bridge'
  records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'materials':[m.name if m else None for m in o.data.materials],'upperRows29to32BothSkinsExact':True,'allSourcePairedStockVectorsRetained':True,'maximumDisplacementM':maximum,'attachment':'Actual source upper receiving strip unchanged; finite support/neighbor interface remains diagnostic, no parenting-only support PASS.'})
 return {'changedMeshes':NAMES,'watchMeshes':WATCH,'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'attachmentAndEraMap':records,'confirmation':'Master03/Maker-clean curved shortneck/throat flow; JulyHEADONLY/immediate throat only.','reconstruction':'28 existing: upper10 guards and18 head-owned throat skirts; lower30 guards exact, retained full coverage; exact unseen finite stock and overlap are proposals.','protected':'All4joint axes/rest/controlendpoints, actual bill/jaw/socket/optic/crown/body/wing asymmetry/materialprofiles sourceexact.','limits':['No continuous rigid motion, containment, engineering or ownerlikeness approval; source receiving bands retained, actual adjacent sevenpose screen follows visuals.','Sourceguard4/10 rootrows19/20 cols6..14+pairedinner retained exactly.','No new auxiliary covers, ownerbridge, exposed hardware hiding or solidneck cuff.']}
