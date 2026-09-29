"""Build a local appearance assessment; never modifies source assets or runtime."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from html import escape
from pathlib import Path
from urllib.request import urlopen
import io
import json
import shutil
import struct
import subprocess

from PIL import Image

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
PARALLEL = Path('/Users/okh/.codex/worktrees/uncaged-production/murderbird-uncaged')
EVIDENCE = OUT / 'evidence'
EVIDENCE.mkdir(exist_ok=True)
def digest(path):
    return sha256(path.read_bytes()).hexdigest()

selected = {
    'master': 'assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png',
    'july': 'context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png',
    'maker': 'assets/img/library/murderbird-unified-maker-clean-candidate-2026-09-06.png',
    'mechanic': 'assets/img/library/murderbird-unified-mechanic-candidate-2026-09-06.png',
    'v1': 'assets/audit/exterior-v1/builder-authoring-neutral.png',
    'head': 'assets/audit/exterior-v1/builder-head-closeup.png',
    'feet': 'assets/audit/exterior-v1/builder-feet-closeup.png',
    'breast': 'assets/audit/exterior-v1/builder-breast-closeup.png',
    'neck': 'assets/audit/exterior-v1/builder-neck-closeup.png',
}
sources = []
for key, relative in selected.items():
    p = ROOT / relative
    with Image.open(p) as im:
        size = list(im.size)
    sources.append({'key': key, 'path': relative, 'sha256': digest(p), 'bytes': p.stat().st_size, 'dimensions': size})
parallel_revision = subprocess.check_output(['git', '-C', str(PARALLEL), 'rev-parse', 'HEAD'], text=True).strip()
parallel_copies = []
for key, filename in [('v2','builder-reference-perspective.png'), ('v2head','neutral-head.png'), ('v2feet','neutral-feet.png')]:
    source = PARALLEL / 'assets/audit/neutral-v2' / filename
    target = EVIDENCE / ('neutral-v2-' + filename)
    before = digest(source)
    shutil.copy2(source, target)
    assert digest(source) == digest(target) == before
    parallel_copies.append({'key': key, 'source': str(source), 'sourceRevisionObserved': parallel_revision,
                           'output': str(target.relative_to(ROOT)), 'sha256': before, 'transformation': 'byte-for-byte copy'})

model = ROOT / 'assets/models/uncaged-exterior-v1/murderbird-exterior-v1.glb'
binary = model.read_bytes()
json_length = struct.unpack_from('<I', binary, 12)[0]
gltf = json.loads(binary[20:20+json_length])
bin_start = 20 + json_length + 8
triangles = sum(gltf['accessors'][p['indices']]['count']//3 for m in gltf['meshes'] for p in m['primitives'])
images = []
for item in gltf.get('images', []):
    view = gltf['bufferViews'][item['bufferView']]
    start = bin_start + view.get('byteOffset', 0)
    with Image.open(io.BytesIO(binary[start:start+view['byteLength']])) as im:
        images.append({'name': item.get('name'), 'dimensions': list(im.size)})
technical = {'model': str(model.relative_to(ROOT)), 'sha256': digest(model), 'bytes': len(binary),
             'trianglesAllVariants': triangles, 'meshes': len(gltf['meshes']), 'materials': len(gltf['materials']),
             'images': images, 'materialsWithOcclusionTexture': sum('occlusionTexture' in m for m in gltf['materials'])}
manifest = json.loads((ROOT / 'assets/review/exterior-v1-publication.json').read_text())
assert technical['sha256'] == manifest['model']['sha256'] == '3ec668b0b9bbaf1cb546ec2e04b09030c5f45b0f0893adc5b7fe5aa57baacdc5'
assert technical['bytes'] == manifest['model']['bytes']
public_root = 'https://okhp3.github.io/murderbird-uncaged/'
def verify_remote(item):
    url = public_root + item['output']
    with urlopen(url, timeout=30) as response:
        data = response.read()
        status = response.status
    result = {'url': url, 'source': item['source'], 'status': status, 'bytes': len(data), 'sha256': sha256(data).hexdigest()}
    result['matchesPublicationManifest'] = result['sha256'] == item['sha256'] and len(data) == item['bytes']
    assert result['matchesPublicationManifest'], url
    return result
public_selection = [item for item in manifest['media'] if item['source'] in selected.values()]
assert len(public_selection) == len(selected) == 9
assert {item['source'] for item in public_selection} == set(selected.values())
for item in public_selection:
    local = ROOT / item['source']
    assert digest(local) == item['sha256'] and local.stat().st_size == item['bytes'], item['source']
with ThreadPoolExecutor(max_workers=4) as pool:
    public_checks = list(pool.map(verify_remote, public_selection))
with urlopen(public_root+'review/', timeout=30) as response:
    gallery = response.read()
    gallery_status = response.status
assert b'3ec668b0b9bbaf1cb546ec2e04b09030c5f45b0f0893adc5b7fe5aa57baacdc5' in gallery
code_paths = ['scripts/build-uncaged-exterior-v1.py','scripts/exterior-body-regions.py','scripts/exterior-head-neck.py',
              'src/scene/presence-exhibit.js','docs/creative-authority.md','docs/exterior-surface-pipeline.md',
              'assets/review/exterior-v1-publication.json']
receipt = {'retrievedUtc': datetime.now(timezone.utc).isoformat(),
           'scope': 'Appearance assessment; no model edits, motion approval or publication',
           'mainRevision': subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),
           'sourceImages': sources, 'parallelEvidenceCopies': parallel_copies, 'glbInspection': technical,
           'liveGallery': {'url':public_root+'review/','httpStatus':gallery_status,'bytes':len(gallery),'sha256':sha256(gallery).hexdigest()},
           'liveMediaChecks':public_checks,
           'codeAndAuthority': [{'path':p,'sha256':digest(ROOT/p)} for p in code_paths],
           'videoManifest': 'video-evidence/video-evidence-manifest.json',
           'rights': 'MurderBird creative material all rights reserved under NOTICE.md; local evidence derivatives only'}
(OUT/'evidence.json').write_text(json.dumps(receipt, indent=2)+'\n')
urls = {key:'../../'+p for key,p in selected.items()}
urls.update({item['key']: str(Path(item['output']).relative_to(OUT.relative_to(ROOT))) for item in parallel_copies})
def figure(key, title, caption, focus=None):
    src = urls[key]
    if focus:
        media = f'<div class="crop" style="--w:{focus[0]}%;--x:{focus[1]}%;--y:{focus[2]}%"><img src="{src}" alt="{escape(title)}"></div>'
    else:
        media = f'<img class="full" src="{src}" alt="{escape(title)}">'
    return f'<figure><a class="picture" href="{src}" target="_blank" rel="noopener" aria-label="Open full image: {escape(title)}">{media}</a><figcaption><strong>{escape(title)}</strong><p>{escape(caption)}</p></figcaption></figure>'

body_comparison = ''.join([
    figure('master','Selected visual target','Candidate 03: visible body identity. Unseen construction remains a proposal.',(165,-62,-4)),
    figure('v1','Published exterior v1','Broad simple forms, separate wing bulges and exposed leg cylinders.'),
    figure('v2','Parallel neutral v2','Better coverage and taper. Clay study; repeated plates and sparse limbs remain.')])
head_comparison = ''.join([
    figure('july','Selected July head','Head only: deep bill, shaped cheek, recessed optic and swept crown.',(177,-72,-1)),
    figure('head','Published head','Helmet, wedge, button optic and pipe-like jaw dominate.',(250,-108,-37)),
    figure('v2head','Newer clay head','Improved hook and coverage; large cheek void and generic plate rhythm persist.',(130,-26,-30))])
detail_comparison = ''.join([
    figure('master','Reference foot and leg language','Nested joint surrounds, segmented toes and dark talons. This is visible design evidence, not measured anatomy.',(250,-105,-48)),
    figure('feet','Published feet','Smooth members and separate toe-top plates expose the construction primitives.'),
    figure('v2feet','Newer clay feet','More shaped toes and hooks; limb casing still needs individual design.')])
era_comparison = figure('maker','Maker: fabrication','Use its exterior hierarchy; the current direction limits age and excludes water deposits.') + figure('mechanic','Mechanic: inherited history','Retain the plated creature and add local repairs. Historical video body/wing cues are not all current authority.')
html = '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MurderBird · Appearance fidelity assessment</title>
<style>
:root{color-scheme:dark;--bg:#121615;--panel:#1d2421;--ink:#f1efe6;--muted:#b7bdb3;--accent:#e1b77a;--line:#3d4740}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,sans-serif}main{max-width:1510px;padding:42px 4vw 80px;margin:auto}header{max-width:1000px}h1{font-size:clamp(34px,4.2vw,68px);line-height:1.08;letter-spacing:-.035em;margin:14px 0 24px}h2{font-size:30px;line-height:1.2;margin:0 0 10px}h3{color:var(--accent);margin:0 0 8px}p{margin:0 0 18px}.eyebrow{font-size:12px;letter-spacing:.12em;color:var(--accent);text-transform:uppercase}.lede{font-size:21px;color:#d6ddd3}a{color:var(--accent);text-underline-offset:4px}nav{display:flex;flex-wrap:wrap;gap:12px 24px;border-block:1px solid var(--line);padding:18px 0;margin:32px 0}section{padding-top:34px;margin-top:18px;border-top:1px solid var(--line);scroll-margin-top:18px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-top:24px}.two{grid-template-columns:repeat(2,minmax(0,1fr))}figure{margin:0;background:var(--panel);border:1px solid var(--line);min-width:0}.picture{display:block;background:#303633}.full{display:block;width:100%;height:450px;object-fit:contain}.crop{height:450px;position:relative;overflow:hidden}.crop img{position:absolute;max-width:none;width:var(--w);left:var(--x);top:var(--y)}figcaption{padding:16px}figcaption strong{font-size:18px}figcaption p{font-size:14px;color:var(--muted);margin:8px 0 0}.note{font-size:14px;color:var(--muted);max-width:1000px}.callout{padding:24px;border-left:4px solid var(--accent);background:var(--panel);margin:24px 0}.facts{display:flex;flex-wrap:wrap;gap:18px 42px;padding:20px 0}.facts strong{display:block;font-size:28px;color:var(--accent)}.facts span{font-size:13px;color:var(--muted)}.findings article{padding:22px;background:var(--panel);border-top:2px solid var(--line)}.findings p{margin:0;color:var(--muted)}.video img{display:block;width:100%;height:auto}.steps{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.step{padding:20px;background:var(--panel)}.step b{color:var(--accent);display:block}.step p{margin:8px 0 0;color:var(--muted)}summary{cursor:pointer;color:var(--accent);padding:14px 0}details p{color:var(--muted)}.controls{display:flex;gap:8px;align-items:center;flex-wrap:wrap}button{background:var(--panel);color:var(--ink);border:1px solid var(--line);padding:9px 16px;font:inherit;cursor:pointer}button[aria-pressed=true]{border-color:var(--accent);color:var(--accent)}a:focus-visible,button:focus-visible,summary:focus-visible{outline:3px solid var(--accent);outline-offset:4px}.grayscale .picture img{filter:grayscale(1)}footer{margin-top:40px;color:var(--muted);font-size:13px}code{overflow-wrap:anywhere}li{margin:8px 0}@media(max-width:900px){.grid,.steps{grid-template-columns:1fr}.two{grid-template-columns:1fr}.full,.crop{height:480px}.crop{max-width:520px;margin:auto}main{padding:24px 20px 50px}}@media(max-width:450px){.full,.crop{height:370px}}@media print{body{background:white;color:black}.grid,.steps{grid-template-columns:repeat(3,1fr)}.full,.crop{height:300px}section{break-inside:avoid}nav,.controls{display:none}}
</style></head><body><main>
<header><div class="eyebrow">Appearance study · 27 September 2026 · Local assessment</div><h1>The frame is there.<br>The creature is not yet convincing.</h1><p class="lede">The gap is authored form, layered construction and material depth. The pictures describe a complete armored creature; the published model still describes an assembly of simplified parts.</p><p class="note">This packet assesses appearance. It does not modify the model or approve anatomy, movement or final art. The parallel neutral study is shown separately from the published exterior.</p></header>
<nav aria-label="Assessment sections"><a href="#body">Whole bird</a><a href="#head">Head identity</a><a href="#feet">Legs &amp; feet</a><a href="#surface">Surface diagnosis</a><a href="#video">Video evidence</a><a href="#production">Production direction</a><a href="../../docs/appearance-fidelity-assessment-2026-09-27.md">Full assessment ↗</a></nav>
<div class="controls" aria-label="Image display"><span>Compare values:</span><button type="button" id="color" aria-pressed="true">Source color</button><button type="button" id="gray" aria-pressed="false">Grayscale inspection</button></div>
<p class="note">Images are evidence, not new proposed artwork. Some source panels use a display crop; click any panel for the full original. Cameras and perspective are not metrically aligned.</p>
<section id="body"><h2>01 · Give the exterior a coherent body</h2><p>Match the head–neck–breast flow and the compact folded mantle before adding finer texture. More bulk everywhere would be the wrong correction.</p><div class="grid">''' + body_comparison + '''</div></section>
<section id="head"><h2>02 · The face has to carry the identity</h2><p>The bill root, brow, cheek, optic recess and crown are a connected design. An orange disk and a hooked bill do not establish the likeness by themselves.</p><div class="grid">''' + head_comparison + '''</div><div class="callout"><strong>First production proof: one Advanced head, neck and shoulder.</strong><br>Explicitly shaped control meshes, regional plate boundaries and a small finished material sample. Prove this view in clay and neutral light before repeating it across the bird.</div></section>
<section id="feet"><h2>03 · Exposed machinery still needs a finished exterior</h2><p>The reference has open mechanical legs. The missing work is shaped casing, nested fittings, joint transitions and talon construction—not covering every opening.</p><div class="grid">''' + detail_comparison + '''</div></section>
<section id="surface"><h2>04 · More pixels cannot author the missing detail</h2><div class="facts"><div><strong>63,815</strong><span>triangles in the Advanced export</span></div><div><strong>7 × 1024²</strong><span>embedded maps in the combined model</span></div><div><strong>256²</strong><span>reused tile per region / role</span></div><div><strong>0</strong><span>exported occlusion-texture inputs</span></div></div><p class="note">Direct file inspection. The combined three-era geometry contains 187,957 triangles. Missing baked occlusion does not mean rendered shadows are absent.</p>
<div class="grid findings"><article><h3>Shape first</h3><p>Primitive chest, jaw and limb forms survive both authoring and browser renders. Shape the hero surfaces and preserve meaningful openings.</p></article><article><h3>Different plate families</h3><p>Crown blades, throat courses, breast panels and folded-wing plates need distinct size, sweep and overlap. One repeated scallop cannot describe the entire bird.</p></article><article><h3>Actual surface history</h3><p>Current relief and patina follow reusable UV tiles. Author wear, cavity and roughness fields that correspond to real parts, seams and service history.</p></article></div>
<div class="grid two">''' + era_comparison + '''</div><p class="note">Maker → Mechanic → Advanced should preserve one inherited creature. Early optics stay dark. The new clay study is not judged as a completed material pass.</p></section>
<section id="video"><h2>05 · The video already shows the missing exterior language</h2><p>Six timestamped samples from each clip. Full decodes passed; these samples establish appearance evidence, not continuous motion acceptance.</p>
<figure class="video"><a href="video-evidence/murderbird-first-choice-controlled-pilot-03-contact-sheet.jpg" target="_blank" rel="noopener"><img src="video-evidence/murderbird-first-choice-controlled-pilot-03-contact-sheet.jpg" alt="Six First Choice pilot 03 frames at 0, 1.5, 2.333, 3.333, 5.5 and 7.958 seconds"></a><figcaption><strong>Controlled First Choice pilot 03 · 1280 × 720 source</strong><p>Layered breast, curved plated neck, covered shoulder and framed leg mechanisms. This is the exact silent clip accepted for the story page; it does not approve a 3D rig or attack animation.</p></figcaption></figure>
<details><summary>Historical Maker, Mechanic and Heart samples</summary><p>These clips remain held/rejected for revised-film continuity. Their surface language is contextual. Heart's power-unit framing changes across the sampled sequence, so it cannot establish fixed internal topology.</p>'''
for slug, title in [('maker','Legacy Maker'),('mechanic','Legacy Mechanic'),('heart','Legacy Heart')]:
    path=f'video-evidence/murderbird-{slug}-legacy-original-contact-sheet.jpg'
    html += f'<figure class="video"><a href="{path}" target="_blank" rel="noopener"><img loading="lazy" src="{path}" alt="{title} six timestamped frames"></a><figcaption><strong>{title} · contextual appearance evidence</strong></figcaption></figure>'
html += '''</details><p><a href="video-evidence/video-evidence-manifest.json">Exact clip hashes, timestamps, status and limits ↗</a></p></section>
<section id="production"><h2>06 · Build quality once, then extend it</h2><div class="steps"><div class="step"><b>1 / Lock the references</b><p>Name the source for each visible feature. Mark unseen construction as proposed.</p></div><div class="step"><b>2 / Prove the hero exterior</b><p>Head, neck and shoulder in a new editable version. Pass likeness in clay first.</p></div><div class="step"><b>3 / Complete the shell</b><p>Author distinct regional plate families around the agreed structural envelope.</p></div><div class="step"><b>4 / Bake and finish</b><p>Deliberate UVs, authored relief, local cavity and wear masks, material separation.</p></div><div class="step"><b>5 / Inherit through the eras</b><p>Fabrication, aging and repairs, then selective Advanced additions.</p></div><div class="step"><b>6 / Verify in the browser</b><p>Neutral and exhibit light, turntable, supplied motion extrema and model-derived fallback.</p></div></div>
<div class="callout"><strong>Shared boundary with the parallel thread</strong><br>Appearance owns shell shape, plates, visible detailing, UVs and materials. Structural work owns proportions, pivots, drives, contacts and motion. Exchange a versioned frame, attachment names and clearance poses. Any conflict is an explicit design issue.</div>
<h3>Acceptance must be visual</h3><p>Recognizable clay silhouette. Constructed face. Distinct plate families. Real depth under neutral light. Materials that separate under a moving highlight. Continuity through rotation and supplied extreme poses. Authoring-to-WebGL parity, plus a separate fallback check.</p><p class="note">These are proposed gates. No likeness pass, future model validation, performance result or publication is claimed by this packet.</p></section>
<footer><p><a href="evidence.json">Source and live-media receipt</a> · <a href="validation.json">Assessment validation</a> · <a href="../../docs/appearance-fidelity-assessment-2026-09-27.md">Full production brief</a> · <a href="https://okhp3.github.io/murderbird-uncaged/review/">Published baseline</a></p><p>MurderBird creative material © Jamie Hill / OverKill Hill P³. All rights reserved. Original assets, the active models and the parallel worktree are preserved. This local packet is excluded from runtime publication.</p></footer>
</main><script>
const color=document.getElementById('color'),gray=document.getElementById('gray');
function setGray(active){document.body.classList.toggle('grayscale',active);color.setAttribute('aria-pressed',String(!active));gray.setAttribute('aria-pressed',String(active));}
color.addEventListener('click',()=>setGray(false));gray.addEventListener('click',()=>setGray(true));
</script></body></html>'''
(OUT/'index.html').write_text(html)
print(json.dumps({'sourceImages':len(sources),'parallelCopies':len(parallel_copies),'liveMediaMatches':len(public_checks),'trianglesAllVariants':triangles,'html':str(OUT/'index.html')},indent=2))
