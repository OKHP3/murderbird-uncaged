"""Portable, procedural-to-glTF appearance materials for the alignment rig.

This module deliberately creates standard image textures and Principled BSDF
materials only. It does not change geometry, rig hierarchy, era visibility, or
write files. Call ``build({})`` after opening the Blender source, then use the
returned ``assign`` function on the appearance meshes before GLB export.

The atlas pattern is an artistic material study, not a measured alloy recipe
or a physically reconstructed corrosion process. Edge coloration is derived
from each mesh's actual boundary/sharp edges; patina placement remains a
procedural surface proposal rather than a baked assembly-cavity simulation.
"""

import hashlib
import math

import bpy
import numpy as np


SIZE = 1024
GRID = 4
CELL = SIZE // GRID
GUTTER = 8
UV_MARGIN = (GUTTER + 1) / CELL
ERAS = ("maker", "mechanic", "advanced")

# Tiles are shared by all materials for an era. Role factors remain visible in
# neutral light, while the atlas gives each family a distinct response.
ROLE_TILE = {
    "plate": 0,
    "shell": 0,
    "head-plate": 1,
    "bearing": 2,
    "frame": 3,
    "inner": 4,
    "edge": 5,
    "recess": 6,
    "optic": 7,
    "repair": 8,
    "bill": 9,
    "talon": 10,
    "head-armor": 11,
    "body-armor": 12,
    "wing-armor": 13,
    "limb-armor": 14,
    "breast-armor": 15,
}
ROLE_BASE = {
    # Maker is dark, blackened warm iron/bronze; warm metal remains localized
    # to edge roles, fasteners, and the fine exposed-scratch response below.
    "plate": (.060, .041, .026),
    "shell": (.060, .041, .026),
    "head-plate": (.076, .050, .030),
    "bearing": (.17, .105, .043),
    "frame": (.050, .045, .032),
    "inner": (.105, .087, .054),
    "edge": (.30, .17, .055),
    "recess": (.022, .026, .023),
    "optic": (.56, .205, .027),
    "repair": (.105, .125, .135),
    "bill": (.090, .082, .062),
    "talon": (.19, .115, .045),
    "body-armor": (.060, .041, .026), "wing-armor": (.055, .038, .025),
    "limb-armor": (.068, .047, .030), "breast-armor": (.060, .041, .026),
    "head-armor": (.076, .050, .030),
}
ROLE_METAL = {
    "plate": .82, "shell": .82, "head-plate": .84, "bearing": .90,
    "frame": .78, "inner": .72, "edge": .90, "recess": .62,
    "optic": .20, "repair": .84, "bill": .86, "talon": .90,
    "head-armor": .84, "body-armor": .82, "wing-armor": .82,
    "limb-armor": .84, "breast-armor": .82,
}
ROLE_ROUGH = {
    "plate": .58, "shell": .57, "head-plate": .51, "bearing": .43,
    "frame": .66, "inner": .62, "edge": .38, "recess": .78,
    "optic": .25, "repair": .55, "bill": .37, "talon": .33,
    "head-armor": .51, "body-armor": .58, "wing-armor": .57,
    "limb-armor": .54, "breast-armor": .58,
}
AGED_BASE = {
    "plate": (.035, .048, .044), "shell": (.035, .048, .044),
    "head-plate": (.041, .055, .050), "bearing": (.082, .060, .036),
    "frame": (.019, .024, .024), "inner": (.028, .038, .036),
    "edge": (.30, .17, .055), "recess": (.009, .014, .014),
    "optic": (.008, .011, .010), "repair": (.070, .089, .092),
    "bill": (.025, .031, .030), "talon": (.13, .087, .039),
    "head-armor": (.042, .056, .050), "body-armor": (.035, .048, .044),
    "wing-armor": (.031, .043, .040), "limb-armor": (.047, .049, .042),
    "breast-armor": (.035, .047, .042),
}
AGED_METAL = {
    "plate": .84, "shell": .84, "head-plate": .85, "bearing": .82,
    "frame": .66, "inner": .48, "edge": .88, "recess": .30,
    "optic": .08, "repair": .82, "bill": .82, "talon": .82,
    "head-armor": .86, "body-armor": .84, "wing-armor": .82,
    "limb-armor": .85, "breast-armor": .84,
}
AGED_ROUGH = {
    "plate": .56, "shell": .56, "head-plate": .55, "bearing": .46,
    "frame": .74, "inner": .69, "edge": .35, "recess": .85,
    "optic": .33, "repair": .64, "bill": .55, "talon": .46,
    "head-armor": .52, "body-armor": .56, "wing-armor": .53,
    "limb-armor": .50, "breast-armor": .54,
}


