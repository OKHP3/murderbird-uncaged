"""Bind the exact V4 model, current validation sources, reports and media.

Run only after the final model and every required validator/capture receipt has
been regenerated. This script reads and verifies those files, then writes the
kinematic binding receipt and candidate assessment. It does not repair or
reinterpret failed validation results.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/audit/alignment-v4'
MODEL_REL = 'assets/models/uncaged-alignment-v4/murderbird-alignment-v4.glb'
BLEND_REL = 'assets/models/uncaged-alignment-v4/murderbird-alignment-v4.blend'

# Each legacy report is explicitly associated with the validator and runtime
# inputs that produced it. The aggregate records their exact hashes, allowing
# reports without their own source manifest to remain auditable.
REPORT_INPUTS = {
    'asset-validation.json': ['scripts/verify-alignment-v4-assets.py'],
    'kinematic-alignment.json': ['scripts/verify-alignment-kinematics.mjs', 'src/scene/rigid-leg-kinematics.js', 'src/scene/era-motion.js'],
    'jaw-sweep.json': ['scripts/verify-alignment-v4-jaw-sweep.mjs'],
    'motion-validation.json': ['scripts/verify-era-motion.mjs', 'src/scene/era-motion.js', 'src/scene/era-controller.js', 'src/scene/presence-state.js'],
    'structural-motion-validation.json': ['scripts/verify-structural-motion.mjs', 'src/scene/era-motion.js', 'src/scene/era-mechanisms.js'],
    'power-move-validation.json': ['scripts/verify-advanced-power-moves.mjs', 'src/scene/era-motion.js', 'src/scene/era-controller.js'],
    'mechanism-validation.json': ['scripts/verify-alignment-v4-mechanisms.mjs', 'src/scene/era-motion.js', 'src/scene/era-mechanisms.js'],
    'browser-validation.json': ['scripts/verify-alignment-v4-browser.mjs', 'src/main.js', 'src/scene/era-motion.js', 'src/scene/era-controller.js', 'src/scene/presence-state.js'],
    'frozen-extrema.json': ['scripts/capture-alignment-v4-extrema.mjs', 'src/main.js', 'src/scene/era-motion.js', 'src/scene/era-controller.js'],
    'motion-demonstration.json': ['scripts/capture-alignment-v4-motion.mjs', 'src/main.js', 'src/scene/era-motion.js', 'src/scene/era-controller.js', 'src/scene/presence-state.js'],
    'claw-contact-v4.json': ['scripts/verify-claw-contact-v4.mjs', 'src/scene/era-motion.js', 'src/scene/era-controller.js', 'src/scene/presence-state.js', 'src/scene/rigid-leg-kinematics.js'],
}
PASS_STATUSES = {'passed', 'no-crossings-detected'}
NAMED_STRING_CHECKS = {'asset-validation.json', 'mechanism-validation.json'}


def fail(message: str) -> None:
    raise SystemExit(f'freeze refused: {message}')


def row(path: Path) -> dict:
    raw = path.read_bytes()
    return {'path': path.relative_to(ROOT).as_posix(), 'bytes': len(raw),
            'sha256': hashlib.sha256(raw).hexdigest()}


def checked_path(relative: str, base: Path) -> Path:
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(base.resolve()):
        fail(f'path escapes allowed directory: {relative}')
    if not path.is_file():
        fail(f'missing file: {relative}')
    return path


def model_identity(value: dict) -> str | None:
    return (value.get('modelSha256') or value.get('sha256') or
            (value.get('modelIdentity') or {}).get('sha256') or
            ((value.get('model') or {}).get('sha256') if isinstance(value.get('model'), dict) else None))


def require_model_identity(value: dict, expected: str, name: str) -> str:
    digest = model_identity(value)
    if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-fA-F]{64}', digest) or digest.lower() != expected:
        fail(f'{name} lacks the exact current V4 model SHA-256')
    return digest.lower()


def model_path(value: dict) -> str | None:
    item = value.get('modelPath') or value.get('model') or (value.get('modelIdentity') or {}).get('path')
    if isinstance(item, dict):
        item = item.get('path')
    if not isinstance(item, str):
        return None
    path = Path(item)
    try:
        return path.resolve().relative_to(ROOT).as_posix() if path.is_absolute() else path.as_posix()
    except ValueError:
        return item


def generated_time(value: dict, name: str) -> dt.datetime:
    raw = value.get('generatedAt') or value.get('reviewedAt') or value.get('date')
    if not raw:
        fail(f'{name} has no generation/review timestamp')
    try:
        stamp = dt.datetime.fromisoformat(raw.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        fail(f'{name} has an invalid generation timestamp: {raw!r}')
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=dt.timezone.utc)
    return stamp.astimezone(dt.timezone.utc)


def validate_status(value: dict, name: str, allow_review: bool = False) -> None:
    status = value.get('status')
    if status in PASS_STATUSES:
        pass
    elif allow_review and status in {'revision-required', 'review-required'}:
        pass
    else:
        fail(f'{name} status is not accepted: {status!r}')
    checks = value.get('checks')
    if checks is None:
        return
    if isinstance(checks, dict):
        # Mechanism validation uses this field for named, structured evidence
        # rather than a flat list of check rows.
        if name != 'mechanism-validation.json' or not checks:
            fail(f'{name} has an unsupported checks object')

        def verify_nested_statuses(item: object) -> None:
            if isinstance(item, dict):
                if 'status' in item and item['status'] != 'passed':
                    fail(f'{name} contains a failed check: {item.get("name", item["status"])}')
                for child in item.values():
                    verify_nested_statuses(child)
            elif isinstance(item, list):
                for child in item:
                    verify_nested_statuses(child)

        verify_nested_statuses(checks)
        return
    if not isinstance(checks, list):
        fail(f'{name} checks must be a list')
    if not checks:
        fail(f'{name} checks list is empty')
    for item in checks:
        if isinstance(item, dict):
            if item.get('status') != 'passed':
                fail(f'{name} contains a failed or malformed check: {item.get("name", item)!r}')
        elif isinstance(item, str):
            if name not in NAMED_STRING_CHECKS or not item.strip():
                fail(f'{name} contains an unsupported string check row')
        else:
            fail(f'{name} contains a malformed check row: {item!r}')


def verify_capture(record: dict, path_key: str, base: Path = OUT) -> dict:
    relative = record.get(path_key)
    if not isinstance(relative, str):
        fail(f'capture row lacks {path_key}: {record}')
    digest = record.get('sha256')
    if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-fA-F]{64}', digest):
        fail(f'capture row lacks a valid SHA-256: {relative}')
    byte_count = record.get('bytes')
    if not isinstance(byte_count, int) or isinstance(byte_count, bool) or byte_count <= 0:
        fail(f'capture row lacks a positive byte count: {relative}')
    path = checked_path((base.relative_to(ROOT) / relative).as_posix(), base)
    actual = row(path)
    if actual['sha256'] != digest.lower():
        fail(f'capture hash mismatch: {relative}')
    if actual['bytes'] != byte_count:
        fail(f'capture byte count mismatch: {relative}')
    return actual


def audit_path(relative: str) -> Path:
    candidate = Path(relative)
    full = ROOT / candidate if candidate.parts and candidate.parts[0] == 'assets' else OUT / candidate
    full = full.resolve()
    if not full.is_relative_to(OUT.resolve()) or not full.is_file():
        fail(f'path is missing or outside V4 audit directory: {relative}')
    return full


def verify_source_identity(value: dict, label: str) -> list[dict]:
    identities = value.get('sourceIdentity') or value.get('sourceHashes')
    if isinstance(identities, dict):
        identities = [{'path': path, 'sha256': digest} for path, digest in identities.items()]
    if not isinstance(identities, list) or not identities:
        fail(f'{label} has no source identity list')
    verified = []
    for item in identities:
        source = item.get('path')
        digest = item.get('sha256')
        if not isinstance(source, str) or not isinstance(digest, str):
            fail(f'{label} contains an incomplete source identity row: {item}')
        actual = row(checked_path(source, ROOT))
        if actual['sha256'] != digest:
            fail(f'{label} source changed since capture: {source}')
        verified.append(actual)
    return verified


def validate_autonomy_manifest(relative: str, expected: str) -> tuple[dict, list[dict]]:
    manifest_path = checked_path(relative, OUT)
    manifest = json.loads(manifest_path.read_text())
    if model_identity(manifest) != expected or model_path(manifest) != MODEL_REL:
        fail('autonomy manifest is not bound to the requested V4 model')
    verify_source_identity(manifest, manifest_path.name)
    runs = manifest.get('runs')
    if not isinstance(runs, list) or len(runs) < 2:
        fail('autonomy manifest must identify at least two separate runs')
    checked_media = []
    for run in runs:
        if not isinstance(run, dict) or run.get('status') != 'passed':
            fail(f'autonomy run did not pass: {run}')
        run_rel = run if isinstance(run, str) else run.get('receipt') or run.get('path')
        if not isinstance(run_rel, str):
            fail(f'autonomy run has no receipt path: {run}')
        run_path = audit_path(run_rel)
        if isinstance(run, dict):
            expected_run_receipt = run.get('receiptSha256') or run.get('receiptSHA256') or run.get('sha256')
            actual_run_receipt = row(run_path)
            if not expected_run_receipt or actual_run_receipt['sha256'] != expected_run_receipt:
                fail(f'autonomy run receipt hash mismatch: {run_rel}')
        receipt = json.loads(run_path.read_text())
        if model_identity(receipt) != expected or model_path(receipt) != MODEL_REL:
            fail(f'autonomy run is not bound to the requested V4 model: {run_rel}')
        validate_status(receipt, run_path.name)
        verify_source_identity(receipt, run_path.name)
        media = receipt.get('media', [])
        if not media and isinstance(run, dict):
            media = run.get('media', [])
        for item in media:
            media_rel = item.get('filename') or item.get('path')
            if not isinstance(media_rel, str):
                fail(f'autonomy media row lacks a path: {item}')
            media_path = audit_path(media_rel)
            actual = row(media_path)
            if actual['sha256'] != item.get('sha256') or ('bytes' in item and actual['bytes'] != item['bytes']):
                fail(f'autonomy media hash/size mismatch: {media_rel}')
            checked_media.append(actual)
    if not checked_media:
        fail('autonomy manifest contains no hash-verified media')
    extensions = {Path(item['path']).suffix.lower() for item in checked_media}
    if not {'.webm', '.mp4'}.issubset(extensions):
        fail('autonomy manifest must include hash-verified WebM and MP4 recordings')
    return row(manifest_path), checked_media


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected-model-sha', required=True,
                        help='Exact reviewed V4 GLB SHA-256 (64 hexadecimal characters)')
    parser.add_argument('--autonomy-manifest', required=True,
                        help='Explicit collision-safe autonomy demonstration manifest, relative to repository root')
    parser.add_argument('--extra-receipt', action='append', default=[],
                        help='Optional extra receipt under the V4 audit directory; must include current model and sourceHashes')
    args = parser.parse_args()
    expected = args.expected_model_sha.lower()
    if not re.fullmatch(r'[0-9a-f]{64}', expected):
        fail('--expected-model-sha must contain exactly 64 hexadecimal characters')

    model = row(ROOT / MODEL_REL)
    if model['sha256'] != expected:
        fail(f'current V4 model SHA is {model["sha256"]}, expected {expected}')
    blend = row(ROOT / BLEND_REL)

    source_paths = []
    for folder in ['src', 'scripts', 'tests']:
        source_paths.extend(path for path in sorted((ROOT / folder).rglob('*'))
                            if path.is_file() and path.suffix in {'.js', '.mjs', '.css', '.py', '.json'}
                            and '__pycache__' not in path.parts)
    source_paths.extend(ROOT / name for name in [
        'package.json', 'package-lock.json', 'vite.config.js', 'README.md',
        'docs/alignment-v4-review.md', 'docs/murderbird-evaluation-prd.md',
        'assets/models/uncaged-alignment-v4/README.md',
    ])
    independent_review = ROOT / 'docs/alignment-v4-independent-review.md'
    if independent_review.is_file():
        source_paths.append(independent_review)
    source_paths.append(Path(__file__).resolve())
    source_rows = [row(path) for path in sorted(set(source_paths))]
    current_source_hash = {item['path']: item['sha256'] for item in source_rows}

    reports = []
    report_values = {}
    for name, input_names in REPORT_INPUTS.items():
        path = OUT / name
        value = json.loads(path.read_text())
        validate_status(value, name)
        digest = require_model_identity(value, expected, name)
        bound_model_path = model_path(value)
        if bound_model_path != MODEL_REL:
            fail(f'{name} model path is not the current V4 export: {bound_model_path!r}')
        inputs = [row(ROOT / input_name) for input_name in input_names]
        newest_input = max((ROOT / item).stat().st_mtime for item in input_names + [MODEL_REL])
        report_time = generated_time(value, name).timestamp()
        if report_time + 1e-3 < newest_input:
            fail(f'{name} predates the current model or validator/runtime inputs; rerun it')
        reports.append({'receipt': row(path), 'modelSha256': digest,
                        'modelPath': bound_model_path, 'generatedAt': generated_time(value, name).isoformat(),
                        'inputs': inputs})
        report_values[name] = value

    for name in ['browser-validation.json', 'frozen-extrema.json']:
        value = report_values[name]
        captures = value.get('screenshots', [])
        if not captures:
            fail(f'{name} has no recorded screenshots')
        names = [item.get('filename') for item in captures]
        if None in names or len(set(names)) != len(names):
            fail(f'{name} has missing or duplicate screenshot paths')
        for item in captures:
            verify_capture(item, 'filename')

    frozen = report_values['frozen-extrema.json']
    frozen_poses = {item.get('name') for item in frozen.get('poses', [])}
    required_poses = {f'builder-claw-{stage}' for stage in
                      ['approach', 'lift', 'contact', 'scrape', 'release', 'recovery']}
    if not required_poses.issubset(frozen_poses):
        fail(f'frozen extrema lacks claw phases: {sorted(required_poses - frozen_poses)}')

    motion = report_values['motion-demonstration.json']
    if not motion.get('samples') or not any(item.get('clawAction') for item in motion['samples']):
        fail('motion demonstration contains no sampled claw action telemetry')
    media = motion.get('media', [])
    if not media:
        fail('motion demonstration does not identify hash-bound source media')
    for item in media:
        verify_capture(item, 'filename')

    autonomy_manifest, autonomy_media = validate_autonomy_manifest(args.autonomy_manifest, expected)

    iteration_review_path = OUT / 'iteration-review.json'
    iteration_review = json.loads(iteration_review_path.read_text())
    if iteration_review.get('status'):
        validate_status(iteration_review, iteration_review_path.name, allow_review=True)
    elif iteration_review.get('assessment') not in {'accepted', 'revision-required', 'review-required'}:
        fail(f'iteration review has no recognized assessment: {iteration_review.get("assessment")!r}')
    if model_identity(iteration_review) != expected:
        fail('iteration review is bound to a different model')
    if iteration_review.get('sourceSha256') != blend['sha256']:
        fail('iteration review is bound to a different editable source')
    if generated_time(iteration_review, iteration_review_path.name).timestamp() + 1e-3 < max(
            (ROOT / MODEL_REL).stat().st_mtime, (ROOT / BLEND_REL).stat().st_mtime):
        fail('iteration review predates the current model or editable source')

    authoring_path = OUT / 'authoring-views.json'
    authoring = json.loads(authoring_path.read_text())
    authoring_rows = authoring if isinstance(authoring, list) else authoring.get('views', [])
    if not authoring_rows:
        fail('authoring view receipt is empty')
    if not (ROOT / BLEND_REL).is_file():
        fail(f'missing editable V4 source: {BLEND_REL}')
    for item in authoring_rows:
        if item.get('modelSha256') != expected or item.get('sourceSha256') != blend['sha256']:
            fail(f'authoring view is bound to a different model/source: {item.get("image")}')
        verify_capture(item, 'image', OUT)

    extra_rows = []
    for relative in args.extra_receipt:
        path = checked_path(relative, OUT)
        value = json.loads(path.read_text())
        validate_status(value, path.name)
        if model_identity(value) != expected or model_path(value) != MODEL_REL:
            fail(f'optional receipt is not bound to the requested V4 model: {relative}')
        source_hashes = value.get('sourceHashes') or value.get('sourceSha256')
        if not isinstance(source_hashes, dict) or not source_hashes:
            fail(f'optional receipt has no sourceHashes binding: {relative}')
        for source, digest in source_hashes.items():
            actual = row(checked_path(source, ROOT))
            if actual['sha256'] != digest:
                fail(f'optional receipt source hash changed: {source}')
        extra_rows.append(row(path))

    aggregate = {
        'generatedAt': dt.datetime.now(dt.timezone.utc).isoformat(),
        'model': model,
        'editableSource': blend,
        'sources': source_rows,
        'reports': reports,
        'autonomyManifest': autonomy_manifest,
        'autonomyMedia': autonomy_media,
        'iterationReview': row(iteration_review_path),
        'additionalReceipts': extra_rows,
        'method': 'Explicit allowlist of validators, V4 model identity/path, source timestamps and hashes; no report discovery by newest-file selection.',
    }
    aggregate_path = OUT / 'kinematic-validation-receipt.json'
    aggregate_path.write_text(json.dumps(aggregate, indent=2) + '\n')

    unit_log = OUT / 'unit-tests.log'
    if not unit_log.is_file():
        fail('current V4 unit log is missing')
    unit_summary = dict(re.findall(r'(?m)^.*?\b(tests|pass|fail|skipped|cancelled) (\d+)\s*$', unit_log.read_text()))
    if not int(unit_summary.get('tests', 0)) or unit_summary.get('tests') != unit_summary.get('pass') or any(unit_summary.get(key) != '0' for key in ['fail', 'skipped', 'cancelled']):
        fail('current V4 unit log does not establish a complete passing suite')
    receipt_rows = [item['receipt'] for item in reports] + [row(unit_log), row(aggregate_path), row(authoring_path),
                    row(iteration_review_path), autonomy_manifest] + extra_rows
    media_rows = [row(path) for path in sorted(OUT.iterdir()) if path.is_file() and path.suffix in {'.png', '.mp4', '.webm', '.html'}]
    candidate = {
        'generatedAt': dt.datetime.now(dt.timezone.utc).isoformat(),
        'assessment': 'V4 technical evidence bound to the explicitly reviewed exported model',
        'overallAssessment': 'revision-required',
        'technicalEvidenceStatus': 'bound-and-verified',
        'iterationReviewAssessment': iteration_review.get('assessment'),
        'baseRevision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'branch': subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip(),
        'model': model,
        'editableSource': blend,
        'runtimeToolAndReviewSources': source_rows,
        'receipts': receipt_rows,
        'media': media_rows,
        'authoringViews': row(authoring_path),
        'captureAssociationsVerified': {
            'browserScreenshots': len(report_values['browser-validation.json'].get('screenshots', [])),
            'frozenScreenshots': len(frozen.get('screenshots', [])),
            'authoringViews': len(authoring_rows),
            'autonomyRuns': len(json.loads(checked_path(args.autonomy_manifest, OUT).read_text()).get('runs', [])),
        },
        'boundaries': [
            'Evidence covers the exact V4 exported model and declared validator scope only.',
            'Kinematic contact does not establish force, grip, balance, or continuous collision clearance.',
            'Full likeness, human acting, screen reader, physical-device, and owner acceptance remain separate.',
            'No push, merge, deployment, or Replit publication is authorized by this local freeze.',
        ],
    }
    (OUT / 'candidate-assessment.json').write_text(json.dumps(candidate, indent=2) + '\n')
    print(f'Bound {len(source_rows)} source files, {len(reports)} required validator/capture receipts, '
          f'{len(extra_rows)} optional receipts, and {len(media_rows)} media files to {expected}')


if __name__ == '__main__':
    main()
