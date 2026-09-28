"""Read-only sampled jaw sweep against every rigid head, bill and crown mesh.

Includes new V17 fittings by owner rather than relying on old mesh names.
This is a discrete surface-crossing diagnostic, not physical simulation.
"""
from pathlib import Path
import argparse, sys, json, hashlib, runpy, shutil
import bpy
from mathutils import Matrix

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--native', required=True)
p.add_argument('--sha', required=True)
p.add_argument('--out', required=True)
a = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
native, out = ROOT / a.native, ROOT / a.out
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
assert sha(native) == a.sha and not out.exists()
bpy.ops.wm.open_mainfile(filepath=str(native))
h = runpy.run_path(str(ROOT / 'scripts/diagnose-native-regional-clearance.py'), run_name='head_surfaces')
k = runpy.run_path(str(ROOT / 'assets/audit/cervical-construction-study-v1/attempt-07/actual-runtime-joint-clearance-v1/executed-review.py'), run_name='head_kernel')
fixed = [o for o in bpy.data.objects if o.type == 'MESH' and o.parent and o.parent.name in ('head', 'upper-bill', 'cranial-cover', 'builder-optics')]
moving = [o for o in bpy.data.objects if o.type == 'MESH' and o.parent and o.parent.name == 'jaw']
assert len(moving) >= 3 and len(fixed) > 20
rows = []
for angle in [i * .04 for i in range(9)]:
    bpy.data.objects['jaw'].rotation_euler.x = angle
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    surfaces = {o.name: h['surface'](o, dg) for o in fixed + moving}
    pairs = []
    for left in moving:
        for right in fixed:
            u, v = surfaces[left.name], surfaces[right.name]
            if not u or not v or not h['bounds_overlap'](u, v): continue
            candidates = u['tree'].overlap(v['tree'])
            if not candidates: continue
            proof = k['proper_crossing_receipt'](u, v, candidates, Matrix.Identity(4), Matrix.Identity(4))
            crossing = bool(proof['confirmedSubjectTriangleCount'] or proof['confirmedTargetTriangleCount'])
            pairs.append({'moving': left.name, 'fixed': right.name, 'candidateTriangles': len(candidates), 'crossing': crossing, 'proof': proof if crossing else None})
    rows.append({'jawRadians': angle, 'strictCrossingPairs': sum(r['crossing'] for r in pairs), 'pairs': pairs})
out.mkdir(parents=True)
shutil.copy2(__file__, out / 'executed-check.py')
receipt = {'native': {'path': a.native, 'sha256': a.sha},
           'status': 'crossings require pair review' if any(r['strictCrossingPairs'] for r in rows) else 'no strict crossings in sampled scope',
           'samples': rows, 'moving': [o.name for o in moving], 'fixed': [o.name for o in fixed],
           'limits': ['Nine discrete positions from 0 to 0.32 radians.', 'All jaw-owned surfaces against head, upper-bill, cranial-cover and builder-optics mesh owners; era-ineligible parts are conservatively included.', 'Intentional journal fits must be distinguished from unintended interference.', 'No containment, continuous collision, physical simulation or artistic acceptance.', 'Native input is read-only.']}
(out / 'head-clearance.json').write_text(json.dumps(receipt, indent=2) + '\n')
assert sha(native) == a.sha
print(json.dumps({'status': receipt['status'], 'crossingCounts': [r['strictCrossingPairs'] for r in rows]}))
