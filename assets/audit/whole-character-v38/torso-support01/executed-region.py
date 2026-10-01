"""First torso exterior protected; targeted passive internal/frame and neckbase reconciliation."""
import bpy,bmesh,json,math,runpy,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
LINER='V30 continuous tapered breast liner'
PLATES=[f'V34 formed breast course {r} plate {c}'for r,n in enumerate([5,6,7,6,5,4],1)for c in range(1,n+1)]
def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
def components(mesh):
 links=[set()for _ in mesh.vertices]
 for e in mesh.edges:a,b=e.vertices;links[a].add(b);links[b].add(a)
 unseen=set(range(len(links)));sizes=[]
 while unseen:
  todo=[unseen.pop()];size=0
  while todo:
   i=todo.pop();size+=1
   for j in links[i]&unseen:unseen.remove(j);todo.append(j)
  sizes.append(size)
 return sorted(sizes,reverse=True)
def stat(o):
 bm=bmesh.new();bm.from_mesh(o.data);r={'components':components(o.data),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'signedVolumeM3':bm.calc_volume(signed=True)};bm.free();return r

def tree(o):
 o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(t.vertices)for t in o.data.loop_triangles],all_triangles=True,epsilon=0)
def annotate(o,text):
 hist={k:json.loads(json.dumps(v,default=lambda x:list(x)))for k,v in o.items()if k in('constructionDescription','geometryStatus','wallM','railEndpointWorld','authoringRole','fixedJoinedReceivers','joiningProposal')or k.endswith('Revision')};o['historyBeforeTorsoSupport01']=json.dumps(hist,separators=(',',':'));o['constructionDescription']=text;o['geometryStatus']='Torso-support01 finite passive construction proposal; attachment fit and owner acceptance unresolved';o['torsoSupportRevision']='torso-support01'
 for k in('courseIndex','courseTopM','courseBottomM','panelKind','lateralSpanRadians'):
  if k in o and ('rail' in o.name or 'fork' in o.name):del o[k]

