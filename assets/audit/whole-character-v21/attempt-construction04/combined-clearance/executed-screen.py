"""Nine-pose evaluated surface-overlap screen for construction04.

Clears object animation data in memory before posing. No native file is saved.
The check reports triangle-surface BVH overlaps between selected owner groups;
it does not detect containment, penetration depth, or guarantee continuous
clearance between the nine sampled poses.
"""

import hashlib
import json
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


ROOT = Path("/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged")
NATIVE = ROOT / "assets/models/whole-character-v21/attempt-construction04/murderbird-whole-character-v21.blend"
EXPECTED_NATIVE_SHA256 = "f57f85b92463d527d6cba528090e8f6ec3d31f1a73a235ce8e78361244061d1e"
OUT = ROOT / "assets/audit/whole-character-v21/attempt-construction04/combined-clearance"
RESULT = OUT / "result.json"
NECK_OWNERS = {"neck", "cervical-upper", "cervical-joint-cover"}
ADJACENT_OWNERS = {"head", "jaw", "upper-bill", "body", "breastplate"}
PITCHES = (-.65, -.4875, -.325, -.1625, 0.0, .1625, .325, .4875, .65)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    if Path(bpy.data.filepath).resolve() != NATIVE.resolve():
        raise RuntimeError("Blender did not load the pinned construction04 native")
    actual_native_hash = sha256(NATIVE)
    if actual_native_hash != EXPECTED_NATIVE_SHA256:
        raise RuntimeError("Construction04 native hash mismatch")
    if RESULT.exists():
        raise FileExistsError("Refusing to overwrite " + str(RESULT))

    # The authoring file has inherited animation data that can reset local
    # head rotations during frame evaluation. Remove it only in this process.
    cleared = []
    for obj in bpy.data.objects:
        if obj.animation_data is not None:
            obj.animation_data_clear()
            cleared.append(obj.name)
    bpy.context.scene.frame_set(1)

    required_owners = NECK_OWNERS | ADJACENT_OWNERS
    missing = sorted(name for name in required_owners if bpy.data.objects.get(name) is None)
    if missing:
        raise RuntimeError("Required owner empties missing: " + repr(missing))
    breast_panels = [obj for obj in bpy.data.objects
                     if obj.type == "MESH" and obj.parent
                     and obj.parent.name == "breastplate"
                     and obj.name.startswith("V21 breast course ")]
    backing = [obj for obj in bpy.data.objects
               if obj.type == "MESH" and obj.parent
               and obj.parent.name == "breastplate"
               and obj.name == "V21 recessed breast course backing"]
    if len(breast_panels) != 30 or len(backing) != 1:
        raise RuntimeError(f"Unexpected breast geometry: {len(breast_panels)} plates, {len(backing)} backing")

    results = []
    pair_samples = {}
    for pitch in PITCHES:
        bpy.data.objects["neck"].rotation_euler = (.35 * pitch, 0, 0)
        bpy.data.objects["cervical-upper"].rotation_euler = (.65 * pitch, 0, 0)
        bpy.data.objects["head"].rotation_euler = (-pitch, 0, 0)
        bpy.data.objects["cervical-joint-cover"].rotation_euler = (.325 * pitch, 0, 0)
        bpy.context.view_layer.update()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        groups = {"neck": [], "adjacent": []}
        owner_counts = {}

        for obj in bpy.data.objects:
            if obj.type != "MESH" or obj.parent is None:
                continue
            owner = obj.parent.name
            if owner not in required_owners:
                continue
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            try:
                mesh.calc_loop_triangles()
                points = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
                if not points or not mesh.loop_triangles:
                    raise RuntimeError("Empty evaluated target mesh: " + obj.name)
                triangles = [tuple(triangle.vertices) for triangle in mesh.loop_triangles]
                tree = BVHTree.FromPolygons(points, triangles, all_triangles=True, epsilon=0.0)
                bounds_min = tuple(min(point[axis] for point in points) for axis in range(3))
                bounds_max = tuple(max(point[axis] for point in points) for axis in range(3))
                row = {"name": obj.name, "owner": owner, "tree": tree,
                       "min": bounds_min, "max": bounds_max,
                       "vertices": len(points), "triangles": len(triangles)}
                groups["neck" if owner in NECK_OWNERS else "adjacent"].append(row)
                owner_counts[owner] = owner_counts.get(owner, 0) + 1
            finally:
                evaluated.to_mesh_clear()

        local_pairs = []
        for index, left in enumerate(groups["neck"]):
            for right in groups["neck"][index + 1:]:
                if left["owner"] == right["owner"]:
                    continue
                if any(left["max"][axis] < right["min"][axis]
                       or right["max"][axis] < left["min"][axis] for axis in range(3)):
                    continue
                hits = left["tree"].overlap(right["tree"])
                if hits:
                    local_pairs.append({"surfaceA": left["name"], "ownerA": left["owner"],
                                        "surfaceB": right["name"], "ownerB": right["owner"],
                                        "trianglePairs": len(hits)})
                    key = (left["name"], right["name"])
                    pair_samples.setdefault(key, []).append({"pitchRad": pitch, "trianglePairs": len(hits)})

        cross_pairs = []
        for neck in groups["neck"]:
            for other in groups["adjacent"]:
                if neck["owner"] == other["owner"]:
                    continue
                if any(neck["max"][axis] < other["min"][axis]
                       or other["max"][axis] < neck["min"][axis] for axis in range(3)):
                    continue
                hits = neck["tree"].overlap(other["tree"])
                if hits:
                    cross_pairs.append({"neckSurface": neck["name"], "neckOwner": neck["owner"],
                                        "adjacentSurface": other["name"], "adjacentOwner": other["owner"],
                                        "trianglePairs": len(hits)})
                    key = (neck["name"], other["name"])
                    pair_samples.setdefault(key, []).append({"pitchRad": pitch, "trianglePairs": len(hits)})

        results.append({"pitchRad": pitch,
                        "appliedLocalRotations": {"neckX": .35 * pitch,
                                                   "cervicalUpperX": .65 * pitch,
                                                   "headX": -pitch,
                                                   "coverX": .325 * pitch},
                        "meshCountByOwner": owner_counts,
                        "neckInterOwnerPairCount": len(local_pairs),
                        "neckAdjacentPairCount": len(cross_pairs),
                        "neckInterOwnerPairs": local_pairs,
                        "neckAdjacentPairs": cross_pairs})

    report = {
        "status": "bounded evaluated nine-pose surface-overlap screen; not clearance acceptance",
        "input": {"nativePath": str(NATIVE.relative_to(ROOT)),
                  "nativeSha256": actual_native_hash,
                  "nativeBytes": NATIVE.stat().st_size},
        "checkerSha256": sha256(Path(__file__)),
        "animationDataClearedInMemory": cleared,
        "poses": results,
        "uniquePairCount": len(pair_samples),
        "uniquePairs": [{"surfaceA": key[0], "surfaceB": key[1], "samples": samples}
                        for key, samples in sorted(pair_samples.items())],
        "scope": {"neckOwners": sorted(NECK_OWNERS),
                  "adjacentOwners": sorted(ADJACENT_OWNERS),
                  "breastCoursePanels": len(breast_panels), "breastBacking": len(backing),
                  "interOwnerOnly": True,
                  "method": "Evaluated dependency-graph mesh triangles; AABB-prefiltered BVHTree surface-overlap pairs; no exemptions.",
                  "limits": ["Nine discrete pitch samples only; no continuous-sweep guarantee.",
                             "Surface crossing only; does not detect full containment or penetration depth.",
                             "No interpretation of intentional mating, structural strength, or artistic acceptance."]},
    }
    RESULT.write_text(json.dumps(report, indent=2) + "\n")
    print("CONSTRUCTION04_CLEARANCE", json.dumps({
        "nativeSha256": actual_native_hash,
        "poses": [{"pitchRad": row["pitchRad"],
                   "neckInterOwnerPairs": row["neckInterOwnerPairCount"],
                   "neckAdjacentPairs": row["neckAdjacentPairCount"]} for row in results],
        "uniquePairCount": len(pair_samples),
        "result": str(RESULT),
    }, sort_keys=True))


main()
