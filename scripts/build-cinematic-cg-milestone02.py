"""Milestone 2 silhouette refinements; preserve accepted 1C, cameras and materials."""
from pathlib import Path
import bpy, json, math, hashlib, importlib.util, argparse, sys, datetime
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--attempt',default='attempt01')
parser.add_argument('--mode',choices=['candidate','lowres','previous'],default='candidate')
parser.add_argument('--era',choices=['maker','mechanic','builder'],default='builder')
parser.add_argument('--final',action='store_true')
parser.add_argument('--resolution',type=int,default=640)
parser.add_argument('--samples',type=int,default=16)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
AUDIT=ROOT/'assets/audit/cinematic-cg-milestone02'
ASSET=ROOT/'assets/models/cinematic-cg-milestone02'
OUT=AUDIT/(args.attempt if args.mode=='candidate' else args.mode)
if args.era!='builder':OUT=OUT/args.era
OUT.mkdir(parents=True,exist_ok=True);ASSET.mkdir(parents=True,exist_ok=True)
INPUT=ROOT/f'assets/models/cinematic-cg-milestone01c/murderbird-cg-1c-{args.era}.blend'
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert SHA(INPUT)=={'builder': 'ff6362e6fc79995b088407f1ef0d3180afc2b7cedd89c3d738b0a172fdeb6b5a', 'maker': 'e09ee61c87794d1d7547291ba62866ddaab9b9a6ff05bfa1acf7257f91cffee6', 'mechanic': 'a0f6e247377f7b31e1864b64dcab347b7ddee632de141377e8d582692b9dd5c9'}[args.era]
input_sha=SHA(INPUT)
OLD=INPUT
old_sha=SHA(OLD)
bpy.ops.wm.open_mainfile(filepath=str(OLD if args.mode=='previous' else INPUT))
s=bpy.context.scene
for o in list(s.objects):
    if o.type in ('LIGHT','CAMERA'):
        bpy.data.objects.remove(o,do_unlink=True)
    # Retain hidden superseded guide objects from accepted1C.
receipt=dict(status='Owner review pending; proposed CG character',mode=args.mode,
             attempt=args.attempt,era=args.era,geometry_input=str(INPUT.relative_to(ROOT)),
             input_sha256=input_sha,previous_detailed_sha256=old_sha,changes={})
