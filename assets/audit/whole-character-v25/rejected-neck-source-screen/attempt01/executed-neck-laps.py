"""V25 short terminal neck receivers, retaining four rigid S-shaped cores.

Native X is the hinge axis; the root front receiver is spherical for root yaw.
This is a bounded construction proposal. Parameters specify authored clearances,
not a claim of continuous clearance or dimensions recovered from reference art.
"""
import bpy,bmesh,math,json
from mathutils import Vector
PROFILE=((.78,-.165,.125,.170),(.87,-.247,.139,.210),(.99,-.365,.128,.252),(1.12,-.425,.095,.280),(1.245,-.417,.038,.258),(1.335,-.382,-.035,.205),(1.410,-.352,-.106,.145),(1.48,-.379,-.160,.116),(1.555,-.428,-.213,.109),(1.635,-.446,-.256,.100))
JOINTS=(('neck',(0,-.188,1.335)),('cervical-mid-a',(0,-.229,1.410)),('cervical-mid-b',(0,-.270,1.480)),('cervical-upper',(0,-.321,1.550)))
SECTORS=((-1.22,-.74),(-.72,-.25),(-.23,.23),(.25,.72),(.74,1.22),(1.245,1.82),(1.84,2.45),(-2.45,-1.84),(-1.82,-1.245),(2.47,math.tau-2.47))
GUARDS=[f'V23 cervical {i+1} directional guard {k+1}' for i in range(4) for k in range(10)]
BREAST=['V24 continuous recessed breast backing']+[f'V24 breast course 01 panel {i:02}' for i in range(1,7)]
WALL=.0035;RUNNING_GAP=.005;RADIAL_STEP=WALL+RUNNING_GAP
INNER=-.00325;OUTER=INNER+RADIAL_STEP
ROOT_OUTER=.209;ROOT_INNER=ROOT_OUTER-RADIAL_STEP

def smooth(t):t=max(0.,min(1.,t));return t*t*(3-2*t)
def sample(z,k):
 x=[r[0] for r in PROFILE];y=[r[k] for r in PROFILE]
 if z<=x[0]:return y[0]
 if z>=x[-1]:return y[-1]
 h=[b-a for a,b in zip(x,x[1:])];d=[(b-a)/hh for a,b,hh in zip(y,y[1:],h)];m=[d[0]]
 for i in range(1,len(x)-1):
  if d[i-1]*d[i]<=0:m.append(0.)
  else:
   w1=2*h[i]+h[i-1];w2=h[i]+2*h[i-1];m.append((w1+w2)/(w1/d[i-1]+w2/d[i]))
 m.append(d[-1])
 for i in range(len(x)-1):
  if x[i]<=z<=x[i+1]:
   t=(z-x[i])/h[i];return (2*t**3-3*t*t+1)*y[i]+(t**3-2*t*t+t)*h[i]*m[i]+(-2*t**3+3*t*t)*y[i+1]+(t**3-t*t)*h[i]*m[i+1]
def point(z,angle,off):
 f,r,w=[sample(z,k) for k in (1,2,3)];return Vector(((w+off)*math.sin(angle),(f+r)/2-((r-f)/2+off)*math.cos(angle),z))
def properties(o):return json.dumps(dict(o.items()),default=lambda x:list(x),sort_keys=True)
def snap(o):return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(f.vertices) for f in o.data.polygons),tuple(m.name if m else None for m in o.data.materials),properties(o),o.hide_render,o.hide_viewport)
def node(o):return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),properties(o))
def cylinder(p,angle,axis,ref_off,delta):
 # Constant yz-radius for each X-section of this partial receiver. Near the
 # axis the free edge withdraws into an explicit transverse service window.
 f,r,w=[sample(axis.z,k) for k in (1,2,3)];xr=(w+ref_off)*math.sin(angle);dy=(f+r)/2-((r-f)/2+ref_off)*math.cos(angle)-axis.y;R=abs(dy)+delta
 if R<.027:return p
 z=p.z-axis.z
 if abs(z)>=R*.95:return p
 return Vector((xr,axis.y+math.copysign(math.sqrt(max(0,R*R-z*z)),dy),p.z))
