"""Run the three targeted jaw/head checks against one hash-pinned V8 GLB.

This does not modify the app or source model. Each check gets its own exclusive
output directory, and the exact GLB hash is verified before and after every run.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
MODEL_REL = Path('assets/models/uncaged-alignment-v8/murderbird-alignment-v8.glb')
MODEL_SHA = 'c8c30cc46059cdd117baf9dce4ceb6ca47040f402618dda419b21acc9d984385'
OUT_REL = Path('assets/audit/alignment-v8/head-checks/attempt-02')
TESTS = [
    ('alignment-v4-jaw-sweep', 'scripts/verify-alignment-v4-jaw-sweep.mjs', 'jaw-sweep.json'),
    ('core-jaw-sweep', 'scripts/verify-jaw-sweep.mjs', 'jaw-sweep.json'),
    ('jaw-neck-matrix', 'scripts/verify-alignment-jaw-neck-matrix.mjs', 'jaw-neck-era-matrix.json'),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    model = ROOT / MODEL_REL
    out = ROOT / OUT_REL
    assert sha(model) == MODEL_SHA, 'Frozen V8 GLB identity mismatch'
    assert not out.exists(), 'Preserve prior evidence; choose another head-check directory'
    out.mkdir(parents=True)
    shutil.copy2(Path(__file__), out / 'executed-runner.py')
    results = []
    for name, script_rel, report_name in TESTS:
        script = ROOT / script_rel
        assert script.is_file(), script
        test_out = out / name
        test_out.mkdir()
        script_copy = test_out / ('executed-' + Path(script_rel).name)
        shutil.copy2(script, script_copy)
        before = sha(model)
        assert before == MODEL_SHA
        env = os.environ.copy()
        env.update({
            'UNCAGED_MODEL': str(model),
            'UNCAGED_MODEL_SHA256': MODEL_SHA,
            'UNCAGED_AUDIT': str(test_out),
        })
        started = datetime.now(timezone.utc).isoformat()
        proc = subprocess.run(['node', str(script)], cwd=ROOT, env=env,
                              text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, check=False)
        (test_out / 'run.log').write_text(proc.stdout)
        after = sha(model)
        report = test_out / report_name
        result = {
            'name': name, 'script': script_rel, 'scriptSha256': sha(script),
            'scriptCopy': str(script_copy.relative_to(ROOT)),
            'scriptCopySha256': sha(script_copy), 'startedAtUtc': started,
            'modelPath': str(MODEL_REL), 'modelSha256Before': before,
            'modelSha256After': after, 'auditPath': str(test_out.relative_to(ROOT)),
            'exitCode': proc.returncode,
            'report': str(report.relative_to(ROOT)) if report.exists() else None,
            'reportSha256': sha(report) if report.exists() else None,
            'logSha256': sha(test_out / 'run.log'),
        }
        if report.exists():
            payload = json.loads(report.read_text())
            model_field = payload.get('model')
            result['reportedModelPath'] = model_field.get('path') if isinstance(model_field, dict) else model_field
            result['reportedModelSha256'] = payload.get('sha256') or (model_field.get('sha256') if isinstance(model_field, dict) else None)
            if name == 'alignment-v4-jaw-sweep':
                rows = payload.get('samples', [])
                result['summary'] = {
                    'status': payload.get('status'), 'sampleCount': len(rows),
                    'samplesWithProperCrossings': sum(bool(row.get('intersections')) for row in rows),
                    'totalProperCrossings': sum(row.get('intersections', 0) for row in rows),
                }
            elif name == 'core-jaw-sweep':
                rows = payload.get('samples', [])
                result['summary'] = {
                    'status': payload.get('status'), 'sampleCount': len(rows),
                    'samplesWithProperCrossings': sum(bool(row.get('intersections')) for row in rows),
                    'totalProperCrossings': sum(row.get('intersections', 0) for row in rows),
                }
            else:
                runs = payload.get('runs', [])
                result['summary'] = {
                    'runCount': len(runs),
                    'runs': [{'label': run.get('label'), 'era': run.get('pose', {}).get('era'),
                              'properCrossingPairs': run.get('result', {}).get('totals', {}).get('properCrossingPairs'),
                              'grazingPairs': run.get('result', {}).get('totals', {}).get('grazingPairs')}
                             for run in runs],
                }
        assert after == MODEL_SHA, f'Model changed while {name} ran'
        assert proc.returncode == 0, f'{name} exited {proc.returncode}; see run.log'
        assert report.exists(), f'{name} produced no report'
        if result.get('reportedModelSha256'):
            assert result['reportedModelSha256'] == MODEL_SHA, f'{name} reported a different model hash'
        if result.get('reportedModelPath'):
            reported = Path(result['reportedModelPath'])
            assert reported.resolve() == model.resolve(), f'{name} reported a different model path'
        results.append(result)
    receipt = {
        'status': 'all targeted checks completed; sampled structural evidence only',
        'model': {'path': str(MODEL_REL), 'absolutePath': str(model),
                  'sha256': MODEL_SHA, 'bytes': model.stat().st_size},
        'runnerSha256': sha(Path(__file__)),
        'nodeVersion': subprocess.run(['node', '--version'], cwd=ROOT, text=True,
                                      stdout=subprocess.PIPE, check=True).stdout.strip(),
        'tests': results,
        'limits': [
            'Jaw checks sample discrete triangle crossings; they do not prove continuous clearance, containment, physical force, browser appearance, or artistic acceptance.',
            'The jaw/neck matrix samples selected reachable states; it is not an exhaustive control sweep.',
            'No app source or model source was modified.',
        ],
    }
    (out / 'run-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'receipt': str((out / 'run-receipt.json').relative_to(ROOT)),
                      'modelSha256': MODEL_SHA,
                      'tests': [{'name': r['name'], 'summary': r.get('summary')} for r in results]}, indent=2))


if __name__ == '__main__':
    main()
