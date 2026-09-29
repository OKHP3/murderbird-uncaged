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
  for v,p in zip(o.data.vertices,vertices[o.name]):v.co=inv@mapped(o.name,p)
  o.data.update()
 bpy.context.view_layer.update()
 untouched=[o.name for o in bpy.data.objects if o not in affected]
 assert all(max(abs(o.matrix_world[i][j]-matrices[o.name][i][j]) for i in range(4) for j in range(4))<1e-6 for o in bpy.data.objects if o.name in untouched)
 return {'region':'head and cervical rest proportions','status':'Whole-character silhouette proposal; owner and movement acceptance pending',
  'changedMeshes':list(vertices),'changedNodes':joints,'added':[],'removed':[],
  'headUniformAuthoringFactor':HEAD_FACTOR,'neckVerticalAuthoringFactor':NECK_FACTOR,
  'headRestDisplacement':list(new_head-head_origin),'fixedRoot':list(root),
  'reference':'Owner whole-bird controls substantial head integrated with curved throat; July controls head construction only.',
  'construction':'Existing rigid assemblies remain independent. Geometry and pivot/marker rest positions authored together. No runtime scaling or metal deformation.',
  'eraEligibility':'Existing materials, roles and era tags unchanged; no new components.',
  'limits':['Qualitative silhouette proposal, not dimensions recovered from perspective art.','Shorter cervical members require renewed movement and clearance review.','Contact solver reach must be rerun on exported geometry.']}
