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
import struct
import zlib
from pathlib import Path
import bpy
import bmesh
import numpy as np
from mathutils import Vector

SOURCE_SHA = '72e7e53daf40b7128cdf9b173006c639bcf123952547a2576fb2de29130f06d4'


def core_gradient():
    """Authored radial amber gradient, explicit linear->sRGB PNG, packed FILE.

    The existing planar UV puts radius19.5 at UV radius .0234/.102.
    No source/reference pixels are used. No geometry or browser shader rewrite.
    """
    path = Path(__file__).resolve().parents[1]/'assets/audit/cg-supervised-optic13/attempt01/core-amber-gradient.png'
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 512
    axis = (np.arange(n, dtype=np.float32)+.5)/n-.5
    x, y = np.meshgrid(axis, axis)
    t = np.clip(np.sqrt(x*x+y*y)/(.0234/.102), 0, 1)
    f = (1-t)**1.45
    center = np.array((.48, .12, .006), dtype=np.float32)
    edge = np.array((.032, .0018, .00005), dtype=np.float32)
    linear = edge+(center-edge)*f[:,:,None]
    # Authored concentric amber optical structure, inferred from pinned crops.
    # Broad, unequal dark grooves and warm ridges; never luminous metal rings.
    ring_factor = np.ones_like(t)
    for radius, width, depth in ((.39,.027,.72),(.60,.022,.78),(.79,.032,.75),(.93,.026,.68)):
        ring_factor *= 1-depth*np.exp(-((t-radius)/width)**2)
    for radius,width,gain in ((.45,.030,.09),(.68,.026,.065),(.86,.018,.035)):
        linear += np.exp(-((t-radius)/width)**2)[:,:,None]*np.array((gain,gain*.19,gain*.007),dtype=np.float32)
    theta = np.arctan2(y,x)
    machining = .96+.04*np.sin(theta*59+t*23)*np.clip(t*2,0,1)
    linear *= (ring_factor*machining)[:,:,None]
    encoded = np.where(linear <= .0031308, linear*12.92, 1.055*np.power(linear, 1/2.4)-.055)
    pixels = np.floor(np.clip(encoded, 0, 1)*255+.5).astype(np.uint8)
    def chunk(tag, data):
        return struct.pack('>I', len(data))+tag+data+struct.pack('>I', zlib.crc32(tag+data)&0xffffffff)
    raw = b''.join(b'\x00'+row.tobytes() for row in pixels[::-1])
    png = b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR', struct.pack('>IIBBBBB', n,n,8,2,0,0,0))+chunk(b'sRGB', b'\x00')+chunk(b'IDAT', zlib.compress(raw,6))+chunk(b'IEND', b'')
    if not path.exists() or path.read_bytes() != png:
        path.write_bytes(png)
    image = bpy.data.images.load(str(path), check_existing=False)
    image.name = 'CGO13 attempt01 radial amber linear-encoded'
    image.colorspace_settings.name = 'sRGB'
    image.pack()
    return image


