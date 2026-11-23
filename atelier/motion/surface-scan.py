import bpy,collections,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
selected=[]
tags={}
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.visible_get(): continue
 t={k:str(ob[k]) for k in ob.keys()}
 tags[ob.name]=t
 if 'ground' in ob.name.lower(): continue
 bb=[ob.matrix_world@Vector(c) for c in ob.bound_box]
 if min(p.x for p in bb)>.17 or max(p.x for p in bb)<-.17 or max(p.z for p in bb)<.55 or min(p.z for p in bb)>.98 or min(p.y for p in bb)>-.08:continue
 tree=BVHTree.FromObject(ob,dg)
 selected.append((ob,ob.matrix_world.inverted(),tree))
def ray(pt,dr):
 result=[]
 for ob,inv,tree in selected:
  c,n,i,d=tree.ray_cast(inv@Vector(pt),inv.to_3x3()@Vector(dr))
  if c is not None:
   w=ob.matrix_world@c
   result.append((round((w-Vector(pt)).length,5),ob.name,[round(a,5) for a in w]))
 return min(result) if result else None
for x in [-.11,0,.11]:
 for y in [-.10,-.12,-.14,-.16,-.18,-.20,-.22,-.24,-.26,-.28,-.30,-.32]:
  print('bottom',x,y,ray((x,y,.45),(0,0,1)))
 for z in [.65,.70,.75,.80,.85]:
  print('front',x,z,ray((x,-.7,z),(0,1,0)))
json.dump(tags,open('native/atelier/motion/original-region-tags.json','w'))
print(collections.Counter((v.get('cg1cRegion'),) for v in tags.values()))
