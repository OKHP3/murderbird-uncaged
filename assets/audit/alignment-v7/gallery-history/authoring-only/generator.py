"""Create a local, write-once review page from verified V7 renders and receipts."""
from pathlib import Path
import hashlib
import html
import json
import os

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/audit/alignment-v7'
MODEL = ROOT / 'assets/models/uncaged-alignment-v7'
inventory = json.loads((MODEL / 'alignment-inventory.json').read_text())
renders = json.loads((OUT / 'neutral-views/authoring-views.json').read_text())
baseline = json.loads((ROOT / 'assets/audit/alignment-v7-v6-baseline/authoring-views.json').read_text())
assert not (OUT / 'index.html').exists(), 'Preserve existing review before regeneration'
records = {}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def register(row):
    path = ROOT / row['path']
    assert path.is_file() and digest(path) == row['sha256'], 'Evidence hash mismatch: ' + row['path']
    records[row['path']] = {'path': row['path'], 'sha256': row['sha256'], 'bytes': path.stat().st_size}
    return row


def url(path):
    return html.escape(os.path.relpath(ROOT / path, OUT), quote=True)


def figure(row, title, note=''):
    register(row)
    link = url(row['path'])
    return f'<figure><a href="{link}"><img loading="lazy" src="{link}" alt="{html.escape(title)}"></a><figcaption><b>{html.escape(title)}</b><p>{html.escape(note)}</p></figcaption></figure>'


for row in inventory['generatedFiles']:
    register(row)
glb = next(row for row in inventory['generatedFiles'] if row['path'].endswith('.glb'))
native = next(row for row in inventory['generatedFiles'] if row['path'].endswith('.blend'))
assert renders['native']['sha256'] == native['sha256']
assert renders['runtimeDerivative']['sha256'] == glb['sha256']
current = {(row['era'], row['view']): row for row in renders['views']}
sections = []
ref_rows = inventory['sourceReferences']['sources']
references = {row['id']: row for row in ref_rows}
sections.append('<section><h2>Controlling references</h2><p>July controls the head only. Candidate 03 guides the common body; Maker-clean and Mechanic guide their construction states. Perspective illustrations are qualitative references, not measured drawings.</p><div class="grid">' + ''.join(
    figure(row, row['id'], row.get('tier', 'Reference scope is recorded in the source packet.'))
    for row in ref_rows if row['id'] in {'candidate-03', 'maker-clean', 'mechanic'}) + '</div></section>')
july = register(references['july-head'])
july_url = url(july['path'])
head_pair = f'<figure><a href="{july_url}"><svg viewBox="510 20 500 490" role="img" aria-label="July reference, head-only display crop"><image href="{july_url}" width="1024" height="1536"/></svg></a><figcaption><b>July head selection</b><p>Head-only display crop; click for the unchanged original. Excluded body proportions are not imported.</p></figcaption></figure>'
sections.append('<section><h2>Head construction remains open</h2><p>The v7 head retains v6 exactly. Bill-root, brow and cheek construction still need refinement against the reference. The two views are approximate perspective comparisons, not camera-calibrated measurements.</p><div class="pair">' + head_pair + figure(current[('builder', 'head')], 'V7 inherited head · neutral') + '</div></section>')
comparisons = []
for before in baseline['views']:
    after = current[('builder', before['view'])]
    for key in ['camera', 'target', 'projection', 'orthoScale', 'resolution']:
        assert before[key] == after[key], 'Unmatched camera: ' + before['view']
    comparisons.append('<h3>' + html.escape(before['view']) + '</h3><div class="pair">' +
        figure(before, 'V6 — before') + figure(after, 'V7 — combined candidate') + '</div>')
sections.append('<section><h2>Same-camera before and after</h2><p>V7 transfers the reviewed limb guards and talons into V6. Head, body, mantle, controls and pivots are retained. The separate bill and toe-cover studies are not included.</p>' + ''.join(comparisons) + '</section>')
for era, label in [('maker', 'I · Maker'), ('mechanic', 'II · Mechanic'), ('builder', 'III · Advanced')]:
    sections.append(f'<section><h2>{label}</h2><p>Neutral authoring reconstruction. Era differences here come from component visibility; finished materials remain gated.</p><div class="grid">' + ''.join(
        figure(row, row['view']) for row in renders['views'] if row['era'] == era) + '</div></section>')
sections.append('<section><h2>Review boundaries</h2><p>This is a local correction candidate. Head construction, toe transitions and regional exterior fidelity remain open. No owner likeness acceptance or publication is implied.</p><ul><li><a href="../../../docs/alignment-v7-review.md">Candidate findings and check results</a></li><li><a href="../alignment-v6/index.html">Previous V6 evidence — applies to V6 only</a></li><li><a href="../../../docs/correction-v2-reference-packet.md">Reference decisions and scope</a></li></ul></section>')
css = 'body{margin:0;background:#151719;color:#e8e8e5;font:16px/1.5 system-ui,sans-serif}main{max-width:1240px;margin:auto;padding:28px}h1{font-size:40px}h2{margin-top:36px}p{max-width:80ch}a{color:#d8b978}code{overflow-wrap:anywhere}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.pair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}figure{margin:0;background:#202427;min-width:0}img,svg{width:100%;display:block}figcaption{padding:12px;overflow-wrap:anywhere}figcaption p{margin:.35em 0}section{border-top:1px solid #444;margin-top:30px;padding-top:6px}@media(max-width:650px){main{padding:16px}.grid,.pair{grid-template-columns:minmax(0,1fr)}h1{font-size:30px}}'
body = f'<header><p>Local review · not deployed</p><h1>MurderBird · Alignment V7</h1><p>Head-and-neck work combined with the reviewed regional limb correction. Neutral structure remains a proposal.</p><p>Model <code>{glb["sha256"]}</code></p><p><a href="{url(glb["path"])}">Runtime GLB</a> · <a href="{url(native["path"])}">Editable Blender source</a> · <a href="{url(str((MODEL / "alignment-inventory.json").relative_to(ROOT)))}">Construction inventory</a> · <a href="../../../">Open local exhibit</a></p></header>'
(OUT / 'index.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MurderBird V7 local review</title><style>' + css + '</style></head><body><main>' + body + ''.join(sections) + '</main></body></html>\n')
(OUT / 'gallery-manifest.json').write_text(json.dumps({
    'status': 'local review only; no artistic acceptance', 'modelSha256': glb['sha256'],
    'nativeSha256': native['sha256'], 'generatorSha256': digest(Path(__file__)),
    'htmlSha256': digest(OUT / 'index.html'), 'matchedPairs': len(comparisons),
    'renderCount': len(renders['views']), 'verifiedFiles': list(records.values()),
}, indent=2) + '\n')
print('Gallery written:', len(records), 'hash-verified files;', len(comparisons), 'matched pairs')
