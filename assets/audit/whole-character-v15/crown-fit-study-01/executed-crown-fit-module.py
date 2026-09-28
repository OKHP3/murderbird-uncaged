"""One local cranial-cover relief proposal for the V15 orbital/brow seam.

The edited vertices tuck only crossing crown edges inward under the fixed
orbital support. The optic, jaw, brows, pivots, and all other scene data stay
fixed. Coordinates are authoring proposals, not recovered dimensions.
"""
import math
import bpy
from mathutils import Vector


def _smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def _ellipsoid_weight(point, center, radii):
    q = math.sqrt(sum(((point[i] - center[i]) / radii[i]) ** 2 for i in range(3)))
    return 1.0 - _smooth((q - 0.55) / 0.45)


def _relief(name, center_abs_x, center_y, center_z, radii, amount):
    obj = bpy.data.objects.get(name)
    assert obj and obj.type == 'MESH' and obj.parent and obj.parent.name == 'cranial-cover', name
    inverse = obj.matrix_world.inverted()
    moved = 0
    max_delta = 0.0
    for vertex in obj.data.vertices:
        point = obj.matrix_world @ vertex.co
        side = 1.0 if point.x >= 0.0 else -1.0
        center = (side * center_abs_x, center_y, center_z)
        weight = _ellipsoid_weight(point, center, radii)
        if weight <= 1e-6:
            continue
        # Tuck the crossing edge toward the skull center. The smooth spatial
        # falloff leaves the plate field and its outer silhouette intact.
        delta = Vector((-side * amount * weight, 0.0, 0.0))
        vertex.co = inverse @ (point + delta)
        moved += 1
        max_delta = max(max_delta, delta.length)
    obj.data.update()
    return {'mesh': name, 'verticesMoved': moved, 'maximumDisplacementM': max_delta}


def apply():
    """Apply one symmetric local inner-edge tuck to the four crossing owners."""
    edits = [
        _relief('Continuous temporal shell -1', .163, -.300, 1.765,
                (.030, .044, .034), .012),
        _relief('Continuous temporal shell 1', .163, -.300, 1.765,
                (.030, .044, .034), .012),
        _relief('Rounded swept crown lamina 0', .080, -.503, 1.802,
                (.052, .052, .038), .012),
        _relief('Swept temporal lamina -1 0 0', .151, -.407, 1.864,
                (.030, .052, .035), .012),
        _relief('Swept temporal lamina 1 0 0', .151, -.407, 1.864,
                (.030, .052, .035), .012),
    ]
    bpy.context.view_layer.update()
    return {
        'region': 'crown-fit',
        'changedMeshes': [row['mesh'] for row in edits],
        'newMeshes': [],
        'edits': edits,
        'method': 'smooth local symmetric inward tuck at the crown/temporal inner edges implicated by native strict-crossing samples',
        'fixed': ['optic assembly', 'orbital brow', 'orbital mount', 'upper bill', 'jaw', 'all pivots', 'all curves'],
        'limits': [
            'One geometry proposal only; not a collision-free guarantee.',
            'The screen uses the prescribed seven discrete cranial-cover world-Z lifts.',
            'No continuous sweep, full head collision, or runtime/browser claim.',
        ],
    }