def apply():
 bpy.context.view_layer.update()
 for n,p in JOINTS:assert (bpy.data.objects[n].matrix_world.translation-Vector(p)).length<1e-6,n
 for i in range(4):
  for k in range(10):
   o=bpy.data.objects[GUARDS[i*10+k]];assert o.parent.name==JOINTS[i][0] and len(o.data.vertices)==825,o.name
   assert abs(o.modifiers[0].thickness-WALL)<1e-7
 for n in BREAST:assert bpy.data.objects[n].parent.name=='breastplate'
 changed=GUARDS+BREAST;protected={o.name:snap(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in changed};nodes={o.name:node(o) for o in bpy.data.objects if o.type=='EMPTY'}
 witnesses=[];changed_bounds=[]
 for i in range(4):
  root=Vector(JOINTS[i][1]);distal=Vector(JOINTS[i+1][1]) if i<3 else bpy.data.objects['head'].matrix_world.translation.copy();off=.005+i*.002
  for k,(a,b) in enumerate(SECTORS):
   name=GUARDS[i*10+k];o=bpy.data.objects[name];old=[o.matrix_world@v.co for v in o.data.vertices];inv=o.matrix_world.inverted();new=[];unchanged=0
   for j in range(33):
    for c in range(25):
     idx=j*25+c;p=old[idx];u=2*c/24-1
     # Recover actual authored angular coordinate, including tangent seam inset.
     f,r,w=[sample(p.z,key) for key in (1,2,3)];ang=math.atan2(p.x/(w+off),-(p.y-(f+r)/2)/((r-f)/2+off))
     dy0=point(root.z,ang,max(.005,off-.002)).y-root.y;dy1=point(distal.z,ang,off).y-distal.y
     service0=smooth((.038-abs(dy0))/.012);service1=smooth((.038-abs(dy1))/.012)
     bottom=root.z-.006-.003*(1-u*u)**2-.0015*math.sin((a+b)/2)*u
     top=distal.z+.006+.0015*math.sin((a+b)/2)*u
     if i==0 and k>=5:bottom=root.z+.010 # rear/side root service seat, no spherical cuff
     bottom=bottom*(1-service0)+(root.z+.015)*service0
     top=top*(1-service1)+(distal.z-.015)*service1
     oldbottom=old[32*25+c].z;oldtop=old[c].z;z=p.z
     if z<root.z+.025:z+=(bottom-oldbottom)*smooth((root.z+.025-z)/(root.z+.025-oldbottom))
     if z>distal.z-.025:z+=(top-oldtop)*smooth((z-(distal.z-.025))/(oldtop-(distal.z-.025)))
     q=point(z,ang,off)
     wr=1-smooth((z-(root.z+.007))/.018);wt=smooth((z-(distal.z-.025))/.018)
     if i==0 and k<5:
      target=root+(q-root).normalized()*ROOT_OUTER
      q=q.lerp(target,wr)
     elif i>0:
      q=q.lerp(cylinder(q,ang,root,off-.002,OUTER),wr*(1-service0))
     q=q.lerp(cylinder(q,ang,distal,off,INNER),wt*(1-service1))
     if root.z+.025<=p.z<=distal.z-.025:q=p.copy();unchanged+=1
     new.append(q)
   o.data=o.data.copy();o.data.name=name+' short V25 receivers'
   for v,p in zip(o.data.vertices,new):v.co=inv@p
   o.data.update();bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
   # Keep the original outward row order after re-forming terminal strips.
   normal=o.matrix_world.to_3x3().inverted().transposed()@o.data.polygons[16*24+12].normal;mid=new[16*25+12];cy=(sample(mid.z,1)+sample(mid.z,2))/2
   if normal.dot(Vector((mid.x,mid.y-cy,0)))<0:
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
   witnesses.append({'name':name,'owner':o.parent.name,'rawCoreVerticesExactlyRetained':unchanged,'maximumPointDisplacementM':max((p-q).length for p,q in zip(old,new)),'rootAxis':list(root),'distalAxis':list(distal)})
 # Local upper breast receiving seat. All points below1.260 stay exact; the
 # upper lip is lowered to a short overlap and its radial seat is concentric
 # with root yaw/pitch. It remains part of the existing moving breast door.
 root=Vector(JOINTS[0][1])
 for n in BREAST:
  o=bpy.data.objects[n];inv=o.matrix_world.inverted();old=[o.matrix_world@v.co for v in o.data.vertices];o.data=o.data.copy();o.data.name=n+' V25 spherical root mating lip'
  maximum=0
  for v,p in zip(o.data.vertices,old):
   weight=smooth((p.z-1.260)/.030);q=p.copy()
   if weight:
    q.z=min(q.z,root.z+.009);q=root+(q-root).normalized()*ROOT_INNER;q=p.lerp(q,weight)
   v.co=inv@q;maximum=max(maximum,(p-q).length)
  o.data.update();witnesses.append({'name':n,'owner':'breastplate','localReceivingSeatBelowNativeZ':1.354,'unchangedAtOrBelowNativeZ':1.260,'maximumPointDisplacementM':maximum})
 bpy.context.view_layer.update()
 assert nodes=={o.name:node(o) for o in bpy.data.objects if o.type=='EMPTY'}
 assert protected=={n:snap(bpy.data.objects[n]) for n in protected}
 return {'region':'neck-short-laps','status':'finite rigid joint-receiver proposal; awaiting discrete pose and visual screen','changedMeshes':changed,'changedNodes':[],'added':[],'removed':[],'nodesExact':len(nodes),'otherMeshSnapshotsExact':len(protected),'materialDefinitionsChanged':False,'eraTagsChanged':False,'witnesses':witnesses,'contract':{'skinWallM':WALL,'runningRadialGapTargetM':RUNNING_GAP,'outerToInnerSurfaceStepM':RADIAL_STEP,'innerTerminalRadialChangeM':INNER,'outerTerminalRadialChangeM':OUTER,'lapApproximateLengthM':[.012,.018],'rootFrontSphereOuterRadiusM':ROOT_OUTER,'rootBreastReceiverRadiusM':ROOT_INNER,'terminalFadeEndsWithinM':.025,'corePointsOutsideTerminalZoneExact':True,'axisSideServiceWindowRadiusThresholdM':[.026,.038],'runtimeChanges':False},'limits':['5mm is authored concentric radial spacing after3.5mm wall allowance, not a continuous-clearance certificate.','Terminal/core blend and side-window corners require actual evaluated pose checks.','Enlarged cranial inner shell is protected; inherited adjacent neck/head conflicts may remain.','Root breast receiving lip stays breastplate-owned; opening motion requires separate review.']}
