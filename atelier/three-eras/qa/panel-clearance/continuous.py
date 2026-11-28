"""Bound a panel's continuous hinge motion from the measured vertices and transforms."""
import json
import sys
from pathlib import Path

import numpy as np


def world_vertices(directory, leaves, matrices):
    transformed = []
    for leaf, matrix in zip(leaves, matrices):
        path = directory / (leaf["geom"] + ".positions")
        points = np.fromfile(path, dtype=np.float32).reshape(-1, 3)
        transformed.append(points @ matrix[:3, :3].T + matrix[:3, 3])
    return np.concatenate(transformed)


def farthest_support(transforms, vertices, sign):
    """Maximize each vertex's signed X coordinate along the monotonic hinge arc."""
    cosines = (np.trace(transforms[:, :3, :3], axis1=1, axis2=2) - 1) / 2
    angles = np.arccos(np.clip(cosines, -1, 1))
    if np.min(np.diff(angles)) < -1e-7:
        raise ValueError("The hinge did not move monotonically")

    # For a rigid rotation around a fixed hinge, signed X is offset + A cos(t) + B sin(t).
    basis = np.column_stack([np.ones(len(angles)), np.cos(angles), np.sin(angles)])
    anchors = [0, len(angles) // 2, len(angles) - 1]
    coefficients = np.linalg.solve(basis[anchors], sign * transforms[anchors, 0, :])
    residual = np.max(np.abs(basis @ coefficients - sign * transforms[:, 0, :]))
    points = np.column_stack([vertices, np.ones(len(vertices))])
    offset, a, b = coefficients @ points.T
    end = angles[-1]
    extrema = np.maximum(offset + a, offset + a * np.cos(end) + b * np.sin(end))
    interior = np.mod(np.arctan2(b, a), 2 * np.pi) <= end
    extrema[interior] = np.maximum(extrema[interior], offset[interior] + np.hypot(a[interior], b[interior]))
    return float(extrema.max()), float(residual), float(np.degrees(end))


def measure(directory, case):
    moving, fixed = case['groups'].values()
    count = len(moving)
    poses = case['samples'][:-1]
    if [p['f'] for p in poses] != list(range(0, 101, 2)) or case['samples'][-1]['f'] != 0:
        raise ValueError("Expected 51 opening samples and one reassembly")
    matrices = np.asarray([p['mats'] for p in poses]).reshape(
        len(poses), count + len(fixed), 4, 4
    ).transpose(0, 1, 3, 2)
    rest = matrices[0]
    relative = matrices @ np.linalg.inv(rest)
    if np.max(np.abs(relative[:, count:] - np.eye(4))) >= 1e-10:
        raise ValueError("The neighboring mesh moved during the test")
    if np.max(np.abs(relative[:, :count] - relative[:, :1])) >= 1e-10:
        raise ValueError("The selected cover did not move as one rigid group")
    sign = -1 if case['region'] == 'right-wing' else 1
    far, residual, degrees = farthest_support(relative[:, 0], world_vertices(directory, moving, rest[:count]), sign)
    near = float(np.min(sign * world_vertices(directory, fixed, rest[count:])[:, 0]))
    if near - far <= .001 or residual >= 1e-10:
        raise ValueError("The observed hinge failed its continuous clearance bound")
    return {
        'era': case['era'], 'region': case['region'], 'axis': 'x' if sign == 1 else '-x',
        'farthestMovingSupport': far, 'nearestFixedSupport': near, 'lowerBound': near - far,
        'angleDegrees': degrees, 'matrixResidual': residual,
        'sampledOpeningPositions': len(poses), 'maxHingeDrift': case['pivotDrift'],
        'reassemblyMatrixError': case['returnMatrixError'],
    }


if __name__ == '__main__':
    source = Path(sys.argv[1])
    capture = json.loads((source / 'capture.json').read_bytes())
    rows = [measure(source, case) for case in capture['cases']]
    report = {key: capture[key] for key in ['portable', 'script', 'model', 'gpu', 'errors']}
    report['rows'] = rows
    Path(sys.argv[2]).write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
