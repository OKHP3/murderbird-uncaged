"""Authored whole-body cage: curved neck, compact mantle and substantial support.
Native metres/Z-up/-Y-front. Shape choices are proposals, not reference measurements.
"""
import json,math
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix
ROOT=Path(globals().get('SOURCE_ROOT',Path(__file__).resolve().parents[2]))
INV=json.loads((ROOT/'assets/audit/whole-character-v20/input/inventory.json').read_text())
OLD={n['name']:Matrix(n['world']) for n in INV['nodes']}
PARENT={n['name']:n['parent'] for n in INV['nodes']}
HEAD_DELTA=Vector((0,-.055,.100))
BODY_Z={'center':.95,'scale':.88,'rise':.105,'anteriorShoulderRise':.025,'frontDepthScale':1.10,'rearDepthScale':.94}
NECK_CAGE=((1.16,.030,-.045,1.04),(1.25,.055,-.050,1.03),(1.35,.080,-.055,1.02),(1.405,.100,-.055,1.00),(1.60,.100,-.055,1.00))
BODY_WIDTH=((.60,.88),(.75,1.08),(.85,1.02),(1.05,1.00),(1.20,1.00),(1.34,.98))
LEG_JOINTS={'hipZ':.875,'kneeZ':.555,'ankleZ':.330,'toeZ':.0726206973195076,'stanceHalfWidth':.305}
MANTLE={'raise':.060,'zScale':.94,'depthScale':1.00,'foreShift':-.005,'radialMass':1.12,'distalWidthTaper':.14}

def smooth(t):t=max(0.,min(1.,t));return t*t*(3-2*t)
def sample(rows,z,k):
 if z<=rows[0][0]:return rows[0][k]
 if z>=rows[-1][0]:return rows[-1][k]
 for a,b in zip(rows,rows[1:]):
  if a[0]<=z<=b[0]:
   t=smooth((z-a[0])/(b[0]-a[0]));return a[k]*(1-t)+b[k]*t

def body_point(p):
 p=Vector(p);q=p.copy();front=smooth((.10-p.y)/.34)
 q.x*=sample(BODY_WIDTH,p.z,1)
 q.y=.02+(p.y-.02)*(BODY_Z['frontDepthScale'] if p.y<.02 else BODY_Z['rearDepthScale'])
 q.z=.95+(p.z-.95)*BODY_Z['scale']+BODY_Z['rise']
 # The narrowed anterior shoulder rises into the broadened neck root.
 q.z+=BODY_Z['anteriorShoulderRise']*smooth((p.z-1.13)/.19)*front*(1-smooth(abs(p.x)/.36))
 return q

def neck_point(p):
 p=Vector(p);q=p.copy();q.x*=sample(NECK_CAGE,p.z,3)
 q.y+=sample(NECK_CAGE,p.z,2);q.z+=sample(NECK_CAGE,p.z,1)
 return q

def mantle_point(owner,p):
 p=Vector(p);side=1 if owner.startswith('left') else -1
 # One authored mantle map, not a second compression of already-compressed body.
 q=p.copy();q.y=.07+(p.y-.07)*MANTLE['depthScale']+MANTLE['foreShift']
 q.z=1.18+(p.z-1.18)*MANTLE['zScale']+MANTLE['raise']
 oldcenter=OLD['left-mantle' if side>0 else 'right-mantle'].translation.x
 newcenter=oldcenter*1.06
 q.x=newcenter+(p.x-oldcenter)*MANTLE['radialMass']
 return q

def foot_z(z):
 return sample(((-.023,0.),(.009,.009),(.073,.095),(.306,.330)),z,1)
def side_of(owner):return 1 if owner.startswith('left') else -1
def leg_nodes(side):
 label='left' if side>0 else 'right';hip=OLD[label+'-thigh'].translation.copy();knee=OLD[label+'-shin'].translation.copy();ankle=OLD[label+'-foot'].translation.copy();toe=OLD[label+'-toes'].translation.copy()
 newhip=Vector((side*.275,.055,.875));newknee=Vector((side*.305,-.080,.555));newankle=Vector((side*.305,.038,.330));newtoe=Vector((side*.305, toe.y, toe.z))
 return (hip,knee,ankle,toe),(newhip,newknee,newankle,newtoe)

