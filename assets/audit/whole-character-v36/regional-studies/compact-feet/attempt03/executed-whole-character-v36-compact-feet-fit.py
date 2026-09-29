"""V36 compact foot fit correction based on a V35 whole-character native.

Reprofiles only foot, toe, and named digit meshes. Toe-root and proximal pivots
stay seated in the existing foot receivers; distal pivots move toward their
proximal axes, with passive links and guards coherently shortened. Hinge-facing guards receive an additional bounded axial relief; the raised arch is omitted. Native
Z-up, -Y front, +X anatomical left. No powered or era-specific geometry.
"""
import math
import bpy
from mathutils import Vector

SIDES = ("left", "right")
DISTAL_PIVOT_SPAN = 0.80
DIGIT_MEMBER_SPAN = 0.80
TALON_SPAN = 0.74
HALLUX_SPAN = 0.62
ARCH_RAISE = 0.0
HINGE_GUARD_SPAN = 0.56
ARCH_MESH_TOKENS = ("metatarsal passive rail", "metatarsus open passive truss", "curved instep guard")


def _matrix_tuple(matrix):
    return tuple(round(float(matrix[r][c]), 10) for r in range(4) for c in range(4))


def _world_bounds(obj):
    points = [obj.matrix_world @ v.co for v in obj.data.vertices]
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]


def _mesh_signature(obj):
    return (tuple(tuple(round(float(c), 10) for c in v.co) for v in obj.data.vertices),
            tuple(tuple(int(i) for i in p.vertices) for p in obj.data.polygons),
            tuple(m.name if m else None for m in obj.data.materials))


def _world_signature(obj):
    return (_matrix_tuple(obj.matrix_world),
            tuple(tuple(round(float(c), 9) for c in (obj.matrix_world @ v.co)) for v in obj.data.vertices),
            tuple(tuple(int(i) for i in p.vertices) for p in obj.data.polygons),
            tuple(m.name if m else None for m in obj.data.materials))


def _side_foot_meshes(side):
    owners = {side + "-foot", side + "-toes"} | {
        f"{side}-digit-{digit}-{part}" for digit in range(1, 4) for part in ("proximal", "distal")
    }
    return [o for o in bpy.data.objects if o.type == "MESH" and o.parent and o.parent.name in owners]


def _role(obj):
    return obj.get("surfaceRole", "")


