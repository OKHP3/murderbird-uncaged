"""Coarse V22 shared armored neck cassette on exact Frame04.
Native metres/Z-up/-Y-front. Runtime owns quaternion half-relative followers.
No driver, animation, export or rendering is installed by this module.
"""
import bpy,bmesh,math
from mathutils import Vector,Matrix
ERAS='maker,mechanic,builder'
BASE_SHA256='b3ac4677d2e76a0e08544323306c07f2ed7e61cd381d274a944d8e5b87031d1f'
WALL=.004
OLD=('V21 lower swept throat keel','V21 upper swept throat keel','V21 lower swept nape return','V21 upper swept nape return','V21 ascending root yoke -1','V21 ascending root yoke 1','V21 upper cervical directional guard -1','V21 upper cervical directional guard 1','V21 linked joint front','V21 linked joint nape','V21 linked joint side -1','V21 linked joint side 1')
BOUNDARIES=('V4 cranial inner shell','V21 recessed breast course backing','V21 fixed shoulder breast return -1','V21 fixed shoulder breast return 1')+tuple('V21 breast course 01 panel '+str(i).zfill(2) for i in range(1,5))
PROFILE=((1.245,-.390,.035,.190),(1.30,-.365,-.018,.166),(1.38,-.335,-.093,.123),(1.43,-.341,-.125,.112),(1.48,-.369,-.160,.110),(1.55,-.420,-.195,.107),(1.60,-.441,-.230,.100),(1.635,-.425,-.260,.098))
SECTORS=(('front left',-.73,-.012),('front right',.012,.73),('flank left',-2.31,-.75),('flank right',.75,2.31),('nape',2.33,math.tau-2.33))


def signature(o):
 return (o.parent.name if o.parent else None,tuple(tuple(float(x) for x in r) for r in o.matrix_world),tuple((k,repr(o[k])) for k in sorted(o.keys())))
def mesh_signature(o):
 return (signature(o),tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(f.vertices) for f in o.data.polygons),tuple(m.name if m else None for m in o.data.materials))
def ease(t):
 t=max(0,min(1,t));return t*t*(3-2*t)
def profile(z):
 # Smooth cubic Hermite sections; the shared throat curve precedes plates.
 i=next((i for i in range(len(PROFILE)-1) if z<PROFILE[i+1][0]),len(PROFILE)-2)
 a,b=PROFILE[i],PROFILE[i+1];t=max(0,min(1,(z-a[0])/(b[0]-a[0])));h=b[0]-a[0];out=[]
 for c in range(1,4):
  p=PROFILE[max(0,i-1)];n=PROFILE[min(len(PROFILE)-1,i+2)]
  m0=(b[c]-p[c])/(b[0]-p[0]);m1=(n[c]-a[c])/(n[0]-a[0])
  out.append((2*t**3-3*t*t+1)*a[c]+(t**3-2*t*t+t)*h*m0+(-2*t**3+3*t*t)*b[c]+(t**3-t*t)*h*m1)
 return out

def formed(name,owner,fun,material,role='guard',rows=20,cols=18):
 verts=[];faces=[];outer=[];inner=[]
 for j in range(rows+1):
  t=j/rows
  for k in range(cols+1):
   q=k/cols;p=Vector(fun(t,q));dt=Vector(fun(min(1,t+.001),q))-Vector(fun(max(0,t-.001),q));dq=Vector(fun(t,min(1,q+.001)))-Vector(fun(t,max(0,q-.001)))
   normal=dt.cross(dq).normalized()
   # Envelope radial direction selects outside consistently for each patch.
   if hasattr(fun,'origin'): radial=p-fun.origin
   else:
    fr,re,wi=profile(p.z);radial=p-Vector((0,(fr+re)/2,p.z))
   if normal.dot(radial)<0:normal.negate()
   outer.append(p);inner.append(p-normal*WALL)
 verts=outer+inner;n=len(outer)
 for j in range(rows):
  for k in range(cols):
   a=j*(cols+1)+k;b=a+cols+1;faces.extend(((a,a+1,b+1,b),(a+n,b+n,b+1+n,a+1+n)))
 edge=list(range(cols+1))+[j*(cols+1)+cols for j in range(1,rows+1)]+list(range(n-2,n-cols-2,-1))+[j*(cols+1) for j in range(rows-1,0,-1)]
 for i,a in enumerate(edge):b=edge[(i+1)%len(edge)];faces.append((a,b,b+n,a+n))
 inv=owner.matrix_world.inverted();mesh=bpy.data.meshes.new(name+' mesh');mesh.from_pydata([inv@p for p in verts],[],faces);mesh.update();mesh.materials.append(material)
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name;assert bm.calc_volume(signed=True)>0,name;bm.to_mesh(mesh);bm.free()
 obj=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(obj);obj.parent=owner;obj.matrix_parent_inverse=Matrix.Identity(4);obj.matrix_basis=Matrix.Identity(4)
 for f in mesh.polygons:f.use_smooth=True
 obj['region']='neck-cassette';obj['surfaceRole']=role;obj['exteriorEras']=ERAS;obj['constructionClass']='inherited-passive';obj['proposal']=True
 obj['constructionOwner']=owner.name;obj['wallM']=WALL;obj['geometryStatus']='Coarse directional cassette; not motion or likeness acceptance'
 return obj


