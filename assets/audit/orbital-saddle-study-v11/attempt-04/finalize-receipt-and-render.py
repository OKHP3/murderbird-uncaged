"""Read-only V11 attempt-04 snapshot, clearance receipt, and matched renders."""
from pathlib import Path
import datetime, hashlib, json, runpy
import bpy

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'assets/models/uncaged-orbital-saddle-study-v6/murderbird-orbital-saddle-study-v6.blend'
NATIVE=ROOT/'assets/models/uncaged-orbital-saddle-study-v11/murderbird-orbital-saddle-study-v11.blend'
AUDIT=Path(__file__).resolve().parent
HELPER=ROOT/'scripts/build-uncaged-alignment-v7.py'
GENERATOR=ROOT/'scripts/study-orbital-saddle-v11.py'
RENDERER=ROOT/'scripts/study-v8-bill-envelope.py'
SIDES=(-1,1)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def artifact(p): return {'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)}

def main():
    assert sha(BASE)=='cb811241d241b0f18f529979b77635caecb83284b8b4df29c7564d4d2bf55eec'
    helper=runpy.run_path(str(HELPER),run_name='v11_receipt_helpers')
    geom=runpy.run_path(str(GENERATOR),run_name='v11_receipt_geometry')
    renderer=runpy.run_path(str(RENDERER),run_name='v11_receipt_renderer')
    bpy.ops.wm.open_mainfile(filepath=str(BASE)); bpy.context.scene.frame_set(1); bpy.context.view_layer.update()
    baseline=helper['scene_snapshot']()
    bpy.ops.wm.open_mainfile(filepath=str(NATIVE)); bpy.context.scene.frame_set(1); bpy.context.view_layer.update()
    candidate=helper['scene_snapshot']()
    allowed=[f'Forged orbital mounting plate {s}' for s in SIDES]
    assert set(baseline['meshes'])==set(candidate['meshes'])
    changed=[n for n in baseline['meshes'] if baseline['meshes'][n]!=candidate['meshes'][n]]
    assert set(changed)==set(allowed),(changed,allowed)
    assert baseline['empties']==candidate['empties'] and baseline['curves']==candidate['curves']
    material_sigs={m.name:helper['material_signature'](m) for m in bpy.data.materials}
    world_before={o.name:o.matrix_world.copy() for o in bpy.data.objects}
    topologies=[]; self_results=[]
    deps=bpy.context.evaluated_depsgraph_get()
    for side in SIDES:
        obj=bpy.data.objects[f'Forged orbital mounting plate {side}']
        topologies.append({'object':obj.name,'topology':geom['topology_profile'](obj)})
        surf=geom['evaluated_surface'](obj,deps)
        cross,pairs=geom['self_crossings'](surf)
        self_results.append({'object':obj.name,'nonadjacentSelfBvhPairs':pairs,'strictCrossings':cross})
    cover=bpy.data.objects['cranial-cover']; original_local=cover.matrix_local.copy(); sweep=[]
    for step in range(41):
        frac=step/40; cover.matrix_local=original_local.copy()
        cover.location.z=original_local.translation.z+.08*frac
        bpy.context.view_layer.update(); deps=bpy.context.evaluated_depsgraph_get(); pairs=[]
        for side in SIDES:
            brow=bpy.data.objects[f'Forged orbital brow {side}']; mount=bpy.data.objects[f'Forged orbital mounting plate {side}']
            a=geom['evaluated_surface'](brow,deps); b=geom['evaluated_surface'](mount,deps)
            candidates=a['tree'].overlap(b['tree'])
            pairs.append({'brow':brow.name,'mount':mount.name,'candidatePairCount':len(candidates),
                          'strictCrossings':geom['strict_crossings'](a,b,candidates)})
        sweep.append({'fraction':frac,'coverLocalZDeltaM':.08*frac,'pairs':pairs})
    cover.matrix_local=original_local.copy(); bpy.context.view_layer.update()
    conflicts=[{'fraction':s['fraction'],'pair':p['brow']+' / '+p['mount'],
                'crossingTriangleCountB':p['strictCrossings']['crossingTriangleCountB']}
               for s in sweep for p in s['pairs'] if p['strictCrossings']['crossingTriangleCountA']]
    max_world_error=max(max(abs(o.matrix_world[r][c]-world_before[o.name][r][c]) for r in range(4) for c in range(4)) for o in bpy.data.objects)
    assert baseline['empties']==candidate['empties'] and baseline['curves']==candidate['curves']
    for name,old in baseline['meshes'].items():
        if name not in allowed: assert candidate['meshes'][name]==old,name
    assert max_world_error<2e-7,max_world_error
    assert material_sigs=={m.name:helper['material_signature'](m) for m in bpy.data.materials}
    renderer['renders'].__globals__['AUDIT']=AUDIT
    views=renderer['renders'](BASE,'before')+renderer['renders'](NATIVE,'after')
    result={'status':'held; native preserved for review, geometric and motion clearance not accepted',
        'generatedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'blenderVersion':bpy.app.version_string,
        'base':artifact(BASE),'native':artifact(NATIVE),'generator':artifact(AUDIT/'executed-generator.py'),
        'generatorSource':artifact(GENERATOR),'receiptFinalizer':artifact(Path(__file__).resolve()),
        'helper':artifact(HELPER),'renderer':artifact(RENDERER),
        'changedMeshes':changed,'preservation':{'onlyTwoMountMeshesChanged':set(changed)==set(allowed),
            'other697MeshSnapshotsExact':all(candidate['meshes'][n]==old for n,old in baseline['meshes'].items() if n not in allowed),
            '51PivotsExact':baseline['empties']==candidate['empties'],'462GuidesExact':baseline['curves']==candidate['curves'],
            'allMaterialsExact':True,'allObjectWorldMatricesMaxErrorM':max_world_error},
        'mountTopology':topologies,'mountSelfCrossings':self_results,
        'browMountLiftSweep':{'sampleCount':len(sweep),'samples':sweep,'strictCrossingPairPoseCount':len(conflicts),
            'conflicts':conflicts,'limits':'Discrete rest plus 40 normalized cover lifts; not continuous clearance certification.'},
        'views':views,'knownIssue':'The authored candidate creates zero-area loop triangles in each mount and strict brow/mount crossings at the listed sampled poses. It is saved as a held native for visual diagnosis, not a viable fit.',
        'limits':['The lower profile is an authored proposal, not source metrology.','Strict checks exclude tangency and coplanar overlap.','No export, runtime selection, browser verification, artistic acceptance, or publication.']}
    (AUDIT/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    (AUDIT/'README.md').write_text('# Orbital saddle study V11, attempt 04\n\nHeld native candidate saved for visual inspection. It has zero-area loop triangles and sampled brow/mount crossings; see [receipt.json](receipt.json) for exact failures and preservation checks. It is not accepted or exported.\n')
    print(json.dumps({'native':result['native'],'crossingPoseCount':len(conflicts),'views':len(views),'receipt':str(AUDIT/'receipt.json')},indent=2))

if __name__=='__main__': main()
