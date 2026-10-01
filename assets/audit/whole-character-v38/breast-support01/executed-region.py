"""Breast-support01: deep high sternum from retained lower-support02 stock.
Original compatible supports, lower breast/pelvis and neck articulation retained.
"""
import bpy,bmesh,json,math,runpy
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];LINER='V30 continuous tapered breast liner'
ROWS=[(1.266,1.139,5),(1.195,1.063,6),(1.106,.975,7),(.995,.884,6),(.904,.791,5),(.815,.723,4)]
PLATES=[f'V34 formed breast course {r} plate {c}'for r,(_,_,n)in enumerate(ROWS,1)for c in range(1,n+1)]
TABS=[f'V30 breast liner receiving tab {s}'for s in(-1,1)]
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def tree(o):
 o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(t.vertices)for t in o.data.loop_triangles],all_triangles=True,epsilon=0)
def measure(o):
 points=[o.matrix_world@v.co for v in o.data.vertices];return {'worldBoundsM':[[min(p[i]for p in points),max(p[i]for p in points)]for i in range(3)],'sectionSamples':[{'z':z,'points':len(q),'xSpanM':max(p.x for p in q)-min(p.x for p in q),'frontY':min(p.y for p in q)}for z in(.85,.95,1.05,1.15,1.25)if(q:=[p for p in points if abs(p.z-z)<.012])]}
def history(o):
 keep={k:json.loads(json.dumps(o[k],default=lambda v:list(v)))for k in list(o.keys())if k.startswith(('v25','v38','lowerSupport'))or k in('constructionDescription','geometryStatus','wallM','courseTopM','courseBottomM','courseIndex','lateralSpanRadians','panelKind','authoringRole')};o['historicalConstructionBeforeBreastSupport01']=json.dumps(keep,separators=(',',':'))
 for k in keep:
  if k.startswith(('v25','v38','lowerSupport')):del o[k]
 return keep