def segment_point(p,a,b,c,d,radial):
 v=b-a;t=(p-a).dot(v)/v.length_squared
 axis=a+v*t;newaxis=c+(d-c)*t
 olddir=v.normalized();newdir=(d-c).normalized();rot=olddir.rotation_difference(newdir)
 return newaxis+rot@(p-axis)*radial

def leg_point(owner,p):
 p=Vector(p);side=side_of(owner);old,new=leg_nodes(side)
 if 'thigh' in owner or 'hip-landmark' in owner:return segment_point(p,old[0],old[1],new[0],new[1],1.32)
 if 'shin' in owner or 'knee-landmark' in owner:return segment_point(p,old[1],old[2],new[1],new[2],1.35)
 if 'foot' in owner or 'sole-landmark' in owner:
  q=segment_point(p,old[2],old[3],new[2],new[3],1.30)
  # The proximal foot thickens around its link axis, but its plantar section
  # retains source Z curvature. A local fade affects this owner only, never claws.
  q.z=p.z+(q.z-p.z)*smooth((p.z-.025)/.18)
  return q
 # All toe, phalanx and claw geometry is rigidly translated as one planted cluster.
 # No per-height remap or root splay distorts its curved talon profile.
 center=old[3];newcenter=new[3];q=p+(newcenter-center)
 return q

def is_head(owner):
 while owner:
  if owner=='head':return True
  owner=PARENT.get(owner)
 return False

def map_point(owner,old_native_world_point):
 """Public old-world -> proposed new-world mapping for frame/socket derivation."""
 p=Vector(old_native_world_point)
 if is_head(owner):return p+HEAD_DELTA
 if owner in ('neck','cervical-upper'):return neck_point(p)
 if 'mantle' in owner or 'wing-shield' in owner:return mantle_point(owner,p)
 if owner.startswith(('left-','right-')) and any(k in owner for k in ('thigh','shin','foot','toes','digit','hip-landmark','knee-landmark','sole-landmark')):return leg_point(owner,p)
 if owner=='industrial-repairs':return mantle_point('left-mantle',p)
 if owner=='murderbird':return p
 if owner.startswith('anchor'):
  return map_point(PARENT.get(owner,'body'),p)
 return body_point(p)

def depth(owner):
 n=0
 while PARENT.get(owner):n+=1;owner=PARENT[owner]
 return n

def bearing_map(obj,points):
 owner=obj.parent.name
 if is_head(owner):return [map_point(owner,p) for p in points]
 center=sum(points,Vector())/len(points);newcenter=map_point(owner,center)
 factor=1.26 if 'mantle' in owner or 'wing' in owner else 1.32
 if owner in ('body','breastplate','neck','cervical-upper'):return [map_point(owner,p) for p in points]
 # Joint axes are native X: grow Y/Z radii equally, keeping journals circular.
 return [newcenter+Vector(((p.x-center.x)*1.20,(p.y-center.y)*factor,(p.z-center.z)*factor)) for p in points]

def fan_vertices(obj,points):
 if 'distal mantle plume' not in obj.name or len(points)!=195:return [map_point(obj.parent.name,p) for p in points]
 out=[]
 for row in range(15):
  group=points[row*13:(row+1)*13];center=sum(group,Vector())/13;t=row/14
  # Root attachment stays broad; a directional separated guard tapers and sweeps back.
  width=1-MANTLE['distalWidthTaper']*smooth((t-.15)/.75)
  for p in group:
   q=center+(p-center)*width;q.y+=.015*smooth(t)
   q=map_point(obj.parent.name,q);q.x+=(1 if obj.parent.name.startswith('left') else -1)*.010*math.sin(math.pi*t)
   out.append(q)
 return out

