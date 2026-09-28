#!/usr/bin/env python3
"""Build a local, hash-bound review gallery for the active alignment-v6 candidate."""
from __future__ import annotations

import hashlib
import html
import json
import os
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "assets/audit/alignment-v6"
MODELS = ROOT / "assets/models/uncaged-alignment-v6"
STATUS_PATH = AUDIT / "review-status.json"
OUT = AUDIT / "index.html"
MANIFEST_OUT = AUDIT / "gallery-manifest.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path: Path, expected: str | None = None, expected_bytes: int | None = None) -> dict:
    if not path.is_file():
        raise FileNotFoundError(path)
    actual = digest(path)
    if expected and actual != expected:
        raise ValueError(f"Hash mismatch for {path}: {actual} != {expected}")
    if expected_bytes is not None and path.stat().st_size != expected_bytes:
        raise ValueError(f"Byte-count mismatch for {path}: {path.stat().st_size} != {expected_bytes}")
    return {"path": Path(os.path.relpath(path, AUDIT)).as_posix(),
            "bytes": path.stat().st_size, "sha256": actual}


def repo_path(path: str) -> Path:
    candidate = (ROOT / path).resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ValueError(f"Evidence path escapes repository: {path}") from exc
    return candidate


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as f:
        tmp = Path(f.name)
        f.write(content)
    os.replace(tmp, path)


def preserve_previous_outputs() -> dict | None:
    existing = [p for p in (OUT, MANIFEST_OUT) if p.exists()]
    if not existing:
        return None
    hashes = {p.name: digest(p) for p in existing}
    archive_id = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()[:16]
    archive = AUDIT / "gallery-history" / archive_id
    archive.mkdir(parents=True, exist_ok=True)
    for path in existing:
        target = archive / path.name
        if target.exists() and digest(target) != hashes[path.name]:
            raise ValueError(f"Existing gallery history conflicts at {target}")
        if not target.exists():
            shutil.copy2(path, target)
    return {"directory": archive.relative_to(ROOT).as_posix(), "sha256ByFile": hashes}


def image_card(path: Path, title: str, detail: str, expected: str | None = None) -> tuple[str, dict]:
    rec = record(path, expected)
    markup = (
        '<figure class="card">'
        f'<a href="{esc(rec["path"])}"><img loading="lazy" src="{esc(rec["path"])}" alt="{esc(title)}"></a>'
        f'<figcaption><strong>{esc(title)}</strong><small>{esc(detail)} · SHA-256 {rec["sha256"]}</small></figcaption>'
        '</figure>'
    )
    return markup, rec


def cropped_reference_card(path: Path, title: str, detail: str, expected: str) -> tuple[str, dict]:
    """Display a head-only SVG viewport while preserving and linking the original image."""
    rec = record(path, expected)
    markup = (
        '<figure class="card">'
        f'<a href="{esc(rec["path"])}" aria-label="Open full original reference image">'
        '<svg class="crop-window" viewBox="510 20 500 490" role="img" '
        f'aria-label="{esc(title)}; cropped viewport of the full source image">'
        f'<image href="{esc(rec["path"])}" x="0" y="0" width="1024" height="1536" preserveAspectRatio="none"></image>'
        '</svg></a>'
        f'<figcaption><strong>{esc(title)}</strong><small>{esc(detail)} · head-only display crop; open image for the full original · SHA-256 {rec["sha256"]}</small></figcaption>'
        '</figure>'
    )
    return markup, rec


def section(title: str, note: str, cards: list[str], section_id: str, grid_class: str = "grid") -> str:
    return (f'<section id="{esc(section_id)}"><h2>{esc(title)}</h2><p>{note}</p>'
            f'<div class="{grid_class}">{"".join(cards)}</div></section>')


