"""Finite receiving aperture for the independently rotating neck root.

The passive breast/shoulder coverings are relieved around an explicit sampled
motion envelope. This is editable kinematic construction, not simulation or
dimensions recovered from an illustration. Cervical plates and pivots stay exact.
"""
import bpy, bmesh, math, json
from mathutils import Vector, Quaternion

NAMES = ['V28 longitudinal breast guard 0 -1', 'V28 longitudinal breast guard 0 1',
         'V28 recessed shaped breast door', 'V24 rising thoracic receiving cheek -1',
         'V24 rising thoracic receiving cheek 1']

def signature(o):
    return (o.parent.name if o.parent else None, tuple(tuple(r) for r in o.matrix_world),
            json.dumps(dict(o.items()), sort_keys=True, default=lambda v: list(v)),
            tuple(tuple(v.co) for v in o.data.vertices) if o.type == 'MESH' else (),
            tuple(tuple(p.vertices) for p in o.data.polygons) if o.type == 'MESH' else ())

def hull(points):
    bm = bmesh.new()
    for p in points: bm.verts.new(p)
    bm.verts.ensure_lookup_table()
    result = bmesh.ops.convex_hull(bm, input=list(bm.verts), use_existing_faces=False)
    unused = set(result['geom_interior']) | set(result['geom_unused'])
    bmesh.ops.delete(bm, geom=list(unused), context='VERTS')
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    return bm

