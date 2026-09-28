"""One-shot read-only native crown-lift screen against fixed V14 brow/socket.

Run in Blender with --native ABSOLUTE_BLEND --native-sha256 SHA256 --audit-dir RELATIVE_AUDIT_DIR.
The audit directory must not already exist. This replays prescribed world-Z offsets,
not browser frames, and uses strict noncoplanar edge-through-face receipts only after BVH candidates.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, runpy, shutil, sys
import bpy
from mathutils import Matrix

ROOT=Path(__file__).resolve().parents[1]
HELPER=ROOT/'scripts/diagnose-native-regional-clearance.py'
KERNEL=ROOT/'assets/audit/cervical-construction-study-v1/attempt-07/actual-runtime-joint-clearance-v1/executed-review.py'
OFFSETS=(0.0,.02,.04,.06,.08,.15,.22)
BROW_NAMES=('Forged orbital brow -1','Forged orbital brow 1')
CHEEK_NAMES=('Broad swept cheek band -1','Broad swept cheek band 1',
 'Recessed cheek fixing','Recessed cheek fixing.001','Recessed cheek fixing.002',
 'Recessed cheek fixing.003','Recessed cheek fixing.004','Recessed cheek fixing.005')
SOCKET_EXACT=('Forged orbital mounting plate -1','Forged orbital mounting plate 1',
 'Recessed orbital bearing -1','Recessed orbital bearing 1',
 'Seated passive optic housing -1','Seated passive optic housing 1',
 'Seated Advanced optic -1','Seated Advanced optic 1')
SOCKET_PREFIXES=('Orbital mounting fixing ',)
COVER_NAME='cranial-cover'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def artifact(p): return {'path':str(Path(p).resolve().relative_to(ROOT)),'sha256':sha(p),'bytes':Path(p).stat().st_size}
def matrix_error(a,b): return max(abs(float(a[r][c])-float(b[r][c])) for r in range(4) for c in range(4))
def direct_owner(o): return o.parent.name if o.parent else None
def under(obj,ancestor):
    cur=obj.parent
    while cur is not None:
        if cur==ancestor:return True
        cur=cur.parent
    return False

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--native',required=True,help='absolute path to final V14 native .blend')
    parser.add_argument('--native-sha256',required=True)
    parser.add_argument('--audit-dir',required=True,help='new repository-relative output directory')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    native=Path(args.native).resolve(); out=(ROOT/args.audit_dir).resolve()
    assert native.is_file() and native.suffix.lower()=='.blend'
    assert native.is_relative_to(ROOT), 'native input must be inside this repository'
    assert sha(native)==args.native_sha256.lower(), 'native SHA-256 mismatch'
    assert out.is_relative_to(ROOT) and not out.exists(), 'choose one new audit directory; will not overwrite'
    assert sha(HELPER) and sha(KERNEL)
    helpers=runpy.run_path(str(HELPER),run_name='v14_crown_clearance_surface_helpers')
    kernel=runpy.run_path(str(KERNEL),run_name='v14_crown_clearance_strict_kernel')
    surface=helpers['surface'];bounds_overlap=helpers['bounds_overlap'];proper=kernel['proper_crossing_receipt']
    bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update()
    objects={o.name:o for o in bpy.data.objects}
    assert COVER_NAME in objects and objects[COVER_NAME].type=='EMPTY'
    cover=objects[COVER_NAME]
    brows=[objects[n] for n in BROW_NAMES]
    cheeks=[objects[n] for n in CHEEK_NAMES]
    sockets=[objects[n] for n in SOCKET_EXACT]
    sockets.extend(o for o in bpy.data.objects if o.type=='MESH' and any(o.name.startswith(p) for p in SOCKET_PREFIXES))
    assert len(brows)==2 and all(o.type=='MESH' for o in brows+cheeks+sockets)
    assert all(not under(o,cover) for o in brows+cheeks+sockets), 'fixed target unexpectedly follows cranial-cover'
    assert all(direct_owner(o) in {'head','builder-optics'} for o in brows+cheeks+sockets), 'unexpected fixed-target owner'
    moving=[o for o in bpy.data.objects if o.type=='MESH' and under(o,cover)]
    assert moving, 'cranial-cover has no mesh descendants'
    fixed=[('brow',o) for o in brows]+[('socket',o) for o in sockets]+[('cheek',o) for o in cheeks]
    pivots={o.name:o for o in bpy.data.objects if o.type=='EMPTY'}
    cover_base=cover.matrix_world.copy()
    other_pivots={n:o.matrix_world.copy() for n,o in pivots.items()
                  if o!=cover and not under(o,cover)}
    helper_hash=sha(HELPER);kernel_hash=sha(KERNEL);script=Path(__file__).resolve()
    records=[]
    for dz in OFFSETS:
        world=cover_base.copy();world.translation.z+=dz;cover.matrix_world=world;bpy.context.view_layer.update()
        now={o.name:surface(o,bpy.context.evaluated_depsgraph_get()) for o in moving+sockets+brows+cheeks}
        pivot_error=max((matrix_error(o.matrix_world,m) for n,m in other_pivots.items() for o in [pivots[n]]),default=0.0)
        assert pivot_error<2e-6, f'non-cover pivot changed at lift {dz}: {pivot_error}'
        pairs=[]
        for moving_mesh in moving:
            for role,fixed_mesh in fixed:
                a=now[moving_mesh.name];b=now[fixed_mesh.name]
                if not a or not b or not bounds_overlap(a,b):continue
                overlaps=a['tree'].overlap(b['tree'])
                if not overlaps:continue
                proof=proper(a,b,overlaps,Matrix.Identity(4),Matrix.Identity(4))
                strict=bool(proof['confirmedSubjectTriangleCount'] or proof['confirmedTargetTriangleCount'])
                pairs.append({'movingCrownMesh':moving_mesh.name,'movingOwner':direct_owner(moving_mesh),
                    'fixedRole':role,'fixedMesh':fixed_mesh.name,'fixedOwner':direct_owner(fixed_mesh),
                    'bvhTrianglePairCandidateCount':len(overlaps),'strictNoncoplanarCrossing':strict,
                    'qualitativeContactIdentity':('strict surface crossing candidate; review triangle examples and bounds' if strict else 'BVH candidate only; strict edge-through-face crossing not confirmed'),
                    'strictReceipt':proof if strict else None})
        strict=[p for p in pairs if p['strictNoncoplanarCrossing']]
        records.append({'coverWorldZTranslationM':dz,'nonCoverPivotWorldMatrixMaxError':pivot_error,
            'bvhCandidatePairCount':len(pairs),'strictCrossingPairCount':len(strict),
            'strictPairsByRole':{role:sum(p['strictNoncoplanarCrossing'] and p['fixedRole']==role for p in pairs) for role in ('brow','socket','cheek')},
            'pairs':pairs})
    # Reset only the in-memory trial; the file is never saved.
    cover.matrix_world=cover_base;bpy.context.view_layer.update()
    result={'schema':'uncaged-orbital-crown-v14-fixed-socket-clearance/v1',
      'status':'discrete read-only native crown translation screen; no browser capture or acceptance claim',
      'generatedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'native':artifact(native),'nativePivotCount':len(pivots),'coverPivot':'cranial-cover',
      'coverMotion':{'axis':'world/native +Z','sampleOffsetsM':list(OFFSETS),'articulationContext':'0..0.08m opening and larger prescribed lift/separation samples through 0.22m; each value is total world-Z offset from rest'},
      'subjects':{'owner':'cranial-cover','meshes':[o.name for o in sorted(moving,key=lambda x:x.name)]},
      'fixedTargets':{'browMeshes':[o.name for o in brows],'socketMeshes':[o.name for o in sockets],'cheekMeshes':[o.name for o in cheeks],
        'ownersByMesh':{o.name:direct_owner(o) for _,o in fixed}},
      'surfaceHelper':{'path':str(HELPER.relative_to(ROOT)),'sha256':helper_hash,'coordinateFrame':'evaluated mesh vertices transformed by evaluated.matrix_world into current native world XYZ'},
      'strictKernel':{'path':str(KERNEL.relative_to(ROOT)),'sha256':kernel_hash,'method':'proper_crossing_receipt: strict noncoplanar edge-through-face tests'},
      'diagnosticScript':artifact(script),'blenderVersion':bpy.app.version_string,'samples':records,
      'pairInterpretation':'Strict identities present at offset0 are rest-present in this candidate and remain separate from lift-emergent identities; neither class is automatically accepted as intended mating. The report does not use cross-version inheritance as a synonym for fit.',
      'limits':['Only cranial-cover translation is varied; all unrelated pivots stay at saved rest.','BVH candidates are distinct from strict surface crossings; coplanar and tangent contacts may be excluded by strict kernel.','No full containment, penetration depth, continuous sweep, physical guide/support, export parity, or runtime/browser-frame proof.','Exact brow/socket/cheek pair identities are retained; no overlap is assumed intended without construction authority.','Native was opened read-only and not saved; no model or application asset was modified.']}
    out.mkdir(parents=True)
    shutil.copy2(script,out/'executed-clearance.py')
    result['diagnosticScript']['frozenCopy']={'path':str((out/'executed-clearance.py').relative_to(ROOT)),'sha256':sha(out/'executed-clearance.py')}
    (out/'native-clearance.json').write_text(json.dumps(result,indent=2)+'\n')
    assert sha(native)==args.native_sha256.lower(), 'native changed during read-only screen'
    print(json.dumps({'nativeSha256':sha(native),'samples':len(records),
      'strictByLift':{str(r['coverWorldZTranslationM']):r['strictCrossingPairCount'] for r in records},
      'audit':str(out.relative_to(ROOT))},indent=2))

main()
