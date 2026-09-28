from pathlib import Path
import hashlib, json, runpy, sys
import bpy
from mathutils import Matrix

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BASE = ROOT/'assets/models/uncaged-orbital-saddle-study-v4/murderbird-orbital-saddle-study-v4.blend'
STUDY = ROOT/'assets/models/uncaged-orbital-saddle-study-v6/murderbird-orbital-saddle-study-v6.blend'
POSE_CODE = ROOT/'src/scene/inspection-pose.js'
DIAGNOSTIC = ROOT/'scripts/diagnose-native-regional-clearance.py'
KERNEL = ROOT/'assets/audit/cervical-construction-study-v1/attempt-07/actual-runtime-joint-clearance-v1/executed-review.py'
EXPECTED = {
    'base':'d1afd0f5d97b48bed7828993bbedab3535acaabdec9f505afc38df9584394c4a',
    'study':'cb811241d241b0f18f529979b77635caecb83284b8b4df29c7564d4d2bf55eec',
}
OWNERS = {'head','upper-bill','jaw','builder-optics','cranial-cover'}
SUBJECT_NAMES = (
    [f'Forged orbital brow {s}' for s in (-1,1)] +
    [f'Forged orbital mounting plate {s}' for s in (-1,1)] +
    ['Rounded swept crown lamina 0','Rounded swept crown lamina 1'] +
    [f'Swept temporal lamina {s} 0 0' for s in (-1,1)] +
    [f'Orbital mounting fixing {s} {n}' for s in (-1,1) for n in (1,3,6,9,13)]
)


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def artifact(p): return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
def snap_surface(o, depsgraph, h): return h['surface'](o, depsgraph)