def main() -> None:
    inventory_path = MODELS / "alignment-inventory.json"
    native_path = MODELS / "murderbird-alignment-v6.blend"
    glb_path = MODELS / "murderbird-alignment-v6.glb"
    inventory = read_json(inventory_path)
    rows = read_json(AUDIT / "authoring-views.json")
    old_rows = read_json(AUDIT / "v5-comparison/authoring-views.json")
    status = read_json(STATUS_PATH)
    candidate = status["activeCandidate"]
    model_hash = digest(glb_path)
    native_hash = digest(native_path)
    if model_hash != candidate["sha256"]:
        raise ValueError("Review status candidate hash does not match the active GLB; update review-status.json first")
    if inventory.get("generatedFiles") is None:
        raise ValueError("Inventory lacks generated-file identities")
    generated = {entry["path"]: entry for entry in inventory["generatedFiles"]}
    for path, actual in ((glb_path, model_hash), (native_path, native_hash)):
        relpath = path.relative_to(ROOT).as_posix()
        if generated.get(relpath, {}).get("sha256") != actual:
            raise ValueError(f"Inventory identity does not match {relpath}")
    by_name = {row["image"]: row for row in rows}
    older_by_name = {row["image"]: row for row in old_rows}
    if not rows or any(row.get("modelSha256") != model_hash for row in rows):
        raise ValueError("Current authoring-view manifest is not consistently bound to the active GLB")
    source_hash = rows[0].get("sourceSha256")
    source_row = next((source for source in rows[0].get("generatorSources", [])
                       if source.get("path") == native_path.relative_to(ROOT).as_posix()), None)
    if not source_row or source_row.get("sha256") != native_hash or source_hash != native_hash:
        raise ValueError("Authoring renders do not bind to the active native BLEND")

    manifest = {
        "status": "local work-in-progress review; not approval, deployment, or full acceptance",
        "candidate": {"label": candidate["label"], "iteration": candidate["iteration"],
                      "model": record(glb_path, model_hash), "native": record(native_path, native_hash),
                      "sourceSha256": source_hash, "inventory": record(inventory_path)},
        "applicationStatus": status["applicationNote"],
        "history": None,
        "comparisonCameraChecks": [],
        "evidence": [],
        "knownResults": [],
    }
    cards: list[str] = []

    # Reference artwork is displayed at its declared scope, never as metrology.
    refs = {item["id"]: item for item in inventory["sourceReferences"]["sources"]}
    scoped_cards: list[str] = []
    for ref_id, view_name, title, scope_note in [
        ("july-head", "alignment-head.png", "July owner-selected image · head-only scope",
         "Only head identity is in scope; this image does not set body or wing proportions."),
        ("candidate-03", "alignment-three-quarter.png", "Candidate 03 · common-body direction",
         "Selected full-body illustration guides common body direction; perspective is not dimensional metrology."),
    ]:
        ref = refs[ref_id]
        ref_path = ROOT / ref["path"]
        if ref_id == "july-head":
            c_ref, r_ref = cropped_reference_card(ref_path, title, scope_note, ref["sha256"])
        else:
            c_ref, r_ref = image_card(ref_path, title, scope_note, ref["sha256"])
        view = by_name[view_name]
        c_model, r_model = image_card(AUDIT / view_name, f"Current {candidate['label']} · {view_name.removesuffix('.png')}",
                                      "Neutral authored view", view["sha256"])
        scoped_cards.extend((c_ref, c_model))
        manifest["evidence"].extend((r_ref, r_model))
    cards.append(section("Reference scope", "These source illustrations define review targets only. They do not provide exact dimensions, hidden topology, or final-art approval.", scoped_cards, "references", "pair-grid"))

    # Compare only when all recorded camera fields are identical.
    compare_names = ["alignment-head.png", "alignment-head-profile-left.png", "alignment-head-profile-right.png",
                     "alignment-three-quarter.png", "alignment-front.png", "alignment-side-right.png", "alignment-rear.png"]
    compare_cards: list[str] = []
    matched = []
    for name in compare_names:
        current, prior = by_name.get(name), older_by_name.get(name)
        if not current or not prior:
            continue
        fields = ("camera", "target", "projection", "orthoScale")
        exact = all(current.get(field) == prior.get(field) for field in fields)
        manifest["comparisonCameraChecks"].append({"image": name, "exactMatch": exact,
                                                     "fields": list(fields)})
        if not exact:
            continue
        c_prior, r_prior = image_card(AUDIT / "v5-comparison" / name, f"V5 · {name.removesuffix('.png')}",
                                      "Camera, target, projection, and scale match", prior["sha256"])
        c_current, r_current = image_card(AUDIT / name, f"V6 · {name.removesuffix('.png')}",
                                          "Same recorded camera as v5", current["sha256"])
        compare_cards.extend((c_prior, c_current))
        manifest["evidence"].extend((r_prior, r_current))
        matched.append(name)
    cards.append(section("Matched v5 / current v6 views", "Each pair is included only when both manifests have identical camera, target, projection, and orthographic scale. This supports visual comparison; it does not transfer v5 app or motion evidence to v6.", compare_cards, "comparison", "pair-grid"))
    manifest["sameCameraImages"] = matched

    # Candidate-specific images not already shown on matched comparison pairs.
    extra_names = ["alignment-head.png", "alignment-head-profile-left.png", "alignment-head-profile-right.png",
                   "alignment-three-quarter.png", "alignment-front.png", "alignment-side-right.png", "alignment-rear.png"]
    extra_cards: list[str] = []
    for name in extra_names:
        row = by_name[name]
        c, rec = image_card(AUDIT / name, name.removesuffix(".png").replace("-", " ").title(),
                            "Current neutral authoring render", row["sha256"])
        extra_cards.append(c)
        manifest["evidence"].append(rec)
    cards.append(section("Current neutral views", "Head three-quarter and bilateral profiles, plus full-body front, right side, three-quarter, and rear views. Images are hash-bound to the current native source and GLB.", extra_cards, "neutral-views"))

    # Browser captures and recordings are included only from the matching, hash-bound evidence manifest.
    browser_root = AUDIT / "browser-ce35024adda8"
    evidence_manifest_path = browser_root / "evidence-manifest.json"
    browser_evidence = read_json(evidence_manifest_path)
    browser_manifest_hash = digest(evidence_manifest_path)
    if browser_manifest_hash != status.get("browserEvidenceManifestSha256"):
        raise ValueError("Browser evidence manifest changed; review its new identity before gallery generation")
    if browser_evidence.get("model", {}).get("sha256") != model_hash:
        raise ValueError("Browser evidence manifest is not bound to the active model")
    if len(browser_evidence.get("captures", [])) != 17 or len(browser_evidence.get("recordings", [])) != 4:
        raise ValueError("Unexpected browser evidence inventory; review it before including captures")
    browser_manifest_rec = record(evidence_manifest_path)
    manifest["browserEvidence"] = {"manifest": browser_manifest_rec, "modelSha256": model_hash,
                                   "captures": [], "recordings": [], "analysis": []}
    browser_record_info = browser_evidence.get("browserRecord", {})
    browser_record_path = repo_path(browser_record_info["path"])
    browser_record = read_json(browser_record_path)
    if browser_record.get("modelSha256") != model_hash:
        raise ValueError("Browser review record is not bound to the active model")
    browser_record_rec = record(browser_record_path, browser_record_info["sha256"])
    manifest["browserEvidence"]["browserRecord"] = browser_record_rec

    browser_cards: list[str] = []
    fallback_cards: list[str] = []
    required_capture_names = {
        "advanced-paused-exhibit", "maker-head-neutral", "maker-open", "maker-exploded", "maker-reassembled",
        "mechanic-head-exhibit", "mechanic-open", "mechanic-exploded", "mechanic-reassembled",
        "advanced-head-neutral", "advanced-head-exhibit", "advanced-open", "advanced-exploded", "advanced-reassembled",
        "fallback-maker", "fallback-mechanic", "fallback-builder",
    }
    capture_names = {item["name"] for item in browser_evidence["captures"]}
    if not required_capture_names.issubset(capture_names):
        raise ValueError(f"Browser evidence is missing required captures: {sorted(required_capture_names-capture_names)}")
    for item in browser_evidence["captures"]:
        p = repo_path(item["path"])
        rec = record(p, item["sha256"], item["bytes"])
        manifest["evidence"].append(rec)
        capture_meta = {k: item.get(k) for k in ("name", "era", "kind", "open", "separation", "light", "loaded", "source") if k in item}
        manifest["browserEvidence"]["captures"].append({**capture_meta, "file": rec})
        if item["name"].startswith("fallback-"):
            detail = f"Illustrated fallback · {item.get('era')} · loaded={item.get('loaded')}"
            card, _ = image_card(p, item["name"].replace("-", " ").title(), detail, item["sha256"])
            fallback_cards.append(card)
        else:
            detail = (f"Browser {item.get('kind')} capture · era={item.get('era')} · light={item.get('light')} · "
                      f"open={item.get('open')} · separation={item.get('separation')}")
            card, _ = image_card(p, item["name"].replace("-", " ").title(), detail, item["sha256"])
            browser_cards.append(card)
    if len(browser_cards) != 14 or len(fallback_cards) != 3:
        raise ValueError("Browser capture categories do not match the declared 14 WebGL / 3 fallback rows")
    maker_preview = record(MODELS / "maker-preview.png")
    mechanic_preview = record(MODELS / "mechanic-preview.png")
    if maker_preview["sha256"] != mechanic_preview["sha256"]:
        raise ValueError("Maker and Mechanic fallback preview files changed; refresh the explicit fallback caveat")
    manifest["browserEvidence"]["previewInputs"] = [maker_preview, mechanic_preview,
                                                   record(MODELS / "builder-preview.png")]
    manifest["evidence"].extend((maker_preview, mechanic_preview, manifest["browserEvidence"]["previewInputs"][2]))
    browser_source_links = (
        f'Browser record: <a href="{esc(browser_record_rec["path"])}">browser-review.json</a> · '
        f'evidence: <a href="{esc(browser_manifest_rec["path"])}">evidence-manifest.json</a>.')
    cards.append(section("Browser views · WebGL", "Hash-verified browser screenshots for neutral head views, the exhibit lighting, and each era’s open, exploded, and reassembled states. Static captures are states, not motion-review substitutes. " + browser_source_links, browser_cards, "browser-views"))
    cards.append(section("Illustrated fallback", "These three loaded fallback captures show the illustrated path. Maker and Mechanic fallback source images are byte-identical (SHA-256 " + maker_preview["sha256"] + "); this is not evidence of visible era differentiation.", fallback_cards, "browser-fallback"))

    analysis_manifest_path = browser_root / "analysis/analysis-manifest.json"
    analysis_manifest = read_json(analysis_manifest_path)
    if analysis_manifest.get("modelSha256") != model_hash:
        raise ValueError("Two-run analysis manifest is not bound to the active model")
    analysis_manifest_rec = record(analysis_manifest_path)
    manifest["evidence"].append(analysis_manifest_rec)
    analysis_verified = []
    for item in analysis_manifest.get("sources", []) + analysis_manifest.get("analysisArtifacts", []):
        expected_bytes = item.get("bytes")
        rec = record(repo_path(item["path"]), item["sha256"], expected_bytes)
        analysis_verified.append(rec)
        manifest["evidence"].append(rec)
    manifest["browserEvidence"]["analysis"] = [{"manifest": analysis_manifest_rec, "verifiedFiles": analysis_verified}]
    analysis_by_basename = {Path(item["path"]).name: item for item in analysis_verified}
    analysis_links = []
    for filename, title in [
        ("autonomy-default-927-analysis-v3.json", "Default-seed run analysis"),
        ("autonomy-seed-20260928-analysis-v3.json", "Explicit review-seed run analysis"),
        ("autonomy-comparison-v2.json", "Two-run comparison result"),
    ]:
        item = analysis_by_basename[filename]
        analysis_links.append(f'<li><a href="{esc(item["path"])}">{esc(title)}</a> · SHA-256 {item["sha256"]}</li>')
    cards.append(section("Two-run analysis", "The captures cover two runs only: production default seed 927 and an explicit DEV review seed 20260928. The comparison package declares that it does not establish visitor-seed randomization, artistic acceptance, or continuous human review.",
                         [f'<article class="result"><p><a href="{esc(analysis_manifest_rec["path"])}">analysis/analysis-manifest.json</a> · SHA-256 {analysis_manifest_rec["sha256"]}</p><ul>{"".join(analysis_links)}</ul></article>'],
                         "two-run-analysis", "result-grid"))

    recording_cards = []
    expected_runs = {
        "autonomy-default-927": ("default-seed-927", 120.0, "No-input recording · application default seed 927"),
        "autonomy-seed-20260928": ("review-seed-20260928", 120.0, "No-input recording · explicit DEV review seed 20260928"),
        "motion-envelope-normal-speed": ("scripted-motion-envelope", 85.967, "Scripted UI sequence · normal-clock motion envelope"),
        "visitor-strike-normal-speed": ("visitor-strike-confirmed-contact", 9.876533, "Separate visitor-strike sequence · confirmed contact then retreat"),
    }
    recording_by_name = {row["name"]: row for row in browser_evidence["recordings"]}
    if set(recording_by_name) != set(expected_runs):
        raise ValueError("Browser recording names differ from the reviewed, supported set")
    for name, (expected_run, expected_duration, label) in expected_runs.items():
        row = recording_by_name[name]
        files = {Path(f["path"]).suffix.lower().lstrip("."): f for f in row["files"]}
        if not {"json", "webm", "mp4"}.issubset(files):
            raise ValueError(f"Recording {name} lacks JSON, original WebM, or MP4")
        verified = {ext: record(repo_path(item["path"]), item["sha256"], item["bytes"])
                    for ext, item in files.items()}
        data = read_json(repo_path(files["json"]["path"]))
        if data.get("declaredSha256") != model_hash or data.get("run") != expected_run:
            raise ValueError(f"Recording telemetry identity mismatch for {name}")
        if not data.get("complete") or data.get("hiddenSamples") != 0:
            raise ValueError(f"Recording is incomplete or contains hidden samples: {name}")
        measured_duration = float(row["probe"]["format"]["duration"])
        if abs(measured_duration - expected_duration) > 0.001:
            raise ValueError(f"Unexpected duration for {name}: {measured_duration}")
        if name.startswith("autonomy-") and "no accelerated step or user controls" not in data.get("clock", ""):
            raise ValueError(f"Autonomy recording clock/control scope is unexpected: {name}")
        if name in {"motion-envelope-normal-speed", "visitor-strike-normal-speed"} and not data.get("sequenceComplete"):
            raise ValueError(f"Scripted recording does not mark complete: {name}")
        if name == "visitor-strike-normal-speed":
            events = {event.get("name"): event.get("seconds") for event in data.get("events", [])}
            event_times = (("actual bill contact", 4.6817), ("entered strike recovery", 4.8643),
                           ("visitor retreat after contact", 4.8644), ("sequence complete", 9.8678))
            if any(name not in events or abs(float(events[name]) - target) > 0.02 for name, target in event_times):
                raise ValueError("Visitor-strike telemetry lacks the expected actual contact/recovery/retreat sequence")
        if row.get("complete") is not True or row.get("hiddenSamples") != 0:
            raise ValueError(f"Evidence manifest completion/hidden-sample check failed: {name}")
        if name in {"motion-envelope-normal-speed", "visitor-strike-normal-speed"} and row.get("sequenceComplete") is not True:
            raise ValueError(f"Evidence manifest does not confirm scripted sequence completion: {name}")
        manifest["browserEvidence"]["recordings"].append({"name": name, "run": expected_run,
            "durationSeconds": measured_duration, "hiddenSamples": 0,
            "sequenceComplete": row.get("sequenceComplete"), "files": verified,
            "scope": row.get("scope")})
        manifest["evidence"].extend(verified.values())
        mp4, webm, source_json = verified["mp4"], verified["webm"], verified["json"]
        analysis_item = analysis_by_basename.get(name + "-analysis-v3.json")
        analysis_link = (f'<a href="{esc(analysis_item["path"])}">run analysis</a> · ' if analysis_item else "")
        card_html = (
            '<article class="recording"><h3>' + esc(label) + '</h3>'
            f'<p>{measured_duration:.3f} seconds · normal application clock · hidden samples 0. '
            + ("Complete scripted UI sequence with condition waits. The longer envelope has visitor warning/retreat but no confirmed strike; see the separate contact recording." if name == "motion-envelope-normal-speed"
               else "Confirmed bill contact at 4.6817s, recovery at 4.8643s, then retreat; complete scripted UI sequence with condition waits." if name == "visitor-strike-normal-speed"
               else "No controls or input during recording; capture complete.")
            + '</p><video controls preload="metadata"><source src="' + esc(mp4["path"]) + '" type="video/mp4">'
            '<source src="' + esc(webm["path"]) + '" type="video/webm"></video>'
            f'<p><a href="{esc(mp4["path"])}">MP4 · SHA-256 {mp4["sha256"]}</a><br>'
            f'<a href="{esc(webm["path"])}">Original WebM · SHA-256 {webm["sha256"]}</a><br>'
            f'<a href="{esc(source_json["path"])}">Source JSON telemetry · SHA-256 {source_json["sha256"]}</a><br>{analysis_link}'
            f'<a href="{esc(analysis_manifest_rec["path"])}">Analysis manifest</a></p></article>')
        recording_cards.append(card_html)
    cards.append(section("Normal-clock recordings", "MP4 is listed first for duration and seeking; each is linked alongside its original WebM and source JSON. Two no-input captures last 120 seconds (default 927 and explicit DEV review seed 20260928). The 85.967-second envelope includes visitor warning/retreat but no confirmed strike. The separate 9.877-second sequence records actual contact, recovery, and only then retreat. These bounded runs are not continuous human review or proof of randomized visitor behavior.", recording_cards, "recordings", "result-grid"))

    frame_manifest_info = browser_evidence.get("frameProvenance", {})
    if not frame_manifest_info:
        raise ValueError("Browser evidence manifest lacks extracted-frame provenance")
    frame_manifest_path = repo_path(frame_manifest_info["path"])
    frame_manifest_rec = record(frame_manifest_path, frame_manifest_info["sha256"], frame_manifest_info["bytes"])
    frame_rows = read_json(frame_manifest_path)
    expected_frames = {"jump-apex.png", "shield-thrust.png", "claw-contact.png", "visitor-strike-contact.png"}
    if {row["image"] for row in frame_rows} != expected_frames:
        raise ValueError("Extracted-frame evidence set is incomplete or unexpected")
    frame_cards = []
    frame_details = {
        "jump-apex.png": "Jump airborne · 50.312s of the motion-envelope recording",
        "shield-thrust.png": "Shield-thrust brace · 52.812s of the motion-envelope recording",
        "claw-contact.png": "Claw scrape contact · 54.813s of the motion-envelope recording",
        "visitor-strike-contact.png": "Visitor-strike contact · 4.700s of the separate confirmed-contact recording",
    }
    video_rows = {item["name"]: {Path(f["path"]).name: f for f in item["files"]}
                  for item in browser_evidence["recordings"]}
    frame_records = []
    for row in frame_rows:
        source_video = video_rows.get(Path(row["video"]).stem, {}).get(row["video"])
        if not source_video or source_video["sha256"] != row.get("videoSha256"):
            raise ValueError(f"Frame provenance does not match its source video: {row['image']}")
        p = browser_root / row["image"]
        rec = record(p, row["sha256"])
        frame_records.append({"image": row["image"], "seconds": row["seconds"], "video": row["video"],
                              "videoSha256": row["videoSha256"], "file": rec})
        manifest["evidence"].append(rec)
        frame_cards.append(f'<figure class="card"><a href="{esc(rec["path"])}"><img loading="lazy" src="{esc(rec["path"])}" alt="{esc(frame_details[row["image"]])}"></a>'
                           f'<figcaption><strong>{esc(row["image"].removesuffix(".png").replace("-", " ").title())}</strong>'
                           f'<small>{esc(frame_details[row["image"]])} · linked video: {esc(row["video"])} · SHA-256 {rec["sha256"]}</small></figcaption></figure>')
    manifest["browserEvidence"]["frameProvenance"] = {"manifest": frame_manifest_rec, "frames": frame_records}
    manifest["evidence"].append(frame_manifest_rec)
    manifest["referenceCrops"] = [{"source": refs["july-head"]["path"], "sha256": refs["july-head"]["sha256"],
                                    "sourceDimensions": [1024, 1536], "viewBox": [510, 20, 500, 490],
                                    "scope": "display-only head crop; linked full original retained"}]
    cards.append(section("Motion keyframes", "Four stills extracted from the hash-bound normal-clock MP4s. The visitor contact still belongs to its separate contact-and-recovery clip, not the longer warning/retreat envelope.", frame_cards, "motion-keyframes"))

    result_cards = []
    for item in status["knownResults"]:
        receipt_path = ROOT / item["receipt"]
        try:
            receipt_path.relative_to(ROOT)
        except ValueError as exc:
            raise ValueError("Receipt path must remain inside the repository") from exc
        receipt = read_json(receipt_path)
        receipt_model = receipt.get("model")
        actual_receipt_model = ((receipt_model.get("sha256") if isinstance(receipt_model, dict) else None)
                                or receipt.get("sha256") or receipt.get("modelSha256")
                                or receipt.get("declaredModel", {}).get("sha256"))
        if actual_receipt_model != item["modelSha256"]:
            raise ValueError(f"Status result model hash does not match its receipt: {item['receipt']}")
        receipt_rec = record(receipt_path)
        manifest["knownResults"].append({**item, "receiptEvidence": receipt_rec})
        result_cards.append(f'<article class="result"><h3>{esc(item["label"])}</h3><p>{esc(item["note"])}</p>'
                            f'<p><a href="{esc(receipt_rec["path"])}">Hash-bound receipt</a> · model SHA-256 {esc(item["modelSha256"])}</p></article>')
    cards.append(section("Known bounded checks and open status", "Results below are tied to their own candidate hashes. A zero crossing count is limited to the declared diagnostic scope; it is not a complete clearance or artistic pass.", result_cards, "results", "result-grid"))

    motion_json = ROOT / "assets/audit/alignment-v6/browser-ce35024adda8/analysis/motion-envelope-review.json"
    motion_md = motion_json.with_suffix(".md")
    motion_data = read_json(motion_json)
    if motion_data["model"]["declared_sha256"] != model_hash:
        raise ValueError("Motion readout model does not match active candidate")
    motion_records = [record(motion_json), record(motion_md)]
    manifest["evidence"].extend(motion_records)
    manifest["motionReadout"] = motion_records
    cards.append(f'<section id="motion-readout"><h2>Sampled motion readout</h2><p>The five Maker channels move and return near rest; the Mechanic turns and settles after stopping; Advanced jump, thrust, claw and separate strike have sampled outcomes. Each era opens, separates and reassembles. These are finite kinematic observations, not continuous collision or artistic acceptance.</p><p><a href="{esc(motion_records[1]["path"])}">Read findings and limits</a> · <a href="{esc(motion_records[0]["path"])}">Hash-bound measurements</a></p></section>')

    pending = "".join(f"<li>{esc(text)}</li>" for text in status["openArtDecisions"])
    history_notes = "".join(f"<li>{esc(text)}</li>" for text in status.get("historicalNotes", []))
    pending_checks = "".join(f"<li>{esc(text)}</li>" for text in status.get("pendingChecks", []))
    cards.append(f'<section id="open"><h2>Open art decisions and checks</h2><p>{esc(candidate["statusNote"])}</p><p>Earlier candidate dispositions:</p><ul>{history_notes}</ul><p>Pending checks:</p><ul>{pending_checks}</ul><p>Art decisions:</p><ul>{pending}</ul>'
                 f'<p>{esc(status["applicationNote"])} See the <a href="../alignment-v5/index.html">previous v5 review gallery</a>; v5 recordings and browser evidence do not establish v6 behavior.</p>'
                 '<p>This gallery is a local review aid. It does not indicate owner acceptance, deployment, or that every declared check was run on the current candidate.</p></section>')

    manifest["history"] = preserve_previous_outputs()
    manifest["historicalNotes"] = status.get("historicalNotes", [])
    manifest["openArtDecisions"] = status.get("openArtDecisions", [])
    manifest["pendingChecks"] = status.get("pendingChecks", [])
    manifest["gallerySections"] = ["Reference scope", "Matched v5 / current v6 views", "Current neutral views", "Browser views · WebGL", "Illustrated fallback", "Two-run analysis", "Normal-clock recordings", "Motion keyframes", "Known bounded checks and open status", "Sampled motion readout", "Open art decisions and checks"]

    css = """
    :root{color-scheme:light;--ink:#151515;--muted:#5e5e5e;--line:#d0d0d0;--paper:#fff;--wash:#f4f4f4;--warn:#7b3700}
    *{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 system-ui,-apple-system,sans-serif}
    header,main{max-width:1200px;margin:auto;padding:24px}header{border-bottom:1px solid var(--line)}h1{font-size:clamp(1.8rem,4vw,3rem);margin:.2em 0}h2{margin:0 0 .3em;font-size:1.6rem}h3{font-size:1.1rem;margin:.2em 0}p{max-width:85ch;color:#333;overflow-wrap:anywhere}.status{background:#fff4e7;border:1px solid #d9a36d;border-left:6px solid var(--warn);padding:14px 18px;margin:18px 0}
    .facts{display:flex;flex-wrap:wrap;gap:10px}.facts a,.facts span{border:1px solid var(--line);padding:7px 10px;background:var(--wash);color:var(--ink);overflow-wrap:anywhere}
    section{padding:28px 0;border-bottom:1px solid var(--line)}.grid,.pair-grid,.result-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;align-items:start}.card{margin:0;border:1px solid var(--line);background:#fafafa}.card img{display:block;width:100%;height:auto;background:#f0f0f0}.crop-window{display:block;width:100%;height:auto;aspect-ratio:500/490;background:#f0f0f0}.recording video{display:block;width:100%;height:auto;background:#111}.card figcaption{padding:10px 12px;display:grid;gap:4px}.card small{color:var(--muted);overflow-wrap:anywhere}.result,.recording{min-width:0;overflow-wrap:anywhere;border:1px solid var(--line);padding:14px;background:var(--wash)}a{color:#123d69}code{overflow-wrap:anywhere}
    @media(max-width:700px){header,main{padding:16px}.grid,.pair-grid,.result-grid{grid-template-columns:minmax(0,1fr)}}
    """
    model_rec, native_rec = manifest["candidate"]["model"], manifest["candidate"]["native"]
    html_doc = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Alignment v6 local review</title><style>{css}</style></head><body>
    <header><p>Local artifact review · not a release page</p><h1>Alignment v6</h1><div class="status"><strong>{esc(status["phase"])}</strong><p>{esc(candidate["label"])} · iteration {esc(candidate["iteration"])} · exact model SHA-256 <code>{model_hash}</code></p><p>{esc(candidate["statusNote"])}</p></div>
    <div class="facts"><a href="{esc(model_rec['path'])}">Current GLB · {model_rec['bytes']:,} bytes</a><a href="{esc(native_rec['path'])}">Native BLEND · {native_rec['bytes']:,} bytes</a><a href="{esc(manifest['candidate']['inventory']['path'])}">Inventory</a><a href="../../../docs/alignment-v6-review.md">Current v6 review notes</a><a href="../../../docs/alignment-v5-review.md">Historical v5 review notes</a><a href="era-eligibility-audit.md">Frozen third-candidate era audit</a><span>Native source SHA-256 {native_hash}</span><span>{esc(status["applicationNote"])}</span></div></header>
    <main>{''.join(cards)}</main></body></html>'''.encode("utf-8")
    manifest["pageSha256"] = hashlib.sha256(html_doc).hexdigest()
    atomic_write(OUT, html_doc)
    atomic_write(MANIFEST_OUT, (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode())
    print(f"Wrote {OUT.relative_to(ROOT)} for {candidate['label']} {model_hash}")
    print(f"HTML SHA-256 {manifest['pageSha256']}; {len(manifest['evidence'])} hash-verified evidence files")


if __name__ == "__main__":
    main()
