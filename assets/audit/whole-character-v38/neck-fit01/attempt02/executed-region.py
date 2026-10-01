import bpy,math,bmesh,runpy
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[2]
SCOPE=['V23 cervical 3 captive pin']+[f'V23 cervical 3 {kind} {side}'for kind in ['distal race','load link']for side in [-1,1]]+[f'V31 {kind} {side}'for kind in ['cranial load bow shaft seat','passive cranial load bow']for side in [-1,1]]
def apply():
 bpy.context.view_layer.update();records=[]
 def shift(o,func):
  inv=o.matrix_world.inverted();old=[o.matrix_world@v.co for v in o.data.vertices]
  for v,p in zip(o.data.vertices,old):v.co=inv@func(p.copy())
  o.data.update()
 for side in [-1,1]:
  o=bpy.data.objects[f'V23 cervical 3 distal race {side}'];shift(o,lambda p:p+Vector((-side*.011,0,0)));records.append({'name':o.name,'axialCenterM':side*.044,'pairedRingWallRadiiM':[.010,.024],'YZBearingCentreNative':[-.356,1.423],'sectionPreserved':True})
 o=bpy.data.objects['V23 cervical 3 captive pin'];shift(o,lambda p:Vector((p.x*.056/.070,p.y,p.z)));records.append({'name':o.name,'axialLimitsM':[-.056,.056],'sourceSymmetricRetainerExtensionM':.0055,'actualSymmetricRetainerExtensionM':.0055,'note':'44mm race centre+6.5mm axial halfstock+5.5mm retainer; radius/YZ unchanged'})
 cylinder=runpy.run_path(str(R/'assets/audit/whole-character-v38/neck-profile01/executed-region.py'))['cylinder']
 for side in [-1,1]:
  o=bpy.data.objects[f'V23 cervical 3 load link {side}'];a=Vector((side*.053,-.307,1.349));direction=Vector((0,.049,-.080)).normalized();b=Vector((side*.044,-.356,1.423))+direction*.018;records.append(cylinder(o,a,b,.006))
  o=bpy.data.objects[f'V31 cranial load bow shaft seat {side}'];shift(o,lambda p:p+Vector((-side*.030,0,0)));records.append({'name':o.name,'axialCenterM':side*.022,'additionalAxialDeltaM':-side*.030,'sectionAndYZExact':True,'nominalMaxRadiusFromHeadCentreM':math.hypot(.028,.017),'upperSocketInnerRadiusM':.0332,'qualification':'Nominal radius permitsrest packaging; actual finite moving surface screen required'})
  o=bpy.data.objects[f'V31 passive cranial load bow {side}'];affected=[]
  def form(p):
   t=max(0,min(1,(1.610-p.z)/.036));t=t*t*(3-2*t)
   if t>0:affected.append(p.z)
   return p+Vector((-side*.030*t,0,0))
  shift(o,form);records.append({'name':o.name,'additionalRootAxialDeltaM':-side*.030,'constantThroughNativeZ':1.574,'falloffEndsNativeZ':1.610,'affectedVertices':len(affected),'upperFrameAbove1_610Exact':True,'receivingRoute':'Seat and lower bow receive same30mm translation; actual finite common stock checked separately'})
 for n in SCOPE:
  o=bpy.data.objects[n];o['v38NeckFit01']='Final calculated axial fit proposal: unchanged5shells/pivots, source5.5mm pin retainer,22mm head seats, bow branch transition endsZ1.610; qualified finite screen'
  bm=bmesh.new();bm.from_mesh(o.data);records.append({'stockTopologyName':n,'connectedComponents':components(bm),'nonmanifoldEdges':sum(not e.is_manifold for e in bm.edges),'signedVolumeM3':bm.calc_volume(signed=True)});bm.free()
 return {'status':'Final structural-fit PROPOSAL, no armor/owner acceptance','changedMeshes':SCOPE,'changedStock':records,'calculationSource':'../calculated-placement.json, finite vertex-derived inner envelope bound with1mm radial margin; pin chosen shorter toretain source retainer','preserved':'All5shell geometry/transforms and all ownerrest/pivots/othergeometry/materials','limits':['Four owner-rigid proxy seams still have no articulated sliding-lap fit.','Axial fit samples are not swept/strength/service or compoundyaw certification.','Bow root footprint refit extends toZ1.610 explicitly; head frame above remains exact.']}

def components(bm):
 unseen=set(bm.verts);count=0
 while unseen:
  count+=1;todo=[unseen.pop()]
  while todo:
   v=todo.pop()
   for e in v.link_edges:
    n=e.other_vert(v)
    if n in unseen:unseen.remove(n);todo.append(n)
 return count
