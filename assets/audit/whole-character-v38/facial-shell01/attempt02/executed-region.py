"""Directional fixed head side volume and compact optic recess; authored study."""
import bpy,bmesh,math,runpy
from mathutils import Vector
REMOVED=[f'V33 diagonal brow receiver {s} {i}'for s in[-1,1]for i in range(3)]+[f'V38 optic cheek shield {s} {i}'for s in[-1,1]for i in range(3)]
# Counter-clockwise native YZ outline: actual volume, not a circular outer bezel.
OUTLINE=[(-.683,1.682,.109),(-.666,1.753,.112),(-.620,1.790,.127),(-.536,1.811,.137),(-.440,1.793,.113),(-.342,1.755,.095),(-.366,1.697,.102),(-.442,1.657,.123),(-.510,1.633,.139),(-.601,1.625,.143),(-.663,1.647,.123)]
CY,CZ=-.5958000421524048,1.6904840469360352

def stock(o):
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 non=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);todo=set(bm.verts);comp=0
 while todo:
  comp+=1;run=[todo.pop()]
  while run:
   for e in run.pop().link_edges:
    for v in e.verts:
     if v in todo:todo.remove(v);run.append(v)
 bm.to_mesh(o.data);bm.free();return {'nonmanifoldEdges':non,'signedVolumeM3':vol,'connectedComponents':comp}
def replace(o,v,f):
 m=bpy.data.meshes.new(o.name+' directional finite stock');m.from_pydata([list(o.matrix_world.inverted()@Vector(p))for p in v],[],f);m.update()
 for mat in o.data.materials:m.materials.append(mat)
 o.data=m
 for p in m.polygons:p.use_smooth=False
 o['constructionDescription']='Reconstructed fixed head-owned directional facial wall/compact optic seat; authored finite stock, assembly fit not certified.';o['v38FacialShell01']='Proposal; lens centre/diameter and all unrelated geometry retained'
 return stock(o)
def boundary(phi):
 dy,dz=math.cos(phi),math.sin(phi);best=None
 for a,b in zip(OUTLINE,OUTLINE[1:]+OUTLINE[:1]):
  ay,az=a[0]-CY,a[1]-CZ;ey,ez=b[0]-a[0],b[1]-a[1];det=dy*(-ez)+dz*ey
  if abs(det)<1e-10:continue
  t=(ay*(-ez)+az*ey)/det;u=(dy*az-dz*ay)/det
  if t>0 and -.00001<=u<=1.00001 and(best is None or t<best[0]):best=(t,a[2]+(b[2]-a[2])*u)
 assert best,phi
 return best

def wall(side):
 o=bpy.data.objects[f'V31 fixed temporal receiving wall {side}'];n,k=96,10;v=[]
 for inner in[False,True]:
  for j in range(k+1):
   t=j/k
   for i in range(n):
    phi=2*math.pi*i/n;r,xend=boundary(phi);rr=.0415+(r-.0415)*t
    # Recess throat locally; sloped broad planes turn inward into skull at outer lands.
    x=.151*(1-t)+xend*t+.006*math.sin(math.pi*t)*max(0,math.sin(phi))
    v.append((side*(x-(.0045 if inner else 0)),CY+rr*math.cos(phi),CZ+rr*math.sin(phi)))
 f=[];h=(k+1)*n
 for j in range(k):
  for i in range(n):a=j*n+i;b=j*n+(i+1)%n;c=(j+1)*n+(i+1)%n;d=(j+1)*n+i;f.extend([(a,b,c,d),(h+d,h+c,h+b,h+a)])
 for j in[0,k]:
  for i in range(n):a=j*n+i;b=j*n+(i+1)%n;f.append((a,h+a,h+b,b))
 return o,replace(o,v,f)
def ring(name,side,inner,outer,x0,x1,sectors=None):
 o=bpy.data.objects[name];v=[];f=[]
 if inner==0:
  n=96
  for x in[x0,x1]:
   for i in range(n):a=2*math.pi*i/n;v.append((side*x,CY+outer*math.cos(a),CZ+outer*math.sin(a)))
  v.extend([(side*x0,CY,CZ),(side*x1,CY,CZ)])
  for i in range(n):j=(i+1)%n;f.extend([(i,j,n+j,n+i),(2*n,j,i),(2*n+1,n+i,n+j)])
  return replace(o,v,f)
 for lo,hi in(sectors or[(0,2*math.pi)]):
  closed=abs(hi-lo-2*math.pi)<1e-6;n=96 if closed else 32;count=n if closed else n+1;base=len(v)
  for x,rad in[(x0,inner),(x0,outer),(x1,outer),(x1,inner)]:
   for i in range(count):a=lo+(hi-lo)*i/n;v.append((side*x,CY+rad*math.cos(a),CZ+rad*math.sin(a)))
  for r in range(4):
   for i in range(n):a=base+r*count+i;b=base+r*count+(i+1)%count;c=base+((r+1)%4)*count+(i+1)%count;d=base+((r+1)%4)*count+i;f.append((a,b,c,d))
  if not closed:f.extend([tuple(base+r*count for r in range(4)),tuple(base+r*count+n for r in reversed(range(4)))])
 return replace(o,v,f)
