#!/usr/bin/env python3
"""Verify imported media bytes against the recorded source snapshot."""
import argparse
import hashlib
import json
from pathlib import Path


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', default='provenance/overkill-hill-import-2026-09-26.json')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / args.manifest).read_text())
    errors = []
    for item in manifest['files']:
        relative = Path(item['destination'])
        if relative.is_absolute() or '..' in relative.parts:
            errors.append(f'Unsafe destination: {relative}')
            continue
        path = root / relative
        if item.get('type') == 'symlink':
            valid = path.is_symlink() and str(path.readlink()) == item['target']
        elif item.get('type') == 'directory':
            valid = path.is_dir() and not path.is_symlink()
        else:
            valid = path.is_file() and not path.is_symlink() and path.stat().st_size == item['bytes'] and digest(path) == item['sha256']
        if not valid:
            errors.append(str(relative))
    print(json.dumps({'verified_entries': len(manifest['files']) - len(errors), 'errors': errors}, indent=2))
    raise SystemExit(bool(errors))


if __name__ == '__main__':
    main()
