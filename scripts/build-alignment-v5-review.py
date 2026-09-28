#!/usr/bin/env python3
"""Build a local review gallery for the hash-bound alignment-v5 candidate."""
from __future__ import annotations

import hashlib
import html
import json
import os
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "assets/audit/alignment-v5"
OUT = AUDIT / "index.html"
MANIFEST_OUT = AUDIT / "gallery-manifest.json"
MODEL_SHA = "1e7febcc03d9f8d1a644580c8422b124403cf4e5768aa01df747e3d9b6af9f1e"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return Path(os.path.relpath(path, AUDIT)).as_posix()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def record(path: Path, expected: str | None = None) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    actual = sha(path)
    if expected and actual != expected:
        raise ValueError(f"Hash mismatch: {path}: {actual} != {expected}")
    return {"path": rel(path), "bytes": path.stat().st_size, "sha256": actual}


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def image_card(path: Path, title: str, detail: str = "", expected: str | None = None,
               alt: str | None = None) -> tuple[str, dict]:
    rec = record(path, expected)
    label = f"SHA-256 {rec['sha256']}"
    if detail:
        label = f"{detail} · {label}"
    markup = (
        '<figure class="card">'
        f'<a href="{esc(rec["path"])}"><img loading="lazy" src="{esc(rec["path"])}" '
        f'alt="{esc(alt or title)}"></a>'
        f'<figcaption><strong>{esc(title)}</strong><small>{esc(label)}</small></figcaption>'
        '</figure>'
    )
    return markup, rec


def section(title: str, intro: str, cards: list[str], section_id: str) -> str:
    return (f'<section id="{esc(section_id)}"><h2>{esc(title)}</h2><p>{intro}</p>'
            f'<div class="grid">{"".join(cards)}</div></section>')


inventory = read_json(ROOT / "assets/models/uncaged-alignment-v5/alignment-inventory.json")
views = read_json(AUDIT / "authoring-views.json")
view_by_name = {row["image"]: row for row in views}
v4_views = read_json(ROOT / "assets/audit/alignment-v4/authoring-views.json")
v4_by_name = {row["image"]: row for row in v4_views}
browser_root = AUDIT / "browser-1e7febcc03d9"
browser = read_json(browser_root / "browser-review.json")
refs = {item["id"]: item for item in inventory["sourceReferences"]["sources"]}

glb = ROOT / "assets/models/uncaged-alignment-v5/murderbird-alignment-v5.glb"
if sha(glb) != MODEL_SHA or inventory["generatedFiles"][1]["sha256"] != MODEL_SHA:
    raise ValueError("Current GLB does not match the frozen gallery identity")
if not any(row.get("modelSha256") == MODEL_SHA for row in views):
    raise ValueError("Authoring-view manifest is not bound to the frozen GLB")

manifest = {
    "status": "local review gallery; not owner approval or deployment",
    "modelSha256": MODEL_SHA,
    "generatedAt": "generated locally; timestamp intentionally omitted for reproducibility",
    "gallery": [],
    "evidence": [],
}
body = []

# Same-camera comparison is allowed only when view names, camera, and target match.
comparison_names = ["alignment-three-quarter.png", "alignment-side-right.png",
                   "alignment-side-left.png", "alignment-front.png", "alignment-rear.png",
                   "alignment-head.png", "alignment-breast.png", "alignment-mantle.png"]
comparison_cards = []
for name in comparison_names:
    current, previous = view_by_name[name], v4_by_name[name]
    for field in ("camera", "target", "projection", "orthoScale"):
        if current.get(field) != previous.get(field):
            raise ValueError(f"Not a same-camera comparison: {name} field {field}")
    p5, p4 = AUDIT / name, ROOT / "assets/audit/alignment-v4" / name
    card5, rec5 = image_card(p5, f"V5 · {name.removesuffix('.png')}",
                             "Camera/target matched with v4", current["sha256"])
    card4, rec4 = image_card(p4, f"V4 · {name.removesuffix('.png')}",
                             "Camera/target matched with v5", previous["sha256"])
    comparison_cards.extend([card4, card5])
    manifest["evidence"].extend([rec4, rec5])