assert sha(BASE)==EXPECTED['base'] and sha(STUDY)==EXPECTED['study']
h = runpy.run_path(str(DIAGNOSTIC), run_name='orbital_clearance_helpers')
kernel = runpy.run_path(str(KERNEL), run_name='frozen_crossing_kernel')
proper_crossing_receipt = kernel['proper_crossing_receipt']
reports = {}
for variant, path in [('base',BASE),('study',STUDY)]:
    bpy.ops.wm.open_mainfile(filepath=str(path))
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    pivots = {o.name:o for o in bpy.data.objects if o.type=='EMPTY'}
    meshes = {o.name:o for o in bpy.data.objects if o.type=='MESH'}
    assert 'cranial-cover' in pivots
    missing = [n for n in SUBJECT_NAMES if n not in meshes]
    assert not missing, f'{variant} missing scoped changed mesh identities: {missing}'
    subjects = [meshes[n] for n in SUBJECT_NAMES]
    targets = [o for o in meshes.values() if o.parent and o.parent.name in OWNERS]
    cover = pivots['cranial-cover']
    initial_local = cover.matrix_local.copy()
    rest_world = {o.name:o.matrix_world.copy() for o in set(subjects+targets)}
    other_pivots = {n:p.matrix_world.copy() for n,p in pivots.items() if n!='cranial-cover'}
    rows = []
    by_pair = {}
    for step in range(41):
        opening = step/40
        cover.matrix_local = initial_local.copy()
        cover.location.z = initial_local.translation.z + .08*opening
        bpy.context.view_layer.update()
        assert all(max(abs(pivots[n].matrix_world[r][c]-m[r][c]) for r in range(4) for c in range(4)) < 2e-7 for n,m in other_pivots.items()), 'Unexpected non-cover pivot motion'
        assert abs((cover.matrix_local.translation-initial_local.translation).z-.08*opening)<1e-6, (variant,opening,tuple(initial_local.translation),tuple(cover.location),tuple(cover.matrix_local.translation))
        depsgraph = bpy.context.evaluated_depsgraph_get()
        scope = list(dict.fromkeys(subjects + targets))
        surfaces = {o.name:snap_surface(o,depsgraph,h) for o in scope}
        candidates=[]; same_owner=[]; different_owner=[]
        visited=set()
        for subject in subjects:
            for target in targets:
                if subject == target: continue
                pair=tuple(sorted((subject.name,target.name)))
                if pair in visited: continue
                visited.add(pair)
                a,b=surfaces[subject.name],surfaces[target.name]
                if not a or not b or not h['bounds_overlap'](a,b): continue
                overlaps=a['tree'].overlap(b['tree'])
                if not overlaps: continue
                category='same-owner' if subject.parent==target.parent else 'different-owner'
                proof=proper_crossing_receipt(a,b,overlaps,rest_world[subject.name]@subject.matrix_world.inverted(),rest_world[target.name]@target.matrix_world.inverted())
                row={'meshA':subject.name,'ownerA':subject.parent.name,'meshB':target.name,'ownerB':target.parent.name,
                     'triangleOverlapCandidates':len(overlaps),'strictCrossing':proof}
                candidates.append(row)
                (same_owner if category=='same-owner' else different_owner).append(row)
                key=(category,*pair)
                state=by_pair.setdefault(key,{'category':category,'meshA':pair[0],'meshB':pair[1],
                    'owners':sorted({subject.parent.name,target.parent.name}),'candidateFractions':[],'crossingFractions':[],
                    'maxTriangleCandidates':0,'maxCrossingTriangles':0})
                state['candidateFractions'].append(opening)
                state['maxTriangleCandidates']=max(state['maxTriangleCandidates'],len(overlaps))
                crossing_triangles=proof['confirmedSubjectTriangleCount']+proof['confirmedTargetTriangleCount']
                state['maxCrossingTriangles']=max(state['maxCrossingTriangles'],crossing_triangles)
                if crossing_triangles:
                    state['crossingFractions'].append(opening)
        rows.append({'openingFraction':opening,'nativeCoverLocalZDeltaM':round(.08*opening,9),
                     'differentOwnerCandidatePairCount':len(different_owner),
                     'differentOwnerStrictCrossingPairCount':sum(bool(x['strictCrossing']['confirmedSubjectTriangleCount'] or x['strictCrossing']['confirmedTargetTriangleCount']) for x in different_owner),
                     'sameOwnerCandidatePairCount':len(same_owner),
                     'sameOwnerStrictCrossingPairCount':sum(bool(x['strictCrossing']['confirmedSubjectTriangleCount'] or x['strictCrossing']['confirmedTargetTriangleCount']) for x in same_owner),
                     'differentOwnerPairs':different_owner,'sameOwnerPairs':same_owner})
    reports[variant]={'native':artifact(path),'missingSubjectMeshes':missing,'scopedSubjectMeshes':SUBJECT_NAMES,
                     'targetOwnerScope':sorted(OWNERS),'targetMeshCount':len(targets),'samples':rows,
                     'pairHistory':[v for v in by_pair.values()]}

# Pair-level classification is based on strict crossing at one or more of the 41 sampled states.
def strict_map(report):
    return {(p['category'],p['meshA'],p['meshB']):p for p in report['pairHistory'] if p['crossingFractions']}
base_strict,study_strict=strict_map(reports['base']),strict_map(reports['study'])
def identity_map(report):
    return {(p['meshA'],p['meshB']):p for p in report['pairHistory'] if p['crossingFractions']}
base_identity,study_identity=identity_map(reports['base']),identity_map(reports['study'])
new_identity_keys=sorted(set(study_identity)-set(base_identity))
inherited_identity_keys=sorted(set(study_identity)&set(base_identity))
resolved_identity_keys=sorted(set(base_identity)-set(study_identity))
category_changes=[{'meshA':k[0],'meshB':k[1],'baseCategory':base_identity[k]['category'],'studyCategory':study_identity[k]['category'],
    'baseOwners':base_identity[k]['owners'],'studyOwners':study_identity[k]['owners'],
    'baseCrossingFractions':base_identity[k]['crossingFractions'],'studyCrossingFractions':study_identity[k]['crossingFractions']}
    for k in inherited_identity_keys if base_identity[k]['category']!=study_identity[k]['category']]
new_keys=sorted(set(study_strict)-set(base_strict))
inherited_keys=sorted(set(study_strict)&set(base_strict))
# Worst sampled fraction is the peak number of distinct strict different-owner pairs in V3.
counts=[r['differentOwnerStrictCrossingPairCount'] for r in reports['study']['samples']]
peak=max(counts)
worst=[reports['study']['samples'][i]['openingFraction'] for i,n in enumerate(counts) if n==peak]
inputs={'base':artifact(BASE),'study':artifact(STUDY),'inspectionPoseCode':artifact(POSE_CODE),
        'regionalClearanceDiagnostic':artifact(DIAGNOSTIC),'frozenCrossingKernel':artifact(KERNEL),
        'auditRunner':artifact(Path(__file__))}
