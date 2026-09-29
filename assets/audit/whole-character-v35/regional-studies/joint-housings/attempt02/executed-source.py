"""V35 compact linked thigh/shin frames with seated receiving housings.

Compresses only the X width of existing meshes under thigh/shin owners. The
profile preserves the current hip and ankle interfaces and brings both sides
to the same narrower width at the knee. Native Z-up, -Y front, +X anatomical
left. This remains a visual reconstruction proposal, not engineering.
"""
import bpy
import math
from mathutils import Vector

OWNERS = ("left-thigh", "right-thigh", "left-shin", "right-shin")
MID_WIDTH = 0.72


def _smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def _width(owner, t):
    if owner.endswith("-thigh"):
        # Retain the full existing hip seat, taper through the thigh, and hold
        # the compact section through the shared knee.
        if t <= 0.15:
            return 1.0
        return 1.0 - (1.0 - MID_WIDTH) * _smoothstep((t - 0.15) / 0.35)
    # Begin at the same compact knee section, then restore the original width
    # before the unchanged ankle/foot receiving structure.
    if t <= 0.35:
        return MID_WIDTH
    return MID_WIDTH + (1.0 - MID_WIDTH) * _smoothstep((t - 0.35) / 0.40)


def _segment(owner_name):
    side, kind = owner_name.split("-")
    next_name = side + ("-shin" if kind == "thigh" else "-foot")
    return bpy.data.objects[owner_name].matrix_world.translation.copy(), \
        bpy.data.objects[next_name].matrix_world.translation.copy()


def apply():
    bpy.context.view_layer.update()
    changed = []
    for obj in sorted(bpy.data.objects, key=lambda item: item.name):
        if obj.type != "MESH" or not obj.parent or obj.parent.name not in OWNERS:
            continue
        owner = obj.parent.name
        p0, p1 = _segment(owner)
        dy, dz = p1.y - p0.y, p1.z - p0.z
        length2 = dy * dy + dz * dz
        assert length2 > 1e-10, owner
        matrix = obj.matrix_world.copy()
        inverse = matrix.inverted()
        original = [matrix @ vertex.co for vertex in obj.data.vertices]
        # Joint races and captive axles are kept geometrically round/straight:
        # use one section factor for the complete mesh. Long frame members get
        # the continuous taper along their actual hip-knee-ankle centerline.
        joint_part = any(tag in obj.name.lower() for tag in (
            "journal", "retainer rim", "captive axle", "captive cheek",
            "journal keeper bolt"))
        moved = 0
        factors = []
        for vertex, point in zip(obj.data.vertices, original):
            t = max(0.0, min(1.0, ((point.y - p0.y) * dy +
                                  (point.z - p0.z) * dz) / length2))
            section_t = (sum(max(0.0, min(1.0,
                ((q.y - p0.y) * dy + (q.z - p0.z) * dz) / length2))
                for q in original) / len(original)) if joint_part else t
            factor = _width(owner, section_t)
            center_x = p0.x + t * (p1.x - p0.x)
            point.x = center_x + (point.x - center_x) * factor
            vertex.co = inverse @ point
            factors.append(factor)
            moved += factor < 0.999999
        if moved:
            obj.data.update()
            changed.append({
                "name": obj.name,
                "owner": owner,
                "widthFactorMin": round(min(factors), 6),
                "widthFactorMax": round(max(factors), 6),
                "materialNames": [mat.name if mat else None for mat in obj.data.materials],
            })
    return {
        "region": "paired compact thigh/shin frames and receiving housings",
        "changedMeshes": changed,
        "added": [],
        "removed": [],
        "changedNodes": [],
        "status": "bounded visual proposal; discrete articulation and fit review pending",
        "limits": [
            "Existing hip interface is unchanged at the thigh proximal centerline.",
            "Both sides meet at a shared 0.72 transverse width at the knee.",
            "Shin frame restores original width at the unchanged ankle/foot interface.",
            "No body, foot, toe, runtime, era, or powered mesh is edited.",
            "Construction geometry does not certify strength, balance, or continuous clearance.",
        ],
    }
