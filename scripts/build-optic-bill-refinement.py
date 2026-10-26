"""One local socket/cuff refinement from the preserved connected-head checkpoint.

Authored displacements are proposals, not measured source dimensions. No
materials, lens/core, crown, jaw, hook, neck or body edits are permitted.
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
EVIDENCE = Path.home() / 'OKH-Local/01_ChatGPT_Exports/murderbird-uncaged/evidence/visual-technical-acceptance/connected-head-correction'
BASE = EVIDENCE / 'attempt-01'
OUTPUT = EVIDENCE / 'optic-bill-refinement'
PINS = {
    'builder': '22e7e72b8425f7fcf91fcdf3e2a790da9488fcfed1599c5451ff295ffdfefa98',
    'maker': '00159f9df2478e678a2713627c186f3d2b9c18c8358660407a59fd0265064c33',
    'mechanic': 'c26b05b8d95b1707ae64eb1793d8a79b99aaa3afa30d1e19214b2165e82b732e',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def module(name):
    spec = importlib.util.spec_from_file_location('socket_' + name, ROOT / 'scripts' / name)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def selected_names():
    names = {'CGH18 formed dorsal bill root cuff'}
    for side in ('L', 'R'):
        names.update(prefix + side for prefix in (
            'CGH05 integrated optical seat ', 'CGO13 deep tapered cavity ',
            'CGO13 unequal stepped metal retainer ', 'CGH18 compact posterior bill root return '))
    return names


def bounds(obj):
    return [[min(v.co[i] for v in obj.data.vertices), max(v.co[i] for v in obj.data.vertices)] for i in range(3)]


def radial(obj):
    # The receiving concentric optic is centered here in its unchanged head frame.
    return [math.hypot(v.co.y - .005, v.co.z - .020) for v in obj.data.vertices]


def refine(scene):
    metrics = []
    for name in sorted(selected_names()):
        obj = scene.objects[name]
        assert obj.type == 'MESH' and not obj.parent
        before = bounds(obj)
        obj.data = obj.data.copy()
        socket = name.startswith(('CGH05 integrated optical seat ', 'CGO13 '))
        radii = radial(obj) if socket else []
        for vertex in obj.data.vertices:
            p = vertex.co
            if socket:
                # Slim the outer assembly, keeping the independent lens, inner
                # rings, aperture collar and core bit-exact and concentric.
                if name.startswith('CGH05 '):
                    scale, inner_depth, depth_factor = .84, .139, .45
                elif name.startswith('CGO13 deep '):
                    scale, inner_depth, depth_factor = .94, .140, .72
                else:
                    scale, inner_depth, depth_factor = .94, .1435, .62
                radius = math.hypot(p.y - .005, p.z - .020)
                if name.startswith('CGO13 unequal '):
                    # Preserve the .0372 aperture edge around the fixed .0354
                    # lens; uniform scaling could cover its outer glass rim.
                    new_radius = .0372 + max(0, radius - .0372) * .72
                    scale = new_radius / radius
                p.y = .005 + (p.y - .005) * scale
                p.z = .020 + (p.z - .020) * scale
                sign = -1 if p.x < 0 else 1
                p.x = sign * (inner_depth + (abs(p.x) - inner_depth) * depth_factor)
            else:
                # A shared smooth field forms an oblique saddle: rear center
                # rises/tucks beneath the forehead; outer shoulders taper down.
                # The lower cuff seam, distal hook and cheek opening stay fixed.
                rear = max(0, min(1, (p.y + .225) / .140))
                top = max(0, min(1, (p.z + .060) / .0884))
                side = min(1, abs(p.x) / .125)
                weight = rear * top
                p.z += weight * (.050 * (1 - side * side) - .012 * side * side)
                p.y += .018 * weight
                p.x *= 1 - .10 * weight
        obj.data.update()
        metrics.append({'object': name, 'before_bounds': before, 'after_bounds': bounds(obj),
                        'before_max_optic_radius': max(radii) if radii else None,
                        'after_max_optic_radius': max(radial(obj)) if socket else None})
    bpy.context.view_layer.update()
    return metrics


def run(args):
    source = BASE / args.era / ('murderbird-recursive-' + args.era + '.blend')
    assert sha(source) == PINS[args.era], 'Checkpoint native changed or unavailable'
    previous = module('build-connected-head-correction.py')
    for path, expected in previous.REFERENCES.items():
        assert sha(ROOT / path) == expected, 'Controlling reference changed'
    output = OUTPUT / 'candidate' / args.era
    output.mkdir(parents=True, exist_ok=False)
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
    strong = module('cg-supervised-head17.py')
    images = module('cg-supervised-preservation.py')
    before = strong.snap()
    frames = {o.name: [list(row) for row in o.matrix_world] for o in bpy.context.scene.objects}
    packed = images.packed_image_snapshot()
    metrics = refine(bpy.context.scene)
    untouched = set(before['objects']) - selected_names()

    def check():
        after = strong.snap()
        assert set(before['objects']) == set(after['objects']), 'Object set changed'
        assert all(before['objects'][n] == after['objects'][n] for n in untouched), 'Nonselected payload changed'
        assert before['visibility'] == after['visibility'], 'Visibility changed'
        assert before['materials'] == after['materials'] and before['images'] == after['images']
        assert all([list(row) for row in bpy.context.scene.objects[n].matrix_world] == matrix for n, matrix in frames.items())
        return images.verify_receiving_images(packed)

    check()
    native = output / source.name
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(native), relative_remap=False)
    bpy.ops.wm.open_mainfile(filepath=str(native), load_ui=False, use_scripts=False)
    packed_result = check()
    assert sha(source) == PINS[args.era]
    receipt = {'status': 'PASS - scoped preservation; owner likeness review pending', 'era': args.era,
               'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'baseline_revision': '87ad6532adf30f84c84b036632cb3e3ee077f8f3',
               'source_path': str(source), 'source_sha256': PINS[args.era],
               'native_path': str(native), 'native_sha256': sha(native),
               'authoring_script_sha256': sha(__file__), 'blender_version': bpy.app.version_string,
               'references': previous.REFERENCES, 'changed_allowlist': sorted(selected_names()),
               'nonselected_objects_checked': len(untouched), 'packed_images': packed_result,
               'metrics': metrics, 'limits': ['No every-RNA-field or whole-file byte identity claim.',
               'Local sculpt parameters are proposals, not approved measurements.',
               'No lens/core, crown, distal hook, jaw, neck, stance, breast or toe changes.',
               'No runtime promotion, animation, engineering or likeness acceptance.']}
    (output / 'preservation.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('OPTIC_BILL_SAVED', args.era, len(untouched), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--era', choices=tuple(PINS), required=True)
    run(parser.parse_args(sys.argv[sys.argv.index('--') + 1:]))