def apply(scene, root_path=None, era='builder'):
    if era not in ('maker', 'mechanic', 'builder', 'advanced'):
        raise ValueError(era)
    if any(o.get('cgSupervisedOptic13') for o in scene.objects):
        raise RuntimeError('Reload receiving native before optic13')
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
        'bronze': ((.135, .041, .012, 1), .82, .31),
        'glass': ((.004, .013, .006, 1), .08, .16),
        'core': ((.20, .038, .002, 1) if awakened else (.004, .006, .005, 1), .12, .24),
    }
    for role, (color, metallic, roughness) in settings.items():
        m = bpy.data.materials.new('CGO13 protected ' + role + ' ' + era)
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
            bs.inputs['Metallic'].default_value = 0
            bs.inputs['Emission Strength'].default_value = 5
            tex = m.node_tree.nodes.new('ShaderNodeTexImage')
            tex.image = core_gradient()
            uv = m.node_tree.nodes.new('ShaderNodeUVMap')
            uv.uv_map = 'optic13-local-planar'
            m.node_tree.links.new(uv.outputs['UV'], tex.inputs['Vector'])
            m.node_tree.links.new(tex.outputs['Color'], bs.inputs['Base Color'])
            m.node_tree.links.new(tex.outputs['Color'], bs.inputs['Emission Color'])
        m['cg2aPreserveMaterial'] = True
        m['opticEra'] = era
        m['cgOptic13Role'] = role
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
        d = bpy.data.meshes.new('CGO13 '+name)
        d.from_pydata(vs, [], fs)
        d.update()
        bm = bmesh.new(); bm.from_mesh(d)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(d); bm.free()
        o = bpy.data.objects.new(d.name, d); scene.collection.objects.link(o)
        o.matrix_world = frame.copy()
        family = 'protected-glass' if role == 'glass' else 'protected-optic'
        for key, value in {'cgSupervisedOptic13': True, 'cg1cRegion': 'head', 'cg2bRegion': 'head',
                           'surfaceRole': role, 'cgSurfaceFamilies': json.dumps([family]),
                           'cgProtectedMaterialSlots': '[0]', 'opticEra': era,
                           'exteriorEras': 'maker,mechanic,builder',
                           'cgConstructionStatus': 'Inferred recessed optical assembly; owner likeness pending'}.items():
            o[key] = value
        d.materials.append(mats[role])
        uv = d.uv_layers.new(name='optic13-local-planar')
        for p in d.polygons:
            p.use_smooth = True
            for li in p.loop_indices:
                q = d.vertices[d.loops[li].vertex_index].co
                uv.data[li].uv = (.5+(q.y-.005)/.102, .5+(q.z-.020)/.102)
        made.append(o)
        return o

    for side, label in ((-1, 'L'), (1, 'R')):
        # All new coordinates stay inside radius42 receiving seat; only central clearances differ from selective07 cavity.
        # Outer lip depth .167; coating recedes to .149 above retained vault.
        surface('deep tapered cavity '+label, [(42, .1613), (39, .158), (33, .154), (29, .149), (0, .149)], side, 'cavity')
        surface('unequal stepped metal retainer '+label, [(39, .1585), (37.4, .161), (34.6, .160), (33.5, .1545), (31, .1525)], side, 'metal')
        surface('recessed dark curved optical coating '+label, [(29.5, .152), (25, .1533), (23, .1517), (20.4, .1505)], side, 'glass')
        # Unequal interrupted metal rings prevent evenly luminous target graphic.
        surface('upper partial bronze retaining ring '+label, [(28.2, .154), (27.4, .1553), (26.5, .1543)], side, 'bronze', -.42, 3.64)
        surface('lower partial metal retaining ring '+label, [(22.6, .153), (21.8, .154), (21.1, .1528)], side, 'metal', 2.92, 5.94)
        surface('small core aperture collar '+label, [(21.0, .1525), (20.8, .1548), (19.8, .1548), (19.6, .153)], side, 'bronze')
        surface('small recessed awakened core '+label, [(19.5, .1525), (4.8*19.5/6.7, .1535), (0, .1539)], side, 'core')
    preservation_root=Path(root_path) if root_path is not None else Path(__file__).resolve().parents[1]
    load_module(preservation_root/'scripts/cg-supervised-preservation.py','optic13-history').retain_packed_image_ids(scene)
    bpy.context.view_layer.update()
    return {'module': 'cg-supervised-optic13', 'era': era, 'hidden_originals': hidden,
            'new_mesh_count': len(made), 'receiving_seat_radius_source_px': 42,
            'maximum_new_radius_source_px': 42, 'outer_seat_center_frame_preserved': True,
            'glass_coating_recess_from_outer_lip_m': .0137,
            'glass_shader': 'Opaque dark dielectric with clearcoat; transmission intentionally zero for browser reliability',
            'core_radius_source_px': 19.5, 'core_radius_m': .0234,
            'core_diameter_m': .0468, 'core_area_fraction_of_seat': (19.5/42)**2,
            'core_emission_strength': 5 if awakened else 0,
            'core_gradient_center_linear_rgb': [.48, .12, .006] if awakened else None,
            'core_gradient_edge_linear_rgb': [.032, .0018, .00005] if awakened else None,
            'core_gradient_exponent': 1.45 if awakened else None,
            'metal_ring_emission': 0, 'pose_changes': False, 'artistic_acceptance': 'pending'}