def apply(second=False):
 bpy.context.view_layer.update();changed=[];records=[];added={};removed=list(REMOVED)
 for n in REMOVED:bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
 if second:
  added,newRecords=formed_plates();records.extend(newRecords);removed += [f'V31 fixed temporal receiving wall {q}'for q in[-1,1]]
  for n in removed[-2:]:bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
 for side in[-1,1]:
  if not second:
   o,s=wall(side);changed.append(o.name);records.append({'name':o.name,'role':'One tapered temple/brow/cheek wall with lens-sized cutout and axial finite thickness','outlineNativeYZX':OUTLINE,'stock':s})
  for name,ri,ro,x0,x1,sec in[(f'V31 optic recessed receiving cup {side}',.0388,.0445,.1345,.1505,None),(f'V31 passive optic cavity floor {side}',0,.0400,.11832,.1218,None),(f'V33 recessed optic retaining lip {side}',.0395,.0422,.1490,.1520,[(math.radians(12),math.radians(160)),(math.radians(195),math.radians(337))])]:
   s=ring(name,side,ri,ro,x0,x1,sec);changed.append(name);records.append({'name':name,'stock':s,'radiiM':[ri,ro],'nativeAbsX':[x0,x1],'role':'Passive compact optic recess/retention; actual lens unchanged'})
 return {'changedMeshes':changed,'removed':removed,'added':added,'changedNodes':[],'construction':records,'opticCentreNativeYZ':[CY,CZ],'preserved':'All node transforms/owners, lens aperture/cognition material/era, bill/contact, jaw/root/socket, crown and opening cranial shell, neck/body exact','limits':['Topology/positive volume not self/neighbor clearance acceptance.','Fixed wall and optic stock form one authored side-volume arrangement; true finite receiver contact still requires targeted checking.','Two segmented lip solids remain one same-owner identity; not a continuous outer bezel.','No head-to-opening-cranial-cover rigid bridge.','July head-only controls visible form; hidden support dimensions are proposals.']}

def choose_patch(name,target,side,optic):
 o=bpy.data.objects[name];v=[o.matrix_world@p.co for p in o.data.vertices];choices=[]
 for f in o.data.polygons:
  ps=[v[i]for i in f.vertices];n=(ps[1]-ps[0]).cross(ps[2]-ps[0]).normalized();c=sum(ps,Vector())/len(ps)
  if side*c.x<=0 or not all(math.hypot(p.y-optic[0],p.z-optic[1])>.066 for p in ps):continue
  if name=='V31 frontal cranial cap receiving seat':
   if not(side*n.x>.2 or n.z>.4):continue
  elif side*n.x<.4:continue
  choices.append(((c-Vector(target)).length,f.index,ps,n))
 assert choices,('No real finite seat patch',name);distance,index,ps,n=min(choices,key=lambda p:p[0]);c=sum(ps,Vector())/len(ps);ps=[c+(p-c)*.70 for p in ps];return{'target':name,'face':index,'receiverCorners':[list(p)for p in ps],'normal':list(n),'desiredToActualFaceCentreM':distance},ps,n
def convex(name,points):
 m=bpy.data.meshes.new(name);bm=bmesh.new();vs=[bm.verts.new(p)for p in points];result=bmesh.ops.convex_hull(bm,input=vs,use_existing_faces=False);bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_edges],context='VERTS');bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(m);bm.free();o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o);return o
