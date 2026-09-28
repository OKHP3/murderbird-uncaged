"""Build a local-only alignment gallery from existing, explicitly recorded media.

Does not render, crop, warp or modify source art or any previous review packet.
Missing or stale captures remain visible as limitations, never broken image links.
"""
from pathlib import Path
from html import escape
import hashlib
import json
import os
import argparse
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/audit/alignment-v4'
BASELINE = ROOT / 'assets/audit/alignment-v3'
MODEL_DIR = ROOT / 'assets/models/uncaged-alignment-v4'
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
    for key, label in [('before', 'before'), ('after', 'after')]:
        claw = pose.get(key, {}).get('motionClawAction')
        if not isinstance(claw, dict):
            continue
        phase = claw.get('phase')
        phase_text = f'{phase:.4f}' if isinstance(phase, (int, float)) else 'unrecorded'
        contact = claw.get('contact')
        contact_text = 'yes' if contact is True else 'no' if contact is False else 'unrecorded'
        values = [f'{label}: claw {claw.get("stage", "unrecorded")} phase {phase_text}',
                  f'support {claw.get("supportSide", "unrecorded")}', f'contact {contact_text}']
        for key, label_text in [('supportGroundMin', 'supportGroundMin'), ('supportError', 'supportError'), ('tipMinY', 'tipMinY')]:
            value = claw.get(key)
            if isinstance(value, (int, float)):
                values.append(f'{label_text} {value:.4f} m')
        text += ' · ' + ', '.join(values)
    return text


def audit_path(relative):
    if Path(relative).is_absolute():
        raise ValueError('Autonomy manifest and evidence paths must be repository-relative')
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(OUT.resolve()):
        raise ValueError(f'Autonomy evidence must remain under alignment-v4 audit: {relative}')
    return path


def verify_sources(value, label):
    rows = value.get('sourceIdentity')
    if not isinstance(rows, list) or not rows:
        raise ValueError(f'{label} has no source identity list')
    for item in rows:
        source, digest = item.get('path'), item.get('sha256')
        if not isinstance(source, str) or not isinstance(digest, str):
            raise ValueError(f'{label} has incomplete source identity: {item}')
        path = (ROOT / source).resolve()
        if not path.is_relative_to(ROOT.resolve()) or not path.is_file():
            raise ValueError(f'{label} source missing or outside repository: {source}')
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f'{label} source identity is stale: {source}')


