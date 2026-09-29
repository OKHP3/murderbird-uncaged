"""V36 formed bill/orbital/mandibular construction, a regional proposal.
Native X lateral,Z up,-Y anterior. July is HEAD ONLY; owner whole-bird
controls near-closed rest. Profiles are authored, not recovered dimensions.
Existing lower throat receivers, lens/cup and jaw/cap axes are retained.
"""
from pathlib import Path
import bpy,bmesh,runpy,math,hashlib,json
from mathutils import Vector,Matrix
ROOT=Path(globals().get('SOURCE_ROOT','/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged'))
# Native offsets from the fixed head attachment, at current V35 head mass.
# Dorsal surface follows a broad formed ridge; posterior land carries the
# near-closed cutting seam. A returned hook is retained, never a straight nose.
BILL=[(-.331,.395,-.276,.221,.109),(-.385,.382,-.313,.200,.123),(-.435,.350,-.348,.183,.115),(-.469,.286,-.379,.170,.095),(-.483,.203,-.405,.161,.073),(-.468,.134,-.417,.139,.048),(-.431,.093,-.415,.119,.026),(-.402,.073,-.403,.086,.0028)]
# Independent asymmetric outer envelope, NOT an offset from the optic circle.
OUTER=[(.143,-.070,.282),(.126,-.073,.403),(.120,-.233,.434),(.123,-.351,.385),(.126,-.393,.278),(.153,-.328,.238),(.161,-.208,.210),(.158,-.115,.209)]

