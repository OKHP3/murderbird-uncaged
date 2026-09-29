"""Measure sampled triangle-pair envelopes for construction04 BVH findings.

Reuses only the exact pitch samples and pair identities in result.json. For
each pair it chooses the stored sample with the largest triangle-pair count,
then records the combined bounds and arithmetic centroid of the vertices in
those overlapping triangle pairs. This is a locator, not the exact clipped
triangle-intersection volume or penetration depth.
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
SOURCE_RESULT = Path(__file__).with_name("result.json")
EXPECTED_RESULT_SHA256 = "19d9366f23889999a181d7ff7b99c62f4225771253529191d4c77482c2b78b06"
OUT = Path(__file__).with_name("witness.json")


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def pose(pitch):
    bpy.data.objects["neck"].rotation_euler = (.35 * pitch, 0, 0)
    bpy.data.objects["cervical-upper"].rotation_euler = (.65 * pitch, 0, 0)
    bpy.data.objects["head"].rotation_euler = (-pitch, 0, 0)
    bpy.data.objects["cervical-joint-cover"].rotation_euler = (.325 * pitch, 0, 0)
    bpy.context.view_layer.update()


def evaluated_geometry(names):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    out = {}
    for name in sorted(names):
        obj = bpy.data.objects.get(name)
        if obj is None or obj.type != "MESH" or obj.parent is None:
            raise RuntimeError("Missing witness mesh: " + name)
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            mesh.calc_loop_triangles()
            points = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
            triangles = [tuple(triangle.vertices) for triangle in mesh.loop_triangles]
            if not points or not triangles:
                raise RuntimeError("Empty evaluated witness mesh: " + name)
            tree = BVHTree.FromPolygons(points, triangles, all_triangles=True, epsilon=0.0)
            out[name] = {"points": points, "triangles": triangles, "tree": tree,
                         "owner": obj.parent.name, "region": obj.get("region"),
                         "role": obj.get("surfaceRole")}
        finally:
            evaluated.to_mesh_clear()
    return out


def measure(points):
    low = [min(point[axis] for point in points) for axis in range(3)]
    high = [max(point[axis] for point in points) for axis in range(3)]
    centroid = [sum(point[axis] for point in points) / len(points) for axis in range(3)]
    return {"min": low, "max": high, "centroid": centroid,
            "vertexOccurrences": len(points)}


def main():
    if Path(bpy.data.filepath).resolve() != NATIVE.resolve():
        raise RuntimeError("Blender did not load the exact construction04 native")
    native_hash = sha256(NATIVE)
    result_hash = sha256(SOURCE_RESULT)
    if native_hash != EXPECTED_NATIVE_SHA256 or result_hash != EXPECTED_RESULT_SHA256:
        raise RuntimeError("Pinned native or prior collision receipt hash mismatch")
    if OUT.exists():
        raise FileExistsError("Refusing to overwrite " + str(OUT))
    original = json.loads(SOURCE_RESULT.read_text())

    cleared = []
    for obj in bpy.data.objects:
        if obj.animation_data is not None:
            obj.animation_data_clear()
            cleared.append(obj.name)
    bpy.context.scene.frame_set(1)

    witnesses = []
    poses_to_pairs = {}
    for pair in original["uniquePairs"]:
        samples = pair["samples"]
        worst = max(samples, key=lambda row: row["trianglePairs"])
        witness = {"surfaceA": pair["surfaceA"], "surfaceB": pair["surfaceB"],
                   "worstCountSamplePitchRad": worst["pitchRad"],
                   "expectedTrianglePairs": worst["trianglePairs"]}
        witnesses.append(witness)
        poses_to_pairs.setdefault(worst["pitchRad"], []).append(witness)

    for pitch, pairs in sorted(poses_to_pairs.items()):
        pose(pitch)
        meshes = evaluated_geometry({name for pair in pairs
                                     for name in (pair["surfaceA"], pair["surfaceB"])})
        for witness in pairs:
            a = meshes[witness["surfaceA"]]
            b = meshes[witness["surfaceB"]]
            hit_pairs = a["tree"].overlap(b["tree"])
            if len(hit_pairs) != witness["expectedTrianglePairs"]:
                raise RuntimeError(
                    f"Pair count drift at pitch {pitch}: {witness['surfaceA']} / {witness['surfaceB']} "
                    f"expected {witness['expectedTrianglePairs']} got {len(hit_pairs)}")
            points = []
            for tri_a, tri_b in hit_pairs:
                points.extend(a["points"][index] for index in a["triangles"][tri_a])
                points.extend(b["points"][index] for index in b["triangles"][tri_b])
            witness["ownerA"] = a["owner"]
            witness["regionA"] = a["region"]
            witness["roleA"] = a["role"]
            witness["ownerB"] = b["owner"]
            witness["regionB"] = b["region"]
            witness["roleB"] = b["role"]
            witness["triangleVertexEnvelope"] = measure(points)

    report = {
        "status": "sampled crossing-triangle location witnesses; not exact intersection volumes",
        "inputNative": {"path": str(NATIVE.relative_to(ROOT)), "sha256": native_hash},
        "sourceCollisionReceipt": {"path": str(SOURCE_RESULT.relative_to(ROOT)), "sha256": result_hash},
        "checkerSha256": sha256(Path(__file__)),
        "animationDataClearedInMemory": cleared,
        "selection": "For each of the 27 existing unique pairs, choose its already-recorded sample with the maximum triangle-pair count; tied maxima select the first stored sample.",
        "measurement": "Union envelope and arithmetic centroid of all six vertices per BVH-overlap triangle pair, in native world coordinates.",
        "limits": ["Bounds/centroids cover source triangles in returned BVH pairs, not the exact clipped intersection region.",
                   "No new pitches or pose range were evaluated.",
                   "No severity, intentional-contact, clearance, or acceptance judgment is made."],
        "witnessCount": len(witnesses),
        "witnesses": witnesses,
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print("CONSTRUCTION04_WITNESS", json.dumps({
        "nativeSha256": native_hash, "sourceResultSha256": result_hash,
        "witnessCount": len(witnesses), "result": str(OUT)}, sort_keys=True))


main()
