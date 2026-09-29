"""V36 compact arched foot reconstruction study for a V35 whole-character native.

Reprofiles only left/right foot, toes, and named digit rig owners. The ankle
pivots and vertical ground-contact coordinates are preserved. Passive geometry
only; all original materials and Maker/Mechanic/Builder eligibility remain.
"""
import math
import bpy
from mathutils import Vector

SIDES = ("left", "right")
TOE_ROOT_SHIFT = 0.030
PROXIMAL_SPAN = 0.90
DISTAL_SPAN = 0.80
DIGIT_FAN = 1.08
TALON_SPAN = 0.74
ARCH_RAISE = 0.022
ARCH_MESH_TOKENS = ("metatarsal passive rail", "metatarsus open passive truss", "curved instep guard")


def _matrix_tuple(matrix):
    return tuple(round(float(matrix[r][c]), 10) for r in range(4) for c in range(4))


def _world_bounds(obj):
    points = [obj.matrix_world @ v.co for v in obj.data.vertices]
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]


def _mesh_signature(obj):
    return (tuple(tuple(round(float(c), 10) for c in v.co) for v in obj.data.vertices),
            tuple(tuple(int(i) for i in p.vertices) for p in obj.data.polygons))


def _side_foot_meshes(side):
    owners = {side + "-foot", side + "-toes"} | {
        f"{side}-digit-{digit}-{part}" for digit in range(1, 4) for part in ("proximal", "distal")
    }
    return [o for o in bpy.data.objects if o.type == "MESH" and o.parent and o.parent.name in owners]


