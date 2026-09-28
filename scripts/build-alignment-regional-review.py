#!/usr/bin/env python3
"""Build a local, hash-checked regional review gallery from a supplied packet.

Expected packet schema (schemaVersion 1):
  status: the literal "revision required"
  models: {baseline, current}, each {label, path, sha256}
  references: rows {id, label, scope, path, sha256}; IDs must include
    maker-clean, candidate-03, and july-head.
  comparisons: exactly one row for each view in
    front, side, rear, three-quarter, head, feet. Each row has view,
    cameraKey, baseline, after. Each image object has
    {path, sha256, modelSha256, cameraKey}; baseline and after must share
    the row cameraKey and their respective model SHA.
  eraConfigurations: exactly maker, mechanic, advanced; each row has
    {era, label, path, sha256, modelSha256, scope}.
  motion: optional {scope, frozenFrames:[asset rows], videos:[asset rows],
    receipts:[asset rows]}, where every asset row is {label, path, sha256,
    modelSha256, scope}. Files are linked as supplied and never transformed.

Every path must be repository-relative, remain inside this checkout, and
match its declared SHA-256. Required source/comparison/configuration media
fail closed when missing. The gallery is a review aid, not likeness, motion,
collision, or owner-acceptance certification.
"""

from __future__ import annotations

import argparse
from html import escape
import hashlib
import json
import math
import numbers
import os
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / 'assets/audit/alignment-v5-regional'
OUT_FILE = OUT_DIR / 'index.html'
REQUIRED_VIEWS = ('front', 'side', 'rear', 'three-quarter', 'head', 'feet')
REQUIRED_REFERENCES = ('maker-clean', 'candidate-03', 'july-head')
REQUIRED_ERAS = ('maker', 'mechanic', 'advanced')


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def verified_asset(row: dict, label: str, expected_model: str | None = None) -> Path:
    if not isinstance(row, dict):
        raise ValueError(f'{label}: expected an asset object')
    rel = row.get('path')
    digest = row.get('sha256')
    if not isinstance(rel, str) or Path(rel).is_absolute():
        raise ValueError(f'{label}: path must be repository-relative')
    path = (ROOT / rel).resolve()
    if not path.is_relative_to(ROOT.resolve()) or not path.is_file():
        raise ValueError(f'{label}: missing or out-of-repository asset: {rel}')
    if not isinstance(digest, str) or len(digest) != 64 or sha256(path) != digest:
        raise ValueError(f'{label}: SHA-256 missing or stale for {rel}')
    if expected_model is not None and row.get('modelSha256') != expected_model:
        raise ValueError(f'{label}: media is not bound to the declared current model')
    return path


def camera_key(camera: dict) -> str:
    if not isinstance(camera, dict) or set(camera) != {'location', 'target', 'orthographicScale'}:
        raise ValueError('camera must contain exactly location, target, and orthographicScale')
    for field in ('location', 'target'):
        vector = camera[field]
        if (not isinstance(vector, list) or len(vector) != 3 or
                any(isinstance(value, bool) or not isinstance(value, numbers.Real) or not math.isfinite(value) for value in vector)):
            raise ValueError(f'camera.{field} must be a finite three-number vector')
    scale = camera['orthographicScale']
    if isinstance(scale, bool) or not isinstance(scale, numbers.Real) or not math.isfinite(scale) or scale <= 0:
        raise ValueError('camera.orthographicScale must be a finite positive number')
    return hashlib.sha256(json.dumps(camera, sort_keys=True).encode()).hexdigest()[:12]


