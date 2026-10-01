"""Lower-support02: preserve compound receivers and functional ends; reinforce mids.
Native Z-up; every revised structure remains an inherited passive proposal.
"""
import bpy,bmesh,json,math,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
TRUSS=['Left metatarsus open passive truss','Right metatarsus open passive truss']
def signature(o):
 return hashlib.sha256(json.dumps({'verts':[list(v.co)for v in o.data.vertices],'edges':[list(e.vertices)for e in o.data.edges],'faces':[(list(p.vertices),p.material_index,p.use_smooth)for p in o.data.polygons],'mats':[m.name if m else None for m in o.data.materials]},sort_keys=True).encode()).hexdigest()
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def tree(o):
 o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(t.vertices)for t in o.data.loop_triangles],all_triangles=True,epsilon=0)
def inside(t,p):
 # Odd ray hits through actual finite surface; tiny advances distinguish exits.
 d=Vector((.397,.571,.718)).normalized();pos=p.copy();hits=0
 for _ in range(80):
  q,normal,index,dist=t.ray_cast(pos,d,10)
  if q is None:break
  hits+=1;pos=q+d*.0000003
 return bool(hits%2)
def volume_witness(rail,receiver):
 # Source source-box end cells. Sample actual rail volume near distal end;
 # receiver containment yields positive finite-volume witness cells, not fit certification.
 rv=[rail.matrix_world@v.co for v in rail.data.vertices[:8]];a=sum(rv[:4],Vector())/4;b=sum(rv[4:],Vector())/4;u=(rv[1]-rv[0])*.5;v=(rv[3]-rv[0])*.5;t=tree(receiver);w=[]
 for along in (.72,.82,.92,.98):
  for x in (-.7,0,.7):
   for y in (-.7,0,.7):
    p=a.lerp(b,along)+u*x+v*y
    if inside(t,p):w.append(list(p))
 return {'method':'36 actual source rail interior samples in distal28% against finite source compound receiver, parity ray epsilon0.3micrometre; points strictly inside both original retained rail stock and actual receiver indicate volumetric overlap, not a manufactured union or engineered fit','candidateReceiverInteriorWitnessCount':len(w),'witnessWorld':w,'sourceCapWorld':[list(p)for p in rv[4:]],'distalCapVertexToActualCompoundSurfaceM':[t.find_nearest(p)[3]for p in rv[4:]],'surfaceCrossingTrianglePairs':len(tree(rail).overlap(t))}
