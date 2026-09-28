"""Read-only evaluated native geometry for independent runtime position checks.

This intentionally does not use the runtime exporter. World-space triangle
positions, material names, era tags and rigid pivot matrices are sampled before
batching. It does not certify normals, UVs, collision or artistic likeness.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import shutil
import sys

import bpy
from mathutils import Matrix

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'package.json').is_file() and (p / 'scripts/build-uncaged-alignment-v7.py').is_file())
C = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0), (0, 0, 0, 1)))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--native', required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    native = ROOT / args.native
    out = ROOT / args.out
    assert digest(native) == args.sha256
    assert not out.exists(), 'Preserve prior evidence; choose a new directory'
    out.mkdir(parents=True)
    shutil.copy2(__file__, out / 'executed-native-snapshot.py')
    bpy.ops.wm.open_mainfile(filepath=str(native))
    bpy.context.scene.frame_set(1)
    # All eras are represented in the export. Visibility changes affect only
    # this unsaved diagnostic process, never the authoring file.
    for obj in bpy.data.objects:
        obj.hide_set(False)
        obj.hide_viewport = False
    bpy.context.view_layer.update()
    graph = bpy.context.evaluated_depsgraph_get()
    groups = {}
    pivots = {}
    for obj in sorted(bpy.data.objects, key=lambda item: item.name):
        if obj.type == 'EMPTY':
            converted = C @ obj.matrix_world @ C.inverted()
            pivots[obj.name] = {
                'parent': obj.parent.name if obj.parent else None,
                'matrix': [float(converted[row][col]) for col in range(4) for row in range(4)],
            }
        if obj.type != 'MESH':
            continue
        assert obj.parent and obj.parent.type == 'EMPTY', obj.name
        assert all(mod.show_viewport == mod.show_render for mod in obj.modifiers), 'Different render/viewport modifier stack'
        evaluated = obj.evaluated_get(graph)
        mesh = evaluated.to_mesh()
        try:
            mesh.calc_loop_triangles()
            transform = C @ evaluated.matrix_world
            positions = [tuple(float(n) for n in (transform @ vertex.co)) for vertex in mesh.vertices]
            for tri in mesh.loop_triangles:
                material = mesh.materials[tri.material_index]
                assert material is not None, obj.name
                identity = (obj.parent.name, obj.get('exteriorEras'), obj.get('region'), obj.get('surfaceRole'), material.name)
                assert all(identity), f'Unclassified {obj.name}'
                key = json.dumps(identity, separators=(',', ':'))
                group = groups.setdefault(key, {'triangles': 0, 'points': set(), 'objects': set()})
                group['triangles'] += 1
                group['points'].update(positions[index] for index in tri.vertices)
                group['objects'].add(obj.name)
        finally:
            evaluated.to_mesh_clear()
    for group in groups.values():
        group['points'] = sorted(group['points'])
        group['objects'] = sorted(group['objects'])
    assert digest(native) == args.sha256
    payload = {
        'native': {'path': args.native, 'sha256': args.sha256, 'bytes': native.stat().st_size},
        'blenderVersion': bpy.app.version_string,
        'coordinateMap': 'browser = (Blender X, Blender Z, -Blender Y)',
        'groups': groups, 'pivots': pivots,
        'limits': ['Evaluated triangle position clouds and material names only; normals, UVs and topology equivalence are not checked.',
                   'No source save, runtime exporter invocation, collision or artistic acceptance.'],
    }
    target = out / 'native-geometry.json.gz'
    with target.open('xb') as stream:
        with gzip.GzipFile(fileobj=stream, mode='wb', mtime=0) as zipped:
            zipped.write(json.dumps(payload, separators=(',', ':')).encode())
    receipt = {'snapshot': {'path': str(target.relative_to(ROOT)), 'sha256': digest(target), 'bytes': target.stat().st_size},
               'source': payload['native'], 'scriptSha256': digest(Path(__file__)),
               'groups': len(groups), 'pivots': len(pivots),
               'triangles': sum(group['triangles'] for group in groups.values())}
    (out / 'snapshot-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
