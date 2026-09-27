#!/usr/bin/env python3
"""Verify imported media bytes against the recorded source snapshot."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', action='append', help='import manifest to check; repeat for multiple ledgers (default: discover provenance/*-import-*.json)')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifests = [root / path for path in args.manifest] if args.manifest else sorted((root / 'provenance').glob('*-import-*.json'))
    errors = []
    if not manifests:
        errors.append('No import manifests found')
    manifest_files = []
    total_entries = 0
    verified_entries = 0
    for manifest_path in manifests:
        manifest = json.loads(manifest_path.read_text())
        for item in manifest['files']:
            total_entries += 1
            relative = Path(item['destination'])
            if relative.is_absolute() or '..' in relative.parts:
                errors.append(f'Unsafe destination in {manifest_path.name}: {relative}')
                continue
            if item.get('type') == 'file':
                manifest_files.append(relative.as_posix())
            path = root / relative
            if item.get('type') == 'symlink':
                valid = path.is_symlink() and str(path.readlink()) == item['target']
            elif item.get('type') == 'directory':
                valid = path.is_dir() and not path.is_symlink()
            else:
                valid = path.is_file() and not path.is_symlink() and path.stat().st_size == item['bytes'] and digest(path) == item['sha256']
            if not valid:
                errors.append(f'{manifest_path.name}: {relative}')
            else:
                verified_entries += 1

    attribute_check = subprocess.run(
        ['git', 'check-attr', '-z', 'text', '--stdin'],
        cwd=root,
        input=b'\0'.join(os.fsencode(path) for path in manifest_files) + b'\0',
        capture_output=True,
        check=False,
    )
    if attribute_check.returncode:
        errors.append('Could not check Git text attributes: ' + attribute_check.stderr.decode(errors='replace').strip())
    else:
        fields = attribute_check.stdout.split(b'\0')
        if fields[-1] != b'' or (len(fields) - 1) % 3:
            errors.append('Git returned malformed text-attribute results')
        else:
            for index in range(0, len(fields) - 1, 3):
                path, attribute, value = (os.fsdecode(field) for field in fields[index:index + 3])
                if attribute != 'text' or value != 'unset':
                    errors.append(f'Imported file must have Git text=unset: {path} ({attribute}={value})')

    print(json.dumps({'verified_entries': verified_entries, 'total_entries': total_entries, 'manifests': [path.relative_to(root).as_posix() for path in manifests], 'errors': errors}, indent=2))
    raise SystemExit(bool(errors))


if __name__ == '__main__':
    main()
