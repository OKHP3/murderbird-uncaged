"""Lower-body02: tapered passive lower torso and substantial open leg channels.
Joint centers, bearing geometry and floor-contact digits remain exact. Native Z-up.
"""
import bpy,bmesh,math,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def smooth(t):
 t=max(0,min(1,t));return t*t*(3-2*t)

def profile(centers,widths,depths,channel=True):
 axis=centers[-1]-centers[0];u=Vector((1,0,0));v=Vector((0,axis.z,-axis.y)).normalized()
 if v.y>0:v.negate()
 cross=((-1,-1),(1,-1),(1,1),(.60,1),(.60,-.63),(-.60,-.63),(-.60,1),(-1,1)) if channel else ((-.72,-1),(.72,-1),(1,-.72),(1,.72),(.72,1),(-.72,1),(-1,.72),(-1,-.72))
 verts=[];faces=[]
 for c,w,d in zip(centers,widths,depths):verts.extend(c+u*x*w+v*y*d for x,y in cross)
 for j in range(len(centers)-1):
  for k in range(8):
   i=j*8+k;n=j*8+(k+1)%8;faces.append((i,n,n+8,i+8))
 faces.extend((tuple(reversed(range(8))),tuple(range((len(centers)-1)*8,len(centers)*8))))
 return verts,faces

def replace(o,geom):
 verts,faces=geom;inv=o.matrix_world.inverted();mesh=bpy.data.meshes.new(o.name+' lower-body02 finite section');mesh.from_pydata([inv@p for p in verts],[],faces);mesh.update()
 for m in o.data.materials:mesh.materials.append(m)
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),o.name
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 volume=bm.calc_volume(signed=True);assert volume>0,o.name;bm.to_mesh(mesh);bm.free();o.data=mesh
 for p in mesh.polygons:p.use_smooth=False
 o['v38LowerBody']='Rigid finite open formed section; joint centers and bearing geometry exact; rest-only fabrication proposal'
 return volume

