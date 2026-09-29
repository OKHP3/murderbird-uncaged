"""Read-only world-frame inventory for V21 Construction06.

Records selected rest pivots, hierarchy segment lengths, finite evaluated mesh
bounds, and mechanism/contact anchors. It does not save or alter the native.
"""

import hashlib
import json
import math
from pathlib import Path

import bpy


ROOT = Path("/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged")
NATIVE = ROOT / "assets/models/whole-character-v21/attempt-construction06/murderbird-whole-character-v21.blend"
EXPECTED_NATIVE_SHA256 = "79ad3e368e7b75edbbc758b1264a1ccaf34f284c6ca185ee8441875576a6f54c"
OUT = ROOT / "assets/audit/whole-character-v22/input/current-frame.json"

OWNER_NAMES = (
    "murderbird", "body", "breastplate", "neck", "cervical-upper", "head", "jaw", "upper-bill",
    "left-mantle", "right-mantle", "left-wing-shield", "right-wing-shield",
    "left-thigh", "right-thigh", "left-shin", "right-shin", "left-foot", "right-foot",
    "left-toes", "right-toes",
)
MARKER_NAMES = (
    "anchor-beak", "anchor-drive", "anchor-guard", "anchor-joint", "anchor-mind",
    "anchor-power", "anchor-shell", "bill-contact", "left-hip-landmark", "right-hip-landmark",
    "left-knee-landmark", "right-knee-landmark", "left-sole-landmark", "right-sole-landmark",
)
SEGMENTS = (
    ("murderbird", "body", "root-to-torso owner pivot"),
    ("body", "neck", "torso to lower-neck pivot"),
    ("neck", "cervical-upper", "lower to upper cervical pivot"),
    ("cervical-upper", "head", "upper cervical to skull pivot"),
    ("head", "jaw", "skull to jaw pivot"),
    ("head", "upper-bill", "skull to upper-bill pivot"),
    ("body", "breastplate", "torso to opening breastplate pivot"),
    ("left-thigh", "left-shin", "left hip to knee joint pivots"),
    ("left-shin", "left-foot", "left knee to ankle/foot joint pivots"),
    ("left-foot", "left-toes", "left foot to toe cluster pivot"),
    ("right-thigh", "right-shin", "right hip to knee joint pivots"),
    ("right-shin", "right-foot", "right knee to ankle/foot joint pivots"),
    ("right-foot", "right-toes", "right foot to toe cluster pivot"),
    ("left-hip-landmark", "left-knee-landmark", "left authored hip-to-knee landmarks"),
    ("left-knee-landmark", "left-sole-landmark", "left authored knee-to-sole landmarks"),
    ("right-hip-landmark", "right-knee-landmark", "right authored hip-to-knee landmarks"),
    ("right-knee-landmark", "right-sole-landmark", "right authored knee-to-sole landmarks"),
)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def vec(values):
    return [float(value) for value in values]


def world_point(obj):
    return vec(obj.matrix_world.translation)


def length(a, b):
    return math.dist(a, b)


def finite_mesh_bounds(owner_name, depsgraph):
    objects = [obj for obj in bpy.data.objects
               if obj.type == "MESH" and obj.parent is not None and obj.parent.name == owner_name]
    bounds_points = []
    vertex_count = triangle_count = 0
    for obj in objects:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            mesh.calc_loop_triangles()
            points = [evaluated.matrix_world @ vertex.co for vertex in mesh.vertices]
            if any(not math.isfinite(value) for point in points for value in point):
                raise RuntimeError("Non-finite evaluated coordinate in " + obj.name)
            bounds_points.extend(points)
            vertex_count += len(points)
            triangle_count += len(mesh.loop_triangles)
        finally:
            evaluated.to_mesh_clear()
    if not bounds_points:
        return {"meshCount": len(objects), "vertexCount": 0, "triangleCount": 0,
                "boundsMin": None, "boundsMax": None, "finite": True}
    return {
        "meshCount": len(objects), "vertexCount": vertex_count,
        "triangleCount": triangle_count,
        "boundsMin": [min(point[axis] for point in bounds_points) for axis in range(3)],
        "boundsMax": [max(point[axis] for point in bounds_points) for axis in range(3)],
        "finite": True,
    }


