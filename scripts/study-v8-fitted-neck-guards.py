"""HELD EXPERIMENT: the supposed coordinate error was disproved after execution.

Do not use this displacement as a coordinate correction. The original recipe
already converts its world-space vertices through the owner inverse. The
saved experiment incorrectly moves the added guards 100 mm forward. See
assets/audit/fitted-neck-guards-study-v1/supervisor-hold.json. The exact script
that produced the native remains preserved in that directory.

Existing native meshes and articulation remain unchanged. New rigid side
guards are proposed passive structure in every era, with explicit ownership.
"""
from pathlib import Path
import hashlib
import json
import runpy
import shutil

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'assets/models/uncaged-alignment-v8/murderbird-alignment-v8.blend'
BASE_SHA = 'b12c442e2f517b676cdd1fae1612730cc0ba83251d34f363285b08f2cd482478'
HELPER = ROOT / 'scripts/build-uncaged-alignment-v7.py'
RECIPE = ROOT / 'scripts/study-v7-neck-shoulder-envelope.py'
OUT = ROOT / 'assets/models/uncaged-fitted-neck-guards-study-v1'
AUDIT = ROOT / 'assets/audit/fitted-neck-guards-study-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path):
    return {'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size, 'sha256': sha(path)}


def render(native, prefix):
    bpy.ops.wm.open_mainfile(filepath=str(native))
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_WORKBENCH'
    sh = scene.display.shading
    sh.light = 'STUDIO'
    sh.studio_light = 'paint.sl'
    sh.color_type = 'MATERIAL'
    sh.show_shadows = True
    sh.show_cavity = True
    sh.cavity_type = 'BOTH'
    sh.background_type = 'WORLD'
    scene.world.color = (.11,.12,.13)
    scene.render.resolution_x = scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj.hide_render = 'builder' not in obj.get('exteriorEras','maker,mechanic,builder').split(',')
            obj.hide_set(False)
    cd = bpy.data.cameras.new('Temporary fitted neck camera')
    cam = bpy.data.objects.new('Temporary fitted neck camera',cd)
    scene.collection.objects.link(cam)
    scene.camera = cam
    cd.type = 'ORTHO'
    rows = []
    for name, position, target, scale in [
        ('neck-profile',(-6,-.3,1.48),(0,-.3,1.48),.93),
        ('neck-three-quarter',(-4,-6,2),(0,-.23,1.48),1.08),
        ('whole-three-quarter',(-4.25,-5.9,3.24),(0,-.10,.99),2.40),
    ]:
        cam.location = position
        cam.rotation_euler = (Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
        cd.ortho_scale = scale
        path = AUDIT/f'{prefix}-{name}.png'
        assert not path.exists()
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        rows.append({**artifact(path),'view':name,'variant':prefix,
                     'camera':{'position':position,'target':target,'orthoScale':scale}})
    return rows


def main():
    assert sha(BASE) == BASE_SHA
    assert sha(HELPER) == '39b6ee2285d8c49df3a902f8fac0a07589da3d41f48ae24df1e06515c839033a'
    assert sha(RECIPE) == 'ce601b716e446269c01d2fe84aa222fde0eca4ce9142cd5cbf7c598f9d82746f'
    assert not OUT.exists() and not AUDIT.exists(), 'Write-once study'
    h = runpy.run_path(str(HELPER),run_name='snapshot_helpers')
    recipe = runpy.run_path(str(RECIPE),run_name='guard_recipe')
    bpy.ops.wm.open_mainfile(filepath=str(BASE))
    before = h['scene_snapshot']()
    materials = {m.name:h['material_signature'](m) for m in bpy.data.materials}
    neck = bpy.data.objects['neck']
    # The recipe's envelope coordinates are authoring-space coordinates.
    # Existing neck meshes were subsequently shifted with the body root.
    assert abs(neck.matrix_world.translation.y + .1) < 1e-7
    template = bpy.data.objects['Cervical flank lamina 1 1']
    additions = []
    for side_name, sign in [('left',1),('right',-1)]:
        for number, band in enumerate(recipe['NECK_GUARD_BANDS'],1):
            name = f'Fitted cervical side guard {side_name} {number}'
            obj = recipe['make_neck_guard'](name,sign,band,template)
            bpy.context.view_layer.update()
            inv = obj.matrix_world.inverted()
            for vertex in obj.data.vertices:
                world = obj.matrix_world @ vertex.co
                world.y -= .1
                vertex.co = inv @ world
            obj.data.update()
            obj['exteriorEras'] = 'maker,mechanic,builder'
            obj['eraClass'] = 'inherited-passive'
            obj['surfaceRole'] = 'plate'
            obj['geometryStatus'] = 'proposed rigid side guard; corrected authoring-space Y offset'
            additions.append(name)
    after = h['scene_snapshot']()
    assert before['empties'] == after['empties'] and before['curves'] == after['curves']
    assert set(after['meshes'])-set(before['meshes']) == set(additions)
    assert all(after['meshes'][name] == row for name,row in before['meshes'].items())
    assert materials == {m.name:h['material_signature'](m) for m in bpy.data.materials}
    OUT.mkdir(parents=True)
    AUDIT.mkdir(parents=True)
    native = OUT/'murderbird-fitted-neck-guards-study-v1.blend'
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False)
    bpy.ops.wm.open_mainfile(filepath=str(native))
    assert h['scene_snapshot']() == after
    shutil.copy2(__file__,AUDIT/'executed-generator.py')
    receipt = {'status':'isolated corrected-placement proposal; visual and motion review pending',
        'base':artifact(BASE),'native':artifact(native),'recipe':artifact(RECIPE),
        'generator':artifact(AUDIT/'executed-generator.py'),'replace':[],'add':additions,
        'correction':{'worldYOffsetM':-.1,'reason':'Prior recipe used authoring envelope centres as world coordinates after the base body was shifted.'},
        'preservation':{'allOriginalMeshesExact':True,'all51PivotsExact':True,'allGuidesExact':True,
                        'allMaterialsExact':True,'saveReloadSnapshotExact':True},
        'construction':{'owner':'neck','eraEligibility':'inherited passive guard, all three eras',
                        'surface':'rigid metal; no deformation','hiddenTopology':'proposed reconstruction'},
        'limits':['No physical or continuous clearance claim.','No runtime export or application selection.','Existing guides do not author the new mesh guards.']}
    (AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    receipt['views'] = render(BASE,'before') + render(native,'after')
    assert sha(BASE) == BASE_SHA
    (AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'native':artifact(native),'images':len(receipt['views'])}))


if __name__ == '__main__':
    main()
