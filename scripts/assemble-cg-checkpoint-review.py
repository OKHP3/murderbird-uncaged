"""Assemble a local fixed-camera CG checkpoint packet from actual receipts.

No rendering, source copies or overwrite. Both homes must be within the
owner's existing visual-technical-acceptance evidence tree.
"""
import argparse
import hashlib
import json
import os
import re
import struct
from pathlib import Path

HOME = Path.home() / 'OKH-Local/01_ChatGPT_Exports/murderbird-uncaged/evidence/visual-technical-acceptance'


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        while block := stream.read(8 * 1024 * 1024):
            digest.update(block)
    return digest.hexdigest()


def material_definitions(path):
    with path.open('rb') as stream:
        stream.seek(12)
        size, kind = struct.unpack('<II', stream.read(8))
        assert kind == 0x4e4f534a
        return {m['name']: m for m in json.loads(stream.read(size))['materials']}


def run(args):
    root, before = Path(args.root).resolve(), Path(args.before).resolve()
    assert root.is_relative_to(HOME.resolve()) and before.is_relative_to(HOME.resolve())
    assert root != before and root.is_dir() and before.is_dir()
    assert re.fullmatch(r'[a-z0-9-]+', args.parity_prefix)
    assert re.fullmatch(r'[a-z0-9-]+', args.native_folder)
    assert re.fullmatch(r'[a-z0-9-]+\.json', args.preservation)
    assert (root / args.preservation).is_file()
    candidate = (root / args.candidate).resolve()
    assert candidate.is_relative_to(root)
    read = lambda path: json.loads(path.read_text(encoding='utf-8'))
    rows = [read(p) for p in sorted(root.glob('*.json'))
            if re.fullmatch(r'(builder|maker|mechanic)-(before|after)-(head|full)-(neutral|exhibit)-\d+-(level|high|low)\.json', p.name)]
    assert len(rows) == 156 and len({r['evidence'] for r in rows}) == 156
    pairs = {}
    for row in rows:
        assert row['saved'] == 201 and row['captureMode'] == 'native viewport; viewer anchor; no emulation'
        path = (root / row['evidence']).resolve()
        assert path.parent == root and path.suffix == '.png'
        with path.open('rb') as stream:
            assert stream.read(8) == b'\x89PNG\r\n\x1a\n'
            stream.seek(16)
            assert list(struct.unpack('>II', stream.read(8))) == row['environment']['viewport']
        key = (row['era'], row['view'], row['light'], row['angle'], row['elevation'])
        pairs.setdefault(key, {})[row['version']] = row
    checks = []
    for key, pair in pairs.items():
        assert set(pair) == {'before', 'after'}
        a, b = pair['before'], pair['after']
        for field in ('camera', 'target', 'zoom', 'framing', 'lighting', 'environment', 'captureMode'):
            assert a[field] == b[field], (key, field)
        checks.append({'era': key[0], 'view': key[1], 'light': key[2], 'angle': key[3],
                       'elevation': key[4], 'status': 'PASS', 'before': a['evidence'], 'after': b['evidence'],
                       'triangles_before': a['triangles'], 'triangles_after': b['triangles']})
    assert len(checks) == 78
    parity = []
    material_rows = []
    for era in ('builder', 'maker', 'mechanic'):
        receipt = read(root / (args.parity_prefix + '-' + era) / 'checker-results.json')
        assert receipt['position_key_decimal_places'] == 5
        assert receipt['UV_absolute_tolerance'] == 2e-6
        assert receipt['normalized_normal_vector_L2_tolerance'] == 2e-5
        assert len(receipt['results']) == 1 and receipt['results'][0]['era'] == era
        actual = receipt['results'][0]
        for suffix, path_key, hash_key in (('.blend', 'native_path', 'native_sha256'), ('.glb', 'GLB_path', 'GLB_sha256')):
            path = (candidate / era / ('murderbird-recursive-' + era + suffix)).resolve()
            assert Path(actual[path_key]).resolve() == path and sha(path) == actual[hash_key]
        parity.extend(receipt['results'])
        filename = 'murderbird-recursive-' + era + '.glb'
        old = material_definitions(before / 'candidate' / era / filename)
        new = material_definitions(candidate / era / filename)
        assert old == new
        material_rows.append({'era': era, 'status': 'PASS', 'unchanged_definitions': len(old)})
    assert len(parity) == 3 and all(p['status'] == 'PASS' for p in parity)
    materials = [m for p in parity for m in p['material_checks']]
    summary = {'status': 'PASS - scoped attributes only', 'material_rows': len(materials),
               'position_key_decimal_places': 5, 'UV_absolute_tolerance': 2e-6,
               'normalized_normal_vector_L2_tolerance': 2e-5,
               'position_max_abs': max(m['position_max_abs'] for m in materials),
               'UV_max_abs': max(m['UV_max_abs'] for m in materials),
               'normal_vector_max_L2': max(m['normal_vector_max_L2'] for m in materials),
               'embedded_images': sum(len(p['embedded_images']) for p in parity),
               'identities': [{key: p[key] for key in ('era', 'native_path', 'native_sha256', 'GLB_path', 'GLB_sha256')} for p in parity],
               'limits': 'No lineage, shader/pixel, engineering, performance or owner likeness acceptance claim.'}
    relative = lambda path: Path(os.path.relpath(path, root)).as_posix()
    native = []
    for folder in ('builder', 'builder-exhibit'):
        a = read(before / 'native-after' / folder / 'render-receipt.json')
        b = read(root / args.native_folder / folder / 'render-receipt.json')
        assert len(a) == len(b) == 2
        for old, new in zip(a, b):
            for field in ('view', 'camera', 'lighting', 'resolution', 'samples'):
                assert old[field] == new[field], (folder, field)
            assert Path(old['image']).resolve().is_relative_to(before)
            assert Path(new['image']).resolve().is_relative_to(root)
            assert sha(Path(old['image'])) == old['sha256'] and sha(Path(new['image'])) == new['sha256']
            native.append({'view': old['view'], 'status': 'PASS', 'before': relative(Path(old['image'])),
                           'after': relative(Path(new['image'])), 'before_sha256': old['sha256'], 'after_sha256': new['sha256']})
    head = next(p for p in native if p['view'] == 'head-neutral')
    html = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>MurderBird tab and sliver review</title><style>body{background:#202622;color:#ede9db;font:17px system-ui;margin:24px}p{max-width:1100px}select{font:inherit;padding:8px;margin:4px}a{color:#ebc58d}.pair{display:grid;grid-template-columns:1fr 1fr;gap:15px}.pair img{width:100%}label{display:inline-block}pre{white-space:pre-wrap;font-size:13px}@media(max-width:850px){.pair{grid-template-columns:1fr}}</style><h1>MurderBird: one tab and sliver correction</h1><p>Before is the preserved358d review checkpoint. After reseats the inset optic lip, smooths its inner retainer fold and tucks upper bill-root tails. Stance, breast, toes and other nonselected gains remain protected. Source likeness and Jamie's acceptance remain open.</p><p><a href="acceptance-matrix.md">Acceptance matrix and remaining holds</a> · <a href="matched-view-check.json">78 matched camera/light pairs</a> · <a href="postflight-preservation.json">Saved-native preservation</a> · <a href="normal-parity-summary.json">Strict export data</a></p><label>Era <select id="era"><option value="builder">Advanced</option><option>maker</option><option>mechanic</option></select></label><label>View <select id="view"><option value="head">Head close-up</option><option value="full">Whole bird</option></select></label><label>Light <select id="light"><option>neutral</option><option>exhibit</option></select></label><label>Angle <select id="angle"></select></label><label>Elevation <select id="elevation"><option value="0">Default</option><option value="0.3">Elevated</option><option value="-0.3">Low</option></select></label><p>Identical camera, target, zoom, frame, light and browser environment. Native-size model captures include their own camera receipts; click for full size.</p><div class="pair"><section><h2>Before:358d checkpoint</h2><a id="before-link"><img id="before" alt="Preserved checkpoint at the selected camera"></a></section><section><h2>After:tab/sliver proposal</h2><a id="after-link"><img id="after" alt="Proposed correction at the same camera"></a></section></div><pre id="metadata"></pre><h2>Matched native Builder views</h2><p>CPU Cycles4samples,800-pixel diagnostics. Native/browser lighting differs; their pixels are not equivalent.</p><div class="pair"><section><h3>Native head before</h3><img src="__NATIVE_BEFORE__" alt="Native head before"></section><section><h3>Native head after</h3><img src="__NATIVE_AFTER__" alt="Native head after"></section></div><p>__NATIVE_LINKS__</p><script>const rows=__ROWS__;const $=id=>document.getElementById(id);function update(change=false){let full=$('view').value==='full';let angles=full?[0,45,90,135,180,225,270,315]:[0,90,180],previous=$('angle').value;if(change||!$('angle').options.length){$('angle').replaceChildren(...angles.map(v=>new Option(v+'°',v)));if(angles.includes(Number(previous)))$('angle').value=previous;}if(!full||$('angle').value!=='0')$('elevation').value='0';$('elevation').disabled=!full||$('angle').value!=='0';let found=rows.filter(r=>r.era===$('era').value&&r.view===$('view').value&&r.light===$('light').value&&r.angle===Number($('angle').value)&&r.elevation===Number($('elevation').value));for(let r of found){$(r.version).src=r.evidence;$(r.version+'-link').href=r.evidence;}$('metadata').textContent=JSON.stringify(found,null,2);}for(let id of ['era','light','angle','elevation'])$(id).onchange=()=>update();$('view').onchange=()=>update(true);update(true);</script></html>'''
    html = html.replace('__ROWS__', json.dumps(rows)).replace('__NATIVE_BEFORE__', head['before']).replace('__NATIVE_AFTER__', head['after'])
    html = html.replace('__NATIVE_LINKS__', ' · '.join(f'<a href="{p[version]}">{p["view"]} {version}</a>' for p in native for version in ('before', 'after')))
    html = html.replace('href="postflight-preservation.json"', 'href="' + args.preservation + '"')
    outputs = {'matched-browser-views.json': rows,
               'matched-view-check.json': {'status': 'PASS', 'captures': 156, 'pairs': 78, 'results': checks,
                   'limits': 'Camera/data/dimensions only; visual inspection must still reject tiling, missing content and artifacts. No acceptance inference.'},
               'normal-parity-summary.json': summary,
               'material-json-comparison.json': {'results': material_rows, 'limits': 'Exact exported material JSON, not rendered appearance parity.'},
               'native-matched-view-check.json': {'status': 'PASS', 'pairs': 4, 'results': native}}
    assert not any((root / name).exists() for name in [*outputs, 'comparison-index.html'])
    for name, value in outputs.items():
        with (root / name).open('x', encoding='utf-8') as stream:
            json.dump(value, stream, indent=2)
    with (root / 'comparison-index.html').open('x', encoding='utf-8') as stream:
        stream.write(html)
    print(json.dumps({'captures': 156, 'matched_pairs': 78, 'native_pairs': 4, 'material_rows': len(materials)}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True)
    parser.add_argument('--before', required=True)
    parser.add_argument('--candidate', default='candidate')
    parser.add_argument('--parity-prefix', default='parity')
    parser.add_argument('--native-folder', default='native-after')
    parser.add_argument('--preservation', default='postflight-preservation.json')
    run(parser.parse_args())
