#!/usr/bin/env python3
"""Stage a technically verified appearance candidate and its three Blender stills.

This copies files into a candidate runtime directory only. It does not select the
candidate in application code or imply artistic/owner acceptance.
"""

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODEL_ROOT = Path('assets/models/uncaged-appearance-v1/iterations')
AUDIT_ROOT = Path('assets/audit/appearance-v1')
RUNTIME_ROOT = Path('assets/models/uncaged-appearance-v1/runtime')
VIEW_NAMES = {
    'maker-three-quarter.png': 'maker-preview.png',
    'mechanic-three-quarter.png': 'mechanic-preview.png',
    'advanced-three-quarter.png': 'builder-preview.png',
}
PACK_PROOFS = (
    'allBufferViewSlicesByteExact',
    'allOtherSemanticJsonUnchanged',
    'bufferViewIndicesAndCountUnchanged',
    'outputBufferViewsFourByteAligned',
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def repo_path(value):
    path = (ROOT / value).resolve()
    require(path.is_relative_to(ROOT), f'Path escapes repository: {value}')
    return path


def read_json(path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f'Cannot read JSON receipt {path.relative_to(ROOT)}: {error}') from error


def facts(path):
    raw = path.read_bytes()
    return {'path': path.relative_to(ROOT).as_posix(), 'bytes': len(raw), 'sha256': digest(raw)}, raw


def validate_png(path, expected_sha):
    record, raw = facts(path)
    require(raw.startswith(b'\x89PNG\r\n\x1a\n'), f'Not a PNG: {record["path"]}')
    require(len(raw) >= 24, f'Truncated PNG: {record["path"]}')
    width, height = struct.unpack_from('>II', raw, 16)
    require(width > 0 and height > 0, f'Invalid PNG dimensions: {record["path"]}')
    require(record['sha256'] == expected_sha,
            f'Authoring-view SHA mismatch: {record["path"]}')
    return record


def validate(iteration):
    model_dir = MODEL_ROOT / iteration
    audit_dir = AUDIT_ROOT / iteration
    inventory_path = repo_path(model_dir / 'appearance-inventory.json')
    inventory, inventory_raw = read_json(inventory_path), inventory_path.read_bytes()
    require(inventory.get('iteration') == iteration, 'Appearance inventory iteration mismatch')
    require(inventory.get('status') == 'appearance candidate; owner artistic acceptance pending',
            'Candidate status must remain pending owner artistic acceptance')

    generated = inventory.get('generatedFiles')
    require(isinstance(generated, list) and generated, 'Inventory has no generated-file records')
    generated_by_path = {}
    for row in generated:
        path_value = row.get('path')
        require(isinstance(path_value, str) and path_value not in generated_by_path,
                'Invalid or duplicate generated-file inventory path')
        path = repo_path(path_value)
        record, _ = facts(path)
        require(record['bytes'] == row.get('bytes'), f'Inventory byte count mismatch: {path_value}')
        require(record['sha256'] == row.get('sha256'), f'Inventory SHA mismatch: {path_value}')
        generated_by_path[path_value] = row

    native_rel = (model_dir / 'murderbird-appearance.blend').as_posix()
    raw_glb_rel = (model_dir / 'murderbird-appearance.glb').as_posix()
    packed_rel = (model_dir / 'murderbird-appearance-packed.glb').as_posix()
    require(native_rel in generated_by_path, 'Inventory does not bind the native Blender source')
    require(raw_glb_rel in generated_by_path, 'Inventory does not bind the raw GLB source')
    native_facts, _ = facts(repo_path(native_rel))
    raw_facts, _ = facts(repo_path(raw_glb_rel))

    receipt_specs = {
        'assetValidation': 'asset-validation.json',
        'opticVisibility': 'optic-visibility.json',
        'authoringViews': 'authoring-views.json',
        'kinematicAlignment': 'kinematic-alignment.json',
        'packing': 'packing.json',
        'artReview': 'art-review.json',
    }
    receipts = {}
    for name, basename in receipt_specs.items():
        path = repo_path(audit_dir / basename)
        receipt, raw = read_json(path), path.read_bytes()
        receipts[name] = {
            'path': path.relative_to(ROOT).as_posix(),
            'sha256': digest(raw),
            'data': receipt,
        }

    asset = receipts['assetValidation']['data']
    require(asset.get('status') == 'passed' and asset.get('iteration') == iteration,
            'Appearance asset validation is not a passing receipt for this iteration')
    require(asset.get('candidate', {}).get('modelSha256') == raw_facts['sha256'],
            'Asset-validation receipt does not bind the raw GLB')
    asset_files = asset.get('candidate', {}).get('generatedFiles', {})
    for rel, expected in ((native_rel, native_facts), (raw_glb_rel, raw_facts)):
        item = asset_files.get(rel)
        require(item and item.get('bytes') == expected['bytes']
                and item.get('sha256') == expected['sha256'],
                f'Asset-validation receipt does not bind {rel}')

    art_review = receipts['artReview']['data']
    require(art_review.get('status') == 'candidate-for-local-review',
            'Art review must explicitly mark this candidate for local review')
    require(art_review.get('sourceModelSha256') == raw_facts['sha256'],
            'Art-review receipt does not bind the exact raw GLB')

    geometry_facts = asset.get('candidate', {})
    accessors_checked = geometry_facts.get('positionAccessorsChecked')
    values_checked = geometry_facts.get('positionValuesChecked')
    maximum_position = geometry_facts.get('maximumPositionComponentMeters')
    position_limit = geometry_facts.get('positionCoordinateLimitMeters')
    require(isinstance(accessors_checked, int) and accessors_checked > 0
            and isinstance(values_checked, int) and values_checked > 0
            and isinstance(maximum_position, (int, float)) and maximum_position >= 0
            and isinstance(position_limit, (int, float)) and 0 < position_limit <= 4.0
            and maximum_position <= position_limit
            and isinstance(geometry_facts.get('maximumPositionComponentMesh'), str)
            and bool(geometry_facts['maximumPositionComponentMesh']),
            'Asset validation lacks passing POSITION bounds/4 m coordinate-guard facts')

    optic = receipts['opticVisibility']['data']
    require(optic.get('status') == 'passed', 'Optic-visibility check did not pass')
    require(optic.get('sourceSha256') == native_facts['sha256'],
            'Optic-visibility receipt does not bind the native Blender source')
    optic_checks = optic.get('checks')
    require(isinstance(optic_checks, list) and len(optic_checks) >= 4,
            'Optic-visibility receipt is incomplete')
    require(all(c.get('centerVisible') is True and c.get('fraction', 0) >= .70
                for c in optic_checks), 'One or more recorded optic views fail visibility')

    views = receipts['authoringViews']['data']
    require(views.get('status') == 'rendered evidence; likeness not automatically accepted',
            'Authoring-view receipt has unexpected status')
    require(views.get('source') == native_rel
            and views.get('sourceSha256') == native_facts['sha256'],
            'Authoring-view receipt does not bind the native Blender source')
    view_rows = views.get('views')
    require(isinstance(view_rows, list), 'Authoring-view receipt has no views array')
    expected_stills = {}
    for view_name, output_name in VIEW_NAMES.items():
        matches = [row for row in view_rows
                   if Path(row.get('path', '')).name == view_name]
        require(len(matches) == 1, f'Expected exactly one authoring still named {view_name}')
        source = repo_path(matches[0].get('path', ''))
        expected_stills[output_name] = validate_png(source, matches[0].get('sha256'))

    kinematic = receipts['kinematicAlignment']['data']
    require(kinematic.get('status') == 'passed', 'Kinematic alignment did not pass')
    require(kinematic.get('sha256') == raw_facts['sha256'],
            'Kinematic receipt does not bind the raw GLB')
    require(kinematic.get('model', '').replace('\\', '/').endswith(raw_glb_rel),
            'Kinematic receipt model path is not the iteration raw GLB')
    kin_checks = kinematic.get('checks')
    require(isinstance(kin_checks, list) and kin_checks
            and all(check.get('status') == 'passed' for check in kin_checks),
            'Kinematic receipt has missing or failed checks')

    packing = receipts['packing']['data']
    packed_path = repo_path(packed_rel)
    packed_facts, _ = facts(packed_path)
    require(packing.get('inputSha256') == raw_facts['sha256'],
            'Packing receipt input hash does not match the raw GLB')
    require(packing.get('outputSha256') == packed_facts['sha256'],
            'Packing receipt output hash does not match the packed GLB')
    require(packing.get('inputBytes') == raw_facts['bytes']
            and packing.get('outputBytes') == packed_facts['bytes'],
            'Packing receipt byte counts do not match GLB files')
    require(all(packing.get('proofs', {}).get(key) is True for key in PACK_PROOFS),
            'Packing receipt is missing a required losslessness proof')
    require(Path(packing.get('inputPath', '')).as_posix().endswith(raw_glb_rel)
            and Path(packing.get('outputPath', '')).as_posix().endswith(packed_rel),
            'Packing receipt paths do not identify this iteration raw and packed GLBs')

    selections = [
        (packed_path, 'murderbird-appearance-packed.glb', packed_facts),
        *[(repo_path(row['path']), output_name, row)
          for output_name, row in expected_stills.items()],
    ]
    destination = repo_path(RUNTIME_ROOT / iteration)
    outputs = []
    for source, filename, source_record in selections:
        target = destination / filename
        require(not target.exists() or target.is_file(),
                f'Runtime output is not a regular file: {target.relative_to(ROOT)}')
        if target.exists():
            existing = target.read_bytes()
            require(len(existing) == source_record['bytes']
                    and digest(existing) == source_record['sha256'],
                    f'Refusing to overwrite unequal runtime file: {target.relative_to(ROOT)}')
        target_rel = target.relative_to(ROOT).as_posix()
        outputs.append({'path': target_rel, 'bytes': source_record['bytes'],
                        'sha256': source_record['sha256']})

    receipt_records = {
        name: {'path': row['path'], 'sha256': row['sha256']}
        for name, row in receipts.items()
    }
    receipt_records['appearanceInventory'] = {
        'path': inventory_path.relative_to(ROOT).as_posix(),
        'sha256': digest(inventory_raw),
    }
    runtime_inventory = {
        'status': 'candidate pending owner acceptance',
        'selectedIteration': iteration,
        'source': {
            'native': native_facts,
            'rawGlb': raw_facts,
            'packedGlb': packed_facts,
        },
        'geometryGuardFacts': {
            'positionAccessorsChecked': accessors_checked,
            'positionValuesChecked': values_checked,
            'maximumPositionComponentMeters': maximum_position,
            'maximumPositionComponentMesh': geometry_facts['maximumPositionComponentMesh'],
            'positionCoordinateLimitMeters': position_limit,
        },
        'receiptPathsAndHashes': receipt_records,
        'generatedFiles': outputs,
        'rights': inventory.get('rights'),
        'selectionScope': 'Staged candidate runtime files only; no application code selection or owner artistic acceptance is implied.',
    }
    inventory_bytes = (json.dumps(runtime_inventory, indent=2, ensure_ascii=False) + '\n').encode('utf-8')
    inventory_target = destination / 'runtime-inventory.json'
    if inventory_target.exists():
        require(inventory_target.is_file(),
                f'Runtime inventory is not a regular file: {inventory_target.relative_to(ROOT)}')
        require(inventory_target.read_bytes() == inventory_bytes,
                f'Refusing to overwrite unequal runtime inventory: {inventory_target.relative_to(ROOT)}')

    return destination, selections, outputs, inventory_target, inventory_bytes, runtime_inventory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--iteration', default='iteration-01')
    args = parser.parse_args()
    require(re.fullmatch(r'iteration-[a-z0-9][a-z0-9-]*', args.iteration) is not None,
            'Iteration must use iteration-<lowercase-label> form')
    destination, selections, outputs, inventory_target, inventory_bytes, report = validate(args.iteration)

    destination.mkdir(parents=True, exist_ok=True)
    for source, filename, source_record in selections:
        target = destination / filename
        if target.exists():
            continue
        payload = source.read_bytes()
        require(len(payload) == source_record['bytes']
                and digest(payload) == source_record['sha256'],
                f'Source changed during selection: {source.relative_to(ROOT)}')
        with target.open('xb') as stream:
            stream.write(payload)
    if not inventory_target.exists():
        with inventory_target.open('xb') as stream:
            stream.write(inventory_bytes)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
