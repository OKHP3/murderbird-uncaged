"""Two-pose read-only optic-assembly versus jaw screen for V14 attempt-specific."""
from pathlib import Path
import datetime
import hashlib
import json
import runpy
import shutil
import sys

import bpy
from mathutils import Matrix


ROOT = Path(__file__).resolve().parents[1]
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--native', required=True, help='repository-relative .blend path')
parser.add_argument('--expected-sha256', required=True)
parser.add_argument('--out', required=True, help='new repository-relative output directory')
args = parser.parse_args(argv)
NATIVE = (ROOT / args.native).resolve(strict=True)
OUT = (ROOT / args.out).resolve()
EXPECTED = args.expected_sha256.lower()
assert NATIVE.is_relative_to(ROOT) and OUT.is_relative_to(ROOT), 'Input and output must stay within repository'
assert len(EXPECTED) == 64 and all(c in '0123456789abcdef' for c in EXPECTED), 'Expected a lowercase SHA-256'
assert not OUT.exists(), 'Refusing to overwrite an existing output directory'
SURFACE_HELPER = ROOT / 'scripts/diagnose-native-regional-clearance.py'
STRICT_KERNEL = ROOT / 'assets/audit/cervical-construction-study-v1/attempt-07/actual-runtime-joint-clearance-v1/executed-review.py'
ANGLES = (0.0, 0.32)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


assert sha(NATIVE) == EXPECTED, 'Native SHA mismatch'
assert Path(bpy.data.filepath).resolve() == NATIVE.resolve(), 'Blender opened a different native'
assert not (OUT / 'optic-jaw-fit.json').exists(), 'Refusing to overwrite fit receipt'
assert not (OUT / 'executed-optic-jaw-fit.source.py').exists(), 'Refusing to overwrite source snapshot'
surface_api = runpy.run_path(str(SURFACE_HELPER), run_name='v14_optic_jaw_surface_helpers')
kernel_api = runpy.run_path(str(STRICT_KERNEL), run_name='v14_optic_jaw_strict_kernel')
surface = surface_api['surface']
bounds_overlap = surface_api['bounds_overlap']
proper = kernel_api['proper_crossing_receipt']

objects = {obj.name: obj for obj in bpy.data.objects}
jaw = objects.get('jaw')
head = objects.get('head')
assert jaw and head and jaw.type == 'EMPTY' and head.type == 'EMPTY'
optic_objects = []
for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
    role = obj.get('surfaceRole')
    region = obj.get('region')
    name = obj.name
    if region == 'optic' and role in {'bearing', 'recess', 'optic'}:
        category = {'bearing': 'bearing', 'recess': 'housing', 'optic': 'lens'}[role]
        optic_objects.append((category, obj))
    elif name in {'Forged orbital mounting plate -1', 'Forged orbital mounting plate 1'}:
        optic_objects.append(('socket', obj))
    elif name.startswith('Orbital mounting fixing '):
        optic_objects.append(('socket-fixing', obj))
jaw_objects = []
for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
    if obj.name.startswith('Forked forged mandible '):
        category = 'jaw-fork'
    elif obj.name == 'Distal mandible bridge':
        category = 'jaw-bridge'
    elif obj.name.startswith('Coaxial mandible journal'):
        category = 'fixed-journal'
    elif obj.name.startswith('Mandible journal cap'):
        category = 'moving-journal-cap'
    else:
        continue
    jaw_objects.append((category, obj))
assert optic_objects and jaw_objects, 'Selected optic or jaw surface inventory is empty'
assert any(kind == 'lens' for kind, _ in optic_objects)
assert any(kind == 'housing' for kind, _ in optic_objects)
assert any(kind == 'bearing' for kind, _ in optic_objects)
assert any(kind == 'jaw-fork' for kind, _ in jaw_objects)
assert any(kind == 'fixed-journal' for kind, _ in jaw_objects)
assert any(kind == 'moving-journal-cap' for kind, _ in jaw_objects)

