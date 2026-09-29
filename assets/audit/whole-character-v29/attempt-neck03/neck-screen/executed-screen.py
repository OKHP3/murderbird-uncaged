"""Bounded finite-geometry screen for cervical guards; not a physics solver."""
from pathlib import Path
import argparse,sys,hashlib,json,shutil
import bpy
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--sha',required=True);p.add_argument('--output',required=True);p.add_argument('--render',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
NATIVE=Path(a.model).resolve();OUT=Path(a.output).resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(NATIVE)==a.sha;assert not OUT.exists();OUT.mkdir(parents=True);shutil.copy2(__file__,OUT/'executed-screen.py')
bpy.ops.wm.open_mainfile(filepath=str(NATIVE));bpy.context.view_layer.update()
CHAIN=['neck','cervical-mid-a','cervical-mid-b','cervical-upper'];OWNERS=CHAIN+['head','jaw'];REST={n:bpy.data.objects[n].matrix_local.copy() for n in OWNERS}
STATES=[('rest',0,0,0,0),('maker-neck-jaw',-.14,-.45,0,.32),('attention',.08,.288,.02,0),('contact-neck',.65,0,-.731,.10),('thrust-neck',-.07,0,-.035,0),('yaw-minus',0,-.45,0,0),('yaw-plus',0,.45,0,0)]
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
for n in OWNERS:bpy.data.objects[n].rotation_mode='QUATERNION'
def pose(state):
 label,q,y,h,j=state
 for i,n in enumerate(CHAIN):
  o=bpy.data.objects[n];d=Quaternion((1,0,0),q*.25)
  if i==0:d=d@Quaternion((0,0,1),y)
  o.rotation_quaternion=o.matrix_parent_inverse.to_quaternion().inverted()@REST[n].to_quaternion()@d
 for n,v in [('head',h),('jaw',j)]:
  o=bpy.data.objects[n];o.rotation_quaternion=o.matrix_parent_inverse.to_quaternion().inverted()@REST[n].to_quaternion()@Quaternion((1,0,0),v)
 bpy.context.view_layer.update()
def inside(p,tri):
 x,y,z=tri;v0=y-x;v1=z-x;v2=p-x;d00=v0.dot(v0);d01=v0.dot(v1);d11=v1.dot(v1);den=d00*d11-d01*d01
 if abs(den)<1e-18:return False
 u=(d11*v2.dot(v0)-d01*v2.dot(v1))/den;v=(d00*v2.dot(v1)-d01*v2.dot(v0))/den
 return min(u,v,1-u-v)>1e-6
def edge(p,q,tri):
 n=(tri[1]-tri[0]).cross(tri[2]-tri[0])
 if n.length<1e-12:return False
 n.normalize();d0=n.dot(p-tri[0]);d1=n.dot(q-tri[0])
 if not(d0*d1<0 and abs(d0)>1e-7 and abs(d1)>1e-7):return False
 direction=q-p;hit=intersect_ray_tri(*tri,direction,p,True)
 if hit is None:return False
 t=(hit-p).dot(direction)/max(direction.length_squared,1e-30)
 return 1e-6<t<1-1e-6 and inside(hit,tri)
def screen(state):
 pose(state);dg=bpy.context.evaluated_depsgraph_get();items=[]
 for o in bpy.data.objects:
  if o.type!='MESH' or not o.parent:continue
  guard=(o.name.startswith('V23 cervical ') and 'directional guard' in o.name) or o.name.startswith('V29 neck root recessed underlap ')
  if not guard and o.parent.name not in OWNERS+['upper-bill','cranial-cover','builder-optics','body','breastplate']:continue
  if 'builder' not in o.get('exteriorEras','maker,mechanic,builder').split(','):continue
  ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@x.co for x in m.vertices];tri=[tuple(f.vertices) for f in m.loop_triangles];ev.to_mesh_clear()
  if not v:continue
  bounds=[[min(pt[k] for pt in v) for k in range(3)],[max(pt[k] for pt in v) for k in range(3)]]
  items.append((o.name,o.parent.name,guard,v,tri,bounds,BVHTree.FromPolygons(v,tri,all_triangles=True)))
 assert sum(x[2] for x in items) in (40,50)
 pairs=[]
 for i,x in enumerate(items):
  for y in items[i+1:]:
   if x[1]==y[1] or not(x[2] or y[2]) or any(x[5][1][k]<y[5][0][k] or y[5][1][k]<x[5][0][k] for k in range(3)):continue
   for ix,iy in x[6].overlap(y[6]):
    tx=[x[3][j] for j in x[4][ix]];ty=[y[3][j] for j in y[4][iy]]
    if any(edge(tx[k],tx[(k+1)%3],ty) or edge(ty[k],ty[(k+1)%3],tx) for k in range(3)):
     pairs.append({'a':x[0],'b':y[0],'owners':[x[1],y[1]],'firstTrianglePair':[ix,iy],'witnessTriangles':[[list(v) for v in tx],[list(v) for v in ty]]});break
 return {'pose':state[0],'angles':list(state[1:]),'screenedGuards':sum(x[2] for x in items),'pairCount':len(pairs),'pairs':pairs}
result={'nativeSHA256':a.sha,'sourceSHA256':sha(Path(__file__)),'method':'Evaluated finite triangles; strict edge through face, 1e-7m plane epsilon and1e-6 barycentric/edge margin. All40 cervical plates plus10 root underlaps when present vs other adjacent assembly owners; first witness per pair. Same-owner contacts excluded. Discrete kinematic poses only.','poses':[]}
for state in STATES:
 result['poses'].append(screen(state));(OUT/'screen.json').write_text(json.dumps(result,indent=2)+'\n');print(state[0],result['poses'][-1]['pairCount'],flush=True)
if a.render:
 scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14)
 scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 data=bpy.data.cameras.new('Screen neutral camera');data.type='ORTHO';data.ortho_scale=1.3;cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);scene.camera=cam
 cam.location=(-6,-3.5,2.45);cam.rotation_euler=(Vector((0,-.27,1.48))-cam.location).to_track_quat('-Z','Y').to_euler()
 for state in [STATES[i] for i in (0,1,3)]:
  pose(state);scene.render.filepath=str(OUT/(state[0]+'.png'));bpy.ops.render.render(write_still=True)
assert sha(NATIVE)==a.sha