def module(name):
    path=ROOT/f'scripts/cinematic-cg-2-{name}.py'
    spec=importlib.util.spec_from_file_location('cg1c_'+name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
if args.mode=='candidate':
    receipt['changes']['head']=module('head').apply(s,ROOT/'assets/audit/basic-shape-study05/murderbird-basic-shapes.blend',args.era)
    receipt['changes']['body']=module('body').apply(s,ROOT/'assets/audit/basic-shape-study05/murderbird-basic-shapes.blend',args.era)
    receipt['materials']='Unchanged packed 1C regional materials; no surface pass'

s.render.engine='CYCLES';s.cycles.samples=args.samples;s.cycles.use_denoising=True
s.cycles.device='CPU';s.render.image_settings.file_format='PNG'
s.render.image_settings.color_mode='RGBA';s.render.film_transparent=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
s.world=bpy.data.worlds.new('1c comparison world');s.world.use_nodes=True
bg=s.world.node_tree.nodes['Background'];bg.inputs[0].default_value=(.08,.08,.08,1)
neutral=[((-3,-4,5),700,4),((4,-1,3),250,4),((0,4,4),500,3)]
lights=[]
for i,(pos,power,size) in enumerate(neutral):
    data=bpy.data.lights.new('1c comparison '+str(i),'AREA');data.energy=power;data.size=size
    obj=bpy.data.objects.new(data.name,data);s.collection.objects.link(obj);obj.location=pos
    obj.rotation_euler=(Vector((0,0,1))-obj.location).to_track_quat('-Z','Y').to_euler();lights.append(data)
data=bpy.data.cameras.new('1c camera');data.type='ORTHO'
cam=bpy.data.objects.new('1c camera',data);s.collection.objects.link(cam);s.camera=cam
reg=json.loads((ROOT/'assets/audit/basic-shape-reference-overlay01/registration.json').read_text())
canon=reg['sources'][0]['camera']
def lighting(name):
    if name=='neutral':
        bg.inputs[1].default_value=.4
        for d,(_,power,_) in zip(lights,neutral):d.energy=power;d.color=(1,1,1)
    else:
        bg.inputs[1].default_value=.08
        for d,p,c in zip(lights,[450,65,150],[(1,.82,.65),(.62,.74,.85),(1,.7,.45)]):d.energy=p;d.color=c
def render(name,size,position=None,target=None,scale=None,registration=None,light='neutral'):
    lighting(light)
    s.render.resolution_x,s.render.resolution_y=size;s.render.resolution_percentage=100
    data.shift_x=data.shift_y=0
    if registration:
        cam.location=registration['location'];cam.rotation_euler=registration['rotation_euler']
        data.ortho_scale=registration['ortho_scale'];data.shift_x=registration['shift_x'];data.shift_y=registration['shift_y']
    else:
        cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=scale
    s.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
    receipt.setdefault('cameras',{})[name]=dict(location=list(cam.location),rotation_euler=list(cam.rotation_euler),ortho_scale=data.ortho_scale,shift_x=data.shift_x,shift_y=data.shift_y,resolution=list(size),lighting=light)

# Aspect and projection exactly match the registered low-res/source layers.
w=args.resolution;landscape=(w,round(w*853/1280));portrait=(round(w*.75),w)
render('canon-neutral',landscape,registration=canon)
render('canon-workshop',landscape,registration=canon,light='workshop')
# Old 1b camera uses its original scale, target and illumination for both assets.
# A common exposure/look is used when 1b is re-rendered by this script.
legacy=(-6,-3.5,2.75);target=(0,-.08,.87)
render('legacy-neutral',portrait,legacy,target,2.25)
if args.final:
    render('legacy-workshop',portrait,legacy,target,2.25,light='workshop')
    for i in range(8):
        a=math.radians(i*45);center=Vector((0,-.04,.92))
        pos=center+Vector((6*math.sin(a),-6*math.cos(a),1.02))
        render(f'angle-{i*45:03d}',portrait,pos,center,2.10)
    render('head-closeup',portrait,(-6,-2.14,2.15),(0,-.28,1.58),.77,light='workshop')
    render('body-closeup',portrait,(-6,-2.14,1.55),(0,.01,.98),1.22,light='workshop')
    render('side-profile',portrait,(-6,0,.94),(0,0,.94),2.08)
if args.final:
    original_slots={o:[m for m in o.data.materials] for o in s.objects if o.type=='MESH' and not o.hide_render}
    silhouette=bpy.data.materials.new('Temporary black silhouette');silhouette.use_nodes=True
    node=silhouette.node_tree.nodes.get('Principled BSDF');node.inputs['Base Color'].default_value=(0,0,0,1);node.inputs['Roughness'].default_value=1;node.inputs['Specular IOR Level'].default_value=0
    world_color=tuple(bg.inputs[0].default_value)
    bg.inputs[0].default_value=(1,1,1,1)
    for o in original_slots:
        o.data.materials.clear();o.data.materials.append(silhouette)
    for i in range(8):
        a=math.radians(i*45);center=Vector((0,-.04,.92));pos=center+Vector((6*math.sin(a),-6*math.cos(a),1.02))
        render(f'silhouette-{i*45:03d}',portrait,pos,center,2.10)
    for o,mats in original_slots.items():
        o.data.materials.clear()
        for m in mats:o.data.materials.append(m)
    bg.inputs[0].default_value=world_color;bpy.data.materials.remove(silhouette)
    # Restore same authored neutral hero camera for editable native file.
    cam.location=legacy;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=2.25
if args.mode=='candidate':
    # No reference art or guide/scaffold alternatives enter the GLB.
    bpy.ops.object.select_all(action='DESELECT')
    visible=[]
    for o in s.objects:
        if o.type=='MESH' and not o.hide_render and not o.get('authoringGuide'):
            o.hide_viewport=False;o.hide_set(False);o.select_set(True);visible.append(o)
    receipt['visible_meshes']=len(visible)
    receipt['visible_geometry_bounds']={a:[min((o.matrix_world@Vector(v))[i] for o in visible for v in o.bound_box),max((o.matrix_world@Vector(v))[i] for o in visible for v in o.bound_box)] for i,a in enumerate(('x','y','z'))}
    receipt['optic_emission']={o.name:o.data.materials[0].node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value for o in visible if o.get('surfaceRole')=='optic'}
    # Editable native parts remain separate. Export temporary evaluated meshes
    # joined by material to avoid thousands of browser draw calls.
    bpy.ops.object.select_all(action='DESELECT')
    export_collection=bpy.data.collections.new('Temporary optimized export')
    s.collection.children.link(export_collection)
    groups={};export_materials={};export_images={}
    dg=bpy.context.evaluated_depsgraph_get()
    for o in visible:
        source_mat=o.data.materials[0]
        if source_mat.name not in export_materials:
            mat=source_mat.copy();mat.name='GLB1024 '+source_mat.name
            for n in mat.node_tree.nodes:
                if n.type=='TEX_IMAGE' and n.image:
                    if n.image.name not in export_images:
                        im=n.image.copy();im.name='GLB1024 '+n.image.name
                        im.scale(1024,1024);im.pack();export_images[n.image.name]=im
                    n.image=export_images[n.image.name]
            export_materials[source_mat.name]=mat
        mesh=bpy.data.meshes.new_from_object(o.evaluated_get(dg),depsgraph=dg)
        if mesh.uv_layers:mesh.uv_layers.active.name='cg1c-uv'
        mesh.materials.clear();mesh.materials.append(export_materials[source_mat.name])
        for p in mesh.polygons:p.material_index=0
        dup=bpy.data.objects.new('Export '+o.name,mesh);export_collection.objects.link(dup)
        dup.matrix_world=o.matrix_world.copy();groups.setdefault(source_mat.name,[]).append(dup)
    merged=[]
    for name,objects in groups.items():
        bpy.ops.object.select_all(action='DESELECT')
        for o in objects:o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0]
        bpy.ops.object.join();o=bpy.context.object;o.name='1c '+name;merged.append(o)
    bpy.ops.object.select_all(action='DESELECT')
    for o in merged:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(ASSET/f'murderbird-cg-2-{args.era}.glb'),export_format='GLB',use_selection=True,export_extras=False,export_apply=True,export_materials='EXPORT')
    receipt['browser_export']=dict(mesh_groups=len(merged),material_groups=list(groups),texture_resolution=1024,native_texture_resolution=2048,method='Evaluated temporary geometry joined by material; normalized UV names; native parts unchanged')
    for o in merged:bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.collections.remove(export_collection)
    for m in export_materials.values():bpy.data.materials.remove(m)
    for im in export_images.values():bpy.data.images.remove(im)
    for img in bpy.data.images:
        if img.source=='FILE':
            try:img.pack()
            except RuntimeError:pass
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET/f'murderbird-cg-2-{args.era}.blend'))
assert SHA(INPUT)==input_sha and SHA(OLD)==old_sha
receipt['source_preserved']=True
receipt['created_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
receipt['image_hashes']={p.name:SHA(p) for p in OUT.glob('*.png')}
(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('CG2_COMPLETE',OUT)