def verify_render_binding(item: dict, label: str, expected_model: str, expected_camera: dict,
                          expected_key: str, expected_era: str | None = None) -> None:
    image_path = verified_asset(item, label, expected_model)
    if item.get('camera') != expected_camera or item.get('cameraKey') != expected_key:
        raise ValueError(f'{label}: camera payload/key mismatch')
    if camera_key(item.get('camera')) != expected_key:
        raise ValueError(f'{label}: camera key does not match canonical camera payload')
    receipt_path = verified_asset(item.get('receipt'), f'{label} views receipt')
    receipt = json.loads(receipt_path.read_text())
    if (receipt.get('model', {}).get('sha256') != expected_model or
            item.get('receiptModelSha256') != expected_model or
            receipt.get('model', {}).get('path') != item.get('receiptModelPath')):
        raise ValueError(f'{label}: receipt model identity mismatch')
    if receipt.get('rendererSha256') != item.get('rendererSha256') or not isinstance(item.get('rendererSha256'), str) or len(item['rendererSha256']) != 64:
        raise ValueError(f'{label}: renderer identity mismatch')
    if receipt.get('era') != item.get('renderEra'):
        raise ValueError(f'{label}: receipt era mismatch')
    if expected_era is not None and item.get('renderEra') != expected_era:
        raise ValueError(f'{label}: unexpected render era')
    image_name = item.get('imageName')
    if not isinstance(image_name, str) or Path(image_name).name != image_name:
        raise ValueError(f'{label}: invalid receipt image name')
    receipt_row = next((row for row in receipt.get('views', []) if row.get('image') == image_name), None)
    if receipt_row is None:
        raise ValueError(f'{label}: image absent from bound render receipt')
    if (receipt_row.get('sha256') != item.get('sha256') or
            receipt_row.get('bytes') != image_path.stat().st_size or
            image_path.resolve() != (receipt_path.parent / image_name).resolve()):
        raise ValueError(f'{label}: image bytes/path do not match bound receipt')
    actual_camera = {key: receipt_row.get(key) for key in ('location', 'target', 'orthographicScale')}
    if actual_camera != expected_camera:
        raise ValueError(f'{label}: actual receipt camera differs from comparison camera')


def rel_href(path: Path) -> str:
    return quote(os.path.relpath(path.resolve(), OUT_DIR.resolve()), safe='/')


def image_card(path: Path, label: str, detail: str = '') -> str:
    url = escape(rel_href(path), quote=True)
    caption = escape(label)
    if detail:
        caption += '<small>' + escape(detail) + '</small>'
    return (f'<figure><a href="{url}"><img loading="lazy" src="{url}" '
            f'alt="{escape(label, quote=True)}"></a><figcaption>{caption}</figcaption></figure>')


def file_link(path: Path, label: str) -> str:
    return f'<a href="{escape(rel_href(path), quote=True)}">{escape(label)}</a>'


