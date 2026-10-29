"""Independent saved-file scope/profile replay for the tab/sliver correction."""
import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {'CGH05 thin inset retaining lip L', 'CGH05 thin inset retaining lip R',
           'CGO13 unequal stepped metal retainer L', 'CGO13 unequal stepped metal retainer R',
           'CGH18 formed dorsal bill root cuff', 'CGH18 compact posterior bill root return L',
           'CGH18 compact posterior bill root return R'}


def load(name):
    spec = importlib.util.spec_from_file_location('tab_postflight_' + name, ROOT / 'scripts' / name)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def coords(scene):
    return {name: [tuple(v.co) for v in scene.objects[name].data.vertices] for name in ALLOWED}


def radius(point):
    return math.hypot(point[1] - .005, point[2] - .020)


def profiles(scene):
    result = []
    for side in ('L', 'R'):
        lip = [v.co for v in scene.objects['CGH05 thin inset retaining lip ' + side].data.vertices]
        seat = [v.co for v in scene.objects['CGH05 integrated optical seat ' + side].data.vertices]
        retainer = [v.co for v in scene.objects['CGO13 unequal stepped metal retainer ' + side].data.vertices]
        lens = [v.co for v in scene.objects['CGO13 recessed dark curved optical coating ' + side].data.vertices]
        bands = {}
        for point in retainer:
            bands.setdefault(round(radius(point), 7), []).append(abs(point.x))
        depths = [(r, sum(values) / len(values)) for r, values in sorted(bands.items(), reverse=True)]
        assert len(depths) == 5
        assert all(a[1] >= b[1] for a, b in zip(depths[1:], depths[2:])), 'Inner return reverses direction'
        slope_a = (depths[2][1] - depths[3][1]) / (depths[2][0] - depths[3][0])
        slope_b = (depths[3][1] - depths[4][1]) / (depths[3][0] - depths[4][0])
        assert abs(slope_a - slope_b) < .001, 'Inner bevel is not continuous'
        assert min(map(radius, seat)) < min(map(radius, lip)) < max(map(radius, lip)) < max(map(radius, seat))
        assert max(abs(p.x) for p in lip) > max(abs(p.x) for p in seat), 'Retaining cover recessed behind its seat'
        assert min(map(radius, retainer)) > max(map(radius, lens))
        result.append({'side': side, 'lip_radius': [min(map(radius, lip)), max(map(radius, lip))],
                       'lip_maximum_outward_coordinate': max(abs(p.x) for p in lip),
                       'seat_maximum_outward_coordinate': max(abs(p.x) for p in seat),
                       'retainer_depth_profile': depths, 'lens_radius': max(map(radius, lens))})
    return result


def run(args):
    author = load('build-tab-sliver-correction.py')
    assert author.selected_names() == ALLOWED
    strong, images = load('cg-supervised-head17.py'), load('cg-supervised-preservation.py')
    structure = load('verify-optic-bill-preservation.py').structure
    candidate = Path(args.candidate).resolve() if args.candidate else author.OUTPUT / 'candidate'
    output = Path(args.out).resolve()
    assert candidate.resolve().is_relative_to(author.OUTPUT.resolve())
    assert output.is_relative_to(author.OUTPUT.resolve()) and not output.exists()
    results = []
    for era in ('builder', 'maker', 'mechanic'):
        source = author.BASE / era / ('murderbird-recursive-' + era + '.blend')
        native = candidate / era / source.name
        assert author.sha(source) == author.PINS[era]
        native_hash = author.sha(native)
        bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
        before = strong.snap()
        old_coords = coords(bpy.context.scene)
        structs = {n: structure(bpy.context.scene.objects[n], strong) for n in ALLOWED}
        frames = {o.name: strong.val(o.matrix_world) for o in bpy.context.scene.objects}
        packed = images.packed_image_snapshot()
        bpy.ops.wm.open_mainfile(filepath=str(native), load_ui=False, use_scripts=False)
        after = strong.snap()
        new_coords = coords(bpy.context.scene)
        untouched = set(before['objects']) - ALLOWED
        changes = [n for n in untouched if before['objects'][n] != after['objects'].get(n)]
        assert set(before['objects']) == set(after['objects']) and not changes
        assert before['materials'] == after['materials'] and before['images'] == after['images']
        assert before['visibility'] == after['visibility']
        assert all(strong.val(bpy.context.scene.objects[n].matrix_world) == matrix for n, matrix in frames.items())
        assert all(structure(bpy.context.scene.objects[n], strong) == digest for n, digest in structs.items())
        protected_vertices = 0
        for name in ALLOWED:
            assert len(old_coords[name]) == len(new_coords[name])
            for old, new in zip(old_coords[name], new_coords[name]):
                if name.startswith('CGH18 '):
                    if abs(old[0]) <= .040 or old[1] <= -.185 or old[2] <= -.005:
                        assert old == new, 'Central saddle/seam/forward root changed'
                        protected_vertices += 1
                elif name.startswith('CGO13 '):
                    assert old[1:] == new[1:], 'Retainer radii/center changed'
                    if min(abs(radius(old) - r) for r in (.044112, .0427296, .0403104, .0372)) < 1e-6:
                        assert old == new, 'Outer course, inner return or aperture moved'
                        protected_vertices += 1
        crown = sorted(n for n in untouched if n.startswith('MBH01 swept crown lap '))
        assert len(crown) == 7
        profile_result = profiles(bpy.context.scene)
        packed_result = images.verify_receiving_images(packed)
        assert author.sha(source) == author.PINS[era] and author.sha(native) == native_hash
        results.append({'era': era, 'status': 'PASS', 'source_sha256': author.PINS[era],
                        'native_sha256': native_hash, 'nonselected_objects_checked': len(untouched),
                        'nonselected_payload_changes': changes, 'selected_structure_changes': [],
                        'protected_selected_vertices': protected_vertices,
                        'visibility_transforms': 'exact', 'preserved_crown_panels': crown,
                        'profiles': profile_result, 'packed_images': packed_result})
        print('TAB_SLIVER_POSTFLIGHT_PASS', era, len(untouched), flush=True)
    with output.open('x') as stream:
        json.dump({'status': 'PASS', 'verifier_sha256': author.sha(__file__),
                   'blender_version': bpy.app.version_string, 'results': results,
                   'limits': ['Supported attributes/graph fields, not every Blender RNA property.',
                              'Profile bounds and monotonicity do not establish full3D clearance or zero visible artifacts.',
                              'Matched visual observations and Jamie acceptance remain separate.']}, stream, indent=2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', help='Explicit replay candidate root inside this purpose home')
    parser.add_argument('--out', required=True)
    run(parser.parse_args(sys.argv[sys.argv.index('--') + 1:]))
