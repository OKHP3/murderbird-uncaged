"""Bind already captured browser artifacts; does not run or certify the browser."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/audit/alignment-v5/browser-1e7febcc03d9'
MODEL = ROOT / 'assets/models/uncaged-alignment-v5/murderbird-alignment-v5.glb'


def identity(path):
    data = path.read_bytes()
    return {'path': str(path.relative_to(ROOT)), 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest()}


browser = json.loads((OUT / 'browser-review.json').read_text())
model = identity(MODEL)
assert browser['servedModel']['sha256'] == model['sha256']
assert browser['servedModel']['bytes'] == model['bytes']
poses = {p['name']: p for p in browser['poses']}
for era in ('maker', 'mechanic', 'advanced'):
    assert poses[f'{era}-exploded']['state']['open'] == 1
    assert poses[f'{era}-exploded']['state']['separation'] == 1
    assert poses[f'{era}-reassembled']['state']['open'] == 0
    assert poses[f'{era}-reassembled']['state']['separation'] == 0
for f in browser['fallback']:
    assert f['requestedEra'] == f['metrics']['era']
    assert f['images'][0]['loaded']

recordings = []
for name in ('motion-normal-speed', 'claw-normal-speed'):
    data = json.loads((OUT / (name + '.json')).read_text())
    assert data['complete'] and data['samples']
    assert not any(s['hidden'] for s in data['samples'])
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_entries',
        'format=duration,size:stream=codec_name,width,height,avg_frame_rate',
        '-of', 'json', str(OUT / (name + '.mp4'))]))
    recordings.append({'name': name, 'durationSeconds': data['durationSeconds'],
        'samples': len(data['samples']), 'hiddenSamples': 0,
        'failedDispatches': [e for e in data['events'] if e.get('error')],
        'observedStates': sorted({s['snapshot']['state'] for s in data['samples']}),
        'probe': probe})

invalid = {'advanced-open.png': 'inspection had not settled',
           'advanced-contact-head.png': 'fixed head camera clipped lowered head',
           **{f'fallback-{e}.png': 'captured during era transition' for e in ('maker','mechanic','builder')}}
paths = sorted(p for p in OUT.rglob('*') if p.is_file() and p.name != 'evidence-manifest.json')
sources = [ROOT / p for p in (
    'src/main.js','src/scene/presence-exhibit.js','src/scene/fallback.js',
    'scripts/record-alignment-v5-browser.js','scripts/record-alignment-v5-claw.js',
    'scripts/freeze-alignment-v5-browser.py')]
manifest = {
    'status': 'local bounded browser evidence; revision required artistically',
    'model': model, 'browserRecord': identity(OUT / 'browser-review.json'),
    'recordings': recordings, 'sourceFiles': [identity(p) for p in sources],
    'files': [dict(identity(p), reviewUse=(
        'rejected capture; retained for audit' if 'rejected' in str(p.relative_to(OUT))
        else invalid.get(p.name, 'evidence; interpret with receipt scope'))) for p in paths],
    'boundedChecks': ['served GLB SHA and bytes', 'all three era exploded/reassembled state values',
                      'all three current fallback images loaded', 'no hidden samples in recordings'],
    'limitations': [
        'Static poses used accelerated settling via the existing DEV step hook; recordings use the normal clock.',
        'The broad recording missed claw, reach and retreat dispatches when controls were unavailable. The separate claw recording fills claw motion only.',
        'Captures are not a complete all-pair collision, human acting, device, accessibility or T01-T18 assessment.',
        'Performance is a short rolling sample on Apple M4 Max, loopback, 856x648 canvas at DPR1, not sustained or physical-mobile certification.',
        'No new deployment, owner approval, full score or finished surfaces are established.',
    ],
}
(OUT / 'evidence-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(json.dumps({'model': model['sha256'], 'files': len(paths),
                  'recordings': recordings}, indent=2))
