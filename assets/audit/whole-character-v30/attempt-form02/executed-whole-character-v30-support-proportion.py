"""V30 neutral structural shortening study, native metres/Z-up.

Author joint rests and finite members together; no crouch pose, runtime scale,
new equipment or material changes. Values are qualitative proposals.
Body/hip -120mm, knee -90mm, ankle -60mm, toes/claws/floor fixed.
"""
import bpy,json,math
from mathutils import Vector

DROP={'body':.12,'thigh':.12,'shin':.09,'foot':.06}
FOOT_MEMBERS=('metatarsal passive rail','metatarsus open passive truss','curved instep guard')

def record(o):
 return {'parent':o.parent.name if o.parent else None,'world':[list(r) for r in o.matrix_world],'local':[list(r) for r in o.matrix_local],'props':json.loads(json.dumps(dict(o.items()),default=lambda x:list(x))),'visible':[o.hide_render,o.hide_viewport]}

def member_map(p,a,b,aa,bb):
 """Shorten only along joint path, rotate unchanged transverse sections."""
 old=(b-a).normalized();new=(bb-aa).normalized();along=(p-a).dot(old);cross=p-a-old*along
 return aa+new*along*((bb-aa).length/(b-a).length)+old.rotation_difference(new)@cross

def apply():
 bpy.context.view_layer.update();nodes=[o for o in bpy.data.objects if o.type=='EMPTY'];assert len(nodes)==54
 old={o.name:o.matrix_world.copy() for o in bpy.data.objects};rests={o.name:record(o) for o in nodes}
 raw={o.name:[v.co.copy() for v in o.data.vertices] for o in bpy.data.objects if o.type=='MESH'}
 body=bpy.data.objects['body'];bodyset={body.name}|{o.name for o in body.children_recursive}
 protected_digits={o.name for side in ('left','right') for o in [bpy.data.objects[f'{side}-toes']]+list(bpy.data.objects[f'{side}-toes'].children_recursive)}
 digitworld={n:old[n].copy() for n in protected_digits};digitmeshes={n:[old[n]@v for v in raw[n]] for n in protected_digits if n in raw}
 targets={};contracts=[]
 for side in ('left','right'):
  a=old[side+'-thigh'].translation.copy();b=old[side+'-shin'].translation.copy();c=old[side+'-foot'].translation.copy();d=old[side+'-toes'].translation.copy()
  aa=a+Vector((0,0,-DROP['thigh']));bb=b+Vector((0,0,-DROP['shin']));cc=c+Vector((0,0,-DROP['foot']))
  targets.update({side+'-thigh':aa,side+'-shin':bb,side+'-foot':cc,side+'-hip-landmark':aa,side+'-knee-landmark':bb,side+'-sole-landmark':cc})
  contracts.extend([{'owner':side+'-thigh','before':[list(a),list(b)],'after':[list(aa),list(bb)],'oldLengthM':(b-a).length,'newLengthM':(bb-aa).length}, {'owner':side+'-shin','before':[list(b),list(c)],'after':[list(bb),list(cc)],'oldLengthM':(c-b).length,'newLengthM':(cc-bb).length}, {'owner':side+'-foot','before':[list(c),list(d)],'after':[list(cc),list(d)],'oldLengthM':(d-c).length,'newLengthM':(d-cc).length}])
 contract={x['owner']:x for x in contracts}
 def depth(o):
  d=0
  while o.parent:d+=1;o=o.parent
  return d
 # Restore each authored WORLD rest explicitly, preventing inherited drops
 # from accumulating down the chain. All original bases/parents remain.
 for o in sorted(nodes,key=depth):
  m=old[o.name].copy()
  if o.name in bodyset:m.translation+=Vector((0,0,-DROP['body']))
  if o.name in targets:m.translation=targets[o.name]
  if o.name in protected_digits:m=old[o.name].copy()
  o.matrix_world=m;bpy.context.view_layer.update()
 geometry=[];rigid=[];footrevised=[];bodytranslated=[];protectedfloor=[];worlderrors={}
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  owner=o.parent.name if o.parent else '';points=[old[o.name]@v for v in raw[o.name]];mapped=None
  if owner in contract:
   row=contract[owner];a,b=[Vector(x) for x in row['before']];aa,bb=[Vector(x) for x in row['after']]
   if owner.endswith(('thigh','shin')):
    role=o.get('surfaceRole');bearing=role in ('bearing','bearing-frame')
    if bearing:
     # Distal captive cheeks belong to upstream owner but seat downstream.
     delta=(bb-b) if 'distal captive cheek' in o.name else (aa-a)
     mapped=[p+delta for p in points];rigid.append(o.name)
    else:
     mapped=[member_map(p,a,b,aa,bb) for p in points];geometry.append(o.name)
   elif any(s.lower() in o.name.lower() for s in FOOT_MEMBERS):
    mapped=[member_map(p,a,b,aa,bb) for p in points];geometry.append(o.name);footrevised.append(o.name)
   elif ('hallux' in o.name.lower()):
    mapped=points;protectedfloor.append(o.name)
   else:
    # Every remaining foot-owned object is local circular ankle hardware.
    assert any(s in o.name.lower() for s in ('bearing','race pin','axle cap')),o.name
    mapped=[p+(aa-a) for p in points];rigid.append(o.name);footrevised.append(o.name)
  elif o.name in bodyset:
   # No body/head/wing skin deformation: their entire assembly is lowered.
   bodytranslated.append(o.name)
  if mapped is not None:
   bpy.context.view_layer.update();inv=o.matrix_world.inverted();o.data=o.data.copy()
   for v,p in zip(o.data.vertices,mapped):v.co=inv@p
   o.data.update();worlderrors[o.name]=max((o.matrix_world@v.co-p).length for v,p in zip(o.data.vertices,mapped))
 bpy.context.view_layer.update()
 # World-space floor descendants retain all raw data and rest attachments.
 errs={n:max((bpy.data.objects[n].matrix_world@v.co-p).length for v,p in zip(bpy.data.objects[n].data.vertices,pts)) for n,pts in digitmeshes.items()}
 assert max(errs.values())<1e-7,errs
 assert all(tuple(v.co)==tuple(before) for n in digitmeshes for v,before in zip(bpy.data.objects[n].data.vertices,raw[n]))
 changednodes=[n for n,s in rests.items() if record(bpy.data.objects[n])!=s]
 for n,s in rests.items():
  o=bpy.data.objects[n];assert (o.parent.name if o.parent else None)==s['parent'],n
  assert max(abs(o.matrix_world[i][j]-old[n][i][j]) for i in range(3) for j in range(3))<1e-7,n
 changedmeshes=sorted(set(geometry+rigid+bodytranslated+protectedfloor))
 return {'region':'neutral-support-proportions','status':'Qualitative structural rest proposal; visual and motion acceptance HOLD','changedNodes':changednodes,'changedMeshes':changedmeshes,'geometryChangedMeshes':geometry,'circularHardwareTranslatedRigidly':rigid,'bodyMeshesTranslatedRigidly':bodytranslated,'footOwnedRevisedMeshes':footrevised,'footOwnedFloorMeshesWorldPreserved':protectedfloor,'protectedDigitMeshesWorldPreserved':sorted(digitmeshes),'protectedDigitNodesWorldPreserved':sorted(n for n in protected_digits if bpy.data.objects[n].type=='EMPTY'),'added':[],'removed':[],'dropContractM':DROP,'memberEndpoints':contracts,'maximumAuthoredWorldErrorM':max(worlderrors.values()),'maximumProtectedDigitWorldErrorM':max(errs.values()),'nodeRestContract':[{'name':n,'beforeWorld':rests[n]['world'],'afterWorld':[list(r) for r in bpy.data.objects[n].matrix_world],'beforeLocal':rests[n]['local'],'afterLocal':[list(r) for r in bpy.data.objects[n].matrix_local]} for n in changednodes],'materialsChanged':False,'eraEligibilityChanged':False,'method':'Body translates rigidly. Circular hardware translates to actual joint. Long members shorten axially with transverse section rotation, never cylindrical joint squashing. Toe/digit/floor geometry fixed. No additional crouch pose.','limits':['Rest-only authored shortening; motion, sockets and travel need fresh validation after visual gate.','Historical leg construction guides are not posed runtime geometry.','The existing named ankle/sole landmark now moves with the ankle; actual floor remains the unchanged toe/claw patches.']}
