"""Breast-envelope01: descending egg breast + reconstructed oblique finite courses.
Actual lower-support02 input; all rigid owners and non-breast stock preserved.
"""
import bpy,bmesh,json,math,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
LINER='V30 continuous tapered breast liner'
ROWS=[(1.224,1.110,5),(1.154,1.015,6),(1.052,.919,7),(.945,.822,6),(.850,.757,5),(.784,.718,4)]
PLATES=[f'V34 formed breast course {r} plate {c}'for r,(_,_,n)in enumerate(ROWS,1)for c in range(1,n+1)]
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def tree(o):
 o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(t.vertices)for t in o.data.loop_triangles],all_triangles=True,epsilon=0)
def measure(o):
 points=[o.matrix_world@v.co for v in o.data.vertices];return {'worldBoundsM':[[min(p[i]for p in points),max(p[i]for p in points)]for i in range(3)],'sectionSamples':[{ 'z':z,'points':len(q),'xSpanM':max(p.x for p in q)-min(p.x for p in q),'frontY':min(p.y for p in q)}for z in(.75,.85,.95,1.05,1.15,1.25)if(q:=[p for p in points if abs(p.z-z)<.012])]}
def apply():
 bpy.context.view_layer.update();liner=bpy.data.objects[LINER];before=measure(liner);records=[];history={};h=runpy.run_path(str(ROOT/'scripts/regions/whole-character-v30-breast-form.py'));actualSupports=[o for o in bpy.data.objects if o.type=='MESH'and(o.name=='Power retaining strap'or o.name.startswith(('V23 breast moving return ','V30 breast liner receiving tab ')))]
 supports=[tree(o)for o in actualSupports];frame=[o for o in bpy.data.objects if o.type=='MESH'and o.parent and o.parent.name=='body'and any(k in o.name.lower()for k in ('thoracic formed rib','hip receiving','hip load bow','pelvic load','sternal','breast hinge','breast opening bearing'))];supportBounds={o.name:measure(o)['worldBoundsM']for o in actualSupports+frame}
 def field(p):
  # High convex breast and neck boundary remain full. Lower width descends
  # toward a compact pelvis instead of a sphere's wide equator.
  w=ease((p.z-.675)/.13)*(1-ease((p.z-1.10)/.135));lower=math.exp(-((p.z-.950)/.175)**2)
  nearest=min(t.find_nearest(p)[3]for t in supports);w*=ease((nearest-.020)/.055)
  q=p.copy();q.x*=1-.145*w*lower;q.y+=.043*w*lower*ease((-p.y-.08)/.20);return q
 points=[liner.matrix_world@v.co for v in liner.data.vertices];inv=liner.matrix_world.inverted()
 for v,p in zip(liner.data.vertices,points):v.co=inv@field(p)
 liner.data.update();backing=tree(liner);sourceProperties={n:dict(bpy.data.objects[n].items())for n in PLATES+[LINER]}
 rootProof=[];allHitFallback=[]
 for row,(top,bottom,count)in enumerate(ROWS,1):
  for col in range(count):
   name=f'V34 formed breast course {row} plate {col+1}';o=bpy.data.objects[name];center=-1+(col+.5)*2/count;step=2/count;stagger=(.005 if col%2 else-.005)*(abs(center)*.65+.35);proof=[];fallback=[]
   def surface(u,v):
    t=2*v-1;side=1 if center>.06 else-1 if center<-.06 else 0
    z=top+stagger+(bottom-top)*u+.011*side*t*ease(u)-.006*(1-t*t)*ease(u)
    door=.45+.45*ease((z-.705)/.225);width=.91 if abs(center)<.3 else .82;angle=(center+step*.5*width*t)*(1-.17*ease(u))*door
    direction=Vector((math.sin(angle),-math.cos(angle),0));start=Vector((0,0,z))+direction*.8;hit=backing.ray_cast(start,-direction,1.1)
    if hit[0]is None:
     guess=field(h['point'](z+.12,angle,0)-Vector((0,0,.12)));near=backing.find_nearest(guess);assert near[0]is not None;seat=near[0];fallback.append({'u':u,'v':v,'targetZ':z,'actualZ':seat.z})
    else:seat=hit[0]
    off=.0045+.0065*ease(u)+.0015*math.sin(math.pi*u)*(1-t*t)
    if u==0:proof.append({'actualBackingPoint':list(seat),'actualReceivingTriangle':hit[2]if hit[0]is not None else None,'rootOffsetM':off})
    return seat+off*direction
   vv,ff=h['solid_sheet'](surface,20,12,.0035);half=len(vv)//2
   # Local finite root lands reach the actual backing on first two rows.
   feet=[]
   for i in range(2):
    for j in range(13):
     idx=i*13+j;near=backing.find_nearest(vv[idx]);assert near[0]is not None;vv[half+idx]=near[0];feet.append({'innerIndex':half+idx,'actualBackingTriangle':near[2],'nearestDistanceM':backing.find_nearest(vv[half+idx])[3]})
   mesh=bpy.data.meshes.new(name+' descended curved finite3.5mm wall');inv=o.matrix_world.inverted();mesh.from_pydata([inv@p for p in vv],[],ff);mesh.update()
   for mat in o.data.materials:mesh.materials.append(mat)
   bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
   if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
   volume=bm.calc_volume(signed=True);assert volume>0,name;bm.to_mesh(mesh);bm.free();o.data=mesh
   for p in mesh.polygons:p.use_smooth=True
   assert not o.modifiers,name
   history[name]={k:json.loads(json.dumps(o[k],default=lambda v:list(v)))for k in ('constructionDescription','geometryStatus','wallM','v38PectoralConnected','v38LowerBody','lowerSupportRevision')if k in o}
   o['constructionHistoryBeforeBreastEnvelope01']=json.dumps(history[name],separators=(',',':'));o['constructionDescription']='Medium descending oblique finite formed breast plate; shallow curved free margin and shorter flank width, actual26-vertex local root land on reshaped finite backing; independent original breastplate opening owner';o['geometryStatus']='Breast-envelope01 reconstructed rigid passive proposal; root samples are actual surface seating, full stock/self/posed fit unverified';o['wallM']=.0035;o['breastEnvelopeRevision']='breast-envelope01'
   for k in ('v38PectoralConnected','v38LowerBody','lowerSupportRevision'):
    if k in o:del o[k]
   rootProof.append({'plate':name,'owner':o.parent.name,'finiteClosedPositiveVolumeM3':volume,'rootLandVertexSamples':len(feet),'maximumSampledRootDistanceM':max(p['nearestDistanceM']for p in feet),'actualRootTriangles':sorted(set(p['actualBackingTriangle']for p in feet)),'rootSamplePoints':proof[::max(1,len(proof)//4)],'receivingStatus':'Actual finite sampled root/backing contact; between-sample triangles, union/fabrication and neighboring posed clearance not certified'})
   if fallback:allHitFallback.append({'plate':name,'uniqueFallbackSamples':len(fallback),'examples':fallback[:3]})
 history[LINER]={k:json.loads(json.dumps(liner[k],default=lambda v:list(v)))for k in ('constructionDescription','geometryStatus','v38PectoralConnected','lowerSupportRevision')if k in liner};liner['constructionHistoryBeforeBreastEnvelope01']=json.dumps(history[LINER],separators=(',',':'));liner['constructionDescription']='Source continuous finite backing reshaped into descending egg/drop through lower/middle field; source top neck and bottom hinge zones retained, actual Power strap/return/tab surface relief';liner['geometryStatus']='Breast-envelope01 bounded rigid contour proposal; existing support defects remain';liner['breastEnvelopeRevision']='breast-envelope01'
 for k in ('v38PectoralConnected','lowerSupportRevision'):
  if k in liner:del liner[k]
 bpy.context.view_layer.update();after=measure(liner)
 for n in PLATES+[LINER]:records.append({'name':n,'owner':bpy.data.objects[n].parent.name,'constructionClass':bpy.data.objects[n].get('constructionClass'),'eras':bpy.data.objects[n].get('exteriorEras'),'role':'Rigid passive breast plate/backing proposal'})
 return {'changedMeshes':PLATES+[LINER],'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'watchMeshes':PLATES+[LINER],'attachmentAndEraMap':records,'modelEnvelopeMeasurements':{'source':before,'candidate':after,'notReferenceDimensions':True},'actualInspectedReceivingFrameBounds':supportBounds,'plateCourseWorldZProposal':ROWS,'finitePlateRootSeating':rootProof,'actualSurfaceFallbackSamples':allHitFallback,'geometryControls':{'maximumLowerMiddleWidthReductionFraction':.145,'maximumAnteriorRetreatM':.043,'freeWallM':.0035,'rootToFreeRadialStandM':[.0045,.011],'functionalSurfaceExclusionM':.020,'functionalSurfaceBlendM':.055},'protected':'All legs/feet/compound receivers/core end stock, head/neck/wings, nodes/pivots, receiving tabs/returns/hinge/Power apparatus, material/era profiles and mechanismLayoutV1 exact. Backing/33 breast identities alone change.','construction':'High convex breast retained above descending middle/lower egg contour; new33 medium staggered oblique courses with narrower flanks, curved shallow free margins and finite local receiving lands.','limits':['Actual backing root vertex seating is scoped evidence, not full finite surface/contact/stock selfintersection certification.','Ray misses use actual nearest finite backing surface, explicitly reported; not silently treated as radial fit.','Source retained support/frame may require separate correction if screen shows incompatibility; no original frame acceptance inferred.','No continuous motion/load/engineering or owner likeness acceptance.']}