def add_cage_guides(body):
 rows=[(z,0,y) for z,_,y,_ in NECK_CAGE]
 curve=bpy.data.curves.new('V20 authored neck control meridian','CURVE');curve.dimensions='3D';spl=curve.splines.new('POLY');spl.points.add(len(rows)-1)
 for v,(z,x,dy) in zip(spl.points,rows):v.co=(*neck_point(Vector((x,-.300,z))),1)
 obj=bpy.data.objects.new(curve.name,curve);bpy.context.scene.collection.objects.link(obj);obj.parent=body;obj.matrix_parent_inverse=body.matrix_world.inverted();obj['authoringRole']='V20 cage control meridian; authored source tables drive baked rigid derivative';obj['region']='neck';obj['surfaceRole']='authoring-control';obj['exteriorEras']='maker,mechanic,builder'
 return obj.name

def apply():
 oldmesh={o.name:([o.matrix_world@v.co for v in o.data.vertices],o.matrix_world.copy()) for o in bpy.data.objects if o.type=='MESH'}
 oldcurve={o.name:o.matrix_world.copy() for o in bpy.data.objects if o.type=='CURVE'}
 newnodes={}
 for name,old in OLD.items():
  new=old.copy();new.translation=map_point(name,old.translation);newnodes[name]=new
 # Preserve rigid orientation bases, names and parents. New geometry is baked around new pivots.
 for name in sorted(OLD,key=depth):bpy.data.objects[name].matrix_world=newnodes[name]
 bpy.context.view_layer.update();changed=[]
 for name,(points,world) in oldmesh.items():
  obj=bpy.data.objects[name];owner=obj.parent.name if obj.parent else 'murderbird'
  if obj.get('surfaceRole')=='bearing':mapped=bearing_map(obj,points)
  elif 'distal mantle plume' in name:mapped=fan_vertices(obj,points)
  else:mapped=[map_point(owner,p) for p in points]
  inv=obj.matrix_world.inverted()
  for v,p in zip(obj.data.vertices,mapped):v.co=inv@p
  obj.data.update();changed.append(name)
 for name,world in oldcurve.items():
  obj=bpy.data.objects[name];owner=obj.parent.name if obj.parent else 'murderbird';inv=obj.matrix_world.inverted()
  for spl in obj.data.splines:
   if spl.type=='BEZIER':
    for v in spl.bezier_points:
     v.co=inv@map_point(owner,world@v.co);v.handle_left=inv@map_point(owner,world@v.handle_left);v.handle_right=inv@map_point(owner,world@v.handle_right)
   else:
    for v in spl.points:v.co=(*(inv@map_point(owner,world@Vector(v.co[:3]))),v.co[3])
 body=bpy.data.objects['body'];controls={'bodyZ':BODY_Z,'bodyWidth':BODY_WIDTH,'neck':NECK_CAGE,'headDelta':list(HEAD_DELTA),'mantle':MANTLE,'legJoints':LEG_JOINTS}
 body['proportionCageV20']=json.dumps(controls,separators=(',',':'));guide=add_cage_guides(body)
 bpy.context.view_layer.update()
 contract={name:{'parent':PARENT[name],'oldWorld':[list(r) for r in OLD[name]],'newWorld':[list(r) for r in bpy.data.objects[name].matrix_world],'oldLocal':[list(r) for r in (OLD[PARENT[name]].inverted()@OLD[name] if PARENT[name] else OLD[name])],'newLocal':[list(r) for r in bpy.data.objects[name].matrix_local]} for name in OLD}
 return {'status':'early whole-body authored cage candidate; visual, attachment, motion and likeness review pending','changed':changed,'added':[],'removed':[],'addedAuthoringGuide':guide,'controls':controls,'rigContract':contract,'mappingAPI':'map_point(owner, old_native_world_point); native metres/Zup/-Yfront; old matrices from pinned inventory','construction':'Raised substantial breast retains anterior depth and shoulder width; gently swept neck cage seats nested finite source guard courses into breast rather than stretching their root into a tube; head identity rises 100 mm and moves forward 55 mm. Independent full-area mantle mapping retains fan area while tapering distal guard courses; strengthened circular journals and leg roots. Toe/phalanx/claw cluster is rigidly translated with exact world-space curvature. All prior source parts/eras retained.','limits':['Proposed authored shape relationships; no measured reference reconstruction.','Broad cage repositions all frame and exterior parts; regional attachment and finite-wall integrity need renewed checking.','Circular radial bearing growth is explicit; other source plate thickness modifiers remain inherited.','No export or runtime clearance acceptance.']}