def radius(which,theta):
 if which=='root':return .224-.076*ease((abs(math.atan2(math.sin(theta),math.cos(theta)))-.73)/1.60)
 return .125 if which=='intermediate' else .115

def spherical(center,r,theta,phi):
 return center+Vector((r*math.sin(theta)*math.cos(phi),-r*math.cos(theta)*math.cos(phi),r*math.sin(phi)))

def skin_fun(level,a,b,root,inter,head):
 z0,z1=(1.286,1.441) if level=='lower' else (1.420,1.623)
 def fun(t,q):
  # Diagonal terminals distribute the joint seam across the S curve.
  theta=a+(b-a)*q;z=z1+(z0-z1)*t+.010*(q-.5)*(1 if a<0 else -1)
  front,rear,width=profile(z);cy=(front+rear)/2;ry=(rear-front)/2
  p=Vector((width*math.sin(theta),cy-ry*math.cos(theta),z))
  # One6mm receiving depth, embedded in the overall armor volume. Actual
  # sphere-centred terminal geometry replaces the old caged end positions.
  joint,which=(inter,'intermediate') if level=='lower' and t<.3 else (root,'root') if level=='lower' else (head,'skull') if t<.3 else (inter,'intermediate')
  w=ease((.30-t)/.30) if t<.30 else ease((t-.70)/.30) if t>.70 else 0
  r=radius(which,theta)-.006;d=p-joint
  if d.length>0:p=p.lerp(joint+d.normalized()*r,w)
  return p
 return fun


def cover_fun(which,a,b,center):
 isfront='unused'
 def fun(t,q):
  theta=a+(b-a)*q;rear=abs(math.atan2(math.sin(theta),math.cos(theta)))>2.3
  if which=='root':lo,hi=(.60,1.08) if rear else (.12,.85)
  elif which=='intermediate':lo,hi=(-.65,.65)
  else:lo,hi=(-1.03,.15) if rear else (-.90,.16)
  # Broad curved sectors have swept/slanted free ends instead of ring edges.
  phi=lo+(hi-lo)*t+.11*(q-.5)*(1 if a<0 else -1)
  return spherical(center,radius(which,theta),theta,phi)
 fun.origin=center
 return fun


def evaluate_into_data(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=bpy.context.evaluated_depsgraph_get());o.data=m;o.modifiers.clear()

def difference(obj,cutter,name):
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
 m=obj.modifiers.new(name,'BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter;bpy.ops.object.modifier_apply(modifier=m.name);obj.select_set(False)

def sphere_cut(name,center,r,objects):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,radius=r,location=center);cut=bpy.context.object;cm=cut.data
 for o in objects:difference(o,cut,name)
 bpy.data.objects.remove(cut,do_unlink=True);bpy.data.meshes.remove(cm)

def journal_window(obj,center,r):
 # A real transverse passage reveals the retained journal/race. The rest of
 # the broad guard remains, unlike the stripped neck05 skin strategy.
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=.65,location=center,rotation=(0,math.pi/2,0));cut=bpy.context.object;cm=cut.data;difference(obj,cut,'Journal receiving passage')
 bpy.data.objects.remove(cut,do_unlink=True);bpy.data.meshes.remove(cm)


