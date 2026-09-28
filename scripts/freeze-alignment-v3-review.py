"""Bind the local alignment evidence to its exact reviewed binary and sources."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/audit/alignment-v3'
EXPECTED = 'c4dc308f77399410368b82443a1b21b9113cfedb258aa055906b4f13c92dda21'


def row(path):
    raw = path.read_bytes()
    return {'path': str(path.relative_to(ROOT)), 'bytes': len(raw),
            'sha256': hashlib.sha256(raw).hexdigest()}


def identity(value):
    return (value.get('modelSha256') or value.get('sha256') or
            value.get('modelIdentity', {}).get('sha256') or
            (value.get('model', {}).get('sha256') if isinstance(value.get('model'), dict) else None))


def check_capture(record, path_key, require_hash=True):
    """Verify the file identified by a capture row, never a same-named replacement."""
    relative = record[path_key]
    path = (OUT / relative).resolve()
    assert path.is_relative_to(OUT.resolve()), f'Capture escapes current evidence directory: {relative}'
    actual = row(path)
    if require_hash or record.get('sha256'):
        assert actual['sha256'] == record.get('sha256'), f'Capture hash mismatch: {relative}'
    if 'bytes' in record:
        assert actual['bytes'] == record['bytes'], f'Capture byte count mismatch: {relative}'
    return actual


model = row(ROOT / 'assets/models/uncaged-alignment-v3/murderbird-alignment-v3.glb')
assert model['sha256'] == EXPECTED, 'A different candidate needs a separately reviewed identity.'
aggregate = json.loads((OUT / 'kinematic-validation-receipt.json').read_text())
assert identity(aggregate) == EXPECTED
for item in aggregate['sources'] + aggregate['reports']:
    assert row(ROOT / item['path'])['sha256'] == item['sha256'], item['path']
receipts = []
capture_associations = {'browserScreenshots': 0, 'frozenScreenshots': 0, 'authoringViews': 0, 'authoringImageHashes': 0}
for name in ['asset-validation.json', 'kinematic-alignment.json', 'jaw-sweep.json',
             'motion-validation.json', 'structural-motion-validation.json',
             'power-move-validation.json', 'mechanism-validation.json',
             'browser-validation.json', 'frozen-extrema.json', 'motion-demonstration.json',
             'footer-copy-validation.json']:
    path = OUT / name
    value = json.loads(path.read_text())
    assert value.get('status') in {'passed', 'no-crossings-detected'}, (name, value.get('status'))
    digest = identity(value)
    if digest:
        assert digest == EXPECTED, name
    else:
        # Legacy geometry validators are tied through the aggregate's report hashes.
        assert any(item['path'] == str(path.relative_to(ROOT)) for item in aggregate['reports']), name
    if name in {'browser-validation.json', 'frozen-extrema.json'}:
        screenshots = value.get('screenshots', [])
        assert screenshots, f'Capture receipt is empty: {name}'
        assert len({item['filename'] for item in screenshots}) == len(screenshots), f'Duplicate capture filenames: {name}'
        for item in screenshots:
            check_capture(item, 'filename')
        capture_associations['browserScreenshots' if name == 'browser-validation.json' else 'frozenScreenshots'] = len(screenshots)
    if name == 'motion-demonstration.json':
        assert {item['filename'] for item in value.get('media', [])} == {
            'alignment-motion-demonstration.webm', 'alignment-motion-demonstration.mp4'}, 'Motion originals and derivative must both be recorded.'
        for item in value['media']:
            check_capture(item, 'filename')
    if name == 'footer-copy-validation.json':
        assert value['mainSourceSha256'] == row(ROOT / 'src/main.js')['sha256'], 'Footer source changed after its check.'
    receipts.append(row(path))
editable_source = row(ROOT / 'assets/models/uncaged-alignment-v3/murderbird-alignment-v3.blend')
authoring = json.loads((OUT / 'authoring-views.json').read_text())
authoring_rows = authoring if isinstance(authoring, list) else authoring.get('views', [])
assert authoring_rows, 'Authoring view receipt is empty.'
assert len({item['image'] for item in authoring_rows}) == len(authoring_rows), 'Duplicate authoring image names.'
for item in authoring_rows:
    assert item.get('modelSha256') == EXPECTED, f'Authoring model identity mismatch: {item["image"]}'
    assert item.get('sourceSha256') == editable_source['sha256'], f'Authoring source identity mismatch: {item["image"]}'
    check_capture(item, 'image', require_hash=False)
    capture_associations['authoringViews'] += 1
    capture_associations['authoringImageHashes'] += bool(item.get('sha256'))
sources = []
for folder in ['src', 'scripts', 'tests']:
    for path in sorted((ROOT / folder).rglob('*')):
        if path.is_file() and path.suffix in {'.js', '.mjs', '.css', '.py', '.json'} and '__pycache__' not in path.parts:
            sources.append(row(path))
for name in ['package.json', 'package-lock.json', 'vite.config.js', 'README.md',
             'docs/alignment-v3-review.md', 'docs/alignment-v3-independent-review.md',
             'assets/models/uncaged-alignment-v3/README.md']:
    sources.append(row(ROOT / name))
media = [row(path) for path in sorted(OUT.iterdir()) if path.is_file()
         and path.suffix in {'.png', '.mp4', '.webm', '.html'}]
report = {
    'generatedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'assessment': 'Geometry and articulation candidate; full likeness revision remains required',
    'baseRevision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'branch': subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip(),
    'model': model,
    'editableSource': editable_source,
    'inventory': row(ROOT / 'assets/models/uncaged-alignment-v3/alignment-inventory.json'),
    'sourceReferencePacket': row(ROOT / 'assets/models/uncaged-neutral-v2/reference-packet.json'),
    'runtimeToolAndReviewSources': sources,
    'receipts': receipts + [row(OUT / 'kinematic-validation-receipt.json')],
    'media': media,
    'authoringViews': row(OUT / 'authoring-views.json'),
    'captureAssociationsVerified': capture_associations,
    'boundaries': [
        'Preserved v2 hashes unchanged; matching model/audit intermediate iterations retained.',
        'No full PRD score, approved exterior, finished surfaces or purposeful supported claw grip.',
        'No continuous collision, physical-force, human acting, screen-reader or physical-device certification.',
        'No push, merge, deployment or Replit publication.',
    ],
}
(OUT / 'candidate-assessment.json').write_text(json.dumps(report, indent=2) + '\n')
print(f'Bound {len(sources)} source/review files, {len(receipts)} receipts and {len(media)} media files to {EXPECTED}')