manifest["gallery"].append({"section": "Same-camera v4 / v5", "images": comparison_names})
body.append(section("Same-camera comparison: v4 → v5",
    "Each pair uses the same recorded camera, target, projection, and scale. Neutral authored renders support comparison; they do not establish artistic acceptance.",
    comparison_cards, "comparison"))

# Scope-limited references. July remains explicitly head-only; candidate 03 is shared neck/body direction.
scope_cards = []
for ref_id, view_name, title, note in [
    ("july-head", "alignment-head.png", "July reference · head only", "Selected owner reference; head identity scope only."),
    ("candidate-03", "alignment-three-quarter.png", "Candidate 03 · proposed common body direction", "Reference guides neck/body direction; no dimension metrology."),
]:
    source = ROOT / refs[ref_id]["path"]
    card_ref, rec_ref = image_card(source, title, note, refs[ref_id]["sha256"])
    card_model, rec_model = image_card(AUDIT / view_name,
        f"Current v5 · {view_name.removesuffix('.png')}", "Authored candidate view",
        view_by_name[view_name]["sha256"])
    scope_cards.extend([card_ref, card_model])
    manifest["evidence"].extend([rec_ref, rec_model])
manifest["gallery"].append({"section": "Scoped identity references", "sources": ["july-head", "candidate-03"]})
body.append(section("Reference scope",
    "The references are shown at their recorded scope. Perspective source art is not treated as exact art metrology.",
    scope_cards, "scope"))

# Per-era reference and corresponding current model presentation.
era_cards = []
era_rows = [
    ("Maker", "maker-clean", "maker-reference-perspective.png", "Newly made bronze treatment; dark optic; broad folded wing."),
    ("Mechanic", "mechanic", "mechanic-reference-perspective.png", "Inherited aged shell and visible industrial repair context."),
    ("Advanced", "sentinel", "builder-reference-perspective.png", "Advanced quiet-presence reference; separate heart image is chest-power inspection scope."),
    ("Advanced power inspection", "heart", "advanced-open-settled.png", "Heart reference constrains chest-power inspection context; this is an opened Builder-era browser pose, not a closed neutral still."),
]
for era, ref_id, view_name, note in era_rows:
    src = ROOT / refs[ref_id]["path"]
    c1, r1 = image_card(src, f"{era} reference · {ref_id}", note, refs[ref_id]["sha256"])
    if ref_id == "heart":
        c2, r2 = image_card(browser_root / view_name, f"Current v5 · {era} browser pose",
                            "Advanced/open settled · exact-state browser capture")
    else:
        c2, r2 = image_card(AUDIT / view_name, f"Current v5 · {era} neutral preview",
                            "Neutral model preview; not era-distinct appearance evidence",
                            view_by_name[view_name]["sha256"])
    era_cards.extend([c1, c2]); manifest["evidence"].extend([r1, r2])
manifest["gallery"].append({"section": "Era comparisons", "eras": ["Maker", "Mechanic", "Advanced"]})
body.append(section("Era references and current model views",
    "Maker, Mechanic, and Advanced references define pending era targets. The Advanced heart study is narrowly scoped to chest-power inspection. Maker and Mechanic neutral perspective-preview files are byte-identical; the current clay images do not demonstrate era-specific model appearance.",
    era_cards, "eras"))

# Exact neutral front/rear/bilateral sides and three-quarter camera views.
ortho_names = ["alignment-front.png", "alignment-rear.png", "alignment-side-left.png",
               "alignment-side-right.png", "alignment-three-quarter.png",
               "alignment-left-three-quarter.png", "alignment-elevated.png", "alignment-low.png"]
ortho_cards = []
for name in ortho_names:
    row = view_by_name[name]
    c, r = image_card(AUDIT / name, name.removesuffix(".png"), "Current neutral authoring render", row["sha256"])
    ortho_cards.append(c); manifest["evidence"].append(r)
manifest["gallery"].append({"section": "Neutral views", "images": ortho_names})
body.append(section("Front, rear, sides, and three-quarter views",
    "These views expose silhouette and coverage from fixed recorded cameras.", ortho_cards, "views"))

