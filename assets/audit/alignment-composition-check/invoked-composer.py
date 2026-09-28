"""Compose explicitly reviewed mesh changes into a new native/runtime candidate.

Run in Blender with -- --contract <repository-relative JSON>. The contract pins
every input and lists each mesh replacement/addition. Existing output is refused.
No scene, motion, material, transform or pivot redesign occurs in this composer.
"""
from pathlib import Path
import argparse
import hashlib
import json
import runpy
import shutil
import subprocess
import sys
import tempfile

import bpy
from mathutils import Matrix

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / 'scripts/build-uncaged-alignment-v7.py'
HELPER_SHA = '39b6ee2285d8c49df3a902f8fac0a07589da3d41f48ae24df1e06515c839033a'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bound(record):
    path = ROOT / record['path']
    assert path.is_file() and sha(path) == record['sha256'], f'Changed input: {path}'
    return path


def artifact(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path), 'bytes': path.stat().st_size}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--contract', required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    contract_path = ROOT / args.contract
    contract = json.loads(contract_path.read_text())
    assert sha(HELPER) == HELPER_SHA, 'Reviewed helper changed'
    helper = runpy.run_path(str(HELPER), run_name='composition_helpers')
    snapshot = helper['scene_snapshot']
    signature = helper['material_signature']
    matrix_values = helper['matrix_values']
    base = bound(contract['base'])
    sources = [(row, bound(row)) for row in contract['sources']]
    out = ROOT / contract['outputDirectory']
    audit = ROOT / contract['auditDirectory']
    assert not out.exists() and not audit.exists(), 'Preserve previous output before another composition'
    replacements = [name for row, _ in sources for name in row['replace']]
    additions = [name for row, _ in sources for name in row['add']]
    assert len(set(replacements + additions)) == len(replacements + additions), 'Overlapping source ownership'
    bpy.ops.wm.open_mainfile(filepath=str(base))
    before = snapshot()
    base_materials = {m.name: signature(m) for m in bpy.data.materials}
    for name in replacements:
        assert name in before['meshes'], f'Replacement missing from base: {name}'
    assert not (set(additions) & set(before['meshes'])), 'Addition already exists in base'

    with tempfile.TemporaryDirectory(prefix='murderbird-reviewed-transfer-') as temporary:
        packages = []
        records = {}
        for number, (row, source_path) in enumerate(sources):
            bpy.ops.wm.open_mainfile(filepath=str(source_path))
            source_snapshot = snapshot()
            assert source_snapshot['empties'] == before['empties'], 'Study changed pivot relationships'
            assert source_snapshot['curves'] == before['curves'], 'Study changed inherited guides'
            assert set(source_snapshot['meshes']) == set(before['meshes']) | set(row['add'])
            allowed = set(row['replace'])
            for name, previous in before['meshes'].items():
                current = source_snapshot['meshes'][name]
                if name not in allowed:
                    assert current == previous, f'Study changed unlisted object: {name}'
                else:
                    assert all(current[k] == previous[k] for k in previous if k != 'mesh'), f'Non-mesh replacement change: {name}'
            assert {m.name: signature(m) for m in bpy.data.materials} == base_materials, 'Study shader/name set differs'
            package_objects = []
            for name in row['replace'] + row['add']:
                obj = bpy.data.objects[name]
                assert obj.parent and obj.parent.name in before['empties'], f'Unmapped owner: {name}'
                records[name] = {
                    'source': row['path'], 'kind': 'replace' if name in allowed else 'add',
                    'owner': obj.parent.name, 'snapshot': source_snapshot['meshes'][name],
                    'basis': matrix_values(obj.matrix_basis), 'parentInverse': matrix_values(obj.matrix_parent_inverse),
                    'materials': [m.name if m else None for m in obj.data.materials],
                }
                clone = obj.copy()
                clone.data = obj.data.copy()
                clone.name = f'REVIEWED_TRANSFER::{name}'
                clone.parent = None
                clone.matrix_world = obj.matrix_world.copy()
                package_objects.append(clone)
            package = Path(temporary) / f'source-{number}.blend'
            bpy.data.libraries.write(str(package), set(package_objects), fake_user=False, compress=True)
            packages.append((package, row['replace'] + row['add']))

        bpy.ops.wm.open_mainfile(filepath=str(base))
        original_materials = {m.name: m for m in bpy.data.materials}
        for package, names in packages:
            with bpy.data.libraries.load(str(package), link=False) as (_, destination):
                destination.objects = [f'REVIEWED_TRANSFER::{name}' for name in names]
            loaded = dict(zip(names, destination.objects))
            for name, transferred in loaded.items():
                record = records[name]
                assert transferred is not None
                materials = []
                for original_name, loaded_material in zip(record['materials'], transferred.data.materials):
                    if original_name is None:
                        assert loaded_material is None
                        materials.append(None)
                    else:
                        assert signature(loaded_material) == base_materials[original_name], f'Material mismatch: {name}'
                        materials.append(original_materials[original_name])
                assert len(materials) == len(record['materials'])
                transferred.data.materials.clear()
                for material in materials:
                    transferred.data.materials.append(material)
                if record['kind'] == 'replace':
                    bpy.data.objects[name].data = transferred.data
                    bpy.data.objects.remove(transferred, do_unlink=True)
                else:
                    transferred.name = name
                    bpy.context.scene.collection.objects.link(transferred)
                    transferred.parent = bpy.data.objects[record['owner']]
                    transferred.matrix_parent_inverse = Matrix(record['parentInverse'])
                    transferred.matrix_basis = Matrix(record['basis'])
                    visibility = record['snapshot']['visibility']
                    transferred.hide_viewport = visibility['hideViewport']
                    transferred.hide_render = visibility['hideRender']
                    transferred.hide_select = visibility['hideSelect']
                    transferred.hide_set(visibility['hideInViewLayer'])
        # Appended shader copies are redundant; the source's original material
        # datablocks are kept, including its two unused records explicitly.
        for material in list(bpy.data.materials):
            if material.name not in original_materials:
                assert material.users == 0, f'Unexpected material dependency: {material.name}'
                bpy.data.materials.remove(material)
        for name in ('Neutral / edge.001', 'Neutral / plate.001'):
            original_materials[name].use_fake_user = True
        after = snapshot()
        assert before['empties'] == after['empties'] and before['curves'] == after['curves']
        assert set(after['meshes']) == set(before['meshes']) | set(additions)
        for name, previous in before['meshes'].items():
            if name not in replacements:
                assert after['meshes'][name] == previous, f'Unrelated mesh changed: {name}'
        for name, record in records.items():
            assert after['meshes'][name] == record['snapshot'], f'Transferred mesh does not match study: {name}'
        assert {m.name: signature(m) for m in bpy.data.materials} == base_materials

        out.mkdir(parents=True)
        audit.mkdir(parents=True)
        shutil.copy2(contract_path, audit / 'transfer-contract.json')
        shutil.copy2(Path(__file__), audit / 'executed-composer.py')
        shutil.copy2(HELPER, audit / 'export-helper.py')
        native = out / f"{contract['stem']}.blend"
        runtime = out / f"{contract['stem']}.glb"
        bpy.context.preferences.filepaths.save_version = 0
        bpy.ops.wm.save_as_mainfile(filepath=str(native), check_existing=False)
        parts = [{'name': obj.name, 'parent': obj.parent.name, 'region': obj.get('region', 'back'),
                  'role': obj.get('surfaceRole', 'frame'), 'eras': obj.get('exteriorEras', 'maker,mechanic,builder').split(','),
                  'class': obj.get('constructionClass', 'inherited-passive'),
                  'geometryStatus': obj.get('geometryStatus', 'inherited proposal')}
                 for obj in bpy.data.objects if obj.type == 'MESH']
        pivots = [{'name': obj.name, 'parent': obj.parent.name if obj.parent else None,
                   'local': list(obj.location), 'world': list(obj.matrix_world.translation), 'scale': list(obj.scale)}
                  for obj in bpy.data.objects if obj.type == 'EMPTY']
        modifiers = {obj.name: helper['modifier_signature'](obj) for obj in bpy.data.objects if obj.type == 'MESH' and obj.modifiers}
        helper['export_from_reopened_native'](native, runtime, after, modifiers)

    assert bound(contract['base']) == base
    for row, path in sources:
        assert bound(row) == path
    receipt = {
        'status': 'neutral composition proposal; owner artistic review pending',
        'startingRevision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'base': contract['base'], 'transfers': contract['sources'], 'scope': contract['scope'],
        'parts': parts, 'pivots': pivots, 'controlCurves': len(after['curves']),
        'generatedFiles': [artifact(native), artifact(runtime)],
        'generationSources': [artifact(audit / name) for name in ('transfer-contract.json', 'executed-composer.py', 'export-helper.py')],
        'checks': {'exactSourceMeshesTransferred': True, 'unrelatedMeshSignaturesUnchanged': True,
                   'pivotMatricesAndParentsUnchanged': True, 'guideCurvesUnchanged': True,
                   'nativeReloadSnapshotExact': True, 'shaderSignaturesAndAssignmentsUnchanged': True},
        'authoringMetadataException': 'Two pre-existing unused Neutral / edge.001 and Neutral / plate.001 material datablocks receive fake-user retention; their shaders and assignments are unchanged.',
        'limits': ['Inherited curves do not regenerate transferred meshes.',
                   'Separate runtime geometry parity, movement, clearance and browser checks required.',
                   'No artistic acceptance, physical simulation, material completion or publication.'],
    }
    (out / 'alignment-inventory.json').write_text(json.dumps(receipt, indent=2) + '\n')
    (audit / 'native-transfer-records.json').write_text(json.dumps(records, indent=2) + '\n')
    print(json.dumps({'native': artifact(native), 'runtime': artifact(runtime), 'parts': len(parts), 'pivots': len(after['empties'])}))


if __name__ == '__main__':
    main()
