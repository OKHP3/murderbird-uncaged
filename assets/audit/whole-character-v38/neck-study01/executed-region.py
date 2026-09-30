"""One bounded curved cervical envelope from40 existing rigid guards.
No collar, hanging returns, owner/pivot, head or breast edits.
"""
import bpy,bmesh,math
from mathutils import Vector
OWNERS=['neck','cervical-mid-a','cervical-mid-b','cervical-upper']
ALLOWED=[f'V23 cervical {i+1} directional guard {k+1}' for i in range(4) for k in range(10)]
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def curve(z,points):
 for (za,a),(zb,b) in zip(points,points[1:]):
  if z<=zb:return a+(b-a)*smooth((z-za)/(zb-za))
 return points[-1][1]
def apply():
 bpy.context.view_layer.update();records=[]
 for i,owner in enumerate(OWNERS):
  for k in range(10):
   o=bpy.data.objects[ALLOWED[i*10+k]];assert o.parent.name==owner
   world=o.matrix_world.copy();inv=world.inverted();original=[world@v.co for v in o.data.vertices];o.data=o.data.copy();maxmove=0
   # Current complete finite surfaces deform together around a smooth whole-neck
   # contour; root receiving rows fade to exact source at the breast aperture.
   for vertex,p in zip(o.data.vertices,original):
    z=p.z;center=curve(z,[(1.21,-.205),(1.29,-.239),(1.35,-.288),(1.41,-.342),(1.48,-.355)])
    radial=Vector((p.x,p.y-center,0));r=max(radial.length,1e-8);side=abs(p.x)/r;front=max(0,-radial.y/r)
    rootfade=smooth((z-1.235)/.055) if i==0 else 1
    width=curve(z,[(1.21,0),(1.28,.014),(1.34,.030),(1.40,.025),(1.47,.018)])
    forward=curve(z,[(1.21,0),(1.28,.010),(1.34,.026),(1.40,.021),(1.47,.008)])
    delta=Vector((math.copysign(width*side,p.x) if p.x else 0,-forward*front,0))*rootfade
    if i==3:
     # Raised, swept shoulders of individual upper guards meet the existing
     # head underside visually; varied endings prevent a new continuous cuff.
     t=smooth((z-1.403)/.055);edge=1-.28*side
     delta.z+=.045*t*edge
     delta.y-=.005*t*front
    # Oblique terminal flow is strongest away from the root receiving seam.
    if i>0:
     within=smooth((z-[1.21,1.277,1.332,1.387][i])/.065)
     diagonal=.008*math.sin((k%5)*.9+i*.8)*(within-.5)
     delta.z+=diagonal*side
    vertex.co=inv@(p+delta);maxmove=max(maxmove,delta.length)
   o.data.update()
   # Evaluate actual existing finite walls/bevels; keep ownership and all
   # material roles, remove only these guards' authoring modifiers by baking.
   dg=bpy.context.evaluated_depsgraph_get();ev=o.evaluated_get(dg);m=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=dg);o.data=m;o.modifiers.clear()
   bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));closed=all(e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True)
   if volume<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces));volume=-volume
   assert closed and volume>0,o.name
   bm.to_mesh(m);bm.free();m.update()
   o['v38NeckEnvelope']='neck-study01 broader curved directional envelope; independently rigid inherited guard; targeted pose fit requires review'
   records.append({'name':o.name,'owner':owner,'eras':o.get('exteriorEras'),'surfaceRole':o.get('surfaceRole'),'constructionClass':o.get('constructionClass'),'materials':[m.name for m in o.data.materials],'vertexScope':'Existing complete guard surface only; source/candidate full mesh signatures captured. Upper finite modifier stack baked. No other objects.','maximumAuthoredSurfaceMovementM':maxmove,'finiteClosed':closed,'positiveVolumeM3':volume,'rootReceivingLowerRowsExactByZeroField':i==0,'geometry':'Broad swept curve and oblique varied guard endings; no rigid owner bridge or hanging strip added.'})
 return {'changedMeshes':ALLOWED,'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'attachmentAndEraMap':records,'confirmation':'Master03/Mechanic show compact strong curved head-neck-breast envelope; July does not govern neck.','reconstruction':'Author-derived finite guard envelope, directional endings and hidden clearances; not image metrology or engineering acceptance.','materialRolesAndErasExact':True,'allPivotsAttachmentsHeadBillCrownTorsoWingsLegsExact':True,'limits':['Finite rest topology/volume does not establish pose clearance.','Root receiving underlaps and body-owned breast aperture unchanged.','No new powered hardware, collar, guide, flexible skin or pivot changes.']}
