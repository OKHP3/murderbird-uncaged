"""V19 coordinated torso, finite cervical underlap and outboard access hinge.
Qualitative authored dimensions; reference likeness and engineering remain review gates.
"""
import math
import bpy,bmesh
from mathutils import Vector

TORso=((.60,.90,.00),(.78,.86,.025),(.98,.89,.061),(1.14,.90,.074),(1.24,.85,.075),(1.34,.76,.075))
PROFILE=((1.17,-.349,-.074,.238),(1.23,-.337,-.087,.216),
 (1.28,-.325,-.112,.185),(1.32,-.335,-.142,.157),
 (1.35,-.348,-.176,.132),(1.395,-.354,-.180,.111))

def smooth(x):
 x=max(0.,min(1.,x));return x*x*(3-2*x)
def sample(profile,z,k):
 if z<=profile[0][0]:return profile[0][k]
 if z>=profile[-1][0]:return profile[-1][k]
 for a,b in zip(profile,profile[1:]):
  if a[0]<=z<=b[0]:
   t=smooth((z-a[0])/(b[0]-a[0]));return a[k]*(1-t)+b[k]*t

def torso_point(p):
 # Whole envelope deformation shared by cover, its backing and body load paths.
 q=p.copy();front=smooth((.10-p.y)/.25)
 q.x*=1-(1-sample(TORso,p.z,1))*front
 q.y+=sample(TORso,p.z,2)*front
 # The top anterior lip slopes into the neck; rear shoulder crown stays planted.
 q.z-=.036*smooth((p.z-1.19)/.14)*front
 return q

def deform(obj,fn):
 inv=obj.matrix_world.inverted()
 for v in obj.data.vertices:v.co=inv@fn(obj.matrix_world@v.co)
 obj.data.update()

def point(z,a,off):
 f,r,w=[sample(PROFILE,z,k) for k in (1,2,3)]
 return Vector(((w+off)*math.sin(a),(f+r)/2-((r-f)/2+off)*math.cos(a),z))

