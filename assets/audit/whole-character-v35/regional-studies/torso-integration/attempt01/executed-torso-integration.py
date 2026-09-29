"""V35 coarse torso: authored sternum cage, open framed flank and scapular seat.
NativeZ-up/-Yfront; dimensions are proposals, not reference-image metrology.
"""
from pathlib import Path
import bpy,bmesh,math,runpy
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(globals().get('SOURCE_ROOT',Path(__file__).resolve().parents[2]))
# z, anterior retreat, breast-width fraction, posterior retreat. Shared cage
# acts on complete finite surfaces; head/neck/hinge/hip origins remain fixed.
CAGE=((.68,0,1,0),(.76,.008,.97,0),(.86,.030,.91,.005),(.99,.050,.90,.018),(1.09,.035,.95,.024),(1.185,0,1,.020),(1.27,0,1,.006))
def ease(t):t=max(0.,min(1.,t));return t*t*(3-2*t)
def controls(z):
 i=next((i for i in range(len(CAGE)-1) if CAGE[i][0]<=z<=CAGE[i+1][0]),0 if z<CAGE[0][0] else len(CAGE)-2);a,b=CAGE[i:i+2];u=ease((z-a[0])/(b[0]-a[0]));return [a[k]+(b[k]-a[k])*u for k in range(1,4)]
def map_point(p):
 p=Vector(p);retreat,width,back=controls(p.z);front=ease((-p.y-.04)/.20);p.x*=1-(1-width)*front;p.y+=retreat*front-back*ease((p.y+.02)/.12);return p

