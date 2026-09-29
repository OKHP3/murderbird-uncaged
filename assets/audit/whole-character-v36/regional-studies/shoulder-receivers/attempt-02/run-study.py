"""Apply and render the write-once V36 shoulder receiver study."""
from pathlib import Path
import bpy, hashlib, json, math, runpy, shutil
from mathutils import Vector
import bmesh

ROOT = Path(__file__).resolve().parents[6]
BASE = ROOT / "assets/models/whole-character-v35/attempt-form01/murderbird-whole-character-v35.blend"
BASE_SHA = "d2c704ccf89f3f0e7dbeb3613dcdbdd964c4ba69991783783830803eecf59cb0"
AUDIT = ROOT / "assets/audit/whole-character-v36/regional-studies/shoulder-receivers/attempt-02"
OUT = ROOT / "assets/models/whole-character-v36/regional-studies/shoulder-receivers/attempt-02"
MODULE = ROOT / "scripts/regions/whole-character-v36-shoulder-receivers.py"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(BASE) == BASE_SHA
assert not (AUDIT / "receipt.json").exists() and not (OUT / "murderbird-v36-shoulder-receivers.blend").exists()
AUDIT.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
executed = AUDIT / "executed-shoulder-receivers.py"
shutil.copyfile(MODULE, executed)
bpy.ops.wm.open_mainfile(filepath=str(BASE))
bpy.context.view_layer.update()
CHANGED = ({f"V35 scapular receiving plate {side} {i}" for side in (-1,1) for i in range(3)}
           | {f"V35 oblique thoracic side guard {side} 0" for side in (-1,1)})

def mesh_sig(obj):
    return {
        "parent": obj.parent.name if obj.parent else None,
        "matrixWorld": tuple(tuple(float(x) for x in row) for row in obj.matrix_world),
        "vertices": tuple(tuple(float(c) for c in v.co) for v in obj.data.vertices),
        "polygons": tuple((tuple(p.vertices), p.material_index, p.use_smooth) for p in obj.data.polygons),
        "materials": tuple(m.name if m else None for m in obj.data.materials),
        "props": tuple(sorted((k, repr(v)) for k,v in obj.items())),
    }

def empty_sig(obj):
    return (obj.parent.name if obj.parent else None,
            tuple(tuple(float(x) for x in row) for row in obj.matrix_world),
            tuple(tuple(float(x) for x in row) for row in obj.matrix_local),
            tuple(sorted((k, repr(v)) for k,v in obj.items())))

before_meshes = {o.name: mesh_sig(o) for o in bpy.data.objects if o.type == 'MESH'}
before_empties = {o.name: empty_sig(o) for o in bpy.data.objects if o.type == 'EMPTY'}
before_materials = {m.name: (m.diffuse_color[:], m.use_nodes) for m in bpy.data.materials}
module = runpy.run_path(str(executed))
result = module['apply']()
bpy.context.view_layer.update()
after_meshes = {o.name: mesh_sig(o) for o in bpy.data.objects if o.type == 'MESH'}
after_empties = {o.name: empty_sig(o) for o in bpy.data.objects if o.type == 'EMPTY'}
assert before_meshes.keys() == after_meshes.keys()
assert before_empties == after_empties, "pivot/object hierarchy changed"
assert before_materials == {m.name: (m.diffuse_color[:], m.use_nodes) for m in bpy.data.materials}
changed_actual = sorted(n for n in before_meshes if before_meshes[n] != after_meshes[n])
assert changed_actual == sorted(CHANGED), (changed_actual, sorted(CHANGED))
for name in before_meshes.keys() - CHANGED:
    assert before_meshes[name] == after_meshes[name], name
volumes = {}
for name in sorted(CHANGED):
    obj = bpy.data.objects[name]
    bm = bmesh.new(); bm.from_mesh(obj.data)
    assert all(e.is_manifold for e in bm.edges), name
    vol = bm.calc_volume(signed=True)
    assert vol > 0, (name, vol)
    bm.free()
    volumes[name] = vol

native = OUT / "murderbird-v36-shoulder-receivers.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(native), check_existing=False)
assert sha(native) and sha(BASE) == BASE_SHA

scene = bpy.context.scene
scene.render.engine = 'BLENDER_WORKBENCH'
sh = scene.display.shading; sh.light = 'STUDIO'; sh.studio_light = 'paint.sl'
sh.color_type = 'SINGLE'; sh.single_color = (.56,.58,.60); sh.show_shadows = False
sh.show_cavity = True; sh.cavity_type = 'BOTH'; sh.background_type = 'WORLD'; scene.world.color = (.12,.13,.14)
scene.render.resolution_x = scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
data = bpy.data.cameras.new('V36 shoulder receiver review camera'); data.type='ORTHO'
camera = bpy.data.objects.new(data.name,data); scene.collection.objects.link(camera); scene.camera = camera
views = [
 ('reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5),
 ('front',(0,-7,1.65),(0,-.08,1.02),2.5),
 ('side',(-7,0,1.35),(0,-.08,1.02),2.5),
 ('shoulder-closeup',(-1.15,-.95,1.48),(-.30,-.04,1.19),.92),
]
view_receipts=[]
for label,pos,target,scale in views:
    camera.location = pos
    camera.rotation_euler = (Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    data.ortho_scale=scale
    dest=AUDIT/f"after-{label}.png";scene.render.filepath=str(dest)
    bpy.ops.render.render(write_still=True)
    view_receipts.append({"path":dest.relative_to(ROOT).as_posix(),"sha256":sha(dest),"bytes":dest.stat().st_size,
      "camera":{"position":pos,"target":target,"orthoScale":scale},"lighting":"neutral Workbench, same family as V35"})

receipt = {
  "status":"bounded regional shape proposal; not owner accepted or full-motion cleared",
  "base":{"path":BASE.relative_to(ROOT).as_posix(),"sha256":BASE_SHA,"bytes":BASE.stat().st_size},
  "native":{"path":native.relative_to(ROOT).as_posix(),"sha256":sha(native),"bytes":native.stat().st_size},
  "executedModule":{"path":executed.relative_to(ROOT).as_posix(),"sha256":sha(executed),"bytes":executed.stat().st_size},
  "result":result,
  "preservation":{"changedMeshes":changed_actual,"otherMeshGeometryExact":True,"emptyNodesAndTransformsExact":True,"materialsExact":True,"signedPositiveVolumesM3":volumes},
  "views":view_receipts,
  "matchedBeforeViews":[
    "assets/audit/whole-character-v35/attempt-form01/after-reference-angle.png",
    "assets/audit/whole-character-v35/attempt-form01/after-front.png",
    "assets/audit/whole-character-v35/attempt-form01/after-side.png"
  ],
  "limits":["Only fixed body-owned receiver plates changed.","No moving mantle geometry or pivots changed.","No fresh shoulder motion clearance screen; fit is unverified."]
}
(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({"native":receipt['native'],"moduleSHA256":receipt['executedModule']['sha256'],"changed":changed_actual,"views":len(view_receipts)}))