depsgraph = bpy.context.evaluated_depsgraph_get()
records = []
for angle in ANGLES:
    jaw.rotation_euler.x = angle
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    optic_surfaces = {obj.name: surface(obj, depsgraph) for _, obj in optic_objects}
    jaw_surfaces = {obj.name: surface(obj, depsgraph) for _, obj in jaw_objects}
    pairs = []
    for optic_kind, optic_obj in optic_objects:
        a = optic_surfaces[optic_obj.name]
        if a is None:
            continue
        for jaw_kind, jaw_obj in jaw_objects:
            b = jaw_surfaces[jaw_obj.name]
            if b is None or not bounds_overlap(a, b):
                continue
            candidates = a['tree'].overlap(b['tree'])
            if not candidates:
                continue
            proof = proper(a, b, candidates, Matrix.Identity(4), Matrix.Identity(4))
            strict = bool(proof['confirmedSubjectTriangleCount'] or proof['confirmedTargetTriangleCount'])
            pairs.append({
                'opticRole': optic_kind, 'opticMesh': optic_obj.name,
                'jawRole': jaw_kind, 'jawMesh': jaw_obj.name,
                'bvhTrianglePairCandidates': len(candidates),
                'strictNoncoplanarCrossing': strict,
                'strictCrossingReceipt': proof if strict else None,
            })
    records.append({
        'jawLocalRotationXRad': angle,
        'jawWorldMatrix': [[round(float(jaw.matrix_world[r][c]), 9) for c in range(4)] for r in range(4)],
        'bvhCandidatePairCount': sum(row['bvhTrianglePairCandidates'] > 0 for row in pairs),
        'strictCrossingPairCount': sum(row['strictNoncoplanarCrossing'] for row in pairs),
        'strictPairs': [row for row in pairs if row['strictNoncoplanarCrossing']],
    })

receipt = {
    'schema': 'v14-optic-jaw-fit/v1',
    'arguments': {'native': args.native, 'expectedSha256': EXPECTED, 'out': args.out},
    'status': 'two-pose read-only native surface screen; no art acceptance claim',
    'generatedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'native': {'path': NATIVE.relative_to(ROOT).as_posix(), 'sha256': sha(NATIVE), 'bytes': NATIVE.stat().st_size},
    'jawPivot': {'name': jaw.name, 'localAxis': 'Euler X', 'samplesRad': list(ANGLES)},
    'opticAssembly': [{'role': role, 'mesh': obj.name, 'owner': obj.parent.name if obj.parent else None}
                      for role, obj in optic_objects],
    'jawAssembly': [{'role': role, 'mesh': obj.name, 'owner': obj.parent.name if obj.parent else None}
                    for role, obj in jaw_objects],
    'inputs': {
        'surfaceHelper': {'path': SURFACE_HELPER.relative_to(ROOT).as_posix(), 'sha256': sha(SURFACE_HELPER)},
        'strictKernel': {'path': STRICT_KERNEL.relative_to(ROOT).as_posix(), 'sha256': sha(STRICT_KERNEL)},
        'diagnostic': {'path': Path(__file__).resolve().relative_to(ROOT).as_posix(), 'sha256': sha(__file__)},
        'blenderVersion': bpy.app.version_string,
    },
    'samples': records,
    'limits': [
        'Only jaw local X rotation at 0 and 0.32 radians was sampled.',
        'The screen compares selected socket/mount, bearing, passive housing, active lens, jaw fork, bridge and journal/cap surfaces.',
        'Strict noncoplanar triangle crossings are reported; BVH candidates alone are not crossings.',
        'Containment, continuous motion, contact pressure, material appearance, processing-rack narrowing and full-system clearance are not tested.',
        'No native data was saved or modified.',
    ],
}
OUT.mkdir(parents=True)
with (OUT / 'executed-optic-jaw-fit.source.py').open('xb') as stream:
    stream.write(Path(__file__).resolve().read_bytes())
with (OUT / 'optic-jaw-fit.json').open('x') as stream:
    stream.write(json.dumps(receipt, indent=2) + '\n')
assert sha(NATIVE) == EXPECTED, 'Native changed during read-only fit screen'
print(json.dumps({'nativeSha256': EXPECTED,
                  'samples': [{'jawLocalRotationXRad': row['jawLocalRotationXRad'],
                              'bvhCandidatePairCount': row['bvhCandidatePairCount'],
                              'strictCrossingPairCount': row['strictCrossingPairCount']}
                             for row in records]}, indent=2))
