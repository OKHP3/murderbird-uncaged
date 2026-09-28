"""Read-only receipt finalizer for the saved V15 legs study."""
from pathlib import Path
import datetime
import hashlib
import json
import runpy

import bpy

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'assets/models/uncaged-orbital-crown-v14/attempt-11/murderbird-orbital-crown-v14.blend'
BASE_SHA = '93cf7908906dab0746ec42ace88867b3c52cb0988c284cf6ae468eb2cce17a5a'
NATIVE = ROOT / 'assets/models/whole-character-v15/legs-study-01/murderbird-v15-legs-study-01.blend'
AUDIT = ROOT / 'assets/audit/whole-character-v15/legs-study-01'
RECEIPT = AUDIT / 'receipt.json'
HELPER = ROOT / 'scripts/build-uncaged-alignment-v7.py'
MODULE = ROOT / 'scripts/regions/whole-character-v15-legs.py'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def art(path):
    path = Path(path)
    return {'path': path.resolve().relative_to(ROOT).as_posix(),
            'sha256': sha(path), 'bytes': path.stat().st_size}

assert not RECEIPT.exists(), 'Refusing to overwrite an existing receipt'
assert sha(BASE) == BASE_SHA
assert sha(HELPER) == '39b6ee2285d8c49df3a902f8fac0a07589da3d41f48ae24df1e06515c839033a'
helpers = runpy.run_path(str(HELPER), run_name='v15_legs_receipt_helpers')

bpy.ops.wm.open_mainfile(filepath=str(BASE))
before = helpers['scene_snapshot']()
before_materials = {m.name: helpers['material_signature'](m) for m in bpy.data.materials}
before_toe_hinges = sorted(o.name for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith('Toe hinge'))

bpy.ops.wm.open_mainfile(filepath=str(NATIVE))
after = helpers['scene_snapshot']()
after_materials = {m.name: helpers['material_signature'](m) for m in bpy.data.materials}
assert before['empties'] == after['empties'] and len(after['empties']) == 52
assert before['curves'] == after['curves']
assert before_materials == after_materials
assert all(after['meshes'][name] == record for name, record in before['meshes'].items())
new_names = sorted(set(after['meshes']) - set(before['meshes']))
assert len(new_names) == 18, f'Expected 18 added meshes, found {len(new_names)}'
new_objects = [bpy.data.objects[name] for name in new_names]
assert all(o.parent and o.parent.name == o.get('constructionOwner') for o in new_objects)
assert all(o.get('exteriorEras') == 'maker,mechanic,builder' for o in new_objects)
assert len([o for o in new_objects if 'open passive truss' in o.name]) == 6
assert len([o for o in new_objects if 'captive toe-bearing flanges' in o.name]) == 12
assert len(before_toe_hinges) == 12

view_records = []
for label in ('before', 'after'):
    for view, pos, target, scale in [
        ('whole-three-quarter', (-3.5, -5.2, 1.9), (0, -.04, .98), 2.65),
        ('legs-front', (0, -3.0, .66), (0, -.06, .43), 1.05),
        ('legs-three-quarter', (-1.35, -2.15, .70), (0, -.06, .43), 1.00),
    ]:
        p = AUDIT / f'{label}-{view}.png'
        assert p.is_file()
        view_records.append({'label': label, 'view': view, **art(p),
                             'camera': {'position': pos, 'target': target, 'orthographicScale': scale}})

owners = sorted({o.parent.name for o in new_objects})
receipt = {
    'schema': 'whole-character-v15-legs-study/v1',
    'status': 'single editable passive leg/foot construction proposal; not accepted or integrated',
    'generatedAtUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'base': art(BASE), 'native': art(NATIVE), 'module': art(MODULE),
    'executedModuleSnapshot': art(AUDIT / 'executed-legs-module.py'),
    'executedStudyRunner': art(AUDIT / 'executed-study.py'),
    'receiptFinalizer': art(Path(__file__)),
    'helper': {'path': HELPER.relative_to(ROOT).as_posix(), 'sha256': sha(HELPER)},
    'preservation': {
        'all52PivotAndParentSnapshotsExact': True,
        'historicalCurvesExact': True,
        'allInheritedMeshesExact': True,
        'materialsAndAssignmentsExact': True,
        'toeHingeMeshes': before_toe_hinges,
        'toeHingesUnchanged': True,
        'newMeshes': len(new_objects),
        'newMeshesByOwner': {owner: sum(o.parent.name == owner for o in new_objects) for owner in owners},
        'savedAndReopenedSnapshotExact': True,
        'attachment': 'Every added mesh is rigidly parented to its constructionOwner, one existing joint only.'
    },
    'construction': {
        'trusses': [n for n in new_names if 'open passive truss' in n],
        'toeBearingFlanges': [n for n in new_names if 'captive toe-bearing flanges' in n],
        'eligibility': 'Passive visible structure across Maker, Mechanic, and Advanced; no new actuator or powered function.'
    },
    'views': view_records,
    'limits': [
        'Neutral Blender Workbench comparison is a construction study, not runtime appearance or art acceptance.',
        'Toe pivots and all inherited claw/contact meshes are preserved; no ground-contact or motion sweep was run.',
        'No exhaustive self-intersection, physical load, stress, or fatigue analysis was run.',
        'The owner image is a whole-body target; this module addresses only legs and feet.'
    ]
}
with RECEIPT.open('x') as f:
    json.dump(receipt, f, indent=2)
    f.write('\n')
print(json.dumps({'status': receipt['status'], 'native': receipt['native'],
                  'newMeshes': len(new_names), 'pivotCount': len(after['empties']),
                  'receipt': art(RECEIPT)}, indent=2))