def load_autonomy(manifest_argument, model_sha):
    if not manifest_argument:
        return [], [], []
    try:
        manifest_path = audit_path(manifest_argument)
        manifest = json.loads(manifest_path.read_text())
        if manifest.get('modelSha256') != model_sha or manifest.get('modelIdentity', {}).get('sha256') != model_sha:
            raise ValueError('manifest belongs to a different model hash')
        verify_sources(manifest, manifest_path.name)
        runs = manifest.get('runs')
        if not isinstance(runs, list) or len(runs) != 2:
            raise ValueError('manifest must identify exactly two separate runs')
        videos, summaries, seen, seeds = [], [], set(), set()
        for run in runs:
            receipt_rel = run.get('receipt')
            if run.get('status') != 'passed' or not isinstance(receipt_rel, str):
                raise ValueError(f'incomplete run entry: {run}')
            receipt_path = audit_path(receipt_rel)
            if receipt_rel in seen or not receipt_path.is_file():
                raise ValueError(f'duplicate or missing receipt: {receipt_rel}')
            seen.add(receipt_rel)
            receipt_bytes = receipt_path.read_bytes()
            if hashlib.sha256(receipt_bytes).hexdigest() != run.get('receiptSha256'):
                raise ValueError(f'receipt hash mismatch: {receipt_rel}')
            receipt = json.loads(receipt_bytes)
            if receipt.get('status') != 'passed' or receipt.get('modelSha256') != model_sha or receipt.get('modelIdentity', {}).get('sha256') != model_sha:
                raise ValueError(f'receipt is failed or bound to an earlier model: {receipt_rel}')
            if receipt.get('durationTargetSeconds') != 120 or receipt.get('actualDurationSeconds', 0) < 120:
                raise ValueError(f'run is shorter than the requested 120 seconds: {receipt_rel}')
            seed = receipt.get('seed', {}).get('value')
            if seed in seeds:
                raise ValueError('the two runs do not use distinct recorded seeds')
            seeds.add(seed)
            samples = receipt.get('samples')
            if not isinstance(samples, list) or len(samples) < 1000 or (samples[-1].get('seconds', 0) < 119.5):
                raise ValueError(f'run lacks a full-rate 120-second telemetry trace: {receipt_rel}')
            if any(sample.get('era') != 'builder' or sample.get('visitorPresent') is not False or sample.get('paused') is not False or sample.get('inspection') is not False or sample.get('reducedMotion') is not False for sample in samples):
                raise ValueError(f'run contains a non-Advanced, visitor, paused, inspection or reduced-motion sample: {receipt_rel}')
            verify_sources(receipt, receipt_rel)
            if run.get('modelSha256') != model_sha:
                raise ValueError(f'manifest model hash mismatch: {receipt_rel}')
            media, verified = receipt.get('media'), {}
            if not isinstance(media, list):
                raise ValueError(f'receipt has no media inventory: {receipt_rel}')
            for item in media:
                filename = item.get('filename')
                path = audit_path(filename) if isinstance(filename, str) else None
                if path is None or not path.is_file():
                    raise ValueError(f'media missing: {item}')
                digest, size = hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_size
                if digest != item.get('sha256') or size != item.get('bytes'):
                    raise ValueError(f'media hash/size mismatch: {filename}')
                manifest_media = next((row for row in run.get('media', []) if row.get('filename') == filename), None)
                if not manifest_media or manifest_media.get('sha256') != digest or manifest_media.get('bytes') != size:
                    raise ValueError(f'manifest media identity mismatch: {filename}')
                verified[path.suffix.lower()] = path
            if not {'.mp4', '.webm'}.issubset(verified):
                raise ValueError(f'run needs verified MP4 and original WebM: {receipt_rel}')
            repetition = receipt.get('actingTrace', {}).get('repetition', {})
            if not all(key in repetition for key in ['selectedPlanFamilies', 'selectedPlanRoutes', 'executedActionFamilies']):
                raise ValueError(f'receipt lacks acting/repetition summaries: {receipt_rel}')
            videos.append({'mp4': verified['.mp4'], 'webm': verified['.webm'], 'receipt': receipt_path, 'run': receipt})
            summaries.append({'receipt': receipt_path, 'repetition': repetition})
        return videos, summaries, []
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        return [], [], ['Fresh no-input autonomy evidence omitted: ' + str(error)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--autonomy-manifest', help='Optional repository-relative manifest under assets/audit/alignment-v4')
    args = parser.parse_args()
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
    by_name = {row['image']: row for row in authoring}
    browser = read_json(OUT / 'browser-validation.json', {})
    warnings = []
    for row in authoring:
        image = safe_capture(row['image'])
        if row.get('modelSha256') != model['sha256'] or not image.is_file() or hashlib.sha256(image.read_bytes()).hexdigest() != row.get('sha256'):
            raise ValueError(f'Current v4 authoring image is stale or changed: {row["image"]}')
    baseline_inventory = read_json(ROOT / 'assets/models/uncaged-alignment-v3/alignment-inventory.json', {})
    baseline_model = next((row for row in baseline_inventory.get('generatedFiles', []) if row.get('path', '').endswith('.glb')), {})
    baseline_sha = baseline_model.get('sha256')
    verified_old = {}
    for row in old_authoring:
        image = BASELINE / row['image']
        image_hash_matches = not row.get('sha256') or (image.is_file() and hashlib.sha256(image.read_bytes()).hexdigest() == row['sha256'])
        if row.get('modelSha256') == baseline_sha and image.is_file() and image_hash_matches:
            verified_old[row['image']] = row
    old_by_name = verified_old
    if old_authoring and len(verified_old) != len(old_authoring):
        warnings.append('Some preserved v3 authoring views failed their authoring receipt hash/model binding and are omitted.')
    if old_authoring and not any(row.get('sha256') for row in old_authoring):
        warnings.append('The preserved v3 authoring manifest binds camera records to the v3 model but records no per-image hashes; v3 image file integrity is not independently established here.')
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
    autonomy_videos, autonomy_summaries, autonomy_warnings = load_autonomy(args.autonomy_manifest, model['sha256'])
    warnings.extend(autonomy_warnings)
    OUT.mkdir(parents=True, exist_ok=True)
    parts = ['''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MurderBird — Alignment correction v4</title><style>body{font:17px/1.55 system-ui;background:#e9e8e3;color:#202522;margin:0}main{max-width:1500px;margin:auto;padding:30px}h1{font-size:2.2rem;line-height:1.15}h2{margin-top:44px}.note{background:#fff3cf;padding:18px;border-left:5px solid #8b6028}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.two{grid-template-columns:repeat(2,minmax(0,1fr))}figure{margin:0;background:#f8f7f3;padding:12px}img{width:100%;height:510px;object-fit:contain}figcaption{font-size:14px}a{color:#244e60}code{overflow-wrap:anywhere}video{max-width:100%;width:1100px;background:#000}nav{display:flex;gap:20px;flex-wrap:wrap}details{margin:18px 0}footer{margin:36px 0;font-size:13px}@media(max-width:800px){main{padding:16px}.grid,.two{grid-template-columns:1fr}img{height:auto}h1{font-size:1.7rem}}</style><main>''']
    nav = [f'<a href="../../../">Local interactive exhibit</a>', link(REFERENCES, 'Scoped source packet'),
           link(BASELINE / 'alignment-review.html', 'Preserved v3 review'),
           link(ROOT / 'docs/correction-v2-stage-b-review.md', 'Prior Stage B assessment')]
    for filename, label in [('alignment-v4-review.md', 'Current review'), ('alignment-v4-independent-review.md', 'Independent review'), ('alignment-v4-neutral-independent-review.md', 'Independent geometry review')]:
        review = ROOT / 'docs' / filename
        if review.is_file():
            nav.append(link(review, label))
    parts.append('<nav>' + ''.join(nav) + '</nav><h1>Alignment correction v4</h1>')
    parts.append('<p class="note"><strong>Geometry and kinematic review candidate.</strong> This local pass follows authorization to refine the existing proportions and their articulation. It is not a completed visual twin, an approved final exterior or a public release. Surface finishing remains dependent on review. No new full score or owner acceptance is claimed.</p>')
    parts.append(f'<p>Current model SHA-256 <code>{model["sha256"]}</code> · {model["bytes"]:,} bytes.</p>')
    parts.append('<p>' + ' · '.join([link(MODEL_DIR / 'murderbird-alignment-v4.blend', 'Editable Blender source'), link(actual_model, 'Runtime GLB'), link(MODEL_DIR / 'alignment-inventory.json', 'Parts, pivots and hashes')]) + '</p>')
    parts.append('<p>The reference artwork controls visible identity within its recorded scope. Rear and hidden construction, mechanical load paths and dimensional reconstruction remain proposals. Perspective art does not establish metrology, force or real physical balance. Existing v3 material remains preserved as comparison evidence.</p>')
    if warnings:
        parts.append('<aside class="note"><strong>Evidence limits</strong><ul>' + ''.join('<li>' + escape(warning) + '</li>' for warning in warnings) + '</ul></aside>')
    for era, title, source_id in [('maker', 'I · Maker', 'maker-clean'), ('mechanic', 'II · Mechanic', 'mechanic'), ('builder', 'III · Advanced', 'candidate-03')]:
        ref = references[source_id]
        parts.append(f'<h2>{title} · source and current envelope</h2><p>{escape(ref["tier"])}. Excluded scope: {escape("; ".join(ref["excludedScope"]))}. The full original is retained, uncropped and unwarped.</p><div class="grid">')
        parts.append(figure(ROOT / ref['path'], title + ' source illustration · scope as above'))
        name = f'{era}-reference-perspective.png'
        if name in old_by_name:
            parts.append(figure(BASELINE / name, title + ' preserved v3 · historical proposal'))
        if name in by_name and name in old_by_name:
            same = camera_match(old_by_name.get(name, {}), by_name[name])
            parts.append(figure(safe_capture(name), title + ' current v4 · ' + ('same authoring camera as v3' if same else 'camera equivalence not established')))
        parts.append('</div>')
    july = references['july-head']
    parts.append('<h2>Head-only authority</h2><p>The July reference controls the head only. Excluded scope: ' + escape('; '.join(july['excludedScope'])) + '.</p><div class="grid two">')
    parts.append(figure(ROOT / july['path'], 'Owner-preferred July reference · head scope only'))
    head = 'alignment-head.png' if 'alignment-head.png' in by_name and 'alignment-head.png' in old_by_name else None
    if head:
        parts.append(figure(safe_capture(head), 'Current v4 · cheek, mandible and bill root proposal'))
    parts.append('</div><h2>Fixed-view comparison: v4 against preserved v3</h2><p>Only matching filenames present in both authoring manifests and verified against their model-specific hashes are shown. Camera equivalence is checked from the recorded camera, target, projection, lens and orthographic scale; this does not normalize lighting or establish a numerical likeness score.</p>')
    for view in ['front', 'side-right', 'side-left', 'rear', 'three-quarter', 'feet', 'mantle', 'breast']:
        name = f'alignment-{view}.png'
        if name not in by_name or name not in old_by_name:
            continue
        same = camera_match(old_by_name[name], by_name[name])
        parts.append('<div class="grid two">' + figure(BASELINE / name, 'Preserved v3 · ' + view) + figure(safe_capture(name), 'Current v4 · ' + view + (' · matched camera' if same else ' · camera equivalence not established')) + '</div>')
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
    parts.append('<h2>Two no-input Advanced-era autonomy runs</h2><p>Each run is a fresh headed WebGL session at normal speed with a recorded 120-second interval and no input after timing begins. Repetition summaries separate selected plans from observed action execution. Actual-contact events and claw stages come from the named runtime telemetry. These records are evidence for review, not a human acting judgment; <strong>human acting judgment remains pending</strong>.</p>')
    if autonomy_videos:
        if args.autonomy_manifest:
            parts.append('<p>' + link(audit_path(args.autonomy_manifest), 'Verified autonomy capture manifest') + '.</p>')
        parts.append('<div class="grid two">')
        for item in autonomy_videos:
            run = item['run']
            repetition = run['actingTrace']['repetition']
            run_title = f'Run {run["run"]} · seed {run["seed"]["value"]} · {run["actualDurationSeconds"]:.2f}s'
            parts.append(f'<section><h3>{escape(run_title)}</h3><video controls preload="metadata" src="{escape(href(item["mp4"]), quote=True)}"></video>')
            parts.append('<p>' + link(item['mp4'], 'MP4') + ' · ' + link(item['webm'], 'Original WebM') + ' · ' + link(item['receipt'], 'Telemetry receipt') + '</p>')
            for key, label in [('selectedPlanFamilies', 'Selected plan families'), ('selectedPlanRoutes', 'Selected routes'), ('executedActionFamilies', 'Observed executed action families')]:
                summary = repetition[key]
                counts = ', '.join(f'{name}: {count}' for name, count in sorted(summary.get('counts', {}).items())) or 'none recorded'
                ngrams = summary.get('repeatedAdjacentNgrams', {})
                repeated = {n: rows for n, rows in ngrams.items() if rows}
                parts.append(f'<p><strong>{escape(label)}:</strong> {escape(counts)}. Adjacent repeats: {summary.get("consecutiveRepeats", 0)}. Repeated adjacent n-grams: <code>{escape(json.dumps(repeated, sort_keys=True))}</code></p>')
            parts.append('</section>')
        parts.append('</div>')
    elif args.autonomy_manifest:
        parts.append('<p class="note">The supplied autonomy manifest was stale or incomplete and its runs were omitted. See the evidence-limit note above. Human acting judgment remains pending.</p>')
    else:
        parts.append('<p class="note">Fresh two-run autonomy recordings have not yet been supplied to this gallery. Human acting judgment remains pending.</p>')
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
