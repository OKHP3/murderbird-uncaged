"""Build a local-only alignment gallery from existing, explicitly recorded media.

Does not render, crop, warp or modify source art or any previous review packet.
Missing or stale captures remain visible as limitations, never broken image links.
"""
from pathlib import Path
from html import escape
import hashlib
import json
import os
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/audit/alignment-v3'
BASELINE = ROOT / 'assets/audit/neutral-v2'
MODEL_DIR = ROOT / 'assets/models/uncaged-alignment-v3'
REFERENCES = ROOT / 'assets/models/uncaged-neutral-v2/reference-packet.json'


def read_json(path, default=None):
    return json.loads(path.read_text()) if path.is_file() else default


def href(path):
    return quote(os.path.relpath(path, OUT), safe='/')


def figure(path, label):
    if not path.is_file():
        return ''
    url = escape(href(path), quote=True)
    return f'<figure><a href="{url}"><img loading="lazy" src="{url}" alt="{escape(label, quote=True)}"></a><figcaption>{escape(label)}</figcaption></figure>'


def link(path, label):
    return f'<a href="{escape(href(path), quote=True)}">{escape(label)}</a>' if path.is_file() else escape(label) + ' (not available)'


def safe_capture(relative):
    path = (OUT / relative).resolve()
    if not path.is_relative_to(OUT.resolve()):
        raise ValueError(f'Capture escapes current audit directory: {relative}')
    return path


def camera_match(old, new):
    keys = ['camera', 'target', 'projection', 'orthoScale', 'lens']
    return all(key in old and key in new and old[key] == new[key] for key in keys)


def recorded_media_rows(receipt):
    """Find recorded filename/hash rows without assuming the capture script nesting."""
    if isinstance(receipt, dict):
        filename = receipt.get('filename') or receipt.get('image') or receipt.get('path')
        if isinstance(filename, str) and receipt.get('sha256'):
            yield Path(filename).name, receipt
        for value in receipt.values():
            yield from recorded_media_rows(value)
    elif isinstance(receipt, list):
        for value in receipt:
            yield from recorded_media_rows(value)


def phase_description(pose):
    before, after = pose.get('before', {}), pose.get('after', {})
    snapshot = before.get('snapshot', {})
    end_snapshot = after.get('snapshot', {})
    move = snapshot.get('powerMove') or {}
    phase = move.get('phase')
    paused = snapshot.get('paused') is True and end_snapshot.get('paused') is True
    text = 'paused live sample' if paused else 'bounded live sample; pause not established by receipt'
    if move.get('kind'):
        text += ' · ' + str(move['kind'])
    if isinstance(phase, (int, float)):
        text += f' phase {phase:.4f}'
        end_phase = (end_snapshot.get('powerMove') or {}).get('phase')
        text += ' held across views' if end_phase == phase else ' (phase equivalence not established)'
    if snapshot.get('state'):
        text += ' · state ' + str(snapshot['state'])
    return text


