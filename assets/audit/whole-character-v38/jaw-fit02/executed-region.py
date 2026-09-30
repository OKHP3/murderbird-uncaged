"""Jaw-fit02: localized distal separation and substantial curved lower return.
Actual bill-shell02; upper hook/contact/optic/source socket footprint unchanged.
"""
import bpy,bmesh,math
from mathutils import Vector
NAME='V32 formed mandibular bowl'
def ease(u):u=max(0,min(1,u));return u*u*(3-2*u)
def upper_contact():
 pts=[(o.name,o.matrix_world@v.co)for o in bpy.data.objects if o.type=='MESH'and o.parent and o.parent.name=='upper-bill'for v in o.data.vertices];lead=min(pts,key=lambda p:p[1].y)
 return {'leadingObject':lead[0],'leadingPointNativeXYZ':list(lead[1]),'actualTriangleVertexBounds':[[min(p[k]for _,p in pts),max(p[k]for _,p in pts)]for k in range(3)]}
def apply():
 bpy.context.view_layer.update();contact=upper_contact();o=bpy.data.objects[NAME];world=o.matrix_world.copy();inv=world.inverted();old=[v.co.copy()for v in o.data.vertices];points=[world@v for v in old];keys=[(r,k)for r in range(53)for k in range(33)if r<=5 or k<=6 or k>=26];half=len(keys);assert len(old)==2*half==1712;lookup={key:i for i,key in enumerate(keys)};o.data=o.data.copy();changes=[]
 for i,(row,col)in enumerate(keys):
  if row<=14:continue
  u=(row-14)/38;edge=col/6 if col<=6 else(32-col)/6;ramp=ease((u-.25)/.75);lower=.009*ramp;depth=.009*edge*ease(u/.50);shorten=.022*ease((u-.30)/.70);curl=.006*ease((u-.70)/.30);move=Vector((0,shorten,-lower-depth+curl))
  for index in (i,i+half):o.data.vertices[index].co=inv@(points[index]+move)
  changes.append({'sourceGrid':[row,col],'worldDeltaM':list(move)})
 protected=[i for i,(row,col)in enumerate(keys)if row<=14];error=max((o.data.vertices[i].co-old[i]).length for i in protected+ [i+half for i in protected]);assert error==0;socketindex=lookup[(12,1)];assert socketindex==283 and o.data.vertices[socketindex].co==old[socketindex];o.data.update()
 bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);assert volume>0;bm.free()
 new=[world@v.co for v in o.data.vertices];stockerror=max(((new[i+half]-new[i])-(points[i+half]-points[i])).length for i in range(half));assert stockerror<3e-7;after=upper_contact();assert after==contact
 o['v38JawFit']='Finite source rail stock, localized descending distal return and deeper band; proposal'
 return {'changedMeshes':[NAME],'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'contactBefore':contact,'contactAfter':after,'contactLandmarksChanged':False,'protectedActualSocketIndex':283,'protectedSourceSocketIndex':397,'protectedRootRows':'Rows0..14 existing keys outer/inner exact, true socket neighborhood row10..14/col0..4 intact','protectedRootCoordinateMaxErrorM':error,'all856SourcePairedStockVectorsPreservedMaxErrorM':stockerror,'actualMaximumDisplacementM':max(math.sqrt(sum(x*x for x in p['worldDeltaM']))for p in changes),'modifiedOuterVertices':len(changes),'modifiedInnerVertices':len(changes),'exactVertexAllowlist':'Existing source-grid rows15..52,cols0..6/26..32 and paired inner+856; only native world Y/Z changed','displacementField':'01 descending depth retained; smooth22mm posterior shortening afteru.30 and6mm terminal upturn afteru.70; source X/stock retained. No thinning/removal or upper hook change.','attachmentAndEraMap':[{'name':NAME,'owner':o.parent.name,'parentLocalMatrix':[list(r)for r in o.matrix_local],'eras':o.get('exteriorEras'),'materials':[m.name if m else None for m in o.data.materials],'rigid':True,'stock':'All856 actual paired vectors retained; paired length not universal normal-thickness certificate','closedEdgeManifold':True,'positiveVolumeM3':volume,'mechanism':'Retained actual jaw pivot and Maker socket; inherited era drive and inspection ownership'}],'confirmation':'ActualJuly HEAD ONLY slender substantial curved lower return and improved fixed hook; Master03/Maker-clean wholebird crosscheck','reconstruction':'Exact displacement/hidden stock/jaw profile authored proposal, not measured art or manufacturing','limits':['Actual complete finite jaw versus head screen follows visible gate; no continuous collision, physical simulation or owner acceptance.','Existing9breast contacts/16.25mm receiver warning and broad temple remain outside scope.','Upperbill contact geometry/marker, true socket footprint, root hardware and all other regions exactly retained.']}
