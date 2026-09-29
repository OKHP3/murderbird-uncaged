"""Coherent rest-shape proposal: larger head seated on shorter curved neck.

This authors rigid geometry AND its pivots together once. Runtime does not
scale/stretch the assembled metal. Numbers are modeling choices, not image
measurements. Apply after the V28 guard reconstruction.
"""
import bpy,json
from mathutils import Vector

NECK_FACTOR=.78
HEAD_FACTOR=1.12

def apply():
 bpy.context.view_layer.update()
 neck=bpy.data.objects['neck'];head=bpy.data.objects['head']
 descendants=list(neck.children_recursive)
 affected=[neck]+descendants
 head_names={head.name}|{o.name for o in head.children_recursive}
 matrices={o.name:o.matrix_world.copy() for o in bpy.data.objects}
 vertices={o.name:[matrices[o.name]@v.co for v in o.data.vertices] for o in affected if o.type=='MESH'}
 root=matrices[neck.name].translation.copy();head_origin=matrices[head.name].translation.copy()
 def cervical(p):
  p=p.copy();p.z=root.z+(p.z-root.z)*NECK_FACTOR;return p
 new_head=cervical(head_origin)
 def mapped(name,p):return new_head+(p-head_origin)*HEAD_FACTOR if name in head_names else cervical(p)
 joint_names=['neck','cervical-mid-a','cervical-mid-b','cervical-upper','head']
 bearing_centers={n:sum(points,Vector())/len(points) for n,points in vertices.items() if bpy.data.objects[n].get('surfaceRole')=='bearing' and n not in head_names}
 head_interface={'V21 head captive shaft','V23 cervical 4 captive pin'}
 def mesh_point(o,p):
  if o.name in head_interface:return p+new_head-head_origin
  if o.name in bearing_centers:
   c=bearing_centers[o.name];return p+cervical(c)-c
  if ' load link ' in o.name and o.name.startswith('V23 cervical '):
   i=int(o.name.split()[2])-1;side=int(o.name.split()[-1]);a=matrices[joint_names[i]].translation.copy();b=matrices[joint_names[i+1]].translation.copy();a.x=b.x=side*.053
   aa=cervical(a);bb=cervical(b);old_axis=(b-a).normalized();new_axis=(bb-aa).normalized();along=(p-a).dot(old_axis)
   return aa+new_axis*(along*(bb-aa).length/(b-a).length)+old_axis.rotation_difference(new_axis)@(p-a-old_axis*along)
  return mapped(o.name,p)
 def depth(o):
  n=0
  while o.parent:n+=1;o=o.parent
  return n
 joints=[]
 for o in sorted(affected,key=depth):
  m=matrices[o.name].copy();m.translation=mapped(o.name,m.translation)
  o.matrix_world=m;bpy.context.view_layer.update()
  if o.type=='EMPTY':joints.append({'name':o.name,'oldWorld':list(matrices[o.name].translation),'newWorld':list(m.translation),'orientationPreserved':True})
 for o in affected:
  if o.type!='MESH':continue
  inv=o.matrix_world.inverted()
  for v,p in zip(o.data.vertices,vertices[o.name]):v.co=inv@mesh_point(o,p)
  o.data.update()
 bpy.context.view_layer.update()
 bearing_errors={}
 for n in set(bearing_centers)|head_interface:
  o=bpy.data.objects[n];old=vertices[n];new=[o.matrix_world@v.co for v in o.data.vertices];delta=new[0]-old[0]
  bearing_errors[n]=max((b-a-delta).length for a,b in zip(old,new));assert bearing_errors[n]<1e-6,n
 untouched=[o.name for o in bpy.data.objects if o not in affected]
 assert all(max(abs(o.matrix_world[i][j]-matrices[o.name][i][j]) for i in range(4) for j in range(4))<1e-6 for o in bpy.data.objects if o.name in untouched)
 return {'region':'head and cervical rest proportions','status':'Whole-character silhouette proposal; owner and movement acceptance pending',
  'changedMeshes':list(vertices),'changedNodes':joints,'added':[],'removed':[],
  'headUniformAuthoringFactor':HEAD_FACTOR,'neckVerticalAuthoringFactor':NECK_FACTOR,
  'headRestDisplacement':list(new_head-head_origin),'fixedRoot':list(root),
  'circularBearingMeshesTranslatedWithoutDeformation':sorted(bearing_centers),
  'headCervicalInterfaceMeshesTranslatedWithoutResizing':sorted(head_interface),
  'maximumBearingPureTranslationErrorM':max(bearing_errors.values()),
  'reference':'Owner whole-bird controls substantial head integrated with curved throat; July controls head construction only.',
  'construction':'Existing rigid assemblies remain independent. Geometry and pivot/marker rest positions authored together. Neck bearings and head interface shafts translate without resizing; links shorten along their axes with circular sections retained. No runtime scaling or metal deformation.',
  'eraEligibility':'Existing materials, roles and era tags unchanged; no new components.',
  'limits':['Qualitative silhouette proposal, not dimensions recovered from perspective art.','Shorter cervical members require renewed movement and clearance review.','Contact solver reach must be rerun on exported geometry.']}
