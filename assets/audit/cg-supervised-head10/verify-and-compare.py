import bpy,json,sys,math,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
BASE=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged/assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend')
report=json.loads((OUT/'attempt02/receipt.json').read_text());checks={}
def p(x,y,d):return Vector((d,(788-x)*.0012+.005,(188-y)*.0012+.020))
def setcam(scene,c):
 scene.camera.matrix_world=Matrix(c['matrix']);scene.camera.data.ortho_scale=c['scale'];scene.camera.data.shift_x,scene.camera.data.shift_y=c['shift'];scene.render.resolution_x,scene.render.resolution_y=c['resolution'];scene.render.resolution_percentage=100;bpy.context.view_layer.update()
def proj(scene,q):
 v=world_to_camera_view(scene,scene.camera,q);return [v.x*scene.render.resolution_x,(1-v.y)*scene.render.resolution_y]
for attempt in ('attempt01','attempt02'):
 bpy.ops.wm.open_mainfile(filepath=str(OUT/attempt/'formed-head10.blend'));scene=bpy.context.scene;frame=scene.objects['CG2b head frame'].matrix_world
 verts=[];polys=[]
 for o in scene.objects:
  if o.get('cgSupervisedHead10'):
   e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh();off=len(verts);verts.extend(o.matrix_world@v.co for v in me.vertices);polys.extend(tuple(off+i for i in f.vertices) for f in me.polygons);e.to_mesh_clear()
 tree=BVHTree.FromPolygons(verts,polys);allchecks={}
 for name,c in report['cameras'].items():
  setcam(scene,c);E=proj(scene,frame@p(788,188,-.166));outline=[proj(scene,frame@p(788+53*math.cos(t*math.tau/128),188+53*math.sin(t*math.tau/128),-.166)) for t in range(128)]
  D=max(math.dist(a,b) for a in outline for b in outline);vs=[proj(scene,v) for v in verts];C=min(vs,key=lambda q:q[1]);R=proj(scene,frame@p(850,175,-.157))
  direction=scene.camera.matrix_world.to_quaternion()@Vector((0,0,-1));blocked=[];count=0
  for side in (-1,1):
   for r in (0,12,24,36,40):
    for k in range(32 if r else 1):
     q=frame@p(788+r*math.cos(k*math.tau/32),188+r*math.sin(k*math.tau/32),side*.160);hit=tree.ray_cast(q-direction*10,direction,10.0);count+=1
     if hit[0] is not None:blocked.append({'side':side,'radius':r,'angle':k*360/32,'distance_before_lens':10-hit[3]})
  allchecks[name]={'E':E,'D':D,'C':C,'R_declared_brow_transition':R,'posterior_C_in_D':(E[0]-C[0])/D,'height_C_in_D':(E[1]-C[1])/D,'anterior_R_in_D':(R[0]-E[0])/D,'aperture_new_geometry_ray_samples':count,'blocked_samples':blocked,'ray_note':'Both sides sampled; far-side rays may cross opposite exterior normally. Inspect near-side separately; original optics not ray-tested here.'}
 checks[attempt]=allchecks
(OUT/'projected-landmarks-and-clearance.json').write_text(json.dumps(checks,indent=2))
# Matched before evidence uses exactly the same frozen saved06 lighting.
bpy.ops.wm.open_mainfile(filepath=str(BASE));scene=bpy.context.scene;scene.cycles.samples=8;scene.cycles.use_denoising=True
clay=bpy.data.materials.new('head10-before-diagnostic-clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.42,.42,.42,1);bs.inputs['Roughness'].default_value=.75
for name,c in report['cameras'].items():
 setcam(scene,c);scene.view_layers[0].material_override=clay if 'clay' in name else None;scene.render.filepath=str(OUT/(name.replace('after','before')+'.png'));bpy.ops.render.render(write_still=True)
print('HEAD10_COMPARISON_COMPLETE',flush=True)
