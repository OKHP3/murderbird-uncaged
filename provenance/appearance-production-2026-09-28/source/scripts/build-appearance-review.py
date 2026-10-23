"""Build a local visual comparison for one exact authored appearance iteration."""

from pathlib import Path
import argparse
import hashlib
import html
import json
import re


ROOT = Path(__file__).resolve().parents[1]
APPEARANCE_MODELS = ROOT / 'assets/models/uncaged-appearance-v1/iterations'
AUDIT = ROOT / 'assets/audit/appearance-v1'
PACK_PROOFS = (
    'allBufferViewSlicesByteExact',
    'allOtherSemanticJsonUnchanged',
    'bufferViewIndicesAndCountUnchanged',
    'outputBufferViewsFourByteAligned',
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repo_path(relative):
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError(f'Missing or out-of-repository file: {relative}')
    return path


def json_file(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--iteration', required=True)
    opts = parser.parse_args()
    iteration = opts.iteration
    if re.fullmatch(r'iteration-[a-z0-9][a-z0-9-]*', iteration) is None:
        raise ValueError('Iteration must use iteration-<lowercase-label> form')

    source = APPEARANCE_MODELS / iteration
    audit_iteration = AUDIT / iteration
    inventory = json_file(repo_path((source / 'appearance-inventory.json').relative_to(ROOT)))
    views = json_file(repo_path((audit_iteration / 'authoring-views.json').relative_to(ROOT)))
    raw_model = repo_path((source / 'murderbird-appearance.glb').relative_to(ROOT))
    raw_sha = sha256(raw_model)
    if inventory.get('iteration') != iteration:
        raise ValueError('Appearance inventory iteration does not match requested iteration')
    raw_record = next((row for row in inventory.get('generatedFiles', [])
                       if row.get('path') == raw_model.relative_to(ROOT).as_posix()), None)
    if not raw_record or raw_record.get('sha256') != raw_sha or raw_record.get('bytes') != raw_model.stat().st_size:
        raise ValueError('Raw GLB does not match its appearance inventory record')
    if views.get('sourceSha256') != next((row.get('sha256') for row in inventory.get('generatedFiles', [])
                                          if row.get('path', '').endswith('/murderbird-appearance.blend')), None):
        raise ValueError('Authoring-view receipt does not bind the native source recorded in inventory')
    native_record = next((row for row in inventory.get('generatedFiles', [])
                          if row.get('path', '').endswith('/murderbird-appearance.blend')), None)
    if not native_record or views.get('source') != native_record.get('path'):
        raise ValueError('Authoring-view source path does not match the native inventory record')

    for view in views.get('views', []):
        image = repo_path(view['path'])
        if sha256(image) != view.get('sha256'):
            raise ValueError(f'Authoring still hash mismatch: {view["path"]}')

    packed_model = source / 'murderbird-appearance-packed.glb'
    packing_path = audit_iteration / 'packing.json'
    packed_sha = None
    packed_download_html = ''
    if packed_model.exists() or packing_path.exists():
        if not packed_model.is_file() or not packing_path.is_file():
            raise ValueError('Packed GLB and packing receipt must either both exist or both be absent')
        packing = json_file(packing_path)
        packed_model = repo_path(packed_model.relative_to(ROOT))
        packed_sha = sha256(packed_model)
        if (packing.get('inputSha256') != raw_sha
                or packing.get('outputSha256') != packed_sha
                or packing.get('inputBytes') != raw_model.stat().st_size
                or packing.get('outputBytes') != packed_model.stat().st_size
                or not all(packing.get('proofs', {}).get(proof) is True for proof in PACK_PROOFS)):
            raise ValueError('Packed GLB does not match its lossless packing receipt')
        packed_rel = f'../../models/uncaged-appearance-v1/iterations/{iteration}/murderbird-appearance-packed.glb'
        raw_rel = f'../../models/uncaged-appearance-v1/iterations/{iteration}/murderbird-appearance.glb'
        packed_download_html = (
            f'<a class="action" href="{packed_rel}">Download packed runtime candidate GLB</a>'
            f'<a href="{raw_rel}">Download raw authoring export</a>'
            f'<p class="hashes">Raw GLB SHA-256: <code>{raw_sha}</code><br>'
            f'Packed GLB SHA-256: <code>{packed_sha}</code></p>'
        )
    else:
        raw_rel = f'../../models/uncaged-appearance-v1/iterations/{iteration}/murderbird-appearance.glb'
        packed_download_html = (
            f'<a class="action" href="{raw_rel}">Download raw appearance candidate GLB</a>'
            f'<p class="hashes">Raw GLB SHA-256: <code>{raw_sha}</code><br>'
            'Packed GLB is not available for this iteration.</p>'
        )

    art_review_path = audit_iteration / 'art-review.json'
    art_review_html = ''
    if art_review_path.is_file():
        art_review = json_file(art_review_path)
        reviewed_model_sha = art_review.get('sourceModelSha256', art_review.get('modelSha256'))
        if reviewed_model_sha and reviewed_model_sha != raw_sha:
            raise ValueError('Art-review receipt is bound to a different raw GLB')
        review_status = art_review.get('status', art_review.get('decision', 'recorded'))
        owner_acceptance = art_review.get('ownerAcceptance', 'not recorded')
        art_review_html = (
            f'<p class="review-status"><strong>Art review: {html.escape(str(review_status))}.</strong> '
            f'Owner acceptance: {html.escape(str(owner_acceptance))}. '
            f'<a href="{iteration}/art-review.json">Open art-review receipt</a>.</p>')
    else:
        art_review_html = '<p class="review-status"><strong>No art-review receipt is recorded for this iteration.</strong></p>'

    browser_dir = audit_iteration / 'browser'
    browser_receipt = browser_dir / 'browser-validation.json'
    browser_images = [browser_dir / 'advanced-exhibit.png', browser_dir / 'head-neutral.png']
    browser_html = ''
    if browser_receipt.exists() and all(image.is_file() for image in browser_images):
        report = json_file(browser_receipt)
        report_model_sha = report.get('modelSha256')
        if report_model_sha and report_model_sha != raw_sha:
            raise ValueError('Browser receipt is bound to a different raw GLB')
        for image in browser_images:
            if not image.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'):
                raise ValueError(f'Browser evidence image is not PNG: {image.relative_to(ROOT)}')
        status = html.escape(str(report.get('status', 'receipt available')))
        browser_html = f'''<section class="browser-evidence"><h2>Local browser evidence</h2>
<p>Browser receipt status: <strong>{status}</strong>. These captures document the browser-rendered candidate and neutral head view; they do not establish artistic acceptance or release readiness. <a href="{iteration}/browser/browser-validation.json">Open browser validation receipt</a>.</p>
<div class="before"><figure><img src="{iteration}/browser/advanced-exhibit.png" alt="Advanced appearance candidate in the browser exhibit"><figcaption><strong>Advanced · exhibit WebGL</strong>Browser capture from the local review.</figcaption></figure>
<figure><img src="{iteration}/browser/head-neutral.png" alt="Neutral-light browser head inspection"><figcaption><strong>Head · neutral-light browser view</strong>Browser capture from the local review.</figcaption></figure></div></section>'''

    template = '''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MurderBird — appearance workshop</title>
<style>
:root{color-scheme:dark;font:16px/1.55 system-ui,sans-serif;background:#121716;color:#e5e6dc}*{box-sizing:border-box}body{margin:0}main{max-width:1540px;margin:auto;padding:40px 4vw 70px}h1{font:500 clamp(2rem,4vw,4rem)/1.05 Georgia,serif;margin:12px 0 20px}h2{font:500 1.8rem Georgia,serif}p{max-width:77ch;color:#bbc3bc}.kicker{color:#c9aa6c;letter-spacing:.13em;font-size:12px;text-transform:uppercase}.controls{display:flex;gap:16px;flex-wrap:wrap;margin:28px 0 20px}label{display:grid;gap:5px;font-size:13px}select,a.action{background:#25302b;color:#fff;border:1px solid #526052;padding:10px 18px;border-radius:3px;font:inherit}a{color:#dec58e}.comparison{display:grid;grid-template-columns:1fr 1fr;gap:18px}figure{margin:0;background:#0c100f;border:1px solid #303c35;overflow:hidden}figure img{display:block;width:100%;height:650px;object-fit:contain;background:#090c0b}figcaption{padding:14px 18px;color:#c9d0c8;font-size:13px}figcaption strong{color:#eadfca;display:block;font-size:16px}.gaps{border:1px solid #806c46;background:#211f18;padding:20px;margin:28px 0}.gaps strong{color:#f0d8ad}.review-status{padding:12px 16px;border-left:4px solid #c9aa6c;background:#1d2521}.hashes{font-size:12px}details{border-top:1px solid #3a463d;margin:30px 0;padding-top:18px}summary{cursor:pointer;color:#dec58e}.before{display:grid;grid-template-columns:1fr 1fr;gap:18px}.before img{height:440px}.browser-evidence{border-top:1px solid #3a463d;margin-top:36px;padding-top:18px}video{display:block;width:min(100%,900px);background:#0b100e;margin:20px auto}code{overflow-wrap:anywhere;font-size:12px}nav{display:flex;gap:22px;flex-wrap:wrap;align-items:center;margin:24px 0}footer{border-top:1px solid #39443c;margin-top:40px;padding-top:20px;color:#9aa69c;font-size:13px}@media(max-width:760px){main{padding:25px 18px}.comparison,.before{grid-template-columns:1fr}figure img{height:450px}}
</style>
<main><div class="kicker">MurderBird: Uncaged · Local production · Not published</div>
<h1>Surface and form.</h1>
<p>Fitted armor, layered head construction, aged metal and articulated casing over the preserved rigid interface. Compare the actual 3D candidate with the selected artwork. The review record below states this iteration’s status; this gallery itself does not confer approval.</p>
<aside class="gaps"><strong>Known limits</strong><br>This is not an exact match to the selected illustrations. It retains frozen alignment-v3 proportions and kinematics; integration with a separately verified parallel structural checkpoint is still pending. Hidden and rear surfaces remain reconstructions.</aside>
<div class="controls"><label>Construction era<select id="era"><option value="advanced">Advanced</option><option value="mechanic">Mechanic</option><option value="maker">Maker</option></select></label><label>View<select id="view"><option value="three-quarter">Whole body</option><option value="head">Head and neck</option><option value="side">Side</option><option value="front">Front</option><option value="rear">Back</option><option value="feet">Feet</option></select></label></div>
__ART_REVIEW__
<div class="comparison"><figure><img id="candidate" src="__ITER__/advanced-three-quarter.png" alt="Actual rendered appearance candidate"><figcaption><strong id="candidate-label">Advanced · whole body</strong>__ITER__ · exact Blender source, physically rendered. Static pose; no image-generation substitute.</figcaption></figure><figure><img id="reference" src="../../img/library/murderbird-unified-master-candidate-03-2026-09-06.png" alt="Selected MurderBird full-body illustration"><figcaption><strong id="reference-label">Selected full-body appearance reference</strong><span id="reference-note">Candidate 03 guides visible form and material language. Different pose and camera; hidden surfaces remain reconstructed proposals.</span></figcaption></figure></div>
<nav><a class="action" href="../../../?review=appearance">Open interactive exhibit</a>__DOWNLOAD__<a href="__ITER__/asset-validation.json">Asset checks</a><a href="__ITER__/authoring-views.json">Render provenance</a></nav>
<p id="view-note" role="status">The candidate retains the established v3 joint locations and hierarchy. Head details use the July reference only for head identity.</p>
<details><summary>Preserved earlier checkpoints</summary><p>These show the progression, including the rejected first appearance pass. Their cameras and lighting differ, so this is a qualitative comparison.</p><div class="before"><figure><img src="../alignment-v3/alignment-three-quarter.png" alt="Preserved neutral alignment model"><figcaption><strong>Neutral structural source</strong>Alignment v3; preserved unchanged.</figcaption></figure><figure><img src="iteration-01/advanced-three-quarter.png" alt="Rejected first appearance iteration"><figcaption><strong>First appearance pass</strong>Rejected during this production loop: large flat plates, excessive gold and insufficient face definition.</figcaption></figure></div></details>
<section id="film" hidden><h2>Inspect every side.</h2><p>A camera orbit of the exact candidate geometry. This demonstrates surfaces and silhouette, not gait, clearance or mechanical acceptance.</p><video controls loop muted playsinline preload="metadata"><source src="__ITER__/turntable-builder/turntable-builder.mp4" type="video/mp4"></video></section>
__BROWSER__
<footer>Raw GLB SHA-256: <code>__RAW_SHA__</code><br>Packed GLB SHA-256: <code>__PACKED_SHA__</code><br>Creative content all rights reserved under NOTICE.md. Local review in <code>assets/audit/appearance-v1/</code>; no publication or owner approval is implied.</footer></main>
<script>
const era=document.querySelector('#era'),view=document.querySelector('#view'),picture=document.querySelector('#candidate'),reference=document.querySelector('#reference');
function update(){const e=era.value,v=view.value,advancedOnly=!['head','three-quarter'].includes(v),renderEra=advancedOnly?'advanced':e;picture.src=`__ITER__/${renderEra}-${v}.png`;document.querySelector('#candidate-label').textContent=`${renderEra[0].toUpperCase()+renderEra.slice(1)} · ${view.selectedOptions[0].text}`;document.querySelector('#view-note').textContent=advancedOnly?'This inspection angle is rendered for Advanced. Head and whole-body views are available for all three eras.':'The candidate retains the established v3 joint locations and hierarchy. Head details use the July reference only for head identity.';reference.src=v==='head'?'../../../context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png':renderEra==='maker'?'../../img/library/murderbird-unified-maker-clean-candidate-2026-09-06.png':renderEra==='mechanic'?'../../img/library/murderbird-unified-mechanic-candidate-2026-09-06.png':'../../img/library/murderbird-unified-master-candidate-03-2026-09-06.png';document.querySelector('#reference-label').textContent=v==='head'?'Selected July head identity':`${renderEra==='advanced'?'Selected full-body':renderEra==='maker'?'Maker':'Mechanic'} appearance reference`;document.querySelector('#reference-note').textContent=v==='head'?'Head identity only. The long train, thin body and CRT support in this illustration are excluded from the body direction.':'Illustrative appearance reference. Different pose and camera; hidden surfaces remain reconstructed.';}
era.addEventListener('change',update);view.addEventListener('change',update);
</script></html>'''
    turntable = audit_iteration / 'turntable-builder/turntable-builder.mp4'
    generated = (template.replace('__ITER__', iteration)
                 .replace('__DOWNLOAD__', packed_download_html)
                 .replace('__ART_REVIEW__', art_review_html)
                 .replace('__RAW_SHA__', raw_sha)
                 .replace('__PACKED_SHA__', packed_sha or 'not generated')
                 .replace('__BROWSER__', browser_html))
    if turntable.is_file():
        generated = generated.replace('<section id="film" hidden>', '<section id="film">')
    output = AUDIT / 'index.html'
    output.write_text(generated, encoding='utf-8')
    print(output)


if __name__ == '__main__':
    main()
