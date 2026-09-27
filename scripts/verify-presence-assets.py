"""Validate the articulated presence-study GLB and its exact Vite build boundary."""
from __future__ import annotations

import hashlib
import json
import re
import struct
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "assets/models/uncaged-presence-study/murderbird-presence-study.glb"
BLEND = ROOT / "assets/models/uncaged-presence-study/murderbird-presence-study.blend"
OUT = ROOT / "assets/audit/uncaged-presence-review/asset-validation.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_glb(path: Path) -> tuple[dict, bytes]:
    data = path.read_bytes()
    assert data[:4] == b"glTF", "GLB is missing or an LFS pointer"
    assert not data.startswith(b"version https://git-lfs"), "GLB is an LFS pointer"
    magic, version, declared_size = struct.unpack_from("<III", data)
    assert magic == 0x46546C67 and version == 2 and declared_size == len(data), "Invalid GLB header/size"

    chunks = []
    offset = 12
    while offset < len(data):
        assert offset + 8 <= len(data), "Truncated GLB chunk header"
        length, kind = struct.unpack_from("<II", data, offset)
        offset += 8
        end = offset + length
        assert end <= len(data), "Truncated GLB chunk"
        chunks.append((kind, data[offset:end]))
        offset = end
    assert offset == len(data) and chunks and chunks[0][0] == 0x4E4F534A, "Missing leading JSON chunk"
    json_chunks = [chunk for kind, chunk in chunks if kind == 0x4E4F534A]
    bin_chunks = [chunk for kind, chunk in chunks if kind == 0x004E4942]
    assert len(json_chunks) == 1 and len(bin_chunks) <= 1, "Unexpected GLB JSON/BIN chunk count"
    gltf = json.loads(json_chunks[0].rstrip(b" \t\r\n\0"))
    assert not any(buffer.get("uri") for buffer in gltf.get("buffers", [])), "GLB has external buffers"
    assert not any(image.get("uri") for image in gltf.get("images", [])), "GLB has external images"
    if gltf.get("buffers"):
        assert len(bin_chunks) == 1, "Declared buffer has no binary chunk"
        assert gltf["buffers"][0]["byteLength"] <= len(bin_chunks[0]), "Binary chunk is shorter than declared buffer"
    assert all(accessor.get("count", 0) > 0 for accessor in gltf.get("accessors", [])), "Empty GLB accessor"
    return gltf, data


def build_allowlist() -> set[str]:
    fixed = {
        "audio/iron-verdict-v3/full-song.mp3",
        "audio/iron-verdict-v3/lyrics.txt",
        "audio/iron-verdict-v3/seamless-loop.flac",
        "brand-icon.svg",
        "browserconfig.xml",
        "favicon.svg",
        "icons/apple-touch-icon.png",
        "icons/favicon-32.png",
        "icons/icon-192.png",
        "icons/icon-512.png",
        "icons/icon-maskable-512.png",
        "icons/mstile-150.png",
        "index.html",
        "og-image.png",
        "robots.txt",
        "safari-pinned-tab.svg",
        "site.webmanifest",
        "sitemap.xml",
        "social-overlay.svg",
        "social-preview.png",
    }
    dynamic_patterns = [
        re.compile(r"assets/index-[A-Za-z0-9_-]+\.css"),
        re.compile(r"assets/index-[A-Za-z0-9_-]+\.js"),
        re.compile(r"assets/theme-player-[A-Za-z0-9_-]+\.css"),
        re.compile(r"assets/theme-player-[A-Za-z0-9_-]+\.js"),
        re.compile(r"assets/murderbird-presence-study-[A-Za-z0-9_-]+\.glb"),
        re.compile(r"assets/murderbird-unified-master-03-2026-09-06-960-[A-Za-z0-9_-]+\.webp"),
    ]
    files = sorted(path.relative_to(ROOT / "dist").as_posix() for path in (ROOT / "dist").rglob("*") if path.is_file())
    assert len(files) == 26, f"Expected exactly 26 runtime files, found {len(files)}"
    actual = set(files)
    assert fixed <= actual, f"Expected runtime files missing: {sorted(fixed - actual)}"
    dynamic = actual - fixed
    assert len(dynamic) == len(dynamic_patterns), f"Expected six hashed assets, found {sorted(dynamic)}"
    for pattern in dynamic_patterns:
        matches = [path for path in dynamic if pattern.fullmatch(path)]
        assert len(matches) == 1, f"Expected exactly one asset matching {pattern.pattern}, found {matches}"
    return actual


