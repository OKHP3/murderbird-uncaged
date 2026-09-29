from pathlib import Path
import bpy,bmesh,json,hashlib,math
from mathutils import Vector
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
OUT=Path(__file__).parent
NATIVE=ROOT/'assets/models/whole-character-v33/attempt-form01/murderbird-whole-character-v33.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
BOUND='122076fb0faa92a78d800c6a97e1d8fcad9d3dd19f9a97693bdb26861a2df850'
assert sha(NATIVE)==BOUND
bpy.ops.wm.open_mainfile(filepath=str(NATIVE));bpy.context.view_layer.update()
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
rest={n:bpy.data.objects[n].matrix_basis.copy() for n in ('jaw','cranial-cover')}
def pose(jaw=0,cap=0):
 for n,m in rest.items():bpy.data.objects[n].matrix_basis=m
 bpy.data.objects['jaw'].rotation_euler.x+=jaw
 bpy.data.objects['cranial-cover'].location.z+=cap
 bpy.context.view_layer.update()
scene=bpy.context.scene
for o in bpy.data.objects:
 if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
 elif o.type=='CURVE':o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14)
scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
d=bpy.data.cameras.new('V33 temporary matched head camera');d.type='ORTHO';cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam
views=json.loads((OUT/'executed-v31-camera-input.json').read_text())['views'];rendered=[]
for v in views:
 if v['name']=='whole':continue
 pose(v['jawNativeX'],v['capNativeZ']);c=v['camera'];cam.location=c['position'];cam.rotation_euler=(Vector(c['target'])-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=c['orthoScale'];scene.render.filepath=str(OUT/(v['name']+'.png'));bpy.ops.render.render(write_still=True)
 rendered.append({**v,'sha256':sha(Path(scene.render.filepath))})
print('MATCHED VIEWS COMPLETE',flush=True)
(OUT/'render-receipt.json').write_text(json.dumps({'nativeSHA256':BOUND,'sourceSHA256':sha(Path(__file__)),'cameraInputSHA256':sha(OUT/'executed-v31-camera-input.json'),'views':rendered,'nativeUnchanged':sha(NATIVE)==BOUND},indent=2)+'\n')
s=(OUT/'executed-strict-kernel.py').read_text();exec(s[s.index('def inside'):s.index('poses=[]')])
def headmesh(o):
 p=o.parent
 while p:
  if p.name=='head':return True
  p=p.parent
 return False
os=[o for o in bpy.data.objects if o.type=='MESH' and o.parent and headmesh(o)];owners={o.name:o.parent.name for o in os};rows=[]
for kind,delta in [('jaw',0),('jaw',.08),('jaw',.16),('jaw',.24),('jaw',.32),('cap',0),('cap',.08)]:
 pose(delta if kind=='jaw' else 0,delta if kind=='cap' else 0);dg=bpy.context.evaluated_depsgraph_get();items=[mesh(o,dg) for o in os];active={o.name for o in os if o.parent.name==('jaw' if kind=='jaw' else 'cranial-cover')};pairs=[]
 for a in items:
  if a[0] not in active:continue
  for b in items:
   if b[0] in active or owners[a[0]]==owners[b[0]]:continue
   hits=0;first=None
   for ia,ib in a[3].overlap(b[3]):
    A=[a[1][i] for i in a[2][ia]];B=[b[1][i] for i in b[2][ib]]
    if any(edge(A[k],A[(k+1)%3],B) or edge(B[k],B[(k+1)%3],A) for k in range(3)):
     hits+=1
     if first is None:first={'indices':[ia,ib],'activeTriangle':[list(x) for x in A],'neighborTriangle':[list(x) for x in B],'centroid':list(sum(A+B,Vector())/6)}
   if hits:pairs.append({'active':a[0],'neighbor':b[0],'owners':[owners[a[0]],owners[b[0]]],'strictTrianglePairs':hits,'firstWitness':first})
  
 rows.append({'pose':kind,'delta':delta,'strictPairCount':len(pairs),'pairs':pairs});print(kind,delta,len(pairs),flush=True)
 (OUT/'screen.json').write_text(json.dumps({'nativeSHA256':BOUND,'executedScreenSHA256':sha(Path(__file__)),'kernelSHA256':sha(OUT/'executed-strict-kernel.py'),'allHeadMeshes':len(os),'meshNames':sorted(owners),'method':'V33 dynamic head-subtree meshes; active jaw/cap vs every other head-subtree rigid owner. Evaluated BVH strict edge-through-face crossings,1e-7 plane epsilon,1e-6 edge/barycentric margin. Tangencies/coplanar/contained and same-owner contacts excluded. Seven discrete poses, not continuous physics clearance.','poses':rows},indent=2)+'\n')
assert sha(NATIVE)==BOUND
print('COMPLETE',flush=True)
