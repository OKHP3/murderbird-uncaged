"""Compact formed crown plates from actual current rigid stock; no new owner."""
import bpy,bmesh,math,json,hashlib
from mathutils import Vector
PREFIX='V38 swept crown course '
def apply(second=False):
 if second:return final_termination()
 bpy.context.view_layer.update();names=sorted(o.name for o in bpy.data.objects if o.type=='MESH'and o.name.startswith(PREFIX));assert len(names)==58;rec=[]
 for name in names:
  o=bpy.data.objects[name];assert o.parent.name=='cranial-cover';old=[v.co.copy()for v in o.data.vertices];h=len(old)//2;assert h in[75,55];M=o.matrix_world.copy();inv=M.inverted();v=[M@p for p in old];outer=v[:h];lo=min(p.y for p in outer);hi=max(p.y for p in outer);span=hi-lo;assert span>.025;root=(outer[0]+outer[1])*.5;axis=(outer[1]-outer[0]).normalized();tip=max(outer,key=lambda p:p.y);drift=(tip-root).dot(axis);rootBand=min(.012,span*.16);part=int(name[-1]);gain=.25 if part==1 else .20;cut=min(.012,span*.13);m=o.data.copy();protected=[]
  for i,p in enumerate(outer):
   if p.y<=lo+rootBand:
    protected.extend([i,h+i]);continue
   u=(p.y-lo)/span;t=max(0,min(1,(p.y-lo-rootBand)/(span-rootBand)));fade=t*t*(3-2*t);across=(p-root).dot(axis)-drift*u;shift=axis*(gain*fade*across)
   for k in[i,h+i]:m.vertices[k].co=inv@(v[k]+shift)
  bm=bmesh.new();bm.from_mesh(m);n=(M.to_3x3().transposed()@Vector((0,1,0))).normalized();bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-8,plane_co=inv@Vector((0,hi-cut,0)),plane_no=n,clear_outer=True,clear_inner=False)
  border=[e for e in bm.edges if e.is_boundary];assert border,name
  bmesh.ops.holes_fill(bm,edges=border,sides=0);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));volume=bm.calc_volume(signed=True)
  if volume<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces));volume=bm.calc_volume(signed=True)
  assert all(e.is_manifold for e in bm.edges)and volume>0,name
  unseen=set(bm.verts);components=0
  while unseen:
   components+=1;stack=[unseen.pop()]
   while stack:
    p=stack.pop()
    for e in p.link_edges:
     z=e.other_vert(p)
     if z in unseen:unseen.remove(z);stack.append(z)
  bm.to_mesh(m);bm.free();coords={tuple(p.co)for p in m.vertices};assert all(tuple(old[i])in coords for i in protected),name
  for p in m.polygons:p.use_smooth=True
  o.data=m;o['constructionDescription']='Compact rigid swept plate proposal: anterior finite actual root patch retained; free breadth deliberately formed, sharp ribbon tip truncated by real finite cross-section cap. Paired stock moved coherently, no normal-sign reinset. All cranial-cover ownership/materials/era inheritance unchanged. Current fit qualified separately.';o['v38CrownPlate01']='Current crown58identity stock reconstruction; no tallercrest/reartrain/ownerchange. Anteriorrootspreserved; 20–25percentfree breadth proposal,8–12mm truncated freeedge.'
  rec.append({'name':name,'owner':o.parent.name,'sourceVertices':len(old),'vertices':len(m.vertices),'sourceRootBandNativeYM':rootBand,'sourceRootPairedVerticesExact':len(protected),'freeBreadthGain':gain,'freeNativeYTrimM':cut,'sourceRearNativeY':hi,'candidateRearNativeY':max((M@p.co).y for p in m.vertices),'nonmanifoldEdges':0,'components':components,'positiveVolumeM3':volume,'construction':'Existing3mm paired stock section directions preserved on formed surviving surfaces; planar freeedge cap physically closes truncatedstock. Not uniform normal thickness, no hidden receiver certification.'})
 return {'status':'Swept crown plate geometry proposal; visible gain/finite fit/owner acceptance pending','changedMeshes':names,'changedNodes':[],'construction':rec,'ownership':'All58parts rigidcranial-cover underhead; passive all3eras, openingmovesasassembly. Actual root/pivot/rest/materials unchanged.','limits':['Rootpatch uses actual current plate geometry, not obsolete338vertex crown-fit grid.','Current actualsource neighboring contacts govern; historical42paircount is not assumedcurrent.','Broader truncated plates are reconstructed proportions, not exactreference measurements.','No optical/bill/jaw/neck/body/finish changes; pendingneckoutline independent.']}

