"""V27 curved cranial construction proposal on the selected V26 head.
July is HEAD ONLY. Owner whole-bird controls closed-rest impression.
Pre-mass native metre/Z-up coordinates are baked through retained1.30 head
mass; surfaces curve across actual dorsal/lateral/rear skull sections.
No runtime scale, node relocation, bill/jaw/lens or material mutation.
"""
import bpy,bmesh,math,json
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
PROFILE=[(-.574,1.785,.100,.059),(-.505,1.783,.149,.100),(-.429,1.765,.153,.124),(-.352,1.746,.146,.115),(-.279,1.718,.118,.092),(-.216,1.687,.075,.047)]
FACADES=['Forged orbital brow','Broad swept cheek band','Forged orbital mounting plate','V24 anterior orbital root receiver']
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def section(y):
 for a,b in zip(PROFILE,PROFILE[1:]):
  if y<=b[0]:
   t=max(0,min(1,(y-a[0])/(b[0]-a[0])));t=smooth(t);return [a[k]*(1-t)+b[k]*t for k in range(1,4)]
 return list(PROFILE[-1][1:])
def scalp(y,theta,offset=0):
 zc,rx,rz=section(y);return Vector(((rx+offset)*math.cos(theta),y,zc+(rz+offset)*math.sin(theta)))
def facade_x(y,z):
 zc,rx,rz=section(y);v=(z-zc)/rz;xx=rx*math.sqrt(max(.015,1-v*v));floor=.128*(1-smooth((z-1.803)/.060))+.058*smooth((z-1.803)/.060);return max(floor,xx)
def closed_patch(fn,nu=30,nv=20,wall=.0035,periodic=False,side=None):
 # Numerical surface normals carry finite wall into the curved receiving
 # envelope. Periodic annuli have welded seam topology, no duplicate rings.
 vs=[];norms=[];countv=nv if periodic else nv+1
 for i in range(nu+1):
  u=i/nu
  for j in range(countv):
   v=j/nv;p=fn(u,v);du=fn(min(1,u+.0001),v)-fn(max(0,u-.0001),v);dv=fn(u,v+.0001 if periodic else min(1,v+.0001))-fn(u,v-.0001 if periodic else max(0,v-.0001));n=du.cross(dv)
   assert n.length>1e-15,(u,v)
   n.normalize();ref=Vector((side,0,0)) if side else p-Vector((0,p.y,section(p.y)[0]))
   if n.dot(ref)<0:n=-n
   vs.append(p);norms.append(n)
 total=len(vs);vs+= [p-wall*n for p,n in zip(vs.copy(),norms)];faces=[]
 for i in range(nu):
  for j in range(nv):
   k=(j+1)%countv;a=i*countv+j;b=i*countv+k;c=(i+1)*countv+k;d=(i+1)*countv+j;faces.extend([(a,b,c,d),(total+d,total+c,total+b,total+a)])
 for j in range(nv):
  k=(j+1)%countv;faces.append((k,j,total+j,total+k));a=nu*countv+j;b=nu*countv+k;faces.append((a,b,total+b,total+a))
 if not periodic:
  for i in range(nu):
   a=i*countv;b=(i+1)*countv;faces.append((a,b,total+b,total+a));a+=nv;b+=nv;faces.append((b,a,total+a,total+b))
 return vs,faces

def skull_band(y0,y1,angle0,angle1,offset=0,tip=.95,lean=.0):
 def fn(u,v):
  width=1-(1-tip)*smooth((u-.45)/.55);center=(angle0+angle1)/2+lean*u;theta=center+(v-.5)*(angle1-angle0)*width;y=y0+(y1-y0)*u+.010*math.sin(math.pi*v)**2*u;return scalp(y,theta,offset)
 return closed_patch(fn)