def basic_digest(o):
    h = hashlib.sha256()
    payload = [tuple(tuple(r) for r in o.matrix_world), o.parent.name if o.parent else None]
    if o.type == 'MESH':
        payload += [[tuple(v.co) for v in o.data.vertices], [(tuple(p.vertices), p.material_index) for p in o.data.polygons],
                    [(u.name, [tuple(v.uv) for v in u.data]) for u in o.data.uv_layers], [m.name if m else None for m in o.data.materials]]
    h.update(repr(payload).encode())
    return h.hexdigest()




def load_module(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def diagnostic():
    p=argparse.ArgumentParser();p.add_argument('--input-root',required=True);p.add_argument('--attempt',default='attempt01');p.add_argument('--stage',choices=['first','remaining','comparisons','all'],default='all')
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    root=Path(__file__).resolve().parents[1];inp=Path(args.input_root);out=root/'assets/audit/cg-supervised-optic13'/args.attempt;out.mkdir(parents=True,exist_ok=True)
    source=inp/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend'
    sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
    assert sha(source)==SOURCE_SHA
    preservation=load_module(inp/'scripts/cg-supervised-preservation.py','preservation13')
    audit=load_module(inp/'scripts/cg-supervised-body12.py','audit13')
    native=out/'murderbird-optic13.blend';receipt=out/'receipt.json'
    if args.stage in ('remaining','comparisons'):
        result=json.loads(receipt.read_text());assert sha(native)==result['nativeSHA256']
        bpy.ops.wm.open_mainfile(filepath=str(native),use_scripts=False);s=bpy.context.scene
        preservation.verify_receiving_images(result['receivingPackedImageSnapshot'])
    else:
        bpy.ops.wm.open_mainfile(filepath=str(source),use_scripts=False);s=bpy.context.scene
        original={o.name:audit.digest(o) for o in s.objects if o.type in ('MESH','EMPTY')}
        materials=audit.material_digest();images=preservation.packed_image_snapshot()
        visibility={o.name:[o.hide_render,o.hide_viewport,o.hide_get()] for o in s.objects}
        result=apply(s,inp,'builder');preservation.retain_packed_image_ids(s)
        native=out/'murderbird-optic13.blend';bpy.context.preferences.filepaths.save_version=0
        bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.wm.open_mainfile(filepath=str(native),use_scripts=False);s=bpy.context.scene
        result['earlyReceivingPackedImages']=preservation.verify_receiving_images(images)
        changed=[n for n,d in original.items() if audit.digest(s.objects[n])!=d];assert not changed,changed
        current=audit.material_digest();changedmat=[n for n,d in materials.items() if current.get(n)!=d];assert not changedmat,changedmat
        unexpected=[n for n,v in visibility.items() if [s.objects[n].hide_render,s.objects[n].hide_viewport,s.objects[n].hide_get()]!=v and n not in result['hidden_originals']];assert not unexpected,unexpected
        for o in s.objects:
            if o.get('cgSupervisedOptic13'):
                assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
                assert all(math.isfinite(c) and 0<=c<=1 for u in o.data.uv_layers for d in u.data for c in d.uv)
        result.update(sourceSHA256=sha(source),nativeSHA256=sha(native),receivingObjectsChecked=len(original),receivingObjectChanges=changed,receivingMaterialChanges=changedmat,unexpectedVisibilityChanges=unexpected,receivingPackedImageSnapshot=images,receivingPayloadDigests=original,receivingMaterialDigests=materials,newUVFiniteNormalized=True,status='Unaccepted CG proposal only',designAttempts=1,sourceCameraUncertainty='Pinned source cameras, scale and light are estimated, not calibrated',mainGoalSHA='251f2f0243181e97140179c2aff6eb057e165438',publication=False,ownerAcceptance=False,cameras={})
        receipt=out/'receipt.json';receipt.write_text(json.dumps(result,indent=2)+'\n')
        print('EARLY_PRESERVATION_PASS',len(original),len(images),flush=True)
    frozen=json.loads((inp/'assets/audit/cg-supervised01/attempt07/builder/receipt.json').read_text())['cameras']
    def render(name,q):
        c=s.camera;c.location=q['location'];c.rotation_euler=q['rotation_euler'];c.data.type=q['projection'];c.data.ortho_scale=q['ortho_scale'];c.data.shift_x,c.data.shift_y=q['shift'];c.data.lens=q['lens_mm']
        for o in list(s.objects):
            if o.type=='LIGHT':bpy.data.objects.remove(o,do_unlink=True)
        for j,a in enumerate(q['areas']):
            d=bpy.data.lights.new('Optic13 fixed diagnostic '+str(j),'AREA');d.energy=a['power'];d.color=a['color'];d.shape='SQUARE';d.size=a['size'];o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=a['location'];o.rotation_euler=a['rotation_euler']
        s.world.use_nodes=True;b=s.world.node_tree.nodes.get('Background');b.inputs['Color'].default_value=q['world_color'];b.inputs['Strength'].default_value=q['world_strength']
        s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=12;s.cycles.use_denoising=True;s.view_settings.view_transform=q['render_settings']['view_transform'];s.view_settings.look=q['render_settings']['look'];s.view_settings.exposure=0;s.view_settings.gamma=1
        s.render.resolution_x,s.render.resolution_y=q['resolution'];s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
        s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
        result['cameras'][name]={'recipe':q,'imageSHA256':sha(Path(s.render.filepath)),'lightShape':'SQUARE'};receipt.write_text(json.dumps(result,indent=2)+'\n');print('VIEW_READY',name,flush=True)
    first=['canon-workshop','head-neck'];remaining=['canon-neutral','side-profile']
    if args.stage=='comparisons':
        frozen_candidate_recipes={n:v['recipe'] for n,v in result['cameras'].items()}
        for label,attempt in [('receiving06','attempt06'),('rejected07','attempt07')]:
            bpy.ops.wm.open_mainfile(filepath=str(inp/'assets/models/cg-supervised01'/attempt/'murderbird-supervised-builder.blend'),use_scripts=False);s=bpy.context.scene
            for name,q in frozen_candidate_recipes.items():
                if name in frozen:continue # exact frozen12-sample copies already included
                render(label+'-'+name,q)
        return
    for name in first+remaining:
        if args.stage=='first' and name not in first:continue
        if args.stage=='remaining' and name not in remaining:continue
        render(name,frozen[name])
    if args.stage!='first':
        import copy
        q=copy.deepcopy(frozen['head-neck']);q['areas']=q['areas'][:1];q['areas'][0].update(location=[-3,3,3],rotation_euler=[1.1,0,-2.3],power=700,size=2.0);q['lighting']='fixed diagnostic grazing';render('head-grazing',q)
        for i in range(8):
            q=copy.deepcopy(frozen['canon-neutral']);a=math.radians(i*45);target=Vector((0,-.04,1));pos=target+Vector((6*math.sin(a),-6*math.cos(a),1.02));q['location']=list(pos);q['rotation_euler']=list((target-pos).to_track_quat('-Z','Y').to_euler());q['ortho_scale']=3.20;q['shift']=[0,0];q['resolution']=[1280,853];render('turn-%03d'%(i*45),q)
    result['sourceBinaryUnchanged']=sha(source)==SOURCE_SHA;result['savedNativeUnchangedAfterRenders']=sha(native)==result['nativeSHA256'];receipt.write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':diagnostic()
