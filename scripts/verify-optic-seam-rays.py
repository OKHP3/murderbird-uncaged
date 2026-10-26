"""Read-only native seam sampling at fixed review directions; no image proof.

Uses double-sided geometric intersections. A passing sample set is not a
complete annulus classification, rendered appearance or engineering clearance.
"""
import argparse
import collections
import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def run(args):
    native, output = Path(args.native).resolve(), Path(args.out).resolve()
    home = Path.home() / 'OKH-Local/01_ChatGPT_Exports/murderbird-uncaged/evidence/visual-technical-acceptance'
    assert output.is_relative_to(home.resolve()) and not output.exists()
    digest = hashlib.sha256(native.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(native), load_ui=False, use_scripts=False)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    trees = []
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH' or obj.hide_render or obj.hide_viewport or obj.hide_get() or obj.get('authoringGuide'):
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        vertices = [evaluated.matrix_world @ v.co for v in mesh.vertices]
        polygons = [tuple(p.vertices) for p in mesh.polygons]
        trees.append((obj.name, BVHTree.FromPolygons(vertices, polygons, all_triangles=False)))
        evaluated.to_mesh_clear()

    def cast(origin, direction):
        best = None
        for name, tree in trees:
            point, normal, index, distance = tree.ray_cast(origin, direction)
            if point is not None and (best is None or distance < best['distance']):
                best = {'object': name, 'distance': distance, 'polygon': index,
                        'point': list(point), 'normal_dot_ray': normal.dot(direction)}
        return best

    convert = lambda p: Vector((p.x, -p.z, p.y))
    camera = Vector((-1.6535807939288083, 2.24883859349462, 1.4378499214625984))
    target = Vector((0, 1.67, .28))
    forward = (target - camera).normalized()
    up = Vector((.2257888317, .9612616897, -.1580990553))
    right = forward.cross(up).normalized()
    actual_up = right.cross(forward).normalized()
    pixels = []
    for px, py in ((510, 410), (525, 414), (540, 410)):
        origin = camera + right * ((px - 112.5 - 520) / 720 * .76) + actual_up * ((360 - py) / 720 * .76)
        hit = cast(convert(origin), convert(forward))
        pixels.append({'pixel': [px, py], 'hit': hit,
                       'covered_by_optic': bool(hit and hit['object'].startswith(('CGH05 ', 'CGO13 ')))})
    sectors = []
    for side, sign in (('L', -1), ('R', 1)):
        frame = bpy.context.scene.objects['CGH05 integrated optical seat ' + side].matrix_world
        direction = convert(forward)
        if side == 'R':
            direction.x *= -1
        counts, failures = collections.Counter(), []
        for radius in (.0520, .0535, .0550, .0565):
            for index in range(64):
                angle = index * math.tau / 64
                point = frame @ Vector((sign * .148, .005 + radius * math.cos(angle), .020 + radius * math.sin(angle)))
                hit = cast(point - direction * 3, direction)
                name = hit['object'] if hit else 'BACKGROUND'
                counts[name] += 1
                # Other head surfaces may legitimately occlude the sampled rim.
                covered = name.startswith(('CGH05 ', 'CGO13 ', 'MBH01 ', 'CGH17 ', 'CGH06 ', 'CGH18 '))
                if not covered:
                    failures.append({'radius': radius, 'sector': index, 'hit': hit})
        sectors.append({'side': side, 'rays': 256, 'direction_native': list(direction),
                        'first_hit_counts': dict(counts), 'uncovered_samples': failures,
                        'status': 'PASS' if not failures else 'FAIL'})
    assert hashlib.sha256(native.read_bytes()).hexdigest() == digest
    receipt = {'native': str(native), 'native_sha256': digest, 'blender': bpy.app.version_string,
               'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'former_opening_pixels': pixels, 'outer_seam_sector_samples': sectors,
               'status': 'PASS' if all(p['covered_by_optic'] for p in pixels) and all(s['status'] == 'PASS' for s in sectors) else 'FAIL',
               'limits': ['Double-sided geometry sampling only; image inspection is a separate gate.',
                          '512 outer-seam rays at two fixed mirrored directions; not all directions or full annulus coverage.',
                          'No native/browser appearance, clearance, engineering or owner acceptance implied.']}
    with output.open('x') as stream:
        json.dump(receipt, stream, indent=2)
    print('OPTIC_SEAM_SAMPLES', receipt['status'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--native', required=True)
    parser.add_argument('--out', required=True)
    run(parser.parse_args(sys.argv[sys.argv.index('--') + 1:]))
