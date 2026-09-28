"""One add-only lower-leg cage proposal from Alignment V8.

Usage inside Blender:
  blender --background --threads 1 --python scripts/study-lower-leg-construction-v1.py -- build
  blender --background --threads 1 --python scripts/study-lower-leg-construction-v1.py -- render

The source scene is hash-bound; output paths are write-once. Geometry is an
authored visual interpretation, not a recovered engineering drawing.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'assets/models/uncaged-alignment-v8/murderbird-alignment-v8.blend'
SOURCE_SHA = 'b12c442e2f517b676cdd1fae1612730cc0ba83251d34f363285b08f2cd482478'
NATIVE = ROOT / 'assets/models/uncaged-lower-leg-construction-study-v1/murderbird-lower-leg-construction-study-v1.blend'
AUDIT = ROOT / 'assets/audit/lower-leg-construction-study-v1'
NATIVE_SHA = None  # filled into audit receipt after save

parser = argparse.ArgumentParser()
parser.add_argument('mode', choices=('build', 'render', 'attachment-check', 'strict-check'))
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def object_signature(obj):
    row = {
        'name': obj.name, 'type': obj.type,
        'parent': obj.parent.name if obj.parent else None,
        'matrixWorld': [round(v, 12) for row in obj.matrix_world for v in row],
        'matrixBasis': [round(v, 12) for row in obj.matrix_basis for v in row],
        'matrixParentInverse': [round(v, 12) for row in obj.matrix_parent_inverse for v in row],
        'materials': [m.name if m else None for m in obj.data.materials] if obj.type == 'MESH' else [],
        'dataName': obj.data.name if obj.data else None,
    }
    if obj.type == 'MESH':
        me = obj.data
        row['mesh'] = {
            'vertices': len(me.vertices), 'edges': len(me.edges), 'polygons': len(me.polygons),
            'sha256': hashlib.sha256(json.dumps({
                'v': [[round(c, 10) for c in v.co] for v in me.vertices],
                'f': [list(p.vertices) for p in me.polygons],
            }, separators=(',', ':')).encode()).hexdigest(),
        }
    return row


def scene_signature():
    return {obj.name: object_signature(obj) for obj in bpy.data.objects}


def stable_material(role):
    preferred = {
        'frame': ('Neutral | frame', 'Neutral | bearing', 'Neutral | plate'),
        'bearing': ('Neutral | bearing', 'Neutral | frame', 'Neutral | plate'),
        'plate': ('Neutral | plate', 'Neutral | frame', 'Neutral | bearing'),
    }[role]
    for name in preferred:
        if bpy.data.materials.get(name):
            return bpy.data.materials[name]
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.get('surfaceRole') == role and obj.data.materials:
            return obj.data.materials[0]
    return None


def beam_vertices(a, b, u, v, hu, hv, sides=8):
    a, b = Vector(a), Vector(b)
    axis = (b-a).normalized()
    u = Vector(u) - axis * Vector(u).dot(axis)
    if u.length < 1e-8:
        u = Vector((1, 0, 0)) - axis * axis.x
    u.normalize()
    v = Vector(v) - axis * Vector(v).dot(axis) - u * Vector(v).dot(u)
    if v.length < 1e-8:
        v = axis.cross(u)
    v.normalize()
    verts = []
    for p in (a, b):
        for k in range(sides):
            angle = 2 * math.pi * k / sides
            verts.append(tuple(p + u * (hu * math.cos(angle)) + v * (hv * math.sin(angle))))
    faces = [tuple(reversed(range(sides))), tuple(range(sides, sides*2))]
    for k in range(sides):
        n = (k+1) % sides
        faces.append((k, n, sides+n, sides+k))
    return verts, faces


def add_part(name, owner, role, note, beams, era='maker,mechanic,builder'):
    verts, faces = [], []
    for a, b, u, v, hu, hv, n in beams:
        vv, ff = beam_vertices(a, b, u, v, hu, hv, n)
        base = len(verts)
        verts.extend(vv)
        faces.extend([tuple(base+i for i in f) for f in ff])
    mesh = bpy.data.meshes.new(name + ' mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    # Vertices are authored in rest-world coordinates; this matrix makes them
    # follow exactly the selected native rigid owner without changing its rest pose.
    obj.parent = owner
    obj.matrix_parent_inverse = owner.matrix_world.inverted()
    obj.matrix_basis.identity()
    obj['region'] = 'leg'
    obj['surfaceRole'] = role
    obj['exteriorEras'] = era
    obj['constructionNote'] = note
    obj['studyOwner'] = owner.name
    material = stable_material(role)
    if material:
        obj.data.materials.append(material)
    for face in mesh.polygons:
        face.use_smooth = True
    return obj


def build():
    assert SOURCE.exists() and sha(SOURCE) == SOURCE_SHA, 'Alignment V8 native hash mismatch'
    model_dir = NATIVE.parent
    assert not model_dir.exists(), 'Preserve an existing model study directory'
    assert not AUDIT.exists(), 'Preserve an existing audit directory'
    model_dir.mkdir(parents=True)
    AUDIT.mkdir(parents=True)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    before = scene_signature()
    before_objects = set(before)
    parts = []
    for side, sign in (('left', 1), ('right', -1)):
        owner = bpy.data.objects[side + '-shin']
        thigh = bpy.data.objects[side + '-thigh']
        foot = bpy.data.objects[side + '-foot']
        knee, ankle = owner.matrix_world.translation.copy(), foot.matrix_world.translation.copy()
        axis = (ankle-knee).normalized()
        across = Vector((1,0,0)) - axis * axis.x
        across.normalize()
        front = Vector((0,-1,0)) - axis * Vector((0,-1,0)).dot(axis)
        front.normalize()
        side_world = across * sign

        def centre(t, x=0.0, y=0.0):
            return knee.lerp(ankle, t) + across*x + front*y

        # Five authored parts per side: twin load members, two bearing saddles,
        # and one open anterior guard frame. All clear the neighboring joint bands.
        spar_span = (.105, .895)
        spar_x = .064
        for label, x in (('outboard', sign*.064), ('inboard', -sign*.064)):
            obj = add_part(f'{side} lower-leg {label} boxed load spar', owner, 'frame',
                'Passive closed octagonal section; rigid shin-owned member; authored proposal.',
                [(centre(spar_span[0], x, .008), centre(spar_span[1], x, .008),
                  across, front, .0105, .009, 8)])
            parts.append(obj.name)

        # Crosswise saddle bars with short returns around both spar seats. These
        # fixed intersections are assembly fittings, not independent clearance claims.
        for label, t in (('proximal', .19), ('distal', .81)):
            y = .010
            beams = [
                (centre(t, -spar_x, y), centre(t, spar_x, y), axis, front, .010, .009, 8),
                (centre(t-.025, -spar_x, y), centre(t+.025, -spar_x, y), axis, front, .008, .008, 8),
                (centre(t-.025, spar_x, y), centre(t+.025, spar_x, y), axis, front, .008, .008, 8),
            ]
            obj = add_part(f'{side} lower-leg {label} shaped bearing saddle', owner, 'bearing',
                'Passive paired spar saddle with short wrap returns; stops clear of knee and ankle races.', beams)
            parts.append(obj.name)

        # A four-sided open window sits forward of the load members. It is a
        # partial guard, leaving the central working aperture exposed.
        lo, hi, half = .32, .68, .046
        yf = .036
        beams = [
            (centre(lo, -half, yf), centre(hi, -half, yf), axis, across, .0065, .007, 8),
            (centre(lo, half, yf), centre(hi, half, yf), axis, across, .0065, .007, 8),
            (centre(lo, -half, yf), centre(lo, half, yf), axis, front, .007, .0065, 8),
            (centre(hi, -half, yf), centre(hi, half, yf), axis, front, .007, .0065, 8),
        ]
        # Diagonal returns connect each open-frame corner back to the load
        # spars, so the inspection guard has a concrete passive attachment.
        for t in (lo, hi):
            for x_guard, x_spar in ((-half, -spar_x), (half, spar_x)):
                beams.append((centre(t, x_guard, yf), centre(t, x_spar, .008),
                              across, front, .006, .006, 8))
        obj = add_part(f'{side} lower-leg partial anterior inspection guard', owner, 'plate',
            'Passive four-sided front guard; open center deliberately exposes the shank mechanism.', beams)
        parts.append(obj.name)

    after = scene_signature()
    added = sorted(set(after)-before_objects)
    assert set(added) == set(parts) and len(added) == 10
    changed = [name for name in before if before[name] != after[name]]
    assert not changed, f'Unexpected preserved-object changes: {changed[:10]}'
    bpy.ops.wm.save_as_mainfile(filepath=str(NATIVE))
    receipt = {
        'status': 'single authored add-only neutral structural proposal; visual review required',
        'source': {'path': str(SOURCE.relative_to(ROOT)), 'sha256': SOURCE_SHA},
        'native': {'path': str(NATIVE.relative_to(ROOT)), 'sha256': sha(NATIVE), 'bytes': NATIVE.stat().st_size},
        'builder': {'path': str(Path(__file__).relative_to(ROOT)), 'sha256': sha(Path(__file__))},
        'blender': bpy.app.version_string,
        'preservation': {'sourceObjectCount': len(before), 'candidateObjectCount': len(after),
            'added': added, 'modifiedOrRemovedSourceObjects': changed,
            'pivotNames': sorted(n for n in before if n.endswith(('-thigh','-shin','-foot'))),
            'meshCountSource': sum(1 for o in bpy.data.objects if o.type == 'MESH')-len(added),
            'newMeshCount': len(added), 'materialCount': len(bpy.data.materials),
            'curveCount': sum(1 for o in bpy.data.objects if o.type == 'CURVE')},
        'design': {'existingGeometryAllowlist': [], 'addedParts': parts,
            'ownership': {name: bpy.data.objects[name].parent.name for name in parts},
            'eraVisibility': {name: bpy.data.objects[name]['exteriorEras'] for name in parts},
            'contactAndTalonGeometry': 'all source objects preserved byte-equivalent by mesh/transform/object signature'},
        'limits': ['Authored neutral native geometry; not a finished or accepted model.',
            'References support paired load members and bearing brackets; hidden construction is reconstructed.',
            'Passive additions only; exact procedural drive clearances remain unverified.']}
    (AUDIT/'native-preservation-receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({'native': str(NATIVE), 'sha256': receipt['native']['sha256'], 'added': added}, indent=2))


def render():
    assert NATIVE.exists(), 'Build the native candidate first'
    assert not (AUDIT/'renders').exists(), 'Preserve any earlier render batch'
    bpy.ops.wm.open_mainfile(filepath=str(NATIVE))
    scene = bpy.context.scene
    scene.frame_set(1)
    scene.render.engine = 'BLENDER_WORKBENCH'
    shading = scene.display.shading
    shading.light = 'STUDIO'; shading.studio_light = 'paint.sl'
    shading.color_type = 'MATERIAL'; shading.show_shadows = True
    shading.show_cavity = True; shading.cavity_type = 'BOTH'
    shading.curvature_ridge_factor = 1.2; shading.curvature_valley_factor = 1.1
    shading.background_type = 'WORLD'; scene.world.color = (.11,.12,.13)
    scene.render.resolution_x = scene.render.resolution_y = 1100
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    camdata = bpy.data.cameras.new('Lower-leg study review camera')
    camera = bpy.data.objects.new('Lower-leg study review camera', camdata)
    scene.collection.objects.link(camera); scene.camera = camera
    renders = AUDIT/'renders'; renders.mkdir()
    views = [
        ('side-right', (-6,0,1.08), (0,-.1,1.08), 2.4),
        ('three-quarter', (-4.7,-6.5,2.30), (0,-.1,1.08), 2.4),
        ('feet-side', (-6,-.10,.32), (0,-.1,.31), .98),
        ('feet', (-4,-6,.6), (0,-.1,.31), .98),
    ]
    records=[]
    # Parent source images are separately hash-bound in the manifest; this
    # renderer only makes after-candidate pictures at matching fixed cameras.
    for era in ('maker','mechanic','builder'):
        for view, pos, target, scale in views:
            for obj in scene.objects:
                if obj.type=='MESH':
                    obj.hide_render = era not in obj.get('exteriorEras','maker,mechanic,builder').split(',')
                    obj.hide_set(False)
            camera.location = pos
            camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
            camdata.type='ORTHO'; camdata.ortho_scale=scale
            path=renders/f'{era}-{view}.png'
            scene.render.filepath=str(path)
            bpy.ops.render.render(write_still=True)
            records.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),'bytes':path.stat().st_size,
                'era':era,'view':view,'camera':pos,'target':target,'projection':'ORTHO','orthoScale':scale,'resolution':[1100,1100]})
    (AUDIT/'render-manifest.json').write_text(json.dumps({'status':'matched native after views; fixed rest pose',
        'nativeSha256':sha(NATIVE),'rendererSha256':sha(Path(__file__)),'blender':bpy.app.version_string,
        'lighting':'neutral Workbench paint.sl, material colors, no textures','views':records,
        'limits':['Authoring view, not browser/export appearance proof.','Fixed rest pose only; dynamic clearances are not established.']},indent=2)+'\n')
    print('Rendered',len(records),'views to',renders)


def attachment_check():
    from mathutils.bvhtree import BVHTree
    assert NATIVE.exists(), 'Build the native candidate first'
    bpy.ops.wm.open_mainfile(filepath=str(NATIVE))
    depsgraph = bpy.context.evaluated_depsgraph_get()
    guards = [bpy.data.objects[f'{side} lower-leg partial anterior inspection guard']
              for side in ('left','right')]
    added_names = {o.name for o in bpy.data.objects if o.get('constructionNote','').startswith('Passive')
                   and o.get('studyOwner')}
    trees = {}
    for ob in bpy.data.objects:
        if ob.type == 'MESH' and ob.name not in added_names:
            try:
                trees[ob.name] = BVHTree.FromObject(ob, depsgraph, epsilon=0.0)
            except Exception:
                pass
    out=[]
    for guard in guards:
        guard_tree=BVHTree.FromObject(guard,depsgraph,epsilon=0.0)
        source_rows=[]
        for name, tree in trees.items():
            if tree is None:
                continue
            nearest = None
            for v in guard.data.vertices[::max(1, len(guard.data.vertices)//1000)]:
                world = guard.matrix_world @ v.co
                hit = tree.find_nearest(world)
                if hit and (nearest is None or hit[3] < nearest['distance']):
                    nearest={'distance':hit[3], 'guardPoint':list(world), 'targetPoint':list(hit[0]),
                             'targetNormal':list(hit[1]), 'targetPolygon':hit[2]}
            if nearest:
                overlap=guard_tree.overlap(tree) if tree else []
                source_rows.append({'object':name, **nearest,'overlapTrianglePairCount':len(overlap)})
        source_rows.sort(key=lambda x:x['distance'])
        pair_rows=[]
        for name in sorted(added_names):
            if name == guard.name:
                continue
            target=bpy.data.objects.get(name)
            if not target:
                continue
            target_tree=BVHTree.FromObject(target,depsgraph,epsilon=0.0)
            nearest=None
            for v in guard.data.vertices:
                world=guard.matrix_world @ v.co
                hit=target_tree.find_nearest(world)
                if hit and (nearest is None or hit[3]<nearest['distance']):
                    nearest={'distance':hit[3],'guardPoint':list(world),'targetPoint':list(hit[0]),
                             'targetNormal':list(hit[1]),'targetPolygon':hit[2]}
            if nearest:
                overlap=guard_tree.overlap(target_tree) if target_tree else []
                pair_rows.append({'object':name,**nearest,'overlapTrianglePairCount':len(overlap)})
        pair_rows.sort(key=lambda x:x['distance'])
        out.append({'guard':guard.name,'parent':guard.parent.name if guard.parent else None,
            'closestSourceMeshes':source_rows[:12], 'closestNewFixedMembers':pair_rows,
            'directNewMemberContactsWithin10um':[r['object'] for r in pair_rows if r['distance']<=1e-5 or r['overlapTrianglePairCount']],
            'sourceGuardContactsWithin10um':[r['object'] for r in source_rows
                if 'sheath' in r['object'].lower() and (r['distance']<=1e-5 or r['overlapTrianglePairCount'])]})
    report={'status':'read-only rest-state triangle-surface nearest-distance screen',
        'nativeSha256':sha(NATIVE),'diagnosticScriptSha256':sha(Path(__file__)),
        'blender':bpy.app.version_string,'method':'sampled guard source vertices against evaluated-object BVH nearest surface plus BVHTree triangle overlap; overlap is a candidate, not a strict noncoplanar crossing receipt.',
        'guards':out,
        'limits':['Rest state only.','Vertex-to-surface nearest query does not prove swept clearance or containment.',
                  'Intended fixed saddle/spar contacts belong to the authored assembly and do not establish neighboring-pose clearance.']}
    dest=AUDIT/'guard-attachment-check.json'
    assert not dest.exists(),'Preserve an earlier attachment diagnostic'
    dest.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


def strict_check():
    import runpy
    from mathutils import Matrix
    helper_path=ROOT/'scripts/diagnose-native-regional-clearance.py'
    kernel_path=ROOT/'assets/audit/cervical-construction-study-v1/attempt-07/actual-runtime-joint-clearance-v1/executed-review.py'
    h=runpy.run_path(str(helper_path),run_name='lower_leg_clearance_helpers')
    proper=runpy.run_path(str(kernel_path),run_name='lower_leg_frozen_crossing_kernel')['proper_crossing_receipt']
    bpy.ops.wm.open_mainfile(filepath=str(NATIVE));bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get()
    guards=[bpy.data.objects[f'{side} lower-leg partial anterior inspection guard'] for side in ('left','right')]
    meshes=[o for o in bpy.data.objects if o.type=='MESH']
    surfaces={o.name:h['surface'](o,dg) for o in meshes}
    rows=[]
    for guard in guards:
        a=surfaces[guard.name];hits=[]
        for target in meshes:
            if target==guard:continue
            b=surfaces[target.name]
            if not a or not b or not h['bounds_overlap'](a,b):continue
            overlaps=a['tree'].overlap(b['tree'])
            if not overlaps:continue
            proof=proper(a,b,overlaps,Matrix.Identity(4),Matrix.Identity(4))
            strict=bool(proof['confirmedSubjectTriangleCount'] or proof['confirmedTargetTriangleCount'])
            if strict or target.get('studyOwner'):
                hits.append({'meshA':guard.name,'ownerA':guard.parent.name if guard.parent else None,
                    'meshB':target.name,'ownerB':target.parent.name if target.parent else None,
                    'triangleOverlapCandidateCount':len(overlaps),'strictNoncoplanarCrossing':strict,
                    'strictReceipt':proof if strict else None,
                    'category':'same-owner' if target.parent==guard.parent else 'different-owner',
                    'fixedAssemblyContactExpected':bool(target.get('studyOwner') and target.parent==guard.parent)})
        rows.append({'guard':guard.name,'strictOrNewMemberPairs':hits,
            'differentOwnerStrictCrossingCount':sum(x['category']=='different-owner' and x['strictNoncoplanarCrossing'] for x in hits),
            'sameOwnerStrictCrossingCount':sum(x['category']=='same-owner' and x['strictNoncoplanarCrossing'] for x in hits),
            'intendedNewAssemblyFitPairs':[x['meshB'] for x in hits if x['fixedAssemblyContactExpected'] and x['triangleOverlapCandidateCount']]})
    report={'status':'rest-state strict triangle-crossing receipt for guard only',
        'nativeSha256':sha(NATIVE),'diagnosticScriptSha256':sha(Path(__file__)),
        'surfaceHelper':{'path':str(helper_path.relative_to(ROOT)),'sha256':sha(helper_path)},
        'strictKernel':{'path':str(kernel_path.relative_to(ROOT)),'sha256':sha(kernel_path)},
        'blender':bpy.app.version_string,'rows':rows,
        'limits':['Strict noncoplanar edge-through-face crossings only; BVH candidates and coplanar/tangent contacts are excluded.',
                  'Rest only; no full containment or continuous-pose proof.']}
    dest=AUDIT/'guard-strict-crossings.json'
    assert not dest.exists(),'Preserve an earlier strict attachment report'
    dest.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'nativeSha256':report['nativeSha256'],'rows':[
        {'guard':r['guard'],'strictDifferentOwner':r['differentOwnerStrictCrossingCount'],
         'strictSameOwner':r['sameOwnerStrictCrossingCount'],'intendedFits':r['intendedNewAssemblyFitPairs'],
         'pairs':[{'meshB':p['meshB'],'strict':p['strictNoncoplanarCrossing'],'candidates':p['triangleOverlapCandidateCount']} for p in r['strictOrNewMemberPairs']]}
        for r in rows]},indent=2))


if args.mode == 'build':
    build()
elif args.mode == 'render':
    render()
elif args.mode == 'attachment-check':
    attachment_check()
else:
    strict_check()