def apply():
 bpy.context.view_layer.update();h=runpy.run_path(str(ROOT/'scripts/regions/whole-character-v31-head-reconstruction.py'));head=bpy.data.objects['head'];origin=head.matrix_world.translation.copy()
 assert all(n in bpy.data.objects for n in ('V32 returned upper bill course 0','V32 formed mandibular bowl','V31 optic recessed receiving cup 1','V33 diagonal brow receiver 1 0'))
 replace=[o.name for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('V33 diagonal brow receiver ','V33 formed lower cheek receiver ','V33 recessed optic retaining lip '))]
 billnames=[f'V32 returned upper bill course {i}' for i in range(3)];jawname='V32 formed mandibular bowl';owned=set(replace+billnames+[jawname]);protected={o.name:h['snap'](o) for o in bpy.data.objects if o.type=='MESH' and o.name not in owned};nodes={o.name:h['node'](o) for o in bpy.data.objects if o.type=='EMPTY'}
 template=bpy.data.objects['V33 diagonal brow receiver 1 0'];props=dict(template.items());materials=list(template.data.materials);added=[];changed=[];solids=[]
 def install(name,owner,geo,existing=None,description=''):
  vv,ff=geo;world=[origin+Vector(p) for p in vv]
  if existing:o=bpy.data.objects[existing];mats=list(o.data.materials)
  else:
   o=bpy.data.objects.new(name,None);bpy.context.scene.collection.objects.link(o);o.parent=bpy.data.objects[owner];o.matrix_basis=Matrix.Identity(4);o.matrix_parent_inverse=Matrix.Identity(4);mats=materials
   for k,v in props.items():o[k]=v
  bpy.context.view_layer.update();inv=o.matrix_world.inverted();m=bpy.data.meshes.new(name+' formed finite mesh');m.from_pydata([inv@p for p in world],[],ff);m.update()
  for material in mats:m.materials.append(material)
  bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  vol=bm.calc_volume(signed=True);assert vol>0,name;bm.to_mesh(m);bm.free();o.data=m;o.modifiers.clear()
  for p in m.polygons:p.use_smooth=False
  o['region']='head';o['surfaceRole']='plate';o['constructionClass']='inherited-passive';o['exteriorEras']='maker,mechanic,builder';o['proposal']=True;o['constructionDescription']=description;o['constructionOwner']=owner
  assert max((o.matrix_world@v.co-p).length for v,p in zip(m.vertices,world))<1e-6
  assert all(math.isfinite(c) for p in world for c in p)
  (changed if existing else added).append(o.name);solids.append({'name':o.name,'owner':owner,'closed':True,'positiveVolumeM3':vol});return o
 # Ring has broad flat side planes and narrow ridge/cutting lands. Three
 # independently formed courses have real finite end faces and tiny gaps.
 h['blade'].__globals__['BILL']=BILL
 for i,(a,b,hollow) in enumerate([(0,.355,True),(.360,.710,True),(.715,1,False)]):install(billnames[i],'upper-bill',h['blade'](a,b,hollow),existing=billnames[i],description='V36 broad formed blade planes and returned hook, finite independently authored bill course')
 # Give the curved mandible visible formed side area, preserving its top
 # seam exactly and its fixed hinge. Only the underside field deepens.
 jaw=bpy.data.objects[jawname];jaw.data=jaw.data.copy();inv=jaw.matrix_world.inverted();points=[]
 for v in jaw.data.vertices:
  p=jaw.matrix_world@v.co-origin;t=max(0,min(1,(-p.y-.17)/.22));width=.140*(1-t)+.025*t;side=min(1,abs(p.x)/max(width,.02));weight=math.sin(math.pi*t)**2*(1-side**4);p.z-=.022*weight;points.append(origin+p);v.co=inv@(origin+p)
 jaw.data.update();changed.append(jawname);jaw['v36MandibleConstruction']='Curved finite bowl with deeper formed midspan side area; original upper lip, hinge and era retained'
 bm=bmesh.new();bm.from_mesh(jaw.data);assert all(e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);assert vol>0;bm.free();solids.append({'name':jawname,'owner':'jaw','closed':True,'positiveVolumeM3':vol})
 # Replace the circular outer geometry while retaining the actual inner
 # receiving cup/lens. Outer faceted planes recede under the swept skull.
 for name in replace:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
 cy,cz=-.2552,.3016
 def receiver(side,a,b,lo):
  def fn(u,v):
   angle=a+(b-a)*u;q=angle/math.tau*8;i=int(q);f=q-i;A=OUTER[i%8];B=OUTER[(i+1)%8];outer=[A[k]*(1-f)+B[k]*f for k in range(3)]
   # Aperture remains clear beyond original59.16mm cup outer radius.
   r=.0645;iy=cy+r*math.cos(angle);iz=cz+r*math.sin(angle);ix=.171
   # Two defined formed planes replace inflated smooth circular eyeliner.
   if v<.32:
    t=v/.32;x=ix*(1-t)+.162*t;y=iy*(1-t)+(iy*.70+outer[1]*.30)*t;z=iz*(1-t)+(iz*.70+outer[2]*.30)*t
   else:
    t=(v-.32)/.68;x=.162*(1-t)+outer[0]*t;y=(iy*.70+outer[1]*.30)*(1-t)+outer[1]*t;z=(iz*.70+outer[2]*.30)*(1-t)+outer[2]*t
   return Vector((side*x,y,z))
  return h['finite_sheet'](fn,nu=32,nv=10,wall=.0045,side=side)
 for side in (-1,1):
  for i,(a,b) in enumerate([(.025,.86),(.885,1.96),(1.985,3.125)]):install(f'V36 formed diagonal brow {side} {i}','head',receiver(side,a,b,0),description='Independent diagonal polygon envelope; finite formed brow, recessed original optic underneath')
  for i,(a,b) in enumerate([(3.15,4.65),(4.675,math.tau-.015)]):install(f'V36 mandibular cheek return {side} {i}','head',receiver(side,a,b,1),description='Formed cheek return from original optic bay toward retained mandibular journal; open jaw cavity retained')
  # Small actual retaining lip, supported by unchanged inner cup; no
  # additional eye, sensor or luminous Maker/Mechanic surface is invented.
  lip=install(f'V36 recessed retaining lip {side}','head',h['annular'](side,cy,cz,[(.165,.0579),(.168,.0579),(.168,.0615),(.165,.0615)]),description='Narrow passive finite retaining lip outside unchanged recessed cup; sensing aperture retains Advanced-only original ownership')
  lip['surfaceRole']='bearing'
 # Actual moving axle needs a stationary finite bore through the lower
 # rear cheek. Bore follows exact preserved jaw centre, not a fake hole.
 center=bpy.data.objects['jaw'].matrix_world.translation-origin;bores=[]
 for side in (-1,1):
  name=f'V36 mandibular cheek return {side} 1';o=bpy.data.objects[name];vv,ff=h['cylinder'](side,center.y,center.z,.10,.22,.014,count=80);m=bpy.data.meshes.new('temporary jaw-axis tool');m.from_pydata([origin+p for p in vv],[],ff);m.update();tool=bpy.data.objects.new(m.name,m);bpy.context.scene.collection.objects.link(tool);bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();bpy.context.view_layer.update();mod=o.modifiers.new('Finite coaxial jaw receiving bore','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True);bpy.data.meshes.remove(m);bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges),name;vol=bm.calc_volume(signed=True);assert vol>0;bm.free();next(s for s in solids if s['name']==name)['positiveVolumeM3']=vol;bores.append({'name':name,'radiusM':.014,'actualAxisWorld':list(origin+center)})
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();front=None
 for name in billnames:
  o=bpy.data.objects[name];ev=o.evaluated_get(dg);m=ev.to_mesh()
  for v in m.vertices:
   p=ev.matrix_world@v.co
   if front is None or p.y<front.y:front=p.copy()
  ev.to_mesh_clear()
 # Contact updates are returned to composer, not silently applied to nodes.
 assert all(h['node'](bpy.data.objects[n])==s for n,s in nodes.items())
 assert all(h['snap'](bpy.data.objects[n])==s for n,s in protected.items())
 return {'region':'constructed face','status':'Coarse reference-led visual proposal; fit and likeness pending','changedMeshes':changed,'added':added,'removed':replace,'changedNodes':[],'allOriginalNodesExact':len(nodes),'protectedMeshesExact':len(protected),'materialsChanged':False,'opticLensCupAndEraExact':True,'lowerCervicalReceivingExact':True,'billContactNativeWorld':list(front),'contactMethod':'Minimum native-Y evaluated upper-bill surface vertex; composer may refit marker after selection','finiteSolids':solids,'billProfileNativeHeadOffsets':BILL,'orbitalOuterProfileNativeHeadOffsets':OUTER,'jawReceivingBores':bores,'constructionChoices':['Profile-led flat/beveled bill side planes and returned hook.','Independently outlined diagonal brow/formed cheek; original recessed optic remains visible.','Deeper finite articulated mandible side area, original top seam and hinge retained.','Original swept crown and temporal receiving envelope retained for continuity; no blank forehead enlargement.'],'limits':['First visual gate precedes sampled jaw/cap checks.','Outer orbital profile is authored from qualitative reference relationships, not image dimensions.','No body, neck, materials or era capability changes; original lower cervical receivers exact.']}
