"""V20 short finite cervical guard courses on the preserved proportions02 study.
Native metres, Z-up, -Y-front. Qualitative constructed profile, not measured engineering.
"""
import math,json
import bpy,bmesh
from mathutils import Vector
PROFILE=((1.28,-.394,-.120,.220),(1.36,-.395,-.145,.185),
 (1.40,-.405,-.170,.155),(1.44,-.418,-.190,.132),
 (1.48,-.425,-.205,.115),(1.52,-.403,-.205,.105),(1.60,-.373,-.190,.122))
# Number, top, bottom. Source rigid owners remain unchanged at the neck/intermediate seam.
COURSES=((6,1.380,1.260),(5,1.415,1.360),(4,1.460,1.400),
 (3,1.505,1.445),(2,1.550,1.490),(1,1.595,1.535))
WALL=.0045
RADIAL_LAP=.0055

def ease(t):
 t=max(0.,min(1.,t));return t*t*(3-2*t)
def sample(z,k):
 """C1 shape-preserving cubic interpolation; no angular banks at profile knots."""
 x=[r[0] for r in PROFILE];y=[r[k] for r in PROFILE]
 if z<=x[0]:return y[0]
 if z>=x[-1]:return y[-1]
 h=[b-a for a,b in zip(x,x[1:])];d=[(b-a)/hh for a,b,hh in zip(y,y[1:],h)]
 m=[d[0]]
 for i in range(1,len(x)-1):
  if d[i-1]*d[i]<=0:m.append(0.)
  else:
   w1=2*h[i]+h[i-1];w2=h[i]+2*h[i-1]
   m.append((w1+w2)/(w1/d[i-1]+w2/d[i]))
 m.append(d[-1])
 for i in range(len(x)-1):
  if x[i]<=z<=x[i+1]:
   t=(z-x[i])/h[i]
   return (2*t**3-3*t*t+1)*y[i]+(t**3-2*t*t+t)*h[i]*m[i]+(-2*t**3+3*t*t)*y[i+1]+(t**3-t*t)*h[i]*m[i+1]

def point(z,angle,radial):
 front,rear,width=[sample(z,k) for k in (1,2,3)]
 # The root stays truly inside the measured breast opening, not flush-clamped.
 front+=.008*(1-ease((z-1.36)/.035))
 radial*=ease((z-1.375)/.035)
 cy=(front+rear)/2;depth=(rear-front)/2
 return Vector(((width+radial)*math.sin(angle),cy-(depth+radial)*math.cos(angle),z))