def face_sheet(side,outline,wall=.0045):
 # Triangulated curved plate includes recursively sampled interior vertices,
 # not merely a warped perimeter/flat n-gon.
 keys={};coords=[];tris=[]
 def ix(p):
  key=(round(p.x,7),round(p.y,7))
  if key not in keys:keys[key]=len(coords);coords.append((p.x,p.y))
  return keys[key]
 def sub(a,b,c,depth):
  if depth:
   ab=(a+b)/2;bc=(b+c)/2;ca=(c+a)/2;sub(a,ab,ca,depth-1);sub(ab,b,bc,depth-1);sub(ca,bc,c,depth-1);sub(ab,bc,ca,depth-1)
  else:tris.append((ix(a),ix(b),ix(c)))
 polygonpoints=[Vector((y,z,0)) for y,z in outline]
 for tri in tessellate_polygon([polygonpoints]):sub(*[polygonpoints[t] if isinstance(t,int) else t for t in tri],2)
 points=[];norms=[]
 for y,z in coords:
  x=facade_x(y,z);dy=(facade_x(y+.0001,z)-facade_x(y-.0001,z))/.0002;dz=(facade_x(y,z+.0001)-facade_x(y,z-.0001))/.0002;n=Vector((side,-dy,-dz)).normalized();points.append(Vector((side*x,y,z)));norms.append(n)
 n=len(points);v=points+[p-wall*nn for p,nn in zip(points,norms)];f=list(tris)+[tuple(n+i for i in reversed(t)) for t in tris];edge={}
 for t in tris:
  for a,b in zip(t,t[1:]+t[:1]):edge.setdefault(tuple(sorted((a,b))),[]).append((a,b))
 for e,x in edge.items():
  if len(x)==1:a,b=x[0];f.append((a,b,n+b,n+a))
 return v,f

def orbital(side):
 def fn(u,v):
  a=math.tau*v;co=math.cos(a);si=math.sin(a);r=.048*(1-u)+(.070+.013*max(0,co)+.013*max(0,si)-.006*max(0,-co))*u;y=-.5055+r*co+.014*max(0,co)**3*u;z=1.756+r*si;x=(.126+.005*si)*(1-u)+facade_x(y,z)*u;return Vector((side*x,y,z))
 return closed_patch(fn,nu=14,nv=72,wall=.005,periodic=True,side=side)
