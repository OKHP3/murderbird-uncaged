"""One owner-selected connected-head pass on retained04; no runtime promotion.

Run in Blender with --python-exit-code 1 and --disable-autoexec. New review
natives belong in the explicit approved evidence home, never a frozen tree.
All existing non-head payloads, material graphs and packed pixels must survive.
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    'maker': 'bee3118c8a50ee672cdc221f852097deba74ce8efb9434e25219c57168721468',
    'mechanic': '4f9dbbcbb6abfa722e275e1e4646ef75ed09d54aac443fb7650f11cd9feb47bc',
    'builder': '9de7c4d1c9ac158135f9f846af61683528e00340a708820b2cfe1d942acc54d5',
}
REFERENCES = {
    'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg':
        '645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114',
    'context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png':
        '47658dba6496f2c8594a40ad412a8bfaa087939e90044d1597329a27ca68d4e9',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def module(name):
    path = ROOT / 'scripts' / name
    spec = importlib.util.spec_from_file_location('connected_' + path.stem, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def selected_names():
    names = {'CGRS04 source-scale frontal crown appearance',
             'CGH18 formed dorsal bill root cuff', 'CGH18 formed distal hooked bill plate'}
    for side in ('L', 'R'):
        names.update({
            'CGH05 integrated optical seat ' + side,
            'CGH06 connected under-eye bill-root cheek sheet ' + side,
            'CGH06 substantial swept plated mandible ' + side,
            'CGH18 compact posterior bill root return ' + side,
        })
        for label in ('deep tapered cavity', 'unequal stepped metal retainer',
                      'recessed dark curved optical coating', 'upper partial bronze retaining ring',
                      'lower partial metal retaining ring', 'small core aperture collar',
                      'small recessed awakened core'):
            names.add('CGO13 ' + label + ' ' + side)
    for side in ('near', 'far'):
        names.update('CGH17 broad curved brow course ' + side + ' ' + str(index) for index in range(3))
    return names


def crown_panels(scene, original):
    """Clip the existing UV-bearing cap into unequal rear-tapering lap panels.

    This preserves the original surface/material mapping instead of replacing
    it with an untextured helmet or a uniform stack of transverse bands.
    """
    shapes = [
        ('center', [(-.030, -.159), (.030, -.159), (.044, -.055), (.012, .140),
                    (-.012, .140), (-.044, -.055)], .0010),
    ]
    side_shapes = [
        ('frontal', [(.025, -.159), (.100, -.155), (.158, -.085), (.150, .005),
                     (.105, -.012), (.035, -.055)], .0020),
        ('middle', [(.030, -.075), (.130, -.080), (.158, -.025), (.145, .090),
                    (.100, .150), (.065, .070)], .0045),
        ('posterior', [(.025, .015), (.115, .005), (.150, .080), (.110, .180),
                       (.035, .100)], .0070),
    ]
    for side, sign in [('left', -1), ('right', 1)]:
        for name, polygon, lift in side_shapes:
            polygon = [(sign * x, y) for x, y in polygon]
            if sign < 0:
                polygon.reverse()
            shapes.append((side + ' ' + name, polygon, lift))
    made = []
    for label, polygon, lift in shapes:
        obj = original.copy()
        obj.data = original.data.copy()
        obj.name = 'MBH01 swept crown lap ' + label
        scene.collection.objects.link(obj)
        bm = bmesh.new()
        try:
            bm.from_mesh(obj.data)
            for a, b in zip(polygon, polygon[1:] + polygon[:1]):
                # CCW polygon interior is to the left of each directed edge.
                normal = Vector((-(b[1] - a[1]), b[0] - a[0], 0))
                bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                    dist=1e-7, plane_co=Vector((*a, 0)), plane_no=normal,
                    clear_inner=True, clear_outer=False)
            if not bm.faces:
                raise RuntimeError('Empty crown panel: ' + label)
            for vertex in bm.verts:
                # A bounded local sculpt proposal, not a source measurement.
                front = max(0, min(1, (-vertex.co.y - .04) / .119))
                vertex.co.y += .014 * front
                vertex.co.z += lift - .008 * max(0, min(1, (vertex.co.z - .08) / .081))
            bm.to_mesh(obj.data)
            obj.data.update()
        finally:
            bm.free()
        obj['connectedHeadCorrection'] = 'one focused owner-selected attempt; artistic review pending'
        obj.hide_render = False; obj.hide_viewport = False; obj.hide_set(False)
        made.append(obj.name)
    original.hide_render = True
    original.hide_set(True)
    return made


def apply(scene):
    allowed = selected_names()
    missing = allowed - set(scene.objects.keys())
    if missing:
        raise RuntimeError('Exact head sources unavailable: ' + repr(sorted(missing)))
    frame = scene.objects['CG2b head frame'].matrix_world.copy()
    for name in allowed:
        obj = scene.objects[name]
        if obj.type != 'MESH' or obj.parent or obj.matrix_world != frame:
            raise RuntimeError('Unexpected head-frame contract: ' + name)
    added = crown_panels(scene, scene.objects['CGRS04 source-scale frontal crown appearance'])
    for name in sorted(allowed - {'CGRS04 source-scale frontal crown appearance'}):
        obj = scene.objects[name]
        obj.data = obj.data.copy()
        for vertex in obj.data.vertices:
            p = vertex.co
            sign = -1 if p.x < 0 else 1
            if name.startswith(('CGO13 ', 'CGH05 integrated optical seat')):
                p.x -= sign * .009
            elif name.startswith('CGH17 broad curved brow course'):
                p.x += sign * .006
                p.y -= .006 * max(0, min(1, (-p.y + .02) / .16))
            elif name.startswith('CGH06 connected under-eye'):
                p.x -= sign * .004
                p.y -= .012 * max(0, min(1, (-p.y - .03) / .13))
                # Keep the rim below the optic and expose its dark opening.
                p.z -= .008 * math.exp(-((p.y + .025) / .07) ** 2)
            elif name.startswith('CGH06 substantial swept plated mandible'):
                weight = max(0, min(1, (-p.z - .10) / .167))
                p.z += .018 * weight
                p.y -= .010 * weight
            elif name.startswith('CGH18 '):
                root = math.exp(-((p.z + .09) / .105) ** 2)
                hook = max(0, min(1, (-p.z - .19) / .1164))
                p.y -= .016 * root + .010 * hook
                p.x += sign * .004 * root
        obj.data.update()
    bpy.context.view_layer.update()
    return allowed, added


def run(args):
    base = ROOT / 'assets/audit/cg-recursive-three-loop01/loop03/delivery/retained04'
    source = base / args.era / ('murderbird-recursive-' + args.era + '.blend')
    if sha(source) != PINS[args.era]:
        raise RuntimeError('Retained native changed')
    for path, expected in REFERENCES.items():
        if sha(ROOT / path) != expected:
            raise RuntimeError('Pinned reference unavailable or changed: ' + path)
    output = Path(args.out).resolve() / args.era
    if output.exists():
        raise FileExistsError('Preserve prior evidence; choose a fresh output')
    output.mkdir(parents=True)
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
    strong, preserve = module('cg-supervised-head17.py'), module('cg-supervised-preservation.py')
    before = strong.snap()
    maps = preserve.packed_image_snapshot()
    preserve.retain_packed_image_ids(bpy.context.scene)
    allowed, added = apply(bpy.context.scene)
    after = strong.snap()
    non_head = {name: digest for name, digest in before['objects'].items() if name not in allowed}
    assert all(after['objects'].get(name) == digest for name, digest in non_head.items())
    assert all(after['visibility'].get(name) == before['visibility'][name] for name in non_head)
    assert before['materials'] == after['materials'], 'Material graph changed'
    assert before['images'] == after['images'], 'Image payload changed'
    native = output / ('murderbird-recursive-' + args.era + '.blend')
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(native), relative_remap=False)
    bpy.ops.wm.open_mainfile(filepath=str(native), load_ui=False, use_scripts=False)
    reopened = strong.snap()
    assert all(reopened['objects'].get(name) == digest for name, digest in non_head.items())
    assert all(reopened['visibility'].get(name) == before['visibility'][name] for name in non_head)
    assert before['materials'] == reopened['materials'], 'Saved material graph changed'
    preserved_images = preserve.verify_receiving_images(maps)
    assert sha(source) == PINS[args.era], 'Original native was modified'
    receipt = {
        'status': 'PASS - preservation only; artistic acceptance pending', 'era': args.era,
        'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'source_baseline_revision': '533c6f19c0ee105bf9bf0f056eb91981382511d9',
        'source': str(source), 'source_sha256': PINS[args.era],
        'native': str(native), 'native_sha256': sha(native), 'authoring_script_sha256': sha(__file__),
        'blender_version': bpy.app.version_string, 'references': REFERENCES,
        'allowed_head_objects': sorted(allowed), 'new_crown_panels': added,
        'non_head_objects_preserved': len(non_head), 'material_graphs_preserved': len(before['materials']),
        'packed_images': preserved_images, 'head_frame_and_neck_seam': 'unchanged',
        'limits': ['All sculpt displacements are integrator proposals, not measured source dimensions.',
                   'No stance, breast, underlap, wing, leg, toe or neck-below-seam edits.',
                   'No engineering, rig, motion, runtime promotion or owner likeness acceptance.'],
    }
    (output / 'preservation.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print('CONNECTED_HEAD_PRESERVATION_PASS', args.era, len(non_head), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--era', choices=tuple(PINS), required=True)
    parser.add_argument('--out', required=True)
    run(parser.parse_args(sys.argv[sys.argv.index('--') + 1:]))
