"""Isolated V8 bill-form study, changing actual silhouette before surface detail.

The July head selection supplies qualitative construction, not dimensions.
Write-once native; no application selection or runtime export here.
"""
from pathlib import Path
import hashlib
import json
import math
import runpy
import shutil

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'assets/models/uncaged-alignment-v8/murderbird-alignment-v8.blend'
BASE_SHA = 'b12c442e2f517b676cdd1fae1612730cc0ba83251d34f363285b08f2cd482478'
HELPER = ROOT / 'scripts/build-uncaged-alignment-v7.py'
HELPER_SHA = '39b6ee2285d8c49df3a902f8fac0a07589da3d41f48ae24df1e06515c839033a'
OUT = ROOT / 'assets/models/uncaged-bill-envelope-study-v1'
AUDIT = ROOT / 'assets/audit/bill-envelope-study-v1'
NAME = 'Profiled upper bill blade 1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path):
    return {'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size, 'sha256': sha(path)}


def window(t):
    if t <= .28 or t >= .88:
        return 0.0
    return math.sin(math.pi * (t - .28) / .60) ** 2


def renders(native, label):
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
    scene.world.color = (.11, .12, .13)
    scene.render.resolution_x = scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj.hide_render = 'builder' not in obj.get('exteriorEras', 'maker,mechanic,builder').split(',')
            obj.hide_set(False)
    cd = bpy.data.cameras.new('Temporary bill study camera')
    cam = bpy.data.objects.new('Temporary bill study camera', cd)
    scene.collection.objects.link(cam)
    scene.camera = cam
    cd.type = 'ORTHO'
    views = []
    for view, position, target, scale in [
        ('front', (0,-6,1.78), (0,-.3,1.78), 1.05),
        ('right-profile', (-6,-.3,1.78), (0,-.3,1.78), 1.1),
        ('three-quarter', (-6,-3,2.4), (0,-.29,1.78), .88),
    ]:
        cam.location = position
        cam.rotation_euler = (Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
        cd.ortho_scale = scale
        path = AUDIT / f'{label}-{view}.png'
        assert not path.exists()
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        views.append({**artifact(path), 'view': view, 'variant': label,
                      'camera': {'position': position, 'target': target, 'ortho': scale}})
    return views


def main():
    assert sha(BASE) == BASE_SHA and sha(HELPER) == HELPER_SHA
    assert not OUT.exists() and not AUDIT.exists(), 'Preserve existing study'
    h = runpy.run_path(str(HELPER), run_name='snapshot_helpers')
    bpy.ops.wm.open_mainfile(filepath=str(BASE))
    before = h['scene_snapshot']()
    materials = {m.name: h['material_signature'](m) for m in bpy.data.materials}
    obj = bpy.data.objects[NAME]
    assert len(obj.data.vertices) == 57*40
    matrix = obj.matrix_world.copy()
    inverse = matrix.inverted()
    original = [matrix @ v.co for v in obj.data.vertices]
    displacement = []
    for j in range(57):
        t = .25 + .75*j/56
        w = window(t)
        if w == 0:
            continue
        width = max(abs(original[j*40+k].x) for k in range(40))
        for k in range(40):
            index = j*40+k
            p = original[index].copy()
            angle = k*math.tau/40
            cross = 1-2*abs((angle+math.pi)%math.tau-math.pi)/math.pi
            inner_weight = (1-cross)/2
            # Move the cutting-side profile aft, making a deeper constructed
            # blade instead of enlarging its outer hook or bill-contact tip.
            p.y += .065*w*inner_weight
            # Broader lateral faces give the blade a plate-like cross-section.
            # Blend smoothly to the unchanged root and distal cutting tip.
            q = abs(p.x)/max(width, 1e-8)
            flattened = width*q**.58
            if abs(p.x) > 1e-9:
                p.x += math.copysign((flattened-abs(p.x))*w, p.x)
            obj.data.vertices[index].co = inverse @ p
            displacement.append((p-original[index]).length)
    obj.data.update()
    after = h['scene_snapshot']()
    assert before['empties'] == after['empties'] and before['curves'] == after['curves']
    assert set(before['meshes']) == set(after['meshes'])
    for name, prior in before['meshes'].items():
        current = after['meshes'][name]
        assert current == prior if name != NAME else all(current[k] == prior[k] for k in current if k != 'mesh'), name
    assert materials == {m.name: h['material_signature'](m) for m in bpy.data.materials}
    for j in range(57):
        t = .25 + .75*j/56
        if window(t) == 0:
            for k in range(40):
                assert (matrix @ obj.data.vertices[j*40+k].co-original[j*40+k]).length < 1e-7
        assert (matrix @ obj.data.vertices[j*40].co-original[j*40]).length < 1e-7
    OUT.mkdir(parents=True)
    AUDIT.mkdir(parents=True)
    native = OUT / 'murderbird-bill-envelope-study-v1.blend'
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(native), check_existing=False)
    bpy.ops.wm.open_mainfile(filepath=str(native))
    assert h['scene_snapshot']() == after
    shutil.copy2(__file__, AUDIT / 'executed-generator.py')
    receipt = {'status':'isolated silhouette proposal; not accepted or selected',
        'base':artifact(BASE), 'native':artifact(native), 'generator':artifact(AUDIT/'executed-generator.py'),
        'replace':[NAME], 'add':[], 'maximumVertexDisplacementM':max(displacement),
        'preservation':{'all51Pivots':True,'allOtherMeshes':True,'materialsAndOwners':True,
                        'outerHookAndTip':True,'savedReloadSnapshot':True},
        'referenceScope':'July head only: broad constructed upper bill; parameters are an authored proposal, not image metrology.',
        'limits':['No runtime export, clearance acceptance or publication.','Unchanged construction guides predate this mesh edit.']}
    (AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    receipt['views'] = renders(BASE,'before') + renders(native,'after')
    assert sha(BASE) == BASE_SHA
    (AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'native':artifact(native),'renders':len(receipt['views'])}))


if __name__ == '__main__':
    main()