def _seed(text):
    return int.from_bytes(hashlib.sha256(str(text).encode("utf-8")).digest()[:4], "little")


def _smooth_field(rng, width, height, coarse=12):
    """Small deterministic bilinear value field with no new Python packages."""
    grid = rng.random((coarse + 1, coarse + 1), dtype=np.float32)
    grid[-1, :] = grid[0, :]
    grid[:, -1] = grid[:, 0]
    xs = np.linspace(0, coarse, width, endpoint=False, dtype=np.float32)
    ys = np.linspace(0, coarse, height, endpoint=False, dtype=np.float32)
    x0 = xs.astype(np.int32)
    y0 = ys.astype(np.int32)
    tx = (xs - x0)[None, :]
    ty = (ys - y0)[:, None]
    a = grid[y0[:, None], x0[None, :]]
    b = grid[y0[:, None], (x0 + 1)[None, :]]
    c = grid[(y0 + 1)[:, None], x0[None, :]]
    d = grid[(y0 + 1)[:, None], (x0 + 1)[None, :]]
    top = a * (1 - tx) + b * tx
    bottom = c * (1 - tx) + d * tx
    return top * (1 - ty) + bottom * ty


def _tile_surface(era, role, size=CELL):
    rng = np.random.default_rng(_seed("murderbird-material-v2:" + era + ":" + role))
    broad = _smooth_field(rng, size, size, 9)
    mid = _smooth_field(rng, size, size, 31)
    micro = rng.random((size, size), dtype=np.float32)

    # Physical marks are sparse pits and individually oriented tool scores.
    # No broad/mid-frequency height field: that read as soft dents at scale.
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    resolution_scale = size / CELL
    height = np.zeros((size, size), dtype=np.float32)
    scratch = np.zeros_like(height)
    for _ in range(90):
        cx, cy = rng.uniform(0, size, size=2)
        radius = rng.uniform(.35, .85) * resolution_scale
        pit = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * radius * radius))
        height -= pit.astype(np.float32) * .0024
    for _ in range(45):
        angle = rng.uniform(0, math.tau)
        length = rng.uniform(3, 17) * resolution_scale
        cx, cy = rng.uniform(0, size, size=2)
        dx, dy = math.cos(angle), math.sin(angle)
        along = np.clip((xx - cx) * dx + (yy - cy) * dy, -length / 2, length / 2)
        across = (xx - cx) * -dy + (yy - cy) * dx
        width = rng.uniform(.38, .78) * resolution_scale
        line = np.exp(-.5 * (across / width) ** 2) * (np.abs((xx - cx) * dx + (yy - cy) * dy) <= length / 2)
        scratch = np.maximum(scratch, line.astype(np.float32))
        height -= line.astype(np.float32) * .0012
    # Fine, nonwoven forged relief has varied phase and orientation per atlas
    # family. UV rotations below vary it between individual rigid parts.
    for _ in range(5):
        kx, ky = rng.integers(18, 43, size=2)
        phase = rng.uniform(0, math.tau)
        angle = rng.uniform(0, math.tau)
        u = xx * math.cos(angle) - yy * math.sin(angle)
        v = xx * math.sin(angle) + yy * math.cos(angle)
        height += np.sin((u * kx + v * ky) * math.tau / size + phase).astype(np.float32) * .00022
    height += (micro - .5) * .0003

    # Aged shell gets sparse, broken green deposits over dark bronze. This is
    # intentionally broad/irregular, not a claim that UV space predicts water.
    base = np.asarray(ROLE_BASE[role] if era == "maker" else AGED_BASE[role], dtype=np.float32)
    if role == "optic":
        # Maker and Mechanic retain dark, passive glass; only Advanced gets amber.
        base = np.asarray((.42, .105, .012) if era == "advanced" else (.006, .008, .008), dtype=np.float32)
    aged_shell = role in {"plate", "shell", "head-plate", "inner", "bill", "head-armor", "body-armor", "wing-armor", "limb-armor", "breast-armor"}
    if era != "maker" and aged_shell:
        deposit_field = .08 * broad + .92 * mid
        deposit = np.clip((deposit_field - .62) * 1.2, 0, .22)
        green = np.asarray((.040, .078, .060), dtype=np.float32)
        color = base[None, None, :] * (1 - deposit[..., None]) + green[None, None, :] * deposit[..., None]
    else:
        color = np.broadcast_to(base, (size, size, 3)).copy()

    # Small tonal variation stays subordinate to the modeled plate profile.
    tone = 1 + (broad - .5) * .035 + (mid - .5) * .042 + (micro - .5) * .024
    color *= tone[..., None]
    if era == "maker" and role != "optic":
        # Exposed, fine cut marks catch warmer alloy against blackened metal.
        scraped_alloy = np.asarray((.19, .105, .038), dtype=np.float32)
        color = color * (1 - scratch[..., None] * .14) + scraped_alloy[None, None, :] * (scratch[..., None] * .14)
    else:
        color *= (1 - scratch[..., None] * .095)

    rough_base = ROLE_ROUGH[role] if era == "maker" else AGED_ROUGH[role]
    rough = np.clip(rough_base + (broad - .5) * .008 + (mid - .5) * .018
                    + (micro - .5) * .008 + scratch * .10, .19, .91)
    if era != "maker" and aged_shell:
        rough = np.clip(rough + deposit * .065, .19, .93)
    metal_base = ROLE_METAL[role] if era == "maker" else AGED_METAL[role]
    metal = np.full((size, size), metal_base, dtype=np.float32)
    if era != "maker" and aged_shell:
        metal = metal - deposit * .13
    if role == "optic":
        metal[:] = .16
        rough[:] = .24 # texture drives connected PBR inputs, not socket defaults

    # Convert linear reflectance to sRGB only for the base-color atlas.
    color = np.clip(color, 0, 1)
    srgb = np.where(color <= .0031308, color * 12.92, 1.055 * color ** (1 / 2.4) - .055)
    return srgb.astype(np.float32), rough.astype(np.float32), metal, height.astype(np.float32)


