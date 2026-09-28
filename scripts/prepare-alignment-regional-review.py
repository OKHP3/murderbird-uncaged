#!/usr/bin/env python3
"""Bind the regional gallery to verified model, render-camera and media identities."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return str(path.resolve().relative_to(ROOT))


def asset(path, **metadata):
    path = path.resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    return {'path': relative(path), 'sha256': digest(path), **metadata}


def render_set(directory, model_hash):
    receipt_path = directory / 'views.json'
    receipt = json.loads(receipt_path.read_text())
    assert receipt['model']['sha256'] == model_hash, f'{receipt_path}: model hash mismatch'
    assert len(receipt.get('rendererSha256', '')) == 64, f'{receipt_path}: renderer hash missing'
    assert isinstance(receipt.get('era'), str) and receipt['era'], f'{receipt_path}: era missing'
    for row in receipt['views']:
        image_path = directory / row['image']
        assert digest(image_path) == row['sha256'], f'{image_path}: image hash mismatch'
        assert row.get('bytes') == image_path.stat().st_size, f'{image_path}: image byte count mismatch'
    return receipt, {row['image']: row for row in receipt['views']}, asset(receipt_path)


def render_binding(receipt_asset, receipt, view):
    row = view
    camera = {key: row[key] for key in ('location', 'target', 'orthographicScale')}
    camera_key = hashlib.sha256(json.dumps(camera, sort_keys=True).encode()).hexdigest()[:12]
    return {'receipt': receipt_asset, 'receiptModelPath': receipt['model']['path'],
            'receiptModelSha256': receipt['model']['sha256'],
            'rendererSha256': receipt['rendererSha256'], 'renderEra': receipt['era'],
            'imageName': row['image'], 'camera': camera, 'cameraKey': camera_key}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--audit', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--previous-model', type=Path)
    parser.add_argument('--previous-audit', type=Path)
    args = parser.parse_args()
    model, audit, output = (p.resolve() for p in (args.model, args.audit, args.output))
    baseline = ROOT / 'assets/models/uncaged-alignment-v5-regional/candidate/input-snapshots/base-v5-sixth/murderbird-alignment-v5.glb'
    baseline_audit = ROOT / 'assets/audit/alignment-v5-regional/native-baseline'
    current_hash, base_hash = digest(model), digest(baseline)
    before, old_views, before_receipt_asset = render_set(baseline_audit, base_hash)
    after, new_views, after_receipt_asset = render_set(audit / 'native-builder', current_hash)
    assert before['rendererSha256'] == after['rendererSha256']
    assert before['era'] == after['era'] == 'builder'
    packet = {
        'schemaVersion': 1, 'status': 'revision required',
        'models': {'baseline': asset(baseline, label='Preserved V5 sixth baseline'),
                   'current': asset(model, label='Regional guard and talon candidate')},
        'references': [], 'comparisons': [], 'eraConfigurations': [],
        'cameraVerification': 'Actual location, target, orthographic scale, renderer SHA and era are asserted equal from hashed render receipts before packet generation.',
        'limits': [
            'Native views show era-eligible exterior geometry. The existing application generates additional mechanisms at runtime.',
            'The active application remains V4. Candidate browser captures use a temporary exact-byte model response override; this is an isolated review candidate.',
            'Geometry remains a reference-informed proposal. Surface wear, whole-body likeness, exhaustive clearance, physical forces, sustained device performance and owner acceptance remain open.'
        ]
    }
    for ref_id, label, scope, path in [
        ('maker-clean', 'Maker Clean', 'Maker-era illustration; visible construction reference.', 'assets/img/library/murderbird-unified-maker-clean-candidate-2026-09-06.png'),
        ('candidate-03', 'Candidate 03', 'Common full-body reference; perspective illustration, not dimensional metrology.', 'assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png'),
        ('july-head', 'Owner-preferred July head', 'Head identity only; does not control hidden or rear construction.', 'context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png')
    ]:
        packet['references'].append(asset(ROOT / path, id=ref_id, label=label, scope=scope))
    for view, filename in [('front', 'full-front.png'), ('side', 'full-side.png'),
                           ('rear', 'full-rear.png'), ('three-quarter', 'full-three-quarter.png'),
                           ('head', 'head-three-quarter.png'), ('feet', 'feet-three-quarter.png')]:
        camera = {key: new_views[filename][key] for key in ('location', 'target', 'orthographicScale')}
        assert camera == {key: old_views[filename][key] for key in camera}, filename
        key = hashlib.sha256(json.dumps(camera, sort_keys=True).encode()).hexdigest()[:12]
        left_binding = render_binding(before_receipt_asset, before, old_views[filename])
        right_binding = render_binding(after_receipt_asset, after, new_views[filename])
        assert left_binding['camera'] == right_binding['camera'] == camera
        assert left_binding['cameraKey'] == right_binding['cameraKey'] == key
        packet['comparisons'].append({'view': view, 'cameraKey': key, 'camera': camera,
            'baseline': asset(baseline_audit / filename, modelSha256=base_hash, **left_binding),
            'after': asset(audit / 'native-builder' / filename, modelSha256=current_hash, **right_binding)})
    for era, directory in [('maker', 'native-maker'), ('mechanic', 'native-mechanic'), ('advanced', 'native-builder')]:
        era_receipt, era_views, era_receipt_asset = render_set(audit / directory, current_hash)
        era_view = era_views['full-three-quarter.png']
        packet['eraConfigurations'].append(asset(audit / directory / 'full-three-quarter.png',
            era=era, label=era.title(), modelSha256=current_hash,
            **render_binding(era_receipt_asset, era_receipt, era_view),
            scope='Native era-eligible exterior only; additional runtime mechanisms are absent from this native render.'))
    frozen, motion = audit / 'frozen', audit / 'motion'
    media = {'scope': 'Exact candidate served in the existing app through a temporary response override. Frozen captures and uncut silent motion are bounded samples, not exhaustive collision or human acting certification.',
             'frozenFrames': [], 'videos': [], 'receipts': []}
    if (frozen / 'frozen-extrema.json').is_file():
        receipt = json.loads((frozen / 'frozen-extrema.json').read_text())
        assert receipt['modelSha256'] == current_hash and receipt['status'] == 'passed'
        for filename in ['builder-jump-frozen-left.png', 'builder-thrust-frozen-right.png',
                         'builder-contact-exhibit-frozen-head.png', 'builder-claw-lift-frozen-feet.png',
                         'builder-claw-contact-frozen-feet.png', 'builder-claw-recovery-frozen-feet.png',
                         'maker-jaw-0-frozen-head.png', 'maker-jaw-100-frozen-head.png']:
            media['frozenFrames'].append(asset(frozen / filename, label=filename.removesuffix('.png').replace('-', ' '),
                modelSha256=current_hash, scope='Actual paused controller phase, with unchanged phase before and after camera moves.'))
        media['receipts'].append(asset(frozen / 'frozen-extrema.json', label='Frozen pose and keyboard receipt', modelSha256=current_hash, scope='Twelve sampled poses plus 18 marker keyboard activations.'))
    if (motion / 'motion-demonstration.json').is_file():
        receipt = json.loads((motion / 'motion-demonstration.json').read_text())
        assert receipt['modelIdentity']['sha256'] == current_hash
        for extension in ['mp4', 'webm']:
            video = motion / ('alignment-motion-demonstration.' + extension)
            if video.is_file():
                media['videos'].append(asset(video, label='Uncut silent motion · ' + extension.upper(), modelSha256=current_hash,
                    scope='Maker controls, Mechanic traversal and stop, Advanced jump/thrust/contact/claw recovery, inspection and reassembly; setup remains uncut.'))
        media['receipts'].append(asset(motion / 'motion-demonstration.json', label='Shared-clock motion receipt', modelSha256=current_hash, scope='Events and samples recorded from the same performance clock.'))
    packet['motion'] = media
    assert bool(args.previous_model) == bool(args.previous_audit), 'Provide both previous-model and previous-audit.'
    if args.previous_model:
        previous_model, previous_audit = args.previous_model.resolve(), args.previous_audit.resolve()
        previous_hash = digest(previous_model)
        previous, previous_views, previous_receipt_asset = render_set(previous_audit / 'native-builder', previous_hash)
        assert previous['rendererSha256'] == after['rendererSha256'] and previous['era'] == after['era']
        packet['models']['previous'] = asset(previous_model, label='Previous regional candidate 02')
        packet['revisionComparisons'] = []
        for view, filename in [('Feet and claws', 'feet-three-quarter.png'), ('Limb plates', 'limbs-three-quarter.png')]:
            camera = {key: new_views[filename][key] for key in ('location', 'target', 'orthographicScale')}
            assert camera == {key: previous_views[filename][key] for key in camera}
            key = hashlib.sha256(json.dumps(camera, sort_keys=True).encode()).hexdigest()[:12]
            left_binding = render_binding(previous_receipt_asset, previous, previous_views[filename])
            right_binding = render_binding(after_receipt_asset, after, new_views[filename])
            assert left_binding['camera'] == right_binding['camera'] == camera
            assert left_binding['cameraKey'] == right_binding['cameraKey'] == key
            packet['revisionComparisons'].append({'label': view, 'cameraKey': key, 'camera': camera,
                'baseline': asset(previous_audit / 'native-builder' / filename, modelSha256=previous_hash, **left_binding),
                'after': asset(audit / 'native-builder' / filename, modelSha256=current_hash, **right_binding)})
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as stream:
        json.dump(packet, stream, indent=2)
        stream.write('\n')
    print(relative(output))


if __name__ == '__main__':
    main()
