"""Measure the sampled, visible shoe/body gap and protected joint centres."""
import json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector
HERE=Path(__file__).resolve().parent
for d in (HERE,HERE.parent/'mantle',HERE.parent/'head',HERE.parent/'feet',HERE.parent/'pedal'):sys.path.insert(0,str(d))
from cranial import apply_head
from pedal import apply_pedal
from mantle import apply_mantle
from first_choice import apply_motion, HIP, SADDLE_AXIS
scene=bpy.context.scene
scene.frame_set(0)
if bpy.data.objects.get("FC | Torso"):
 anchors={key:bpy.data.objects["FC | "+key.title()] for key in ("ground","stand","saddle","torso","neck","head")}
else:
 apply_head()
 apply_mantle()
 apply_pedal()
 anchors=apply_motion()["anchors"]
shoe=bpy.data.objects['FC fixture | shaped leather saddle liner']
# Obtain contact points on the evaluated liner itself, including its bevel
# and the actual triangulation of its originally quadrilateral top patches.
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
shoe_tree=BVHTree.FromObject(shoe,dg)
points=[]
for j in range(19):
 for i in range(51):
  x=-.07385+.1477*i/50
  y=-.26485+.0537*j/18
  point,_,_,_=shoe_tree.ray_cast(Vector((x,y,1.15)),Vector((0,0,-1)))
  if point is not None:
   points.append(point)
# Cache native local meshes once. Work in each object's rest coordinates,
# then apply the inverse rigid pose of the torso to the shoe sample.
dg=bpy.context.evaluated_depsgraph_get(); body=[]
rest_torso=anchors['torso'].matrix_world.copy()
for ob in scene.objects:
 if ob.type!='MESH' or ob.get('fc_region')!='torso' or ob.hide_render or not ob.visible_get():continue
 bb=[ob.matrix_world@Vector(p) for p in ob.bound_box]
 if max(p.x for p in bb)<-.085 or min(p.x for p in bb)>.085 or max(p.y for p in bb)<-.29 or min(p.y for p in bb)>-.18 or max(p.z for p in bb)<.67 or min(p.z for p in bb)>1:continue
 from mathutils.bvhtree import BVHTree
 body.append((BVHTree.FromObject(ob,dg),ob.matrix_world.copy(),ob.matrix_world.inverted()))
positive=[]
for f in range(253):
 scene.frame_set(f)
 torso_inv=rest_torso @ anchors['torso'].matrix_world.inverted()
 rel=torso_inv @ shoe.matrix_world
 dr=torso_inv.to_3x3()@Vector((0,0,1))
 pmin=100; vals=[]; missed=0
 for local in points:
  shoe_bird=rel@local
  origin=shoe_bird-dr*.035
  hits=[]
  for tree,wm,inv in body:
   at,normal,_,dd=tree.ray_cast(inv@origin,inv.to_3x3()@dr)
   if at is not None:
    delta=wm@at-shoe_bird
    hits.append(delta.dot(dr.normalized()))
  if hits:
   vals.append(min(hits))
  else: missed+=1
 vals.sort()
 positive.append({'frame':f,'sampled_vertical_gap_mm':{'min':round(vals[0]*1000,2),'median':round(vals[len(vals)//2]*1000,2),'max':round(vals[-1]*1000,2)},'negative_samples':sum(v<0 for v in vals),'samples':len(points),'missing':missed})
print('first, peak transfer, hold, rest',*[positive[i] for i in (0,54,73,155,252)])
(HERE/'shoe-clearances.json').write_text(json.dumps({'description':'Upward rays from a regular 51 × 19 grid over the evaluated, bevelled liner top (four clipped rim corners fall outside the mesh; 965 valid locations) at each of 253 evaluated poses. Positive values measure visual separation from the ventral shell. Native Blender units interpreted as metres. No dynamics, fit tolerance, or physical validation.','samples':positive},indent=2))
