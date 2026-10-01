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
  o.data.update();return old
 for side in [-1,1]:
  o=bpy.data.objects[f'V23 cervical 3 distal race {side}'];old=shift(o,lambda p:p+Vector((-side*.016,0,0)));center=Vector((side*.071,-.356,1.423));radii=[math.hypot(p.y-center.y,p.z-center.z)for p in old];records.append({'name':o.name,'owner':o.parent.name,'axialDeltaM':-side*.016,'sectionRadiusRangeM':[min(radii),max(radii)],'bearingYZExact':True})
 o=bpy.data.objects['V23 cervical 3 captive pin'];old=shift(o,lambda p:Vector((p.x*.070/.083,p.y,p.z)));records.append({'name':o.name,'owner':o.parent.name,'oldAxialLimitsM':[-.083,.083],'newAxialLimitsM':[-.070,.070],'radiusAndYZExact':True,'nominalEqualRetainerExtensionBeyondRaceM':.0085})
 cylinder=runpy.run_path(str(R/'assets/audit/whole-character-v38/neck-profile01/executed-region.py'))['cylinder']
 for side in [-1,1]:
  o=bpy.data.objects[f'V23 cervical 3 load link {side}'];a=Vector((side*.053,-.307,1.349));direction=Vector((0,.049,-.080)).normalized();b=Vector((side*.055,-.356,1.423))+direction*.018;rec=cylinder(o,a,b,.006);rec['receivingRole']='Distal finite link section enters own annular race stock at lower/front sector; common stock test pending';records.append(rec)
  o=bpy.data.objects[f'V31 cranial load bow shaft seat {side}'];old=shift(o,lambda p:p+Vector((-side*.012,0,0)));records.append({'name':o.name,'owner':o.parent.name,'axialDeltaM':-side*.012,'ringSectionAndYZExact':True})
  o=bpy.data.objects[f'V31 passive cranial load bow {side}'];affected=[]
  def form(p):
   t=max(0,min(1,(1.570-p.z)/.034));t=t*t*(3-2*t)
   if t>0:affected.append(p.z)
   return p+Vector((-side*.012*t,0,0))
  shift(o,form);records.append({'name':o.name,'owner':o.parent.name,'rootMaximumAxialDeltaM':-side*.012,'transitionZNative':[1.536,1.570],'affectedVertices':len(affected),'upperCranialBowAboveZ1_570Exact':True,'seatQualification':'Paired stock route retained/refitted axially; finite intersection and connectivity pending'})
 for n in SCOPE:
  o=bpy.data.objects[n];o['v38NeckFit01']='Passive axial bearing packaging proposal; existing pivot YZ and all shell geometry unchanged; finite seat and service access qualified'
  bm=bmesh.new();bm.from_mesh(o.data);records.append({'stockTopologyName':n,'connectedComponents':components(bm),'nonmanifoldEdges':sum(not e.is_manifold for e in bm.edges),'signedVolumeM3':bm.calc_volume(signed=True)});bm.free()
 return {'status':'Structural-fit proposal under exact frozen simple silhouette; not final articulated armor or accepted likeness','changedMeshes':SCOPE,'changedStock':records,'preserved':'All5 shell geometry/transforms, all articulation transforms, head/breast worldrest, other meshes/materials/era owners','limits':['Four owner-rigid proxy seams are not solved sliding laps.','Service access, structural strength and complete swept motion remain unvalidated.','Upper skull bow above1.570 remains intact and may remain exposed intentionally inside cheek; no shell cutout or hidden stock.']}
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
