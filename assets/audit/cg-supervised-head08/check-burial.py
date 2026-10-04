import bpy,json,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[3];A=R/'assets/audit/cg-supervised-head08';result={}
def measure(s):
 frame=s.objects['CG2b head frame'].matrix_world;back=s.objects['CGH05 curved recessed vault above cheek opening'];dg=bpy.context.evaluated_depsgraph_get();ev=back.evaluated_get(dg);em=ev.to_mesh();mat=frame.inverted()@back.matrix_world;vv=[mat@v.co for v in em.vertices];bv=BVHTree.FromPolygons(vv,[list(f.vertices) for f in em.polygons]);ev.to_mesh_clear()
 # Ring centers are derived from actual evaluated backing, not old04 stations.
 centers={}
 for v in vv:centers.setdefault(round(v.y,6),[]).append(v)
 rings=sorted((y,sum(v.z for v in vs)/len(vs)) for y,vs in centers.items())
 def center(y):
  for (a,b),(c,d) in zip(rings,rings[1:]):
   if y<=c:return Vector((0,y,b+(d-b)*max(0,min(1,(y-a)/(c-a)))))
  return Vector((0,y,rings[-1][1]))
 out={}
 for kind in ['base','evaluated']:
  hits=0;miss=0;buried=0;minimum=1.;maximum=0.;total=0
  for o in s.objects:
   if not o.get('cgSupervisedHead08') or 'actual vault swept plate' not in o.name:continue
   eo=o.evaluated_get(dg) if kind=='evaluated' else None;m=eo.to_mesh() if eo else o.data;xf=frame.inverted()@o.matrix_world
   for v in m.vertices:
    total+=1;q=xf@v.co;c=center(q.y);direction=(q-c).normalized();hit=bv.ray_cast(c+direction*.8,-direction)
    if hit[0] is None:miss+=1;continue
    hits+=1;clearance=(q-hit[0]).dot(direction);minimum=min(minimum,clearance);maximum=max(maximum,-clearance)
    if clearance<-.0002:buried+=1
   if eo:eo.to_mesh_clear()
  out[kind]={'vertices':total,'ray_hits':hits,'ray_misses':miss,'buried_beyond_0_0002m':buried,'minimum_signed_clearance_m':minimum,'maximum_penetration_m':maximum}
 return {'actual_backing':back.name,'backing_hidden_render':back.hide_render,'backing_hidden_viewport':back.hide_get(),'hidden04':s.objects['CGH04 nine section cranial vault'].hide_render,'measurements':out,'scope':'radial ray diagnostic against actual evaluated original05 backing; negative means underneath original backing surface. Backing is explicitly hidden so numeric burial does not itself measure final pixel occlusion.'}
for attempt in ['attempt01','attempt02']:
 bpy.ops.wm.open_mainfile(filepath=str(A/attempt/'formed-head08.blend'));result[attempt]=measure(bpy.context.scene)
(A/'backing-burial.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
