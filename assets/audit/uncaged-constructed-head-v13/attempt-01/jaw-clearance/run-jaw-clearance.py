"""Discrete read-only V13 native jaw-angle screen against fixed bill/cheek/cervical surfaces."""
from pathlib import Path
import hashlib, json, math, runpy, datetime
import bpy
from mathutils import Matrix
ROOT=Path(__file__).resolve().parents[5]
NATIVE=ROOT/'assets/models/uncaged-constructed-head-v13/attempt-01/murderbird-constructed-head-v13.blend'
MOTION=ROOT/'src/scene/era-motion.js'
GEN=ROOT/'scripts/build-constructed-head-v13.py'
HELPER=ROOT/'scripts/diagnose-native-regional-clearance.py'
KERNEL=ROOT/'assets/audit/cervical-construction-study-v1/attempt-07/actual-runtime-joint-clearance-v1/executed-review.py'
OUT=ROOT/'assets/audit/uncaged-constructed-head-v13/attempt-01/jaw-clearance'
NATIVE_SHA='32f9af41c93603ebdad3b12148c432acfe8c896b338364fdc9cf73700c918d27'
GEN_SHA='579859c946bc9b5733b07bbb11161f5d693a029b59ad38017ffcc702119ba6c7'
CHANGED=['Profiled upper bill blade 0','Profiled upper bill blade 1','Forked forged mandible -1','Forked forged mandible 1','Distal mandible bridge']
# Actual positive-only rotation ranges: Maker .32 rad; Builder cage edge-probe .12*.27=.0324; seam-rattle .04*.27=.0108; other listed builder jaw paths are zero.
ANGLES=[0.0,0.0108,0.0324,0.08,0.16,0.2025,0.24,0.32]
INTENDED={'Coaxial mandible journal':'fixed coaxial hinge journal / intended mating interface',
          'Mandible journal cap':'moving same-owner hinge cap / intended mating interface'}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def art(p): return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
def desc(o): return o.parent.name if o.parent else None
def intended(name):
    for prefix,label in INTENDED.items():
        if name==prefix or name.startswith(prefix+'.'):
            return label
    return None