def main() -> None:
    assert MODEL.is_file() and BLEND.is_file(), "Presence-study source and GLB must both exist"
    gltf, glb_data = parse_glb(MODEL)
    blend_data = BLEND.read_bytes()
    assert len(blend_data) > 10_000 and not blend_data.startswith(b"version https://git-lfs"), "Blend is missing, too small, or an LFS pointer"

    nodes = gltf.get("nodes", [])
    names = [node.get("name") for node in nodes]
    assert all(names), "Every exported hierarchy node must be named"
    assert len(names) == len(set(names)), "Exported node names must be unique for the runtime contract"
    by_name = {node["name"]: i for i, node in enumerate(nodes)}
    prior = [
        "body", "neck", "head", "jaw", "breastplate", "cranial-cover", "winding-drive", "power-core",
        "processing", "industrial-repairs", "builder-optics", "left-mantle", "right-mantle",
        "left-wing-shield", "right-wing-shield",
    ]
    required = ["murderbird", *prior, "left-thigh", "left-shin", "left-foot", "left-toes",
                "right-thigh", "right-shin", "right-foot", "right-toes", "upper-bill"]
    missing = [name for name in required if name not in by_name]
    assert not missing, f"Missing required hierarchy nodes: {missing}"

    parents: dict[int, int] = {}
    for parent_index, node in enumerate(nodes):
        for child_index in node.get("children", []):
            assert child_index not in parents, f"Node has multiple parents: {names[child_index]}"
            parents[child_index] = parent_index

    def parent_name(name: str) -> str | None:
        parent = parents.get(by_name[name])
        return names[parent] if parent is not None else None

    expected_parent = {
        "body": "murderbird", "neck": "body", "head": "neck", "jaw": "head",
        "breastplate": "body", "cranial-cover": "head", "winding-drive": "body",
        "power-core": "body", "processing": "head", "industrial-repairs": "body",
        "builder-optics": "head", "left-mantle": "body", "right-mantle": "body",
        "left-wing-shield": "left-mantle", "right-wing-shield": "right-mantle",
    }
    for name, parent in expected_parent.items():
        assert parent_name(name) == parent, f"Expected hierarchy {parent} -> {name}"
    for side in ("left", "right"):
        chain = [f"{side}-thigh", f"{side}-shin", f"{side}-foot", f"{side}-toes"]
        assert parent_name(chain[0]) == "murderbird", f"{chain[0]} must be a root child, sibling to body"
        for parent, child in zip(chain, chain[1:]):
            assert parent_name(child) == parent, f"Expected hierarchy {parent} -> {child}"
    assert parent_name("upper-bill") == "head", "upper-bill must be a child of head"

    assert not gltf.get("skins"), "Presence study should use rigid meshes, not skinned deformation"
    animations = gltf.get("animations", [])
    assert len(animations) == 1 and animations[0].get("name") == "attention-export-proof", "Expected one attention-export-proof animation"
    animation_targets = []
    for channel in animations[0].get("channels", []):
        target = channel.get("target", {})
        node_index = target.get("node")
        if node_index is not None:
            assert 0 <= node_index < len(nodes), "Animation targets an invalid node"
            animation_targets.append((names[node_index], target.get("path")))
    assert ("head", "rotation") in animation_targets, "Proof clip must animate head rotation"
    for animation in animations:
        for channel in animation.get("channels", []):
            assert 0 <= channel.get("sampler", -1) < len(animation.get("samplers", [])), "Invalid animation sampler index"

    triangles = sum(
        gltf["accessors"][primitive["indices"]]["count"] // 3
        for mesh in gltf.get("meshes", [])
        for primitive in mesh.get("primitives", [])
        if "indices" in primitive
    )
    assert triangles > 0 and gltf.get("meshes"), "GLB contains no indexed mesh geometry"

    dist_root = ROOT / "dist"
    assert dist_root.is_dir(), "Run npm run build before verification"
    allowed = build_allowlist()
    files = sorted((dist_root / path) for path in allowed)
    for path in files:
        data = path.read_bytes()
        assert not data.startswith(b"version https://git-lfs"), f"LFS pointer in build: {path.relative_to(dist_root)}"
        assert path.suffix not in {".blend", ".py", ".md", ".zip", ".jsonl"}, f"Source/private artifact in build: {path.relative_to(dist_root)}"

    models = [path for path in files if path.suffix == ".glb"]
    assert len(models) == 1 and sha256(models[0]) == sha256(MODEL), "Built runtime GLB differs from the authoring export"
    built_names = {path.name for path in files}
    assert any(name.startswith("murderbird-presence-study-") and name.endswith(".glb") for name in built_names), "Presence GLB is not in the runtime build"
    assert not any("murderbird-shield-study" in name or "murderbird-study-" in name for name in built_names), "Stale study export leaked into the build"

    source_rel = MODEL.relative_to(ROOT).as_posix()
    blend_rel = BLEND.relative_to(ROOT).as_posix()
    report = {
        "status": "verified-local",
        "date": date.today().isoformat(),
        "validator": "scripts/verify-presence-assets.py",
        "model": {
            "path": source_rel,
            "bytes": len(glb_data),
            "sha256": sha256(MODEL),
            "nodes": len(nodes),
            "meshes": len(gltf.get("meshes", [])),
            "triangles": triangles,
            "requiredNodes": required,
            "legHierarchy": {
                side: [f"{side}-thigh", f"{side}-shin", f"{side}-foot", f"{side}-toes"]
                for side in ("left", "right")
            },
            "upperBillParent": "head",
            "skins": len(gltf.get("skins", [])),
            "animations": [{"name": animations[0]["name"], "targets": animation_targets}],
            "selfContained": True,
        },
        "editableSource": {"path": blend_rel, "bytes": len(blend_data), "sha256": sha256(BLEND)},
        "build": {
            "fileCount": len(files),
            "totalBytes": sum(path.stat().st_size for path in files),
            "files": [
                {"path": path.relative_to(dist_root).as_posix(), "bytes": path.stat().st_size, "sha256": sha256(path)}
                for path in files
            ],
            "modelMatchesSource": True,
            "exactAllowlist": True,
        },
        "limits": [
            "Validates local GLB structure, named rigid hierarchy, one proof animation, source-to-build identity, and the explicit runtime allowlist.",
            "Does not establish visual likeness, owner acceptance, physical balance/force, production animation quality, clean-clone asset availability, remote CI, or deployment behavior.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "status": report["status"],
        "modelBytes": len(glb_data),
        "meshes": len(gltf.get("meshes", [])),
        "triangles": triangles,
        "nodes": len(nodes),
        "buildFiles": len(files),
        "totalBuildBytes": report["build"]["totalBytes"],
        "sha256": report["model"]["sha256"],
        "receipt": OUT.relative_to(ROOT).as_posix(),
    }, indent=2))


if __name__ == "__main__":
    main()
