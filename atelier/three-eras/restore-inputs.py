"""Recover the private exhibit build inputs from the verified portable HTML."""
from argparse import ArgumentParser
from pathlib import Path
import base64
import hashlib
import json
import re
import shutil

parser = ArgumentParser(description=__doc__)
parser.add_argument("html", type=Path)
parser.add_argument("--loop", type=Path, help="Optional approved seamless-loop.flac companion")
args = parser.parse_args()
here = Path(__file__).resolve().parent
manifest = json.loads((here / "manifest.json").read_text())
html = args.html.read_bytes()
digest = lambda data: hashlib.sha256(data).hexdigest()
if len(html) != manifest["portable"]["bytes"] or digest(html) != manifest["portable"]["sha256"]:
    raise SystemExit("Portable file does not match this source revision")

assets = {}
asset_pattern = rb'<script type="application/octet-stream" data-asset="([\w.-]+)" data-type="[^"]+">([A-Za-z0-9+/=]+)</script>'
for key, block in re.findall(asset_pattern, html):
    assets.setdefault(key.decode(), bytearray()).extend(base64.b64decode(block, validate=True))
if set(assets) != set(manifest) - {"portable"}:
    raise SystemExit("Embedded asset list differs from the frozen manifest")

stage = {"concrete.jpg", "enamel.jpg", "oak.jpg", "phosphor.png", "plaster.jpg", "standing-contact.png"}
maps = {"stand-albedo.jpg", "floor-normal.jpg"}
for name, data in assets.items():
    if len(data) != manifest[name]["bytes"] or digest(data) != manifest[name]["sha256"]:
        raise SystemExit("Asset verification failed for " + name)
for name, data in assets.items():
    parent = here / "src" / "stage-assets" if name in stage else here / "src" / "maps" if name in maps else here / "assets"
    parent.mkdir(parents=True, exist_ok=True)
    (parent / name).write_bytes(data)
print("Restored", len(assets), "verified embedded build inputs.")

companion = args.loop or (args.html.resolve().parent / "Audio" / "seamless-loop.flac")
if args.loop or companion.is_file():
    loop_hash = "d9bc121c0c2f1a04ff8456b8aeea1ae6d48fdc1777119ef4823bebc458425a72"
    if companion.stat().st_size != 30880257 or digest(companion.read_bytes()) != loop_hash:
        raise SystemExit("The companion file differs from the approved lossless recording.")
    target = here / "assets" / "seamless-loop.flac"
    if companion.resolve() != target.resolve():
        shutil.copyfile(companion, target)
    print("Restored the verified lossless companion for both hosted loop segments.")
