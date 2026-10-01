"""13 directly authored crown shingles on actual skull triangles; coherent graph stock."""
import bpy,bmesh,math
from mathutils import Vector
from collections import Counter
PREFIX='V38 swept crown course '
ROWS=[(0,.36,5,.0115),(.27,.68,5,.0075),(.58,.99,3,.0035)]
def clip(poly,a,b):
 d=b-a;out=[]
 for p,q in zip(poly,poly[1:]+poly[:1]):
  sp=d.x*(p.y-a.y)-d.y*(p.x-a.x);sq=d.x*(q.y-a.y)-d.y*(q.x-a.x);ip=sp>=0;iq=sq>=0
  if ip:out.append(p)
  if ip!=iq:out.append(p+(q-p)*(sp/(sp-sq)))
 return out
def apply():
 bpy.context.view_layer.update();oldnames=sorted(o.name for o in bpy.data.objects if o.type=='MESH'and o.name.startswith(PREFIX));assert len(oldnames)==58;template=bpy.data.objects[oldnames[6]];shell=bpy.data.objects['V38 compact cranial inner shell'];M=shell.matrix_world.copy();outer=[M@p.co for p in shell.data.vertices[:1189]];assert len(shell.data.vertices)==2378;shell.data.calc_loop_triangles();base=[]
 for tri in shell.data.loop_triangles:
  inds=tuple(tri.vertices)
  if not all(i<1189 for i in inds):continue
  uv=[Vector((i//29/40,i%29/28))for i in inds];p=[outer[i]for i in inds];den=(uv[1]-uv[0]).x*(uv[2]-uv[0]).y-(uv[1]-uv[0]).y*(uv[2]-uv[0]).x
  if abs(den)>1e-12:base.append((uv,p,den))
 assert len(base)==2240
 records=[];added=[]
 for row,(lo,hi,count,level)in enumerate(ROWS):
  for col in range(count):
   center=(col+.5)/count;half=.090 if count==5 else .125;phase=.008*(col%2);start=lo+phase;end=hi-.010*((row+col)%2);sweep=(-1 if center<.5 else 1)*.008
   shape=[(0,-.88),(0,.88),(.25,1),(.72,.80),(1,.25),(1,-.20),(.70,-.77),(.25,-1)]
   poly=[Vector((start+(end-start)*u,center+half*w+sweep*u))for u,w in shape]
   poly=[q for a,b in zip(poly,poly[1:]+poly[:1])for q in(.88*a+.12*b,.12*a+.88*b)]
   # Enforce counterclockwise domain for clipping actual finite backing triangles.
   area=sum(a.x*b.y-a.y*b.x for a,b in zip(poly,poly[1:]+poly[:1]))
   if area<0:poly.reverse()
   points=[];params=[];index={};fs=[];sourceFaces=[]
   for uv,p,den in base:
    if max(q.x for q in uv)<min(q.x for q in poly)or min(q.x for q in uv)>max(q.x for q in poly)or max(q.y for q in uv)<min(q.y for q in poly)or min(q.y for q in uv)>max(q.y for q in poly):continue
    clipped=uv.copy()
    for a,b in zip(poly,poly[1:]+poly[:1]):
     if clipped:clipped=clip(clipped,a,b)
    if len(clipped)<3:continue
    rowids=[]
    for q in clipped:
     key=(round(q.x,7),round(q.y,7))
     if key not in index:
      d=q-uv[0];a=uv[1]-uv[0];b=uv[2]-uv[0];w1=(d.x*b.y-d.y*b.x)/den;w2=(a.x*d.y-a.y*d.x)/den;position=p[0]*(1-w1-w2)+p[1]*w1+p[2]*w2;index[key]=len(points);points.append(position);params.append(q)
     if not rowids or rowids[-1]!=index[key]:rowids.append(index[key])
    if len(rowids)>1 and rowids[-1]==rowids[0]:rowids.pop()
    for k in range(1,len(rowids)-1):
     tri=(rowids[0],rowids[k],rowids[k+1])
     if len(set(tri))==3 and(points[tri[1]]-points[tri[0]]).cross(points[tri[2]]-points[tri[0]]).length>1e-12:fs.append(tri)
   seen=set();fs=[t for t in fs if not(tuple(sorted(t))in seen or seen.add(tuple(sorted(t))))]
   assert fs
   out=[p+Vector((0,0,level))for p in points];inn=[];rootAreas=0
   for p,q in zip(points,params):
    u=(q.x-start)/(end-start);blend=max(0,min(1,(u-.18)/.15));blend=blend*blend*(3-2*blend);inn.append(p+Vector((0,0,(level-.003)*blend)))
   for tri in fs:
    if all((params[k].x-start)/(end-start)<=.18+1e-8 for k in tri):rootAreas+=(points[tri[1]]-points[tri[0]]).cross(points[tri[2]]-points[tri[0]]).length*.5
   assert rootAreas>0
   n=len(points);verts=out+inn;faces=fs+[tuple(n+k for k in reversed(t))for t in fs];ec=Counter(tuple(sorted((t[j],t[(j+1)%3])))for t in fs for j in range(3))
   for t in fs:
    for j in range(3):
     a,b=t[j],t[(j+1)%3]
     if ec[tuple(sorted((a,b)))]==1:faces.append((a,b,n+b,n+a))
   name=f'V38 crown-layout swept plate course {row+1} panel {col+1}';o=template.copy();o.name=name;bpy.context.scene.collection.objects.link(o)
   for k in list(o.keys()):
    if k not in['region','surfaceRole','exteriorEras','constructionClass','constructionOwner','articulatesAcrossJoint','proposal']:del o[k]
   bpy.context.view_layer.update();inv=o.matrix_world.inverted();m=bpy.data.meshes.new(name+' finite nativeZ stock');m.from_pydata([inv@p for p in verts],[],faces);m.update()
   for mat in template.data.materials:m.materials.append(mat)
   bm=bmesh.new();bm.from_mesh(m);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=2e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));vol=bm.calc_volume(signed=True)
   if vol<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces));vol=bm.calc_volume(signed=True)
   print('STOCK',name,'nonmanifold',Counter(len(e.link_faces)for e in bm.edges if not e.is_manifold),'volume',vol,flush=True);assert all(e.is_manifold for e in bm.edges)and vol>0,name
   bm.to_mesh(m);bm.free()
   for i,f in enumerate(m.polygons):f.use_smooth=i<2*len(fs)
   o.data=m;o['constructionDescription']='Directly authored broad tapered rigid crown shingle. Ordered3mm freewall nativeZ; anterior integral root bottom copies finite actual skull triangles, no extra floating carrier. Three independent nested layers, butt-clear lateral domains. All passive cranial-cover owned; actual fit qualified separately.';o['v38CrownLayout01']='13plates/3staggered swept courses; layer offsets11.5/7.5/3.5mm are proposals, not full engineering/likeness acceptance.';added.append(name)
   records.append({'name':name,'owner':o.parent.name,'exteriorEras':o.get('exteriorEras'),'course':row+1,'outerNativeZOffsetM':level,'freeWallNativeZ':.003,'rootActualBackingObject':shell.name,'rootExactBackingTriangleAreaM2':rootAreas,'rootParamRange':[0,.18],'rootTransitionRange':[.18,.33],'footprintParameterPolygon':[list(q)for q in poly],'vertices':len(verts),'closed':True,'positiveVolumeM3':vol,'actualRootRole':'Finitecopied backing triangle faces; no centercorner approximation. Root route belowpreviouslayer and beforelowercourse footprint.'})
 for name in oldnames:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
 return {'status':'13broadplate crown-layout proposal; visual/finite acceptance pending','changedMeshes':[],'addedMeshes':added,'removedMeshes':oldnames,'changedNodes':[],'construction':records,'ownership':'All13newpassive parts cranial-cover; exact parent/pivot/opening/materials/era capabilities. No backing geometry/extras change.','constructionScheme':'Actualskulltriangle-clipped convex footprint graphs; samebasefield separate11.5/7.5/3.5mm outerlayers; 3mmfreewall; integral copiedrootfoot beloweachlayer. Lateral butt domains; broadfront/taperedrear; no complexoldmeshbevel.','limits':['Footprintparameter coordinates are not newtextureUV.','3mmnativeZ stock is not uniform normal gauge.','Copiedfinite rootarea supports seating hypothesis; not bolting/loadbearing acceptance.','Rest/open strictsurface screen still governs; no continuousphysical engineering/ownerlikeness claim.']}
