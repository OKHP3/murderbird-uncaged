"""One owner-selected root/optic continuity pass, directly from358d native pins.

Lens, retainer, crown and body stay fixed; the outer dark socket backing expands. Study-unit coordinates are
an artistic proposal, not source measurements or engineering tolerances.
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
HOME = Path.home() / 'OKH-Local/01_ChatGPT_Exports/murderbird-uncaged/evidence/visual-technical-acceptance/connected-head-correction'
BASE = HOME / 'optic-bill-refinement/candidate'
OUTPUT = HOME / 'root-optic-continuity'
PINS = {
    'builder': '7e10d8b5bbb8a94627d463d86ff393dff138e4cbe6853202b37c897c62e61486',
    'maker': '87ad807038df0bf2d5ddb55ee40ec7702be54ca18c8956579ccbacdb0a3aa12f',
    'mechanic': '39cbba9a6e7c1f7059f49440ea7fee1101975d165bd5c66ebb3a18bde58681f6',
}
REFERENCES = {
    'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg':
        '645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114',
    'context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png':
        '47658dba6496f2c8594a40ad412a8bfaa087939e90044d1597329a27ca68d4e9',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(name):
    spec = importlib.util.spec_from_file_location('root_gap_' + name, ROOT / 'scripts' / name)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def selected_names():
    return {'CGH18 formed dorsal bill root cuff'} | {
        prefix + side for side in ('L', 'R') for prefix in
        ('CGH05 thin inset retaining lip ', 'CGH05 integrated optical seat ', 'CGH18 compact posterior bill root return ')}


def smooth(value):
    value = max(0, min(1, value))
    return value * value * (3 - 2 * value)



def refine(scene):
    metrics = []
    for name in sorted(selected_names()):
        obj = scene.objects[name]
        assert obj.type == 'MESH' and not obj.parent
        obj.data = obj.data.copy()
        moved = 0
        for vertex in obj.data.vertices:
            p = vertex.co
            before = tuple(p)
            if name.startswith('CGH05 thin '):
                radius = math.hypot(p.y - .005, p.z - .020)
                rings = (.0576, .0564, .0528, .0516)
                ring = min(range(4), key=lambda i: abs(radius - rings[i]))
                assert abs(radius - rings[ring]) < 1e-6
                # The full baseline radius covers the outer socket seam.
                # Only depth changes; shrinking this rim opened the prior trial.
                p.x = math.copysign((.1488, .1497, .1488, .1469)[ring], p.x)
            elif name.startswith('CGH05 integrated '):
                radius = math.hypot(p.y - .005, p.z - .020)
                # Expand only the existing dark outer backing behind the lip.
                # Inner courses, aperture, retainer and glass are untouched.
                if abs(radius - .053424) < 1e-6:
                    scale = .068 / radius
                    p.y = .005 + (p.y - .005) * scale
                    p.z = .020 + (p.z - .020) * scale
            else:
                # Compress the raised upper cuff/returns continuously, including
                # the narrow central tips left tall by the prior lateral field.
                # Lower seam and the entire distal hook remain unmodified.
                rise = max(0, p.z + .012)
                p.z -= .72 * rise * smooth(rise / .025)
            moved += tuple(p) != before
        obj.data.update()
        metrics.append({'object': name, 'cage_vertices_moved': moved,
                        'cage_vertices': len(obj.data.vertices)})
    bpy.context.view_layer.update()
    return metrics


def run(args):
    source = BASE / args.era / ('murderbird-recursive-' + args.era + '.blend')
    assert sha(source) == PINS[args.era], '358d native pin unavailable/changed'
    reference_root = Path(args.reference_root).resolve()
    for path, expected in REFERENCES.items():
        assert sha(reference_root / path) == expected, 'Pinned original unavailable/changed'
    output = OUTPUT / 'candidate' / args.era
    output.mkdir(parents=True, exist_ok=False)
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
    strong, images = load('cg-supervised-head17.py'), load('cg-supervised-preservation.py')
    before, packed = strong.snap(), images.packed_image_snapshot()
    frames = {o.name: strong.val(o.matrix_world) for o in bpy.context.scene.objects}
    metrics = refine(bpy.context.scene)
    untouched = set(before['objects']) - selected_names()

    def check():
        after = strong.snap()
        assert set(before['objects']) == set(after['objects'])
        assert all(before['objects'][n] == after['objects'][n] for n in untouched)
        assert before['visibility'] == after['visibility']
        assert before['materials'] == after['materials'] and before['images'] == after['images']
        assert all(strong.val(bpy.context.scene.objects[n].matrix_world) == matrix for n, matrix in frames.items())
        return images.verify_receiving_images(packed)

    check()
    native = output / source.name
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(native), relative_remap=False)
    bpy.ops.wm.open_mainfile(filepath=str(native), load_ui=False, use_scripts=False)
    packed_result = check()
    assert sha(source) == PINS[args.era]
    receipt = {'status': 'PASS - preservation only; visual/owner acceptance separate',
               'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'baseline_revision': '358d924afbf79ad1fc3dee66392db96c08554fd5',
               'era': args.era, 'source_path': str(source), 'source_sha256': PINS[args.era],
               'native_path': str(native), 'native_sha256': sha(native),
               'authoring_script_sha256': sha(__file__), 'blender_version': bpy.app.version_string,
               'reference_root': str(reference_root), 'references': REFERENCES,
               'allowed_objects': sorted(selected_names()), 'metrics': metrics,
               'nonselected_objects_checked': len(untouched), 'packed_images': packed_result,
               'limits': ['Coordinates only on seven objects; lip radii and inner socket courses fixed.',
                          'No pose, stance, breast, toes, crown, hook, jaw or material changes.',
                          'No full appearance parity, likeness, mechanics or performance acceptance.']}
    with (output / 'preservation.json').open('x') as stream:
        json.dump(receipt, stream, indent=2)
    print('ROOT_CONTINUITY_SAVED', args.era, len(untouched), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--era', choices=tuple(PINS), required=True)
    parser.add_argument('--reference-root', required=True, help='Existing checkout holding exact original binaries')
    run(parser.parse_args(sys.argv[sys.argv.index('--') + 1:]))
