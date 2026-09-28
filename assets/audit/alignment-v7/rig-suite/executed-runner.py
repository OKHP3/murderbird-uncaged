"""Freeze one V7 export and run the affected rigid motion/limb checks locally."""
from pathlib import Path
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import platform
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--model', required=True)
parser.add_argument('--sha256', required=True)
parser.add_argument('--out', required=True)
args = parser.parse_args()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


model = (ROOT / args.model).resolve()
out = (ROOT / args.out).resolve()
assert digest(model) == args.sha256, 'Exact model identity does not match'
assert not out.exists(), 'Use a new evidence directory; never overwrite receipts'
out.mkdir(parents=True)
snapshot = out / 'frozen-model.glb'
shutil.copy2(model, snapshot)
assert digest(snapshot) == args.sha256
shutil.copy2(Path(__file__), out / 'executed-runner.py')
checks = ['verify-era-motion', 'verify-structural-motion', 'verify-alignment-kinematics',
          'verify-advanced-power-moves', 'verify-claw-contact-v4',
          'verify-inspection-pose-v4', 'verify-alignment-limb-clearance']
sources = [ROOT / 'src/main.js', *sorted((ROOT / 'src/scene').glob('*.js')),
           ROOT / 'scripts/load-rigid-validation.mjs', ROOT / 'package.json',
           ROOT / 'package-lock.json', *[ROOT / f'scripts/{name}.mjs' for name in checks],
           Path(__file__)]
source_hashes = {str(p.relative_to(ROOT)): digest(p) for p in sources}
report = {
    'startedAtUtc': datetime.now(timezone.utc).isoformat(),
    'gitHead': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'model': {'path': str(model.relative_to(ROOT)), 'sha256': args.sha256,
              'snapshot': str(snapshot.relative_to(ROOT)), 'bytes': snapshot.stat().st_size},
    'sourcesFrozenBeforeChecks': source_hashes,
    'runtime': {'node': subprocess.check_output(['node', '--version'], text=True).strip(),
                'platform': platform.system(), 'architecture': platform.machine()},
    'checks': [],
    'limits': ['Deterministic kinematic/geometry checks, not physical simulation.',
               'Limb clearance checks sampled adjacent plate pairs only, excluding frame/bearings.',
               'No authoring, browser, device, continuous collision or artistic acceptance.'],
}
report_path = out / 'run-manifest.json'
report_path.write_text(json.dumps(report, indent=2) + '\n')
for name in checks:
    target = out / name
    env = {**os.environ, 'UNCAGED_MODEL': str(snapshot), 'UNCAGED_AUDIT': str(target),
           'UNCAGED_MODEL_SHA256': args.sha256, 'UNCAGED_EXPECTED_MODEL_SHA256': args.sha256}
    command = ['node', f'scripts/{name}.mjs']
    log = out / f'{name}.log'
    with log.open('x') as stream:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
    evidence = [{'path': str(p.relative_to(ROOT)), 'sha256': digest(p), 'bytes': p.stat().st_size}
                for p in sorted(target.rglob('*')) if p.is_file()] if target.exists() else []
    report['checks'].append({'name': name, 'command': command, 'exitCode': result.returncode,
                            'log': str(log.relative_to(ROOT)), 'logSha256': digest(log),
                            'evidence': evidence})
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    print(name, 'PASS' if result.returncode == 0 else 'FAIL', flush=True)
report['sourceHashesUnchangedAfterChecks'] = all(digest(ROOT / p) == h for p, h in source_hashes.items())
report['modelUnchangedAfterChecks'] = digest(model) == digest(snapshot) == args.sha256
report['completedAtUtc'] = datetime.now(timezone.utc).isoformat()
report['status'] = 'pass' if (all(c['exitCode'] == 0 for c in report['checks'])
    and report['sourceHashesUnchangedAfterChecks'] and report['modelUnchangedAfterChecks']) else 'fail'
report_path.write_text(json.dumps(report, indent=2) + '\n')
assert report['status'] == 'pass', 'Affected checks failed; inspect preserved reports'