detail_cards = []
for name, title in [("alignment-head.png", "Head / orbital construction"),
                    ("alignment-breast.png", "Breast course coverage"),
                    ("alignment-mantle.png", "Mantle and wing cover"),
                    ("alignment-feet.png", "Inherited legs and feet")]:
    row = view_by_name[name]
    c, r = image_card(AUDIT / name, title, "Current neutral authoring render", row["sha256"])
    detail_cards.append(c); manifest["evidence"].append(r)
manifest["gallery"].append({"section": "Regional closeups", "images": ["alignment-head.png", "alignment-breast.png", "alignment-mantle.png", "alignment-feet.png"]})
body.append(section("Regional closeups",
    "The images show authored exterior geometry; hidden construction and material finish remain proposals.", detail_cards, "regions"))

# Select only completed meaningful poses; intentionally omit advanced-open and rejected/cropped artifacts.
browser_rows = {row["name"]: row for row in browser.get("poses", [])}
pose_names = ["maker-jaw", "maker-neck", "maker-wing", "maker-exploded", "maker-reassembled",
              "mechanic-release", "mechanic-stopped", "mechanic-exploded", "mechanic-reassembled",
              "advanced-contact-exhibit", "advanced-exploded", "advanced-reassembled", "advanced-jump", "advanced-thrust"]
pose_cards = []
for name in pose_names:
    row = browser_rows[name]
    p = browser_root / row["filename"]
    articulation = row.get("state", {}).get("motion", {}).get("actualArticulation", {})
    detail = f"Observed browser capture · {row.get('state', {}).get('era', '')} · articulation {json.dumps(articulation, sort_keys=True)}"
    c, r = image_card(p, name.replace("-", " ").title(), detail)
    pose_cards.append(c); manifest["evidence"].append(r)
for name in ["fallback-settled-maker.png", "fallback-settled-mechanic.png", "fallback-settled-builder.png"]:
    c, r = image_card(browser_root / name, name.removesuffix(".png").replace("-", " ").title(),
                      "Settled illustrated fallback capture")
    pose_cards.append(c); manifest["evidence"].append(r)
manifest["gallery"].append({"section": "Browser poses and fallback", "poses": pose_names,
                            "fallbacks": ["fallback-settled-maker.png", "fallback-settled-mechanic.png", "fallback-settled-builder.png"]})
body.append(section("Selected browser poses, exploded views, and fallback",
    "Bounded in-app captures of the local v5 QA build. Cropped/rejected captures and the premature Advanced-open image are excluded. These are not continuous human or animation acceptance.",
    pose_cards, "browser"))

# Embed the available actual-canvas captures and expose both source formats and telemetry.
motion_sections = []
for stem, title, caveat in [
    ("motion-normal-speed", "Main scheduled interaction capture",
     "115.008 seconds at normal application clock, silent, actual WebGL canvas. At 65 s claw-scrape, 78 s reach, and 88 s retreat dispatches were unavailable and failed. The separate claw capture documents claw-scrape only; reach and retreat remain unobserved in this recording set."),
    ("claw-normal-speed", "Supplementary claw-scrape capture",
     "20.004 seconds at normal application clock, silent, actual canvas; dispatch waited for the control to become enabled and records approach, lift, contact, scrape, release, and recovery."),
]:
    media_cards = []
    for ext in ("mp4", "webm"):
        media = browser_root / f"{stem}.{ext}"
        if media.is_file():
            rec = record(media)
            media_cards.append(f'<a href="{esc(rec["path"])}">{ext.upper()} · {rec["bytes"]} bytes · SHA-256 {rec["sha256"]}</a>')
            manifest["evidence"].append(rec)
    telemetry = browser_root / f"{stem}.json"
    telemetry_link = ""
    if telemetry.is_file():
        rec = record(telemetry)
        telemetry_link = f'<p><a href="{esc(rec["path"])}">Recorded telemetry JSON</a> · SHA-256 {rec["sha256"]}</p>'
        manifest["evidence"].append(rec)
    # Prefer MP4 for native duration and seeking; retain WebM as a download.
    primary = browser_root / f"{stem}.mp4"
    if not primary.is_file():
        primary = browser_root / f"{stem}.webm"
    video = ""
    if primary.is_file():
        rec = record(primary)
        video = f'<video controls preload="metadata" src="{esc(rec["path"])}"></video>'
    motion_sections.append(
        f'<article class="recording"><h3>{esc(title)}</h3><p>{esc(caveat)}</p>{video}'
        f'<p class="links">{" · ".join(media_cards)}</p>{telemetry_link}</article>')
