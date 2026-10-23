"""Small fabrication details fitted to the retained bill and jaw surfaces.

The visible ports, fixings and joining lines are appearance proposals. Their
positions are authored rather than measured from an illustration. Every part
is seated by ray intersection with the existing evaluated surface and inherits
that surface's rigid owner. Bill contact and joint locations are unchanged.
"""

def build(ctx):
    from mathutils.bvhtree import BVHTree
    bpy, Vector, math = ctx['bpy'], ctx['Vector'], ctx['math']
    wr, wt = ctx['wr'], ctx['wt']
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    surfaces = {}
    for owner, prefixes in [('upper-bill', ('Profiled upper bill blade',)),
                            ('jaw', ('Crescent mandible',))]:
        vertices, faces = [], []
        for obj in list(bpy.context.scene.objects):
            if obj.type != 'MESH' or not obj.name.startswith(prefixes):
                continue
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            start = len(vertices)
            vertices.extend(evaluated.matrix_world @ v.co for v in mesh.vertices)
            faces.extend(tuple(start+i for i in p.vertices) for p in mesh.polygons)
            evaluated.to_mesh_clear()
        assert vertices, owner
        surfaces[owner] = BVHTree.FromPolygons(vertices, faces)

    count = 0
    def seat(owner, side, yz):
        p, normal, _, _ = surfaces[owner].ray_cast(
            Vector((side*.6, yz[0], yz[1])), Vector((-side, 0, 0)), 1.2)
        if p is None:
            return None
        if normal.x*side < 0:
            normal = -normal
        return p, normal.normalized()

    def fixing(owner, side, yz, radius=.0024):
        nonlocal count
        hit = seat(owner, side, yz)
        if hit is None:
            return
        p, normal = hit
        parent = bpy.data.objects[owner]
        wr(f'Fitted {owner} flush washer {side} {count}', p-normal*.0003,
           p+normal*.0006, radius*1.35, parent, 'head', 'recess', sides=12)
        wr(f'Fitted {owner} peened fixing {side} {count}', p+normal*.0004,
           p+normal*.0019, radius, parent, 'head', 'bearing', sides=12)
        tangent = normal.cross(Vector((0,0,1))).normalized()
        wt(f'Fitted {owner} tool slot {side} {count}',
           [p+normal*.0020-tangent*radius*.62,
            p+normal*.0020+tangent*radius*.62], [.00032,.00032],
           parent, 'head', 'recess', sides=5)
        count += 1

    # Separate tracks across the broad forged bill; all stop before the thin
    # cutting hook. The loops below are not new contact or motion geometry.
    upper_track = [(-.481,1.800),(-.519,1.783),(-.555,1.754),
                   (-.591,1.722),(-.621,1.683),(-.642,1.643)]
    lower_track = [(-.472,1.719),(-.506,1.708),(-.544,1.688),
                   (-.575,1.664),(-.604,1.630)]
    jaw_track = [(-.369,1.601),(-.407,1.601),(-.446,1.596),
                 (-.486,1.577),(-.527,1.550),(-.570,1.540)]
    for side in (-1,1):
        for yz in upper_track+lower_track:
            fixing('upper-bill', side, yz)
        for yz in jaw_track:
            fixing('jaw', side, yz, .0021)
        for number, track in enumerate([upper_track,lower_track]):
            hits=[seat('upper-bill',side,p) for p in track]
            assert all(hits), 'Bill joining line left the retained surface'
            wt(f'Surface fitted bill fine joining line {side} {number}',
               [p+n*.00035 for p,n in hits], [.0006]*len(hits),
               bpy.data.objects['upper-bill'], 'head', 'recess', sides=6)
        hit=seat('upper-bill',side,(-.514,1.743))
        if hit:
            p,normal=hit
            # A dark inset and narrow raised lip give a small service-port
            # appearance; no through-hole or underlying mechanism is claimed.
            wr(f'Bill dark service inset {side}',p-normal*.0002,p+normal*.0006,
               .0085,bpy.data.objects['upper-bill'],'head','recess',sides=32)
            tangent=normal.cross(Vector((0,0,1))).normalized()
            bitangent=normal.cross(tangent).normalized()
            points=[p+normal*.0008+.0085*(tangent*math.cos(i*math.tau/32)+
                     bitangent*math.sin(i*math.tau/32)) for i in range(33)]
            wt(f'Bill service inset fine lip {side}',points,[.00075]*len(points),
               bpy.data.objects['upper-bill'],'head','bearing',sides=6)
    return {'fittedFixings':count,'placement':'ray-seated on retained evaluated surfaces',
            'status':'visible fabrication proposal; no structural or contact changes'}
