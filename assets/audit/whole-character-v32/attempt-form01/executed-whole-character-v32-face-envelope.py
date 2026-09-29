"""V32 editable bill, formed mandible and nested orbital plates.

Direct native metre/Z-up profiles, based on the V31 head's retained joint.
Owner whole-bird controls nearly closed rest; July controls head construction
and the open pose only. These coordinates are authored, not image dimensions.
"""
from pathlib import Path
import bpy,bmesh,runpy,math,json,hashlib
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2]
BILL=[(-.285,.341,-.238,.190,.092),(-.328,.328,-.270,.172,.101),(-.369,.301,-.300,.158,.095),(-.398,.245,-.326,.147,.079),(-.414,.175,-.350,.139,.063),(-.402,.115,-.359,.120,.042),(-.375,.078,-.358,.103,.023),(-.346,.062,-.347,.074,.002)]
JAW=[(.118,-.135,.202,.017),(.122,-.188,.195,.019),(.116,-.234,.179,.022),(.104,-.272,.159,.019),(.082,-.298,.148,.017),(.061,-.318,.140,.016),(.047,-.336,.133,.012),(.032,-.345,.131,.009),(.017,-.352,.132,.004)]

def apply():
 helper=ROOT/'scripts/regions/whole-character-v31-head-reconstruction.py'
 assert hashlib.sha256(helper.read_bytes()).hexdigest()=='76c8bad1825ede7cf3fac5d068ab60f29a4e8e5059a78dfc5a9cabfd03d39022'
 h=runpy.run_path(str(helper))
 h['blade'].__globals__['BILL']=BILL
 origin=bpy.data.objects['head'].matrix_world.translation.copy()
 oldnames=['V31 formed upper bill course '+str(i) for i in range(3)]+['V31 formed curved mandible shell']
 oldnames += [o.name for o in bpy.data.objects if o.name.startswith(('V31 formed diagonal orbital facade ','V31 optic structural outer seat ','V31 swept dorsal crown course ','V31 swept temporal fan '))]
 protected={o.name:h['snap'](o) for o in bpy.data.objects if o.type=='MESH' and o.name not in oldnames}
 nodes={o.name:h['node'](o) for o in bpy.data.objects if o.type=='EMPTY'}
 originals={n:bpy.data.objects[n] for n in oldnames}
 templates={k:{'props':dict(originals[n].items()),'materials':list(originals[n].data.materials)} for k,n in [('plate','V31 formed upper bill course 0'),('jaw','V31 formed curved mandible shell'),('bearing','V31 optic structural outer seat 1')]}
 for o in originals.values():bpy.data.objects.remove(o,do_unlink=True)
 added=[];solids=[]
 def add(name,owner,geo,kind='plate',role='plate',smooth=False):
  points,faces=geo;mesh=bpy.data.meshes.new(name+' mesh');o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.parent=bpy.data.objects[owner];o.matrix_basis=Matrix.Identity(4);bpy.context.view_layer.update();inv=o.matrix_world.inverted();mesh.from_pydata([inv@(origin+Vector(p)) for p in points],[],faces);mesh.update()
  for m in templates[kind]['materials']:mesh.materials.append(m)
  for k,v in templates[kind]['props'].items():o[k]=v
  o['region']='head';o['surfaceRole']=role;o['proposal']=True;o['constructionOwner']=owner;o['constructionDescription']='V32 near-closed profile, finite formed rigid surface';o['exteriorEras']='maker,mechanic,builder';o['constructionClass']='inherited-passive'
  bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  volume=bm.calc_volume(signed=True);assert volume>0,name;bm.to_mesh(mesh);bm.free()
  for f in mesh.polygons:f.use_smooth=smooth and len(f.vertices)==4
  added.append(name);solids.append({'name':name,'owner':owner,'closed':True,'positiveVolumeM3':volume});return o
 for i,(a,b,hollow) in enumerate([(0,.355,True),(.360,.710,True),(.715,1,False)]):add(f'V32 returned upper bill course {i}','upper-bill',h['blade'](a,b,hollow))
 def jawfn(u,v):
  x,y,z,_=h['sample'](JAW,u);t=2*v-1;depth=.042*(1-u)+.012*u
  # A broad bottom and near-vertical formed flanks give the lower mandible
  # visible area. The upper lip remains an open, functional mouth cavity.
  return Vector((x*t,y,z-depth*(1-t*t*t*t)))
 add('V32 formed mandibular bowl','jaw',h['finite_sheet'](jawfn,nu=52,nv=32,wall=.0045,reference=lambda p:Vector((p.x,0,-.25))),'jaw')
 outer=h['ORBIT_OUTER'];eye=h['EYE'];cy,cz=eye[1:]
 def orbit_sector(side,lo,hi,brow):
  def fn(u,v):
   angle=lo+(hi-lo)*u;c=math.cos(angle);s=math.sin(angle);q=(angle%math.tau)/math.tau*8;i=int(q);f=q-i;a,b=outer[i%8],outer[(i+1)%8];oy=a[0]*(1-f)+b[0]*f;oz=a[1]*(1-f)+b[1]*f
   # The independent upper lip shelters the lens from above. The lower
   # cheek does not reproduce a complete external circular spectacle.
   iy=cy+.046*c;iz=cz+.043*s-(.006*max(0,s) if brow else 0)
   y=iy*(1-v)+oy*v;z=iz*(1-v)+oz*v
   x=(.155 if brow else .147)*(1-v)+(.122+.009*s-.008*c)*v+.008*math.sin(math.pi*v)
   return Vector((side*x,y,z))
  return h['finite_sheet'](fn,nu=48,nv=12,wall=.005,side=side)
 for side in (-1,1):
  add(f'V32 slanted orbital brow {side}','head',orbit_sector(side,.15,3.00,True))
  add(f'V32 swept orbital cheek {side}','head',orbit_sector(side,3.06,5.85,False))
  add(f'V32 recessed optic bearing {side}','head',h['annular'](side,cy,cz,[(.135,.036),(.138,.046),(.130,.049),(.125,.038)]),'bearing','bearing',True)
 # Smaller tapered courses describe the swept crown without repeating the
 # torso or wing treatment. The independently opening cap stays distinct.
 for row,(a,b) in enumerate([(-.285,-.066),(-.132,.077),(.000,.166)]):
  for col in range(7):
   center=.805+col*.255;stagger=(.009 if col%2 else -.008)*(1 if row%2 else -1)
   aa=a+stagger;bb=b+stagger*.5
   if row==0 and col in (0,1,5,6):aa=max(aa,-.252)
   if row==0 and col in (0,6):center+=(.09 if col==0 else -.09)
   width=.247;tip=.36-.05*row+.04*(col%2)
   add(f'V32 swept crown plate {row} {col}','cranial-cover',h['crown'](aa,bb,center-width/2,center+width/2,.011+row*.006+(.017 if row==0 and col in (0,6) else 0)+(.009 if row==1 and col in (0,6) else 0),tip,(col-3)*.007,root=.96),smooth=True)
 for side in (-1,1):
  for i,(a,b,theta) in enumerate([(-.19,.08,.66),(-.145,.119,.43),(-.102,.151,.20),(-.057,.164,-.03),(-.012,.171,-.26)]):
   lo,hi=theta-.155,theta+.155;lean=-.05
   if side==-1:lo,hi=math.pi-hi,math.pi-lo;lean=-lean
   add(f'V32 swept temporal plate {side} {i}','head',h['crown'](a,b,lo,hi,.015+i*.003,.30,lean,root=.92),smooth=True)
 # Replace stale V31 guides only in this new derivative. The earlier native
 # remains unchanged. Each actual profile has an editable three-dimensional
 # curve in the same coordinate space as the finite generated surfaces.
 for o in list(bpy.data.objects):
  if o.get('authoringGuide') is True and o.type=='CURVE':bpy.data.objects.remove(o,do_unlink=True)
 for label,points in [('dorsal-bill',[(0,q[0],q[1]) for q in BILL]),('cutting-seat',[(0,q[2],q[3]) for q in BILL]),('mandible-lip',[(q[0],q[1],q[2]) for q in JAW])]:
  data=bpy.data.curves.new('V32 authoring '+label,'CURVE');data.dimensions='3D';sp=data.splines.new('POLY');sp.points.add(len(points)-1);o=bpy.data.objects.new(data.name,data);bpy.context.scene.collection.objects.link(o);o.parent=bpy.data.objects['head'];o.matrix_basis=Matrix.Identity(4);bpy.context.view_layer.update();inv=o.matrix_world.inverted()
  for v,p in zip(sp.points,points):v.co=(*list(inv@(origin+Vector(p))),1)
  o.hide_render=True;o.hide_viewport=False;o['authoringGuide']=True;o['exportExclude']=True;o['profileSource']='V32 direct authored native profile'
 # Preserve a true moving-surface external control declaration after jaw
 # reconstruction. The lever socket is an exact finite vertex, not a guess.
 bpy.context.view_layer.update();jaw=bpy.data.objects['jaw'];receiver=bpy.data.objects['V32 formed mandibular bowl'];aim=origin+Vector((-.110,-.225,.170));socket=min((receiver.matrix_world@v.co for v in receiver.data.vertices),key=lambda p:(p-aim).length);local=jaw.matrix_world.inverted()@socket
 jaw['makerControlSocketV1']=json.dumps({'schema':1,'point':[local.x,local.z,-local.y],'coordinateSpace':'gltf-node-local','surfaceObject':receiver.name,'status':'reconstructed external control attachment'},sort_keys=True)
 # The complete body layout must agree with the explicit owner override.
 body=bpy.data.objects['body'];layout=json.loads(body['mechanismLayoutV1']);layout['makerControlOffsets']['jaw']=[local.x,local.z,-local.y];body['mechanismLayoutV1']=json.dumps(layout,sort_keys=True)
 dg=bpy.context.evaluated_depsgraph_get();front=None
 for name in added:
  o=bpy.data.objects[name]
  if o.parent.name!='upper-bill':continue
  ev=o.evaluated_get(dg);mesh=ev.to_mesh()
  for v in mesh.vertices:
   p=ev.matrix_world@v.co
   if front is None or p.y<front.y:front=p.copy()
  ev.to_mesh_clear()
 for n in ('bill-contact','anchor-beak'):
  o=bpy.data.objects[n];m=o.matrix_world.copy();m.translation=front;o.matrix_world=m
 bpy.context.view_layer.update()
 allowed={'jaw','body','bill-contact','anchor-beak'}
 assert all(h['node'](bpy.data.objects[n])==r for n,r in nodes.items() if n not in allowed)
 assert all(h['snap'](bpy.data.objects[n])==r for n,r in protected.items())
 return {'region':'head-face-envelope','status':'Visible shape proposal; neither fit nor owner acceptance','changedNodes':sorted(allowed),'removed':oldnames,'added':added,'changedMeshes':[],'finiteSolids':solids,'billProfile':BILL,'jawProfile':JAW,'headOrigin':list(origin),'materialsChanged':False,'protectedMeshesExact':len(protected),'restingJaw':0,'makerJawSocket':json.loads(jaw['makerControlSocketV1']),'limits':['Qualitative perspective-reference interpretation, no recovered dimensions.','No body, neck, rig or era capability changes.','Fresh jaw/crown/neck articulation screens required after visual gate.']}
