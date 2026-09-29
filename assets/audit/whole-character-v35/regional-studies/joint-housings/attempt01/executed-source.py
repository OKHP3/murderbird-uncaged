"""V35 compact passive receiving housings on existing leg-owned joint parts.

Qualitative bounded proposal. Keeps all four leg rig nodes and their rests,
owners, materials, cross-joint center locations, and connected frame members.
Only existing meshes parented to left/right thigh and shin are reshaped.
"""
import bpy
import bmesh
from mathutils import Vector

OWNERS = {"left-thigh", "right-thigh", "left-shin", "right-shin"}


def apply():
    bpy.context.view_layer.update()
    changed = []
    for obj in sorted(bpy.data.objects, key=lambda item: item.name):
        if obj.type != "MESH" or not obj.parent or obj.parent.name not in OWNERS:
            continue
        name = obj.name.lower()
        if "proximal journal" in name or "proximal retainer rim" in name:
            radial_scale = 0.72
        elif "distal captive cheek" in name:
            radial_scale = 0.73 if "shin" in obj.parent.name else 0.72
        elif "proximal captive axle" in name:
            # Retain the full bridge span so it still enters both receivers.
            radial_scale = 0.62
        else:
            continue

        mesh = obj.data
        world = [obj.matrix_world @ vert.co for vert in mesh.vertices]
        cy = sum(point.y for point in world) / len(world)
        cz = sum(point.z for point in world) / len(world)
        for vert, point in zip(mesh.vertices, world):
            dy, dz = point.y - cy, point.z - cz
            radius = (dy * dy + dz * dz) ** 0.5
            if radius:
                angle = __import__("math").atan2(dz, dy)
                # A restrained four-lobed contour gives the bearing a formed,
                # compact housing silhouette while preserving its open race.
                housing = 1.0 + 0.045 * __import__("math").cos(4.0 * angle)
                factor = radial_scale * housing
                point.y = cy + dy * factor
                point.z = cz + dz * factor
            vert.co = obj.matrix_world.inverted() @ point
        mesh.update()
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(mesh)
        bm.free()
        changed.append({"name": obj.name, "owner": obj.parent.name,
                        "radialScale": radial_scale,
                        "materialNames": [mat.name for mat in mesh.materials]})

    return {
        "region": "compact passive thigh and shin receiving housings",
        "changedMeshes": changed,
        "added": [],
        "removed": [],
        "changedNodes": [],
        "status": "qualitative regional proposal; sampled articulation and clearance review pending",
        "limits": [
            "No body or hip receiver, foot, toe, runtime, material, rig rest, or joint center edited.",
            "The housing contour is a visual reconstruction, not engineering evidence.",
            "No continuous or discrete fit check is claimed.",
        ],
    }
