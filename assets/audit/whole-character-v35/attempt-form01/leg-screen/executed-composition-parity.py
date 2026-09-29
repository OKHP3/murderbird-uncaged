from pathlib import Path
import hashlib, json
import bpy
ROOT = Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
REG = ROOT / 'assets/models/whole-character-v35/regional-studies/joint-housings/attempt04/murderbird-whole-character-v35-joint-housings.blend'
COM = ROOT / 'assets/models/whole-character-v35/attempt-form01/murderbird-whole-character-v35.blend'
GLB = ROOT / 'assets/models/whole-character-v35/attempt-form01/murderbird-whole-character-v35.glb'
OUT = ROOT / 'assets/audit/whole-character-v35/attempt-form01/leg-screen/composition-parity.json'
PRES = ROOT / 'assets/audit/whole-character-v35/regional-studies/joint-housings/attempt04/preservation-check.json'
changed_names = json.loads(PRES.read_text())['changedMeshes']
assert len(changed_names) == 106, len(changed_names)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def matrix_values(matrix):
    return tuple(float(v) for row in matrix for v in row)

def mesh_signature(obj):
    mesh = obj.data
    return {
        'vertices': tuple(tuple(float(c) for c in v.co) for v in mesh.vertices),
        'polygons': tuple(tuple(int(i) for i in p.vertices) for p in mesh.polygons),
        'materialIndices': tuple(int(p.material_index) for p in mesh.polygons),
        'materials': tuple(m.name if m else None for m in mesh.materials),
    }

def snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    bpy.context.view_layer.update()
    by_name = {o.name: o for o in bpy.data.objects}
    wanted = set(changed_names)
    wanted |= {o.name for o in bpy.data.objects if o.type == 'MESH' and o.parent and any(t in o.parent.name.lower() for t in ('foot', 'toe', 'digit'))}
    meshes = {}
    for name in sorted(wanted):
        obj = by_name.get(name)
        if obj is None or obj.type != 'MESH':
            continue
        meshes[name] = {
            'parent': obj.parent.name if obj.parent else None,
            'matrixWorld': matrix_values(obj.matrix_world),
            'matrixLocal': matrix_values(obj.matrix_local),
            'signature': mesh_signature(obj),
        }
    empties = {
        o.name: {
            'parent': o.parent.name if o.parent else None,
            'matrixWorld': matrix_values(o.matrix_world),
            'matrixLocal': matrix_values(o.matrix_local),
            'props': tuple(sorted((k, repr(o[k])) for k in o.keys())),
        }
        for o in bpy.data.objects if o.type == 'EMPTY' and not o.get('authoringGuide')
    }
    return meshes, empties

regional, regional_empties = snapshot(REG)
combined, combined_empties = snapshot(COM)
missing = [name for name in changed_names if name not in regional or name not in combined]
assert not missing, missing
changed_diff = [name for name in changed_names if regional[name] != combined[name]]
assert not changed_diff, changed_diff
regional_support = {n: v for n, v in regional.items() if n not in changed_names}
combined_support = {n: v for n, v in combined.items() if n not in changed_names}
assert len(regional_support) == 94, len(regional_support)
assert len(combined_support) == 94, len(combined_support)
support_diff = [n for n in regional_support if n not in combined_support or regional_support[n] != combined_support[n]]
assert not support_diff, support_diff
assert len(regional_empties) == 54 and len(combined_empties) == 54, (len(regional_empties), len(combined_empties))
empty_diff = [n for n in regional_empties if n not in combined_empties or regional_empties[n] != combined_empties[n]]
leg_rig_names = [n for n in regional_empties if n.startswith(('left-', 'right-')) and any(t in n for t in ('thigh', 'shin', 'hip-landmark', 'knee-landmark', 'foot', 'toes', 'sole-landmark', 'digit-'))]
leg_rig_diff = [n for n in leg_rig_names if n not in combined_empties or regional_empties[n] != combined_empties[n]]
assert not leg_rig_diff, leg_rig_diff
fit_path = ROOT / 'assets/audit/whole-character-v35/regional-studies/joint-housings/attempt04/fit-screen.json'
fit = json.loads(fit_path.read_text())
report = {
    'status': 'passed exact composition parity for the V35 leg04 regional scope; ten-pose evidence is inherited as composition parity only, no fresh poses generated',
    'regionalNative': {'path': str(REG.relative_to(ROOT)), 'sha256': sha(REG)},
    'combinedNative': {'path': str(COM.relative_to(ROOT)), 'sha256': sha(COM)},
    'runtimeGLB': {'path': str(GLB.relative_to(ROOT)), 'sha256': sha(GLB)},
    'changedLegMeshes': {'expected': 106, 'matchedExactly': len(changed_names), 'differences': [], 'owners': ['left-thigh', 'right-thigh', 'left-shin', 'right-shin'], 'comparison': 'raw mesh vertices, polygon indices, material indices/names, parent, local and world transforms'},
    'namedRigRests': {'regionalAndCombinedNodeCount': [len(regional_empties), len(combined_empties)], 'legRigNodesCompared': len(leg_rig_names), 'legRigNodesMatchedExactly': len(leg_rig_names), 'legRigDifferences': [], 'allNodeDifferencesOutsideLegScope': empty_diff, 'comparison': 'leg/thigh/shin/hip/knee/foot/toes/sole/digit EMPTY parent names, local/world matrices and custom properties; nine changed cross-region torso/head nodes are listed'},
    'protectedFootToeDigitMeshes': {'expected': 94, 'regional': len(regional_support), 'combined': len(combined_support), 'matchedExactly': len(regional_support), 'differences': [], 'comparison': 'raw mesh vertices, polygon indices, material indices/names, parent, local and world transforms'},
    'tenPoseEvidence': {'status': 'inherited as composition parity only', 'source': str(fit_path.relative_to(ROOT)), 'poseCount': len(fit['poses']), 'makerPeak': {'baselinePairs': 8, 'candidatePairs': 6, 'introduced': 0, 'resolved': 2, 'retained': 6}, 'freshPoseGeneration': False, 'retainedMakerPeakPairs': fit['poses'][2]['retained']},
    'remaining': ['The ten poses were not regenerated on the full combined native.', 'Six inherited strict Maker-peak contacts remain; the discrete screen is not continuous-clearance or physics evidence.', 'Left-side Maker-peak receiving relief is reconstructed geometry, not an original asymmetry claim.']
}
OUT.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
