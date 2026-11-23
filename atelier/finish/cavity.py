"""Bake model-space contact and crevice tone to the assembled resting sculpture.

Run after material assignment, before the native save and modifier evaluation
for export. Stored point colors are neutral linear-RGB multipliers. The caller
can multiply them into the material in Blender or export them as COLOR_0.
"""
from collections import defaultdict
from math import cos, sin, sqrt, pi
from time import perf_counter

import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ATTRIBUTE = "FC_Occlusion"
# Model-space distances in the retained two-metre CG convention.
NEAR = .040
FAR = .155
BIAS = .0013
# One world-oriented sphere keeps neighboring patches on different castings
# coherent. Each vertex receives the Lambert-weighted outward hemisphere.
DIRECTION_COUNT = 60


def _directions():
    golden = pi * (3 - sqrt(5))
    directions = []
    for i in range(DIRECTION_COUNT):
        z = 1 - 2*(i+.5)/DIRECTION_COUNT
        radius = sqrt(1-z*z)
        a = golden*(i+.37)
        directions.append((radius*cos(a),radius*sin(a),z))
    return np.asarray(directions, dtype=np.float32)


def _coords(mesh, matrix):
    points = np.empty(3*len(mesh.vertices), dtype=np.float32)
    mesh.vertices.foreach_get("co",points)
    mat = np.asarray(matrix, dtype=np.float32)
    return points.reshape(-1,3) @ mat[:3,:3].T + mat[:3,3]


def _world_normals(mesh, matrix):
    normals = np.empty(3*len(mesh.vertices),dtype=np.float32)
    mesh.vertices.foreach_get("normal",normals)
    inverse = np.linalg.pinv(np.asarray(matrix, dtype=np.float32)[:3,:3])
    normals = normals.reshape(-1,3) @ inverse
    lengths = np.linalg.norm(normals,axis=1)
    normals /= np.maximum(lengths[:,None],1e-9)
    return normals


def _scene_tree(objects):
    points, faces, owners = [], [], []
    offset = 0
    deps = bpy.context.evaluated_depsgraph_get()
    for index, obj in enumerate(objects):
        ev = obj.evaluated_get(deps)
        mesh = ev.data
        if not mesh.polygons:
            continue
        xyz = _coords(mesh,ev.matrix_world)
        mesh.calc_loop_triangles()
        tri = np.empty(3*len(mesh.loop_triangles),dtype=np.int32)
        mesh.loop_triangles.foreach_get("vertices",tri)
        points.append(xyz)
        faces.append(tri.reshape(-1,3)+offset)
        owners.append(np.full(len(mesh.loop_triangles),index,dtype=np.int32))
        offset += len(xyz)
    if not faces:
        raise ValueError("No visible surfaces for the cavity bake")
    xyz = np.concatenate(points)
    triangles = np.concatenate(faces)
    tree = BVHTree.FromPolygons(xyz.tolist(),triangles.tolist(),all_triangles=True)
    return tree, np.concatenate(owners), len(xyz), len(triangles)


def _protected(mesh):
    """Protect every original vertex touching optical, enamel or liner faces."""
    pins = np.zeros(len(mesh.vertices),dtype=bool)
    protected_slots = [
        i for i,m in enumerate(mesh.materials)
        if m and (m.name.casefold().startswith("cgo13")
                  or any(k in m.name.casefold() for k in ("enamel","leather")))
    ]
    if not protected_slots:
        return pins
    if len(protected_slots) == len(mesh.materials):
        pins[:] = True
        return pins
    indices = np.empty(len(mesh.polygons),dtype=np.int32)
    counts = np.empty(len(mesh.polygons),dtype=np.int32)
    mesh.polygons.foreach_get("material_index",indices)
    mesh.polygons.foreach_get("loop_total",counts)
    loops = np.empty(len(mesh.loops),dtype=np.int32)
    mesh.loops.foreach_get("vertex_index",loops)
    pins[loops[np.repeat(np.isin(indices,protected_slots),counts)]] = True
    return pins


def _exposure(mesh, xyz, normals):
    """Small convex-highlight relief, inferred from one-ring mesh curvature."""
    n = len(xyz)
    edges = np.empty(2*len(mesh.edges),dtype=np.int32)
    mesh.edges.foreach_get("vertices",edges)
    a,b = edges.reshape(-1,2).T
    delta = xyz[a]-xyz[b]
    delta /= np.maximum(1.e-9,np.linalg.norm(delta,axis=1)[:,None])
    sa = np.einsum("ij,ij->i",delta,normals[a])
    sb = -np.einsum("ij,ij->i",delta,normals[b])
    total = np.bincount(a,weights=sa,minlength=n)+np.bincount(b,weights=sb,minlength=n)
    counts = np.bincount(a,minlength=n)+np.bincount(b,minlength=n)
    return np.clip(total/np.maximum(counts,1)*3.2,0.,1.)


