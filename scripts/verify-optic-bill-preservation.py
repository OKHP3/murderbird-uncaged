"""Read-only saved-native verification of the nine-object socket/cuff pass."""
import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {
    'CGH05 integrated optical seat L', 'CGH05 integrated optical seat R',
    'CGO13 deep tapered cavity L', 'CGO13 deep tapered cavity R',
    'CGO13 unequal stepped metal retainer L', 'CGO13 unequal stepped metal retainer R',
    'CGH18 formed dorsal bill root cuff',
    'CGH18 compact posterior bill root return L', 'CGH18 compact posterior bill root return R',
}


def load(name):
    spec = importlib.util.spec_from_file_location('optic_postflight_' + name, ROOT / 'scripts' / name)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def structure(obj, strong):
    mesh = obj.data
    attributes = []
    for attr in mesh.attributes:
        if attr.name == 'position':
            continue
        field = {'FLOAT': 'value', 'INT': 'value', 'BOOLEAN': 'value', 'FLOAT_VECTOR': 'vector',
                 'FLOAT_COLOR': 'color', 'BYTE_COLOR': 'color', 'FLOAT2': 'vector',
                 'INT32_2D': 'value'}.get(attr.data_type)
        assert field, 'Unsupported attribute requires explicit verification: ' + attr.data_type
        attributes.append((attr.name, attr.domain, attr.data_type,
                           [strong.val(getattr(value, field)) for value in attr.data]))
    data = [obj.type, strong.val(obj.matrix_world), strong.val(obj.matrix_local),
            obj.parent.name if obj.parent else None, strong.properties(obj), strong.properties(mesh),
            [(m.name, m.type, strong.rna(m)) for m in obj.modifiers],
            [m.name if m else None for m in mesh.materials], len(mesh.vertices),
            [(tuple(p.vertices), p.material_index, p.use_smooth) for p in mesh.polygons],
            [(tuple(e.vertices), e.use_edge_sharp) for e in mesh.edges],
            [(uv.name, uv.active_render) for uv in mesh.uv_layers], attributes]
    return hashlib.sha256(repr(data).encode()).hexdigest()


def optic_metrics(scene):
    rows = []
    for side in ('L', 'R'):
        seat = scene.objects['CGH05 integrated optical seat ' + side]
        retainer = scene.objects['CGO13 unequal stepped metal retainer ' + side]
        lens = scene.objects['CGO13 recessed dark curved optical coating ' + side]
        radial = lambda obj: [math.hypot(v.co.y - .005, v.co.z - .020) for v in obj.data.vertices]
        rows.append({'side': side, 'seat_outer_radius': max(radial(seat)),
                     'seat_maximum_standoff_coordinate': max(abs(v.co.x) for v in seat.data.vertices),
                     'retainer_aperture_radius': min(radial(retainer)),
                     'lens_outer_radius': max(radial(lens))})
    return rows


def run(args):
    author = load('build-optic-bill-refinement.py')
    assert author.selected_names() == ALLOWED, 'Author scope differs from frozen verifier scope'
    strong = load('cg-supervised-head17.py')
    packed = load('cg-supervised-preservation.py')
    output = Path(args.out)
    assert not output.exists(), 'Preserve retained postflight evidence'
    results = []
    for era in ('builder', 'maker', 'mechanic'):
        source = author.BASE / era / ('murderbird-recursive-' + era + '.blend')
        native = author.OUTPUT / 'candidate' / era / source.name
        assert author.sha(source) == author.PINS[era]
        candidate_hash = author.sha(native)
        bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
        before = strong.snap()
        structs = {name: structure(bpy.context.scene.objects[name], strong) for name in ALLOWED}
        frames = {o.name: strong.val(o.matrix_world) for o in bpy.context.scene.objects}
        image_state = packed.packed_image_snapshot()
        optic_before = optic_metrics(bpy.context.scene)
        bpy.ops.wm.open_mainfile(filepath=str(native), load_ui=False, use_scripts=False)
        after = strong.snap()
        untouched = set(before['objects']) - ALLOWED
        assert set(before['objects']) == set(after['objects'])
        changed = [name for name in untouched if before['objects'][name] != after['objects'][name]]
        assert not changed and before['visibility'] == after['visibility']
        assert before['materials'] == after['materials'] and before['images'] == after['images']
        assert all(structure(bpy.context.scene.objects[name], strong) == digest for name, digest in structs.items())
        assert all(strong.val(bpy.context.scene.objects[name].matrix_world) == frame for name, frame in frames.items())
        crown = sorted(n for n in untouched if n.startswith('MBH01 swept crown lap '))
        assert len(crown) == 7
        optic_after = optic_metrics(bpy.context.scene)
        for first, last in zip(optic_before, optic_after):
            assert last['seat_outer_radius'] < first['seat_outer_radius']
            assert last['seat_maximum_standoff_coordinate'] < first['seat_maximum_standoff_coordinate']
            assert last['retainer_aperture_radius'] > last['lens_outer_radius']
            assert last['lens_outer_radius'] == first['lens_outer_radius']
        assert author.sha(source) == author.PINS[era] and author.sha(native) == candidate_hash
        results.append({'era': era, 'status': 'PASS', 'source_sha256': author.PINS[era],
                        'native_sha256': candidate_hash, 'nonselected_objects_checked': len(untouched),
                        'nonselected_payload_changes': changed, 'selected_structure_changes': [],
                        'all_visibility_and_transforms': 'exact', 'preserved_crown_panels': crown,
                        'packed_images': packed.verify_receiving_images(image_state),
                        'optic_before': optic_before, 'optic_after': optic_after})
        print('OPTIC_BILL_POSTFLIGHT_PASS', era, len(untouched), flush=True)
    output.write_text(json.dumps({'status': 'PASS', 'verifier_sha256': author.sha(__file__),
                                 'blender_version': bpy.app.version_string, 'results': results,
                                 'limits': ['Selected topology/UVs/material slots/modifiers/properties are exact; vertex coordinates alone may change.',
                                            'Supported fields only, not every Blender RNA field.',
                                            'Aperture radii and source preservation do not establish full three-dimensional clearance or artistic acceptance.']}, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', required=True)
    run(parser.parse_args(sys.argv[sys.argv.index('--') + 1:]))
