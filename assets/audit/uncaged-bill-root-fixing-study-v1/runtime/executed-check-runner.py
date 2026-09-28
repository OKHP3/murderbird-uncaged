"""Run two pinned, bounded GLB checks and preserve exact commands/outputs."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[4]
MODEL = Path('assets/models/uncaged-bill-root-fixing-study-v1/murderbird-bill-root-fixing-study-v1.glb')
MODEL_SHA = 'f5c0f5ad99ace316ed84426d2a1148a093706612c9602d78b93023d46d989e6e'
RUNTIME = Path('assets/audit/uncaged-bill-root-fixing-study-v1/runtime')
JAW_SCRIPT = Path('scripts/verify-alignment-v4-jaw-sweep.mjs')
STRUCTURE_SCRIPT = Path('scripts/verify-structural-motion.mjs')
LOADER = Path('scripts/load-rigid-validation.mjs')
STRUCTURE_SOURCES = [Path('src/scene/era-controller.js'), Path('src/scene/era-mechanisms.js'), Path('src/scene/era-motion.js')]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path):
    return {'path': str(path), 'bytes': path.stat().st_size, 'sha256': digest(path)}


def run(label, script, out_dir, report, additional_sources):
    destination = ROOT / out_dir
    destination.mkdir(parents=True, exist_ok=False)
    copied_script = destination / ('executed-' + script.name)
    shutil.copy2(ROOT / script, copied_script)
    copied_loader = destination / 'executed-load-rigid-validation.mjs'
    shutil.copy2(ROOT / LOADER, copied_loader)
    sources = [script, LOADER, *additional_sources]
    if Path('package-lock.json').exists():
        sources.append(Path('package-lock.json'))
    input_hashes_before = {str(path): digest(ROOT / path) for path in sources}
    assert digest(ROOT / script) == digest(copied_script)
    assert digest(ROOT / LOADER) == digest(copied_loader)
    command = ['node', str(script)]
    env = dict(os.environ)
    env['UNCAGED_MODEL'] = str(MODEL)
    env['UNCAGED_AUDIT'] = str(out_dir)
    result = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True)
    output = result.stdout + (('\n--- STDERR ---\n' + result.stderr) if result.stderr else '')
    (destination / 'command-output.txt').write_text(output)
    model_after = digest(ROOT / MODEL)
    source_hashes_after = {str(path): digest(ROOT / path) for path in sources}
    assert model_after == MODEL_SHA, 'Pinned diagnostic GLB changed during verifier execution'
    generated = ROOT / report
    parsed = json.loads(generated.read_text()) if generated.exists() else None
    receipt = {
        'label': label,
        'generatedAtUtc': datetime.now(timezone.utc).isoformat(),
        'command': command,
        'cwd': str(ROOT),
        'environment': {'UNCAGED_MODEL': str(MODEL), 'UNCAGED_AUDIT': str(out_dir)},
        'exitCode': result.returncode,
        'status': 'passed' if result.returncode == 0 else 'failed',
        'modelBefore': artifact(ROOT / MODEL), 'modelAfterSha256': model_after,
        'executedVerifierCopy': artifact(copied_script),
        'executedLoaderCopy': artifact(copied_loader),
        'inputHashesBefore': input_hashes_before,
        'inputHashesAfter': source_hashes_after,
        'sourceInputsUnchanged': input_hashes_before == source_hashes_after,
        'output': artifact(destination / 'command-output.txt'),
        'report': artifact(generated) if generated.exists() else None,
        'reportedModelSha256': (parsed.get('modelSha256') or parsed.get('sha256')) if isinstance(parsed, dict) else None,
        'reportedStatus': parsed.get('status') if isinstance(parsed, dict) else None,
    }
    (destination / 'execution-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    assert input_hashes_before == source_hashes_after, 'Verifier/source changed during run'
    return receipt


def main():
    assert digest(ROOT / MODEL) == MODEL_SHA, 'Pinned GLB hash mismatch'
    assert not (ROOT / RUNTIME / 'jaw-sweep').exists()
    assert not (ROOT / RUNTIME / 'structure').exists()
    jaw = run('33-sample jaw against fixed head geometry', JAW_SCRIPT,
              RUNTIME / 'jaw-sweep', RUNTIME / 'jaw-sweep/jaw-sweep.json', [])
    structure = run('structural contact and motion regressions', STRUCTURE_SCRIPT,
                    RUNTIME / 'structure', RUNTIME / 'structure/structural-motion-validation.json',
                    STRUCTURE_SOURCES)
    jaw_json = json.loads((ROOT / RUNTIME / 'jaw-sweep/jaw-sweep.json').read_text())
    names = set(jaw_json['stationaryMeshes'])
    pinned_names = {f'Bill root fixing{s}' for s in ('', '.001', '.002', '.003')}
    jaw['stationaryFixingNamesIncluded'] = sorted(names & pinned_names)
    assert names & pinned_names == pinned_names, f'Jaw sweep omitted fixings: {sorted(pinned_names-names)}'
    # Preserve the augmented inclusion assertion in the execution receipt.
    (ROOT / RUNTIME / 'jaw-sweep/execution-receipt.json').write_text(json.dumps(jaw, indent=2) + '\n')
    print(json.dumps({'jawSweep': {'status': jaw['status'], 'reportedStatus': jaw['reportedStatus'],
                                  'fixingsIncluded': jaw['stationaryFixingNamesIncluded'],
                                  'report': jaw['report']},
                      'structure': {'status': structure['status'], 'reportedStatus': structure['reportedStatus'],
                                    'report': structure['report']}}))
    if jaw['exitCode'] or structure['exitCode']:
        sys.exit(1)


if __name__ == '__main__':
    main()