def _new_image(name, rgba, non_color):
    image = bpy.data.images.new(name=name, width=SIZE, height=SIZE, alpha=True, float_buffer=False)
    image.colorspace_settings.name = "Non-Color" if non_color else "sRGB"
    image.pixels.foreach_set(np.asarray(rgba, dtype=np.float32).reshape(-1))
    image.pack()
    image["appearanceSource"] = "deterministic procedural proposal; not scan data"
    return image


def _normal_image(name, height, factor):
    normal = np.ones((height.shape[0], height.shape[1], 4), dtype=np.float32)
    dy = (np.roll(height, -1, axis=0) - np.roll(height, 1, axis=0)) * .5
    dx = (np.roll(height, -1, axis=1) - np.roll(height, 1, axis=1)) * .5
    nx, ny, nz = -dx * factor, -dy * factor, np.ones_like(dx)
    length = np.sqrt(nx * nx + ny * ny + nz * nz)
    normal[..., :3] = np.stack((nx / length * .5 + .5, ny / length * .5 + .5,
                                nz / length * .5 + .5), axis=-1)
    return _new_image(name, normal, True)


def _normal_atlas(name, heights):
    normal = np.ones((SIZE, SIZE, 4), dtype=np.float32)
    for tile in range(16):
        row, col = divmod(tile, GRID)
        y = slice(row * CELL, (row + 1) * CELL)
        x = slice(col * CELL, (col + 1) * CELL)
        height = heights[y, x]
        dy = (np.roll(height, -1, axis=0) - np.roll(height, 1, axis=0)) * .5
        dx = (np.roll(height, -1, axis=1) - np.roll(height, 1, axis=1)) * .5
        nx, ny, nz = -dx * (CELL * .08), -dy * (CELL * .08), np.ones_like(dx)
        length = np.sqrt(nx * nx + ny * ny + nz * nz)
        normal[y, x, :3] = np.stack((nx / length * .5 + .5, ny / length * .5 + .5,
                                     nz / length * .5 + .5), axis=-1)
    return _new_image(name, normal, True)