if motion_sections:
    perf_note = ('<p>Performance note: the short rolling samples reported about 10 ms median and 11.2 ms p95 on Apple M4 Max, loopback, 856×648 canvas at DPR 1. This is not sustained desktop/mobile or thermal certification.</p>')
    body.append('<section id="motion"><h2>Normal-speed browser recordings</h2>' + "".join(motion_sections) + perf_note + '</section>')
    manifest["gallery"].append({"section": "Normal-speed recordings", "stems": ["motion-normal-speed", "claw-normal-speed"]})

links = [
    ("Open the local QA exhibit", "http://127.0.0.1:5183/"),
    ("Review notes", "../../../docs/alignment-v5-review.md"),
    ("Model inventory", "../../../assets/models/uncaged-alignment-v5/alignment-inventory.json"),
    ("Current v5 GLB", "../../../assets/models/uncaged-alignment-v5/murderbird-alignment-v5.glb"),
    ("Editable v5 Blender source", "../../../assets/models/uncaged-alignment-v5/murderbird-alignment-v5.blend"),
    ("v5 regional body source", "../../../scripts/alignment-v5-body.py"),
    ("v5 head source", "../../../scripts/alignment-v5-head.py"),
    ("v5 neck source", "../../../scripts/alignment-v5-neck.py"),
    ("v5 composer", "../../../scripts/build-uncaged-alignment-v5.py"),
    ("Asset validation", "asset-validation-1e7febcc03d9.json"),
    ("Rig run manifest", "rig-1e7febcc03d9/run-manifest.json"),
    ("Expanded jaw/neck receipt", "rig-1e7febcc03d9/jaw-neck-structure.json"),
    ("Jaw/head sweep receipt", "rig-1e7febcc03d9/jaw-head-sweep/jaw-sweep.json"),
    ("Build boundary receipt", "build-boundary-1e7febcc03d9.json"),
    ("Export fixture log", "export-contract-tests.log"),
    ("Browser evidence manifest", "browser-1e7febcc03d9/evidence-manifest.json"),
    ("Browser review record", "browser-1e7febcc03d9/browser-review.json"),
]
link_markup = "".join(f'<li><a href="{esc(url)}">{esc(label)}</a></li>' for label, url in links)
body.append(f"<section id='evidence'><h2>Evidence and review limits</h2><p>This checkpoint is revision-required across all eras. Technical checks are evidence for their exact model/source identities; they do not close artistic review.</p><ul class='links'>{link_markup}</ul><p><strong>Stage B remains pending.</strong> Review bill profile and mandible shell continuity, orbital integration, angular neck-layer decisions, mantle coverage, and inherited legs/feet. The main timed sequence missed claw, reach, and retreat dispatches; the supplementary recording fills only the claw sequence. This is not a full T01–T18 or continuous human acting review. Preserve the references' scopes: July head only; candidate 03 shared body/neck direction. No score is assigned.</p></section>")

page = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>MurderBird alignment v5 · local review</title>
<style>
:root{color-scheme:light;--ink:#20252a;--muted:#5d6871;--line:#d4d9dc;--paper:#f5f6f4;--card:#fff;--accent:#596b70}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}header,main,footer{max-width:1440px;margin:auto;padding:1.25rem 2rem}header{padding-top:2rem;border-bottom:1px solid var(--line)}h1{font-size:clamp(1.7rem,4vw,2.8rem);line-height:1.1;margin:.25rem 0 .75rem}h2{font-size:1.45rem;margin:0 0 .25rem}h3{font-size:1rem}p{max-width:90ch;margin:.35rem 0 1rem}.eyebrow,.hash,small{color:var(--muted)}.status{display:inline-block;padding:.2rem .6rem;border:1px solid #9ca9aa;border-radius:2rem;font-size:.84rem;font-weight:650}.facts{display:flex;gap:.6rem 1.5rem;flex-wrap:wrap;margin-top:1rem}.facts code{font-size:.82rem;overflow-wrap:anywhere}nav{display:flex;flex-wrap:wrap;gap:.5rem 1rem;padding:1rem 0}nav a,.links a{color:#314f57}section{padding:1.5rem 0 1.7rem;border-bottom:1px solid var(--line)}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,310px),1fr));gap:1rem;margin-top:1rem}#comparison .grid{grid-template-columns:repeat(2,minmax(0,1fr))}.card{margin:0;background:var(--card);border:1px solid var(--line);padding:.45rem}.card img{display:block;width:100%;height:auto;background:#e7e9e8}.card figcaption{padding:.55rem .35rem .3rem;display:grid;gap:.2rem}.card small{font-size:.72rem;overflow-wrap:anywhere}.links{display:flex;flex-wrap:wrap;gap:.5rem 1.5rem;padding-left:1.2rem}video{display:block;max-width:100%;background:#111}footer{font-size:.85rem;color:var(--muted)}@media(max-width:600px){header,main,footer{padding-left:1rem;padding-right:1rem}#comparison .grid{grid-template-columns:1fr}}
</style></head><body><header><div class="eyebrow">MurderBird · local authoring review</div><h1>Alignment v5</h1><p><span class="status">Revision required · all eras</span> Local neutral-geometry checkpoint. Not owner-approved or deployed. The browser capture set is bounded; technical checks do not close artistic review.</p><div class="facts"><div>GLB SHA-256 <code>''' + MODEL_SHA + '''</code></div><div>''' + str(glb.stat().st_size) + ''' bytes</div><div>''' + str(len(views)) + ''' hash-bound neutral renders</div></div><nav><a href="#comparison">v4 / v5</a><a href="#scope">Reference scope</a><a href="#eras">Eras</a><a href="#views">Neutral views</a><a href="#regions">Regions</a><a href="#browser">Browser captures</a><a href="#evidence">Open decisions</a></nav></header><main>''' + "\n".join(body) + '''</main><footer>Local QA gallery. Creative source images remain rights reserved; this page does not publish them or select them as runtime assets.</footer></body></html>'''

manifest["evidence"] = sorted({item["path"]: item for item in manifest["evidence"]}.values(), key=lambda item: item["path"])
manifest["htmlSha256"] = hashlib.sha256(page.encode("utf-8")).hexdigest()


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


# Preserve a previous generated gallery before replacing it on future runs.
if OUT.exists():
    previous = OUT.read_bytes()
    previous_hash = hashlib.sha256(previous).hexdigest()
    if previous_hash != manifest["htmlSha256"]:
        archive = AUDIT / "gallery-iterations" / previous_hash[:12]
        archive.mkdir(parents=True, exist_ok=True)
        archived_html = archive / "index.html"
        if archived_html.exists() and sha(archived_html) != previous_hash:
            raise ValueError(f"Existing gallery snapshot differs: {archived_html}")
        if not archived_html.exists():
            atomic_write(archived_html, previous)
        if MANIFEST_OUT.exists():
            archived_manifest = archive / "gallery-manifest.json"
            old_manifest = MANIFEST_OUT.read_bytes()
            if archived_manifest.exists() and sha(archived_manifest) != hashlib.sha256(old_manifest).hexdigest():
                raise ValueError(f"Existing gallery manifest snapshot differs: {archived_manifest}")
            if not archived_manifest.exists():
                atomic_write(archived_manifest, old_manifest)

atomic_write(OUT, page.encode("utf-8"))
atomic_write(MANIFEST_OUT, (json.dumps(manifest, indent=2) + "\n").encode("utf-8"))
print(f"Wrote {rel(OUT)} ({sha(OUT)})")
print(f"Wrote {rel(MANIFEST_OUT)} ({len(manifest['evidence'])} hash-verified media files)")
