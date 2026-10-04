"""Single unpromoted HEAD16 localized eyehood material-routing trial.

No geometry, material graph, texture, pose, camera or light edits in apply().
The runner opens frozen head15 in memory, renders twice, and restores routing.
It never saves a native or exports an asset.
"""
import bpy
import hashlib
import importlib.util
import json
from pathlib import Path
from mathutils import Matrix
import datetime

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
NAMES = tuple('CGH15 localized orbital brow and root return '+s for s in ('near', 'far'))
INPUT = BASE/'assets/audit/cg-supervised-head15/attempt02/localized-head15.blend'
EXPECTED = 'a3b753c768b7bf0346f41eac10b74e62d240050056631053c1a5bb319d833980'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def apply(scene, root=None, era='builder'):
    """Route slot0 of exactly the two new head15 brows to their slot2 bronze.

    Validate both objects before any mutation. A second apply is rejected.
    Era names follow the existing renderer (builder is Advanced).
    """
    if era not in ('maker', 'mechanic', 'builder'):
        raise ValueError('Unknown existing material era: '+str(era))
    objects = []
    for name in NAMES:
        obj = scene.objects.get(name)
        if obj is None or obj.type != 'MESH' or not obj.get('cgSupervisedHead15'):
            raise RuntimeError('Missing or invalid new head15 object: '+name)
        if len(obj.data.materials) != 3:
            raise RuntimeError('Expected exactly three existing slots: '+name)
        mats = list(obj.data.materials)
        for mat, family in zip(mats, ('head-armor', 'black-iron', 'worn-bronze')):
            if mat is None or mat.get('cgMetal05Family') != family or mat.get('cgMetal05Era') != era:
                raise RuntimeError('Invalid same-era material routing: '+name+' / '+family)
        if not any(m.type == 'SOLIDIFY' and m.material_offset == 1 and m.material_offset_rim == 1 for m in obj.modifiers):
            raise RuntimeError('Dark-edge routing unavailable: '+name)
        if any(p.material_index != 0 for p in obj.data.polygons):
            raise RuntimeError('Unexpected face material indices: '+name)
        objects.append((obj, mats))
    routes = []
    for obj, mats in objects:
        obj.data.materials[0] = mats[2]
        routes.append({'object': obj.name, 'before_slots': [m.name for m in mats],
                       'after_slots': [m.name for m in obj.data.materials],
                       'changed_slot': 0, 'unchanged_slots': [1, 2]})
    return {'era': era, 'routes': routes, 'material_graph_edits': 0,
            'new_materials': 0, 'geometry_edits': 0,
            'proposal_only': True, 'integration_requires_root_retention_and_full09_qc': True}

def run():
    out = ROOT/'assets/audit/cg-supervised-head16'
    out.mkdir(parents=True, exist_ok=True)
    assert sha(INPUT) == EXPECTED
    frozen = json.loads((BASE/'assets/audit/cg-supervised-head15/frozen-manifest.json').read_text())
    frozen_before = {p: sha(BASE/p) for p in frozen['files']}
    assert frozen_before == frozen['files']
    spec = importlib.util.spec_from_file_location('frozen15', BASE/'scripts/cg-supervised-head15.py')
    h15 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(h15)
    bpy.ops.wm.open_mainfile(filepath=str(INPUT))
    scene = bpy.context.scene
    before = h15.snap()
    original = {n: scene.objects[n].data.materials[0] for n in NAMES}
    report = apply(scene, ROOT, 'builder')
    after = h15.snap()
    report['preservation'] = {
        'changed_object_payloads': [n for n, h in before['objects'].items() if after['objects'].get(n) != h],
        'material_graph_changes': [n for n, h in before['materials'].items() if after['materials'].get(n) != h],
        'file_image_changes': [n for n, h in before['images'].items() if h['source']=='FILE' and after['images'].get(n) != h],
        'visibility_equal': before['visibility'] == after['visibility'],
        'all_material_graph_sha256_before': before['materials'],
        'all_material_graph_sha256_after': after['materials'],
    }
    assert set(report['preservation']['changed_object_payloads']) == set(NAMES)
    assert not report['preservation']['material_graph_changes']
    assert not report['preservation']['file_image_changes']
    assert report['preservation']['visibility_equal']
    report.update(input_path=str(INPUT), input_sha256=EXPECTED,
                  started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  renders=0, native_saves=0, exports=0, cameras={}, frozen15_entry_count=len(frozen_before))
    reference = json.loads((BASE/'assets/audit/cg-supervised-head15/attempt02/receipt.json').read_text())
    # Exact baseline render controls; existing lights/world/exposure retained.
    scene.render.engine='CYCLES';scene.cycles.samples=8;scene.cycles.use_denoising=True
    scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
    scene.view_layers[0].material_override=None
    report['frozen_lighting'] = {'world': scene.world.name,
        'view_settings': h15.rna(scene.view_settings),
        'lights': {o.name: {'matrix': h15.val(o.matrix_world), 'data': h15.rna(o.data)} for o in scene.objects if o.type=='LIGHT'},
        'samples': scene.cycles.samples, 'denoising': scene.cycles.use_denoising}
    def write():
        (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    try:
        for view in ('source-full-bird', 'head-grazing'):
            key='after-pbr-'+view;rc=reference['cameras'][key]
            camera=scene.camera;camera.matrix_world=Matrix(rc['matrix'])
            camera.data.ortho_scale=rc['scale'];camera.data.shift_x,camera.data.shift_y=rc['shift']
            scene.render.resolution_x,scene.render.resolution_y=rc['resolution']
            path=out/('trial16-pbr-'+view+'.png');scene.render.filepath=str(path)
            bpy.context.view_layer.update();bpy.ops.render.render(write_still=True)
            report['renders']+=1;report['cameras'][view]=rc
            report.setdefault('render_hashes',{})[path.name]=sha(path)
            report.setdefault('render_completed_utc',{})[view]=datetime.datetime.now(datetime.timezone.utc).isoformat()
            write();print('HEAD16_RENDERED',view,flush=True)
    finally:
        for name, mat in original.items():scene.objects[name].data.materials[0]=mat
        restored=h15.snap()
        report['restored_original_object_payloads']=before['objects']==restored['objects']
        report['restored_material_graphs']=before['materials']==restored['materials']
        report['frozen15_hashes_after']={p:sha(BASE/p) for p in frozen_before}
        report['frozen15_all_88_unchanged']=report['frozen15_hashes_after']==frozen_before
        report['source_before_trial_native_unchanged']=sha(INPUT)==EXPECTED
        report['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        write()
    assert report['restored_original_object_payloads'] and report['restored_material_graphs'] and report['frozen15_all_88_unchanged']
    print('HEAD16_COMPLETE_TWO_RENDERS_NO_SAVE_NO_EXPORT',flush=True)

if __name__ == '__main__':
    run()
