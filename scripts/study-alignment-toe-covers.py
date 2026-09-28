#!/usr/bin/env python3
"""Create an isolated neutral toe-cover study from the frozen Alignment v6 scene."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/models/uncaged-alignment-v6/murderbird-alignment-v6.blend"
OUT_DIR = ROOT / "assets/models/uncaged-toe-cover-study-v1"
AUDIT_DIR = ROOT / "assets/audit/toe-cover-study-v1"
OUTPUT_BLEND = OUT_DIR / "murderbird-toe-cover-study-v1-refined.blend"
RECEIPT = AUDIT_DIR / "study-receipt-refined.json"
VIEWS = [
    {"name": "feet-three-quarter", "location": [-4.0, -6.0, 1.1], "target": [0.0, -0.17, 0.16], "orthographicScale": 1.0},
    {"name": "feet-low-three-quarter", "location": [-4.0, -6.0, -0.25], "target": [0.0, -0.20, 0.035], "orthographicScale": 0.9},
]
RENDER_RESOLUTION = [1200, 1200]
ERA = "maker,mechanic,builder"
ROLE = "plate"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def mat4(o):
    return [round(float(v), 9) for row in o.matrix_world for v in row]


def object_snapshot():
    result = {}
    for o in bpy.data.objects:
        props = {k: o[k] for k in o.keys() if k != "_RNA_UI"}
        item = {
            "type": o.type,
            "parent": o.parent.name if o.parent else None,
            "world": mat4(o),
            "location": [round(float(v), 9) for v in o.location],
            "rotation": [round(float(v), 9) for v in o.rotation_euler],
            "scale": [round(float(v), 9) for v in o.scale],
            "parentInverse": [round(float(v), 9) for row in o.matrix_parent_inverse for v in row],
            "props": props,
        }
        if o.type == "MESH":
            mesh = o.data
            topology = {
                "verts": [[round(float(c), 9) for c in v.co] for v in mesh.vertices],
                "edges": [list(e.vertices) for e in mesh.edges],
                "faces": [[list(p.vertices), p.material_index, p.use_smooth] for p in mesh.polygons],
                "materials": [m.name if m else None for m in mesh.materials],
            }
            item["mesh"] = hashlib.sha256(json.dumps(topology, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            item["modifiers"] = [(m.name, m.type) for m in o.modifiers]
        result[o.name] = item
    return result


def configure_camera(view):
    scene = bpy.context.scene
    cam_data = bpy.data.cameras.new("study-camera-temporary")
    cam = bpy.data.objects.new("study-camera-temporary", cam_data)
    scene.collection.objects.link(cam)
    cam.location = view["location"]
    direction = Vector(view["target"]) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = view["orthographicScale"]
    scene.camera = cam
    scene.render.resolution_x, scene.render.resolution_y = RENDER_RESOLUTION
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.studio_light = "paint.sl"
    scene.display.shading.color_type = "SINGLE"
    scene.display.shading.single_color = (0.58, 0.60, 0.62)
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = True
    scene.display.shading.cavity_type = "WORLD"
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "Medium High Contrast"
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    return cam


def render_to(path: Path, view):
    cam = configure_camera(view)
    bpy.context.scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    bpy.context.scene.camera = None
    cam_data = cam.data
    bpy.data.objects.remove(cam, do_unlink=True)
    bpy.data.cameras.remove(cam_data)


def create_cover(name, source, owner, side, digit, segment):
    # Measure the unchanged frame mesh in pivot-local coordinates. Verify the
    # source is identity-local to its owner before building the surface BVH.
    inv = owner.matrix_world.inverted()
    source_in_owner = inv @ source.matrix_world
    if max(abs(source_in_owner[r][c] - Matrix.Identity(4)[r][c]) for r in range(4) for c in range(4)) > 1e-8:
        raise RuntimeError(f"Frame mesh is not identity-local to owner pivot: {source.name}")
    points = [source_in_owner @ v.co for v in source.data.vertices]
    xmin, xmax = min(p.x for p in points), max(p.x for p in points)
    ymin, ymax = min(p.y for p in points), max(p.y for p in points)
    ztop = max(p.z for p in points)
    width = xmax - xmin
    length = ymax - ymin

    # Stop short of both rotary interfaces and the distal talon sheath. The
    # opening at y=0 keeps the proximal bearing visible; the opposite gap is
    # deliberately generous because the downstream claw assembly overlaps it.
    xhalf = width * 0.36
    y0 = ymin + length * 0.24
    y1 = ymax - length * 0.19
    # Taper each end, giving a broad, low armor face without ornamental detail.
    stations = [
        (y0, 0.56),
        (y0 + (y1 - y0) * 0.12, 0.90),
        (y0 + (y1 - y0) * 0.50, 1.00),
        (y0 + (y1 - y0) * 0.88, 0.90),
        (y1, 0.56),
    ]
    thickness = min(0.0045, width * 0.11)
    # Raycast the original segment in pivot-local space so the cover underside
    # follows the link crown instead of hovering above its curved surface.
    bvh = BVHTree.FromPolygons(
        [v.co.copy() for v in source.data.vertices],
        [tuple(p.vertices) for p in source.data.polygons],
        all_triangles=False,
    )
    def surface_z(x, y):
        hit, _normal, _index, _distance = bvh.ray_cast(
            Vector((x, y, ztop + 0.08)), Vector((0, 0, -1)), 0.20
        )
        return hit.z if hit else ztop - 0.0015
    # Extruded chamfered plate: broad dorsal face, conforming underside, thin edge.
    outline = []
    for y, factor in stations:
        outline.append((-xhalf * factor, y))
    for y, factor in reversed(stations):
        outline.append((xhalf * factor, y))
    lower = [(x, y, surface_z(x, y) + 0.0005) for x, y in outline]
    upper = [(x * 0.985, y, z + thickness) for x, y, z in lower]
    verts = lower + upper
    n = len(outline)
    faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, j + n, i + n))

    mesh = bpy.data.meshes.new(f"{name}-mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = owner
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.location = (0, 0, 0)
    obj.rotation_euler = (0, 0, 0)
    obj.scale = (1, 1, 1)
    for polygon in mesh.polygons:
        polygon.use_smooth = False
    bevel = obj.modifiers.new("small machined edge radius", "BEVEL")
    bevel.width = min(0.0025, width * 0.055, (y1-y0) * 0.025)
    bevel.segments = 2
    obj["region"] = "foot"
    obj["surfaceRole"] = ROLE
    obj["exteriorEras"] = ERA
    obj["constructionClass"] = "proposed-passive"
    obj["proposal"] = True
    obj["studyVersion"] = "toe-cover-study-v1"
    obj["ownerPivot"] = owner.name
    obj["coveredFrame"] = source.name
    obj["sourceReference"] = "candidate-03-unified-master-and-maker-clean"
    obj["digit"] = f"{side}-digit-{digit}"
    obj["segment"] = segment
    return obj, {
        "name": name,
        "parent": owner.name,
        "region": obj["region"],
        "role": obj["surfaceRole"],
        "eras": ERA.split(","),
        "class": obj["constructionClass"],
        "digit": obj["digit"],
        "segment": segment,
        "frame": source.name,
        "dimensionsLocal": [round(width * .72, 6), round(y1-y0, 6), round(thickness, 6)],
        "hingeGapAtParent": round(abs(ymax-y1), 6),
        "hingeGapAtDistalEnd": round(abs(y0-ymin), 6),
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    outputs = [OUTPUT_BLEND, RECEIPT] + [AUDIT_DIR / f"{v['name']}-{phase}-refined.png" for v in VIEWS for phase in ("before", "after")]
    existing_outputs = [str(p) for p in outputs if p.exists()]
    if existing_outputs:
        raise RuntimeError("Refusing to overwrite existing study outputs: " + ", ".join(existing_outputs))
    if not SOURCE.is_file():
        raise RuntimeError(f"Frozen source missing: {SOURCE}")
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    source_hash = sha(SOURCE)
    if source_hash != "5a7a51941423dd0efcb48b9641b7a49597dad117e218ccb4e94f26315c5e9ded":
        raise RuntimeError("Frozen v6 Blender source hash differs from authorized input")
    before_state = object_snapshot()
    before_images = {}
    for view in VIEWS:
        path = AUDIT_DIR / f"{view['name']}-before-refined.png"
        render_to(path, view)
        before_images[view["name"]] = path

    additions = []
    for side in ("left", "right"):
        for digit in (1, 2, 3):
            for segment in ("proximal", "distal"):
                owner = bpy.data.objects.get(f"{side}-digit-{digit}-{segment}")
                source = next((o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("Digit inner link") and o.parent == owner), None)
                if owner is None or source is None:
                    raise RuntimeError(f"Missing unchanged owner/frame: {side} digit {digit} {segment}")
                name = f"{side}-digit-{digit}-{segment}-dorsal-cover-study-v1"
                if bpy.data.objects.get(name):
                    raise RuntimeError(f"Refusing to overwrite existing study object: {name}")
                obj, record = create_cover(name, source, owner, side, digit, segment)
                additions.append(record)

    after_state = object_snapshot()
    if {name: after_state.get(name) for name in before_state} != before_state:
        raise RuntimeError("Retained objects, mesh topology/materials, parent links or transforms changed")
    added_names = {item["name"] for item in additions}
    current_names = set(after_state)
    original_names = set(before_state)
    if current_names != original_names | added_names:
        raise RuntimeError("Object change set does not equal the exact 12-cover allowlist")
    if len(additions) != 12 or len(set(item["name"] for item in additions)) != 12:
        raise RuntimeError("Unexpected cover count")

    after_images = {}
    for view in VIEWS:
        path = AUDIT_DIR / f"{view['name']}-after-refined.png"
        render_to(path, view)
        after_images[view["name"]] = path
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
    bpy.ops.wm.open_mainfile(filepath=str(OUTPUT_BLEND))
    reloaded_state = object_snapshot()
    if {name: reloaded_state.get(name) for name in before_state} != before_state:
        raise RuntimeError("Saved native changed a retained mesh/object after reload")
    if set(reloaded_state) != set(before_state) | added_names:
        raise RuntimeError("Saved native does not contain the exact object allowlist")
    for item in additions:
        obj = bpy.data.objects[item["name"]]
        if obj.parent.name != item["parent"] or obj.get("region") != "foot" or obj.get("surfaceRole") != "plate" or obj.get("exteriorEras") != ERA:
            raise RuntimeError(f"Saved proposal metadata mismatch: {item['name']}")

    script_hash = sha(Path(__file__).resolve())
    record = {
        "status": "unaccepted neutral geometry proposal for owner review",
        "source": {
            "blend": SOURCE.relative_to(ROOT).as_posix(),
            "blendSha256": source_hash,
            "glb": "assets/models/uncaged-alignment-v6/murderbird-alignment-v6.glb",
            "glbSha256": "ce35024adda89681a0f37e7018e2563a74af67cd06558a887222df87b78a87fe",
        },
        "references": [
            {"path":"assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png", "sha256":sha(ROOT / "assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png")},
            {"path":"assets/img/library/murderbird-unified-maker-clean-candidate-2026-09-06.png", "sha256":sha(ROOT / "assets/img/library/murderbird-unified-maker-clean-candidate-2026-09-06.png")},
        ],
        "scope": "Twelve shallow dorsal plates attached to existing proximal/distal toe pivots. No frame, hinge, claw, instep, limb or pivot edits; no runtime export.",
        "era": "passive construction proposal tagged for maker, mechanic and builder exteriors; acceptance and fit per era unknown",
        "role": "plate",
        "exactAdditionAllowlist": sorted(added_names),
        "additions": additions,
        "retainedObjectCount": len(original_names),
        "retainedIntegrity": "PASS after saved-file reload: every original object parent/local/world transform/custom property retained; every original mesh topology, vertex position, face/material index, smoothing flag and material slot retained",
        "addedObjectDelta": sorted(current_names - original_names),
        "render": {
            "resolution": RENDER_RESOLUTION,
            "views": [
                {"name":v["name"], "location":v["location"], "target":v["target"], "orthographicScale":v["orthographicScale"],
                 "before":{"path":before_images[v["name"]].relative_to(ROOT).as_posix(), "sha256":sha(before_images[v["name"]])},
                 "after":{"path":after_images[v["name"]].relative_to(ROOT).as_posix(), "sha256":sha(after_images[v["name"]])}}
                for v in VIEWS
            ],
            "engine": "Blender Workbench studio; single neutral studio shade; matched camera pairs",
        },
        "files": {
            "studyBlend": OUTPUT_BLEND.relative_to(ROOT).as_posix(),
            "studyBlendSha256": sha(OUTPUT_BLEND),
            "builderScript": Path(__file__).resolve().relative_to(ROOT).as_posix(),
            "builderScriptSha256": script_hash,
        },
        "limitations": [
            "No posed hinge, collision, flex, ground-contact or mechanical clearance review was performed.",
            "Reference images are perspective illustrations and do not establish dimensions.",
            "Era assignment records proposed passive role only; owner acceptance is pending.",
        ],
    }
    RECEIPT.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"status":"PASS", "sourceSha256":source_hash, "scriptSha256":script_hash, "blendSha256":sha(OUTPUT_BLEND), "added":len(additions), "retainedIntegrity":"PASS after reload"}, indent=2))


if __name__ == "__main__":
    main()
