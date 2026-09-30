"""Gather28 trailing mantle plates along their actual source surfaces; receiving rows exact."""
import bpy,bmesh,math
from mathutils import Vector
COUNTS={1:[4,5],2:[4,5,6],3:[3,4,5,6],4:[3,4,5],5:[3,4]}
ALLOWED=[f'V38 {side} mantle layered course {course} plate {plate}'for side in ('left','right')for course,plates in COUNTS.items()for plate in plates]
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def apply():
 bpy.context.view_layer.update();records=[]
 for name in ALLOWED:
  o=bpy.data.objects[name];side='left'if'left'in name else'right';assert o.parent.name==side+'-mantle'and len(o.data.vertices)==286;course=int(name.split(' course ')[1].split()[0]);plate=int(name.split(' plate ')[1]);source=[v.co.copy()for v in o.data.vertices];world=o.matrix_world.copy();inv=world.inverted();outer=[world@v for v in source[:143]];inner=[world@v for v in source[143:]];stock=[a-b for a,b in zip(outer,inner)];assert all(abs(s.length-.005)<2e-7for s in stock)
  o.data=o.data.copy();moves=[];rowmap=[]
  compression={1:.28,2:.30,3:.34,4:.38,5:.44}[course]
  for row in range(13):
   # Three actual receiving rows remain byte-exact. Only the free sheet contracts.
   targetrow=row if row<=2 else row-(row-2)*compression*smooth((row-2)/10)
   lo=min(11,int(targetrow));fraction=targetrow-lo;rowmap.append(targetrow)
   for col in range(11):
    i=row*11+col
    if row<=2:moves.append(0);continue
    center=outer[lo*11+5].lerp(outer[(lo+1)*11+5],fraction)
    section=outer[i]-outer[row*11+5]
    target=center+section
    # Retain each original normalized cross-section, including terminal taper
    # and rounded center overhang. Vertical course station retains overlap.
    target.z=outer[i].z+(center.z-outer[row*11+5].z)*(.20 if course==5 else 0)
    o.data.vertices[i].co=inv@target;o.data.vertices[i+143].co=inv@(target-stock[i]);moves.append((target-outer[i]).length)
  o.data.update();assert all(o.data.vertices[i].co==source[i]and o.data.vertices[i+143].co==source[i+143]for i in range(33));bm=bmesh.new();bm.from_mesh(o.data);closed=all(e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free();assert closed and volume>0,name
  actual=[world@v.co for v in o.data.vertices];actualstock=[(actual[i]-actual[i+143]).length for i in range(143)];assert max(abs(v-.005)for v in actualstock)<2e-7
  o['v38CompactMantle']='Compact02 rounded terminal cross-sections and retained vertical overlap; shortened XYcenterline free mantlecourse; first3receivingrows exact; rigid passive shell; likeness/continuousfit unaccepted'
  records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'constructionClass':o.get('constructionClass'),'surfaceRole':o.get('surfaceRole'),'materials':[m.name for m in o.data.materials],'vertexScope':'Outer indices33..142 and paired inner176..285 only; source receiving outer0..32 +inner143..175 byte-exact.','actualChangedVertexIndices':[i for i,v in enumerate(o.data.vertices)if v.co!=source[i]],'preservedReceivingOuterIndices':list(range(33)),'preservedReceivingInnerIndices':list(range(143,176)),'sourceRowToAuthoredRowMap':rowmap,'shorteningFraction':compression,'method':'Free centerline XY sampled along actual source curvature; ORIGINAL cross-section/taper/rounding retained at every normalized station; original verticalcourse1–4station exact,course5 only20%ofcenterlineZcontraction; no uniformwing scale,rotation,pivot or root relocation. Each original5mm stock vector retained.','maximumMovementM':max(moves),'minimumPairedStockM':min(actualstock),'maximumPairedStockM':max(actualstock),'closedEdgeManifold':closed,'positiveVolumeM3':volume,'originalWorldBounds':[[min(p[k]for p in outer),max(p[k]for p in outer)]for k in range(3)],'candidateWorldBounds':[[min(p[k]for p in actual[:143]),max(p[k]for p in actual[:143])]for k in range(3)]})
 return {'changedMeshes':ALLOWED,'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'attachmentAndEraMap':records,'rigidVsFlexible':'28finite rigid mantle-owned trailingplates reformed at authoring time; no flexible skin/runtime deformation; elbow-owned parts exact.','confirmed':'Master03 plus scopedMaker-clean/Mechanic show compact flightless tucked shield following torso,actualshoulder/elbow readable; JulyHEADONLY excludes longwings.','reconstruction':'Exact free-end shortening/hidden stock/attachment strength remain authoredproposal,not dimensions from artwork.','preservation':'Each66receiving vertices exact,allowner/rest/pivot/parentinverse/socketloadmember/leftlimit/excludedmaterials exact. Receiving-row preservation is not proof of wholeplate support.','limits':['Fullbird visualreview required before anysecondattempt.','Paired5mm stock/closedmesh do notcertify normalsurface thickness,fastening/continuousmotion or engineering.','Changed mantle52pool strict differentowner surfaces screened separately; sameownerlaps/containment/continuoussweep not certified.','No flightspan increase; no head/neck/body/machinery/elbow/socket change.']}