def apply():
    bpy.context.view_layer.update()
    expected_source = "assets/models/whole-character-v35/attempt-form01/murderbird-whole-character-v35.blend"
    foot_nodes = {f"{side}-foot": bpy.data.objects[f"{side}-foot"] for side in SIDES}
    toe_nodes = {f"{side}-toes": bpy.data.objects[f"{side}-toes"] for side in SIDES}
    digit_nodes = {f"{side}-digit-{d}-{part}": bpy.data.objects[f"{side}-digit-{d}-{part}"]
                   for side in SIDES for d in range(1, 4) for part in ("proximal", "distal")}
    all_nodes = {**foot_nodes, **toe_nodes, **digit_nodes}
    node_before = {name: obj.matrix_world.copy() for name, obj in all_nodes.items()}
    source_meshes = {obj.name: obj for side in SIDES for obj in _side_foot_meshes(side)}
    mesh_before = {name: _world_signature(obj) for name, obj in source_meshes.items()}
    vertex_world_before = {
        name: [obj.matrix_world @ vert.co for vert in obj.data.vertices]
        for name, obj in source_meshes.items()
    }
    contact_before = {side: min(_world_bounds(obj)[2][0] for obj in _side_foot_meshes(side)) for side in SIDES}
    original_pivots = {name: matrix.translation.copy() for name, matrix in node_before.items()}

    # Move distal axes toward their proximal axis in hierarchy order. Toe-root
    # and proximal frames remain fixed at the existing receiving interfaces.
    joint_moves = []
    for side in SIDES:
        for digit in range(1, 4):
            p_name = f"{side}-digit-{digit}-proximal"
            d_name = f"{side}-digit-{digit}-distal"
            proximal = digit_nodes[p_name]
            distal = digit_nodes[d_name]
            old_pivot = original_pivots[d_name]
            prox_pivot = original_pivots[p_name]
            new_y = prox_pivot.y + (old_pivot.y - prox_pivot.y) * DISTAL_PIVOT_SPAN
            target = node_before[d_name].copy()
            target.translation.y = new_y
            distal.matrix_world = target
            joint_moves.append({"node": d_name, "owner": distal.parent.name,
                                "oldWorldXYZ": list(old_pivot),
                                "newWorldXYZ": [old_pivot.x, new_y, old_pivot.z],
                                "parentNode": p_name,
                                "oldAxisSpanM": old_pivot.y - prox_pivot.y,
                                "newAxisSpanM": new_y - prox_pivot.y})
            bpy.context.view_layer.update()

    # Rebuild affected world vertices from the frozen V35 signatures and map
    # them into the new owner transforms. Bearings remain circular and rigid;
    # frames, plate guards, and talons shorten about their actual joint axes.
    arch_members = []
    talon_reprofiles = []
    hallux_reprofiles = []
    for name, obj in source_meshes.items():
        owner = obj.parent.name
        before_points = vertex_world_before[name]
        owner_old = original_pivots.get(owner)
        owner_new = obj.parent.matrix_world.translation.copy()
        inverse_new = obj.matrix_world.inverted()
        is_digit = "-digit-" in owner
        role = _role(obj)
        is_talon = role == "edge" and "tapered claw sheath" in name
        is_hallux = name.endswith("rear hallux sheath v4")
        is_arch = any(token in name.lower() for token in ARCH_MESH_TOKENS)
        if is_digit and role != "bearing":
            assert owner_old is not None, (name, owner)
            for vertex, source_point in zip(obj.data.vertices, before_points):
                point = source_point.copy()
                factor = TALON_SPAN if is_talon else DIGIT_MEMBER_SPAN
                if "dorsal guard" in name.lower():
                    factor *= HINGE_GUARD_SPAN
                point.y = owner_old.y + (source_point.y - owner_old.y) * factor
                point.y += owner_new.y - owner_old.y
                vertex.co = inverse_new @ point
            obj.data.update()
            if is_talon:
                talon_reprofiles.append({"name": name, "owner": owner,
                                         "beforeWorldBounds": _world_bounds(obj),
                                         "foreAftFactor": TALON_SPAN})
        elif is_hallux:
            assert owner_old is not None, (name, owner)
            before_bounds = _world_bounds(obj)
            for vertex, source_point in zip(obj.data.vertices, before_points):
                point = source_point.copy()
                point.y = owner_old.y + (source_point.y - owner_old.y) * HALLUX_SPAN
                vertex.co = inverse_new @ point
            obj.data.update()
            hallux_reprofiles.append({"name": name, "owner": owner,
                                      "beforeWorldBounds": before_bounds,
                                      "afterWorldBounds": _world_bounds(obj),
                                      "foreAftFactor": HALLUX_SPAN})
        elif is_arch:
            # Keep passive truss/instep vertices exactly at source elevation;
            # root attribution tied the prior 22 mm lift to landing contacts.
            arch_members.append({"name": name, "owner": owner,
                                 "raisedVertices": 0, "maximumLiftM": 0.0})

    bpy.context.view_layer.update()
    contact_after = {side: min(_world_bounds(obj)[2][0] for obj in _side_foot_meshes(side)) for side in SIDES}
    ankle_unchanged = all(_matrix_tuple(foot_nodes[name].matrix_world) == _matrix_tuple(node_before[name])
                          for name in foot_nodes)
    roots_unchanged = all(_matrix_tuple(toe_nodes[name].matrix_world) == _matrix_tuple(node_before[name])
                          for name in toe_nodes)
    proximal_unchanged = all(_matrix_tuple(digit_nodes[name].matrix_world) == _matrix_tuple(node_before[name])
                             for name in digit_nodes if name.endswith("-proximal"))
    assert ankle_unchanged and roots_unchanged and proximal_unchanged
    assert all(abs(contact_before[s] - contact_after[s]) < 1e-7 for s in SIDES), (contact_before, contact_after)
    assert len(joint_moves) == 6 and len(arch_members) == 8 and len(talon_reprofiles) == 6 and len(hallux_reprofiles) == 2

    # Local projected endpoint evidence: each shortened proximal load member
    # still overlaps the relocated distal bearing envelope at the receiving lap.
    endpoint_checks = []
    for side in SIDES:
        for digit in range(1, 4):
            p_owner = f"{side}-digit-{digit}-proximal"
            d_owner = f"{side}-digit-{digit}-distal"
            p_link = next(o for o in source_meshes.values() if o.parent.name == p_owner
                          and o.name.startswith("Digit inner link"))
            d_bearing = next(o for o in source_meshes.values() if o.parent.name == d_owner
                             and o.get("surfaceRole") == "bearing" and "captive toe-bearing flanges" in o.name)
            p_bounds = _world_bounds(p_link)[1]
            d_bounds = _world_bounds(d_bearing)[1]
            y_overlap = min(p_bounds[1], d_bounds[1]) - max(p_bounds[0], d_bounds[0])
            assert y_overlap > 0.0, (p_link.name, d_bearing.name, y_overlap)
            endpoint_checks.append({"proximalFrame": p_link.name, "distalBearing": d_bearing.name,
                                    "proximalFrameWorldYBoundsM": p_bounds,
                                    "distalBearingWorldYBoundsM": d_bounds,
                                    "projectedYOverlapM": y_overlap,
                                    "interpretation": "bounding-interval overlap only; not a full surface-seat or clearance proof"})

    changed_nodes = [name for name, matrix in node_before.items()
                     if _matrix_tuple(all_nodes[name].matrix_world) != _matrix_tuple(matrix)]
    changed_meshes = []
    for name, obj in source_meshes.items():
        if _world_signature(obj) != mesh_before[name]:
            changed_meshes.append({"name": name, "owner": obj.parent.name,
                                   "vertices": len(obj.data.vertices), "polygons": len(obj.data.polygons),
                                   "surfaceRole": _role(obj),
                                   "worldPlacementChanged": _matrix_tuple(obj.matrix_world) != mesh_before[name][0]})
    result = {
        "source": expected_source,
        "region": "paired compact foot, toe, and digit assemblies",
        "changedNodes": changed_nodes,
        "changedFootMeshes": changed_meshes,
        "added": [],
        "removed": [],
        "rationale": "Retains the compact fore-aft foot profile, six distal pivot relocations, and shortened talons/hallux from attempt02. Removes attempt02’s 22 mm arch lift implicated in landing shin contacts. Applies additional axial shortening only to existing dorsal guards that meet moved toe hinges; no bearing geometry or pivot changes.",
        "numericInvariants": {
            "anklePivotsWorldMatricesUnchanged": ankle_unchanged,
            "toeRootWorldMatricesUnchanged": roots_unchanged,
            "proximalDigitWorldMatricesUnchanged": proximal_unchanged,
            "anklePivotWorldXYZ": {name: list(foot_nodes[name].matrix_world.translation) for name in foot_nodes},
            "lowestFootRegionZBeforeAfterM": {side: [contact_before[side], contact_after[side]] for side in SIDES},
            "distalPivotSpanFactor": DISTAL_PIVOT_SPAN,
            "digitMemberForeAftFactor": DIGIT_MEMBER_SPAN,
            "forwardTalonForeAftFactor": TALON_SPAN,
            "rearHalluxForeAftFactor": HALLUX_SPAN,
            "maximumDorsalArchLiftM": ARCH_RAISE,
            "hingeFacingGuardAdditionalSpanFactor": HINGE_GUARD_SPAN,
        },
        "distalJointMoves": joint_moves,
        "digitEndpointChecks": endpoint_checks,
        "archMembers": arch_members,
        "talonReprofiles": talon_reprofiles,
        "halluxReprofiles": hallux_reprofiles,
        "scopeLimitations": [
            "Rest-shape construction study only; no pose sweep, continuous clearance, force, balance, or engineering validation.",
            "Foot and digit meshes/pivots are reconstructed geometry; owner likeness acceptance remains pending.",
            "Endpoint checks are projected bounds overlaps, not full 3D surface attachment or bearing-fit proofs.",
        ],
    }
    return result