def load_packet(path: Path) -> tuple[dict, dict[str, Path], dict[str, Path]]:
    packet = json.loads(path.read_text())
    if packet.get('schemaVersion') != 1:
        raise ValueError('Packet schemaVersion must be 1')
    if packet.get('status') != 'revision required':
        raise ValueError('Packet status must remain exactly "revision required"')
    models = packet.get('models')
    if not isinstance(models, dict) or not {'baseline', 'current'} <= models.keys():
        raise ValueError('Packet needs models.baseline and models.current')
    model_paths = {}
    for key in ('baseline', 'current'):
        model_paths[key] = verified_asset(models[key], f'models.{key}')
    if packet.get('revisionComparisons'):
        model_paths['previous'] = verified_asset(models['previous'], 'models.previous')
        for row in packet['revisionComparisons']:
            if row.get('cameraKey') != camera_key(row.get('camera')):
                raise ValueError(f'revision {row.get("label")}: camera key mismatch')
            for key, model_key in [('baseline', 'previous'), ('after', 'current')]:
                verify_render_binding(row[key], f'revision {row["label"]}/{key}', models[model_key]['sha256'],
                                      row['camera'], row['cameraKey'], 'builder')

    references = packet.get('references')
    if not isinstance(references, list):
        raise ValueError('Packet references must be a list')
    reference_by_id = {}
    reference_paths = {}
    for row in references:
        ref_id = row.get('id') if isinstance(row, dict) else None
        if not isinstance(ref_id, str) or ref_id in reference_by_id:
            raise ValueError(f'Duplicate or invalid reference row: {row}')
        reference_paths[ref_id] = verified_asset(row, f'reference {ref_id}')
        reference_by_id[ref_id] = row
    missing_refs = set(REQUIRED_REFERENCES) - reference_by_id.keys()
    if missing_refs:
        raise ValueError('Missing required source references: ' + ', '.join(sorted(missing_refs)))

    comparisons = packet.get('comparisons')
    if not isinstance(comparisons, list) or len(comparisons) != len(REQUIRED_VIEWS):
        raise ValueError('Packet must provide exactly six fixed-camera comparison rows')
    comparison_by_view = {}
    for row in comparisons:
        view = row.get('view') if isinstance(row, dict) else None
        if view not in REQUIRED_VIEWS or view in comparison_by_view:
            raise ValueError(f'Duplicate or unexpected comparison view: {view}')
        key = row.get('cameraKey')
        camera = row.get('camera')
        if not isinstance(key, str) or key != camera_key(camera):
            raise ValueError(f'{view}: cameraKey is missing or does not match camera payload')
        baseline = row.get('baseline')
        verify_render_binding(baseline, f'{view} baseline', models['baseline']['sha256'], camera, key, 'builder')
        current = row.get('after')
        verify_render_binding(current, f'{view} after', models['current']['sha256'], camera, key, 'builder')
        comparison_by_view[view] = row
    if set(comparison_by_view) != set(REQUIRED_VIEWS):
        raise ValueError('Comparison views must be front, side, rear, three-quarter, head, feet')

    configs = packet.get('eraConfigurations')
    if not isinstance(configs, list) or len(configs) != len(REQUIRED_ERAS):
        raise ValueError('Packet must supply one configuration image for each of three eras')
    config_by_era = {}
    for row in configs:
        era = row.get('era') if isinstance(row, dict) else None
        if era not in REQUIRED_ERAS or era in config_by_era:
            raise ValueError(f'Duplicate or unexpected era configuration: {era}')
        config_by_era[era] = row
        expected_render_era = 'builder' if era == 'advanced' else era
        if row.get('era') != era:
            raise ValueError(f'{era} configuration: displayed era identity mismatch')
        # The application calls the Advanced configuration "builder" in its render receipt.
        camera = row.get('camera')
        key = row.get('cameraKey')
        if key != camera_key(camera):
            raise ValueError(f'{era} configuration: camera key mismatch')
        verify_render_binding(row, f'{era} configuration', models['current']['sha256'], camera, key, expected_render_era)
        if not row.get('scope'):
            raise ValueError(f'{era} configuration is missing its scope note')

    optional_paths = {}
    motion = packet.get('motion') or {}
    if not isinstance(motion, dict):
        raise ValueError('motion must be an object when supplied')
    for kind in ('frozenFrames', 'videos', 'receipts'):
        rows = motion.get(kind, [])
        if not isinstance(rows, list):
            raise ValueError(f'motion.{kind} must be a list')
        optional_paths[kind] = []
        for index, row in enumerate(rows):
            path_value = verified_asset(row, f'motion.{kind}[{index}]', models['current']['sha256'])
            if not row.get('scope'):
                raise ValueError(f'motion.{kind}[{index}] is missing a bounded scope note')
            optional_paths[kind].append(path_value)
    return packet, {**model_paths, **{f'ref:{key}': value for key, value in reference_paths.items()}}, {
        **{f'comparison:{view}': row for view, row in comparison_by_view.items()},
        **{f'config:{era}': row for era, row in config_by_era.items()},
        **optional_paths,
    }