def _add_arched_pad(side, foot, template):
    """Add one closed, broad passive pad under the short arched metatarsus."""
    # Coordinates are in world metres around the unshifted ankle pivot. The
    # ellipse rings make a continuous formed volume, broadest at midfoot.
    stations = [
        (-0.205, 0.040, 0.010, 0.083),
        (-0.170, 0.071, 0.008, 0.118),
        (-0.120, 0.094, 0.007, 0.151),
        (-0.060, 0.102, 0.007, 0.172),
        ( 0.000, 0.088, 0.008, 0.153),
        ( 0.055, 0.056, 0.011, 0.108),
    ]
    count = 24
    center_x = foot.matrix_world.translation.x
    world_vertices = []
    faces = []
    for y, width, floor, crown in stations:
        center_z = (floor + crown) * 0.5
        radius_z = (crown - floor) * 0.5
        for k in range(count):
            angle = math.tau * k / count
            world_vertices.append(Vector((center_x + width * math.cos(angle), y,
                                          center_z + radius_z * math.sin(angle))))
    for j in range(len(stations) - 1):
        for k in range(count):
            a = j * count + k
            b = j * count + (k + 1) % count
            faces.append((a, b, b + count, a + count))
    faces.append(tuple(reversed(range(count))))
    last = (len(stations) - 1) * count
    faces.append(tuple(last + k for k in range(count)))

    name = f"V36 {side} compact arched metatarsal pad"
    mesh = bpy.data.meshes.new(name + " finite mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = foot
    obj.matrix_basis = __import__("mathutils").Matrix.Identity(4)
    obj.matrix_parent_inverse = __import__("mathutils").Matrix.Identity(4)
    bpy.context.view_layer.update()
    inv = obj.matrix_world.inverted()
    mesh.from_pydata([inv @ p for p in world_vertices], [], faces)
    mesh.update()
    for material in template.data.materials:
        mesh.materials.append(material)
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    for key, value in template.items():
        obj[key] = value
    obj["region"] = "foot"
    obj["surfaceRole"] = "frame"
    obj["constructionOwner"] = foot.name
    obj["constructionClass"] = "inherited-passive"
    obj["articulatesAcrossJoint"] = False
    obj["proposal"] = True
    obj["compactFootRevision"] = "V36 broad arched metatarsal pad"
    obj["constructionDescription"] = "Closed passive formed pad linking the ankle arch to the compact toe-root cluster; no powered or era-specific function."
    obj["exteriorEras"] = "maker,mechanic,builder"
    return obj


def apply():
    bpy.context.view_layer.update()
    expected_source = "assets/models/whole-character-v35/attempt-form01/murderbird-whole-character-v35.blend"
    foot_nodes = {f"{side}-foot": bpy.data.objects[f"{side}-foot"] for side in SIDES}
    toe_nodes = {f"{side}-toes": bpy.data.objects[f"{side}-toes"] for side in SIDES}
    digit_nodes = {f"{side}-digit-{d}-{part}": bpy.data.objects[f"{side}-digit-{d}-{part}"]
                   for side in SIDES for d in range(1, 4) for part in ("proximal", "distal")}
    node_before = {n: _matrix_tuple(o.matrix_world) for n, o in {**foot_nodes, **toe_nodes, **digit_nodes}.items()}
    contact_before = {side: min(_world_bounds(obj)[2][0] for obj in _side_foot_meshes(side)) for side in SIDES}
    foot_meshes_before = {obj.name: _mesh_signature(obj) for side in SIDES for obj in _side_foot_meshes(side)}

    # Keep the ankle receiver fixed. Shift the toe-root pivot modestly aft,
    # then shorten each phalanx center-to-center while retaining its rotation.
    # Lateral fan increases gently to keep the three forward digits distinct.
    for side in SIDES:
        foot = foot_nodes[side + "-foot"]
        toes = toe_nodes[side + "-toes"]
        toes_world = toes.matrix_world.copy()
        toes_world.translation.y += TOE_ROOT_SHIFT
        toes.matrix_world = toes_world
        root = toes.matrix_world.translation.copy()
        center_x = foot.matrix_world.translation.x
        for digit in range(1, 4):
            proximal = digit_nodes[f"{side}-digit-{digit}-proximal"]
            p = proximal.matrix_world.copy()
            p.translation.y = root.y + (p.translation.y - node_before[f"{side}-digit-{digit}-proximal"][7]) * PROXIMAL_SPAN
            p.translation.x = center_x + (p.translation.x - center_x) * DIGIT_FAN
            proximal.matrix_world = p
            distal = digit_nodes[f"{side}-digit-{digit}-distal"]
            d = distal.matrix_world.copy()
            old_prox_y = node_before[f"{side}-digit-{digit}-proximal"][7]
            old_dist_y = node_before[f"{side}-digit-{digit}-distal"][7]
            d.translation.y = p.translation.y + (old_dist_y - old_prox_y) * DISTAL_SPAN
            d.translation.x = center_x + (d.translation.x - center_x) * DIGIT_FAN
            distal.matrix_world = d
        bpy.context.view_layer.update()

    # Lift only the exposed foot-owned dorsal rails/truss along a shallow arch.
    # Their ankle ends and toe-seat ends fade to the original height.
    arch_deltas = []
    for side in SIDES:
        for obj in _side_foot_meshes(side):
            if not any(token in obj.name.lower() for token in ARCH_MESH_TOKENS):
                continue
            inv = obj.matrix_world.inverted()
            moved = 0
            for vertex in obj.data.vertices:
                point = obj.matrix_world @ vertex.co
                t = (point.y + 0.168) / 0.234
                if 0.0 < t < 1.0:
                    point.z += ARCH_RAISE * math.sin(math.pi * t)
                    vertex.co = inv @ point
                    moved += 1
            obj.data.update()
            arch_deltas.append({"name": obj.name, "owner": obj.parent.name, "raisedVertices": moved,
                                "maxRaiseM": ARCH_RAISE})

    # Shorten the exposed curved talon sheaths around each distal joint. The
    # shortening follows each named rigid digit owner and leaves Z contact intact.
    talon_changes = []
    for side in SIDES:
        for digit in range(1, 4):
            owner = digit_nodes[f"{side}-digit-{digit}-distal"]
            name = f"{side} digit {digit} tapered claw sheath"
            obj = bpy.data.objects[name]
            pivot = owner.matrix_world.translation.copy()
            inv = obj.matrix_world.inverted()
            bounds_before = _world_bounds(obj)
            for vertex in obj.data.vertices:
                point = obj.matrix_world @ vertex.co
                point.y = pivot.y + (point.y - pivot.y) * TALON_SPAN
                vertex.co = inv @ point
            obj.data.update()
            talon_changes.append({"name": name, "owner": owner.name,
                                  "beforeForeAftM": bounds_before[1][1] - bounds_before[1][0],
                                  "afterForeAftM": _world_bounds(obj)[1][1] - _world_bounds(obj)[1][0],
                                  "foreAftScale": TALON_SPAN})

    added = []
    for side in SIDES:
        template = bpy.data.objects[f"{side} curved instep guard"]
        added.append(_add_arched_pad(side, foot_nodes[side + "-foot"], template))
    bpy.context.view_layer.update()

    contact_after = {}
    for side in SIDES:
        contact_after[side] = min(_world_bounds(obj)[2][0] for obj in _side_foot_meshes(side))
    ankle_nodes_unchanged = all(_matrix_tuple(foot_nodes[name].matrix_world) == node_before[name] for name in foot_nodes)
    assert ankle_nodes_unchanged, "ankle pivots must remain fixed"
    assert all(abs(contact_before[s] - contact_after[s]) < 1e-7 for s in SIDES), (contact_before, contact_after)
    assert len(arch_deltas) == 8, len(arch_deltas)
    assert len(talon_changes) == 6, len(talon_changes)

    changed_foot_meshes = []
    for side in SIDES:
        for obj in _side_foot_meshes(side):
            if obj.name not in foot_meshes_before or _mesh_signature(obj) != foot_meshes_before[obj.name]:
                changed_foot_meshes.append({"name": obj.name, "owner": obj.parent.name,
                                            "vertices": len(obj.data.vertices), "polygons": len(obj.data.polygons),
                                            "added": obj.name not in foot_meshes_before})
    changed_nodes = [name for name, before in node_before.items()
                     if _matrix_tuple(bpy.data.objects[name].matrix_world) != before]
    result = {
        "source": expected_source,
        "region": "paired compact feet, metatarsal arch, and articulated digit assemblies",
        "changedNodes": changed_nodes,
        "changedFootMeshes": changed_foot_meshes,
        "added": [obj.name for obj in added],
        "removed": [],
        "rationale": "The owner reference shows a compact, broad grounded forefoot, visible arch, and short curved talons. The V35 rails and digit chain read too long and flat. This study shortens the digit chain coherently, slightly fans the digits, raises the existing passive dorsal rails into an arch, and adds one closed passive metatarsal pad per foot.",
        "numericInvariants": {
            "anklePivotsWorldMatricesUnchanged": ankle_nodes_unchanged,
            "anklePivotWorldXYZ": {name: list(foot_nodes[name].matrix_world.translation) for name in foot_nodes},
            "lowestFootRegionZBeforeAfterM": {side: [contact_before[side], contact_after[side]] for side in SIDES},
            "toeRootAftShiftM": TOE_ROOT_SHIFT,
            "proximalDigitSpanFactor": PROXIMAL_SPAN,
            "distalDigitSpanFactor": DISTAL_SPAN,
            "digitLateralFanFactor": DIGIT_FAN,
            "talonForeAftFactor": TALON_SPAN,
            "maximumDorsalArchLiftM": ARCH_RAISE,
        },
        "archMembers": arch_deltas,
        "talonReprofiles": talon_changes,
        "scopeLimitations": [
            "Rest-shape construction study only; no pose sweep, continuous clearance, force, balance, or engineering validation.",
            "Foot and digit meshes/pivots are reconstructed geometry; owner likeness acceptance remains pending.",
            "The image does not establish hidden toe joints, load paths, material thickness, or exact dimensions.",
        ],
    }
    return result