def apply():
 bpy.context.view_layer.update();changed=[];records=[];seats=[];lib=runpy.run_path(str(ROOT/'assets/audit/whole-character-v38/torso-coherent01/executed-region.py'));sourceReceivers=[]
 # Actual source frame surfaces remain datum stock; individual support free
 # transitions can change while real seat footprints are kept byte-exact.
 for side in(-1,1):
  targets=[f'V24 rising thoracic receiving cheek {side}',f'V35 lateral thoracic bay load rail {side}',f'V35 oblique thoracic side guard {side} 0',f'V35 scapular receiving plate {side} 0',f'V23 root load fork {side}']
  sources=[n for n in[f'V23 thoracic formed rib {side}',f'V24 shoulder lower load fork {side}',f'V35 posterior bay load rail {side}']if n in bpy.data.objects];trees={n:tree(bpy.data.objects[n])for n in sources}
  for name in targets:
   o=bpy.data.objects[name];world=o.matrix_world.copy();original=[v.co.copy()for v in o.data.vertices];pts=[world@p for p in original];before=stat(o);protected={i for i,p in enumerate(pts)if p.y>=-.16};actualSeats={}
   for n,t in trees.items():
    ix=[i for i,p in enumerate(pts)if t.find_nearest(p)[3]<.0015];actualSeats[n]=ix;protected.update(ix)
   if 'bay load rail' in name:protected.update(i for i,p in enumerate(pts)if p.z>=1.145 or p.z<=.936)
   o.data=o.data.copy();inv=world.inverted();moves=[]
   for i,p in enumerate(pts):
    if i in protected:d=Vector()
    else:
     if 'bay load rail' in name:w=ease((1.145-p.z)/.045)*ease((p.z-.936)/.055)
     else:w=ease((-.16-p.y)/.060)
     d=Vector((0,.078*w,0))
    
    if d.length:o.data.vertices[i].co=inv@(p+d)
    moves.append(d.length)
   o.data.update();assert all(o.data.vertices[i].co==original[i]for i in protected);after=stat(o);assert after['nonManifoldEdges']==0 and after['signedVolumeM3']>0;changed.append(name)
   annotate(o,'Body-owned passive receiving/frame member: anterior free transition reconstructed posteriorly into retained torso envelope; actual original rib/shoulder/posterior-rail near-seat stock and rail terminal sections listed exact. No new moving-owner bridge, pivot or shoulder change; continuous cap seat/load still qualified.')
   landmarks=[]
   for n,ix in actualSeats.items():
    faces=[p for p in o.data.polygons if all(j in protected for j in p.vertices)and any(j in ix for j in p.vertices)];landmarks.append({'source':n,'sourceNearSeatVertices':len(ix),'protectedFaceCount':len(faces),'actualProtectedFacePatches':[{'vertexIndices':list(p.vertices),'worldPoints':[list(world@o.data.vertices[j].co)for j in p.vertices]}for p in faces[:2]],'allProtectedLocalVerticesExact':True,'limits':'Existing source proximity footprint preserved, not independently confirmed mating-cap union or load acceptance.'})
   records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'maximumFreeTransitionDeltaM':max(moves),'protectedVertices':len(protected),'beforeStock':before,'afterStock':after,'actualSourceAttachmentPatches':landmarks})
 # Preserve actual hinge first4 rings and terminal2 rings; only C-return
 # midspan moves back inside the new lower plate envelope.
 for side in(-1,1):
  o=bpy.data.objects[f'V23 breast moving return {side}'];original=[v.co.copy()for v in o.data.vertices];world=[o.matrix_world@p for p in original];o.data=o.data.copy();inv=o.matrix_world.inverted()
  for i,p in enumerate(world):
   if i<32 or i>=232:continue
   w=ease((p.z-.70)/.08)*(1-ease((p.z-.86)/.08));o.data.vertices[i].co=inv@(p+Vector((0,.030*w,0)))
  o.data.update();assert all(o.data.vertices[i].co==original[i]for i in list(range(32))+list(range(232,248)));annotate(o,'Breast-owned source C-return hinge rings0–3 and terminal rings29–30 exact; intervening passive span refitted posteriorly up to30mm to retain lower plate clearance. No pivot or terminal receiving coordinate change.');changed.append(o.name);records.append({'name':o.name,'owner':'breastplate','hingeFirst32AndTerminal16VerticesExact':True,'stock':stat(o)})
 # Replace wide old integral C receivers, not the first outer plate field.
 liner=bpy.data.objects[LINER];old=liner.get('integralPassiveReceivers');vv,ff=lib['solid'](lambda u,v:lib['point'](.685+(1.248-.685)*u,lib['ANGLE']*(2*v-1)),72,52,.004);lib['install'](liner,vv,ff,'first exact analytic exterior with new internal flat landings');outer=tree(liner);joins=[]
 for side in(-1,1):
  ret=bpy.data.objects[f'V23 breast moving return {side}'];p=[ret.matrix_world@v.co for v in ret.data.vertices];seat=sum((p[240+j]for j in(0,1,4,5)),Vector())/4;near=outer.find_nearest(seat);direction=(near[0]-seat).normalized();choices=[]
  for j in range(8):
   ids=[232+j,232+(j+1)%8,240+(j+1)%8,240+j];q=[p[i]for i in ids];n=(q[1]-q[0]).cross(q[3]-q[0]).normalized();area=(q[1]-q[0]).cross(q[3]-q[0]).length
   if n.dot(direction)>.15:choices.append((area*n.dot(direction),ids,q))
  _,ids,q=max(choices,key=lambda x:x[0]);span=.004/(((q[3]-q[0]).length+(q[2]-q[1]).length)*.5);span=min(span,.65);root=[q[0].lerp(q[3],.72-span*.5),q[1].lerp(q[2],.72-span*.5),q[1].lerp(q[2],.72+span*.5),q[0].lerp(q[3],.72+span*.5)];ends=[];endtris=[]
  for c in root:
   h=outer.ray_cast(c+direction*.8,-direction,1.2);assert h[0]is not None;ends.append(h[0]-h[1]*.002);endtris.append(h[2])
  verts=root+ends;faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];m=bpy.data.meshes.new('finite flat return receiver');m.from_pydata([liner.matrix_world.inverted()@p for p in verts],[],faces);m.update();frame=liner.data.materials[-1];m.materials.append(frame);temp=bpy.data.objects.new('temporary actual flat landing',m);bpy.context.scene.collection.objects.link(temp);temp.matrix_world=liner.matrix_world.copy();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  bm.to_mesh(m);bm.free();oldmesh=liner.data.copy();before=stat(liner);mod=liner.modifiers.new('Single flat return receiving union','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=temp
  with bpy.context.temp_override(object=liner,active_object=liner,selected_objects=[liner],selected_editable_objects=[liner]):bpy.ops.object.modifier_apply(modifier=mod.name)
  after=stat(liner);ok=after['nonManifoldEdges']==0 and after['signedVolumeM3']>0 and len(after['components'])==1
  assert ok,'Actual receiver union not one connected closed stock';bpy.data.objects.remove(temp,do_unlink=True);joins.append({'side':side,'sourceReturn':ret.name,'sourceRearWebFaceVertexIndices':ids,'actualSourceRootPatchWorld':[list(x)for x in root],'actualTerminalPatchWorld':[list(x)for x in ends],'terminalActualOuterTriangles':endtris,'terminalOuterWallEmbedM':.002,'beforeComponents':before['components'],'afterComponents':after['components'],'oneBooleanUnionAttempt':True,'connectedManifoldPositive':ok,'qualification':'Complete root/end corner loops, not continuous between-corner seating or welded-load certificate.'})
 annotate(liner,'First continuous analytic torso outer shell recreated with actual finite flat rearweb receiving bridges; all33 exterior plate meshes protected. Two one-shot unions each one connected manifold stock; cap triangulation/fit remains qualified.');liner['integralPassiveReceivers']=json.dumps(joins,separators=(',',':'));liner['previousIntegralReceiverHistory']=old or 'unknown';changed.append(LINER)
 # Articulated lowest guard free laps follow outside the preserved first
 # breast skins. Root20mm / original owner/shaft remains exact.
 skinTrees=[tree(bpy.data.objects[n])for n in PLATES[:5]];guardRecords=[]
 for g in range(1,6):
  o=bpy.data.objects[f'V23 cervical 1 directional guard {g}'];original=[v.co.copy()for v in o.data.vertices];pts=[o.matrix_world@p for p in original];inv=o.matrix_world.inverted();o.data=o.data.copy();protected=[];deltas=[]
  for i,p in enumerate(pts):
   w=1-ease((p.z-1.238)/.027)
   if p.z>=1.265:protected.append(i);continue
   x=abs(p.x);rx=lib['component'](p.z,1);ry=lib['component'](p.z,2);front=-.08-ry*math.sqrt(max(.08,1-min(.98,x/rx)**2))-.012;d=min(0,front-p.y)*w;o.data.vertices[i].co=inv@(p+Vector((0,d,0)));deltas.append(abs(d))
  o.data.update();assert all(o.data.vertices[i].co==original[i]for i in protected);annotate(o,'Lowest neck-owner rigid free lap reconstructed forward over preserved breast shoulder curve; upper rootZ>=1.265, captive shaft/joint owner/rest exact.12mm intended radial sector relief, not a sampled swept-fit certificate.');changed.append(o.name);guardRecords.append({'name':o.name,'owner':'neck','protectedUpperRootVertices':len(protected),'maximumFreeLapDeltaM':max(deltas),'stock':stat(o)})
 # Replace two failed broad fan yokes with explicit compact owner-local
 # frame-to-guard finite hexahedral landings, using genuine source quads.
 for side in(-1,1):
  o=bpy.data.objects[f'V38 curved-neck formed yoke neck {side}'];frame=bpy.data.objects[f'V23 cervical 1 load link {side}'];guard=bpy.data.objects[f'V23 cervical 1 directional guard {1 if side<0 else 5}'];frameWorld=[frame.matrix_world@v.co for v in frame.data.vertices];target=[guard.matrix_world@guard.data.vertices[i].co for i in(475+19+8,475+19+9,475+38+9,475+38+8)];center=sum(target,Vector())/4;quads=[p for p in frame.data.polygons if len(p.vertices)==4];face=min(quads,key=lambda p:(sum((frameWorld[i]for i in p.vertices),Vector())/4-center).length);root=[frameWorld[i]for i in face.vertices];v=root+target;f=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];lib['install'](o,v,f,'compact finite neckbase frame landing');annotate(o,'Compact neck-owner passive finite landing from one actual original cervical loadlink quad to one actual upper guard inner quad; no wide fan and no rigid body/neck bridge. Root/end cap corner loops are actual stock; mating triangulation/sweep/physical support unresolved.');changed.append(o.name);seats.append({'name':o.name,'owner':'neck','sourceFrame':frame.name,'actualSourceFaceIndex':face.index,'actualRootVertexIndices':list(face.vertices),'actualRootLoopWorld':[list(x)for x in root],'actualGuardInnerVertexIndices':[475+19+8,475+19+9,475+38+9,475+38+8],'actualEndLoopWorld':[list(x)for x in target],'sameOwnerFrameGuard':frame.parent==o.parent==guard.parent,'stock':stat(o),'limits':'Two actual finite cap corner loops, not continuous-area seat/load certification.'})
 return {'changedMeshes':changed,'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'watchMeshes':changed+PLATES[:5]+PLATES[-4:],'bodySupportStock':records,'breastReceiverUnions':joins,'lowestGuardFreeLaps':guardRecords,'compactNeckYokeLandings':seats,'construction':'First whole breast exterior/33 plate meshes protected; internal/frame passive receiving transitions, exact hinge/end return rings, flat connected receiving landings and local articulated neckbase laps/yokes.','protected':'All33 breastplate geometry/metadata/rest/owners/materials exact; all pivots/head/bill/jaw/optic/crown/other neckcourses/wing/leg/foot stock/rest/hierarchy/material definitions/era profiles unchanged.','limits':['Existing body-source near-seat vertices are preserved, not upgraded to independently verified true face-to-face load seats.','New flat integral unions count one connected manifold stock; source/end cap contact and finite swept fit remain qualified.','Lowest guard forming retains upper roots but nominal stock after forming requires actual finite diagnostics; no texture/material finishing.','Source pelvic/lower sternal interfaces remain unchanged and may still intersect backing; no blanket whole-body fit claim.','Actual pitch stress is a captured neck pitch slice at body rest, not complete strike animation.','No engineering, full three-era likeness or owner acceptance.']}
