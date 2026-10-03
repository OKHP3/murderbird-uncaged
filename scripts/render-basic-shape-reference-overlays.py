"""Register study05 against untouched sources using cameras only; render alpha layers.

Run with Blender --background --threads 4 --python this-file.py.
No mesh edits, source warps, texture transfer or detailed-model changes.
"""
import hashlib
import json
import os
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/audit/basic-shape-reference-overlay01'
OUT.mkdir(parents=True, exist_ok=True)
INPUT = ROOT / 'assets/audit/basic-shape-study05/murderbird-basic-shapes.blend'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
source_hash = sha(INPUT)
bpy.ops.wm.open_mainfile(filepath=str(INPUT))
s = bpy.context.scene
meshes = [o for o in s.objects if o.type == 'MESH']
def signature():
    return hashlib.sha256(json.dumps([
        [o.name, list(map(list, o.matrix_world)), [list(v.co) for v in o.data.vertices],
         [list(p.vertices) for p in o.data.polygons]]
        for o in sorted(meshes, key=lambda o:o.name)
    ], sort_keys=True).encode()).hexdigest()
geometry_hash = signature()
s.render.film_transparent = True
s.render.image_settings.color_mode = 'RGBA'
s.display.shading.show_object_outline = True
s.display.shading.object_outline_color = (.03, .04, .05)
records = []
specs = [
    dict(id='canon', path='assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg',
         sha256='645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114',
         size=[1280,853], target_box=[548,26,1034,826], parts=None,
         scope='Full-bird canon. All study05 parts shown without deformation.'),
    dict(id='july-head', path='context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png',
         sha256='47658dba6496f2c8594a40ad412a8bfaa087939e90044d1597329a27ca68d4e9',
         size=[1024,1536], target_box=[527,47,985,459], parts=['head'],
         scope='Head identity only. Review crop excludes July body and wings.'),
]
for spec in specs:
    source = ROOT / spec['path']
    assert sha(source) == spec['sha256'], source
    for o in meshes:
        o.hide_render = spec['parts'] is not None and o.get('study_part') not in spec['parts']
    visible = [o for o in meshes if not o.hide_render]
    width,height = spec['size']
    s.render.resolution_x, s.render.resolution_y = width,height
    s.render.resolution_percentage = 100
    data = bpy.data.cameras.new(spec['id']+' estimated source view')
    cam = bpy.data.objects.new(spec['id']+' estimated source view',data)
    s.collection.objects.link(cam)
    data.type = 'ORTHO'
    data.ortho_scale = 2.0
    target = Vector((0,-.04,.92))
    cam.location = target+Vector((-6,-2.1,1.05))
    cam.rotation_euler = (target-cam.location).to_track_quat('-Z','Y').to_euler()
    s.camera = cam
    bpy.context.view_layer.update()
    def projected_bounds():
        points=[]
        dg=bpy.context.evaluated_depsgraph_get()
        for o in visible:
            eo=o.evaluated_get(dg)
            for v in eo.data.vertices:
                p=world_to_camera_view(s,cam,eo.matrix_world@v.co)
                points.append((p.x*width,(1-p.y)*height))
        return [min(p[0] for p in points),min(p[1] for p in points),
                max(p[0] for p in points),max(p[1] for p in points)]
    box=projected_bounds()
    tx0,ty0,tx1,ty1=spec['target_box']
    # Uniform size from crown-to-sole (or crown-to-bill-tip for head).
    # X only centres the complete silhouette. No region-specific scale fitting.
    data.ortho_scale *= (box[3]-box[1])/(ty1-ty0)
    bpy.context.view_layer.update()
    box=projected_bounds()
    dx=(tx0+tx1-box[0]-box[2])/2
    dy=(ty0+ty1-box[1]-box[3])/2
    # Calibrate shift axes numerically to preserve Blender aspect conventions.
    data.shift_x=.1
    shifted=projected_bounds()
    data.shift_x=.1*dx/(shifted[0]-box[0])
    data.shift_y=.1
    shifted=projected_bounds()
    data.shift_y=.1*dy/(shifted[1]-box[1])
    bg=data.background_images.new()
    bg.image=bpy.data.images.load(str(source),check_existing=True)
    bg.image.filepath='//'+os.path.relpath(source,OUT)
    bg.alpha=.5
    bg.display_depth='FRONT'
    bg.frame_method='STRETCH'
    data.show_background_images=True
    s.render.filepath=str(OUT/(spec['id']+'-model.png'))
    bpy.ops.render.render(write_still=True)
    records.append(dict(**spec, model_layer=spec['id']+'-model.png',
        alignment='Estimated orthographic camera; uniform height registration and silhouette-centre translation only.',
        camera=dict(location=list(cam.location),rotation_euler=list(cam.rotation_euler),
                    ortho_scale=data.ortho_scale,shift_x=data.shift_x,shift_y=data.shift_y),
        projected_model_box=projected_bounds()))
assert signature()==geometry_hash
assert sha(INPUT)==source_hash
for o in meshes:o.hide_render=False
s.camera=bpy.data.objects['canon estimated source view']
s.render.resolution_x,s.render.resolution_y=1280,853
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'murderbird-reference-overlay.blend'))
(OUT/'registration.json').write_text(json.dumps(dict(
    status='Proposed alignment for owner review; likeness not accepted',
    input_model=str(INPUT.relative_to(ROOT)),input_sha256=source_hash,
    geometry_signature=geometry_hash,geometry_preserved=True,
    sources=records,limitations=[
        'Source camera intrinsics are unknown; view angle is an estimate.',
        'Source art includes armour and talons absent from the simplified masses.',
        'July framing is head-only; body, wing and stance are excluded.',
        'No texture projection, hidden-surface inference or detailed-CG edits in this checkpoint.'
    ]),indent=2)+'\n')