def main():
    assert sha(NATIVE)==NATIVE_SHA and sha(GEN)==GEN_SHA
    assert not (OUT/'jaw-clearance.json').exists()
    helper=runpy.run_path(str(HELPER),run_name='jaw_clearance_surface_helpers')
    kernel=runpy.run_path(str(KERNEL),run_name='jaw_clearance_strict_kernel')
    surface=helper['surface']; bounds_overlap=helper['bounds_overlap']; proper=kernel['proper_crossing_receipt']
    bpy.ops.wm.open_mainfile(filepath=str(NATIVE)); scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update()
    meshes={o.name:o for o in bpy.data.objects if o.type=='MESH'}
    pivots={o.name:o for o in bpy.data.objects if o.type=='EMPTY'}
    jaw=pivots['jaw']; assert len(CHANGED)==5 and all(n in meshes for n in CHANGED)
    subjects=[meshes[n] for n in CHANGED]
    fixed=[]
    for o in meshes.values():
        owner=desc(o)
        if owner=='upper-bill': category='fixed-bill'
        elif owner=='head' and ('Broad swept cheek band' in o.name or o.name.startswith('Recessed cheek fixing') or o.name.startswith('Coaxial mandible journal')): category='fixed-cheek/hinge'
        elif owner in {'neck','cervical-upper','breastplate'}: category='fixed-cervical'
        else: continue
        fixed.append((o,category))
    moving_same=[o for o in meshes.values() if desc(o)=='jaw' and o.name not in CHANGED]
    # Save each object's rest matrix; change only jaw's local opening rotation between samples.
    rest=jaw.matrix_basis.copy()
    sample_records=[]
    for angle in ANGLES:
        jaw.rotation_mode='XYZ';jaw.rotation_euler.x=angle;bpy.context.view_layer.update()
        dg=bpy.context.evaluated_depsgraph_get()
        all_surfaces={o.name:surface(o,dg) for o in subjects+[o for o,_ in fixed]+moving_same}
        pairs=[]
        def check(a,b,category,expected=None):
            if a==b:return
            sa,sb=all_surfaces[a.name],all_surfaces[b.name]
            if not sa or not sb or not bounds_overlap(sa,sb): return
            overlaps=sa['tree'].overlap(sb['tree'])
            if not overlaps: return
            proof=proper(sa,sb,overlaps,Matrix.Identity(4),Matrix.Identity(4))
            strict=bool(proof['confirmedSubjectTriangleCount'] or proof['confirmedTargetTriangleCount'])
            pairs.append({'meshA':a.name,'ownerA':desc(a),'meshB':b.name,'ownerB':desc(b),
                'category':category,'bvhCandidateTrianglePairCount':len(overlaps),
                'strictNoncoplanarCrossing':strict,'interpretation':expected or ('penetration candidate; strict crossing requires review' if strict else 'BVH candidate only'),
                'strictReceipt':proof if strict else None})
        for subject in subjects:
            for target,category in fixed:
                expected=intended(target.name)
                check(subject,target,category,expected)
            for target in moving_same:
                expected=intended(target.name)
                check(subject,target,'same-owner jaw assembly',expected)
        # The modified bill blades are stationary upper-bill children while
        # the modified mandible pieces rotate with jaw; test all changed pairs
        # once, retaining the two-owner and same-owner categories.
        for i,a in enumerate(subjects):
            for b in subjects[i+1:]:
                check(a,b,'changed-region pair',None)
        strict=[p for p in pairs if p['strictNoncoplanarCrossing']]
        sample_records.append({'jawRotationXRad':angle,'jawRotationXDeg':math.degrees(angle),
            'pairCandidateCount':len(pairs),'strictCrossingPairCount':len(strict),
            'strictDifferentOwnerCount':sum(p['ownerA']!=p['ownerB'] for p in strict),
            'strictSameOwnerCount':sum(p['ownerA']==p['ownerB'] for p in strict),'pairs':pairs})
    # Restore the exact pre-test local matrix in memory; do not save.
    jaw.matrix_basis=rest;bpy.context.view_layer.update()
    output={'schema':'constructed-head-v13-jaw-clearance/v1','status':'bounded native discrete jaw-angle surface screen; not continuous clearance or physics proof',
      'generatedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'native':art(NATIVE),
      'generator':art(GEN),'motionSource':art(MOTION),'surfaceHelper':art(HELPER),'strictKernel':art(KERNEL),
      'blenderVersion':bpy.app.version_string,'changedMovingMeshes':CHANGED,'movingOwner':'jaw','fixedTargets':{'bill':[o.name for o,c in fixed if c=='fixed-bill'],'cheekAndHinge':[o.name for o,c in fixed if c=='fixed-cheek/hinge'],'cervical':[o.name for o,c in fixed if c=='fixed-cervical'],'sameOwnerJawMeshes':[o.name for o in moving_same]},
      'runtimeRange':{'makerMaxRad':.32,'builderWarningStrikeMaxRad':.2025,'builderEdgeProbeMaxRad':.0324,'builderSeamRattleMaxRad':.0108,'otherCageFamilyJawRad':0,'samplesRad':ANGLES,'sourceEvidence':'src/scene/era-motion.js:26-41 cage profile maxima; :430-435 warning/strike max .75; :278 Maker articulation; :464 builder applied pose jaw*0.27'},
      'classification':'Fixed coaxial mandible journals and moving journal caps are retained as intended hinge-mating overlaps, but still recorded. Closed bill contact candidates remain explicitly marked for interpretation. Same-owner bridge/fork overlaps are separate from different-owner fixed-surface crossings.',
      'samples':sample_records,'limits':['Only sampled jaw rotation about the actual native jaw pivot; all other pivots are at frame-1 rest.','Strict kernel reports noncoplanar edge-through-face crossings; coplanar/tangent contacts and full containment are not detected.','No penetration depth, friction/contact mechanics, continuous sweep guarantee, or browser/WebGL claim.','No native save, export, application/runtime change.']}
    out=OUT/'jaw-clearance.json';out.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({'angles':len(sample_records),'candidatePairs':[r['pairCandidateCount'] for r in sample_records],'strictPairs':[r['strictCrossingPairCount'] for r in sample_records],'differentOwner':[r['strictDifferentOwnerCount'] for r in sample_records],'sameOwner':[r['strictSameOwnerCount'] for r in sample_records]},indent=2))
main()
