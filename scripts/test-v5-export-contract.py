"""Adversarial export-contract fixtures; no Blender/model regeneration."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('v5_contract', ROOT / 'scripts/verify-alignment-v5-assets.py')
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)


class ExportContractTests(unittest.TestCase):
    def setUp(self):
        self.gltf = {'nodes': [
            {'name': 'head', 'translation': [0, 1.638, .335], 'children': [1]},
            {'name': 'jaw', 'translation': [0, .066, -.035]},
        ]}
        self.pivots = [
            {'name': 'head', 'local': [0, -.335, 1.638], 'world': [0, -.335, 1.638]},
            {'name': 'jaw', 'local': [0, .035, .066], 'world': [0, -.300, 1.704]},
        ]

    def test_axis_conversion_and_parent_accumulation(self):
        contract.verify_exported_pivots(self.gltf, self.pivots)

    def test_wrong_jaw_translation_is_rejected(self):
        self.gltf['nodes'][1]['translation'][1] += .001
        with self.assertRaisesRegex(ValueError, 'local joint differs.*jaw'):
            contract.verify_exported_pivots(self.gltf, self.pivots)

    def test_unexpected_joint_orientation_is_rejected(self):
        self.gltf['nodes'][1]['rotation'] = [.1, 0, 0, .9949874371]
        with self.assertRaisesRegex(ValueError, 'rest joint rotation.*jaw'):
            contract.verify_exported_pivots(self.gltf, self.pivots)

    def test_wrong_recorded_world_attachment_is_rejected(self):
        self.pivots[1]['world'][1] += .01
        with self.assertRaisesRegex(ValueError, 'world joint differs.*jaw'):
            contract.verify_exported_pivots(self.gltf, self.pivots)

    def test_matrix_translation_retains_same_contract(self):
        node = self.gltf['nodes'][1]
        translation = node.pop('translation')
        node['matrix'] = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, *translation, 1]
        contract.verify_exported_pivots(self.gltf, self.pivots)
        node['matrix'][12] += .01
        with self.assertRaisesRegex(ValueError, 'local joint differs.*jaw'):
            contract.verify_exported_pivots(self.gltf, self.pivots)


if __name__ == '__main__':
    unittest.main()