result={
 'status':'read-only native geometry screening; V4 base to V6 study; no app/export/browser claim',
 'sceneDefinition':{'openingFractions':[i/40 for i in range(41)],'coverMotion':'cranial-cover native local Z += 0.08 m * opening fraction (browser local Y per src/scene/inspection-pose.js)',
   'fixedState':'all other native pivots held at source rest; separation zero; head/body rest; these are synthesized native states, not captured browser poses',
   'ownersCompared':sorted(OWNERS),'subjects':SUBJECT_NAMES,'sameOwnerPairsKeptSeparate':True},
 'inputs':inputs,
 'results':{'newStrictCrossingPairIdentities':[study_identity[k] for k in new_identity_keys],
   'inheritedStrictCrossingPairIdentities':[study_identity[k] for k in inherited_identity_keys],
   'resolvedStrictCrossingPairIdentities':[base_identity[k] for k in resolved_identity_keys],
   'inheritedPairOwnerCategoryChanges':category_changes,
   'newDifferentOwnerStrictCrossingPairs':[study_strict[k] for k in new_keys if k[0]=='different-owner'],
   'inheritedDifferentOwnerStrictCrossingPairs':[study_strict[k] for k in inherited_keys if k[0]=='different-owner'],
   'inheritedSameOwnerStrictCrossingPairs':[study_strict[k] for k in inherited_keys if k[0]=='same-owner'],
   'newSameOwnerStrictCrossingPairs':[study_strict[k] for k in new_keys if k[0]=='same-owner'],
   'newDifferentOwnerBVHCandidateOnlyPairs':[p for p in reports['study']['pairHistory'] if p['category']=='different-owner' and p['candidateFractions'] and not p['crossingFractions'] and (p['category'],p['meshA'],p['meshB']) not in base_strict],
   'worstSampledDifferentOwnerCrossingPairCount':peak,'worstSampledOpeningFractions':worst,
   'sampledDifferentOwnerCrossingPairCounts':counts,
   'baseDifferentOwnerCrossingPairCount':sum(k[0]=='different-owner' for k in base_strict),
   'studyDifferentOwnerCrossingPairCount':sum(k[0]=='different-owner' for k in study_strict),
   'newStrictCrossingIdentityCount':len(new_identity_keys),'inheritedStrictCrossingIdentityCount':len(inherited_identity_keys),
   'resolvedStrictCrossingIdentityCount':len(resolved_identity_keys)},
 'restingSourceHashPreserved':sha(STUDY)==EXPECTED['study'],
 'limits':['BVH triangle candidates are broad surface overlap evidence; strict receipts count only noncoplanar edge-through-face crossings.',
   'Full containment is untested; absence of strict crossings does not prove clearance.',
   'Discrete 0.025 opening increments do not prove continuous clearance between samples.',
   'Same-owner intersections, including nominal pin embedding, are reported separately and are not classified as intended or defective by geometry alone.',
   'This is a native Blender replay of the specified rigid cover translation, not captured browser poses or owner likeness acceptance.',
   'No native source was saved or changed; no export, app/runtime edit, CI, deployment, or publication was performed.'],
 'blenderVersion':bpy.app.version_string,
 'kernelFixtures':{'strictKernel':'proper_crossing_receipt from frozen executed-review.py','syntheticTriangles':'inherited kernel module loaded without invoking its main entrypoint'}
}
assert result['restingSourceHashPreserved']
(OUT/'cranial-opening-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'newDifferentOwnerCrossingPairs':len(result['results']['newDifferentOwnerStrictCrossingPairs']),
                  'inheritedDifferentOwnerCrossingPairs':len(result['results']['inheritedDifferentOwnerStrictCrossingPairs']),
                  'peakPairs':peak,'worstFractions':worst,'sourceHashPreserved':result['restingSourceHashPreserved']}))
