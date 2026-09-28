"""Post-composition rest-geometry cleanup for V16's lowest neck guard courses.

This module is intended to be run after the V16 mapping has transformed the
scene and before the composed native is saved. It keeps the compressed neck
envelope and all joint/owner transforms intact; only the inferior extent of
the existing lower guard meshes is eased back to make the overlapping courses
read as a stepped cascade at the neck-to-breast transition.

This is a proposal, not a motion-clearance or artistic acceptance result.
"""

import bpy


def _target_names():
    names = set()
    # Preserve the formed throat and lateral guard identities. The upper edge
    # remains seated while only the lower free edge is shortened modestly.
    names.update(f"Throat formed lamina {course}" for course in (4, 5, 6))
    names.update(
        f"Cervical flank lamina {side} {course}"
        for side in (-1, 1)
        for course in (4, 5, 6)
    )
    # Posterior courses 1-3 are upper-owned; the lower courses remain on neck.
    names.update(
        f"V11 posterior cervical lap {course} {column}"
        for course in (4, 5, 6)
        for column in range(1, 6)
    )
    return names


def apply():
    """Refit 24 existing lower guard meshes in-place and return a receipt."""
    targets = _target_names()
    missing = sorted(name for name in targets if bpy.data.objects.get(name) is None)
    if missing:
        raise RuntimeError(f"V16 lower-neck guard contract missing objects: {missing}")

    # At course 4 the adjustment is barely perceptible; course 6 is the broad
    # terminal course that currently bunches most visibly against the breast.
    # Values reduce only the inferior half-span, keeping the superior edge and
    # each mesh's pivot, parent, material, era tags, and rigid owner unchanged.
    shorten_by_course = {4: 0.025, 5: 0.060, 6: 0.105}
    changed = []
    for name in sorted(targets):
        obj = bpy.data.objects[name]
        if obj.type != "MESH":
            raise RuntimeError(f"Expected mesh for lower-neck guard {name}: {obj.type}")
        if obj.get("region") != "neck":
            raise RuntimeError(f"Unexpected region on lower-neck guard {name}: {obj.get('region')}")
        if len(obj.data.materials) == 0:
            raise RuntimeError(f"Lower-neck guard has no assigned material: {name}")
        if obj.data.users != 1:
            raise RuntimeError(f"Refusing to mutate shared mesh data for {name}")

        course = int(name.split()[-2]) if name.startswith("V11 posterior") else int(name.rsplit(" ", 1)[-1])
        if obj.parent is None or obj.parent.name != "neck":
            raise RuntimeError(f"Unexpected rigid owner for lower-neck guard {name}: {obj.parent.name if obj.parent else None}")
        ratio = shorten_by_course[course]
        world = obj.matrix_world.copy()
        inverse = world.inverted()
        coords = [world @ vertex.co for vertex in obj.data.vertices]
        z_min = min(point.z for point in coords)
        z_max = max(point.z for point in coords)
        span = z_max - z_min
        if span <= 1e-6:
            raise RuntimeError(f"Degenerate vertical span on lower-neck guard {name}")

        # Preserve every vertex at or above the upper 30% of the plate and
        # ease the inferior contour progressively. A smoothstep avoids a hard
        # bend line while retaining overlap at the seated upper lap.
        for vertex, point in zip(obj.data.vertices, coords):
            depth = max(0.0, min(1.0, (z_max - point.z) / span))
            t = max(0.0, min(1.0, (depth - 0.30) / 0.70))
            eased = t * t * (3.0 - 2.0 * t)
            point.z += span * ratio * eased
            vertex.co = inverse @ point

        obj.data.update()
        changed.append({
            "name": name,
            "parent": obj.parent.name if obj.parent else None,
            "course": course,
            "inferiorEdgeShorteningFraction": ratio,
            "worldZSpanBeforeM": span,
            "worldZSpanAfterM": span * (1.0 - ratio),
            "materialNames": [material.name if material else None for material in obj.data.materials],
            "region": obj.get("region"),
            "surfaceRole": obj.get("surfaceRole"),
            "exteriorEras": obj.get("exteriorEras"),
        })

    return {
        "status": "V16 lower-neck guard rest-geometry proposal",
        "changedMeshCount": len(changed),
        "changedMeshes": changed,
        "preserved": [
            "object names and parent ownership",
            "object transforms and all joint pivots",
            "materials, era tags, and rigid attachment owners",
            "guard upper edges and the compressed curved neck envelope",
        ],
        "limits": [
            "No animation-time deformation or metal stretching is introduced.",
            "This local rest-shape refit does not establish movement clearance.",
            "The integrated V16 attempt must be re-exported and rechecked after composition.",
        ],
    }