def final_termination():
 bpy.context.view_layer.update();names=sorted(o.name for o in bpy.data.objects if o.type=='MESH'and o.name.startswith(PREFIX));records=[]
 for name in names:
  o=bpy.data.objects[name];M=o.matrix_world.copy();inv=M.inverted();old=[p.co.copy()for p in o.data.vertices];world=[M@p for p in old];lo=min(p.y for p in world);hi=max(p.y for p in world);axis=(world[1]-world[0]).normalized();endpoints=[p for p in world if p.y>=hi-2e-7];amin=min(p.dot(axis)for p in endpoints);amax=max(p.dot(axis)for p in endpoints);mid=(amin+amax)*.5;half=(amax-amin)*.5;assert half>.002;band=.012;protected=[i for i,p in enumerate(world)if p.y<=hi-band-1e-6];m=o.data.copy();bm=bmesh.new();bm.from_mesh(m);tag=bm.faces.layers.int.new('terminalcap')
  for f in bm.faces:
   if all((M@v.co).y>=hi-2e-7 for v in f.verts):f[tag]=1
  capedges=[e for e in bm.edges if all((M@v.co).y>=hi-2e-7 for v in e.verts)]
  for v in bm.verts:
   p=M@v.co;t=max(0,min(1,(p.y-(hi-band))/band));fade=t*t*(3-2*t);a=(p.dot(axis)-mid)/half
   if fade>0:v.co=inv@(p-axis*(.10*fade*(p.dot(axis)-mid))-Vector((0,.0035*fade*a*a,0)))
  result=bmesh.ops.bevel(bm,geom=capedges,offset=.0006,segments=2,affect='EDGES',clamp_overlap=True,loop_slide=True)
  for f in result.get('faces',[]):f[tag]=1
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));volume=bm.calc_volume(signed=True)
  if volume<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces));volume=bm.calc_volume(signed=True)
  assert all(e.is_manifold for e in bm.edges)and volume>0,name
  for f in bm.faces:f.smooth=not bool(f[tag])
  corners=[v.co.copy()for v in bm.verts];coords={tuple(p)for p in corners};assert all(tuple(old[i])in coords for i in protected),name
  unseen=set(bm.verts);components=0
  while unseen:
   components+=1;stack=[unseen.pop()]
   while stack:
    q=stack.pop()
    for e in q.link_edges:
     w=e.other_vert(q)
     if w in unseen:unseen.remove(w);stack.append(w)
  bm.to_mesh(m);bm.free();o.data=m;o['constructionDescription']='Second/final compact swept crown plate proposal: first anterior roots and breadth retained; only12mm free termination curls in flow with10percenttaper,3.5mm corner sweep and0.6mm finite bevel. Cap/bevel faces use discrete normals; broad plate faces remain smooth. Rigid cranial-cover ownership unchanged; fit separately qualified.';o['v38CrownPlate01']='Attempt02 rounded/tapered terminal stock; no breadth increase, rootseat unchanged. Current geometry supersedes historical exterior-exact/inset annotations.'
  records.append({'name':name,'owner':o.parent.name,'changedTerminalBandM':band,'terminalTaper':.10,'cornerFlowSweepM':.0035,'actualFiniteBevelM':.0006,'rootAndExcludedVerticesExact':len(protected),'components':components,'nonmanifoldEdges':0,'positiveVolumeM3':volume,'rootSeats':'First actual root band unchanged; no extra receiving claim from bevel/manifold.'})
 return {'status':'Final swept crown termination proposal; fit/likeness pending','changedMeshes':names,'changedNodes':[],'construction':records,'ownership':'All58cranial-cover plates/rig/eras/materials fixed','limits':['Only12mm terminalband changed againstfirst; broader firstface retained.','Rounded terminalstock is proposedconstruction, not reference-exact dimensions.','Inherited historical outer-exact/headfit extras are history, not currentgeometryfacts.','No otherhead/body/neck change; pendingneckoutline independent.']}
