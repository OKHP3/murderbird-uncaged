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
 if z<=PROFILE[0][0]:return PROFILE[0][k]
 if z>=PROFILE[-1][0]:return PROFILE[-1][k]
 for a,b in zip(PROFILE,PROFILE[1:]):
  if a[0]<=z<=b[0]:
   t=(z-a[0])/(b[0]-a[0]);return a[k]*(1-t)+b[k]*t

def point(z,angle,radial):
 front,rear,width=[sample(z,k) for k in (1,2,3)]
 cy=(front+rear)/2;depth=(rear-front)/2
 return Vector(((width+radial)*math.sin(angle),cy-(depth+radial)*math.cos(angle),z))

def install(obj,patches,wall):
 """Install separate open curved patches, each with a finite returned wall modifier."""
 inv=obj.matrix_world.inverted();verts=[];faces=[];rows=20;cols=16
 for top,bottom,center,half,radial in patches:
  base=len(verts)
  for j in range(rows+1):
   t=j/rows
   for k in range(cols+1):
    u=2*k/cols-1
    # A shallow formed lower arch retains separate course edges without pointed skirts.
    z=top+(bottom-top)*t-.0015*(1-u*u)*ease(t)
    verts.append(inv@point(z,center+half*u,radial))
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
  parts.append(install(obj,[(top,bottom,0,.64,off)],WALL));names.append(name)
  for side in (-1,1):
   name=f'Cervical flank lamina {side} {n}';obj=bpy.data.objects[name]
   parts.append(install(obj,[(top,bottom,side*1.22,.43,off)],WALL));names.append(name)
 # Separate backing strips guard the real lateral frame; neither closes the cervical tube.
 name='Lower cervical open backing';obj=bpy.data.objects[name]
 parts.append(install(obj,[(1.460,1.260,side*1.03,.16,-.010) for side in (-1,1)],.0035));names.append(name)
 name='Cervical articulated inner guards';obj=bpy.data.objects[name]
 parts.append(install(obj,[(1.595,1.410,side*.86,.12,-.014) for side in (-1,1)],.0035));names.append(name)
 bpy.context.view_layer.update()
 return {'status':'V20 local cervical construction study; no whole-silhouette, motion or engineering acceptance','changed':sorted(names),'added':[],'removed':[],
 'profile':PROFILE,'courses':COURSES,'finiteWallM':WALL,'radialLapStepM':RADIAL_LAP,'parts':parts,
 'construction':'Six short curved courses replace each front/lateral skirt sequence. Lower course extends into breast cavity as a finite underlap; consecutive courses overlap vertically and step outward5.5mm with4.5mm walls. Independent lateral backing strips retain deliberate front/side frame reveals instead of closing the neck into a smooth monolithic tube.',
 'preserved':['52 rigid names, parents, world/local rest transforms','head geometry and rigid nodes','all meshes outside20 named cervical surfaces','all historical guide geometry','material definitions and source era eligibility','existing runtime interfaces and anatomical-left restriction'],
 'limits':['Source posterior cervical laps and load frame retained; mating and motion need renewed checks after the clay gate.','Authored profile is a construction proposal; no quantitative reference fit or engineered running-clearance claim.','Existing throat/front corner reveals are spaces between finite separate guards, not cut holes.']}
