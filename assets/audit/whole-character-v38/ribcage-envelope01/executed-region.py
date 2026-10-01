"""Deep lower oval body; continuous stock plus actual liner/return receiving refit."""
import bpy,bmesh,math,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
LINER='V30 continuous tapered breast liner'
PLATES=[f'V34 formed breast course {r} plate {c}'for r,n in[(1,5),(2,6),(3,7),(4,6),(5,5),(6,4)]for c in range(1,n+1)]
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def weight(z):
 keys=[(.70,0),(.78,.38),(.88,.91),(.96,1),(1.04,.70),(1.12,.28),(1.185,0)]
 if z<keys[0][0]or z>keys[-1][0]:return 0
 for a,b in zip(keys,keys[1:]):
  if z<=b[0]:t=ease((z-a[0])/(b[0]-a[0]));return a[1]*(1-t)+b[1]*t
 return 0

def field(p):
 q=p.copy();w=weight(p.z);q.y-=.055*w*ease((-p.y-.055)/.14);q.x*=1+.06*w*ease((abs(p.x)-.12)/.09);return q

def tree(o,inner=False):
 o.data.calc_loop_triangles();v=[o.matrix_world@p.co for p in o.data.vertices];f=[]
 for t in o.data.loop_triangles:
  tri=tuple(t.vertices);normal=(v[tri[1]]-v[tri[0]]).cross(v[tri[2]]-v[tri[0]]);center=sum((v[i]for i in tri),Vector())/3
  if not inner or(normal.y>.00000001 and center.y<-.20 and .86<center.z<1.09):f.append(tri)
 assert f;return BVHTree.FromPolygons(v,f,all_triangles=True,epsilon=0)

def measure(o):
 v=[o.matrix_world@p.co for p in o.data.vertices];return {'worldBoundsM':[[min(p[i]for p in v),max(p[i]for p in v)]for i in range(3)],'actualModelSections':[{'z':z,'samples':len(q),'widthM':max(p.x for p in q)-min(p.x for p in q),'frontY':min(p.y for p in q)}for z in(.75,.85,.95,1.05,1.15)if(q:=[p for p in v if abs(p.z-z)<.012])]}
def stock(o):
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),o.name
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 vol=bm.calc_volume(signed=True);assert vol>0;bm.to_mesh(o.data);bm.free();return vol

def annotate(o,role):
 old={k:json.loads(json.dumps(o[k],default=lambda x:list(x)))for k in list(o.keys())if k.startswith(('lowerSupport','breastSupport','v38'))or k in('constructionDescription','geometryStatus','railEndpointWorld','wallM','jointCentersWorld')}
 o['constructionHistoryBeforeRibcageEnvelope01']=json.dumps(old,separators=(',',':'))
 for k in old:
  if k.startswith(('lowerSupport','breastSupport','v38')):del o[k]
 o['constructionDescription']=role;o['geometryStatus']='Ribcage-envelope01 authored passive oval body/receiving refit; finite samples and owner acceptance unresolved';o['ribcageEnvelopeRevision']='ribcage-envelope01'