def apply():
    bpy.context.view_layer.update()
    before = {o.name: signature(o) for o in bpy.data.objects if o.type in ('EMPTY', 'MESH') and o.name not in NAMES}
    dg = bpy.context.evaluated_depsgraph_get()
    root = bpy.data.objects['neck'].matrix_world.translation.copy()
    points = []
    for o in bpy.data.objects:
        if o.type == 'MESH' and o.name.startswith('V23 cervical 1 directional guard '):
            ev = o.evaluated_get(dg); m = ev.to_mesh()
            points.extend(ev.matrix_world @ v.co for v in m.vertices); ev.to_mesh_clear()
    first = hull(points); base = [v.co.copy() for v in first.verts]; first.free()
    swept = []
    pitches = [-.14, 0., .08, .325, .65]
    yaws = [-.45, -.30, -.15, 0., .15, .30, .45]
    for pitch in pitches:
        for yaw in yaws:
            rotation = Quaternion((1, 0, 0), pitch * .25) @ Quaternion((0, 0, 1), yaw)
            swept.extend(root + rotation @ (v-root) for v in base)
    envelope = hull(swept); boundary = [v.co.copy() for v in envelope.verts]; envelope.free()
    pad = .004
    offsets = [Vector((x, y, z))*pad for x, y, z in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]]
    cutter_mesh = bpy.data.meshes.new('V29 temporary sampled root clearance')
    bm = hull([p+d for p in boundary for d in offsets]); bm.to_mesh(cutter_mesh); bm.free()
    cutter = bpy.data.objects.new('V29 temporary root receiving cutter', cutter_mesh)
    bpy.context.scene.collection.objects.link(cutter)
    results = []
    for name in NAMES:
        o = bpy.data.objects[name]; ev = o.evaluated_get(dg)
        m = bpy.data.meshes.new_from_object(ev, preserve_all_data_layers=True, depsgraph=dg)
        o.data = m; o.modifiers.clear()
        bm = bmesh.new(); bm.from_mesh(m); initial = abs(bm.calc_volume(signed=True)); bm.free()
        mod = o.modifiers.new('Finite neck root receiving clearance', 'BOOLEAN')
        mod.operation = 'DIFFERENCE'; mod.solver = 'EXACT'; mod.object = cutter
        with bpy.context.temp_override(object=o, active_object=o, selected_objects=[o], selected_editable_objects=[o]):
            bpy.ops.object.modifier_apply(modifier=mod.name)
        bm = bmesh.new(); bm.from_mesh(o.data)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        volume = abs(bm.calc_volume(signed=True)); closed = all(e.is_manifold for e in bm.edges)
        assert closed and volume > 0 and volume/initial > .65, (name, closed, volume/initial)
        bm.to_mesh(o.data); bm.free()
        o['v29ReceivingConstruction'] = 'Finite passive aperture around 35 sampled neck root poses plus authored 4 mm six-direction margin; no joint bridge'
        o['proposal'] = True
        results.append({'name': name, 'owner': o.parent.name, 'initialVolumeM3': initial,
                        'retainedVolumeFraction': volume/initial, 'closedEdgeManifold': closed})
    bpy.data.objects.remove(cutter, do_unlink=True); bpy.data.meshes.remove(cutter_mesh)
    # A short, plate-mounted return nests inside the receiving aperture. Its
    # upper rim meets the existing inner plate face; the lower edge remains
    # free to travel behind the breast. It is rigid on the neck, not a bridge
    # joining the moving neck to the body-fixed breast.
    returns = []
    for k in range(10):
        plate = bpy.data.objects[f'V23 cervical 1 directional guard {k+1}']
        assert len(plate.data.vertices) == 399
        points = [plate.matrix_world @ v.co for v in plate.data.vertices]
        verts = []; faces = []; rows = 8; cols = 18
        for row in range(rows+1):
            t = row/rows
            for col in range(cols+1):
                high = points[16*19+col]; low = points[20*19+col]
                normal = Vector((high.x/(.205**2), (high.y+.2085)/(.1735**2), 0)).normalized()
                top = high-normal*.0035
                end = low-normal*.023-Vector((0,0,.036))
                verts.append(top.lerp(end,t))
        for row in range(rows):
            for col in range(cols):
                q = row*19+col; faces.append((q,q+19,q+20,q+1))
        mesh = bpy.data.meshes.new(f'V29 root underlap {k+1} formed mesh')
        mesh.from_pydata(verts, [], faces); mesh.update()
        bm = bmesh.new(); bm.from_mesh(mesh)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        mid = bm.faces[len(bm.faces)//2]
        center = mid.calc_center_median(); radial = Vector((center.x, center.y+.2085, 0))
        if mid.normal.dot(radial) < 0: bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
        bm.to_mesh(mesh); bm.free()
        for mat in plate.data.materials: mesh.materials.append(mat)
        o = bpy.data.objects.new(f'V29 neck root recessed underlap {k+1}', mesh)
        bpy.context.scene.collection.objects.link(o); o.parent = bpy.data.objects['neck']
        o.matrix_parent_inverse = o.parent.matrix_world.inverted()
        for face in mesh.polygons: face.use_smooth = True
        m = o.modifiers.new('Finite rigid return wall', 'SOLIDIFY'); m.thickness = .0025; m.offset = -1
        m = o.modifiers.new('Return edge', 'BEVEL'); m.width = .0004; m.segments = 2
        o['region'] = 'neck'; o['surfaceRole'] = 'guard'; o['exteriorEras'] = 'maker,mechanic,builder'
        o['constructionClass'] = 'inherited-passive'; o['proposal'] = True
        o['authoringRole'] = 'Plate-mounted rigid recessed underlap; upper seam meets guard inner face, lower free edge nests behind independent breast'
        returns.append(o.name)
    bpy.context.view_layer.update()
    assert before == {n: signature(bpy.data.objects[n]) for n in before}
    return {'region': 'neck root receiving aperture', 'changedMeshes': NAMES, 'added': returns, 'removed': [],
            'samples': {'totalNeckPitch': pitches, 'rootYaw': yaws, 'pitchShareAtRoot': .25},
            'authoredMarginM': pad, 'clearance': results, 'allOtherObjectsExact': len(before),
            'reference': 'Owner whole-bird controls the breast to articulated neck transition; the hidden receiving aperture is reconstruction.',
            'eraEligibility': 'Inherited passive guard and shell, all three eras; no power or sensing added.',
            'limits': ['Discrete pose sweep, not continuous collision certification.',
                       'Adjacent cervical overlaps are unchanged and remain unresolved.',
                       'Breast inspection opening and visible aperture must be reviewed in composition.']}