def apply():
 bpy.context.view_layer.update();h=runpy.run_path(str(ROOT/'scripts/regions/whole-character-v30-breast-form.py'));g=runpy.run_path(str(ROOT/'scripts/regions/whole-character-v28-torso-pelvis.py'));s=runpy.run_path(str(ROOT/'scripts/regions/whole-character-v31-head-reconstruction.py'))
 skins=sorted(o.name for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('V34 formed breast course '));assert len(skins)==33
 removed=[f'V30 long fixed shoulder flank {i}' for i in (-1,1)]+[f'V30 long swept dorsal cheek {i}' for i in (-1,1)]
 changed=skins+['V30 continuous tapered breast liner','V30 continuous dorsal pelvic liner']+[f'V30 breast liner receiving tab {i}' for i in (-1,1)]
 assert all(n in bpy.data.objects for n in changed+removed)
 nodes={o.name:s['node'](o) for o in bpy.data.objects if o.type=='EMPTY'};protected={o.name:s['snap'](o) for o in bpy.data.objects if o.type=='MESH' and o.name not in changed+removed}
 assert (bpy.data.objects['neck'].matrix_world.translation-Vector((0,-.188,1.215))).length<1e-5
 template=bpy.data.objects[skins[0]];tags=dict(template.items());materials=list(template.data.materials);added=[];solids=[];cuts=[];seats=[];dg=bpy.context.evaluated_depsgraph_get()
 mask={n:h['evaluated_bvh'](bpy.data.objects[n]) for n in removed}
 def install(name,v,f,owner='body',role='plate',existing=False):
  if existing:o=bpy.data.objects[name];mats=list(o.data.materials)
  else:
   m=bpy.data.meshes.new(name+' finite formed mesh');o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o);o.parent=bpy.data.objects[owner];o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Identity(4);mats=[bpy.data.materials['Neutral / frame']] if role=='frame' else materials
   for k,vv in tags.items():o[k]=vv
   o['constructionClass']='proposed-passive';o['exteriorEras']='maker,mechanic,builder';o['region']='torso';o['surfaceRole']=role;o['constructionOwner']=owner;o['geometryStatus']='V35 coarse integrated torso proposal; not owner approved';added.append(name)
  bpy.context.view_layer.update();inv=o.matrix_world.inverted();m=bpy.data.meshes.new(name+' finite formed wall');m.from_pydata([inv@Vector(p) for p in v],[],f);m.update()
  for mat in mats:m.materials.append(mat)
  bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  assert bm.calc_volume(signed=True)>0,name;bm.to_mesh(m);bm.free();o.data=m;o.modifiers.clear()
  for p in m.polygons:p.use_smooth=role!='frame'
  assert max((o.matrix_world@q.co-Vector(p)).length for q,p in zip(m.vertices,v))<1e-6
  return o
 # Whole sternum/liner contour changed as one cage, including finite inner
 # walls. Upper cervical receiving rim is exactlyunchangedaboveZ1.185.
 for name in changed:
  if 'receiving tab' in name:continue
  o=bpy.data.objects[name];ev=o.evaluated_get(dg);mm=ev.to_mesh();v=[map_point(ev.matrix_world@q.co) for q in mm.vertices];f=[tuple(p.vertices) for p in mm.polygons];ev.to_mesh_clear();install(name,v,f,o.parent.name,o.get('surfaceRole','plate'),True)
 bpy.context.view_layer.update();liner=h['evaluated_bvh'](bpy.data.objects['V30 continuous tapered breast liner'])
 for side in (-1,1):
  name=f'V30 breast liner receiving tab {side}';o=bpy.data.objects[f'V23 breast moving return {side}'];assert len(o.data.vertices)==248
  seat=sum((o.matrix_world@o.data.vertices[30*8+j].co for j in (0,1,4,5)),Vector())/4;end=liner.find_nearest(map_point(seat))[0];v,f=h['load_tab']([seat,seat.lerp(end,.5),end],.019,.014,.004);install(name,v,f,'breastplate','frame',True);seats.append({'name':name,'retainedReturnSeat':list(seat),'actualLinerSeat':list(end),'linerDistanceM':liner.find_nearest(end)[3]})
 # Actual source receiving footprints retained around hip/lowerframe only.
 # The prior broad112mm shoulder bore is deliberatelynotreused: upper hood
 # receives the actual moving saddle/races at runtime angles below.
 def point(z,a,off=0):return map_point(h['point'](z+.120,a,off)-Vector((0,0,.120)))
 def make_patch(name,side,top,bottom,a0,a1,slant=.012,off=.012,taper=.87,masked=True,maskname=None):
  def params(u,v):
   t=2*v-1;z=top+(bottom-top)*u+slant*t*ease(u)-.008*(1-t*t)*ease(u);theta=side*((a0+a1)/2+(v-.5)*(a1-a0)*(1-(1-taper)*ease(u))+.025*ease(u));return z,theta
  def fn(u,v):
   z,a=params(u,v);return point(z,a,off+.010*ease(u))
  R,C=20,14;uv=[(i/R,j/C) for i in range(R+1) for j in range(C+1)];verts=[fn(u,v) for u,v in uv]
  def valid(u,v):
   if not masked:return True
   z,a=params(u,v);base=h['point'](z+.120,a,0)-Vector((0,0,.120));n=Vector((math.sin(a),-math.cos(a),0));return mask[maskname].ray_cast(base+.06*n,-n,.12)[0] is not None
  states=[valid(u,v) for u,v in uv];faces=[];clipped={}
  def edge(i,j):
   key=tuple(sorted((i,j)))
   if key in clipped:return clipped[key]
   lo,hi=0.,1.
   for _ in range(16):
    t=(lo+hi)/2;u=uv[i][0]+(uv[j][0]-uv[i][0])*t;v=uv[i][1]+(uv[j][1]-uv[i][1])*t
    if valid(u,v)==states[i]:lo=t
    else:hi=t
   t=(lo+hi)/2;u=uv[i][0]+(uv[j][0]-uv[i][0])*t;v=uv[i][1]+(uv[j][1]-uv[i][1])*t;clipped[key]=len(verts);verts.append(fn(u,v));return clipped[key]
  for i in range(R):
   for j in range(C):
    k=i*(C+1)+j
    for tri in [(k,k+1,k+C+2),(k,k+C+2,k+C+1)]:
     f=[]
     for x,y in zip(tri,tri[1:]+tri[:1]):
      if states[x]:f.append(x)
      if states[x]!=states[y]:f.append(edge(x,y))
     if len(f)>=3:faces.append(tuple(f))
  used=sorted({x for f in faces for x in f});assert used,name;mapping={x:i for i,x in enumerate(used)};v=[verts[i] for i in used];f=[tuple(mapping[i] for i in t) for t in faces]
  # Bake finite4mm inward walls after forming actual open surface.
  m=bpy.data.meshes.new(name+' surface');m.from_pydata(v,[],f);m.update();o=bpy.data.objects.new(name+' temporary surface',m);bpy.context.scene.collection.objects.link(o);bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();q=o.modifiers.new('Finite4mm wall','SOLIDIFY');q.thickness=.004;q.offset=-1;q.use_even_offset=False
  with bpy.context.temp_override(object=o,active_object=o,selected_objects=[o],selected_editable_objects=[o]):bpy.ops.object.modifier_apply(modifier=q.name)
  v=[p.co.copy() for p in o.data.vertices];f=[tuple(p.vertices) for p in o.data.polygons];bpy.data.objects.remove(o,do_unlink=True);return install(name,v,f)
 hood=[]
 for side in (-1,1):
  # Short diagonal pectoral courses, not a continuous ovalcover. The upper
  # field is a scapular bridge and its fixed lip ends beside movingjournal.
  for j in range(3):
   a0=.89+j*.265;a1=a0+.25
   o=make_patch(f'V35 scapular receiving plate {side} {j}',side,1.265-j*.013,1.115-j*.006,a0,a1,.018,.008,.97,False);hood.append(o.name)
  rows=[(1.137,.928,.90,1.12,.014),(1.105,.906,1.11,1.28,.018),(.974,.737,.91,1.18,.030),(.948,.705,1.17,1.42,.024),(.976,.755,1.43,1.71,.018),(1.130,.934,1.51,1.73,.010)]
  for j,(a,b,c,d,slant) in enumerate(rows):make_patch(f'V35 oblique thoracic side guard {side} {j}',side,a,b,c,d,slant,.010,.87,True,f'V30 long fixed shoulder flank {side}')
  # Compact posterior courses seat around existing spherical hipreceiver.
  for j,(top,bottom) in enumerate([(1.249,1.053),(1.084,.871),(.901,.677)]):
   make_patch(f'V35 compact dorsal return {side} {j}',side,top,bottom,1.72,3.115,-.010,.012,.97,True,f'V30 long swept dorsal cheek {side}')
  # Passive formed channels border the servicebay and connect actual rib
  # section into retained upperpelvic loadbow; no movinghipbridge.
  rows=[(side*.183,-.132,1.141),(side*.230,-.116,1.071),(side*.244,-.072,.944),(side*.169,.009,.821)]
  v,f=g['channel']([tuple(map_point(p)) for p in rows],.026,.020,.0045);install(f'V35 lateral thoracic bay load rail {side}',v,f,role='frame')
  rows=[(side*.201,-.071,1.150),(side*.239,.031,1.113),(side*.234,.058,.987),(side*.105,.065,.746)]
  v,f=g['channel'](rows,.026,.022,.0045);install(f'V35 posterior bay load rail {side}',v,f,role='frame')
 # Fit upper fixed receive to actual finite moving hardware, without
 # treating old oversize circular aperture as identity. Discrete toolsonly.
 for side,label in [(-1,'right'),(1,'left')]:
  pivot=bpy.data.objects[label+'-mantle'].matrix_world.copy();angles=[0,.065,.07] if side==1 else [0,-.24,-.64]
  tools=[o for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name==label+'-mantle' and (o.name.startswith(label+' oblique shoulder saddle') or o.name.startswith(label+' shouldered shoulder journal') or o.name.startswith(label+' stepped shoulder race') or o.name.startswith('V21 '+label+' shoulder captive bonnet'))]
  assert tools,label
  for source in tools:
   ev=source.evaluated_get(bpy.context.evaluated_depsgraph_get());mm=ev.to_mesh();raw=[ev.matrix_world@v.co for v in mm.vertices];normal=ev.matrix_world.to_3x3().inverted().transposed();ns=[(normal@v.normal).normalized() for v in mm.vertices];fs=[tuple(f.vertices) for f in mm.polygons];ev.to_mesh_clear()
   for angle in angles:
    change=pivot@Matrix.Rotation(angle,4,'X')@pivot.inverted();vv=[change@(p+.003*n) for p,n in zip(raw,ns)];cm=bpy.data.meshes.new('V35 finite shoulder receiving tool');cm.from_pydata(vv,[],fs);cm.update();c=bpy.data.objects.new(cm.name,cm);bpy.context.scene.collection.objects.link(c);bpy.context.view_layer.update();edited=[]
    for target in [n for n in hood if n.startswith(f'V35 scapular receiving plate {side} ')]:
     o=bpy.data.objects[target];q=o.modifiers.new('Actual shoulder hardware receiving seat','BOOLEAN');q.operation='DIFFERENCE';q.solver='EXACT';q.object=c
     with bpy.context.temp_override(object=o,active_object=o,selected_objects=[o],selected_editable_objects=[o]):bpy.ops.object.modifier_apply(modifier=q.name)
     assert len(o.data.polygons)>0,target;edited.append(target)
    bpy.data.objects.remove(c,do_unlink=True);bpy.data.meshes.remove(cm);cuts.append({'source':source.name,'mantleLocalXAngle':angle,'targets':edited,'nominalVertexNormalExpansionM':.003})
 for name in removed:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
 bpy.context.view_layer.update()
 for name in changed+added:
  o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges),name;volume=bm.calc_volume(signed=True);assert volume>0,name;bm.free();assert all(math.isfinite(x) for v in o.data.vertices for x in v.co),name;solids.append({'name':name,'positiveVolumeM3':volume,'closed':True})
 assert all(s['node'](bpy.data.objects[n])==v for n,v in nodes.items());assert all(s['snap'](bpy.data.objects[n])==v for n,v in protected.items())
 return {'region':'coarse torso integration','status':'Unapproved source-supported geometry proposal; firstvisualbeforefit','changedMeshes':changed,'added':added,'removed':removed,'changedNodes':[],'outsideMeshesExact':len(protected),'nodesExact':len(nodes),'materialsChanged':False,'controlCage':CAGE,'receivingTabs':seats,'shoulderReceivingTools':cuts,'finiteSolids':solids,'construction':'Coordinated tapered sternum/liner, short oblique pectoral/ventral plates, scapular receiving bridge to actual hardware, framed lateral servicebay and compact posteriorreturns; independent breastdoor retained','limits':['First coarse visual candidate; fresh posed opening/neck/wing fit remains pending.','Fixed named joints are compatibilityconstraints, not approval of current macroproportions.','Nominal3mm hardwaretool vertex-normal expansion is not constantnormal/continuous clearance.']}
