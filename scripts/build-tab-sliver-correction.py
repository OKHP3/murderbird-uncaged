"""One diagnosed tab/sliver pass from358d; no material or runtime changes."""
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
OUTPUT = HOME / 'tab-sliver-correction'
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
LIP_OLD_RADII = (.0576, .0564, .0528, .0516)
LIP_RADII = (.048384, .047376, .044352, .043344)
LIP_DEPTH = (.1507, .1516, .15115, .1498)
RETAINER_RADII = (.044112, .0427296, .0403104, .03936, .0372)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(name):
    spec = importlib.util.spec_from_file_location('tab_sliver_' + name, ROOT / 'scripts' / name)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def selected_names():
    names = {'CGH18 formed dorsal bill root cuff'}
    for side in ('L', 'R'):
        names.update(prefix + side for prefix in ('CGH05 thin inset retaining lip ',
                    'CGO13 unequal stepped metal retainer ', 'CGH18 compact posterior bill root return '))
    return names


def smooth(value):
    value = max(0, min(1, value))
    return value * value * (3 - 2 * value)


def nearest(radius, rings):
    index = min(range(len(rings)), key=lambda i: abs(radius - rings[i]))
    assert abs(radius - rings[index]) < 1e-6, 'Unrecognized pinned cross-section'
    return index


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
            if name.startswith('CGH05 '):
                # Fit the unscaled lip to the reduced seat while keeping it
                # in front as a retaining cover, rather than opening the rim.
                radius = math.hypot(p.y - .005, p.z - .020)
                ring = nearest(radius, LIP_OLD_RADII)
                factor = LIP_RADII[ring] / radius
                p.y = .005 + (p.y - .005) * factor
                p.z = .020 + (p.z - .020) * factor
                p.x = math.copysign(LIP_DEPTH[ring], p.x)
            elif name.startswith('CGO13 '):
                # The diagnosed silver face is the abrupt inner2->3 fold.
                # Preserve every radius, aperture and outer crest. A continuous
                # inner bevel keeps the retainer in front of the fixed cavity.
                radius = math.hypot(p.y - .005, p.z - .020)
                ring = nearest(radius, RETAINER_RADII)
                if ring == 3:
                    blend = (radius - RETAINER_RADII[4]) / (RETAINER_RADII[2] - RETAINER_RADII[4])
                    p.x = math.copysign(.1435 + (.14815 - .1435) * blend, p.x)
            else:
                # Fold side/rear upper tails only. The central saddle, lower
                # seam and forward root are exactly outside this smooth field.
                weight = (smooth((abs(p.x) - .040) / .040)
                          * smooth((p.y + .185) / .065)
                          * smooth((p.z + .005) / .040))
                if weight:
                    p.y -= .022 * weight
                    p.z -= .026 * weight
                    p.x *= 1 - .10 * weight
            moved += tuple(p) != before
        obj.data.update()
        metrics.append({'object': name, 'cage_vertices_moved': moved, 'cage_vertices': len(obj.data.vertices)})
    bpy.context.view_layer.update()
    return metrics


def run(args):
    source = BASE / args.era / ('murderbird-recursive-' + args.era + '.blend')
    assert sha(source) == PINS[args.era], '358d checkpoint native changed/unavailable'
    for path, expected in REFERENCES.items():
        assert sha(ROOT / path) == expected, 'Pinned reference changed/unavailable'
    candidate_base = Path(args.out).resolve() if args.out else OUTPUT / 'candidate'
    assert candidate_base.resolve().is_relative_to(OUTPUT.resolve()), 'Use this approved purpose home'
    output = candidate_base / args.era
    output.mkdir(parents=True, exist_ok=False)
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
    strong, images = load('cg-supervised-head17.py'), load('cg-supervised-preservation.py')
    before = strong.snap()
    packed = images.packed_image_snapshot()
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
    receipt = {'status': 'PASS - scoped preservation only; visual and owner review remain separate',
               'era': args.era, 'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'baseline_revision': '358d924afbf79ad1fc3dee66392db96c08554fd5',
               'source_path': str(source), 'source_sha256': PINS[args.era],
               'native_path': str(native), 'native_sha256': sha(native),
               'authoring_script_sha256': sha(__file__), 'blender_version': bpy.app.version_string,
               'references': REFERENCES, 'allowed_objects': sorted(selected_names()),
               'nonselected_objects_checked': len(untouched), 'packed_images': packed_result, 'metrics': metrics,
               'limits': ['Seven vertex-only object edits; no source material/pixel replacement.',
                          'Sculpt/profile values are proposals in study units, not source measurements.',
                          'No pose, stance, breast, toe, lens/core, crown, hook, jaw, outer seat or cavity changes.',
                          'No full3D clearance, engineering, runtime promotion, likeness or performance acceptance.']}
    with (output / 'preservation.json').open('x') as stream:
        json.dump(receipt, stream, indent=2)
    print('TAB_SLIVER_SAVED', args.era, len(untouched), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--era', choices=tuple(PINS), required=True)
    parser.add_argument('--out', help='Fresh candidate root inside the approved tab-sliver purpose home')
    run(parser.parse_args(sys.argv[sys.argv.index('--') + 1:]))
