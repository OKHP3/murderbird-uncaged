"""Independent saved-file scope replay; profiles do not grant visual acceptance."""
import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {'CGH18 formed dorsal bill root cuff',
           'CGH18 compact posterior bill root return L', 'CGH18 compact posterior bill root return R',
           'CGH05 thin inset retaining lip L', 'CGH05 thin inset retaining lip R'}


def load(name):
    spec = importlib.util.spec_from_file_location('gap_check_' + name, ROOT / 'scripts' / name)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def run(args):
    author = load('build-bill-root-optic-gap-correction.py')
    strong, images = load('cg-supervised-head17.py'), load('cg-supervised-preservation.py')
    structure = load('verify-optic-bill-preservation.py').structure
    assert author.selected_names() == ALLOWED
    output = Path(args.out).resolve()
    assert output.is_relative_to(author.OUTPUT.resolve()) and not output.exists()
    rows = []
    for era in ('builder', 'maker', 'mechanic'):
        source = author.BASE / era / ('murderbird-recursive-' + era + '.blend')
        native = author.OUTPUT / 'candidate' / era / source.name
        assert author.sha(source) == author.PINS[era]
        native_sha = author.sha(native)
        bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
        before = strong.snap()
        old = {n: [tuple(v.co) for v in bpy.context.scene.objects[n].data.vertices] for n in ALLOWED}
        structs = {n: structure(bpy.context.scene.objects[n], strong) for n in ALLOWED}
        frames = {o.name: strong.val(o.matrix_world) for o in bpy.context.scene.objects}
        packed = images.packed_image_snapshot()
        bpy.ops.wm.open_mainfile(filepath=str(native), load_ui=False, use_scripts=False)
        after = strong.snap()
        untouched = set(before['objects']) - ALLOWED
        assert set(before['objects']) == set(after['objects'])
        assert all(before['objects'][n] == after['objects'][n] for n in untouched)
        assert before['materials'] == after['materials'] and before['images'] == after['images']
        assert before['visibility'] == after['visibility']
        assert all(strong.val(bpy.context.scene.objects[n].matrix_world) == m for n, m in frames.items())
        assert all(structure(bpy.context.scene.objects[n], strong) == m for n, m in structs.items())
        protected = 0
        changed = {}
        for name in ALLOWED:
            new = [tuple(v.co) for v in bpy.context.scene.objects[name].data.vertices]
            assert len(old[name]) == len(new)
            changed[name] = sum(a != b for a, b in zip(old[name], new))
            for a, b in zip(old[name], new):
                if name.startswith('CGH05 '):
                    assert a[1:] == b[1:], 'Lip radii/center changed'
                elif abs(a[0]) <= .015 or a[1] <= -.185 or a[2] <= -.005:
                    assert a == b, 'Protected central saddle/forward/lower seam changed'
                    protected += 1
        crown = [n for n in untouched if n.startswith('MBH01 swept crown lap ')]
        assert len(crown) == 7
        packed_result = images.verify_receiving_images(packed)
        assert author.sha(source) == author.PINS[era] and author.sha(native) == native_sha
        rows.append({'era': era, 'status': 'PASS', 'source_sha256': author.PINS[era],
                     'native_sha256': native_sha, 'nonselected_objects_checked': len(untouched),
                     'changed_cage_vertices': changed, 'protected_selected_vertices': protected,
                     'lip_radii_centers': 'exact', 'visibility_transforms': 'exact',
                     'selected_structure': 'exact', 'packed_images': packed_result,
                     'protected_crown_panels': sorted(crown)})
        print('ROOT_GAP_POSTFLIGHT_PASS', era, len(untouched), flush=True)
    with output.open('x') as stream:
        json.dump({'status': 'PASS', 'verifier_sha256': author.sha(__file__),
                   'results': rows, 'limits': ['Supported payload fields, not every Blender RNA property.',
                   'No geometry-ray, visual likeness, performance, engineering or owner acceptance implied.']}, stream, indent=2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    run(parser.parse_args(sys.argv[sys.argv.index('--') + 1:]))