def apply():
 bpy.context.view_layer.update();changed=[];records=[];joints={n:list(bpy.data.objects[n].matrix_world.translation)for n in ('left-thigh','left-shin','left-foot','left-toes','right-thigh','right-shin','right-foot','right-toes')}
 hips=[bpy.data.objects[s+'-thigh'].matrix_world.translation.copy()for s in ('left','right')]
 strap=bpy.data.objects['Power retaining strap'];strap.data.calc_loop_triangles();strapTree=BVHTree.FromPolygons([strap.matrix_world@v.co for v in strap.data.vertices],[tuple(t.vertices)for t in strap.data.loop_triangles],all_triangles=True)
 def torsofield(p):
  q=p.copy();w=smooth((p.z-.670)/.115)*(1-smooth((p.z-.91)/.20))
  # Exact source hinge strip and hip journal envelopes remain excluded.
  for c in hips:w*=smooth(((p-c).length-.095)/.070)
  nearest=strapTree.find_nearest(p)
  if nearest[0]is not None:w*=smooth((nearest[3]-.025)/.045)
  front=smooth((-p.y-.02)/.17);rear=smooth((p.y+.01)/.13)
  q.x*=1-.18*w;q.y+=.050*w*front-.032*w*rear
  return q
 skins=[o for o in bpy.data.objects if o.type=='MESH' and (o.name.startswith(('V34 formed breast course ','V35 oblique thoracic side guard ','V35 compact dorsal return ','V38 tapered pelvic return course ')) or o.name in ('V30 continuous tapered breast liner','V30 continuous dorsal pelvic liner'))]
 for o in skins:
  src=[o.matrix_world@v.co for v in o.data.vertices];inv=o.matrix_world.inverted();dst=[torsofield(p)for p in src];disp=max((p-q).length for p,q in zip(src,dst))
  if disp>1e-7:
   for v,q in zip(o.data.vertices,dst):v.co=inv@q
   o.data.update();o['v38LowerBody']='Common tapered lower-body cage; source hinge strip/hip envelopes held; finite receiving interfaces still need screen';changed.append(o.name);records.append({'name':o.name,'owner':o.parent.name,'role':'Existing rigid lower torso plate/backing formed with common taper cage','maxWorldVertexDisplacementM':disp,'fit':'Skin/backing share field; untouched support frame interface is not verified or asserted seated'})
 # Retained upper limb spans; section mass develops through continuous members,
 # preserving journals and their existing concentric hardware.
 for side in ('left','right'):
  for kind,nextkind in (('thigh','shin'),('shin','foot')):
   owner=bpy.data.objects[side+'-'+kind];p0=owner.matrix_world.translation.copy();p1=bpy.data.objects[side+'-'+nextkind].matrix_world.translation.copy();axis=(p1-p0).normalized();length=(p1-p0).length
   for lateral in (-1,1):
    name=f'V25 {side} {kind} primary load member {lateral}';o=bpy.data.objects[name]
    # Fit existing journal-side terminal widths; center broadens instead of
    # covering joints with blank armor. Same rigid owner throughout.
    if kind=='thigh':
     offsets=[.055,.085,.090,.085];distances=[.046,length*.30,length*.61,length-.068];widths=[.021,.037,.036,.023];depths=[.030,.054,.052,.024]
    else:
     inward=-1 if side=='left' else 1;offsets=[.070,.055,.040,.018];distances=[.045,length*.42,length*.55,length-.079];widths=[.017,.027,.026,.017];depths=[.023,.040,.039,.025]
    centers=[p0+axis*d+Vector((lateral*x,0,0))for d,x in zip(distances,offsets)]
    volume=replace(o,profile(centers,widths,depths));changed.append(name);records.append({'name':name,'owner':owner.name,'role':'Open passive load channel with deeper midspan and retained terminal stations','proximalCenter':list(p0),'distalCenter':list(p1),'centerStations':[list(c)for c in centers],'halfWidthsM':widths,'halfDepthsM':depths,'finiteClosedPositiveVolumeM3':volume,'fit':'Journal-side terminal stations retained for thigh; shin center realigned to concentric pivot strip. Existing collar/gusset interfaces require separate screen.'})
  owner=bpy.data.objects[side+'-foot'];p0=owner.matrix_world.translation.copy();p1=bpy.data.objects[side+'-toes'].matrix_world.translation.copy();axis=(p1-p0).normalized();length=(p1-p0).length;v=Vector((0,axis.z,-axis.y)).normalized()
  if v.y>0:v.negate()
  for index,lateral in enumerate((-1,1)):
   name=f'{side} metatarsal passive rail'+('.001' if index else '');o=bpy.data.objects[name]
   centers=[p0+axis*d+Vector((lateral*x,0,0))for d,x in zip([.052,length*.32,length*.62,length-.075],[.026,.034,.035,.032])]
   volume=replace(o,profile(centers,[.009,.014,.014,.010],[.016,.021,.021,.016]));changed.append(name);records.append({'name':name,'owner':owner.name,'role':'Substantial paired metatarsal formed channel, open center retained','proximalCenter':list(p0),'distalCenter':list(p1),'centerStations':[list(c)for c in centers],'finiteClosedPositiveVolumeM3':volume,'fit':'Proximal/distal bearing centers exact; new section ends/rims need actual receiving and posed screen'})
  def joined(parts):
   verts=[];faces=[]
   for vv,ff in parts:
    off=len(verts);verts+=vv;faces+=[tuple(i+off for i in f)for f in ff]
   return verts,faces
  def crossbrace(t):
   c=p0.lerp(p1,t)-v*.014;u=Vector((1,0,0));vv=[c+u*x*.039+axis*y*.004+v*z*.006 for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
   ff=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)];return vv,ff
  name=f'{side.title()} metatarsus open passive truss';o=bpy.data.objects[name]
  volume=replace(o,joined([crossbrace(.34),crossbrace(.62)]));changed.append(name);records.append({'name':name,'owner':owner.name,'role':'Two short finite rear cross ties; longitudinal central service slot fully open','finiteClosedPositiveVolumeM3':volume,'fit':'Fixed same-owner cross ties meet paired channels; exact fabricated unions/neighbor motion unverified'})
  name=f'{side} curved instep guard';o=bpy.data.objects[name];parts=[]
  for t0,t1 in ((.33,.46),(.56,.69)):
   a=p0.lerp(p1,t0)+Vector((-.034,0,0))+v*.022;b=p0.lerp(p1,t1)+Vector((-.034,0,0))+v*.022
   parts.append(profile([a,a.lerp(b,.5)+v*.002,b],[.008,.009,.008],[.003,.003,.003],False))
  volume=replace(o,joined(parts));changed.append(name);records.append({'name':name,'owner':owner.name,'role':'Two short side-rail wear caps; no central instep shield or longitudinal rear hull','finiteClosedPositiveVolumeM3':volume,'fit':'Caps follow left same-owner rail; finite mounting/weld lands unverified'})
 # No joint or mechanism socket moves: lower cage is zero at unchanged
 # Maker leg point and all declared upper-body attachment coordinates.
 layout=json.loads(bpy.data.objects['body']['mechanismLayoutV1']);sockets=[]
 for side in ('left','right'):
  owner=bpy.data.objects[side+'-thigh'];q=layout['makerControlOffsets']['leg'];p=owner.matrix_world@Vector((q[0],-q[2],q[1]));sockets.append({'owner':owner.name,'makerLegLocalGltf':q,'sourceAndCandidateWorldExact':list(p),'surfaceSeating':'Socket marker exact; finite revised load-channel receiving seating still unverified'})
 bpy.context.view_layer.update();assert joints=={n:list(bpy.data.objects[n].matrix_world.translation)for n in joints}
 return {'changedMeshes':sorted(changed),'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'watchMeshes':sorted(changed),'attachmentAndEraMap':records,'jointFramesExact':joints,'runtimeAttachmentEndpointsExact':sockets,'geometryControls':{'lowerTorsoMaximumWidthReductionFraction':.18,'lowerTorsoMaximumAnteriorRetreatM':.050,'lowerTorsoMaximumPosteriorRetreatM':.032,'lowerFieldStartsZ':.670,'upperFieldEndsZ':1.11,'hipExclusionRadiusM':.095,'hipBlendM':.070,'powerStrapFieldExclusionM':.025,'powerStrapFieldBlendM':.045},'construction':'Existing rigid passive lower torso skins/backing taper together; deeper open thigh/shin load channels and substantial paired metatarsal channels replace thin rails. No new joints, drive or organic skin.','protected':'All native object transforms, named pivots, material records/era profiles, mechanismLayoutV1, bearing hardware, toe/digit/floor geometry, head/neck/wing geometry exact.','limits':['Not owner likeness acceptance or engineering certification.','Changed leg channels and torso skins require actual rest/posed neighboring/receiving-fit screens; unchanged parentage and pivots do not prove fit.','Reference metatarsal structure remains an authored reconstruction; paired narrower open channels/cross ties require finite terminal seating and posed clearance checks.','No runtime edits, release or publication.']}