def props(o):return json.dumps(dict(o.items()),default=lambda x:list(x),sort_keys=True)
def snap(o):return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(f.vertices) for f in o.data.polygons),tuple(m.name if m else None for m in o.data.materials),props(o),o.hide_render,o.hide_viewport)
def node(o):return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),props(o))
def apply():
 bpy.context.view_layer.update();pivot=bpy.data.objects['head'].matrix_world.translation.copy();assert (pivot-Vector((0,-.3226,1.6028))).length<1e-6
 nodes={o.name:node(o) for o in bpy.data.objects if o.type=='EMPTY'}
 removed=[o.name for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('Rounded swept crown lamina','Swept temporal lamina'))]
 changed=['V4 cranial inner shell','Continuous temporal shell -1','Continuous temporal shell 1']+[f'{prefix} {side}' for prefix in FACADES for side in (-1,1)]
 owned=set(removed+changed);protected={o.name:snap(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in owned};added=[];errors=[];witness=[]
 def install(name,v,f,owner=None):
  if owner:
   template=bpy.data.objects['Forged orbital brow -1'];o=bpy.data.objects.new(name,template.data.copy());bpy.context.scene.collection.objects.link(o);o.parent=bpy.data.objects[owner]
   for k in template.keys():o[k]=template[k]
   o['region']='head';o['surfaceRole']='plate';o['exteriorEras']='maker,mechanic,builder';o['constructionClass']='inherited-passive';added.append(name)
  else:o=bpy.data.objects[name]
  assert o.parent.name in ('head','cranial-cover');bpy.context.view_layer.update();inv=o.matrix_world.inverted();world=[pivot+1.30*(Vector(p)-pivot) for p in v];m=bpy.data.meshes.new(name+' V27 wrapped finite sheet');m.from_pydata([inv@p for p in world],[],f);m.update()
  for mat in o.data.materials:m.materials.append(mat)
  bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  assert bm.calc_volume(signed=True)>0,name;bm.to_mesh(m);bm.free();o.data=m;o.modifiers.clear()
  for q in m.polygons:q.use_smooth=len(q.vertices)==4
  err=max((o.matrix_world@q.co-p).length for q,p in zip(m.vertices,world));assert err<1e-6;errors.append(err);witness.append({'name':name,'owner':o.parent.name,'rawBounds':[[min(p[k] for p in world) for k in range(3)],[max(p[k] for p in world) for k in range(3)]]})
 for n in removed:bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
 # Three closed backing patches leave optic ports and jaw mechanism open.
 pieces=[skull_band(-.555,-.222,.44,2.70,-.011),skull_band(-.406,-.217,-.66,.48,-.013),skull_band(-.406,-.217,math.pi-.48,math.pi+.66,-.013)];v=[];f=[]
 for a,b in pieces:start=len(v);v+=a;f+=[tuple(start+k for k in face) for face in b]
 install('V4 cranial inner shell',v,f)
 for side in (-1,1):
  a,b=(-.72,.40) if side==1 else (math.pi-.40,math.pi+.72);v,f=skull_band(-.419,-.226,a,b,-.005,tip=.78,lean=-.08*side);install(f'Continuous temporal shell {side}',v,f)
  outline=[(-.353,1.824),(-.395,1.860),(-.449,1.870),(-.501,1.846),(-.548,1.811),(-.556,1.784),(-.548,1.789),(-.538,1.800),(-.523,1.806),(-.505,1.810),(-.486,1.806),(-.468,1.796),(-.442,1.805),(-.416,1.811),(-.393,1.796),(-.374,1.793)]
  v,f=face_sheet(side,outline);install(f'Forged orbital brow {side}',v,f)
  outline=[(-.402,1.794),(-.424,1.753),(-.455,1.716),(-.483,1.705),(-.509,1.700),(-.535,1.708),(-.558,1.725),(-.581,1.737),(-.596,1.713),(-.574,1.693),(-.532,1.683),(-.490,1.684),(-.451,1.702),(-.421,1.735),(-.394,1.781)]
  v,f=face_sheet(side,outline);install(f'Broad swept cheek band {side}',v,f)
  v,f=orbital(side);install(f'Forged orbital mounting plate {side}',v,f)
  outline=[(-.547,1.800),(-.565,1.812),(-.582,1.784),(-.588,1.729),(-.576,1.710),(-.561,1.725),(-.559,1.765)]
  v,f=face_sheet(side,outline);install(f'V24 anterior orbital root receiver {side}',v,f)
 # Anterior plate lies outside the following row by6mm pre-mass. Curved
 # transverse sweep and narrowing aft edge retain plate character, no fins.
 for i,(a,b,offset,ang) in enumerate([(-.555,-.388,.018,.43),(-.474,-.302,.012,.37),(-.388,-.218,.006,.46)]):
  v,f=skull_band(a,b,ang,math.pi-ang,offset,tip=.56,lean=.045*(-1 if i%2 else 1));install(f'V27 dorsal swept cranial course {i}',v,f,'cranial-cover')
 for side in (-1,1):
  for bank,(a,b,off) in enumerate([(-.473,-.295,.018),(-.386,-.218,.010)]):
   for row,(theta,span,lean) in enumerate([(.50,.63,-.18),(-.02,.64,-.14),(-.48,.54,-.06)]):
    if bank==0 and row==2:a=-.421;b=-.256
    lo=theta-span/2;hi=theta+span/2
    if side==-1:lo,hi=math.pi-hi,math.pi-lo;lean=-lean
    v,f=skull_band(a+.012*row,b+.007*row,lo,hi,off,tip=.30,lean=lean);install(f'V27 temporal swept cranial course {side} {bank} {row}',v,f,'cranial-cover')
 bpy.context.view_layer.update();assert nodes=={o.name:node(o) for o in bpy.data.objects if o.type=='EMPTY'};assert protected=={n:snap(bpy.data.objects[n]) for n in protected}
 return {'region':'cranial-wrap','status':'Curved construction study; likeness and movement acceptance pending','changedMeshes':changed,'added':added,'removed':removed,'ownedOriginals':sorted(owned),'changedNodes':[],'allNamedNodesExact':len(nodes),'protectedMeshSnapshotsExact':len(protected),'selectedBillJawOpticExact':True,'materialDefinitionsChanged':False,'eraEligibilityChanged':False,'maximumAuthoredWorldErrorM':max(errors),'profilePreMassNative':PROFILE,'wallPreMassM':.0035,'newPlateCount':len(added),'boundWitnesses':witness,'limits':['Finite closed walls and rigid rest attachments only.','Aft layering/skull backing are proposed hidden construction; jaw and cranial opening require discrete evaluated checks.']}