def apply():
 bpy.context.view_layer.update();protected={n:signature(bpy.data.objects[n])for n in TRUSS};changed=[];records=[];history={};stock=[]
 strap=bpy.data.objects['Power retaining strap'];strapTree=tree(strap);frameObjects=[o for o in bpy.data.objects if o.type=='MESH'and o.parent and o.parent.name=='body'and any(token in o.name.lower()for token in ('thoracic formed rib','sternal','hip receiving','hip load bow','pelvic formed load web','breast hinge','breast opening bearing','fixed joined posterior','posteriorstiffener','pelvic load'))];frameTrees=[tree(o)for o in frameObjects];hips=[bpy.data.objects[s+'-thigh'].matrix_world.translation.copy()for s in ('left','right')]
 def field(p):
  q=p.copy();w=smooth((p.z-.670)/.115)*(1-smooth((p.z-.91)/.20))
  for c in hips:w*=smooth(((p-c).length-.095)/.070)
  nearest=strapTree.find_nearest(p)
  if nearest[0]is not None:w*=smooth((nearest[3]-.025)/.045)
  # Actual finite source support surface distance protects source interfaces.
  # This is an explicit50mm source-nearest exclusion/50mm blend, not an
  # axis-aligned box or assumed joint marker. Triangle-level screen follows.
  nearestFrame=min(t.find_nearest(p)[3]for t in frameTrees)
  w*=smooth((nearestFrame-.050)/.050)
  q.x*=1-.18*w;q.y+=.050*w*smooth((-p.y-.02)/.17)-.032*w*smooth((p.y+.01)/.13);return q
 def annotation(o,description,endpoints=None):
  history[o.name]={k:json.loads(json.dumps(o[k],default=lambda v:list(v)))for k in ('constructionDescription','geometryStatus','railEndpointWorld','jointCentersWorld','footAssemblyRevision','proportionStudy','silhouetteRevision')if k in o}
  o['constructionHistoryBeforeLowerSupport02']=json.dumps(history[o.name],separators=(',',':'));o['constructionDescription']=description;o['geometryStatus']='Lower-support02 inferred passive reinforcement/taper; finite receiver stock retained; fabrication and continuous travel not validated';o['lowerSupportRevision']='lower-support02'
  if endpoints is not None:o['railEndpointWorld']=endpoints
  if 'footAssemblyRevision'in o:o['footAssemblyRevision']='lower-support02 source-end-preserving member reinforcement'
  if 'proportionStudy'in o:o['proportionStudy']='lower-support02 current unchanged joint centers; source labels in constructionHistoryBeforeLowerSupport02'
  if 'silhouetteRevision'in o:o['silhouetteRevision']='lower-support02 bounded midspan reinforcement, named rests unchanged'
  if 'jointCentersWorld'in o:
   side='left'if'left'in o.name.lower()else'right';kind='thigh'if'thigh'in o.name else'foot';distal='shin'if kind=='thigh'else'toes';o['jointCentersWorld']=[list(bpy.data.objects[side+'-'+kind].matrix_world.translation),list(bpy.data.objects[side+'-'+distal].matrix_world.translation)]
 skins=[o for o in bpy.data.objects if o.type=='MESH'and(o.name.startswith(('V34 formed breast course ','V35 oblique thoracic side guard ','V35 compact dorsal return ','V38 tapered pelvic return course '))or o.name in ('V30 continuous tapered breast liner','V30 continuous dorsal pelvic liner'))]
 for o in skins:
  src=[o.matrix_world@v.co for v in o.data.vertices];dst=[field(p)for p in src];disp=max((p-q).length for p,q in zip(src,dst))
  if disp>1e-7:
   inv=o.matrix_world.inverted()
   for v,q in zip(o.data.vertices,dst):v.co=inv@q
   o.data.update();annotation(o,'Rigid lower torso cover/backing shaped by common tapered field, exact source hip/hinge strip, actual Power strap relief and actual finite fixed-frame receiving surface relief; fixed-frame receiving seating remains unresolved');changed.append(o.name);records.append({'name':o.name,'owner':o.parent.name,'role':'Retained rigid passive torso skin/backing; tapered proposal','maxWorldVertexDisplacementM':disp})
 # Preserve every actual source functional end/compound subcomponent. Source
 # rails carry their original complete8vertex box as a continuous load path;
 # formed C-section midspan jackets add depth without deleting that stock.
 for side in ('left','right'):
  receiver=bpy.data.objects[('Left'if side=='left'else'Right')+' metatarsus open passive truss']
  for suffix in ('','.001'):
   o=bpy.data.objects[side+' metatarsal passive rail'+suffix];srcLocal=[v.co.copy()for v in o.data.vertices];src=[o.matrix_world@v.co for v in o.data.vertices];assert len(src)==8;fs=[tuple(p.vertices)for p in o.data.polygons];a=sum(src[:4],Vector())/4;b=sum(src[4:],Vector())/4;u=(src[1]-src[0]).normalized();v=(src[3]-src[0]).normalized();axis=(b-a).normalized();vv=list(src);faces=list(fs);cross=((-1,-1),(1,-1),(1,1),(.60,1),(.60,-.63),(-.60,-.63),(-.60,1),(-1,1))
   for t,w,d in zip((.16,.34,.65,.84),(.014,.020,.020,.014),(.018,.025,.025,.018)):
    c=a.lerp(b,t);vv.extend(c+u*x*w+v*y*d for x,y in cross)
   for j in range(3):
    for k in range(8):i=8+j*8+k;n=8+j*8+(k+1)%8;faces.append((i,n,n+8,i+8))
   faces.extend((tuple(reversed(range(8,16))),tuple(range(32,40))));inv=o.matrix_world.inverted();mesh=bpy.data.meshes.new(o.name+' source stock plus finite formed midspan jacket');mesh.from_pydata([inv@p for p in vv],[],faces);mesh.update()
   for mat in o.data.materials:mesh.materials.append(mat)
   bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);assert volume>0;bm.to_mesh(mesh);bm.free();o.data=mesh
   # Original8 coordinates are reinstated from the frozen original mesh in
   # local space, preventing world roundtrip differences at receiving ends.
   old=srcLocal
   for vertex,p in zip(mesh.vertices[:8],old):vertex.co=p
   assert all(vertex.co==p for vertex,p in zip(mesh.vertices[:8],srcLocal))
   annotation(o,'Complete source continuous metatarsal rail and original proximal/distal terminal stock retained. Added finite open formed C-section jacket only between16%and84%of actual rail span; paired service slot remains open. Fixed same-owner jacket/core stock overlap is a fabrication proposal, not a proven union.',[list(a),list(b)]);changed.append(o.name);witness=volume_witness(o,receiver);records.append({'name':o.name,'owner':o.parent.name,'role':'Inherited passive source rail plus limited formed midspan reinforcement','sourceEndStockPreserved':True,'retainedOriginalVertices':8,'finiteClosedPositiveVolumeM3':volume,'actualFiniteDistalReceiver':witness})
  for lateral in (-1,1):
   o=bpy.data.objects[f'V25 {side} thigh primary load member {lateral}'];src=[v.co.copy()for v in o.data.vertices];assert len(src)>=32;world=[o.matrix_world@p for p in src];inv=o.matrix_world.inverted();centers=[sum(world[i:i+8],Vector())/8 for i in(0,8,16,24)]
   for ring in (1,2):
    c=centers[ring]
    for i in range(ring*8,(ring+1)*8):
     delta=world[i]-c;q=c+Vector((delta.x*1.10,delta.y*1.15,delta.z*1.15));o.data.vertices[i].co=inv@q
   o.data.update();assert all(o.data.vertices[i].co==src[i]for i in list(range(8))+list(range(24,len(src))))
   annotation(o,'Source proximal/distal full end rings and all additional receiving-relief vertices exact; two existing formed thigh-channel middle rings gain10%native-Xwidth and15%YZsection depth. No shin or bearing geometry changed; existing fabrication interfaces are retained, not newly certified.',[list(centers[0]),list(centers[-1])]);changed.append(o.name);records.append({'name':o.name,'owner':o.parent.name,'role':'Inherited passive formed thigh member midspan mass gain','endRingsAndReceivingReliefVerticesExact':True})
 bpy.context.view_layer.update();assert protected=={n:signature(bpy.data.objects[n])for n in TRUSS}
 return {'changedMeshes':sorted(changed),'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'watchMeshes':sorted(changed),'attachmentAndEraMap':records,'receiverGeometryExact':{n:{'sourceAndCandidateSha256':s,'vertices':len(bpy.data.objects[n].data.vertices),'faces':len(bpy.data.objects[n].data.polygons),'includes':'Both source shoulders, toe-root crossmember, six split receiving cheeks and their six webs remain byte-exact'}for n,s in protected.items()},'historicalAnnotations':history,'geometryControls':{'lowerTorsoMaximumWidthReductionFraction':.18,'lowerTorsoMaximumAnteriorRetreatM':.050,'lowerTorsoMaximumPosteriorRetreatM':.032,'powerStrapExclusionM':.025,'powerStrapBlendM':.045,'fixedFrameActualSurfaceExclusionM':.050,'fixedFrameActualSurfaceBlendM':.050,'fixedFrameSurfaceObjects':[o.name for o in frameObjects],'midspanJacketAxialSpanFraction':[.16,.84]},'protected':'Complete actual compound receivers, all shin meshes, all dedicated bearings/digits/instep guards, all native transforms/pivots, mechanismLayoutV1, materials and era finishes exact. Original source rail continuous box/end stock retained.','construction':'Passive midspan reinforcements and common lower-torso taper; no new actuator, repair, organic tissue or invisible joint shortening','limits':['Positive-volume receiving overlap witnesses and exact retained terminal stock establish source interface preservation, not fabricated union quality/engineering fit.','Inherited source split receivers retain their own documented original fit defects; preserving them does not upgrade acceptance.','Torso frame/skin interfaces, named apparatus clearance and posed neighboring parts require bounded screens and reviewer judgment.','No runtime change, continuous motion/load certificate or owner acceptance.']}
