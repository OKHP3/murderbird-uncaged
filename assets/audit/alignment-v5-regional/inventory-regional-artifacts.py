#!/usr/bin/env python3
"""Inventory the regional review package; never change a model or evidence file."""
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / 'assets/audit/alignment-v5-regional/artifact-inventory.json'
TREES = ['assets/models/uncaged-alignment-v5-regional', 'assets/audit/alignment-v5-regional']
FILES = [
    'docs/alignment-regional-transfer.md',
    'docs/alignment-v5-regional-review.md',
    'docs/alignment-v5-regional-independent-review.md',
    'docs/alignment-v5-regional-candidate04-independent-review.md',
    'scripts/build-alignment-regional-review.py',
    'scripts/capture-alignment-regional-extrema.mjs',
    'scripts/capture-alignment-regional-motion.mjs',
    'scripts/compose-alignment-regional-study.py',
    'scripts/prepare-alignment-regional-review.py',
    'scripts/render-alignment-regional-study.py',
    'scripts/serve-alignment-regional-review.mjs',
    'scripts/study-alignment-limb-profiles-06.py',
    'scripts/study-alignment-limb-profiles.py',
    'scripts/study-alignment-talon-profiles-02.py',
    'scripts/study-alignment-talon-profiles-03.py',
    'scripts/study-alignment-talon-profiles.py',
    'scripts/verify-alignment-jaw-neck-matrix.mjs',
    'scripts/verify-alignment-limb-clearance.mjs',
    'scripts/verify-alignment-regional-export.mjs',
    'scripts/verify-alignment-regional-gallery.mjs',
    'scripts/verify-alignment-regional-viewer.mjs',
]


def main():
    paths = {ROOT / name for name in FILES}
    for name in TREES:
        paths.update(path for path in (ROOT / name).rglob('*') if path.is_file())
    paths.discard(OUTPUT)
    rows = []
    for path in sorted(paths):
        assert path.is_file() and not path.is_symlink(), path
        assert '.local' not in path.relative_to(ROOT).parts, path
        rows.append({'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size,
                     'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    receipt = {
        'generatedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope': 'Regional studies, selected candidate04, historical attempts, evidence, scripts and review documents. Hash inventory only; individual receipts retain their own model identities and validation limits.',
        'selection': 'assets/models/uncaged-alignment-v5-regional/current-selection.json',
        'excluded': ['This inventory itself, to avoid a circular hash.', 'Private .local material and unrelated repository files.'],
        'observedFileCount': len(rows), 'observedBytes': sum(row['bytes'] for row in rows),
        'files': rows,
    }
    OUTPUT.write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'path': str(OUTPUT.relative_to(ROOT)), 'files': len(rows), 'bytes': receipt['observedBytes']}))


if __name__ == '__main__':
    main()
