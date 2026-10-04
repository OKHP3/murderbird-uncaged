"""Inner optic construction only. Frozen completed06 retained; no source edits.

apply(scene, root_path=None, era='builder') is the integration API.
Dark optical coating uses opaque Principled/clearcoat for reliable native/glTF
response. It is a visual glass approximation, not a transmission claim.
"""
import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector

SOURCE_SHA = '72e7e53daf40b7128cdf9b173006c639bcf123952547a2576fb2de29130f06d4'


def apply(scene, root_path=None, era='builder'):
    if era not in ('maker', 'mechanic', 'builder', 'advanced'):
        raise ValueError(era)
    if any(o.get('cgSupervisedOptic07') for o in scene.objects):
        raise RuntimeError('Reload receiving native before optic07')
    frame = scene.objects['CG2b head frame'].matrix_world.copy()
    hidden = []
    patterns = ('dark optical backplate', 'broad restrained awakened iris',
                'nested warm optic ring', 'restrained pupil', 'recessed optical glass')
    for o in scene.objects:
        if o.type == 'MESH' and not o.hide_render and o.get('cgSupervisedHead05') and any(p in o.name for p in patterns):
            o.hide_render = True
            o.hide_set(True)
            hidden.append(o.name)
    awakened = era in ('builder', 'advanced')
    mats = {}
    settings = {
        'cavity': ((.003, .004, .003, 1), .32, .34),
        'metal': ((.030, .025, .015, 1), .88, .34),
        'bronze': ((.075, .041, .012, 1), .82, .31),
        'glass': ((.004, .007, .006, 1), .08, .16),
        'core': ((.20, .038, .002, 1) if awakened else (.004, .006, .005, 1), .12, .24),
    }
    for role, (color, metallic, roughness) in settings.items():
        m = bpy.data.materials.new('CGO07 protected ' + role + ' ' + era)
        m.use_nodes = True
        bs = m.node_tree.nodes.get('Principled BSDF')
        bs.inputs['Base Color'].default_value = color
        bs.inputs['Metallic'].default_value = metallic
        bs.inputs['Roughness'].default_value = roughness
        if role == 'glass':
            bs.inputs['Coat Weight'].default_value = .55
            bs.inputs['Coat Roughness'].default_value = .09
            bs.inputs['IOR'].default_value = 1.46
        if role == 'core' and awakened:
            bs.inputs['Emission Color'].default_value = (.8, .16, .007, 1)
            bs.inputs['Emission Strength'].default_value = .42
        m['cg2aPreserveMaterial'] = True
        m['opticEra'] = era
        m['cgOptic07Role'] = role
        mats[role] = m
    made = []

    def surface(name, profiles, side, role, start=0, end=math.tau):
        n = max(12, round(96 * (end-start)/math.tau))
        closed = abs(end-start-math.tau) < 1e-6
        count = n if closed else n+1
        vs = []
        loops = []
        for r, depth in profiles:
            if r == 0:
                loops.append([len(vs)])
                vs.append((side*depth, .005, .020))
            else:
                loops.append(list(range(len(vs), len(vs)+count)))
                for k in range(count):
                    a = start + (end-start)*k/n
                    vs.append((side*depth, .005-r*.0012*math.cos(a), .020-r*.0012*math.sin(a)))
        fs = []
        for aa, bb in zip(loops, loops[1:]):
            for k in range(n):
                kk = (k+1) % count
                if len(aa) == 1:
                    fs.append((aa[0], bb[kk], bb[k]))
                elif len(bb) == 1:
                    fs.append((aa[k], aa[kk], bb[0]))
                else:
                    fs.append((aa[k], aa[kk], bb[kk], bb[k]))
        if side < 0:
            fs = [tuple(reversed(f)) for f in fs]
        d = bpy.data.meshes.new('CGO07 '+name)
        d.from_pydata(vs, [], fs)
        d.update()
        bm = bmesh.new(); bm.from_mesh(d)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(d); bm.free()
        o = bpy.data.objects.new(d.name, d); scene.collection.objects.link(o)
        o.matrix_world = frame.copy()
        family = 'protected-glass' if role == 'glass' else 'protected-optic'
        for key, value in {'cgSupervisedOptic07': True, 'cg1cRegion': 'head', 'cg2bRegion': 'head',
                           'surfaceRole': role, 'cgSurfaceFamilies': json.dumps([family]),
                           'cgProtectedMaterialSlots': '[0]', 'opticEra': era,
                           'exteriorEras': 'maker,mechanic,builder',
                           'cgConstructionStatus': 'Inferred recessed optical assembly; owner likeness pending'}.items():
            o[key] = value
        d.materials.append(mats[role])
        uv = d.uv_layers.new(name='optic07-local-planar')
        for p in d.polygons:
            p.use_smooth = True
            for li in p.loop_indices:
                q = d.vertices[d.loops[li].vertex_index].co
                uv.data[li].uv = (.5+(q.y-.005)/.102, .5+(q.z-.020)/.102)
        made.append(o)
        return o

    for side, label in ((-1, 'L'), (1, 'R')):
        # All new coordinates stay inside radius42 receiving seat.
        # Outer lip depth .167; coating recedes to .149 above retained vault.
        surface('deep tapered cavity '+label, [(42, .1607), (39, .158), (33, .154), (29, .149), (0, .149)], side, 'cavity')
        surface('unequal stepped metal retainer '+label, [(39, .1585), (37.4, .161), (34.6, .160), (33.5, .1545), (31, .1525)], side, 'metal')
        surface('recessed dark curved optical coating '+label, [(29.5, .152), (25, .1533), (18, .1517), (8, .1505)], side, 'glass')
        # Unequal interrupted metal rings prevent evenly luminous target graphic.
        surface('upper partial bronze retaining ring '+label, [(28.2, .154), (27.4, .1553), (26.5, .1543)], side, 'bronze', -.42, 3.64)
        surface('lower partial metal retaining ring '+label, [(22.6, .153), (21.8, .154), (21.1, .1528)], side, 'metal', 2.92, 5.94)
        surface('small core aperture collar '+label, [(10.1, .1525), (9.4, .1548), (7.5, .1548), (6.8, .153)], side, 'bronze')
        surface('small recessed awakened core '+label, [(6.7, .1525), (4.8, .1535), (0, .1539)], side, 'core')
    bpy.context.view_layer.update()
    return {'module': 'cg-supervised-optic07', 'era': era, 'hidden_originals': hidden,
            'new_mesh_count': len(made), 'receiving_seat_radius_source_px': 42,
            'maximum_new_radius_source_px': 42, 'outer_seat_center_frame_preserved': True,
            'glass_coating_recess_from_outer_lip_m': .0137,
            'glass_shader': 'Opaque dark dielectric with clearcoat; transmission intentionally zero for browser reliability',
            'core_radius_source_px': 6.7, 'core_emission_strength': .42 if awakened else 0,
            'metal_ring_emission': 0, 'pose_changes': False, 'artistic_acceptance': 'pending'}