def install(obj,patches,wall):
 """Install separate open curved patches, each with a finite returned wall modifier."""
 inv=obj.matrix_world.inverted();verts=[];faces=[];rows=28;cols=24
 for top,bottom,center,half,radial in patches:
  base=len(verts)
  for j in range(rows+1):
   t=j/rows
   for k in range(cols+1):
    u=2*k/cols-1
    # A shallow formed lower arch retains separate course edges without pointed skirts.
    side=1 if center>0 else -1 if center<0 else 0
    # Rounded swept free edge: the tip continues down/aft, with no pointed skirt.
    z=top+(bottom-top)*t-.009*(1-u*u)**2*ease(t)-.008*side*u*ease(t)
    angle=center+half*(1-.14*ease(t))*u
    verts.append(inv@point(z,angle,radial+.0015*math.sin(math.pi*t)*(1-u*u)))
  for j in range(rows):
   for k in range(cols):
    i=base+j*(cols+1)+k;faces.append((i,i+cols+1,i+cols+2,i+1))
 old=obj.data;mesh=bpy.data.meshes.new(obj.name+' V20 short curved guard');mesh.from_pydata(verts,[],faces);mesh.update()
 for m in old.materials:mesh.materials.append(m)
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 # World radial orientation is explicit; finite wall is inward into the underlap.
 first=patches[0];center=first[2]
 n=obj.matrix_world.to_3x3()@mesh.polygons[(rows//2)*cols+cols//2].normal
 if n.dot(Vector((math.sin(center),-math.cos(center),0)))<0:
  bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
 obj.data=mesh
 if not old.users:bpy.data.meshes.remove(old)
 obj.modifiers.clear();m=obj.modifiers.new('Finite short cervical guard wall','SOLIDIFY');m.thickness=wall;m.offset=-1;m.use_even_offset=True
 m=obj.modifiers.new('Short formed guard edge','BEVEL');m.width=.0006;m.segments=2
 for p in mesh.polygons:p.use_smooth=True
 obj['constructionV20']='Short finite curved articulated guard; proposed construction; reference and motion review pending'
 obj['cervicalProfileV20']=json.dumps(PROFILE,separators=(',',':'))
 return {'name':obj.name,'owner':obj.parent.name,'patches':[{'topZ':a,'bottomZ':b,'angle':c,'halfAngle':d,'radialOffset':e} for a,b,c,d,e in patches],'wallM':wall,'openPatchCount':len(patches),'sourceEraEligibility':obj.get('exteriorEras')}

def apply():
 names=[];parts=[]
 for n,top,bottom in COURSES:
  off=.0015+(6-n)*RADIAL_LAP
  name=f'Throat formed lamina {n}';obj=bpy.data.objects[name]
  half={1:.70,2:.74,3:.78,4:.75,5:.79,6:.82}[n]
  parts.append(install(obj,[(top,bottom,0,half,off)],WALL));names.append(name)
  for side in (-1,1):
   name=f'Cervical flank lamina {side} {n}';obj=bpy.data.objects[name]
   stagger=.017 if n%2 else -.010
   if n==6:stagger=0
   center=side*(1.20 if n%2 else 1.24)
   parts.append(install(obj,[(top+stagger,bottom+stagger,center,.58,off+RADIAL_LAP)],WALL));names.append(name)
 # Separate backing strips guard the real lateral frame; neither closes the cervical tube.
 name='Lower cervical open backing';obj=bpy.data.objects[name]
 parts.append(install(obj,[(1.460,1.260,side*1.03,.16,-.010) for side in (-1,1)],.0035));names.append(name)
 name='Cervical articulated inner guards';obj=bpy.data.objects[name]
 parts.append(install(obj,[(1.595,1.410,side*.86,.12,-.014) for side in (-1,1)],.0035));names.append(name)
 bpy.context.view_layer.update()
 return {'status':'V20 local cervical construction study; no whole-silhouette, motion or engineering acceptance','changed':sorted(names),'added':[],'removed':[],
 'profile':PROFILE,'profileInterpolation':'C1 shape-preserving cubic Hermite','courseFreeEdges':'rounded9mm drop, lateral8mm down/aft sweep,14% angular taper; lateral heights alternate+17/-10mm','rootSeat':'front profile recessed8mm belowZ1.36; lap radial offset fades fromzero belowZ1.375 tofull by1.410','courses':COURSES,'finiteWallM':WALL,'radialLapStepM':RADIAL_LAP,'parts':parts,
 'construction':'Six short shaped metal guard courses follow a continuously interpolated cervical profile without adding height. Front free edges round downward; flank free edges sweep down/aft with14% taper and alternate staggered elevations. Their angular overlap interrupts the former straight reveal; lateral guards step out from frontal guards with5.5mm radial lap and4.5mm finite walls. The root is recessed inside the breast cavity with a finite depth underlap, and independent inner strips leave the actual frame visible rather than closing it into a tube.',
 'preserved':['52 rigid names, parents, world/local rest transforms','head geometry and rigid nodes','all meshes outside20 named cervical surfaces','all historical guide geometry','material definitions and source era eligibility','existing runtime interfaces and anatomical-left restriction'],
 'limits':['Source posterior cervical laps and load frame retained; mating and motion need renewed checks after the clay gate.','Authored profile is a construction proposal; no quantitative reference fit or engineered running-clearance claim.','Existing throat/front corner reveals are spaces between finite separate guards, not cut holes.']}