def intersect_volume(a,b):
 o=a.copy();o.data=a.data.copy();bpy.context.scene.collection.objects.link(o);mod=o.modifiers.new('Finite commonstock diagnostic','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=b;bpy.context.view_layer.objects.active=o
 try:
  bpy.ops.object.modifier_apply(modifier=mod.name);r=stock(o);r['boundedByParticipatingVolumes']=0<r['signedVolumeM3']<=min(stock(a)['signedVolumeM3'],stock(b)['signedVolumeM3'])*1.001
 except Exception as error:r={'error':str(error)}
 bpy.data.objects.remove(o,do_unlink=True);return r

def formed_plates():
 head=bpy.data.objects['head'];records=[];added={}
 profiles={'brow':[(-.463,1.786,1.762,.106),(-.510,1.805,1.759,.136),(-.558,1.794,1.746,.154),(-.605,1.776,1.744,.151),(-.641,1.773,1.731,.130),(-.675,1.743,1.731,.108)],'cheek':[(-.460,1.710,1.680,.110),(-.501,1.681,1.651,.143),(-.550,1.657,1.626,.155),(-.601,1.650,1.622,.155),(-.645,1.664,1.638,.148),(-.677,1.653,1.644,.122)]}
 for side in[-1,1]:
  source=bpy.data.objects[f'V31 fixed temporal receiving wall {side}'];materials=[m for m in source.data.materials if m]
  for kind,rows in profiles.items():
   name=f'V38 facial-shell {"brow roof"if kind=="brow"else"cheek bridge"} {side}';nu,nv=48,8;v=[]
   for i in range(nu+1):
    u=i/nu;y=rows[0][0]+(rows[-1][0]-rows[0][0])*u
    for a,b in zip(rows,rows[1:]):
     if a[0]>=y>=b[0]:t=(y-a[0])/(b[0]-a[0]);top=a[1]+(b[1]-a[1])*t;bottom=a[2]+(b[2]-a[2])*t;x=a[3]+(b[3]-a[3])*t;break
    dy=y-CY
    if abs(dy)<.0432:
     edge=math.sqrt(.0432**2-dy**2)
     if kind=='brow':bottom=max(bottom,CZ+edge+.001)
     else:top=min(top,CZ-edge-.001)
    assert top>bottom,(name,i,top,bottom)
    for j in range(nv+1):q=j/nv;v.append(Vector((side*(x+.003*math.sin(math.pi*q)*math.sin(math.pi*u)),y,bottom+(top-bottom)*q)))
   h=len(v);v+= [p-Vector((side*.0045,0,0))for p in v];f=[];stride=nv+1
   for i in range(nu):
    for j in range(nv):a=i*stride+j;b=a+stride;f.extend([(a,a+1,b+1,b),(h+b,h+b+1,h+a+1,h+a)])
   edge=list(range(stride))+[i*stride+nv for i in range(1,nu+1)]+[nu*stride+j for j in range(nv-1,-1,-1)]+[i*stride for i in range(nu-1,0,-1)]
   for a,b in zip(edge,edge[1:]+edge[:1]):f.append((a,b,b+h,a+h))
   m=bpy.data.meshes.new(name+' finite directional stock');m.from_pydata(v,[],f);m.update();o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o);o.parent=head;bpy.context.view_layer.update();o.matrix_world=__import__('mathutils').Matrix.Identity(4)
   for mat in materials:m.materials.append(mat)
   ex={'region':'head','exteriorEras':'maker,mechanic,builder','surfaceRole':'brow-roof'if kind=='brow'else'cheek-bridge','constructionClass':'inherited-passive','constructionDescription':'Fixed longitudinal formed shield with finite head-owned receiving routes; visible/support/clearance proposal separately qualified.','v38FacialShell01':'Final second proposal, no engineering/owner acceptance'}
   for k,value in ex.items():o[k]=value
   stock(o);routes=[]
   if kind=='brow':targets=[(f'V31 passive cranial load bow {side}',(side*.13,-.478,1.711),(side*.13,-.499,1.785)),('V31 frontal cranial cap receiving seat',(side*.082,-.627,1.760),(side*.13,-.642,1.756))]
   else:targets=[(f'V31 passive cranial load bow {side}',(side*.13,-.479,1.710),(side*.137,-.493,1.674)),(f'V33 formed lower cheek receiver {side} 0',(side*.148,-.660,1.635),(side*.146,-.646,1.650))]
   for slot,(target,desired,end)in enumerate(targets):
    rec,patch,n=choose_patch(target,desired,side,(CY,CZ));e=Vector(end);pts=[p-n*.0008 for p in patch]+[p+n*.003 for p in patch]
    for dx in[-.006,-.001]:
     for dy,dz in[(-.003,-.003),(.003,-.003),(.003,.003),(-.003,.003)]:pts.append(e+Vector((side*dx,dy,dz)))
    route=convex(name+' route '+str(slot),pts);rec['routeStock']=stock(route);rec['receivingCommonStock']=intersect_volume(route,bpy.data.objects[target]);rec['plateEndCommonStock']=intersect_volume(route,o);rec['endNativeXYZ']=end
    mod=o.modifiers.new('Integral passive receiving route','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=route;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(route,do_unlink=True);routes.append(rec)
   for face in o.data.polygons:face.use_smooth=False
   records.append({'name':name,'stock':stock(o),'longitudinalYZXControls':rows,'finiteRoutes':routes,'nominalWallM':.0045});added[name]={'parent':'head','exteriorEras':'maker,mechanic,builder','region':'head','surfaceRole':ex['surfaceRole']}
 return added,records