def main():
    inventory = read_json(MODEL_DIR / 'alignment-inventory.json')
    if inventory is None:
        raise ValueError('Generate alignment-inventory.json before building the gallery')
    model = next(row for row in inventory['generatedFiles'] if row['path'].endswith('.glb'))
    actual_model = ROOT / model['path']
    if not actual_model.is_file() or hashlib.sha256(actual_model.read_bytes()).hexdigest() != model['sha256']:
        raise ValueError('Current GLB does not match the alignment inventory')
    packet = read_json(REFERENCES)
    references = {row['id']: row for row in packet['sources']}
    authoring_data = read_json(OUT / 'authoring-views.json', [])
    authoring = authoring_data if isinstance(authoring_data, list) else authoring_data.get('views', authoring_data.get('images', []))
    authoring_identity = None if isinstance(authoring_data, list) else authoring_data.get('modelSha256')
    if authoring_identity and authoring_identity != model['sha256']:
        raise ValueError('Authoring render receipt belongs to a different GLB')
    old_authoring_data = read_json(BASELINE / 'authoring-views.json', [])
    old_authoring = old_authoring_data if isinstance(old_authoring_data, list) else old_authoring_data.get('views', [])
    old_by_name = {row['image']: row for row in old_authoring}
    by_name = {row['image']: row for row in authoring if safe_capture(row['image']).is_file()}
    browser = read_json(OUT / 'browser-validation.json', {})
    warnings = []
    if authoring and not authoring_identity and not all(row.get('modelSha256') == model['sha256'] for row in authoring):
        warnings.append('Authoring views exist, but their receipt does not establish the current model hash. Their currentness requires separate verification.')
    browser_current = browser.get('modelIdentity', {}).get('sha256') == model['sha256']
    captures = []
    if browser_current:
        for row in browser.get('screenshots', []):
            capture = safe_capture(row['filename'])
            if not capture.is_file():
                warnings.append('Missing recorded browser capture: ' + row['filename'])
                continue
            if not row.get('sha256') or hashlib.sha256(capture.read_bytes()).hexdigest() != row['sha256']:
                warnings.append('Unverified or changed browser capture omitted: ' + row['filename'])
                continue
            captures.append(row)
    elif browser:
        warnings.append('Browser evidence belongs to an earlier model hash and is omitted from this gallery.')
    else:
        warnings.append('Fresh browser evidence has not yet been recorded for this model.')
    frozen = read_json(OUT / 'frozen-extrema.json', {})
    frozen_current = frozen.get('modelSha256') == model['sha256']
    frozen_captures = []
    if frozen_current:
        frozen_hashes = dict(recorded_media_rows(frozen))
        for pose in frozen.get('poses', []):
            for view in pose.get('views', []):
                filename = f'{pose["name"]}-frozen-{view}.png'
                image = safe_capture(filename)
                if not image.is_file():
                    warnings.append('Missing frozen pose capture: ' + filename)
                    continue
                record = frozen_hashes.get(filename)
                if record and hashlib.sha256(image.read_bytes()).hexdigest() != record['sha256']:
                    warnings.append('Changed frozen pose capture omitted: ' + filename)
                    continue
                integrity = 'image hash verified' if record else 'individual image hash not recorded'
                frozen_captures.append((image, f'{pose["name"]} · {view} · {phase_description(pose)} · {integrity}'))
    elif frozen:
        warnings.append('Frozen pose receipt belongs to a different model hash; its images are omitted.')
    motion = read_json(OUT / 'motion-demonstration.json', {})
    motion_current = motion.get('modelIdentity', {}).get('sha256') == model['sha256']
    motion_videos = []
    if motion_current:
        video_hashes = dict(recorded_media_rows(motion))
        for extension in ['mp4', 'webm']:
            filename = 'alignment-motion-demonstration.' + extension
            video = safe_capture(filename)
            if not video.is_file():
                continue
            record = video_hashes.get(filename)
            if record and hashlib.sha256(video.read_bytes()).hexdigest() != record['sha256']:
                warnings.append('Changed motion video omitted: ' + filename)
                continue
            motion_videos.append(video)
    elif motion:
        warnings.append('Motion demonstration receipt belongs to a different model hash; its videos are omitted.')
    OUT.mkdir(parents=True, exist_ok=True)
    parts = ['''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MurderBird — Alignment correction v3</title><style>body{font:17px/1.55 system-ui;background:#e9e8e3;color:#202522;margin:0}main{max-width:1500px;margin:auto;padding:30px}h1{font-size:2.2rem;line-height:1.15}h2{margin-top:44px}.note{background:#fff3cf;padding:18px;border-left:5px solid #8b6028}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.two{grid-template-columns:repeat(2,minmax(0,1fr))}figure{margin:0;background:#f8f7f3;padding:12px}img{width:100%;height:510px;object-fit:contain}figcaption{font-size:14px}a{color:#244e60}code{overflow-wrap:anywhere}video{max-width:100%;width:1100px;background:#000}nav{display:flex;gap:20px;flex-wrap:wrap}details{margin:18px 0}footer{margin:36px 0;font-size:13px}@media(max-width:800px){main{padding:16px}.grid,.two{grid-template-columns:1fr}img{height:auto}h1{font-size:1.7rem}}</style><main>''']
    nav = [f'<a href="../../../">Local interactive exhibit</a>', link(REFERENCES, 'Scoped source packet'),
           link(BASELINE / 'neutral-review.html', 'Preserved v2 review'),
           link(ROOT / 'docs/correction-v2-stage-b-review.md', 'Prior Stage B assessment')]
    for filename, label in [('alignment-v3-review.md', 'Current review'), ('alignment-v3-independent-review.md', 'Independent review'), ('alignment-v3-neutral-independent-review.md', 'Independent geometry review')]:
        review = ROOT / 'docs' / filename
        if review.is_file():
            nav.append(link(review, label))
    parts.append('<nav>' + ''.join(nav) + '</nav><h1>Alignment correction v3</h1>')
    parts.append('<p class="note"><strong>Geometry and kinematic review candidate.</strong> This local pass follows authorization to refine the existing proportions and their articulation. It is not a completed visual twin, an approved final exterior or a public release. Surface finishing remains dependent on review. No new full score or owner acceptance is claimed.</p>')
    parts.append(f'<p>Current model SHA-256 <code>{model["sha256"]}</code> · {model["bytes"]:,} bytes.</p>')
    parts.append('<p>' + ' · '.join([link(MODEL_DIR / 'murderbird-alignment-v3.blend', 'Editable Blender source'), link(actual_model, 'Runtime GLB'), link(MODEL_DIR / 'alignment-inventory.json', 'Parts, pivots and hashes')]) + '</p>')
    parts.append('<p>The reference artwork controls visible identity within its recorded scope. Rear and hidden construction, mechanical load paths and dimensional reconstruction remain proposals. Perspective art does not establish metrology, force or real physical balance. Existing v2 material remains preserved as comparison evidence.</p>')
    if warnings:
        parts.append('<aside class="note"><strong>Evidence limits</strong><ul>' + ''.join('<li>' + escape(warning) + '</li>' for warning in warnings) + '</ul></aside>')
    for era, title, source_id in [('maker', 'I · Maker', 'maker-clean'), ('mechanic', 'II · Mechanic', 'mechanic'), ('builder', 'III · Advanced', 'candidate-03')]:
        ref = references[source_id]
        parts.append(f'<h2>{title} · source and current envelope</h2><p>{escape(ref["tier"])}. Excluded scope: {escape("; ".join(ref["excludedScope"]))}. The full original is retained, uncropped and unwarped.</p><div class="grid">')
        parts.append(figure(ROOT / ref['path'], title + ' source illustration · scope as above'))
        old_image = BASELINE / f'{era}-reference-perspective.png'
        parts.append(figure(old_image, title + ' preserved v2 · historical proposal'))
        name = f'{era}-reference-perspective.png'
        if name in by_name:
            same = camera_match(old_by_name.get(name, {}), by_name[name])
            parts.append(figure(safe_capture(name), title + ' current v3 · ' + ('same authoring camera as v2' if same else 'camera equivalence not established')))
        parts.append('</div>')
    july = references['july-head']
    parts.append('<h2>Head-only authority</h2><p>The July reference controls the head only. Excluded scope: ' + escape('; '.join(july['excludedScope'])) + '.</p><div class="grid two">')
    parts.append(figure(ROOT / july['path'], 'Owner-preferred July reference · head scope only'))
    head = next((name for name in ['alignment-head.png', 'neutral-head.png'] if name in by_name), None)
    if head:
        parts.append(figure(safe_capture(head), 'Current v3 · cheek, mandible and bill root proposal'))
    parts.append('</div><h2>Fixed-view comparison with preserved v2</h2><p>Only views present in the current authoring receipt are shown. Camera equivalence is checked from the recorded camera, target, projection, lens and orthographic scale; this does not normalize lighting or establish a numerical likeness score.</p>')
    for view in ['front', 'side-right', 'side-left', 'rear', 'three-quarter', 'feet', 'mantle', 'breast']:
        name = next((value for value in [f'alignment-{view}.png', f'neutral-{view}.png'] if value in by_name), None)
        if not name:
            continue
        previous_name = f'neutral-{view}.png'
        same = camera_match(old_by_name.get(previous_name, {}), by_name[name])
        parts.append('<div class="grid two">' + figure(BASELINE / previous_name, 'Preserved v2 · ' + view) + figure(safe_capture(name), 'Current v3 · ' + view + (' · matched camera' if same else ' · camera equivalence not established')) + '</div>')
    if captures:
        parts.append('<h2>Current browser samples</h2><p>Each image below matches its capture receipt and the current model hash. Freely running action samples remain bounded observations; they do not prove all moving clearances. The recorded state follows the screenshot and does not claim an exact exposure phase. ' + link(OUT / 'browser-validation.json', 'Browser receipt') + '.</p><div class="grid">')
        for row in captures:
            if '-labels-' in row['filename'] or 'fallback-preview' in row['filename']:
                continue
            parts.append(figure(safe_capture(row['filename']), f'{row["era"]} · {row["view"]} · {row["pose"]} · {row["lighting"]}'))
        parts.append('</div><details><summary>Inspection layout and illustrated fallback evidence</summary><div class="grid">')
        for row in captures:
            if '-labels-' in row['filename'] or 'fallback-preview' in row['filename']:
                parts.append(figure(safe_capture(row['filename']), row['filename'].removesuffix('.png')))
        parts.append('</div></details>')
    if frozen_captures:
        parts.append('<h2>Frozen live poses and bilateral views</h2><p>These bounded captures share the current model hash. Before/after state records establish only the recorded paused phase and views, not every intermediate contact or collision. Selected action phases are not continuous acting or physical-force evidence. ' + link(OUT / 'frozen-extrema.json', 'Frozen pose receipt') + '.</p><div class="grid">')
        for image, label in frozen_captures:
            parts.append(figure(image, label))
        parts.append('</div>')
    if motion_videos:
        video = motion_videos[0]
        parts.append('<h2>Silent normal-speed motion demonstration</h2><p>The receipt names the current model. Its synchronized clock and event samples define the observed interval; setup may precede that interval. This bounded demonstration does not substitute for two no-input runs, complete interruption testing or human acting acceptance. ' + link(OUT / 'motion-demonstration.json', 'Synchronized motion receipt') + '.</p>')
        parts.append(f'<video controls preload="metadata" src="{escape(href(video), quote=True)}"></video>')
        parts.append('<p>' + ' · '.join(link(path, path.suffix[1:].upper() + ' video') for path in motion_videos) + '</p>')
    parts.append('<h2>Recorded checks and remaining judgment</h2><ul>')
    for filename, label in [('asset-validation.json', 'Source/export integrity'), ('browser-validation.json', 'Browser and fallback checks'), ('kinematic-validation-receipt.json', 'Model and kinematic source binding'), ('kinematic-alignment.json', 'Rigid limb alignment checks'), ('jaw-sweep.json', 'Mandible sweep samples'), ('motion-validation.json', 'Era motion checks'), ('structural-motion-validation.json', 'Structural motion checks'), ('power-move-validation.json', 'Power move checks'), ('mechanism-validation.json', 'Mechanism checks'), ('frozen-extrema.json', 'Frozen live pose receipt'), ('motion-demonstration.json', 'Motion demonstration receipt')]:
        receipt = OUT / filename
        if receipt.is_file():
            parts.append('<li>' + link(receipt, label) + ' · inspect its exact model identity and declared scope.</li>')
    parts.append('</ul><p>Technical passes establish only their stated mechanical checks. Full reference-video review, human likeness and acting judgment, continuous clearance, complete interruption/restoration coverage, screen reader and physical device review, audio listening and sustained performance remain separate acceptance work. The previous PRD definitions remain unchanged.</p>')
    parts.append('<p>V10 repair/load-path geometry and V12 early-era motion reconstruction remain scoped proposals under the preserved source packet. The current pass does not turn historical clips into new controlling targets. No push, merge, deployment or Replit publication is authorized by this local gallery.</p><footer>© Jamie Hill / OverKill Hill P³ · Creative content all rights reserved.</footer></main></html>')
    destination = OUT / 'alignment-review.html'
    destination.write_text('\n'.join(parts) + '\n')
    print(destination)


if __name__ == '__main__':
    main()
