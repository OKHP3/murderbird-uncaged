"""Rebuild the private First Choice derivative in Blender from the exact retained04 source.

blender -b media/cg-retained04-builder-murderbird-recursive-builder.blend \
  --python-exit-code 1 -P atelier/finish/build_candidate.py -- --out ../candidate
"""
import argparse
from collections import defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import bpy

ATELIER=Path(__file__).resolve().parent.parent
SRC_HASH='9de7c4d1c9ac158135f9f846af61683528e00340a708820b2cfe1d942acc54d5'
args=argparse.ArgumentParser()
args.add_argument('--out',type=Path,required=True)
args.add_argument('--still-only',action='store_true',help="Omit glTF and render a draft studio still")
args.add_argument('--baseline',action='store_true',help="Look development only, leave retained04 geometry intact")
opt=args.parse_args(sys.argv[sys.argv.index('--')+1:])
out=opt.out.resolve()
out.mkdir(parents=True,exist_ok=True)
if hashlib.file_digest(open(bpy.data.filepath,'rb'),'sha256').hexdigest()!=SRC_HASH:
    raise ValueError("This build requires the pinned retained04 Advanced native file.")
def load(relative, name):
    path=ATELIER/relative
    spec=importlib.util.spec_from_file_location(path.stem,path)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    return getattr(mod,name)

scene=bpy.context.scene
if not opt.baseline:
    load('head/cranial.py','apply_head')()
    load('mantle/mantle.py','apply_mantle')()
    load('pedal/pedal.py','apply_pedal')()
apply_motion=load('motion/first_choice.py','apply_motion')
motion=apply_motion() if opt.baseline else apply_motion(load('head/reach.py','apply_reach')())
scene.frame_set(0)
bpy.context.view_layer.update()

# Keep the native source file intact. Remove dormant historical variants only in this derivative.
keep=[ob for ob in scene.objects if
      (ob.type=='MESH' and ob.parent and ob.parent in list(motion['anchors'].values()) and not ob.hide_render)
      or ob in list(motion['anchors'].values())]
kept=set(keep)
other=[ob for ob in bpy.data.objects if ob not in kept]
bpy.data.batch_remove(other)
objects=[ob for ob in keep if ob.type=='MESH']
print("Kept mounted assembly:",len(objects),flush=True)
load('finish/metal.py','apply_finish')(objects)
measurements=load('finish/cavity.py','apply_cavity')(objects)
(out/'surface-evidence.json').write_text(json.dumps(measurements,indent=2,default=str))
# Rehouse mounted pieces and free historical material libraries from the derivative.
# The full native donor remains available at its pinned path and byte identity.
for key,anchor in motion['anchors'].items():
    col=bpy.data.collections.new("Mounted · "+key.title())
    scene.collection.children.link(col)
    for ob in [anchor]+[obj for obj in objects if obj.parent==anchor]:
        for old in list(ob.users_collection): old.objects.unlink(ob)
        col.objects.link(ob)
for col in list(bpy.data.collections):
    if not col.name.startswith("Mounted · "): bpy.data.collections.remove(col)
for ob in objects:
    for prop in list(ob.keys()):
        if prop not in {'fc_region','fc_rigid','first_choice_region','cg1cRegion','surfaceRole'}:
            del ob[prop]
bpy.context.view_layer.update()

floor,cam=load('finish/studio.py','studio')()
# Drop obsolete donor image/material blocks, scene texts and unused packed data.
scene.world.use_fake_user=False
for textblock in list(bpy.data.texts): bpy.data.texts.remove(textblock)
for seq in [bpy.data.images,bpy.data.materials,bpy.data.meshes,bpy.data.worlds,bpy.data.actions]:
    for datablock in seq:
        if datablock.use_fake_user: datablock.use_fake_user=False
bpy.ops.outliner.orphans_purge(do_recursive=True)
scene['project']='MurderBird: Uncaged'
scene['candidate']='First Choice · Advanced · private production candidate'
scene['source_sha256']=SRC_HASH
scene['rights']='MurderBird character and creative assets © OverKill Hill P³. All rights reserved.'
scene.render.filepath='//first-choice-still.jpg'
bpy.ops.object.select_all(action='DESELECT')
bpy.context.view_layer.objects.active=motion['anchors']['torso']
if opt.still_only:
    scene.render.resolution_percentage=65
    scene.cycles.samples=12
    scene.render.filepath=str(out/'studio-test.jpg')
    bpy.ops.render.render(write_still=True)
    sys.exit(0)

bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(out/'first-choice.blend'),compress=True)

# Frozen native source retains every individual casting. Batch only the runtime geometry.
# Keep subassemblies separate across pivots (and separate the feet from the upper legs).
def detail(ob):
    region=ob.get('first_choice_region') or ob.get('cg1cRegion') or ob.get('fc_region') or 'assembly'
    if ob.get('fc_rigid')=='fixed' and region=='fixed': region='foot'
    return str(region).lower()
groups=defaultdict(list)
for o in objects: groups[(o.parent.name,detail(o))].append(o)
dg=bpy.context.evaluated_depsgraph_get()
for (anchor_name,region),pieces in groups.items():
    parent=bpy.data.objects[anchor_name]
    pieces.sort(key=lambda x:x.name)
    # Replace meshes with evaluated, incidence-preserving copies in place. Protect optic UVs.
    for ob in pieces:
        ev=ob.evaluated_get(dg)
        prepared=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=dg)
        ob.modifiers.clear();ob.data=prepared
        if all((s.material and not s.material.name.startswith('CGO13')) for s in ob.material_slots):
            for uv in list(prepared.uv_layers):
                if uv.name!='FirstChoiceSurface': prepared.uv_layers.remove(uv)
        for attr in list(prepared.color_attributes):
            if attr.name!='FC_Occlusion': prepared.color_attributes.remove(attr)
    bpy.ops.object.select_all(action='DESELECT')
    for ob in pieces: ob.select_set(True)
    base=pieces[0]
    bpy.context.view_layer.objects.active=base
    if len(pieces)>1: bpy.ops.object.join()
    base.name=f"{anchor_name.removeprefix('FC | ')} – {region}"
    for key in list(base.keys()): del base[key]
    base['region']=region
bpy.context.view_layer.update()
bpy.ops.object.select_all(action='DESELECT')
for ob in scene.objects:
    if ob in motion['anchors'].values() or (ob.type=='MESH' and ob.parent is not None): ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'first-choice.glb'),export_format='GLB',use_selection=True,
  export_animations=True,export_animation_mode='NLA_TRACKS',export_frame_range=True,export_frame_step=1,
  export_optimize_animation_size=True,export_apply=False,export_cameras=False,export_lights=False,
  export_vertex_color='MATERIAL',export_all_influences=False,export_image_format='AUTO',export_extras=True,
  export_copyright='MurderBird character and creative assets © OverKill Hill P³. All rights reserved.')
print("Candidate exported.",flush=True)