def _make_atlases():
    roles_by_tile = [None] * 16
    for role, tile in ROLE_TILE.items():
        roles_by_tile[tile] = role
    # Fill unused cells with restrained shell variations, keeping the atlas
    # valid if a downstream author adds a role without assigning a unique tile.
    for index, role in enumerate(roles_by_tile):
        if role is None:
            roles_by_tile[index] = "plate"

    colors, orms = {}, {}
    heights = {}
    for era in ERAS:
        color_map = np.ones((SIZE, SIZE, 4), dtype=np.float32)
        orm_map = np.ones((SIZE, SIZE, 4), dtype=np.float32)
        height_atlas = np.zeros((SIZE, SIZE), dtype=np.float32)
        map_era = era
        for tile, role in enumerate(roles_by_tile):
            color, rough, metal, height = _tile_surface(map_era, role)
            row, col = divmod(tile, GRID)
            sy = slice(row * CELL, (row + 1) * CELL)
            sx = slice(col * CELL, (col + 1) * CELL)
            color_map[sy, sx, :3] = color
            orm_map[sy, sx, :3] = np.stack((np.ones_like(rough), rough, metal), axis=-1)
            height_atlas[sy, sx] = height
        colors[era] = _new_image("appearance-" + era + "-base-color", color_map, False)
        orm_key = "maker" if era == "maker" else "aged"
        if orm_key not in orms:
            orms[orm_key] = _new_image("appearance-" + orm_key + "-roughness-metallic", orm_map, True)
        if era != "maker":
            heights[era] = height_atlas

    normals = _normal_atlas("appearance-shared-forging-normal", heights["advanced"])
    # Allocate a full 1024 head map only to the Advanced hero surfaces. The
    # other 256px role tiles stay compact; total decoded maps remain ~48 MiB.
    hero_rgb, hero_rough, hero_metal, hero_height = _tile_surface("advanced", "head-armor", SIZE)
    hero_color = np.ones((SIZE, SIZE, 4), dtype=np.float32)
    hero_color[..., :3] = hero_rgb
    hero_rm = np.ones_like(hero_color)
    hero_rm[..., :3] = np.stack((np.ones_like(hero_rough), hero_rough, hero_metal), axis=-1)
    hero_maps = {
        "base": _new_image("appearance-advanced-head-hero-base-color", hero_color, False),
        "rm": _new_image("appearance-advanced-head-hero-roughness-metallic", hero_rm, True),
        "normal": _normal_image("appearance-advanced-head-hero-normal", hero_height, SIZE * .08),
    }
    return colors, orms, normals, hero_maps


def _resolve_role(obj, explicit=None):
    if explicit:
        role = str(explicit).lower()
    else:
        role = str(obj.get("role", obj.get("surfaceRole", ""))).lower()
    name = obj.name.lower()
    # Named hardware keeps its declared role. A bill fixing is a bearing,
    # and a dark service inset is a recess, even though both names say bill.
    # Name heuristics apply only to the broad exterior surface itself.
    if role in {"plate", "shell", ""} and ("talon" in name or "claw" in name):
        return "talon"
    if role in {"plate", "shell", ""} and ("bill" in name or "beak" in name):
        return "bill"
    aliases = {"plate": "plate", "shell": "shell", "bearing": "bearing", "frame": "frame",
               "inner": "inner", "edge": "edge", "recess": "recess", "optic": "optic", "repair": "repair"}
    if role in {"plate", "shell", ""}:
        region = str(obj.get("region", "")).lower()
        if not region:
            lineage = []
            parent = obj
            while parent:
                lineage.append(parent.name.lower())
                parent = parent.parent
            if any("head" in part or "cranial" in part for part in lineage):
                region = "head"
            elif any("wing" in part or "mantle" in part for part in lineage):
                region = "wing"
            elif any(any(token in part for token in ("thigh", "shin", "foot", "toe")) for part in lineage):
                region = "leg"
            elif any("breast" in part or "pelvis" in part for part in lineage):
                region = "breast"
            else:
                region = "body"
        family = {"head": "head-armor", "wing": "wing-armor", "shoulder": "wing-armor",
                  "leg": "limb-armor", "limb": "limb-armor", "foot": "limb-armor",
                  "breast": "breast-armor", "body": "body-armor", "neck": "body-armor",
                  "back": "body-armor", "pelvis": "body-armor"}.get(region)
        if family:
            return family
    if role in aliases:
        return role
    for key in aliases:
        if key in name:
            return key
    return "plate" if any(t in name for t in ("armor", "guard", "mantle", "crown", "breast")) else "frame"