def build(packet_path: Path, replace: bool, output_file: Path = OUT_FILE) -> Path:
    output_file = output_file.resolve()
    if output_file.parent != OUT_DIR.resolve():
        raise ValueError(f'Gallery output must be directly inside {OUT_DIR}')
    packet, fixed_paths, data = load_packet(packet_path)
    current_sha = packet['models']['current']['sha256']
    baseline_sha = packet['models']['baseline']['sha256']
    parts = ['''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MurderBird · V5 regional review</title>
<style>
:root{color-scheme:light;--ink:#1c2422;--muted:#55615c;--paper:#f0efe9;--panel:#fffefa;--line:#ccd0c8;--accent:#805b2d}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}
main{max-width:1700px;margin:auto;padding:34px clamp(16px,3vw,48px) 72px}h1{font-size:clamp(2rem,4vw,3.5rem);line-height:1.08;margin:.3em 0}h2{margin:54px 0 8px;font-size:1.8rem}h3{font-size:1.15rem;margin:12px 0 4px}
p{max-width:100ch;color:var(--muted)}code{overflow-wrap:anywhere;font-size:.85em}.banner{background:#fff3d7;border-left:5px solid var(--accent);padding:16px 20px;margin:22px 0}.meta{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.meta section,.card{background:var(--panel);border:1px solid var(--line);padding:14px;min-width:0}
.comparison{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:18px 0 34px}.references{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.configs{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
figure{margin:0;background:var(--panel);border:1px solid var(--line);padding:8px;min-width:0}figure img{width:100%;height:auto;max-height:760px;object-fit:contain;display:block;background:#ddd}figcaption{font-size:.9rem;padding:8px 3px 2px;overflow-wrap:anywhere}figcaption small{display:block;color:var(--muted);margin-top:4px}.video{width:min(100%,1100px);background:#101414}.media-list{display:flex;gap:12px;flex-wrap:wrap}.hash{display:block;color:var(--muted);font:12px/1.5 ui-monospace,monospace;overflow-wrap:anywhere;margin:5px 0 14px}
@media(max-width:1000px){.comparison{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:650px){main{padding:18px 12px}.comparison,.references,.configs,.meta{grid-template-columns:1fr}}
</style><main>''']
    parts.append('<p>Local regional geometry comparison · packet status: <strong>revision required</strong></p>')
    parts.append('<h1>Regional form review</h1><div class="banner"><strong>Revision required.</strong> This gallery presents recorded source art, fixed-camera geometry comparisons, era configurations and bounded motion evidence. Images are displayed in their original proportions without crop or warp. It does not claim final likeness, dimensional reconstruction, collision clearance, acting acceptance or owner approval.</div>')
    parts.append('<div class="meta">')
    for key, title in [('baseline', 'Before · preserved source baseline'), ('current', 'After · current regional candidate')]:
        model = packet['models'][key]
        parts.append(f'<section><h3>{escape(title)}</h3><p>{file_link(fixed_paths[key], model["label"])} · SHA-256</p><code>{escape(model["sha256"])}</code></section>')
    parts.append('</div>')
    parts.append('<h2>Controlling image references</h2><p>Each source retains its declared scope. The July image controls head identity only; Candidate 03 is the selected common full-body reference, and Maker Clean is an era illustration.</p><div class="references">')
    for ref_id in REQUIRED_REFERENCES:
        row = next(item for item in packet['references'] if item['id'] == ref_id)
        image = fixed_paths[f'ref:{ref_id}']
        parts.append(image_card(image, row['label'], f'{ref_id} · {row["scope"]} · SHA-256 {row["sha256"]}'))
    parts.append('</div>')

    parts.append('<h2>Same-camera regional comparisons</h2><p>Each row is bound to a hashed views receipt. The builder rechecks the image path and bytes, receipt model identity, renderer, era, camera payload and recomputed camera key for both versions. This establishes camera provenance, not quantitative similarity; lighting and material differences remain.</p>')
    for view in REQUIRED_VIEWS:
        row = data[f'comparison:{view}']
        camera_label = json.dumps(row['camera'], sort_keys=True, separators=(',', ':'))
        parts.append(f'<h3>{escape(view.replace("-", " ").title())} · camera key {escape(row["cameraKey"])}</h3><p>Camera payload: <code>{escape(camera_label)}</code></p><div class="comparison">')
        entries = [('baseline', 'Before · source baseline'), ('after', 'After · combined current geometry')]
        for key, title in entries:
            item = row[key]
            path = verified_asset(item, f'{view}/{key}', baseline_sha if key == 'baseline' else current_sha)
            detail = (f'model SHA-256 {item["modelSha256"]} · {item["renderEra"]} render · '
                      f'renderer SHA-256 {item["rendererSha256"]} · '
                      f'views receipt SHA-256 {item["receipt"]["sha256"]}')
            parts.append(image_card(path, title, detail))
        parts.append('</div>')

    parts.append('<h2>Three era configurations</h2><p>These separate views identify the current era-specific surface/configuration presentation. Their packet scope notes govern what each image demonstrates.</p><div class="configs">')
    for era in REQUIRED_ERAS:
        row = data[f'config:{era}']
        path = verified_asset(row, f'{era} configuration', current_sha)
        parts.append(image_card(path, row['label'], row['scope']))
    parts.append('</div>')

    if packet.get('revisionComparisons'):
        parts.append('<h2>Review-driven refinement</h2><p>The prior regional candidate prompted another local shape correction: simpler instep crowns and flatter claw roots. These matched views preserve that comparison.</p>')
        for row in packet['revisionComparisons']:
            parts.append(f'<h3>{escape(row["label"])}</h3><div class="comparison">')
            for key, label in [('baseline', 'Previous regional candidate 02'), ('after', 'Current regional correction')]:
                item = row[key]
                parts.append(image_card(ROOT / item['path'], label, f'model SHA-256 {item["modelSha256"]}'))
            parts.append('</div>')

    motion = packet.get('motion') or {}
    parts.append('<h2>Bounded motion evidence</h2>')
    if not any(data[key] for key in ('frozenFrames', 'videos', 'receipts')):
        parts.append('<p class="banner">No frozen-motion frames, videos or receipts were supplied in this packet. Motion acceptance remains unassessed.</p>')
    else:
        scope = motion.get('scope', 'Scope was not supplied; no broader motion claim is made.')
        parts.append(f'<p>{escape(scope)}</p>')
        if data['frozenFrames']:
            parts.append('<div class="references">')
            for row, path in zip(motion['frozenFrames'], data['frozenFrames']):
                parts.append(image_card(path, row['label'], row['scope']))
            parts.append('</div>')
        if data['videos']:
            for row, path in zip(motion['videos'], data['videos']):
                if path.suffix.lower() in ('.mp4', '.webm'):
                    url = escape(rel_href(path), quote=True)
                    parts.append(f'<h3>{escape(row["label"])}</h3><video class="video" controls preload="metadata" src="{url}"></video><p>{escape(row["scope"])} · {file_link(path, "Original recorded file")}</p>')
                else:
                    parts.append(f'<p>{file_link(path, row["label"])} · {escape(row["scope"])}</p>')
        if data['receipts']:
            parts.append('<h3>Motion receipts</h3><ul>')
            for row, path in zip(motion['receipts'], data['receipts']):
                parts.append(f'<li>{file_link(path, row["label"])} · {escape(row["scope"])}</li>')
            parts.append('</ul>')
    parts.append('<h2>Provenance and limits</h2><p>Current model SHA-256: <code>' + escape(current_sha) + '</code>. Baseline model SHA-256: <code>' + escape(baseline_sha) + '</code>.</p>')
    for note in packet.get('limits', []):
        parts.append('<p>' + escape(str(note)) + '</p>')
    parts.append('<p>Creative material remains rights reserved under NOTICE.md. This local gallery is not publication or owner acceptance.</p></main></html>')

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if output_file.exists() and not replace:
        raise FileExistsError(f'Refusing to overwrite existing gallery: {output_file}; pass --replace after review')
    html = '\n'.join(parts) + '\n'
    if replace:
        temp = output_file.with_suffix(output_file.suffix + '.tmp')
        temp.write_text(html)
        temp.replace(output_file)
    else:
        with output_file.open('x', encoding='utf8') as stream:
            stream.write(html)
    return output_file


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--packet', required=True, type=Path, help='Supplied regional review packet JSON')
    parser.add_argument('--output', type=Path, default=OUT_FILE, help='New gallery filename directly inside the regional audit directory')
    parser.add_argument('--replace', action='store_true', help='Explicitly replace the selected local gallery')
    args = parser.parse_args()
    packet_path = args.packet.expanduser().resolve()
    if not packet_path.is_file():
        raise FileNotFoundError(f'Review packet does not exist: {packet_path}')
    output_file = args.output if args.output.is_absolute() else OUT_DIR / args.output
    destination = build(packet_path, args.replace, output_file)
    print(destination)


if __name__ == '__main__':
    main()
