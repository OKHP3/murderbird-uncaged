"""Read-only native postflight; includes nonselected visibility and saved files."""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location('head_postflight_' + name, ROOT / 'scripts' / name)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def run(args):
    author = load('build-connected-head-correction.py')
    strong = load('cg-supervised-head17.py')
    images = load('cg-supervised-preservation.py')
    output = Path(args.out)
    if output.exists():
        raise FileExistsError('Preserve previous verification')
    rows = []
    for era in ('builder', 'maker', 'mechanic'):
        original = ROOT / 'assets/audit/cg-recursive-three-loop01/loop03/delivery/retained04' / era / ('murderbird-recursive-' + era + '.blend')
        native = Path(args.candidate) / era / ('murderbird-recursive-' + era + '.blend')
        assert author.sha(original) == author.PINS[era]
        candidate_hash = author.sha(native)
        bpy.ops.wm.open_mainfile(filepath=str(original), load_ui=False, use_scripts=False)
        before = strong.snap()
        packed = images.packed_image_snapshot()
        frame = [list(row) for row in bpy.context.scene.objects['CG2b head frame'].matrix_world]
        source_frames = {name: [list(row) for row in bpy.context.scene.objects[name].matrix_world]
                         for name in author.selected_names()}
        bpy.ops.wm.open_mainfile(filepath=str(native), load_ui=False, use_scripts=False)
        after = strong.snap()
        untouched = set(before['objects']) - author.selected_names()
        changed = sorted(name for name in untouched if before['objects'][name] != after['objects'].get(name))
        visibility = sorted(name for name in untouched if before['visibility'][name] != after['visibility'].get(name))
        materials = sorted(name for name, digest in before['materials'].items() if digest != after['materials'].get(name))
        assert set(before['materials']) == set(after['materials'])
        packed_result = images.verify_receiving_images(packed)
        added = set(after['objects']) - set(before['objects'])
        assert len(added) == 7 and all(name.startswith('MBH01 swept crown lap ') for name in added)
        assert not (set(before['objects']) - set(after['objects'])), 'Original object missing'
        # Compare each existing object to its own saved source transform. The
        # retained head objects are not all bit-identical to the frame empty.
        changed_frames = [name for name, matrix in source_frames.items()
                          if [list(row) for row in bpy.context.scene.objects[name].matrix_world] != matrix]
        crown_frame = source_frames['CGRS04 source-scale frontal crown appearance']
        changed_added_frames = [name for name in added
                                if [list(row) for row in bpy.context.scene.objects[name].matrix_world] != crown_frame]
        assert not changed_frames and not changed_added_frames, (changed_frames, changed_added_frames)
        assert bpy.context.scene.objects['CGRS04 source-scale frontal crown appearance'].hide_render
        assert not changed and not visibility and not materials
        assert author.sha(original) == author.PINS[era] and author.sha(native) == candidate_hash
        rows.append({'era': era, 'status': 'PASS', 'source_sha256': author.PINS[era],
                     'native_sha256': candidate_hash, 'nonselected_objects_checked': len(untouched),
                     'nonselected_payload_changes': changed, 'nonselected_visibility_changes': visibility,
                     'material_graph_changes': materials, 'packed_images': packed_result,
                     'new_crown_panels': sorted(added), 'head_frame': frame,
                     'limits': 'Supported mesh attributes/transforms and graph fields are digested; no claim that every Blender RNA field or whole file bytes are identical.'})
        print('HEAD_POSTFLIGHT_PASS', era, len(untouched), flush=True)
    output.write_text(json.dumps({'status': 'PASS', 'blender_version': bpy.app.version_string,
                                 'verifier_sha256': author.sha(__file__), 'results': rows}, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', required=True)
    parser.add_argument('--out', required=True)
    run(parser.parse_args(sys.argv[sys.argv.index('--') + 1:]))
