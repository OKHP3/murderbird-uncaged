from pathlib import Path
R=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
a=(R/'scripts/regions/whole-character-v26-head-selected.py').read_text();b=(R/'scripts/regions/whole-character-v27-cranial-wrap.py').read_text()
utilities=a[a.index('def sample'):a.index('def apply():')]
curved=b[b.index('def section'):b.index('def props')]
# Curved functions are self-contained authored construction, frozen into this file.
s='''"""V30 major head-form study. July controls head; owner whole-bird controls closed rest.
Editable pre-mass profile coordinates are baked into the retained V29 head mass.
No runtime deformation, head-root movement, new materials or body edits.
"""\nimport bpy,bmesh,math,json\nfrom mathutils import Vector\nfrom mathutils.geometry import tessellate_polygon\nOWNERS={'head','jaw','upper-bill','cranial-cover','builder-optics'}\nBOUNDARY={'V21 head captive shaft','V23 cervical 4 captive pin'}\nBILL=[(-.526,1.825,-.526,1.715,.090),(-.569,1.817,-.548,1.699,.096),(-.611,1.791,-.564,1.684,.085),(-.642,1.751,-.578,1.670,.067),(-.649,1.704,-.594,1.650,.048),(-.639,1.662,-.608,1.629,.031),(-.616,1.628,-.609,1.618,.014),(-.594,1.607,-.596,1.603,.0025)]\nPROFILE=[(-.574,1.776,.100,.050),(-.505,1.777,.149,.081),(-.429,1.765,.153,.112),(-.352,1.746,.146,.115),(-.279,1.718,.118,.092),(-.216,1.687,.075,.047)]\n'''+utilities+curved
s+='''
def narrow_receiver(side):
 def fn(u,v):
  a=math.tau*v;co=math.cos(a);si=math.sin(a)
  # Deliberately asymmetric shallow seat: substantial diagonal upper/back
  # receiver, narrow lower/front return, rather than a blank full eye disk.
  outer=.056+.013*max(0,si)+.007*max(0,co)
  r=.048*(1-u)+outer*u;y=-.5055+r*co;z=1.756+r*si
  x=(.126+.005*si)*(1-u)+(facade_x(y,z)-.005)*u
  return Vector((side*x,y,z))
 return closed_patch(fn,nu=10,nv=72,wall=.004,periodic=True,side=side)

def apply():
 bpy.context.view_layer.update();pivot=bpy.data.objects['head'].matrix_world.translation.copy()
 oldpivot=Vector((0,-.3226,1.6028));factor=1.456
 nodes={o.name:node(o) for o in bpy.data.objects if o.type=='EMPTY'}
 targets=['Profiled upper bill blade 0','Overlapping nasal hood','Profiled upper bill blade 1','Distal mandible bridge']+[f'{p} {side}' for p in ('Cere root transition','Forked forged mandible','Forged orbital brow','Broad swept cheek band','Forged orbital mounting plate','V24 anterior orbital root receiver') for side in (-1,1)]
 capnames=['V27 fixed frontal cranial receiving return','V27 dorsal swept cranial course 0','V27 dorsal swept cranial course 1','V27 dorsal swept cranial course 2']
 protected={o.name:snap(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in set(targets+capnames)}
 changed=[];errors=[]
 def mapped(p):return pivot+factor*(Vector(p)-oldpivot)
 def install(n,v,f):
  o=bpy.data.objects[n];assert o.parent and o.parent.name in OWNERS
  bpy.context.view_layer.update();inv=o.matrix_world.inverted();world=[mapped(p) for p in v]
  m=bpy.data.meshes.new(n+' V30 formed solid');m.from_pydata([inv@p for p in world],[],f);m.update()
  for material in o.data.materials:m.materials.append(material)
  bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
  assert all(e.is_manifold for e in bm.edges),n
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  assert bm.calc_volume(signed=True)>0,n
  bm.to_mesh(m);bm.free();o.data=m;o.modifiers.clear()
  for face in m.polygons:face.use_smooth=len(face.vertices)==4
  errors.append(max((o.matrix_world@q.co-p).length for q,p in zip(m.vertices,world)));changed.append(n)
 for n,a,b,hollow in [('Profiled upper bill blade 0',0,.345,True),('Overlapping nasal hood',.349,.715,True),('Profiled upper bill blade 1',.719,1,False)]:
  v,f=bill(a,b,hollow);install(n,v,f)
 for side in (-1,1):
  v,f=ribbon(side,[(.093,-.527,1.803,.014),(.098,-.557,1.774,.018),(.083,-.580,1.736,.017),(.062,-.593,1.689,.009)],wall=.0045);install(f'Cere root transition {side}',v,f)
  # Rear jaw is inboard of the unchanged orbital races; closed distal edge
  # follows the blade's posterior curve, while the original hinge opens it.
  v,f=ribbon(side,[(.119,-.432,1.663,.020),(.097,-.470,1.670,.014),(.075,-.514,1.681,.011),(.061,-.555,1.679,.010),(.049,-.580,1.660,.008),(.031,-.597,1.637,.005),(.021,-.605,1.621,.0025)],wall=.005,along=40);install(f'Forked forged mandible {side}',v,f)
  outline=[(-.374,1.810),(-.397,1.847),(-.438,1.850),(-.478,1.829),(-.519,1.811),(-.546,1.795),(-.550,1.782),(-.535,1.791),(-.520,1.803),(-.502,1.811),(-.484,1.807),(-.465,1.792),(-.446,1.795),(-.418,1.807),(-.396,1.793)]
  v,f=face_sheet(side,outline,wall=.005);install(f'Forged orbital brow {side}',v,f)
  outline=[(-.407,1.783),(-.429,1.745),(-.456,1.721),(-.483,1.711),(-.510,1.709),(-.540,1.719),(-.565,1.735),(-.584,1.730),(-.567,1.707),(-.538,1.696),(-.509,1.695),(-.479,1.700),(-.447,1.720),(-.422,1.750),(-.398,1.775)]
  v,f=face_sheet(side,outline,wall=.005);install(f'Broad swept cheek band {side}',v,f)
  v,f=narrow_receiver(side);install(f'Forged orbital mounting plate {side}',v,f)
  outline=[(-.543,1.792),(-.552,1.800),(-.569,1.779),(-.578,1.741),(-.567,1.724),(-.556,1.741),(-.553,1.770)]
  v,f=face_sheet(side,outline,wall=.004);install(f'V24 anterior orbital root receiver {side}',v,f)
 v,f=crown_sheet([(-.597,1.633,.028),(-.603,1.626,.024),(-.607,1.620,.020)]);install('Distal mandible bridge',v,f)
 # Lower the anterior roof into the diagonal brow. Retain the swept aft
 # crown courses exactly: this is a seated forehead correction, no curtain.
 specs=[('V27 fixed frontal cranial receiving return',(-.552,-.397,.80,math.pi-.80,.002,.88,0,.87,None)),('V27 dorsal swept cranial course 0',(-.550,-.354,1.12,2.02,.022,.43,.04,.72,.007)),('V27 dorsal swept cranial course 1',(-.491,-.286,.82,1.41,.017,.40,-.08,.91,None)),('V27 dorsal swept cranial course 2',(-.495,-.295,1.73,2.32,.017,.34,.10,.91,None))]
 for n,(a,b,lo,hi,off,tip,lean,rw,seat) in specs:
  v,f=skull_band(a,b,lo,hi,off,tip=tip,lean=lean,root_width=rw,seat_front=seat);install(n,v,f)
 bpy.context.view_layer.update();front=None;frontname=None;dg=bpy.context.evaluated_depsgraph_get()
 for o in bpy.data.objects:
  if o.type=='MESH' and o.parent and o.parent.name=='upper-bill':
   ev=o.evaluated_get(dg);mesh=ev.to_mesh()
   for v in mesh.vertices:
    p=ev.matrix_world@v.co
    if front is None or p.y<front.y:front=p.copy();frontname=o.name
   ev.to_mesh_clear()
 for n in ('bill-contact','anchor-beak'):
  o=bpy.data.objects[n];m=o.matrix_world.copy();m.translation=front;o.matrix_world=m
 bpy.context.view_layer.update()
 assert protected=={n:snap(bpy.data.objects[n]) for n in protected}
 assert all(node(bpy.data.objects[n])==v for n,v in nodes.items() if n not in ('bill-contact','anchor-beak'))
 return {'region':'head-major-form','status':'Coarse visual proposal, likeness and movement HOLD','changedMeshes':changed,'added':[],'removed':[],'changedNodes':['bill-contact','anchor-beak'],'primaryPivotChanges':[],'outsideAndUnselectedMeshesExact':len(protected),'headRootAndCervicalInterfaceExact':True,'materialDefinitionsChanged':False,'eraEligibilityChanged':False,'billContactNativeWorld':list(front),'contactObject':frontname,'contactMethod':'minimum nativeY evaluated upper-bill surface vertex','maximumAuthoredWorldErrorM':max(errors),'transformContract':{'authoredOrigin':list(oldpivot),'currentOrigin':list(pivot),'bakedUniformHeadFactor':factor,'nodeScaling':'none','jawHinge':'unchanged'},'billProfile':BILL,'foreheadProfile':PROFILE,'limits':['First coarse visible candidate; no full collision or motion clearance claim.','Hidden receiving surfaces are proposals. Crown opening remains independent and requires fresh checks.']}
'''
(R/'scripts/regions/whole-character-v30-head-form.py').write_text(s)
