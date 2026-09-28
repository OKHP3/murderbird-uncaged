"""Build and render one isolated V15 breast proposal from pinned V14 a11."""
from pathlib import Path
import datetime
import hashlib
import json
import shutil
import sys
import argparse

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "assets/models/uncaged-orbital-crown-v14/attempt-11/murderbird-orbital-crown-v14.blend"
BASE_SHA = "93cf7908906dab0746ec42ace88867b3c52cb0988c284cf6ae468eb2cce17a5a"
MODULE = ROOT / "scripts/regions/whole-character-v15-breast.py"
parser = argparse.ArgumentParser()
parser.add_argument("--attempt", default="01")
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
assert args.attempt in {"01", "02"}
OUT = ROOT / f"assets/audit/whole-character-v15/breast-study-{args.attempt}"
NATIVE = OUT / f"murderbird-whole-character-v15-breast-study-{args.attempt}.blend"
REFERENCE = ROOT / "context/threads/assets/murderbird-owner-likeness-rejection-2026-09-28/2-Pasted-Image-2.jpg"
CANDIDATE03 = ROOT / "assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png"
CURRENT = ROOT / "assets/audit/uncaged-orbital-crown-v14/attempt-11/after-reference-angle.png"


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    assert BASE.is_file() and sha(BASE) == BASE_SHA, "Pinned a11 native hash mismatch"
    assert MODULE.is_file() and REFERENCE.is_file() and CANDIDATE03.is_file() and CURRENT.is_file()
    assert not OUT.exists(), "Preserve prior study; choose a new numbered output"
    OUT.mkdir(parents=True)
    shutil.copy2(Path(__file__).resolve(), OUT / "executed-build-study.py")
    shutil.copy2(MODULE, OUT / "executed-breast-module.py")

    bpy.ops.wm.open_mainfile(filepath=str(BASE))
    scene = bpy.context.scene
    scene.frame_set(1)
    bpy.context.view_layer.update()
    helpers = __import__("runpy").run_path(
        str(ROOT / "scripts/build-uncaged-alignment-v7.py"),
        run_name="v15_breast_snapshot_helpers")
    snapshot = helpers["scene_snapshot"]
    material_signature = helpers["material_signature"]
    before = snapshot()
    materials_before = {mat.name: material_signature(mat) for mat in bpy.data.materials}
    old_mesh_names = set(before["meshes"])
    old_curve_names = set(before["curves"])
    old_pivot_names = set(before["empties"])
    assert len(old_pivot_names) == 52
    assert "breastplate" in before["empties"] and "body" in before["empties"]

    views = [
        ("three-quarter", (-6, -3.5, 2.75), (0, -.08, 1.02), 2.5),
        ("front", (0, -7, 1.65), (0, -.08, 1.02), 2.5),
        ("side", (-7, 0, 1.08), (0, -.10, 1.02), 2.5),
        ("breast-close", (-2, -6, 1.50), (0, -.14, 1.10), 1.20),
    ]
    render_state = {
        "engine": scene.render.engine,
        "filepath": scene.render.filepath,
        "resolution_x": scene.render.resolution_x,
        "resolution_y": scene.render.resolution_y,
        "resolution_percentage": scene.render.resolution_percentage,
        "file_format": scene.render.image_settings.file_format,
        "film_transparent": scene.render.film_transparent,
        "world_color": tuple(scene.world.color) if scene.world else None,
        "camera": scene.camera,
    }
    shading = scene.display.shading
    shading_state = {key: getattr(shading, key) for key in (
        "light", "studio_light", "color_type", "show_shadows", "show_cavity",
        "cavity_type", "curvature_ridge_factor", "curvature_valley_factor",
        "background_type", "background_color") if hasattr(shading, key)}
    render_visibility = {o.name: o.hide_render for o in bpy.data.objects if o.type == "MESH"}

    def render_set(prefix):
        scene.render.engine = "BLENDER_WORKBENCH"
        scene.display.shading.light = "STUDIO"
        scene.display.shading.studio_light = "paint.sl"
        scene.display.shading.color_type = "MATERIAL"
        scene.display.shading.show_shadows = True
        scene.display.shading.show_cavity = True
        scene.display.shading.cavity_type = "BOTH"
        scene.display.shading.curvature_ridge_factor = 1.2
        scene.display.shading.curvature_valley_factor = 1.1
        scene.display.shading.background_type = "WORLD"
        if scene.world:
            scene.world.color = (.11, .12, .13)
        scene.render.resolution_x = scene.render.resolution_y = 1000
        scene.render.resolution_percentage = 100
        scene.render.image_settings.file_format = "PNG"
        scene.render.film_transparent = False
        for obj in bpy.data.objects:
            if obj.type == "MESH":
                eras = obj.get("exteriorEras", "maker,mechanic,builder").split(",")
                obj.hide_render = "builder" not in eras
                obj.hide_set(False)
        cam_data = bpy.data.cameras.new("V15 breast study review camera")
        cam = bpy.data.objects.new("V15 breast study review camera", cam_data)
        scene.collection.objects.link(cam)
        scene.camera = cam
        records = []
        for name, position, target, scale in views:
            cam.location = position
            cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
            cam_data.type = "ORTHO"
            cam_data.ortho_scale = scale
            image_path = OUT / f"{prefix}-{name}.png"
            scene.render.filepath = str(image_path)
            bpy.ops.render.render(write_still=True)
            records.append({"path": str(image_path.relative_to(ROOT)),
                            "sha256": sha(image_path), "bytes": image_path.stat().st_size,
                            "camera": list(position), "target": list(target),
                            "projection": "ORTHO", "orthoScale": scale,
                            "resolution": [1000, 1000], "era": "builder"})
        scene.camera = render_state["camera"]
        bpy.data.objects.remove(cam, do_unlink=True)
        bpy.data.cameras.remove(cam_data)
        for name, value in render_state.items():
            if name == "world_color" or name == "camera":
                continue
            if name == "file_format":
                scene.render.image_settings.file_format = value
            else:
                setattr(scene.render, name, value)
        if scene.world and render_state["world_color"] is not None:
            scene.world.color = render_state["world_color"]
        for key, value in shading_state.items():
            setattr(scene.display.shading, key, value)
        for name, value in render_visibility.items():
            if bpy.data.objects.get(name):
                bpy.data.objects[name].hide_render = value
        bpy.context.view_layer.update()
        return records

    before_views = render_set("before")
    assert not any(o.name.startswith("V15 breast") for o in bpy.data.objects)

    module = __import__("runpy").run_path(str(MODULE), run_name="v15_breast_module")
    build = module["apply"]()
    after = snapshot()
    assert before["empties"] == after["empties"], "A pivot or transform changed"
    assert before["curves"] == after["curves"], "An existing guide curve changed"
    removed = set(build["removedExisting"])
    created = set(build["createdNames"])
    assert old_mesh_names - set(after["meshes"]) == removed
    assert set(after["meshes"]) - old_mesh_names == created
    for name in sorted(old_mesh_names - removed):
        assert before["meshes"][name] == after["meshes"][name], f"Unrelated mesh changed: {name}"
    materials_after = {mat.name: material_signature(mat) for mat in bpy.data.materials}
    assert materials_before == materials_after, "An existing material changed"
    assert len(after["empties"]) == 52 and len(after["curves"]) == len(old_curve_names)
    assert all(obj.parent.name == "breastplate" for obj in build["createdObjects"])
    assert all(obj.get("exteriorEras") == "maker,mechanic,builder"
               and obj.get("constructionClass") == "inherited-passive"
               for obj in build["createdObjects"])
    assert set(build["retainedRepairLandmarks"]) == {
        obj.name for obj in bpy.data.objects if obj.type == "MESH"
        and obj.parent and obj.parent.name == "industrial-repairs"
        and obj.get("surfaceRole") == "repair"}

    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    bpy.ops.wm.save_as_mainfile(filepath=str(NATIVE))
    after_views = render_set("after")

    report = {
        "status": "single-region breast construction proposal; visual review required",
        "generatedAtUtc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "base": {"path": str(BASE.relative_to(ROOT)), "sha256": BASE_SHA,
                 "bytes": BASE.stat().st_size},
        "candidate": {"path": str(NATIVE.relative_to(ROOT)),
                      "sha256": sha(NATIVE), "bytes": NATIVE.stat().st_size},
        "module": {"path": str(MODULE.relative_to(ROOT)), "sha256": sha(MODULE),
                   "executedCopy": {"path": str((OUT / "executed-breast-module.py").relative_to(ROOT)),
                                    "sha256": sha(OUT / "executed-breast-module.py")}},
        "baseComparison": {"pivotsExact": len(after["empties"]),
                           "guidesExact": len(after["curves"]),
                           "unchangedMeshesExact": len(old_mesh_names - removed),
                           "removedExistingBreastMeshes": sorted(removed),
                           "addedMeshes": sorted(created),
                           "materialsExact": True,
                           "repairLandmarksRetained": build["retainedRepairLandmarks"]},
        "region": {"owner": build["owner"], "region": build["region"],
                   "eligibility": build["eligibility"],
                   "design": "Twenty-four staggered formed panels split into two or three irregular plates per side across five courses, two inset service-access returns, and forty-eight captive lap anchors. Existing continuous inner access shell, thoracic load rails, body ribs, core, and repair landmarks are retained."},
        "views": {"renderer": "Blender Workbench paint.sl, material colors, cavity; matched fixed cameras",
                  "before": before_views, "after": after_views},
        "breastReferences": {
            "ownerResuppliedTarget": {"path": str(REFERENCE.relative_to(ROOT)),
                                      "sha256": sha(REFERENCE),
                                      "use": "Owner-supplied whole-body appearance target; visual guide only, not measured geometry"},
            "candidate03": {"path": str(CANDIDATE03.relative_to(ROOT)),
                            "sha256": sha(CANDIDATE03),
                            "use": "Existing whole-character appearance reference; visual guide only, not measured geometry"},
            "excludedScope": "July owner image controls head only; no July breast/body proportions were used.",
        },
        "currentA11View": {"path": str(CURRENT.relative_to(ROOT)), "sha256": sha(CURRENT)},
        "limits": ["Static native rest-pose study; no runtime opening pose or browser capture.",
                   "Basic parent, pivot, and unchanged-region comparisons only; no full collision/containment or continuous-motion proof.",
                   "Geometry is a proposal and remains subject to owner visual review; no likeness acceptance is claimed."]}
    (OUT / "study-receipt.json").write_text(json.dumps(report, indent=2) + "\n")
    assert sha(BASE) == BASE_SHA, "Pinned V14 input changed"
    print(json.dumps({"native": report["candidate"],
                      "removed": len(removed), "added": len(created),
                      "pivots": len(after["empties"]), "curves": len(after["curves"]),
                      "unchangedMeshes": len(old_mesh_names - removed),
                      "beforeViews": len(before_views), "afterViews": len(after_views),
                      "audit": str(OUT.relative_to(ROOT))}, indent=2))


if __name__ == "__main__":
    main()