def _ensure_uv(obj, role, role_extent, full_image=False):
    mesh = obj.data
    if mesh is None or not mesh.vertices:
        return None
    grid = 1 if full_image else GRID
    tile = 0 if full_image else ROLE_TILE[role]
    row, col = divmod(tile, grid)
    margin = GUTTER / SIZE if full_image else UV_MARGIN
    active = mesh.uv_layers.active
    if active is not None and len(active.data):
        values = np.asarray([tuple(loop.uv) for loop in active.data], dtype=np.float32)
        u0, v0 = col / grid, row / grid
        if (values[:, 0].min() >= u0 + margin * .5 and values[:, 0].max() <= (col + 1) / grid - margin * .5
                and values[:, 1].min() >= v0 + margin * .5 and values[:, 1].max() <= (row + 1) / grid - margin * .5):
            return active
    if mesh.users > 1:
        obj.data = mesh = mesh.copy()
    uv = mesh.uv_layers.get("AppearanceUV") or mesh.uv_layers.new(name="AppearanceUV")
    active = uv
    active.active_render = True
    coords = np.asarray([tuple(vertex.co) for vertex in mesh.vertices], dtype=np.float32)
    mins = coords.min(axis=0)
    spans = coords.max(axis=0) - mins
    axes = np.argsort(spans)[-2:]
    max_span = max(float(role_extent.get(role, max(spans[axes]))), 1e-5)
    usable = 1 - 2 * margin
    # Per-role maximum bounds give consistent metres-per-texel among parts
    # sharing a tile. Slight deterministic offsets reduce obvious repeats on
    # smaller pieces while staying within the tile gutter.
    scale = usable / max_span
    widths = spans[axes] * scale
    room = np.maximum(usable - widths, 0)
    source_part = str(obj.get("appearanceSourcePart", obj.name))
    digest = _seed(source_part)
    turns = digest & 3
    rotated_spans = spans[axes][::-1] if turns % 2 else spans[axes]
    room = np.maximum(usable - rotated_spans * scale, 0)
    offset = np.asarray((room[0] * (((digest >> 2) & 0xffff) / 65535),
                         room[1] * (((digest >> 18) & 0x3fff) / 16383)), dtype=np.float32)
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            co = coords[mesh.loops[li].vertex_index]
            a = co[axes[0]] - mins[axes[0]]
            b = co[axes[1]] - mins[axes[1]]
            if turns == 1:
                a, b = spans[axes[1]] - b, a
            elif turns == 2:
                a, b = spans[axes[0]] - a, spans[axes[1]] - b
            elif turns == 3:
                a, b = b, spans[axes[0]] - a
            uu = margin + offset[0] + (a * scale)
            vv = margin + offset[1] + (b * scale)
            active.data[li].uv = ((col + uu) / grid, (row + vv) / grid)
    return active


def _edge_tint(mesh, role, era):
    """Create portable vertex color: actual boundaries/sharp edges polish."""
    # Keep one unambiguous vertex-color set so the material and glTF COLOR_0
    # use the same data instead of stale source colors becoming COLOR_1+.
    for old_attr in list(mesh.color_attributes):
        mesh.color_attributes.remove(old_attr)
    attr = mesh.color_attributes.new(name="AppearanceTint", type="FLOAT_COLOR", domain="POINT")
    color_index = mesh.color_attributes.find(attr.name)
    mesh.color_attributes.active_color_index = color_index
    mesh.color_attributes.render_color_index = color_index
    adjacency = [[] for _ in mesh.vertices]
    boundary = np.zeros(len(mesh.vertices), dtype=np.float32)
    sharp = np.zeros(len(mesh.vertices), dtype=np.float32)
    for edge in mesh.edges:
        a, b = edge.vertices
        adjacency[a].append(b)
        adjacency[b].append(a)
    # MeshEdge has no linked faces in the RNA API; compute edge incidence from
    # polygons and dihedral angles using adjacent polygon normals.
    edge_faces = {}
    for poly in mesh.polygons:
        verts = list(poly.vertices)
        for i, a in enumerate(verts):
            b = verts[(i + 1) % len(verts)]
            edge_faces.setdefault(tuple(sorted((a, b))), []).append(poly.index)
    for key, faces in edge_faces.items():
        a, b = key
        if len(faces) == 1:
            boundary[a] = boundary[b] = 1
        elif len(faces) > 1:
            normals = [mesh.polygons[index].normal for index in faces]
            if any(normals[i].angle(normals[j]) > .82 for i in range(len(normals)) for j in range(i + 1, len(normals))):
                sharp[a] = sharp[b] = 1
    mask = np.maximum(boundary, sharp * .72)
    # Two-ring falloff makes a real edge read as worn metal instead of a hard
    # one-vertex color stripe; it follows actual mesh topology, not atlas edges.
    falloff = mask.copy()
    for _ in range(2):
        updated = falloff.copy()
        for index, neighbors in enumerate(adjacency):
            if neighbors:
                updated[index] = max(updated[index], .58 * max(falloff[n] for n in neighbors))
        falloff = updated
    if role == "optic" or role == "recess":
        falloff *= .18
    # glTF COLOR_0 is a base-color multiplier. Keep values in [0, 1]: the
    # dark face factor rises to neutral at real edges, while separate edge-role
    # geometry supplies the bright bronze hardware/read.
    colors = np.ones((len(mesh.vertices), 4), dtype=np.float32)
    if era == "maker":
        face = np.asarray((.72, .75, .78), dtype=np.float32)
    else:
        face = np.asarray((.66, .73, .74), dtype=np.float32)
    edge = np.asarray((1.0, .91, .72), dtype=np.float32)
    colors[:, :3] = face[None, :] + falloff[:, None] * (edge - face)[None, :]
    for i, color in enumerate(colors):
        attr.data[i].color = tuple(np.clip(color, .65, 1.0))
    return attr


