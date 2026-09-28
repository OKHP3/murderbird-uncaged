"""Add frozen browser evidence without replacing the first V8 review record."""
from pathlib import Path
import hashlib
import html
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/audit/alignment-v8'
BROWSER = OUT / 'browser-c8c30cc46059'


def artifact(path):
    return {'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    page = OUT / 'index.html'
    manifest = OUT / 'gallery-manifest.json'
    prior = json.loads(manifest.read_text())
    assert artifact(page) == prior['html'], 'Review page changed since its receipt'
    history = OUT / 'authoring-only-gallery'
    assert not history.exists(), 'Preserve the previous gallery snapshot'
    telemetry = json.loads((BROWSER / 'motion-envelope.json').read_text())
    assert telemetry['declaredSha256'] == prior['modelSha256']
    assert telemetry['sequenceComplete'] and telemetry['complete']
    for file in ('motion-envelope.mp4', 'loaded-model.json', 'static-captures.json', 'fallback-captures.json'):
        assert (BROWSER / file).is_file()
    history.mkdir()
    shutil.copy2(page, history / 'index.html')
    shutil.copy2(manifest, history / 'gallery-manifest.json')
    shutil.copy2(__file__, OUT / 'executed-browser-gallery-extension.py')
    movie = 'browser-c8c30cc46059/motion-envelope.mp4'
    chapters = [('Maker controls', 0), ('Mechanic movement', 24), ('Advanced actions', 48),
                ('Maker inspection', 64.4), ('Mechanic inspection', 71.9), ('Advanced inspection', 79.3)]
    section = '''<section id="motion"><h2>The combined model in motion</h2>
<p>Actual V8 browser recording: Maker controls, Mechanic stepping, Advanced jump, short shield thrust, claw action and strike, followed by opening, separation and reassembly in all three eras. Normal browser time; no accelerated stepping.</p>
<video id="motion-video" controls playsinline preload="metadata" src="''' + movie + '''" aria-label="V8 motion and inspection recording"></video>
<p>Choose a section: ''' + ' · '.join(f'<button type="button" data-seek="{time}">{label}</button>' for label, time in chapters) + '''</p>
<p>The recording combines neutral and exhibit lighting. The canvas is 856 × 648; this is a bounded desktop demonstration, not a sustained performance benchmark or a physical simulation.</p>
<p><a href="browser-c8c30cc46059/loaded-model.json">Verified model loaded by browser</a> · <a href="browser-c8c30cc46059/motion-envelope.json">Recorded events and measurements</a> · <a href="independent-visual-review.md">Independent likeness findings</a></p></section>'''
    rows = json.loads((BROWSER / 'static-captures.json').read_text())['images']
    sections = [section]
    for era, label in [('maker', 'I · Maker'), ('mechanic', 'II · Mechanic'), ('builder', 'III · Advanced')]:
        figures = []
        for pose in ('closed', 'inspection-0', 'inspection-50', 'inspection-100', 'reassembled'):
            filename = f'{era}-{pose}.png'
            assert (BROWSER / filename).is_file(), filename
            title = {'closed':'Closed', 'inspection-0':'Open panels', 'inspection-50':'Half separated',
                     'inspection-100':'Fully separated', 'reassembled':'Reassembled'}[pose]
            figures.append(f'<figure><a href="browser-c8c30cc46059/{filename}"><img loading="lazy" src="browser-c8c30cc46059/{filename}" alt="{html.escape(label + ': ' + title)}"></a><figcaption>{title}</figcaption></figure>')
        sections.append(f'<section><h2>{label} · browser inspection</h2><p>Actual WebGL stills. Development stepping settled these static poses; the movie above provides normal-time motion evidence. Opening still exposes simplified internal construction.</p><div class="grid">' + ''.join(figures) + '</div></section>')
    sections.append('''<section><h2>Still requires correction</h2><p>The neck-to-breast transition remains too open and angular; the shoulder coverings read as separate side pods; the toes remain sparsely covered. Head construction is cleaner but still differs from the selected reference. Automated checks do not resolve these appearance gaps.</p><p>Maker and Mechanic neutral authoring views are currently pixel-identical. Their browser mechanisms differ, but distinct exterior history is still unfinished. These fixed fallback previews do not include the runtime mechanisms.</p></section>''')
    source = page.read_text()
    assert source.count('</header>') == 1
    source = source.replace('</header>', '</header>' + ''.join(sections), 1)
    source = source.replace('Neck inclusion is recorded in the transfer contract.', 'The existing V7 neck is retained; the tapered neck study was held after additional contact conflicts.')
    source = source.replace('</main></body>', '''</main><script>document.querySelectorAll('[data-seek]').forEach(button=>button.addEventListener('click',()=>{const video=document.getElementById('motion-video');video.currentTime=Number(button.dataset.seek);video.play();}));</script></body>''')
    page.write_text(source)
    evidence = [artifact(path) for path in sorted(BROWSER.iterdir()) if path.is_file() and path.suffix in ('.json','.png','.mp4','.webm','.js')]
    prior.update({'status':'local neutral candidate; normal-clock browser demonstration; likeness remains revision required',
                  'html':artifact(page), 'previousGallery':artifact(history / 'gallery-manifest.json'),
                  'browserEvidence': evidence, 'browserStaticCaptureCount': len(rows),
                  'extensionScript':artifact(OUT / 'executed-browser-gallery-extension.py')})
    manifest.write_text(json.dumps(prior, indent=2) + '\n')
    print('Extended V8 review with browser movie and 15 inspection stills; first gallery preserved.')


if __name__ == '__main__':
    main()