def digest(o):
    h = hashlib.sha256()
    payload = [tuple(tuple(r) for r in o.matrix_world), o.parent.name if o.parent else None]
    if o.type == 'MESH':
        payload += [[tuple(v.co) for v in o.data.vertices], [(tuple(p.vertices), p.material_index) for p in o.data.polygons],
                    [(u.name, [tuple(v.uv) for v in u.data]) for u in o.data.uv_layers], [m.name if m else None for m in o.data.materials]]
    h.update(repr(payload).encode())
    return h.hexdigest()


def diagnostic():
    p = argparse.ArgumentParser(); p.add_argument('--input-root', required=True); p.add_argument('--attempt', default='attempt01')
    args = p.parse_args(sys.argv[sys.argv.index('--')+1:])
    root = Path(__file__).resolve().parents[1]; inp = Path(args.input_root)
    out = root/'assets/audit/cg-supervised-optic07'/args.attempt; out.mkdir(parents=True, exist_ok=True)
    source = inp/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend'
    sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
    assert sha(source) == SOURCE_SHA
    bpy.ops.wm.open_mainfile(filepath=str(source)); s = bpy.context.scene
    original = {o.name: digest(o) for o in s.objects if o.type in ('MESH', 'EMPTY')}
    initial_visibility = {o.name: (o.hide_render, o.hide_get()) for o in s.objects}
    cam = s.camera
    q = json.loads((inp/'assets/audit/cg-supervised-camera04/receipt.json').read_text())['hypotheses']['ortho-35']['camera']
    s.render.engine = 'CYCLES'; s.cycles.device = 'CPU'; s.cycles.samples = 6; s.cycles.use_denoising = True
    s.render.resolution_percentage = 100; s.render.image_settings.file_format = 'PNG'
    views = {}
    lights = [{'name': o.name, 'location': list(o.location), 'energy': o.data.energy, 'color': list(o.data.color), 'type': o.data.type} for o in s.objects if o.type == 'LIGHT']
    def render(name, close=False, clay=False):
        cam.location = q['location']; cam.rotation_euler = q['rotation_euler']; cam.data.type = 'ORTHO'; cam.data.ortho_scale = q['ortho_scale']; cam.data.shift_x, cam.data.shift_y = q['shift']
        s.render.resolution_x = 1280; s.render.resolution_y = 853
        if close:
            target = s.objects['CG2b head frame'].matrix_world @ Vector((-.15, .005, .020))
            direction = cam.rotation_euler.to_matrix() @ Vector((0, 0, -1))
            cam.location = target-direction*6; cam.data.ortho_scale = .62; cam.data.shift_x = cam.data.shift_y = 0
        s.view_layers[0].material_override = claymat if clay else None
        views[name] = {'location': list(cam.location), 'rotation': list(cam.rotation_euler), 'scale': cam.data.ortho_scale, 'shift': [cam.data.shift_x, cam.data.shift_y], 'clay': clay}
        s.render.filepath = str(out/(name+'.png')); bpy.ops.render.render(write_still=True)
    claymat = bpy.data.materials.new('Optic07 diagnostic clay'); claymat.use_nodes = True
    claymat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value = (.25, .25, .25, 1)
    claymat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value = .64
    render('before-whole'); render('before-head', True)
    render('before-whole-clay', clay=True); render('before-head-clay', True, True)
    s.view_layers[0].material_override = None
    result = apply(s, inp, 'builder')
    render('after-whole'); render('after-head', True); render('after-head-clay', True, True); render('after-whole-clay', clay=True)
    render('after-whole')
    s.view_layers[0].material_override = None
    assert all(digest(s.objects[n]) == d for n, d in original.items())
    unexpected = [n for n, v in initial_visibility.items() if (s.objects[n].hide_render, s.objects[n].hide_get()) != v and n not in result['hidden_originals']]
    assert not unexpected
    native = out/'murderbird-optic07.blend'; bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(native)); bpy.ops.wm.open_mainfile(filepath=str(native)); s = bpy.context.scene
    assert all(digest(s.objects[n]) == d for n, d in original.items())
    finite = []
    for o in s.objects:
        if not o.get('cgSupervisedOptic07'): continue
        ev = o.evaluated_get(bpy.context.evaluated_depsgraph_get()); md = ev.to_mesh()
        assert all(math.isfinite(c) for v in md.vertices for c in v.co)
        assert all(math.isfinite(c) and 0 <= c <= 1 for u in md.uv_layers for d in u.data for c in d.uv)
        finite.append(o.name); ev.to_mesh_clear()
    spec = importlib.util.spec_from_file_location('export07', inp/'scripts/cg-supervised-export.py'); exporter = importlib.util.module_from_spec(spec); spec.loader.exec_module(exporter)
    export_receipt = exporter.export(s, out/'murderbird-optic07.glb')
    result.update(sourceSHA256=sha(source), nativeSHA256=sha(native), originalObjectsChecked=len(original), savedNativeReadback='PASS', originalDataChanges=[], unexpectedVisibilityChanges=unexpected, evaluatedFiniteNormalizedUV=finite, cameras=views, lights=lights, nativeRenderer={'engine': s.render.engine, 'samples': s.cycles.samples, 'viewTransform': s.view_settings.view_transform, 'exposure': s.view_settings.exposure}, export=export_receipt)
    (out/'receipt.json').write_text(json.dumps(result, indent=2)+'\n')
    print('OPTIC07_COMPLETE', out)


if __name__ == '__main__':
    diagnostic()
