import bpy, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def eval_surface(obj):
    deps = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(deps); mesh = ev.to_mesh(); mesh.calc_loop_triangles()
    verts = [ev.matrix_world @ v.co for v in mesh.vertices]
    faces = [tuple(t.vertices) for t in mesh.loop_triangles]
    tree = BVHTree.FromPolygons(verts, faces, all_triangles=True, epsilon=0)
    ev.to_mesh_clear()
    return tree

shell = bpy.data.objects['Breast inner access shell']
shell_tree = eval_surface(shell)
def ray_hits(x,z):
    origin=Vector((x,-1.5,z)); direction=Vector((0,1,0)); hits=[]
    for _ in range(12):
        loc,norm,face,distance=shell_tree.ray_cast(origin,direction,3.0)
        if loc is None: break
        hits.append({'y':float(loc.y),'normalY':float(norm.y),'face':int(face)})
        origin=loc+direction*0.0001
    return hits
rows=[]
for name in ['Passive rib behind access cover.002','Passive rib behind access cover.003']:
    obj=bpy.data.objects[name]
    deps=bpy.context.evaluated_depsgraph_get(); ev=obj.evaluated_get(deps); mesh=ev.to_mesh()
    mesh.calc_loop_triangles(); points=[ev.matrix_world@v.co for v in mesh.vertices]
    xlo=min(p.x for p in points); xhi=max(p.x for p in points)
    bins=[]
    for k in range(10):
        lo=xlo+(xhi-xlo)*k/10; hi=xlo+(xhi-xlo)*(k+1)/10
        band=[p for p in points if lo<=p.x<hi]
        bins.append({'x':[(lo+hi)/2,'count',len(band)],'minY':min(p.y for p in band),'maxY':max(p.y for p in band),'minZ':min(p.z for p in band),'maxZ':max(p.z for p in band)})
    samples=[]
    for p in points[::max(1,len(points)//60)]:
        hitneg=shell_tree.ray_cast(Vector((p.x,-2,p.z)),Vector((0,1,0)),4)[0]
        hitpos=shell_tree.ray_cast(Vector((p.x,2,p.z)),Vector((0,-1,0)),4)[0]
        samples.append({'ribXYZ':list(p),'shellFromFront':list(hitneg) if hitneg else None,'shellFromRear':list(hitpos) if hitpos else None})
    rows.append({'name':name,'parent':obj.parent.name if obj.parent else None,'vertices':len(points),'triangles':len(mesh.loop_triangles),'bounds':[[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]],'bins':bins,'samples':samples,'shellRayGrid':[{'x':x,'z':z,'hits':ray_hits(x,z)} for x in (-.30,-.24,-.18,-.12,0,.12,.18,.24,.30) for z in (1.10,1.12,1.23,1.25)]})
    ev.to_mesh_clear()
print(json.dumps(rows))
