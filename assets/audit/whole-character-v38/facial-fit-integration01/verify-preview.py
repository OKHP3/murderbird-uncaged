"""Read-only checkpoint verification, in one process; no hydration or Git writes.

Run after the authorized fetch/fast-forward and exact manifest asset hydration.
Only current checkpoint media is hashed. An ancestor diff proves earlier tracked
asset paths were not changed by this checkpoint; Git status detects local edits.
This is delivery evidence, never artistic or mechanical acceptance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.parse
import urllib.request

parser = argparse.ArgumentParser()
parser.add_argument('--sha', required=True)
parser.add_argument('--parent', required=True)
parser.add_argument('--port', type=int, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[4]
audit = Path(__file__).resolve().parent
origin = f'http://127.0.0.1:{args.port}/'

def git(*parts):
    return subprocess.check_output(['git', '-C', str(root), *parts], text=True).strip()

def sha(data):
    return hashlib.sha256(data).hexdigest()

def served(path):
    with urllib.request.urlopen(origin + urllib.parse.quote(path, safe='/'), timeout=20) as response:
        assert response.status == 200, (path, response.status)
        return response.read()

assert re.fullmatch(r'[0-9a-f]{40}', args.sha), 'Expected full Git SHA'
assert re.fullmatch(r'[0-9a-f]{40}', args.parent), 'Expected full parent SHA'
assert git('rev-parse', 'HEAD') == args.sha, 'Wrong checkout'
subprocess.run(['git', '-C', str(root), 'merge-base', '--is-ancestor', args.parent, args.sha], check=True)
asset_changes = git('diff', '--name-status', args.parent, args.sha, '--', 'assets')
assert all(line.startswith('A\t') for line in asset_changes.splitlines()), 'Earlier asset paths changed; inspect before claiming preservation'
results = []
for item in json.loads((audit / 'asset-routes.json').read_text()):
    relative = item['path']
    path = root / relative
    assert path.resolve().is_relative_to(root.resolve()), 'Path outside checkout'
    data = path.read_bytes()
    pointer = git('show', f'{args.sha}:{relative}')
    oid = re.search(r'^oid sha256:([0-9a-f]{64})$', pointer, re.M)
    size = re.search(r'^size (\d+)$', pointer, re.M)
    assert oid and size, ('Expected LFS pointer', relative)
    assert sha(data) == item['sha256'] == oid.group(1), ('File hash mismatch', relative)
    assert len(data) == int(size.group(1)), ('File size mismatch', relative)
    assert sha(served(relative)) == item['sha256'], ('Served bytes mismatch', relative)
    results.append({'path': relative, 'sha256': item['sha256'], 'bytes': len(data)})
review = str((audit / 'review.html').relative_to(root))
assert b'MurderBird' in served(review), 'Review route failed'
evidence = str((audit / 'export-boundary.json').relative_to(root))
assert sha(served(evidence)) == sha((root / evidence).read_bytes()), 'Evidence route mismatch'
assert "'bill-vault02':" in (root / 'src/scene/presence-exhibit.js').read_text(), 'Candidate selector missing'
assert "'facial-fit02':" in (root / 'src/scene/presence-exhibit.js').read_text(), 'Final candidate selector missing'
status = git('status', '--porcelain')
result = {'sha': args.sha, 'parent': args.parent, 'clean': not status,
          'statusPaths': status.splitlines(), 'assets': results,
          'routes': [review, evidence],
          'preservation': 'Checkpoint adds asset paths only; no earlier tracked asset path changed.',
          'scope': 'Read-only delivery check. No likeness, clearance, motion or deployment acceptance.'}
print(json.dumps(result, indent=2))
raise SystemExit(0 if not status else 2)
