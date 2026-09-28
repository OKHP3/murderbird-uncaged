"""Isolated swept crown-tip construction study on the frozen V8 native."""
from pathlib import Path
import hashlib
import json
import runpy
import shutil

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'assets/models/uncaged-alignment-v8/murderbird-alignment-v8.blend'
OUT = ROOT/'assets/models/uncaged-crown-edge-study-v1'
AUDIT = ROOT/'assets/audit/crown-edge-study-v1'
BASE_SHA = 'b12c442e2f517b676cdd1fae1612730cc0ba83251d34f363285b08f2cd482478'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def artifact(p):
    return {'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)}


def main():
    assert sha(BASE) == BASE_SHA
    assert not OUT.exists() and not AUDIT.exists()
    helper = ROOT/'scripts/build-uncaged-alignment-v7.py'
    assert sha(helper) == '39b6ee2285d8c49df3a902f8fac0a07589da3d41f48ae24df1e06515c839033a'
    h = runpy.run_path(str(helper),run_name='snapshot_helpers')
    bpy.ops.wm.open_mainfile(filepath=str(BASE))
    before = h['scene_snapshot']()
    materials = {m.name:h['material_signature'](m) for m in bpy.data.materials}
    names = sorted(name for name in before['meshes'] if name.startswith(('Rounded swept crown lamina ', 'Swept temporal lamina ')))
    assert len(names) == 33, names
    changed = []
    for name in names:
        obj = bpy.data.objects[name]
        assert obj.parent.name == 'cranial-cover'
        vertices = obj.data.vertices
        along = 32 if name.startswith('Rounded') else 28
        stride = 9
        layer = (along+1)*stride
        assert len(vertices) == layer*2, name
        old = [v.co.copy() for v in vertices]
        maximum = 0.0
        for skin in (0,1):
            offset = skin*layer
            for row in range(along+1):
                t = row/along
                if t <= .62:
                    continue
                u = (t-.62)/.38
                weight = u*u*(3-2*u)
                # Tighten the trailing edge to a cut metal tip. Its root and
                # fastening neighborhood remain exactly the existing mesh.
                center = sum((old[offset+row*stride+k] for k in range(stride)),Vector())/stride
                previous = sum((old[offset+(row-1)*stride+k] for k in range(stride)),Vector())/stride
                direction = (center-previous).normalized()
                width_factor = 1-.82*weight
                for column in range(stride):
                    index = offset+row*stride+column
                    updated = center+(old[index]-center)*width_factor+direction*(.012*weight)
                    vertices[index].co = updated
                    maximum = max(maximum,(updated-old[index]).length)
        obj.data.update()
        changed.append({'name':name,'maximumDisplacementM':maximum,'rootFractionUnchanged':.62})
    after = h['scene_snapshot']()
    assert before['empties'] == after['empties'] and before['curves'] == after['curves']
    assert set(before['meshes']) == set(after['meshes'])
    for name,prior in before['meshes'].items():
        current = after['meshes'][name]
        assert current == prior if name not in names else all(current[k] == prior[k] for k in current if k != 'mesh'), name
    assert materials == {m.name:h['material_signature'](m) for m in bpy.data.materials}
    OUT.mkdir(parents=True)
    AUDIT.mkdir(parents=True)
    native = OUT/'murderbird-crown-edge-study-v1.blend'
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False)
    bpy.ops.wm.open_mainfile(filepath=str(native))
    assert h['scene_snapshot']() == after
    shutil.copy2(__file__,AUDIT/'executed-generator.py')
    receipt = {'status':'isolated head-plate shape proposal; not selected','base':artifact(BASE),
        'native':artifact(native),'generator':artifact(AUDIT/'executed-generator.py'),
        'replace':names,'add':[],'geometry':changed,
        'referenceScope':'July head only: directionally swept, cut plate terminations rather than rounded leaf pads. Exact taper and length are reconstructed.',
        'preservation':{'allOtherMeshesExact':True,'allPivotsGuidesMaterialsOwnersExact':True,'savedReloadExact':True},
        'limits':['This tests plate silhouette only; orbital construction and bill remain unresolved.','No runtime export, motion clearance or artistic acceptance.']}
    (AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    renderer = runpy.run_path(str(ROOT/'scripts/study-v8-bill-envelope.py'),run_name='render_helpers')['renders']
    renderer.__globals__['AUDIT'] = AUDIT
    receipt['views'] = renderer(BASE,'before')+renderer(native,'after')
    (AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    assert sha(BASE) == BASE_SHA
    print(json.dumps({'native':artifact(native),'meshCount':len(names),'renders':len(receipt['views'])}))


if __name__ == '__main__':
    main()
