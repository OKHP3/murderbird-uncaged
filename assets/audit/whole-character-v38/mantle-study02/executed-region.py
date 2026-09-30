"""Directional mantle envelope:52 existing finite plates, exact rigid ownership.
No elbow, breast, supporting frame, pivot, era/material or head/neck change.
"""
import bpy,bmesh,math
from mathutils import Vector
NAMES=[f'V38 {side} mantle layered course {course} plate {plate}' for side in ['left','right'] for course,count in [(1,5),(2,6),(3,6),(4,5),(5,4)] for plate in range(1,count+1)]
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
RETURNS={('left',2,1),('right',2,1),('left',3,1),('right',3,1),('left',3,2),('right',4,1),('left',5,1),('left',5,2),('right',5,2)}
def apply():
 bpy.context.view_layer.update();records=[]
 for name in NAMES:
  o=bpy.data.objects[name];side='left' if 'left' in name else 'right';assert o.parent.name==side+'-mantle' and len(o.data.vertices)==286
  source=[v.co.copy() for v in o.data.vertices];world=o.matrix_world.copy();inv=world.inverted();outer=[world@p for p in source[:143]];inner=[world@p for p in source[143:]];stocks=[a-b for a,b in zip(outer,inner)];zero=[i for i,v in enumerate(stocks) if v.length<1e-10];assert all(v.length<1e-10 or abs(v.length-.005)<2e-7 for v in stocks)
  valid=[i for i,v in enumerate(stocks) if v.length>1e-10]
  for i in zero:
   nearest=min(valid,key=lambda j:(i//11-j//11)**2+(i%11-j%11)**2);stocks[i]=stocks[nearest].normalized()*.005
  o.data=o.data.copy();displacements=[]
  for i,p in enumerate(outer):
   depth=max(0,min(1,(1.33-p.z)/.42));posterior=smooth((p.y+.04)/.32);anterior=1-smooth((p.y+.04)/.22);upper=smooth((p.z-1.08)/.23)
   # Flatten the upper crest, draw its leading side into the upper-breast
   # junction, then sweep the lower rear course away/down along the flank.
   delta=Vector((0,-.11*anterior*upper+.07*posterior*(.2+.8*depth),(.045-.30*(p.z-1.28))*upper*(1-.65*posterior)-.025*depth*posterior))
   course=int(name.split(' course ')[1].split()[0]);plate=int(name.split(' plate ')[1]);
   if (side,course,plate) in RETURNS:delta=Vector((0,0,0))
   target=p+delta;o.data.vertices[i].co=inv@target;o.data.vertices[i+143].co=inv@(target-stocks[i]);displacements.append(delta.length)
  o.data.update();bm=bmesh.new();bm.from_mesh(o.data);closed=all(e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free();assert closed and volume>0,name
  stock=[((world@o.data.vertices[i].co)-(world@o.data.vertices[i+143].co)).length for i in range(143)];assert max(abs(t-.005) for t in stock)<2e-7
  o['v38MantleEnvelope']='mantle-study02 flatter forward shoulder connection and diagonal rear/down flank sweep; rigid inherited plate; fit and likeness pending'
  records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'constructionClass':o.get('constructionClass'),'surfaceRole':o.get('surfaceRole'),'materials':[m.name for m in o.data.materials],'vertexScope':'All286 vertices of existing finite plate; paired143 outer/inner vertices, original connectivity retained.','sourcePositionReceivingReturn':(side,course,plate) in RETURNS,'maximumAuthoredOuterMovementM':max(displacements),'inheritedZeroStockPairsReconstructed':zero,'zeroPairReconstruction':'Nearest nonzero source stock direction on actual13x11 grid,5mm finite vector; all nonzero source stock vectors retained.','minimumPairedStockM':min(stock),'maximumPairedStockM':max(stock),'finiteClosed':closed,'positiveVolumeM3':volume})
 return {'changedMeshes':NAMES,'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'attachmentAndEraMap':records,'allOtherGeometryPivotsMaterialsEraIdentityExact':True,'rigidVsFlexible':'Authored reshaped finite rigid plates on original matching mantle owners; no skins/flexible metal or runtime deformation. Elbow-owned parts exact.','confirmed':'Master03/Maker-clean/Mechanic show broad compact layered mantle with flatter shoulder top and diagonal progression down flank. July head-only.','reconstruction':'Exact unseen surfaces, outline/receiving joints and stock are authored proposals; no reference metrology or accepted engineering.','clearanceScope':'Actual supporting structures, elbows, inspection nodes, stops and left repair landmark preserved. No cross-owner bridge; sampled surface review still needed.','limits':['No uniform cap scale or extra decorative row; original52 layered identities retained.','No new flight surface or long train.','Finite topology/stock and unchanged pivots do not establish continuous pose clearance or inspection clearance.']}
