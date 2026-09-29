from pathlib import Path
import bpy, json
ROOT = Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
BASE = ROOT / 'assets/models/whole-character-v35/attempt-form01/murderbird-whole-character-v35.blend'
CAND = ROOT / 'assets/models/whole-character-v36/regional-studies/compact-feet/attempt02/murderbird-whole-character-v36-compact-feet.blend'
REPORT = ROOT / 'assets/audit/whole-character-v36/regional-studies/compact-feet/attempt02/preservation-check.json'

def spans(path):
    bpy.ops.wm.open_mainfile(filepath=str(path)); bpy.context.view_layer.update()
    result = {}
    for side in ('left', 'right'):
        owners = {side+'-foot', side+'-toes'} | {
            f'{side}-digit-{d}-{part}' for d in range(1, 4) for part in ('proximal', 'distal')
        }
        pts = [obj.matrix_world @ vertex.co for obj in bpy.data.objects
               if obj.type == 'MESH' and obj.parent and obj.parent.name in owners
               for vertex in obj.data.vertices]
        bounds = [[min(p[k] for p in pts), max(p[k] for p in pts)] for k in range(3)]
        result[side] = {'worldBoundsM': bounds,
                        'foreAftYSpanM': bounds[1][1] - bounds[1][0],
                        'widthXSpanM': bounds[0][1] - bounds[0][0]}
    return result

before, after = spans(BASE), spans(CAND)
for side in ('left', 'right'):
    assert after[side]['foreAftYSpanM'] < before[side]['foreAftYSpanM']
    assert abs(after[side]['widthXSpanM'] - before[side]['widthXSpanM']) < 1e-7
report = json.loads(REPORT.read_text())
report['footRestEnvelope'] = {
    'source': before,
    'candidate': after,
    'foreAftSpanReductionFraction': {
        side: 1.0 - after[side]['foreAftYSpanM'] / before[side]['foreAftYSpanM'] for side in ('left', 'right')
    },
    'interpretation': 'Rest mesh envelope reduction measured in native world Y; not a balance, clearance, or gait result.'
}
REPORT.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report['footRestEnvelope'], indent=2))