def apply():
 bpy.context.view_layer.update();liner=bpy.data.objects[LINER];before=measure(liner);h=runpy.run_path(str(ROOT/'scripts/regions/whole-character-v30-breast-form.py'));old=[liner.matrix_world@v.co for v in liner.data.vertices];inv=liner.matrix_world.inverted();fixed=[]
 for v,p in zip(liner.data.vertices,old):
  if p.z<=1.005:fixed.append(v.index);continue
  u=ease((p.z-1.005)/.090);edge=1-ease((abs(math.atan2(p.x,-p.y))-.23)/.30);topFade=1-ease((p.z-1.195)/.045);bulge=u*math.exp(-((p.z-1.135)/.080)**2)*topFade*edge;q=p.copy();q.y-=.060*bulge;q.x*=1+.015*bulge;v.co=inv@q
 liner.data.update();backing=tree(liner);roots=[];fallbacks=[]
 # Actual highest radial hit at each angle, supporting top roots below finite
 # backing boundary rather than projected points beyond its cut edge.
 topSamples=[]
 for i in range(101):
  a=-.9+1.8*i/100;d=Vector((math.sin(a),-math.cos(a),0));z=1.290
  while z>1.160 and backing.ray_cast(Vector((0,0,z))+d*.8,-d,1.1)[0]is None:z-=.001
  topSamples.append((a,z))
 def topAt(a):
  f=max(0,min(100,(a+.9)/1.8*100));i=min(99,int(f));return topSamples[i][1]*(1-(f-i))+topSamples[i+1][1]*(f-i)
 for r,(nominalTop,bottom,count)in enumerate(ROWS,1):
  for c in range(count):
   o=bpy.data.objects[f'V34 formed breast course {r} plate {c+1}'];center=-1+(c+.5)*2/count;step=2/count;fallback=[]
   def surface(u,v):
    t=2*v-1;side=1 if center>.05 else-1 if center<-.05 else 0;theta=(center+step*.5*(.92 if abs(center)<.35 else .86)*t)*(1-.13*ease(u))*(.86 if r<3 else(.45+.45*ease((nominalTop-.705)/.225)));stagger=.006*(1 if c%2 else-1)*(.4+.6*abs(center));ratio=.245/.46 if r<=2 else max(.10,.245-(1.06-nominalTop)*.36)/max(.2,abs(h['point'](nominalTop+.12,0,0).y));polar=math.atan(ratio*math.tan(theta));top=1.246-.020*abs(center)+stagger if r==1 else nominalTop+stagger;z=top+(bottom-top)*u+.016*side*t*ease(u)-.010*(1-t*t)*ease(u);d=Vector((math.sin(polar),-math.cos(polar),0));probeZ=min(z,1.194)if r==1 else z;hit=backing.ray_cast(Vector((0,0,probeZ))+d*.8,-d,1.1)
    if hit[0]is None:
     p=backing.find_nearest(h['point'](z+.12,theta,0)-Vector((0,0,.12)))[0];fallback.append({'targetZ':z,'actualZ':p.z,'u':u,'v':v})
    else:p=hit[0]
    if r==1 and z>1.194:p.z=z;p.y+=.028*ease((z-1.194)/.05)
    return p+d*(.007+.013*ease(u)+.002*math.sin(math.pi*u)*(1-t*t))
   vv,ff=h['solid_sheet'](surface,24,14,.0035);half=len(vv)//2;seats=[]
   for i in((9,10)if r==1 else(0,1)):
    for j in range(15):
     idx=i*15+j;near=backing.find_nearest(vv[idx]);vv[half+idx]=near[0];seats.append({'triangle':near[2],'point':list(near[0]),'distanceM':backing.find_nearest(vv[half+idx])[3]})
   mesh=bpy.data.meshes.new(o.name+' deep curved oblique finite stock');inv=o.matrix_world.inverted();mesh.from_pydata([inv@p for p in vv],[],ff);mesh.update()
   for m in o.data.materials:mesh.materials.append(m)
   bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),o.name
   if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
   vol=bm.calc_volume(signed=True);assert vol>0;bm.to_mesh(mesh);bm.free();o.data=mesh
   for p in mesh.polygons:p.use_smooth=True
   assert not o.modifiers;history(o);o['constructionDescription']='Deep breast curved oblique rigid finite plate; broad central course and shorter swept flank hierarchy, actual30-vertex root lands on finite backing; independent original inspection-cover owner';o['geometryStatus']='Breast-support01 authored stock proposal; finite sampled root seating does not prove between-sample union, neighboring fit or full motion';o['wallM']=.0035;o['courseIndex']=r;o['courseTopM']=measure(o)['worldBoundsM'][2][1];o['courseBottomM']=measure(o)['worldBoundsM'][2][0];o['lateralSpanRadians']=step*.9*.86;o['panelKind']='sternum'if abs(center)<.35 else'oblique-flank';o['authoringRole']='Finite passive formed breast plate with actual sampled backing root lands';o['breastSupportRevision']='breast-support01'
   roots.append({'plate':o.name,'owner':o.parent.name,'rootLandVertexSamples':30,'maximumSampledBackingGapM':max(s['distanceM']for s in seats),'actualRootTriangles':sorted({s['triangle']for s in seats}),'actualRootSamplePoints':seats[::7],'closedPositiveVolumeM3':vol})
   if fallback:fallbacks.append({'plate':o.name,'sampleCalls':len(fallback),'examples':fallback[:3]})
 history(liner);liner['constructionDescription']='Source finite backing retains exact lower breast/pelvis stock at nativeworldZ<=1.005; continuous existing upper stock forms up-to60mm convex high-sternum projection, blended back to original upper/lateral boundaries; formed top-course free lip curves back toward retained collar, no raised backing rim or altered neck';liner['geometryStatus']='Breast-support01 mass/construction proposal; actual aperture surfaces and selected poses require bounded screens';liner['breastSupportRevision']='breast-support01'
 tabs=[]
 for n in TABS:
  o=bpy.data.objects[n];history(o)
  for k in('courseTopM','courseBottomM','courseIndex','lateralSpanRadians','panelKind'):
   if k in o:del o[k]
  o['wallM']=.004;o['authoringRole']='Finite passive C-section receiving tab between original moving-return rear web and breast liner, same rigid inspection-cover owner';o['constructionDescription']='Original source C receiving stock preserved exactly; source recipe nominal18mm width14mm depth4mm wall, local actual dimensions recorded separately after inherited forming operations';o['geometryStatus']='Breast-support01 source-exact receiving geometry; historical fits not upgraded by metadata correction';o['constructionClass']='inherited-passive';o['breastSupportRevision']='breast-support01'
  v=[o.matrix_world@p.co for p in o.data.vertices];samples=[]
  for i in range(0,len(v)-7,8):samples.append({'ring':i//8,'lipWallEdgesM':[(v[i+2]-v[i+3]).length,(v[i+6]-v[i+7]).length],'webWallAcrossSectionM':(v[i+4]-v[i+1]).length})
  o['actualStockSectionSamples']=json.dumps(samples,separators=(',',':'));tabs.append({'name':n,'meshByteExact':True,'sourceNominalWallM':.004,'actualSectionSamples':samples,'remainingDimensionalQualification':'Inherited formed sections may differ from original nominal recipe; samples are actual transformed finite ring edges, not stock uniformity certification'})
 bpy.context.view_layer.update();records=[{'name':n,'owner':bpy.data.objects[n].parent.name,'eras':bpy.data.objects[n].get('exteriorEras'),'constructionClass':bpy.data.objects[n].get('constructionClass')}for n in PLATES+[LINER]+TABS]
 return {'changedMeshes':PLATES+[LINER],'changedNodes':TABS,'addedMeshes':[],'removedMeshes':[],'watchMeshes':PLATES+[LINER]+TABS,'attachmentAndEraMap':records,'sourceBasis':'Actual retained lower-support02, not held thin breast-envelope02','modelEnvelopeMeasurements':{'source':before,'candidate':measure(liner),'notReferenceDimensions':True},'highSternumControls':{'maximumAnteriorProjectionM':.060,'maximumUpperRiseM':0,'upperWidthGainFraction':.015,'topAndFlankBlend':'Actual stock projection vanishes at source upper boundary and lateral polar angle>=.53 rad; top free lip root lands are lower within actual backing, not unsupported seats','lowerBreastExactAtOrBelowNativeWorldZ':1.005,'lowerBackingVerticesExact':len(fixed)},'finiteRootSeating':roots,'actualFiniteBackingFallbackSamples':fallbacks,'receivingTabAnnotationCorrections':tabs,'preserved':'All complete leg/foot stock/receivers; original moving returns, hinge stock and receiving tabs geometry; all named nodes/transforms and head/neck/wing/pelvis geometry; material and era profiles. Only34 breast mesh geometries change; two source-exact receiving tabs have reconciled metadata.','limits':['Actual30-vertex root-land samples are not finite between-sample union or swept fit certification.','Finite backing ray misses use explicitly reported actual nearest triangles; no unsupported projected seat is claimed.','Source compatibility at unchanged stock does not establish shell seating; inherited/new intersections must remain separate.','Authored sternum dimensions are model controls, not exact raster-reference measurements.','No owner likeness, continuous motion/load or engineering acceptance.']}