def build(ctx=None):
    """Create maps/materials and return ``materials``, ``assign``, ``textures``.

    ``assign(obj, era, role=None, variant='primary')`` attaches a material,
    adds role-atlas UVs when the mesh lacks a suitable ``AppearanceUV``, and
    writes topology-derived ``AppearanceTint`` vertex colors. ``materials`` is
    also a callable lookup: ``materials(era, role, variant='primary')``.
    ``ctx`` is accepted for a stable ``build(ctx)`` integration surface; this
    module currently needs no external helpers from it.
    """
    colors, orms, normal, hero_maps = _make_atlases()
    texture_list = list(colors.values()) + list(orms.values()) + [normal] + list(hero_maps.values())
    material_cache = {}
    role_extent = {role: 0.0 for role in ROLE_TILE}
    for obj in bpy.data.objects:
        if obj.type != "MESH" or obj.data is None or not obj.data.vertices:
            continue
        role = _resolve_role(obj)
        coords = np.asarray([tuple(v.co) for v in obj.data.vertices], dtype=np.float32)
        spans = coords.max(axis=0) - coords.min(axis=0)
        role_extent[role] = max(role_extent.get(role, 0.0), float(np.sort(spans)[-1]))
    for role, default in ROLE_TILE.items():
        role_extent[role] = max(role_extent.get(role, 0), .02)

    def get_material(era, role, variant="primary"):
        era = str(era).lower()
        era = "advanced" if era in {"advanced", "builder"} else era
        if era not in ERAS:
            raise ValueError("era must be maker, mechanic, or advanced/builder")
        role = str(role).lower()
        if role not in ROLE_TILE:
            role = "plate"
        variant = str(variant or "primary")
        key = (era, role, variant)
        if key in material_cache:
            return material_cache[key]
        aged = era != "maker"
        atlas_era = era
        orm_era = "maker" if not aged else "aged"
        mat = bpy.data.materials.new(name=f"{era.title()} / {role} / {variant}")
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        bsdf = nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = (1, 1, 1, 1)
        bsdf.inputs["Metallic"].default_value = ROLE_METAL[role]
        bsdf.inputs["Roughness"].default_value = ROLE_ROUGH[role] + (.08 if aged and role in {"plate", "shell", "head-plate", "inner"} else 0)
        color_node = nodes.new("ShaderNodeTexImage")
        color_node.name = "Appearance base color atlas"
        hero_head = era == "advanced" and role == "head-armor"
        color_node.image = colors["mechanic"] if variant == "dark-iris" else hero_maps["base"] if hero_head else colors[atlas_era]
        vertex_node = nodes.new("ShaderNodeVertexColor")
        vertex_node.name = "Appearance edge wear COLOR_0"
        vertex_node.layer_name = "AppearanceTint"
        multiply = nodes.new("ShaderNodeMix")
        multiply.data_type = "RGBA"
        multiply.blend_type = "MULTIPLY"
        next(socket for socket in multiply.inputs if socket.identifier == "Factor_Float").default_value = 1.0
        socket_a = next(socket for socket in multiply.inputs if socket.identifier == "A_Color")
        socket_b = next(socket for socket in multiply.inputs if socket.identifier == "B_Color")
        result_color = next(socket for socket in multiply.outputs if socket.identifier == "Result_Color")
        mat.node_tree.links.new(color_node.outputs["Color"], socket_a)
        mat.node_tree.links.new(vertex_node.outputs["Color"], socket_b)
        mat.node_tree.links.new(result_color, bsdf.inputs["Base Color"])
        orm_node = nodes.new("ShaderNodeTexImage")
        orm_node.name = "Appearance roughness-metallic atlas (no AO bake)"
        orm_node.image = hero_maps["rm"] if hero_head else orms[orm_era]
        split = nodes.new("ShaderNodeSeparateColor")
        mat.node_tree.links.new(orm_node.outputs["Color"], split.inputs["Color"])
        mat.node_tree.links.new(split.outputs["Green"], bsdf.inputs["Roughness"])
        mat.node_tree.links.new(split.outputs["Blue"], bsdf.inputs["Metallic"])
        normal_node = nodes.new("ShaderNodeTexImage")
        normal_node.name = "Appearance tangent normal"
        normal_node.image = hero_maps["normal"] if hero_head else normal
        normal_map = nodes.new("ShaderNodeNormalMap")
        normal_map.inputs["Strength"].default_value = .8
        mat.node_tree.links.new(normal_node.outputs["Color"], normal_map.inputs["Color"])
        mat.node_tree.links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])
        if role == "optic":
            if era == "advanced" and variant != "dark-iris":
                bsdf.inputs["Emission Color"].default_value = (.6, .12, .009, 1)
                bsdf.inputs["Emission Strength"].default_value = .7
                bsdf.inputs["Coat Weight"].default_value = .35
                bsdf.inputs["Coat Roughness"].default_value = .12
        mat["appearanceEra"] = era
        mat["appearanceRole"] = role
        mat["appearanceVariant"] = variant
        mat["pipeline"] = "glTF base color, roughness/metallic atlas, tangent normal, COLOR_0 edge wear"
        mat["limitations"] = "procedural material proposal; no scan, chemistry, ambient-occlusion map, or assembly-cavity bake"
        material_cache[key] = mat
        return mat

    def assign(obj, era, role=None, variant="primary"):
        resolved = _resolve_role(obj, role)
        if obj.get("appearanceOpticSurface") == "dark-iris":
            variant = "dark-iris"
        if obj.type == "MESH" and obj.data is not None:
            era_key = str(era).lower()
            hero_head = era_key in {"advanced", "builder"} and resolved == "head-armor"
            _ensure_uv(obj, resolved, role_extent, full_image=hero_head)
            _edge_tint(obj.data, resolved, "maker" if era == "maker" else "aged")
        mat = get_material(era, resolved, variant)
        if obj.type == "MESH":
            obj.data.materials.clear()
            obj.data.materials.append(mat)
            for poly in obj.data.polygons:
                poly.material_index = 0
        return mat

    return {
        "materials": get_material,
        "assign": assign,
        "textures": texture_list,
        "notes": {
            "maps": "Three 1024x1024 base-color atlases (Maker, Mechanic, Advanced), two roughness/metallic atlases, one shared tangent normal atlas, and three 1024 Advanced head-hero maps; about 48 MiB estimated RGBA mip memory. Occlusion red is constant 1; no AO bake or occlusionTexture is claimed.",
            "surface": "Maker uses dark warm iron/bronze with localized warm hardware and scratch highlights. Aged shell/armor fields stay dark oxidized green-brown/charcoal with metallic alloy response around .82-.86; localized deposits reduce metallicity and raise roughness. Fine pits and oriented tool scores are authored surface proposals. Topology-derived warm edge tint is clamped as a COLOR_0 multiplier.",
            "uv": "Keeps UVs already wholly inside the assigned atlas role tile. Otherwise applies object-dominant continuous projection with per-role metres-per-texel and deterministic offsets seeded from appearanceSourcePart so era clones share UV phase. Advanced head armor receives dedicated full-image maps.",
            "limits": "Patina is a procedural visual proposal, not a mesh-cavity or water-history bake. Atlas projection can distort curved surfaces; preserve authored UVs for hero meshes when suitable. Human material and likeness review remains required.",
            "roles": dict(ROLE_TILE),
        },
    }
