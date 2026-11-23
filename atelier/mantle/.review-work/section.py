import bpy, sys
from mathutils import Vector
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from mantle import apply_mantle
apply_mantle()
from mathutils.bvhtree import BVHTree
from collections import Counter
verts=[];faces=[];objects=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.hide_render:continue
 if min((o.matrix_world@Vector(p)).z for p in o.bound_box)>.94:continue
 start=len(verts);verts.extend(o.matrix_world@v.co for v in o.data.vertices);faces.extend(tuple(start+i for i in f.vertices) for f in o.data.polygons);objects.extend([o]*len(o.data.polygons))
tree=BVHTree.FromPolygons(verts,faces)
for z in [.91,.87,.83,.79,.75,.71,.67,.63,.59]:
 out=[]
 for y in [-.38,-.34,-.30,-.26,-.22,-.18,-.14,-.10,-.06,-.02,.02,.06,.10,.14,.18,.22,.26,.30,.34]:
  p,n,k,d=tree.ray_cast(Vector((-.8,y,z)),Vector((1,0,0)),1.6)
  if p is not None:
   o=objects[k].name
   ty=('leg' if any(w in o.lower() for w in ('thigh',' hip','leg','upper','knee',' hock','shank','barrel','ram')) else 'back' if 'compact posterior' in o else 'front' if 'rounded course' in o or 'FC torso' in o else 'other')
   out.append(f"{ty[:1]}{-p.x*100:02.0f}")
  else:out.append('---')
 print(f'z {z:.2f}',*out)
for y in [-.34,-.28,-.21,-.14,-.07,0,.07,.14,.21,.28,.33]:
 print('section',y,end=' ')
 for x in [0,.03,.07,.10,.13,.16]:
  p,n,k,d=tree.ray_cast(Vector((x,y,.40)),Vector((0,0,1)),.6)
  print(f"{p.z:.3f}:{objects[k].name[:34]}" if p is not None else '-',end='|')
 print()
