"""Run with Blender --background --factory-startup --disable-autoexec --python.

Regression: Blender's custom-normal storage must not silently pass the strict
native/export contract. No scene/native save or derivative export is performed.
"""
import importlib.util
import pathlib
import unittest
import tempfile
import os
import json
import struct
import bpy
from mathutils import Vector

source = pathlib.Path(__file__).resolve().parents[1] / 'scripts/export-cg-strict.py'
spec = importlib.util.spec_from_file_location('cg_export', source)
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)


class NormalFidelity(unittest.TestCase):
    def check_roundtrip(self, direction, vertices=None):
        mesh = bpy.data.meshes.new('normal regression')
        try:
            mesh.from_pydata(vertices or [(0, 0, 0), (1, 0, 0), (0, 1, 0)], [], [(0, 1, 2)])
            mesh.polygons[0].use_smooth = True
            normals = [tuple(Vector(direction).normalized())] * 3
            mesh.normals_split_custom_set(normals)
            return exporter.verify_batched_normal_readback(mesh, normals)
        finally:
            bpy.data.meshes.remove(mesh)

    def test_axis_normal_remains_exportable(self):
        self.assertLessEqual(self.check_roundtrip((0, 0, 1)), 2e-5)

    def test_lossy_custom_normal_roundtrip_is_rejected(self):
        # Exact narrow triangle and normal from the retained Maker toe, isolated
        # without a binary fixture. Large loss occurs in Blender's corner basis.
        with self.assertRaisesRegex(AssertionError, 'no derivative written'):
            self.check_roundtrip((-0.9227542281150818, -0.32480037212371826, -0.20743554830551147), [
                (-0.1941569447517395, 0.09033267945051193, 0.16920150816440582),
                (-0.1905297189950943, 0.0798056349158287, 0.1695525348186493),
                (-0.1941535919904709, 0.0903339609503746, 0.16920815408229828),
            ])

    def test_float_transport_repairs_the_reproduced_toe_without_source_mutation(self):
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        mesh = bpy.data.meshes.new('toe regression source')
        mesh.from_pydata([
            (-0.1941569447517395, 0.09033267945051193, 0.16920150816440582),
            (-0.1905297189950943, 0.0798056349158287, 0.1695525348186493),
            (-0.1941535919904709, 0.0903339609503746, 0.16920815408229828),
        ], [], [(0, 1, 2)])
        material = bpy.data.materials.new('toe regression material')
        mesh.materials.append(material)
        obj = bpy.data.objects.new('toe regression', mesh)
        bpy.context.scene.collection.objects.link(obj)
        # Use the evaluated source normals as the acceptance target. The first
        # two tests separately demonstrate the historical corner storage loss.
        mesh.polygons[0].use_smooth = True
        wanted = tuple(mesh.corner_normals[0].vector)
        expected = (wanted[0], wanted[2], -wanted[1])
        fingerprint = exporter._digest_mesh(mesh)
        with tempfile.TemporaryDirectory(dir=os.environ['MURDERBIRD_TEST_OUTPUT']) as directory:
            output = pathlib.Path(directory) / 'toe.glb'
            receipt = exporter.export(bpy.context.scene, output)
            self.assertTrue(receipt['native_meshes_unchanged'])
            self.assertTrue(receipt['temporary_datablocks_removed'])
            self.assertEqual(fingerprint, exporter._digest_mesh(mesh))
            raw = output.read_bytes()
            size = struct.unpack_from('<I', raw, 12)[0]
            doc = json.loads(raw[20:20 + size])
            blob = raw[28 + size:]
            for primitive in doc['meshes'][0]['primitives']:
                self.assertNotIn('_CG_EXACT_NORMAL', primitive['attributes'])
                accessor = doc['accessors'][primitive['attributes']['NORMAL']]
                view = doc['bufferViews'][accessor['bufferView']]
                start = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
                for index in range(accessor['count']):
                    actual = struct.unpack_from('<3f', blob, start + index * view.get('byteStride', 12))
                    self.assertLessEqual(sum((a-b)**2 for a,b in zip(actual, expected))**.5, 2e-5)
            with self.assertRaises(FileExistsError):
                exporter.export(bpy.context.scene, output)


result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(NormalFidelity))
if not result.wasSuccessful():
    raise SystemExit(1)
