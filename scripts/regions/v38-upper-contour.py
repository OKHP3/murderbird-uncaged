"""Upper-contour02: continuous upper-body contour proposal from pinned bill-relationship02.
Four genuine articulated frames remain; small rest translation revision, rigid joints and refitted links.
"""
import bpy,json,math
from mathutils import Vector
CHAIN=['neck','cervical-mid-a','cervical-mid-b','cervical-upper','head']
COLLAR=[f'V33 tapered throat cheek plate {s} {r} {i}'for s in(-1,0,1)for r in(0,1)for i in range(3)]
BREAST=[f'V34 formed breast course {c} plate {i}'for c,n in[(1,5),(2,6)]for i in range(1,n+1)]+['V30 continuous tapered breast liner']+[f'V30 breast liner receiving tab {s}'for s in(-1,1)]
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def apply():
 bpy.context.view_layer.update();world={o.name:o.matrix_world.copy()for o in bpy.data.objects};local={o.name:o.matrix_local.copy()for o in bpy.data.objects};changed=[];records=[];frames=[]
 knots=[(1.215,0.,0.),(1.2735,-.005,-.008),(1.3281,-.014,-.017),(1.3827,-.018,-.027),(1.423884,-.018,-.035)]
 def pathdelta(z):
  if z<=knots[0][0]:return Vector((0,0,0))
  for (a,y0,z0),(b,y1,z1)in zip(knots,knots[1:]):
   if z<=b:
    t=(z-a)/(b-a);return Vector((0,y0+(y1-y0)*t,z0+(z1-z0)*t))
  return Vector((0,-.018,-.035))
 def neckfield(p,guard=False):
  q=p+pathdelta(p.z)
  if guard:
   # Sustained convex anterior line, with little lateral expansion and open side-joint strip.
   w=math.exp(-((p.z-1.305)/.105)**2);cy=-.188-.65*(p.z-1.215);anterior=smooth((cy-p.y)/.09)
   q.y-=.012*w*anterior;q.x*=1+.040*w*anterior
  return q
 neckmeshes=[o for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name in CHAIN[:4]]
 points={o.name:[world[o.name]@v.co for v in o.data.vertices]for o in neckmeshes+[bpy.data.objects[n]for n in COLLAR+BREAST]}
 for name in CHAIN:
  o=bpy.data.objects[name];m=world[name].copy();m.translation+=pathdelta(m.translation.z);o.matrix_world=m;bpy.context.view_layer.update()
  frames.append({'name':name,'sourceWorldTranslation':list(world[name].translation),'candidateWorldTranslation':list(o.matrix_world.translation),'sourceLocalTranslation':list(local[name].translation),'candidateLocalTranslation':list(o.matrix_local.translation),'rotationAxisAndOrientationExact':True})
 for o in neckmeshes:
  rigid=any(k in o.name for k in('captive pin','distal race','root captive shaft'))
  if rigid:
   if 'distal race' in o.name:
    idx=int(o.name.split()[2]);target=CHAIN[idx];m=world[o.name].copy();m.translation+=pathdelta(world[target].translation.z);o.matrix_world=m;bpy.context.view_layer.update()
   records.append({'name':o.name,'role':'Rigid unchanged journal/shaft geometry at actual revised joint center','meshGeometryExact':True})
  else:
   inv=o.matrix_world.inverted();src=points[o.name];guard='directional guard' in o.name
   for v,p in zip(o.data.vertices,src):v.co=inv@neckfield(p,guard)
   o.data.update();changed.append(o.name);records.append({'name':o.name,'role':'Refitted rigid load link between revised joint centers'if not guard else'Existing directional guard follows revised curve, independent owner retained','owner':o.parent.name,'maxWorldVertexDisplacementM':max((neckfield(p,guard)-p).length for p in src)})
 # Replace18 legacy folded collar solids with actual bow-rooted finite directional plates.
 import bmesh
 collarSeats=[]
 for name in COLLAR:
  o=bpy.data.objects[name];oldmaterial=list(o.data.materials);parts=name.split();side,row,course=map(int,parts[-3:]);supportside=side if side else(-1 if row==0 else 1);bow=bpy.data.objects[f'V31 passive cranial load bow {supportside}'];bow.data.calc_loop_triangles();bv=[bow.matrix_world@v.co for v in bow.data.vertices];start=[26,31,36][course];nu,nv=16,6;inn=[];out=[];mapping={}
  root=[bv[start*11+2+j]for j in range(7)];center=sum(root,Vector())/7;top=center.z-.004
  if side==0:angle0,angle1=.035,1.36
  elif row==0:angle0,angle1=1.12,1.83
  else:angle0,angle1=1.65,2.31
  height=[.076,.072,.066][course];rx=[.111,.122,.126][course];ry=[.090,.084,.079][course];cy=-.381
  direction=Vector((supportside*.80,-.60,0));wall=.003
  def face(u,t):
   theta=angle0+(angle1-angle0)*u;radiusx=rx-.012*t;radiusy=ry-.006*t;z=top-height*t-.009*t*u+.004*math.sin(math.pi*u)*(1-t)
   return Vector((supportside*radiusx*math.sin(theta),cy-radiusy*math.cos(theta)+.013*t,z))
  for i in range(nu+1):
   for j in range(7):
    u=j/6
    if i<=2:src=(start+2-i)*11+2+j;q=bv[src].copy();mapping[src]=i*7+j
    elif i<=5:
     t=(i-2)/3;q=root[j]*(1-t)+face(u,0)*t
    else:q=face(u,(i-5)/(nu-5))
    inn.append(q);out.append(q+direction*wall)
  n=len(inn);faces=[];seat=[]
  for tri in bow.data.loop_triangles:
   if all(k in mapping for k in tri.vertices):
    f=tuple(mapping[k]for k in tri.vertices);faces.extend([f,tuple(n+k for k in reversed(f))]);seat.append({'receiverTriangle':tri.index,'sourceIndices':list(tri.vertices),'plateInnerIndices':[n+k for k in f]})
  assert len(seat)==24
  for i in range(2,nu):
   for j in range(6):k=i*7+j;l=k+7;faces.extend([(k,k+1,l+1),(k,l+1,l),(n+k,n+l+1,n+k+1),(n+k,n+l,n+l+1)])
  border=list(range(7))+[i*7+6 for i in range(1,nu+1)]+[nu*7+j for j in range(5,-1,-1)]+[i*7 for i in range(nu-1,0,-1)]
  for i,k in enumerate(border):q=border[(i+1)%len(border)];faces.append((k,q,n+q,n+k))
  mesh=bpy.data.meshes.new(name+' reconstructed compact oblique finite collar');inv=o.matrix_world.inverted();mesh.from_pydata([inv@p for p in out+inn],[],faces);mesh.update()
  for mat in oldmaterial:mesh.materials.append(mat)
  o.data=mesh;bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  volume=bm.calc_volume(signed=True);assert volume>0;bm.to_mesh(mesh);bm.free()
  for p in mesh.polygons:p.use_smooth=False
  o['v38UpperContour']='Actual bowed finite root and short independent down/back plate envelope; source legacy topology replaced'
  changed.append(name);records.append({'name':name,'owner':'head','role':'Fresh finite short staggered oblique plate with connected compact root return','vertices':len(mesh.vertices),'closedEdgeManifold':True,'positiveVolumeM3':volume,'stockVectorWorld':list(direction*wall),'receiver':bow.name,'receivingPatchActualRows':[start,start+2],'receivingPatchActualColumns':[2,8],'rootActualTriangleCorrespondence':seat,'supportState':'Full actual copied24-triangle receiving surface, outgoing root return/laps still independently require strict screen; not parentage PASS'})
  collarSeats.append({'plate':name,'receiver':bow.name,'triangles':seat})
 def breastfield(p):
  t=smooth((p.z-1.09)/.155);q=p.copy();q.z+=.020*t;q.y-=.007*t*max(0,1-abs(p.x)/.28);q.x*=1-.020*t;return q
 for name in BREAST:
  o=bpy.data.objects[name];inv=o.matrix_world.inverted();src=points[name];new=[]
  for i,p in enumerate(src):
   q=p if 'receiving tab'in name and i<8 else breastfield(p);new.append(q);o.data.vertices[i].co=inv@q
  o.data.update()
  if max((p-q).length for p,q in zip(src,new))>1e-7:changed.append(name);records.append({'name':name,'owner':'breastplate','role':'Only upper envelope aboveZ1.09 rises into neck; lower barrel and real return-side tab vertices exact','maxWorldVertexDisplacementM':max((p-q).length for p,q in zip(src,new))})
 # Update authored owner-local runtime attachment points through the same geometry field.
 body=bpy.data.objects['body'];layout=json.loads(body['mechanismLayoutV1']);endpoint=[]
 def native(q):return Vector((q[0],-q[2],q[1]))
 def gltf(q):return [q.x,q.z,-q.y]
 oldneck=world['neck'];newneck=bpy.data.objects['neck'].matrix_world
 for e in layout['cervical']:
  p=oldneck@native(e['neckPoint']);mapped=neckfield(p);old=e['neckPoint'];e['neckPoint']=gltf(newneck.inverted()@mapped);endpoint.append({'role':'Builder cervical','side':e['side'],'sourceNeckLocalGltf':old,'candidateNeckLocalGltf':e['neckPoint'],'sourceWorld':list(p),'candidateWorld':list(mapped),'bodyPointExact':e['bodyPoint'],'surfaceFit':'Common field follows original receiving point; actual finite nearest-face proof still required, not marker-only attachment PASS'})
 old=layout['makerControlOffsets']['neck'];p=oldneck@native(old);mapped=neckfield(p);layout['makerControlOffsets']['neck']=gltf(newneck.inverted()@mapped);endpoint.append({'role':'Maker neck external control','sourceLocalGltf':old,'candidateLocalGltf':layout['makerControlOffsets']['neck'],'sourceWorld':list(p),'candidateWorld':list(mapped)})
 layout['source']='Upper-contour02 authored four-center loadpath and receiving-point field from actual bill-relationship02; exact finite seat/clearance not yet accepted';body['mechanismLayoutV1']=json.dumps(layout,separators=(',',':'))
 bpy.context.view_layer.update();nodes=[n for n in world if bpy.data.objects[n].matrix_world!=world[n] or bpy.data.objects[n].matrix_local!=local[n]];nodes.append('body')
 return {'changedMeshes':sorted(set(changed)),'changedNodes':sorted(set(nodes)),'addedMeshes':[],'removedMeshes':[],'watchMeshes':sorted(set(changed)),'attachmentAndEraMap':records,'collarFiniteSeatCorrespondence':collarSeats,'revisedJointFrames':frames,'runtimeAttachmentEndpoints':endpoint,'geometryControls':{'headWorldShiftM':[0,-.018,-.035],'upperBreastZLiftM':.020,'upperBreastAnteriorShiftM':.007,'lowerBreastExactBelowZ':1.09,'lowerNeckAnteriorCurveReliefM':.012},'construction':'Retained four articulated joints and rigid journal geometry; continuous shorter S-curve refits load members, guard coverage and upper breast rather than adding a cuff. Head identity local geometry exact except declared18 throat plates.','inspection':'Breastplate pivot/localX+1.1 and actual return-side seats unchanged; upper receiving mismatch including existing16.25mm warning remains unvalidated, not a fit PASS.','protected':'All unrelated body/wing/leg/head identity geometry, era finish profiles and hierarchy remain exact. Head branch rest-position changes are declared, not disguised exclusions.','limits':['Source collar topology remains inherited and may retain folded surfaces; visual gate precedes expanded diagnostics.','Runtime points track common geometry field but exact finite attachment/posed clearance remains unproved.','No owner likeness, continuous motion, load/fabrication or release acceptance.']}
