"""Validate v5 with an explicit reconstructed jaw contract and frozen v4 source.

Reuses the established rigid-asset checks. It does not relax joint tolerances:
only the jaw's expected position is replaced by the authored reconstruction.
This proves compliance with that proposed contract, not artistic correctness.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('inherited_asset_checks', ROOT / 'scripts/verify-alignment-v4-assets.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
base.MODEL_DIR = 'assets/models/uncaged-alignment-v5'
base.INVENTORY_PATH = base.MODEL_DIR + '/alignment-inventory.json'
base.MODEL_PATH = base.MODEL_DIR + '/murderbird-alignment-v5.glb'
base.SOURCE_PATH = base.MODEL_DIR + '/murderbird-alignment-v5.blend'
JAW_WORLD = [0.0, -.300, 1.704]
inherited_compare = base.compare_saved_pivots


def reconstructed_compare(actual, reference, label):
    expected = copy.deepcopy(reference)
    by_name = {row['name']: row for row in expected}
    head = by_name['head']['world']
    by_name['jaw']['world'] = JAW_WORLD
    by_name['jaw']['local'] = [value - origin for value, origin in zip(JAW_WORLD, head)]
    inherited_compare(actual, expected, label + ' with explicit reconstructed jaw')


base.compare_saved_pivots = reconstructed_compare


def verify_exported_pivots(gltf, pivots):
    """Verify the declared identity-rest rigid rig through glTF's axis change.

    This candidate has no authored rest joint rotations. Reject any unexpected
    orientation rather than silently reducing an arbitrary matrix to position.
    """
    nodes = {row['name']: row for row in gltf['nodes']}
    indices = {i: row['name'] for i, row in enumerate(gltf['nodes'])}
    parents = {indices[child]: row['name'] for row in gltf['nodes']
               for child in row.get('children', [])}
    expected = {row['name']: row for row in pivots}
    local = {}
    for name in expected:
        node = nodes[name]
        rotation = node.get('rotation', [0, 0, 0, 1])
        base.require(max(abs(v) for v in rotation[:3]) <= 1e-6 and
                     abs(abs(rotation[3]) - 1) <= 1e-6,
                     'Unexpected exported rest joint rotation: ' + name)
        if 'matrix' in node:
            matrix = node['matrix']
            identity = [1 if i in [0, 5, 10, 15] else 0 for i in range(16)]
            base.require(all(abs(matrix[i] - identity[i]) <= 1e-6
                             for i in range(16) if i not in [12, 13, 14]),
                         'Unexpected exported rest joint matrix: ' + name)
            local[name] = matrix[12:15]
        else:
            local[name] = node.get('translation', [0, 0, 0])
        if name in parents:
            base.require(parents[name] in expected, 'Unexpected non-joint ancestor: ' + name)

    def world(name):
        parent = parents.get(name)
        return [a+b for a, b in zip(local[name], world(parent))] if parent else local[name]

    for name, record in expected.items():
        for field, actual in [('local', local[name]), ('world', world(name))]:
            x, y, z = record[field]
            converted = [x, z, -y]
            base.require(max(abs(a-b) for a, b in zip(actual, converted)) <= 1e-6,
                         f'Exported {field} joint differs from native contract: {name}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    frozen = json.loads((ROOT / 'assets/models/uncaged-alignment-v4/alignment-inventory.json').read_text())
    for record in frozen['generatedFiles']:
        base.validate_record(record)
    base.validate_record({'path': 'assets/models/uncaged-alignment-v4/murderbird-alignment-v4.glb',
                          'sha256': 'bcfb03ef96c6b64f3bf18caca7851d7b3bd5808d196c55e334ecda1e1ca04299'})
    report = base.validate()
    inventory = json.loads((ROOT / base.INVENTORY_PATH).read_text())
    gltf, _ = base.parse_glb(base.source_file(base.MODEL_PATH))
    verify_exported_pivots(gltf, inventory['pivots'])
    report['checks'].append('Every exported rest joint has identity orientation and matches native/inventory local and world positions after Z-up to Y-up conversion at 1e-6 m tolerance, including jaw and bill contact')
    report['checks'] = [check.replace('Saved native v4 Empty local/world joint positions match preserved v3 inventory except bill-contact; unit scales retained',
                                     'Native and recorded joint transforms match the fixed reconstruction contract: jaw world (0,-0.300,1.704); all other joints preserve v3, except the surface bill-contact landmark; unit scales retained')
                        for check in report['checks']]
    report['checks'].append('Every preserved v4 generated file matches its frozen inventory hash')
    report['jawContract'] = {'world': JAW_WORLD, 'parent': 'head', 'status': 'proposed mechanical reconstruction',
                             'reason': 'Attach the forked mandible to the lower cheek rather than below the skull'}
    report['validatorSources'] = [{'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
                                  for path in [Path(__file__), ROOT / 'scripts/verify-alignment-v4-assets.py']]
    if args.report:
        path = args.report.resolve()
        base.require(path.is_relative_to(ROOT / 'assets/audit/alignment-v5'), 'Receipt must stay under alignment-v5 audit')
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('x') as stream:
            json.dump(report, stream, indent=2)
            stream.write('\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
