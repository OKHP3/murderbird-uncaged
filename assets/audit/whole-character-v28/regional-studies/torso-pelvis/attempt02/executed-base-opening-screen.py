from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Quaternion
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree
OUT=Path('/tmp/v28-torso-pelvis/attempt02');NATIVE=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/models/whole-character-v27/attempt-form01/murderbird-whole-character-v27.blend');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();r=json.loads((OUT/'receipt.json').read_text());bound=sha(NATIVE);assert bound==r['baseSHA256'];bpy.ops.wm.open_mainfile(filepath=str(NATIVE));bpy.context.view_layer.update()
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
def inside(p,tri):
 a,b,c=tri;v0=b-a;v1=c-a;v2=p-a;d00=v0.dot(v0);d01=v0.dot(v1);d11=v1.dot(v1);d20=v2.dot(v0);d21=v2.dot(v1);den=d00*d11-d01*d01
 if abs(den)<1e-18:return False
 u=(d11*d20-d01*d21)/den;v=(d00*d21-d01*d20)/den;return min(u,v,1-u-v)>1e-6
def edge(p,q,tri):
 n=(tri[1]-tri[0]).cross(tri[2]-tri[0])
 if n.length<1e-12:return False
 n.normalize();d0=n.dot(p-tri[0]);d1=n.dot(q-tri[0])
 if not(d0*d1<0 and abs(d0)>1e-7 and abs(d1)>1e-7):return False
 direction=q-p;hit=intersect_ray_tri(*tri,direction,p,True)
 if hit is None:return False
 t=(hit-p).dot(direction)/max(direction.length_squared,1e-30);return 1e-6<t<1-1e-6 and inside(hit,tri)
def mesh(o,dg):
 ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@x.co for x in m.vertices];t=[tuple(f.vertices) for f in m.loop_triangles];ev.to_mesh_clear();return (o.name,v,t,BVHTree.FromPolygons(v,t,all_triangles=True))


rest={o.name:(o.location.copy(),o.rotation_mode,o.rotation_quaternion.copy(),o.rotation_euler.copy(),o.matrix_world.copy()) for o in bpy.data.objects if o.type=='EMPTY'}
legposes=json.loads(Path('/tmp/v28-torso-pelvis/leg-studies.json').read_text())['states']
def pose(label,angle=0):
 for n,(p,m,q,e,w) in rest.items():
  o=bpy.data.objects[n];o.location=p;o.rotation_mode=m;o.rotation_quaternion=q;o.rotation_euler=e
 if label=='opening':bpy.data.objects['breastplate'].rotation_euler.x=angle
 elif label in legposes:
  state=legposes[label];dz=state['bodyDeltaNative'][2];bpy.data.objects['body'].location.z+=dz
  for side,lp in state['legs'].items():
   hip=bpy.data.objects[side+'-thigh'];knee=bpy.data.objects[side+'-shin'];hip.location.z+=dz
   for o,key in [(hip,'hipQuaternionNative'),(knee,'kneeQuaternionNative')]:
    x,y,z,w=lp[key];o.rotation_mode='QUATERNION';o.rotation_quaternion=Quaternion((w,x,y,z))
 elif label.startswith('hip-yaw'):
  for side in ['left','right']:bpy.data.objects[side+'-thigh'].rotation_euler.z=angle
 elif label.startswith('hip-roll'):
  for side in ['left','right']:bpy.data.objects[side+'-thigh'].rotation_euler.y=angle
 bpy.context.view_layer.update()
 if label in legposes:
  for side in legposes[label]['legs']:
   f=bpy.data.objects[side+'-foot'];f.rotation_mode='QUATERNION';f.rotation_quaternion=f.parent.matrix_world.to_quaternion().inverted()@rest[f.name][4].to_quaternion()
 bpy.context.view_layer.update()
changed=set()
# Two screens: fixed new structure vs leg-root linkage in rest/IK/multiaxis,
# new thigh structure vs adjacent fixed body/shin/wing surfaces,
# and the complete door vs fixed torso/neck/wing roots in five opening states.
poses=[]
for label,angle in [('opening',a) for a in [0,.275,.55,.825,1.1]]:
 pose(label,angle);dg=bpy.context.evaluated_depsgraph_get()
 if label=='opening':
  sources=[o for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name=='breastplate']
  targets=[o for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name in ['body','neck','cervical-mid-a','cervical-mid-b','cervical-upper','left-mantle','right-mantle','left-wing-shield','right-wing-shield','left-thigh','right-thigh']]
 else:
  sources=[bpy.data.objects[n] for n in changed if bpy.data.objects[n].parent.name in ['body','left-thigh','right-thigh']]
  targets=[o for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name in ['body','left-thigh','right-thigh','left-shin','right-shin','left-mantle','right-mantle','left-wing-shield','right-wing-shield']]
 items={o.name:mesh(o,dg) for o in sources+targets};pairs=[]
 for oa in sorted(sources,key=lambda o:o.name):
  a=items[oa.name]
  for ob in sorted(targets,key=lambda o:o.name):
   
   if oa.parent==ob.parent:continue
   b=items[ob.name];strict=[]
   for ia,ib in a[3].overlap(b[3]):
    A=[a[1][i] for i in a[2][ia]];B=[b[1][i] for i in b[2][ib]]
    if any(edge(A[k],A[(k+1)%3],B) or edge(B[k],B[(k+1)%3],A) for k in range(3)):strict.append((ia,ib))
   if strict:
    ia,ib=strict[0];w=sum([a[1][i] for i in a[2][ia]]+[b[1][i] for i in b[2][ib]],Vector())/6
    pairs.append({'source':a[0],'neighbor':b[0],'owners':[oa.parent.name,ob.parent.name],'trianglePairs':len(strict),'firstTrianglePair':list(strict[0]),'firstPairCentroidNative':list(w)})
 poses.append({'pose':label,'angleNative':angle,'sources':len(sources),'targets':len(targets),'strictPairCount':len(pairs),'pairs':pairs});print(label,angle,len(pairs),flush=True)
out={'nativeSHA256':bound,'sourceSHA256':r['sourceSHA256'],'screenSHA256':sha(Path(__file__)),'method':'Evaluated edge-through-triangle strict interior crossings; plane epsilon1e-7m and barycentric1e-6. Triangle pair counts are not penetration depth. Seven rest/illustrative IK/multiaxis leg samples and five breast opening samples only; no continuous clearance or engineering validation. Named fixed hip seat mating/support interfaces have not been blanket excluded.','poses':poses}
(OUT/'base-opening-screen.json').write_text(json.dumps(out,indent=2)+'\n');assert sha(NATIVE)==bound