def load_tab(points):
 w=.018;d=.014;wall=.004;cross=[(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(w/2-wall,d/2),(w/2-wall,-d/2+wall),(-w/2+wall,-d/2+wall),(-w/2+wall,d/2),(-w/2,d/2)];v=[];f=[]
 for i,p in enumerate(points):
  axis=(points[min(i+1,2)]-points[max(i-1,0)]).normalized();b=axis.cross(Vector((1,0,0))).normalized();a=b.cross(axis).normalized();v.extend(p+a*x+b*y for x,y in cross)
 for i in range(2):
  for j in range(8):a=i*8+j;b=i*8+(j+1)%8;f.append((a,b,b+8,a+8))
 f.extend([tuple(reversed(range(8))),tuple(range(16,24))]);return v,f

def apply():
 bpy.context.view_layer.update();before=measure(bpy.data.objects[LINER]);changed=[];records=[];rootProof=[];oldLiner={};allnames=[]
 shell=[o for o in bpy.data.objects if o.type=='MESH'and(o.name in PLATES+[LINER,'V30 continuous dorsal pelvic liner']or o.name.startswith(('V35 oblique thoracic side guard ','V38 tapered pelvic return course ')))]
 for o in shell:
  old=[o.matrix_world@p.co for p in o.data.vertices];new=[field(p)for p in old];maximum=max((a-b).length for a,b in zip(old,new))
  if maximum<1e-7:continue
  o.data=o.data.copy();inv=o.matrix_world.inverted()
  for v,p in zip(o.data.vertices,new):v.co=inv@p
  o.data.update();vol=stock(o);annotate(o,'Existing directional rigid cover/backing follows deeper descending oval mid/lower torso; shoulder/top aboveZ1.185 and hip/hinge belowZ.70 exact; existing flank apertures/independent cover identity retained. Formed stock thickness and frame fit remain qualified.');changed.append(o.name);records.append({'name':o.name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'class':'inherited-passive','maxWorldDisplacementM':maximum,'volumeM3':vol,'sameSourceFaces':True})
 # Actual fixed-frame receiving footprints remain exact: thoracic C-member
 # endrings and finite neighboring forks/rails/cheeks receive these members.
 for side in(-1,1):
  o=bpy.data.objects[f'V23 thoracic formed rib {side}'];oldLocal=[v.co.copy()for v in o.data.vertices];old=[o.matrix_world@p for p in oldLocal];assert len(old)==248
  neighbors=[bpy.data.objects[n]for n in[f'V23 breast hinge fixed fork {side}',f'V35 lateral thoracic bay load rail {side}',f'V35 posterior bay load rail {side}',f'V24 rising thoracic receiving cheek {side}']];ts=[tree(n)for n in neighbors]
  protected={i for i,p in enumerate(old)if i<32 or i>=216 or min(t.find_nearest(p)[3]for t in ts)<.008};o.data=o.data.copy();inv=o.matrix_world.inverted()
  for i,v in enumerate(o.data.vertices):
   if i not in protected:v.co=inv@field(old[i])
  o.data.update();vol=stock(o);assert all(o.data.vertices[i].co==oldLocal[i]for i in protected);annotate(o,'Passive thoracic formed rib midspan follows lower oval support field; complete first/last4rings and actual8mm proximity footprints to named fixed fork/side rails/rising cheek exact. Stock interfaces not globally certified.');changed.append(o.name);rootProof.append({'name':o.name,'exactVertices':len(protected),'actualProtectedNeighbors':[n.name for n in neighbors],'sourceRootAndEndRingsExact':True});records.append({'name':o.name,'owner':'body','eras':o.get('exteriorEras'),'class':'inherited-passive','volumeM3':vol,'maxWorldDisplacementM':max((o.matrix_world@v.co-old[i]).length for i,v in enumerate(o.data.vertices))})
 bpy.context.view_layer.update();liner=bpy.data.objects[LINER];backing=tree(liner,True);refits=[]
 for side in(-1,1):
  o=bpy.data.objects[f'V23 breast moving return {side}'];oldLocal=[v.co.copy()for v in o.data.vertices];old=[o.matrix_world@p for p in oldLocal];assert len(old)==248;oldEnd=sum(old[240:248],Vector())/8
  endNear=backing.find_nearest(field(oldEnd)+Vector((0,.025,0)));assert endNear[0]is not None;target=endNear[0]+Vector((0,.024,0));formedEnd=field(oldEnd);delta=target-formedEnd;o.data=o.data.copy();inv=o.matrix_world.inverted()
  for i,v in enumerate(o.data.vertices):
   if i<32:continue
   t=(i//8-3)/27;v.co=inv@(field(old[i])+delta*ease(t))
  o.data.update();vol=stock(o);assert all(o.data.vertices[i].co==oldLocal[i]for i in range(32));seat=sum((o.matrix_world@o.data.vertices[240+j].co for j in(0,1,4,5)),Vector())/4;end=backing.find_nearest(seat)[0];assert (end-seat).length>.004
  annotate(o,'Original passive C-return hinge-end first4rings exact; free/midspan formed toward actual new inner-liner stock; end relocated and paired finite C receiving tab refit. Same opening owner, fixed hinge and annular bearing geometry unchanged; clear load route still requires finite screen.');o['railEndpointWorld']=[list(sum(old[:8],Vector())/8),list(sum((o.matrix_world@v.co for v in o.data.vertices[240:248]),Vector())/8)];changed.append(o.name);records.append({'name':o.name,'owner':'breastplate','eras':o.get('exteriorEras'),'class':'inherited-passive','volumeM3':vol})
  tab=bpy.data.objects[f'V30 breast liner receiving tab {side}'];vv,ff=load_tab([seat,seat.lerp(end,.5),end]);corners=[]
  # Actual terminal rear-web corners independently receive actual inner
  # finite triangles. Lip/channel stock stays behind that wall, not a marker.
  for j in(0,1,4,5):
   hit=backing.find_nearest(vv[16+j]);vv[16+j]=hit[0];corners.append({'terminalVertex':16+j,'actualInnerTriangle':hit[2],'surfaceDistanceM':backing.find_nearest(hit[0])[3]})
  mesh=bpy.data.meshes.new(tab.name+' finite actual inner-wall receiving C');mesh.from_pydata([tab.matrix_world.inverted()@p for p in vv],[],ff);mesh.update()
  for m in tab.data.materials:mesh.materials.append(m)
  tab.data=mesh;vol=stock(tab);annotate(tab,'Finite passive18mm width14mm depth4mm nominal wall C landing from actual retained return web to actual revised inner-liner triangle lands; four terminal web corners fitted to finite wall, interior section retains nominal stock. Coplanarity/between-corner seating, normal wall and structural union remain unresolved.');tab['wallM']=.004;tab['constructionClass']='inherited-passive';tab['actualReceivingRole']='Rigid return-to-inner-liner C landing; all3eras inherited passive; current actual endpoint samples below'
  for stale in('courseTopM','courseBottomM','courseIndex','lateralSpanRadians','panelKind'):
   if stale in tab:del tab[stale]
  tab['railEndpointWorld']=[list(seat),list(end)];changed.append(tab.name);records.append({'name':tab.name,'owner':'breastplate','eras':tab.get('exteriorEras'),'class':'inherited-passive','volumeM3':vol});refits.append({'return':o.name,'tab':tab.name,'hingeFirst32VerticesExact':True,'oldReturnEndCenterWorld':list(oldEnd),'newReturnEndCenterWorld':list(sum((o.matrix_world@v.co for v in o.data.vertices[240:248]),Vector())/8),'returnEndDeltaM':list(target-oldEnd),'actualReturnRearWebSeatWorld':list(seat),'actualNewInnerLinerSeatWorld':list(end),'innerLinerTriangle':backing.find_nearest(end)[2],'fourTerminalWebCornerSamples':corners,'scopeLimit':'Four finite corner samples, not whole cap seating/union/physical proof. Full tab/return/plate surface screen required.'})
 bpy.context.view_layer.update();return {'changedMeshes':sorted(changed),'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'watchMeshes':sorted(changed),'attachmentAndEraMap':records,'modelEnvelopeMeasurements':{'source':before,'candidate':measure(liner),'notReferenceDimensions':True},'controls':{'maximumAnteriorDepthGainM':.055,'maximumFlankWidthGainFraction':.06,'zWeightKeys':[[.70,0],[.78,.38],[.88,.91],[.96,1],[1.04,.70],[1.12,.28],[1.185,0]],'hipsHingeAndShoulderAboveOrBelowBoundsExact':True},'fixedThoracicRootProof':rootProof,'actualReturnAndTabRefits':refits,'construction':'Carry ribcage convex anterior mass through waist toward rounded pelvis, taper near actual hip mounts; existing independent directional cover courses and purposeful flank openings retained. Actual inner wall/return/tab seating reconstructed together, not only a common vector warp.','protected':'All original pivots/rest transforms/head/neck/jaw/bill/crown/optics/wings/hips/legs/feet/material profiles/era eligibility; hinge seats, bearing stock, sternal/hip bridges, named fixed fork and actual receiving footprints exact. All new work inherited passive all3eras.','limits':['Nominal C wall and paired cover stock after forming are qualified; no whole-solid fit or constant-normal thickness claim.','Finite terminal corner seating is not a manufactured weld/load or continuous clearance proof.','Inherited lower return/plate crossings and first curved-neck fans/seams remain unresolved; do not claim general validity.','No owner likeness approval, runtime change or broad engineering validation.']}