def _visibility(obj,index,tree,owners,directions,ray_vectors):
    mesh = obj.data
    xyz = _coords(mesh,obj.matrix_world)
    normals = _world_normals(mesh,obj.matrix_world)
    pins = _protected(mesh)
    count = len(xyz)
    values = np.ones(count,dtype=np.float32)
    blocked = np.zeros(count,dtype=np.float32)
    sum_weight = np.zeros(count,dtype=np.float32)
    origins = [Vector(v) for v in xyz+BIAS*normals]
    cast = tree.ray_cast
    samples = 0
    for direction,ray in zip(directions,ray_vectors):
        weights = normals @ direction
        active = np.flatnonzero((weights > .035) & ~pins)
        sum_weight[active] += weights[active]
        samples += len(active)
        for i in active:
            origin = origins[i]
            location,_,triangle,distance = cast(origin,ray,FAR)
            if triangle is None:
                continue
            # A bevel or newly solidified skin can straddle the source vertex.
            # Skip its near self-surface, but preserve a different plate resting
            # directly against the same point.
            if distance < .0024 and owners[triangle] == index:
                offset = distance + .0024
                _,_,triangle,d = cast(location + ray*.0024,ray,FAR-offset)
                if triangle is None:
                    continue
                distance = offset+d
            # A close occluder carries the strongest tone. A broader, weaker
            # term joins neighboring dark recesses without staining open metal.
            a = max(0.,1.-distance/NEAR)
            b = max(0.,1.-distance/FAR)
            blocked[i] += weights[i] * (.70*a**.75 + .30*b*b)
    occlusion = np.clip(blocked/np.maximum(sum_weight,1.e-8),0.,1.)
    exposed = _exposure(mesh,xyz,normals)
    values[:] = .32 + .68*(1.-occlusion)**1.35
    values += (1.-values)*(.082*exposed)
    values[pins] = 1.
    return values, int(np.count_nonzero(pins)), int(samples)


def _store(mesh, values):
    attr = mesh.color_attributes.get(ATTRIBUTE)
    if attr and (attr.domain != "POINT" or attr.data_type != "BYTE_COLOR"):
        raise ValueError(f"Existing attribute {ATTRIBUTE} has incompatible storage on {mesh.name}")
    if attr is None:
        attr = mesh.color_attributes.new(name=ATTRIBUTE,type="BYTE_COLOR",domain="POINT")
    colors = np.empty((len(values),4),dtype=np.float32)
    colors[:,:3] = values[:,None]
    colors[:,3] = 1.
    # Blender's 'color' accessor converts linear RGB to byte storage; avoid
    # writing linear values through 'color_srgb', which would bake double-dark.
    attr.data.foreach_set("color",colors.ravel())
    i = mesh.color_attributes.find(ATTRIBUTE)
    mesh.color_attributes.active_color_index = i
    mesh.color_attributes.render_color_index = i


def _summary(chunks):
    vals = np.concatenate(chunks)
    stats = np.percentile(vals,[0,5,25,50,75,95,100])
    return dict(vertices=int(len(vals)),mean=round(float(vals.mean()),4),
                **{k:round(float(v),4) for k,v in zip(("min","p05","p25","median","p75","p95","max"),stats)},
                at_most_045=int(np.count_nonzero(vals<=.45)),at_least_097=int(np.count_nonzero(vals>=.97)))


def apply_cavity(objects):
    """Bake against visible, evaluated geometry at the current rest pose.

    Supply only model and fixture mesh objects. Returns JSON-serializable
    coverage, distribution and wall-time evidence; leaves topology unchanged.
    """
    start = perf_counter()
    objects = sorted((o for o in objects if o.type=="MESH" and not o.hide_render
                      and o.data.vertices), key=lambda o:o.name)
    unique = {o.data.as_pointer() for o in objects}
    if len(unique) != len(objects):
        raise ValueError("Per-instance cavity requires an independent mesh per visible object")
    bpy.context.view_layer.update()
    tree,owners,evaluated_vertices,triangles = _scene_tree(objects)
    bvh_seconds = perf_counter()-start
    directions = _directions()
    rays = [Vector(d) for d in directions]
    groups = defaultdict(list)
    protected,cast = 0,0
    for i,obj in enumerate(objects):
        values,pins,samples = _visibility(obj,i,tree,owners,directions,rays)
        _store(obj.data,values)
        region = str(obj.get("fc_region") or obj.get("cg1cRegion") or "fixture")
        groups[region].append(values)
        protected += pins
        cast += samples
        if (i+1)%500 == 0:
            print(f"Cavity bake: {i+1}/{len(objects)} parts, {perf_counter()-start:.1f} s",flush=True)
    all_values = [v for vv in groups.values() for v in vv]
    summary = _summary(all_values)
    return dict(attribute=ATTRIBUTE,domain="POINT",type="BYTE_COLOR",linear=True,
                objects=len(objects),evaluated_vertices=evaluated_vertices,evaluated_triangles=triangles,
                samples=cast,short_radius=NEAR,broad_radius=FAR,surface_bias=BIAS,
                protected_vertices=protected,distribution=summary,
                regions={r:_summary(vv) for r,vv in sorted(groups.items())},
                bvh_seconds=round(bvh_seconds,2),bake_seconds=round(perf_counter()-start,2))