def main():
    if Path(bpy.data.filepath).resolve() != NATIVE.resolve():
        raise RuntimeError("Unexpected Blender input file")
    native_sha = sha256(NATIVE)
    if native_sha != EXPECTED_NATIVE_SHA256:
        raise RuntimeError("Construction06 native SHA256 mismatch")
    if OUT.exists():
        raise FileExistsError("Refusing to overwrite " + str(OUT))
    missing = [name for name in OWNER_NAMES + MARKER_NAMES if bpy.data.objects.get(name) is None]
    if missing:
        raise RuntimeError("Required pivots/markers missing: " + repr(missing))

    bpy.context.scene.frame_set(1)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    pivots = {}
    for name in OWNER_NAMES:
        obj = bpy.data.objects[name]
        pivots[name] = {
            "parent": obj.parent.name if obj.parent else None,
            "worldPosition": world_point(obj),
            "localBasisPosition": vec(obj.location),
            "worldRotationEuler": vec(obj.matrix_world.to_euler()),
        }
    segments = []
    for a_name, b_name, label in SEGMENTS:
        a, b = bpy.data.objects[a_name], bpy.data.objects[b_name]
        pa, pb = world_point(a), world_point(b)
        segments.append({"from": a_name, "to": b_name, "label": label,
                         "fromWorld": pa, "toWorld": pb, "distanceM": length(pa, pb),
                         "parentRelation": b.parent.name if b.parent else None})

    bounds = {name: finite_mesh_bounds(name, depsgraph) for name in OWNER_NAMES}
    markers = {}
    for name in MARKER_NAMES:
        obj = bpy.data.objects[name]
        markers[name] = {"parent": obj.parent.name if obj.parent else None,
                         "worldPosition": world_point(obj),
                         "localBasisPosition": vec(obj.location)}

    body = bpy.data.objects["body"]
    mechanism = json.loads(body["mechanismLayoutV1"])
    envelope = json.loads(body["sharedEnvelopeV21"])
    cage = json.loads(body["proportionCageV20"])
    report = {
        "schema": "murderbird-v22-input-frame-v1",
        "status": "read-only Construction06 rest-frame inventory; no proposed mapping applied",
        "input": {"path": str(NATIVE.relative_to(ROOT)), "sha256": native_sha,
                   "bytes": NATIVE.stat().st_size},
        "scriptSha256": sha256(Path(__file__)),
        "coordinateConvention": "Native scene world coordinates, metres; +Z up; positive X is anatomical left.",
        "pivots": pivots,
        "finiteEvaluatedMeshBoundsByOwner": bounds,
        "segmentLengths": segments,
        "contactAndAttachmentMarkers": markers,
        "currentBodyMetadata": {
            "mechanismLayoutV1": {
                "status": mechanism.get("status"),
                "coordinateSpace": mechanism.get("coordinateSpace"),
                "makerControlOffsets": mechanism.get("makerControlOffsets"),
                "tailPosition": mechanism.get("tailPosition"),
                "distributionPosition": mechanism.get("distributionPosition"),
                "transmissionPosition": mechanism.get("transmissionPosition"),
                "cervical": mechanism.get("cervical"),
                "makerCradleWidth": mechanism.get("makerCradleWidth"),
                "cervicalSocketProvenanceV21": mechanism.get("cervicalSocketProvenanceV21"),
            },
            "sharedEnvelopeV21": {
                "pivots": envelope.get("pivots"),
                "status": envelope.get("status"),
            },
            "proportionCageV20Keys": sorted(cage.keys()),
        },
        "rederiveAfterPiecewiseMapping": [
            "Recompute every body.mechanismLayoutV1 makerControlOffsets point for leg, wing, tail, neck, and jaw in its named owner-local frame; all five are currently explicit offsets.",
            "Recompute body-local tailPosition, distributionPosition, and transmissionPosition, plus makerCradleWidth if mapped body proportions change.",
            "Recompute both mechanismLayoutV1.cervical bodyPoint/neckPoint socket pairs against the mapped body and neck geometry; current provenance says retained envelope03 frame points.",
            "Rebuild or supersede sharedEnvelopeV21 profile and stored neck/cervical-upper/head pivots; these are fixed authored values for the current Construction06 pose.",
            "Re-evaluate all proportionCageV20 bodyZ/bodyWidth/neck/headDelta/mantle/legJoints mapping control points so a second mapping does not compound stale V20 values.",
            "Re-seat anchor-joint, anchor-shell, anchor-beak, anchor-guard, anchor-mind, anchor-power, and anchor-drive to their mapped hardware owners.",
            "Recompute bill-contact against the final upper-bill tip and revalidate left/right sole-landmark plus toe geometry against the ground plane; remeasure hip/knee landmarks and the thigh/shin/foot/toes segment lengths after lower-body shortening.",
        ],
        "limits": [
            "Bounds aggregate evaluated meshes directly parented to each listed owner; they are not collision or articulation tests.",
            "Pivot-to-pivot distances are hierarchy-frame distances, not necessarily physical link centerline lengths.",
            "No mapping, export, rendering, or artistic/engineering acceptance was performed.",
        ],
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print("V22_CURRENT_FRAME", json.dumps({
        "nativeSha256": native_sha,
        "segmentLengths": [{"from": row["from"], "to": row["to"], "distanceM": row["distanceM"]}
                           for row in segments],
        "output": str(OUT),
    }, sort_keys=True))


main()
