"""Finish the local neutral V8 package after composition and matched rendering.

Preserves the original composition receipt before adding fallback derivatives.
Existing previews or gallery are never overwritten. No publishing occurs.
"""
from pathlib import Path
import hashlib
import html
import json
import os
import shutil

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / 'assets/models/uncaged-alignment-v8'
OUT = ROOT / 'assets/audit/alignment-v8'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': digest(path), 'bytes': path.stat().st_size}


def main():
    inventory_path = MODEL / 'alignment-inventory.json'
    inventory = json.loads(inventory_path.read_text())
    source = json.loads((ROOT / 'assets/models/uncaged-alignment-v7/alignment-inventory.json').read_text())
    renders_path = OUT / 'neutral-views/authoring-views.json'
    renders = json.loads(renders_path.read_text())
    baseline_path = ROOT / 'assets/audit/alignment-v7/neutral-views/authoring-views.json'
    baseline = json.loads(baseline_path.read_text())
    native = next(row for row in inventory['generatedFiles'] if row['path'].endswith('.blend'))
    runtime = next(row for row in inventory['generatedFiles'] if row['path'].endswith('.glb'))
    assert native['sha256'] == renders['native']['sha256']
    assert runtime['sha256'] == renders['runtimeDerivative']['sha256']
    for row in [*inventory['generatedFiles'], *renders['views'], *baseline['views']]:
        assert digest(ROOT / row['path']) == row['sha256'], 'Changed evidence: ' + row['path']
    assert not (OUT / 'index.html').exists()
    assert not (OUT / 'composition-inventory.json').exists()
    for era in ('maker', 'mechanic', 'builder'):
        assert not (MODEL / f'{era}-preview.png').exists()
    shutil.copy2(inventory_path, OUT / 'composition-inventory.json')
    shutil.copy2(__file__, OUT / 'executed-review-builder.py')
    current = {(row['era'], row['view']): row for row in renders['views']}
    before = {(row['era'], row['view']): row for row in baseline['views']}
    previews = []
    for era in ('maker', 'mechanic', 'builder'):
        row = current[(era, 'left-three-quarter')]
        target = MODEL / f'{era}-preview.png'
        shutil.copy2(ROOT / row['path'], target)
        previews.append({**artifact(target), 'from': row['path'], 'view': 'left-three-quarter',
                         'status': 'fixed neutral authoring render; procedural runtime mechanisms are not included'})
    inventory['status'] = 'neutral geometry proposal awaiting owner review'
    inventory['generatedFiles'] += [{key: row[key] for key in ('path', 'sha256', 'bytes')} for row in previews]
    inventory['fallbackPreviews'] = previews
    inventory['sourceReferences'] = source['sourceReferences']
    for key in ('conventions', 'jointContract', 'billContact', 'billContactSpace', 'controls'):
        inventory[key] = source[key]
    inventory['previousCandidate'] = {'inventory': artifact(ROOT / 'assets/models/uncaged-alignment-v7/alignment-inventory.json'),
                                      'runtime': next(row for row in source['generatedFiles'] if row['path'].endswith('.glb'))}
    inventory['originalCompositionReceipt'] = artifact(OUT / 'composition-inventory.json')
    inventory['authoringViewReceipt'] = artifact(renders_path)
    inventory['reviewBuilder'] = artifact(OUT / 'executed-review-builder.py')
    inventory_path.write_text(json.dumps(inventory, indent=2) + '\n')
    records = {}

    def register(row):
        p = ROOT / row['path']
        assert digest(p) == row['sha256'], row['path']
        records[row['path']] = artifact(p)
        return row

    def url(p):
        return html.escape(os.path.relpath(ROOT / p, OUT), quote=True)

    def figure(row, title, note=''):
        register(row)
        link = url(row['path'])
        return f'<figure><a href="{link}"><img loading="lazy" src="{link}" alt="{html.escape(title)}"></a><figcaption><b>{html.escape(title)}</b><p>{html.escape(note)}</p></figcaption></figure>'

    for row in inventory['generatedFiles']:
        register(row)
    references = {row['id']: row for row in inventory['sourceReferences']['sources']}
    sections = []
    sections.append('<section><h2>The combined neutral bird</h2><p>The selected head, shoulder and digit studies are joined in one editable source. Neck inclusion is recorded in the transfer contract. These are structural proposals; the head and regional plate hierarchy still need artistic judgment.</p><div class="grid">' + ''.join(figure(current[(era, 'three-quarter')], label) for era, label in [('maker','I · Maker'),('mechanic','II · Mechanic'),('builder','III · Advanced')]) + '</div></section>')
    sections.append('<section><h2>Controlling appearance references</h2><p>Candidate 03 controls the common-body direction; Maker-clean and Mechanic guide their construction states. The July image controls the head only. These perspective illustrations do not establish exact engineering dimensions.</p><div class="grid">' + ''.join(figure(references[key], label) for key, label in [('candidate-03','Common body · candidate 03'),('maker-clean','Maker · newly fabricated'),('mechanic','Mechanic · inherited and repaired')]) + '</div></section>')
    july = register(references['july-head'])
    sections.append('<section><h2>Head identity remains under review</h2><p>Rebuilt cheek and cere plates remove the prior floating/folded impression; the bill root is broader. The smooth bill, broad orbital field and thin upper brow still differ from the selected construction.</p><div class="pair"><figure><a href="' + url(july['path']) + '"><svg viewBox="510 20 500 490" role="img" aria-label="July head-only reference crop"><image href="' + url(july['path']) + '" width="1024" height="1536"/></svg></a><figcaption>July selection · head only</figcaption></figure>' + figure(current[('builder','head')], 'Combined V8 head · neutral') + '</div></section>')
    matched = []
    for view in ('front','side-right','side-left','rear','three-quarter','head','neck','left-shoulder','feet','feet-side'):
        old, new = before[('builder',view)], current[('builder',view)]
        for key in ('camera','target','projection','orthoScale','resolution'):
            assert old[key] == new[key], f'Unmatched {view}/{key}'
        matched.append(view)
        sections.append('<section><h2>' + html.escape(view.replace('-',' ').title()) + '</h2><div class="pair">' + figure(old,'V7 · before') + figure(new,'V8 · combined correction') + '</div></section>')
    for era, label in [('maker','I · Maker'),('mechanic','II · Mechanic'),('builder','III · Advanced')]:
        sections.append('<section><h2>' + label + ' · all neutral views</h2><p>Component visibility follows the era inventory. These authoring views exclude runtime control rods, transmissions and support rigs. The actual browser is reviewed separately.</p><div class="grid">' + ''.join(figure(row,row['view'].replace('-',' ').title()) for row in renders['views'] if row['era']==era) + '</div></section>')
    sections.append('<section><h2>Review status</h2><p>Local correction candidate. Automated evidence describes bounded technical checks; it does not establish likeness acceptance, physical simulation or deployment.</p><p><a href="../../../docs/alignment-v8-review.md">Findings and check coverage</a> · <a href="../neutral-regional-studies/index.html">Individual studies and isolated claw clip</a> · <a href="../alignment-v7/index.html">Preserved V7 review</a></p></section>')
    css = 'body{margin:0;background:#151719;color:#e8e8e5;font:16px/1.5 system-ui,sans-serif}main{max-width:1240px;margin:auto;padding:28px}h1{font-size:40px}h2{margin-top:30px}p{max-width:80ch}a{color:#d8b978}code{overflow-wrap:anywhere}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.pair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}figure{margin:0;background:#202427;min-width:0}img,svg,video{display:block;width:100%}figcaption{padding:12px;overflow-wrap:anywhere}figcaption p{margin:.35em 0}section{border-top:1px solid #444;margin-top:30px;padding-top:6px}@media(max-width:650px){main{padding:16px}.grid,.pair{grid-template-columns:minmax(0,1fr)}h1{font-size:30px}}'
    header = '<header><p>Local review · owner likeness decision pending</p><h1>MurderBird · Alignment V8</h1><p>One neutral model combining the reviewed regional corrections.</p><p>Model <code>' + runtime['sha256'] + '</code></p><p><a href="' + url(runtime['path']) + '">Runtime model</a> · <a href="' + url(native['path']) + '">Editable Blender source</a> · <a href="' + url(str(inventory_path.relative_to(ROOT))) + '">Construction inventory</a> · <a href="../../../">Local exhibit</a></p></header>'
    page = OUT / 'index.html'
    page.write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MurderBird V8 local review</title><style>' + css + '</style></head><body><main>' + header + ''.join(sections) + '</main></body></html>\n')
    (OUT / 'gallery-manifest.json').write_text(json.dumps({'status':'local authoring review; browser/owner review separate',
        'nativeSha256':native['sha256'],'modelSha256':runtime['sha256'],'html':artifact(page),
        'inventory':artifact(inventory_path),'matchedViews':matched,'renderCount':len(renders['views']),
        'verifiedFiles':list(records.values())}, indent=2) + '\n')
    print('Prepared neutral V8 review:',len(renders['views']),'renders;',len(matched),'matched comparisons')


if __name__ == '__main__':
    main()
