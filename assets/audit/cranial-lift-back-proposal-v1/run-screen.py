"""Read-only comparison of V6 vertical opening with one smooth cranial lift-back path."""
from pathlib import Path
import hashlib, json, itertools, runpy
import bpy

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
NATIVE=ROOT/'assets/models/uncaged-orbital-saddle-study-v6/murderbird-orbital-saddle-study-v6.blend'
POSE=ROOT/'src/scene/inspection-pose.js'
DIAGNOSTIC=ROOT/'scripts/diagnose-native-regional-clearance.py'
KERNEL=ROOT/'assets/audit/cervical-construction-study-v1/attempt-07/actual-runtime-joint-clearance-v1/executed-review.py'
EXPECTED_NATIVE='cb811241d241b0f18f529979b77635caecb83284b8b4df29c7564d4d2bf55eec'
REGION_OWNERS={'head','upper-bill','jaw','builder-optics','cranial-cover'}
COVER_OWNER='cranial-cover'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def artifact(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
def pair_key(a,b):return tuple(sorted((a,b)))
def strict(proof):return proof['confirmedSubjectTriangleCount']+proof['confirmedTargetTriangleCount']>0

def scan(pathname):
    bpy.ops.wm.open_mainfile(filepath=str(NATIVE));scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update()
    objects={o.name:o for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name in REGION_OWNERS}
    cover_meshes=[o for o in objects.values() if o.parent.name==COVER_OWNER]
    cover=bpy.data.objects[COVER_OWNER]
    initial=cover.matrix_local.copy()
    other={o.name:o.matrix_world.copy() for o in bpy.data.objects if o.type=='EMPTY' and o.name!=COVER_OWNER}
    rest={n:o.matrix_world.copy() for n,o in objects.items()}
    all_pairs=[(a,b) for a,b in itertools.combinations(objects.values(),2) if a.parent.name==COVER_OWNER or b.parent.name==COVER_OWNER]
    by_pair={};samples=[]
    for step in range(41):
        f=step/40
        cover.matrix_local=initial.copy()
        cover.location.z=initial.translation.z+.08*f
        lift_y=.05*(f*f*(3-2*f)) if pathname=='lift_back' else 0.0
        cover.location.y=initial.translation.y+lift_y
        bpy.context.view_layer.update()
        assert all(max(abs(bpy.data.objects[n].matrix_world[r][c]-m[r][c]) for r in range(4) for c in range(4))<2e-7 for n,m in other.items())
        dg=bpy.context.evaluated_depsgraph_get()
        h=HELPERS['surface'];bounds_overlap=HELPERS['bounds_overlap']
        surfaces={n:h(o,dg) for n,o in objects.items()}
        diff=[];same=[]
        for a,b in all_pairs:
            sa,sb=surfaces[a.name],surfaces[b.name]
            if not sa or not sb or not bounds_overlap(sa,sb):continue
            overlaps=sa['tree'].overlap(sb['tree'])
            if not overlaps:continue
            category='same-owner' if a.parent.name==b.parent.name else 'different-owner'
            proof=PROPER(sa,sb,overlaps,rest[a.name]@a.matrix_world.inverted(),rest[b.name]@b.matrix_world.inverted())
            key=(category,*pair_key(a.name,b.name))
            row=by_pair.setdefault(key,{'category':category,'meshA':key[1],'meshB':key[2],
               'ownerA':objects[key[1]].parent.name,'ownerB':objects[key[2]].parent.name,
               'candidateFractions':[],'strictCrossingFractions':[],'maxTriangleOverlapCandidates':0,
               'maxConfirmedCrossingTriangles':0})
            row['candidateFractions'].append(f)
            row['maxTriangleOverlapCandidates']=max(row['maxTriangleOverlapCandidates'],len(overlaps))
            confirmed=proof['confirmedSubjectTriangleCount']+proof['confirmedTargetTriangleCount']
            row['maxConfirmedCrossingTriangles']=max(row['maxConfirmedCrossingTriangles'],confirmed)
            if strict(proof):row['strictCrossingFractions'].append(f)
            (same if category=='same-owner' else diff).append({'meshA':a.name,'meshB':b.name,'strict':strict(proof),'candidateTriangles':len(overlaps)})
        samples.append({'openingFraction':f,'coverLocalZDeltaM':round(.08*f,9),'coverLocalYDeltaM':round(lift_y,9),
          'differentOwnerBVHCandidatePairs':sum(1 for x in diff),'differentOwnerStrictCrossingPairs':sum(x['strict'] for x in diff),
          'sameOwnerBVHCandidatePairs':sum(1 for x in same),'sameOwnerStrictCrossingPairs':sum(x['strict'] for x in same)})
    return {'meshes':objects,'coverMeshCount':len(cover_meshes),'regionMeshCount':len(objects),'possiblePairCount':len(all_pairs),
            'samples':samples,'pairHistory':[x for x in by_pair.values()]}

assert sha(NATIVE)==EXPECTED_NATIVE
HELPERS=runpy.run_path(str(DIAGNOSTIC),run_name='lift_back_clearance_helpers')
K=runpy.run_path(str(KERNEL),run_name='frozen_lift_back_kernel')
PROPER=K['proper_crossing_receipt']
vertical=scan('vertical_only')
proposed=scan('lift_back')

def strictmap(scan_result):
    return {(p['category'],p['meshA'],p['meshB']):p for p in scan_result['pairHistory'] if p['strictCrossingFractions']}
vmap,pmap=strictmap(vertical),strictmap(proposed)
new=sorted(set(pmap)-set(vmap));inherited=sorted(set(pmap)&set(vmap));resolved=sorted(set(vmap)-set(pmap))
counts=[s['differentOwnerStrictCrossingPairs'] for s in proposed['samples']]
peak=max(counts);worst=[s['openingFraction'] for s in proposed['samples'] if s['differentOwnerStrictCrossingPairs']==peak]
closed=[p for p in pmap.values() if 0.0 in p['strictCrossingFractions'] and any(t in p['meshA']+' '+p['meshB'] for t in ('hood','Cere root transition','crown lamina'))]
ref_five_map={**vmap,**pmap}
ref_five=[p for p in ref_five_map.values() if any(t in p['meshA']+' '+p['meshB'] for t in ('Overlapping nasal hood','Nasal hood fixing','Cere root transition')) and 'Rounded swept crown lamina 0' in p['meshA']+' '+p['meshB']]
# Deduplicate the explicit five-pair reference list by identity.
ref_five={ (p['category'],p['meshA'],p['meshB']): {'identity':(p['category'],p['meshA'],p['meshB']),
  'verticalStrictCrossingFractions':vmap.get((p['category'],p['meshA'],p['meshB']),{}).get('strictCrossingFractions',[]),
  'liftBackStrictCrossingFractions':pmap.get((p['category'],p['meshA'],p['meshB']),{}).get('strictCrossingFractions',[])} for p in ref_five}
result={
 'status':'read-only native access-path comparison; proposed path is not implemented or approved',
 'native':artifact(NATIVE),'inspectionPoseCode':artifact(POSE),'regionalClearanceDiagnostic':artifact(DIAGNOSTIC),'frozenCrossingKernel':artifact(KERNEL),'runner':artifact(Path(__file__)),
 'sceneDefinition':{'nativeState':'exact V6 pinned source, all objects at rest at closed state','ownerRegion':sorted(REGION_OWNERS),
   'coverOwner':'cranial-cover','pairScope':'all distinct pairs of meshes owned by the head-region set with at least one mesh owned by cranial-cover',
   'cranialCoverMeshCount':proposed['coverMeshCount'],'headRegionMeshCount':proposed['regionMeshCount'],'possiblePairIdentitiesPerPath':proposed['possiblePairCount'],
   'sampleCount':41,'fractions':[i/40 for i in range(41)],
   'verticalOnly':'native local Z += 0.08 m * f; local Y unchanged',
   'proposedLiftBack':'native local Z += 0.08 m * f; native local Y += 0.05 m * (f*f*(3-2*f)); +Y is rear',
   'transforms':'Both paths start from the unchanged native local transform at every sample; all other pivots remain at rest.',
   'relationshipToRuntime':'same vertical cranial-cover lift as src/scene/inspection-pose.js plus one proposed rigid Y translation; synthesized native states, not captured browser poses.'},
 'results':{'newStrictCrossingPairs':[pmap[k] for k in new],'inheritedStrictCrossingPairs':[pmap[k] for k in inherited],
   'resolvedStrictCrossingPairs':[vmap[k] for k in resolved],
   'newStrictIdentityCount':len(new),'inheritedStrictIdentityCount':len(inherited),'resolvedStrictIdentityCount':len(resolved),
   'proposedWorstSampledDifferentOwnerStrictPairCount':peak,'proposedWorstSampledOpeningFractions':worst,
   'proposedDifferentOwnerStrictPairCountsByFraction':counts,
   'closedStateHoodCrownStrictPairs':closed,'fiveKnownCrownHoodCerePairIdentities':list(ref_five.values()),
   'verticalOnly':{'samples':vertical['samples'],'pairHistory':vertical['pairHistory']},
   'proposedLiftBack':{'samples':proposed['samples'],'pairHistory':proposed['pairHistory']}},
 'limits':['BVH overlap pairs are candidate evidence; strict receipts count only frozen-kernel noncoplanar edge-through-face crossings.',
   'Full containment and continuous swept-volume clearance are untested; 0.025 samples do not prove clearance between states.',
   'The lift-back path is a proposed prescribed rigid motion, not a physical guide or captured runtime path. Hardware/support guidance would be required before implementation.',
   'The closed-state hood/crown interference is preserved because both proposed offsets are zero at f=0; this access path does not solve it.',
   'No native was edited/saved; no V8/V9 artifacts, app/runtime, export, or implementation were changed.'],
 'blenderVersion':bpy.app.version_string,'strictKernel':'proper_crossing_receipt from frozen executed-review.py; loaded without invoking its main entrypoint'}
(OUT/'lift-back-screen.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'possiblePairCount':proposed['possiblePairCount'],'strictIdentityCounts':[len(new),len(inherited),len(resolved)],'proposedPeak':peak,'worstFractions':worst,'closedStateHoodCrownPairs':len(closed),'knownFive':len(ref_five)}))
