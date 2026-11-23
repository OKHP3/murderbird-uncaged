import json, bpy, sys, re
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
folder=Path(__file__).resolve().parent
sys.path.insert(0,str(folder))
from mantle import apply_mantle
report=apply_mantle()
def tree(names):
    verts=[];faces=[]
    for o in bpy.context.scene.objects:
        if o.type!="MESH" or o.hide_render or not names(o):continue
        offset=len(verts)
        verts.extend([o.matrix_world@v.co for v in o.data.vertices])
        faces.extend([tuple(offset+i for i in f.vertices) for f in o.data.polygons])
    return BVHTree.FromPolygons(verts,faces),len(faces),len(verts)
body,nface,nvert=tree(lambda o:('breast' in o.name.lower() or 'compact posterior' in o.name or o.name.startswith('CGRB0') or o.name=='FC torso | nested ventral keel'))
for y in (-.28,-.24,-.2,-.16,-.12):
    hits=[]
    for x in (-.08,0,.08):
        hit,*_=body.ray_cast(Vector((x,y,.3)),Vector((0,0,1)),1.)
        hits.append([round(hit.z,4),x] if hit else None)
    print('Lower body underside at Y',y,hits,flush=True)
for rg in ['wing.L','wing.R','torso','neck']:
    oo=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('first_choice_region')==rg]
    bbox=[o.matrix_world@Vector(p) for o in oo for p in o.bound_box]
    print('Region',rg,len(oo),[round(min(p[i] for p in bbox),4) for i in range(3)],[round(max(p[i] for p in bbox),4) for i in range(3)],flush=True)
print(report,flush=True)