def follower(name,parent,target):
 node=bpy.data.objects.new(name,None);bpy.context.scene.collection.objects.link(node);node.parent=parent
 node.matrix_world=Matrix.Translation(target.matrix_world.translation);bpy.context.view_layer.update()
 node['region']='neck-cassette';node['exteriorEras']=ERAS;node['linkedMotionTarget']=target.name
 node['linkedMotion']='parent-space delta=currentJointQ*inverse(restJointQ); coverQ=slerp(identity,delta,0.5)*restCoverQ'
 assert node.matrix_world.to_quaternion().angle<1e-6
 assert (node.location-target.location).length<1e-6
 return node


def apply():
 bpy.context.view_layer.update();original_nodes={o.name:signature(o) for o in bpy.data.objects if o.type=='EMPTY'}
 protected={o.name:mesh_signature(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in OLD+BOUNDARIES}
 root=bpy.data.objects['neck'].matrix_world.translation.copy();inter=bpy.data.objects['cervical-upper'].matrix_world.translation.copy();head=bpy.data.objects['head'].matrix_world.translation.copy()
 mat=bpy.data.objects['V21 lower swept throat keel'].data.materials[0];staged=[];added=[]
 for n in OLD:
  o=bpy.data.objects[n];staged.append({'name':n,'owner':o.parent.name});bpy.data.objects.remove(o,do_unlink=True)
 newroot=follower('cervical-root-cover',bpy.data.objects['body'],bpy.data.objects['neck']);newskull=follower('cervical-skull-cover',bpy.data.objects['cervical-upper'],bpy.data.objects['head'])
 added.extend((newroot.name,newskull.name))
 for level,owner in (('lower','neck'),('upper','cervical-upper')):
  for label,a,b in SECTORS:
   o=formed('V22 '+level+' cassette '+label,bpy.data.objects[owner],skin_fun(level,a,b,root,inter,head),mat);added.append(o.name)
 for which,node,center in (('root',newroot,root),('intermediate',bpy.data.objects['cervical-joint-cover'],inter),('skull',newskull,head)):
  for label,a,b in SECTORS:
   o=formed('V22 '+which+' directional joint cover '+label,node,cover_fun(which,a,b,center),mat);added.append(o.name)
   if label.startswith('flank'):journal_window(o,center,.031 if which!='skull' else .029)
 # The original door remains. Its top is fitted as the finite receiving edge
 # beneath the full root cassette, not concealed by a surface clamp.
 changed=[]
 for name in BOUNDARIES:
  o=bpy.data.objects[name];evaluate_into_data(o);changed.append(name)
 sphere_cut('Finite neck-root receiving cavity',root,.227,[bpy.data.objects[n] for n in BOUNDARIES if n!='V4 cranial inner shell'])
 sphere_cut('Finite skull inner receiving socket',head,.118,[bpy.data.objects['V4 cranial inner shell']])
 bpy.context.view_layer.update()
 assert all(signature(bpy.data.objects[n])==s for n,s in original_nodes.items())
 assert all(mesh_signature(bpy.data.objects[n])==s for n,s in protected.items())
 return {'status':'ONE coarse full-volume cervical cassette proposal, awaiting3actual-pose visual gate','region':'neck-cassette','changed':changed,'added':added,'removed':staged,'primaryPivotChanges':[],
  'preservedOriginalNodes':len(original_nodes),'preservedProtectedMeshes':len(protected),'profile':PROFILE,'wallM':WALL,'receivingStepM':.006,
  'followers':[{'name':newroot.name,'parent':'body','target':'neck','worldRestNativeM':list(root)},{'name':newskull.name,'parent':'cervical-upper','target':'head','worldRestNativeM':list(head)}],
  'followerRule':'parent-space delta=currentJointQ*inverse(restJointQ); coverQ=slerp(identity,delta,.5)*restCoverQ; no drivers',
  'construction':'Full shared S-profile lower/upper armor remains. Broad outer covers at root/intermediate/skull receive recessed concentric finite terminals. Transverse journal passages expose actual bearings. Body/door upper skin forms a finite root receiving boundary; cranial INNER shell forms the head receiving socket. Visible head exterior and all primary frame/joints retained.',
  'limits':['Authored hidden receiving construction is proposed, not historical evidence.','Only3actual pose smoke/visual checks; no continuous or whole-model clearance claim.','Root angular radius transitions are proposed and must be checked with Maker yaw.','Existing frame/body and head exterior interfaces remain subject to fresh checks.']}
