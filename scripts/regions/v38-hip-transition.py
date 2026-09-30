"""V38 bounded hip-bearing transition study, built from a receipt-bound V37 native.

The two fixed C-seat shells stop above/beside the moving thigh journal. The
thigh-owned proximal cheeks follow existing pivots; no body-to-thigh bridge is
added. This is a shape proposal, not likeness or engineering acceptance.
"""
import bpy, math
from mathutils import Vector

ERAS = "maker,mechanic,builder"

def _mesh(name, verts, faces, owner, material, role):
    mesh = bpy.data.meshes.new(name + " mesh")
    mesh.from_pydata(verts, [], faces); mesh.update()
    mesh.materials.append(material)
    obj = bpy.data.objects.new(name, mesh); bpy.context.scene.collection.objects.link(obj)
    parent = bpy.data.objects[owner]
    obj.parent = parent; obj.matrix_parent_inverse.identity(); obj.matrix_basis.identity()
    inv = parent.matrix_world.inverted()
    for v in mesh.vertices:
        v.co = inv @ v.co
    obj["region"] = "hip-transition"; obj["surfaceRole"] = role
    obj["exteriorEras"] = ERAS; obj["constructionClass"] = "proposed-passive"
    obj["geometryStatus"] = "V38 bounded transition study; not likeness or engineering acceptance"
    return obj

def _seat(side, material):
    # Axle lies on local X. A 236-degree annular seat leaves the lower/front
    # sector open around the rotating proximal thigh assembly.
    cx, cy, cz = side * .231, .051, .668
    n = 32; start = math.radians(-58); end = math.radians(182)
    verts=[]; faces=[]
    for x in (cx-side*.040, cx+side*.040):
        for radius in (.077, .120):
            for i in range(n+1):
                a=start+(end-start)*i/n
                verts.append((x, cy+radius*math.cos(a), cz+radius*math.sin(a)))
    layer=(n+1)
    for i in range(n):
        faces += [(i,i+1,layer+i+1,layer+i),
                  (2*layer+i,3*layer+i,3*layer+i+1,2*layer+i+1),
                  (i,2*layer+i,2*layer+i+1,i+1),
                  (layer+i,layer+i+1,3*layer+i+1,3*layer+i)]
    # Close the two cut ends without closing the axle bore.
    for i in (0,n): faces.append((i,layer+i,3*layer+i,2*layer+i))
    name=f"V38 {'left' if side>0 else 'right'} open hip bearing seat"
    return _mesh(name, verts, faces, "body", material, "open C-seat around retained thigh pivot")

def _thigh_cheek(side, material):
    # A compact tapered side cheek at the proximal load path, owned by thigh;
    # positioned outside the existing links, with no cover across their span.
    sign="left" if side>0 else "right"
    x=side*.231
    poly=[(x+side*.066,.045,.638),(x+side*.104,.020,.604),
          (x+side*.115,-.074,.488),(x+side*.078,-.104,.500),
          (x+side*.058,-.042,.630)]
    verts=[(px,py-.028,pz) for px,py,pz in poly]+[(px,py+.028,pz) for px,py,pz in poly]
    faces=[tuple(range(5)),tuple(range(9,4,-1))]
    faces += [(i,(i+1)%5,(i+1)%5+5,i+5) for i in range(5)]
    return _mesh(f"V38 {sign} thigh proximal load cheek",verts,faces,f"{sign}-thigh",material,"outboard proximal thigh support cheek")

def apply():
    # Match existing proximal journal/frame colors; no material definitions change.
    frame=bpy.data.objects["V25 left thigh proximal journal -1"].data.materials[0]
    for side in (1,-1):
        _seat(side,frame)
        _thigh_cheek(side,frame)
    bpy.context.view_layer.update()
    return [o.name for o in bpy.data.objects if o.get("region")=="hip-transition"]