def install(obj,top,bottom,center,half,off=.003,wall=.005):
 rows=24;cols=24;verts=[];faces=[];inv=obj.matrix_world.inverted()
 for j in range(rows+1):
  t=j/rows
  for k in range(cols+1):
   u=2*k/cols-1;z=top+(bottom-top)*t-.003*(1-u*u)*smooth(t)
   verts.append(inv@point(z,center+half*u,off+.0015*(1-u*u)*math.sin(math.pi*t)))
 for j in range(rows):
  for k in range(cols):
   i=j*(cols+1)+k;faces.append((i,i+cols+1,i+cols+2,i+1))
 old=obj.data;mesh=bpy.data.meshes.new(obj.name+' V19 continuous formed underlap');mesh.from_pydata(verts,[],faces);mesh.update()
 for mat in old.materials:mesh.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 if (obj.matrix_world.to_3x3()@mesh.polygons[len(mesh.polygons)//2].normal).dot(Vector((math.sin(center),-math.cos(center),0)))<0:
  bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 obj.data=mesh
 if not old.users:bpy.data.meshes.remove(old)
 obj.modifiers.clear();m=obj.modifiers.new('Finite formed wall','SOLIDIFY');m.thickness=wall;m.offset=-1;m.use_even_offset=True
 m=obj.modifiers.new('Returned formed edges','BEVEL');m.width=.0007;m.segments=2
 for p in mesh.polygons:p.use_smooth=True
 return {'name':obj.name,'owner':obj.parent.name,'topZ':top,'bottomZ':bottom,'center':center,'halfAngle':half,'wall':wall}

def rigid_mesh(name,verts,faces,owner,material,role):
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
 # Orientation-only repair: finite support solids must export outward normals.
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(mesh);bm.free();mesh.update()
 obj=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(obj)
 obj.parent=owner;obj.matrix_parent_inverse=owner.matrix_world.inverted();mesh.materials.append(material)
 obj['region']='breast';obj['surfaceRole']=role;obj['exteriorEras']='maker,mechanic,builder'
 bevel=obj.modifiers.new('Machined support edges','BEVEL');bevel.width=.001;bevel.segments=2
 return obj

def box(name,center,size,owner,mat):
 c=Vector(center);s=Vector(size)/2
 verts=[tuple(c+Vector((x*s.x,y*s.y,z*s.z))) for z in (-1,1) for y in (-1,1) for x in (-1,1)]
 return rigid_mesh(name,verts,[(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)],owner,mat,'frame')

def bottom_bearing(name,x,owner,mat):
 verts=[];faces=[];n=32;cy=-.077;cz=.625
 for xx in (x-.007,x+.007):
  for r in (.008,.015):
   for k in range(n):a=2*math.pi*k/n;verts.append((xx,cy+r*math.cos(a),cz+r*math.sin(a)))
 for k in range(n):
  l=(k+1)%n
  faces.extend([(k,l,n+l,n+k),(2*n+k,3*n+k,3*n+l,2*n+l),(k,2*n+k,2*n+l,l),(n+k,n+l,3*n+l,3*n+k)])
 return rigid_mesh(name,verts,faces,owner,mat,'bearing')

def bottom_pin(owner,mat):
 verts=[];faces=[];n=32
 for x in (-.185,.185):
  for k in range(n):a=2*math.pi*k/n;verts.append((x,-.077+.006*math.cos(a),.625+.006*math.sin(a)))
 for k in range(n):l=(k+1)%n;faces.append((k,l,n+l,n+k))
 faces.extend([tuple(reversed(range(n))),tuple(n+k for k in range(n))])
 return rigid_mesh('V19 moving bottom access axle',verts,faces,owner,mat,'bearing')

def apply():
 changed=[];guards=[];added=[];hinge=bpy.data.objects['breastplate'];body=bpy.data.objects['body']
 hinge['inspectionAxis']='x';hinge['inspectionOpenRadians']=1.1
 old=hinge.matrix_world.copy();children={o:o.matrix_world.copy() for o in hinge.children}
 new=old.copy();new.translation=Vector((0,-.077,.625));hinge.matrix_world=new;bpy.context.view_layer.update()
 for o,m in children.items():o.matrix_world=m
 bpy.context.view_layer.update()
 # Preserve rest matrices exactly despite the new rotation origin; direct children include anchor empties/guides.
 assert all(max(abs(o.matrix_world[r][c]-m[r][c]) for r in range(4) for c in range(4))<2e-7 for o,m in children.items())
 torso=[]
 for obj in bpy.data.objects:
  if obj.type=='MESH' and (obj.parent==hinge or (obj.parent==body and obj.get('region') in ('breast','back'))):
   deform(obj,torso_point);changed.append(obj.name);torso.append(obj.name)
 upper=bpy.data.objects['Throat formed lamina 3']
 # Upper mounting rows remain exact; lower rows reform into the continuous throat curve.
 # The existing 13x13 patch retains its first four rows and rigid cervical-upper owner.
 inv=upper.matrix_world.inverted()
 assert len(upper.data.vertices)==169
 for v in upper.data.vertices:
  row,col=divmod(v.index,13)
  if row<=3:continue
  t=smooth((row-3)/9);u=2*col/12-1
  original=upper.matrix_world@v.co
  z=original.z+.007*t
  target=point(z,.61*u,.003)
  v.co=inv@(original*(1-t)+target*t)
 upper.data.update();changed.append(upper.name)
 for n,top,bottom,half in ((4,1.360,1.312,.67),(5,1.324,1.263,.75),(6,1.275,1.174,.84)):
  o=bpy.data.objects[f'Throat formed lamina {n}'];guards.append(install(o,top,bottom,0,half));changed.append(o.name)
 for side in (-1,1):
  for n,top,bottom in ((5,1.350,1.258),(6,1.273,1.172)):
   o=bpy.data.objects[f'Cervical flank lamina {side} {n}'];guards.append(install(o,top,bottom,side*1.32,.43));changed.append(o.name)
 o=bpy.data.objects['Lower cervical open backing'];guards.append(install(o,1.350,1.169,0,1.72,off=-.009,wall=.004));changed.append(o.name)
 mat=bpy.data.materials['Neutral / frame'];bmat=bpy.data.materials['Neutral / bearing']
 for side in (-1,1):
  x=side*.145
  added.append(box('V19 fixed bottom hinge support '+str(side),(x,-.014,.640),(.035,.112,.024),body,mat).name)
  added.append(bottom_bearing('V19 fixed bottom access bearing '+str(side),x,body,bmat).name)
  # Door returns sit inboard of fixed bearings and rise into the finite cover wall.
  added.append(box('V19 moving bottom cover return '+str(side),(side*.120,-.078,.648),(.014,.014,.048),hinge,mat).name)
 added.append(bottom_pin(hinge,bmat).name)
 bpy.context.view_layer.update()
 return {'status':'V19 bottom-hinged coordinated construction candidate; changed mechanism after expanded side-hinge failure; visual/motion review pending','changed':sorted(changed),'added':added,'removed':[],
 'torsoChangedNames':torso,'torsoMapWorld':TORso,'neckProfileWorld':PROFILE,'guards':guards,
 'articulation':{'name':'breastplate','parent':body.name,'oldWorldMatrix':[list(r) for r in old],'newWorldMatrix':[list(r) for r in hinge.matrix_world],'preservedDirectChildWorldRestNames':sorted(o.name for o in children),'nativeOpeningAxis':'local X positive1.1rad; browser local X positive1.1rad','inspectionAxis':'x','inspectionOpenRadians':1.1},
 'construction':'Tapered breast with gentler upper lip recession, finite flared neck underlap reaching Z1.17 inside cavity, smooth front throat contour. Bottom horizontal native-X access hinge at the actual lower anterior shell section; two fixed annular bearings, body seats, two finite door returns and a captive solid axle. Cover opens forward/down by1.1rad.',
 'preserved':['rigid node inventory','all non-breastplate rigid world rest transforms','all direct breastplate child world rest transforms before shaping','historical guides','material definitions','explicit axis/range extension through existing movement interface; existing left restriction','era eligibility'],
 'limits':['Authored dimensions and hidden support are proposals.','Fresh hinge movement and regional crossing checks required; no engineering, owner likeness or continuous sweep acceptance.']}
