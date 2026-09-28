"""Inspect and author a separate shoulder-root transition proposal.

All output is local review material. Never overwrite a historical native.
"""
from pathlib import Path
import hashlib
import json
import sys

import bpy

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'assets/models/uncaged-alignment-v9/murderbird-alignment-v9.blend'
SOURCE_SHA = '4d7568d1c2ba7cab716876f57a6c20cb6a788d4daeef1d5d34f85c1910ed2bbe'
AUDIT = ROOT / 'assets/audit/shoulder-root-transition-study-v1'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert digest(SOURCE) == SOURCE_SHA
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
bpy.context.scene.frame_set(1)
bpy.context.view_layer.update()
rows = []
for obj in bpy.data.objects:
    if obj.type == 'EMPTY' and ('mantle' in obj.name or obj.name in ('torso', 'breastplate', 'neck')):
        rows.append({'name': obj.name, 'type': 'pivot', 'position': list(obj.matrix_world.translation)})
    if obj.type != 'MESH' or obj.get('region') not in ('shoulder', 'breast', 'torso', 'back'):
        continue
    points = [obj.matrix_world @ v.co for v in obj.data.vertices]
    if not points:
        continue
    bounds = [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]
    if bounds[2][1] < 1.2:
        continue
    rows.append({'name': obj.name, 'type': 'mesh', 'owner': obj.parent.name,
                 'region': obj.get('region'), 'role': obj.get('surfaceRole'), 'boundsXYZ': bounds})
AUDIT.mkdir(parents=True, exist_ok=True)
out = AUDIT / 'source-upper-torso-inventory.json'
assert not out.exists()
out.write_text(json.dumps({'source': str(SOURCE.relative_to(ROOT)), 'sha256': SOURCE_SHA,
                           'coordinates': 'native rest-world XYZ; Z up, negative Y forward, positive X anatomical left',
                           'parts': rows}, indent=2) + '\n')
print(json.dumps(rows, indent=2))
