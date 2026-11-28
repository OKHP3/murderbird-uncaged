"""Compare a rebuilt exhibit with the release's original file identities."""
from argparse import ArgumentParser
from pathlib import Path
import hashlib
import json

parser = ArgumentParser(description=__doc__)
parser.add_argument("--full", action="store_true", help="Require both hosted FLAC segments")
args = parser.parse_args()
root = Path(__file__).resolve().parent
portable = "MurderBird-Three-Eras.html"
release = json.loads((root / "hosted-manifest.json").read_text())
expected = {portable: release["portable"]}
hosted = release["files"]
only_full = {"assets/loop-a.bin", "assets/loop-b.bin"}
present_segments = {name for name in only_full if (root / "web" / name).is_file()}
if present_segments and present_segments != only_full:
    raise SystemExit("Incomplete lossless loop: the hosted build must contain both verified segments.")
for name, entry in hosted.items():
    if args.full or name not in only_full or present_segments:
        expected["web/" + name] = entry
actual = {"web/" + f.relative_to(root / "web").as_posix() for f in (root / "web").rglob("*") if f.is_file()}
if actual != set(expected) - {portable}:
    raise SystemExit("Hosted file-list mismatch: " + str(set(expected) ^ (actual | {portable})))
for name, entry in expected.items():
    file = root / name
    if file.stat().st_size != entry["bytes"] or hashlib.sha256(file.read_bytes()).hexdigest() != entry["sha256"]:
        raise SystemExit("Frozen output mismatch: " + name)
print(f"Verified the portable HTML and {len(actual)} hosted files byte-for-byte.")
