"""Compose scoped V21 regional proposals on the preserved envelope03 native."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import runpy
import shutil
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'assets/models/whole-character-v21/attempt-envelope03/murderbird-whole-character-v21.blend'
BASE_SHA = '720c343645ef2de298a50e53c82fad66448c187b1eaf9311de2514cac079f280'
LAYOUT = ROOT / 'assets/audit/whole-character-v21/attempt-envelope03/derived-mechanism-layout.json'
LAYOUT_SHA = '10b4638dc8ff00d3117ce2c494194b3f21df1b48ae7c62fab237a34f266a244a'
p = argparse.ArgumentParser()
p.add_argument('--attempt', required=True)
p.add_argument('--modules', nargs='+', required=True)
args = p.parse_args(sys.argv[sys.argv.index('--') + 1:])
assert args.attempt.replace('-', '').isalnum()
assert set(args.modules) <= {'head-refinement', 'directional-plates', 'joint-clearance', 'ankle-clevis'}
AUDIT = ROOT / f'assets/audit/whole-character-v21/attempt-{args.attempt}'
OUT = ROOT / f'assets/models/whole-character-v21/attempt-{args.attempt}'
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
def art(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path), 'bytes': path.stat().st_size}

assert sha(BASE) == BASE_SHA and sha(LAYOUT) == LAYOUT_SHA
assert not AUDIT.exists() and not OUT.exists()
AUDIT.mkdir(parents=True)
OUT.mkdir(parents=True)
shutil.copy2(__file__, AUDIT / 'executed-composition.py')
h = runpy.run_path(str(ROOT / 'scripts/build-uncaged-alignment-v7.py'))
bpy.ops.wm.open_mainfile(filepath=str(BASE))
before = h['scene_snapshot']()
materials = {m.name: h['material_signature'](m) for m in bpy.data.materials}
scopes = {'head-refinement': {'head', 'jaw', 'upper-bill', 'cranial-cover', 'builder-optics'},
          'directional-plates': {'neck', 'cervical-upper', 'breastplate', 'body'},
          'joint-clearance': {'neck', 'cervical-upper', 'breastplate', 'body'},
          'ankle-clevis': {'left-shin', 'right-shin', 'left-foot', 'right-foot'}}
contracts = []
for region in args.modules:
    source = ROOT / f'scripts/regions/whole-character-v21-{region}.py'
    frozen = AUDIT / f'executed-{region}.py'
    shutil.copy2(source, frozen)
    prior = h['scene_snapshot']()
    result = runpy.run_path(str(frozen))['apply']()
    after = h['scene_snapshot']()
    # Regional authoring may change mesh data, never the articulation rests.
    assert before['empties'] == after['empties'], f'{region} changed rigid nodes'
    assert before['curves'] == after['curves'], f'{region} changed historical guides'
    names = set(prior['meshes']) | set(after['meshes'])
    altered = sorted(n for n in names if prior['meshes'].get(n) != after['meshes'].get(n))
    for name in altered:
        old = prior['meshes'].get(name)
        new = after['meshes'].get(name)
        for record in (old, new):
            if record:
                assert record['parent'] in scopes[region], (region, name, record['parent'])
    contracts.append({'region': region, 'source': art(frozen), 'alteredMeshes': altered, 'construction': result})
assert materials == {m.name: h['material_signature'](m) for m in bpy.data.materials}
contact_updates = []
for contract in contracts:
    proposal = contract['construction'].get('billContactNativeWorld')
    if proposal is not None:
        marker = bpy.data.objects['bill-contact']
        old = list(marker.matrix_world.translation)
        matrix = marker.matrix_world.copy()
        matrix.translation = Vector(proposal)
        marker.matrix_world = matrix
        bpy.context.view_layer.update()
        contact_updates.append({'name': marker.name, 'beforeNativeWorld': old,
                                'afterNativeWorld': list(marker.matrix_world.translation),
                                'status': 'contact marker follows the revised authored bill; no physical-force claim'})
layout = json.loads(LAYOUT.read_text())
body = bpy.data.objects['body']
body['mechanismLayoutV1'] = json.dumps(layout, separators=(',', ':'))
body['v21SocketStatus'] = 'Cervical points derived from envelope03 frame; retained other offsets. Moving clearance remains under review.'
shared = json.loads(body['sharedEnvelopeV21'])
shared['status'] = 'Regional construction proposal; cervical socket metadata refreshed from the preserved envelope03 frame, swept clearance unaccepted.'
body['sharedEnvelopeV21'] = json.dumps(shared, separators=(',', ':'))
shutil.copy2(LAYOUT, AUDIT / 'mechanism-layout.json')
checks = []
deps = bpy.context.evaluated_depsgraph_get()
for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
    evaluated = obj.evaluated_get(deps)
    mesh = evaluated.to_mesh()
    assert all(math.isfinite(c) for v in mesh.vertices for c in v.co), obj.name
    checks.append(obj.name)
    evaluated.to_mesh_clear()
after = h['scene_snapshot']()
native = OUT / 'murderbird-whole-character-v21.blend'
bpy.context.preferences.filepaths.save_version = 0
bpy.ops.wm.save_as_mainfile(filepath=str(native), check_existing=False)
bpy.ops.wm.open_mainfile(filepath=str(native))
assert h['scene_snapshot']() == after
assert bpy.data.objects['body']['mechanismLayoutV1'] == json.dumps(layout, separators=(',', ':'))
receipt = {'status': 'regional construction proposal; likeness and swept clearance unaccepted',
           'base': art(BASE), 'native': art(native), 'composition': art(AUDIT / 'executed-composition.py'),
           'contracts': contracts, 'mechanismLayout': art(AUDIT / 'mechanism-layout.json'),
           'contactUpdates': contact_updates,
           'checks': {'articulationRestTransformsAndParentsExact': 52-len(contact_updates), 'materialsExact': True,
                      'allEvaluatedMeshesFinite': len(checks), 'saveReopenExact': True},
           'views': [], 'limits': ['No physical simulation or owner artistic acceptance.',
                                 'No new runtime selection or publication from this composer.']}
receipt_path = AUDIT / 'receipt.json'
receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
views = [('reference-angle', (-6,-3.5,2.75), (0,-.08,1.02), 2.5),
         ('front', (0,-7,1.65), (0,-.08,1.02), 2.5),
         ('side', (-7,0,1.35), (0,-.08,1.02), 2.5),
         ('neck', (-6,-3.5,2.45), (0,-.27,1.48), 1.30),
         ('rear', (0,7,1.65), (0,-.08,1.02), 2.5),
         ('maker-reference-angle', (-6,-3.5,2.75), (0,-.08,1.02), 2.5),
         ('mechanic-reference-angle', (-6,-3.5,2.75), (0,-.08,1.02), 2.5)]
for label, path in [('after',native), ('before',BASE)]:
    bpy.ops.wm.open_mainfile(filepath=str(path))
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    sh = scene.display.shading
    sh.light = 'STUDIO'
    sh.studio_light = 'paint.sl'
    sh.color_type = 'SINGLE'
    sh.single_color = (.56,.58,.60)
    sh.show_shadows = False
    sh.show_cavity = True
    sh.cavity_type = 'BOTH'
    sh.background_type = 'WORLD'
    scene.world.color = (.12,.13,.14)
    scene.render.resolution_x = scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    for obj in bpy.data.objects:
        obj.hide_set(False)
        if obj.type == 'MESH':
            obj.hide_render = 'builder' not in obj.get('exteriorEras','maker,mechanic,builder').split(',')
        elif obj.type == 'CURVE':
            obj.hide_render = True
    data = bpy.data.cameras.new('Temporary V21 construction review')
    data.type = 'ORTHO'
    camera = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    for name, position, target, scale in views:
        era = 'maker' if name.startswith('maker-') else 'mechanic' if name.startswith('mechanic-') else 'builder'
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                obj.hide_render = era not in obj.get('exteriorEras','maker,mechanic,builder').split(',')
        camera.location = position
        camera.rotation_euler = (Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
        data.ortho_scale = scale
        scene.render.filepath = str(AUDIT / f'{label}-{name}.png')
        bpy.ops.render.render(write_still=True)
        receipt['views'].append({**art(Path(scene.render.filepath)), 'era':era,
                                 'camera':{'position':position,'target':target,'scale':scale},
                                 'lighting':'neutral native Workbench, cast shadows off'})
        receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
    if label == 'after':
        # Render-time frame evaluation must not reset the requested pose.
        for obj in bpy.data.objects:
            if obj.animation_data is not None:
                obj.animation_data_clear()
            if obj.type == 'MESH':
                obj.hide_render = 'builder' not in obj.get('exteriorEras','maker,mechanic,builder').split(',')
        for name, joint, angle, target, scale in (
            ('native-jaw-open','jaw',.32,(0,-.27,1.48),1.30),
            ('native-breast-open','breastplate',1.1,(0,-.08,1.02),2.5),
        ):
            bpy.data.objects['jaw'].rotation_euler.x = 0
            bpy.data.objects['breastplate'].rotation_euler.x = 0
            bpy.data.objects[joint].rotation_euler.x = angle
            bpy.context.view_layer.update()
            expected = bpy.data.objects[joint].matrix_world.copy()
            camera.location = (-6,-3.5,2.45 if joint == 'jaw' else 2.75)
            camera.rotation_euler = (Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
            data.ortho_scale = scale
            scene.render.filepath = str(AUDIT / f'{name}.png')
            bpy.ops.render.render(write_still=True)
            actual = bpy.data.objects[joint].matrix_world
            error = max(abs(actual[r][c]-expected[r][c]) for r in range(4) for c in range(4))
            assert error < 2e-6
            receipt['views'].append({**art(Path(scene.render.filepath)), 'era':'builder',
                'nativeLocalX':{joint:angle}, 'postRenderWorldMatrixError':error,
                'status':'in-memory authoring illustration, not runtime or continuous clearance proof'})
            receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
assert sha(BASE) == BASE_SHA and sha(native) == receipt['native']['sha256']
print(json.dumps({'native':receipt['native'],'checks':receipt['checks'],'views':len(receipt['views'])}))
