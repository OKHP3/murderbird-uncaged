"""Milestone 2a photorealism; preserve approved posture and source assets."""
from pathlib import Path
import bpy, json, math, hashlib, importlib.util, argparse, sys, datetime
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--attempt',default='attempt01')
parser.add_argument('--mode',choices=['candidate','lowres','previous'],default='candidate')
parser.add_argument('--era',choices=['maker','mechanic','builder'],default='builder')
parser.add_argument('--final',action='store_true')
parser.add_argument('--stage-only',action='store_true')
parser.add_argument('--resolution',type=int,default=640)
parser.add_argument('--samples',type=int,default=16)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
AUDIT=ROOT/'assets/audit/cinematic-cg-milestone02a'
ASSET=ROOT/'assets/models/cinematic-cg-milestone02a'
OUT=AUDIT/(args.attempt if args.mode=='candidate' else args.mode)
if args.era!='builder':OUT=OUT/args.era
OUT.mkdir(parents=True,exist_ok=True);ASSET.mkdir(parents=True,exist_ok=True)
INPUT=ROOT/f'assets/models/cinematic-cg-milestone03/murderbird-cg-3-{args.era}.blend'
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert SHA(INPUT)=={'builder': '12b70d4b1b3358bf0f8c5d0512653b4116983764ae73f8a2cc273c86c859747e', 'maker': 'b02f254535035ce96c761becf2b2eb33ad91690b6d63050f21776d505b667ae3', 'mechanic': 'cdf01bdc19ea087140a10f6eb5c4e658435c808a546238bd68190624fa2a65b0'}[args.era]
input_sha=SHA(INPUT)
OLD=INPUT
old_sha=SHA(OLD)
bpy.ops.wm.open_mainfile(filepath=str(OLD if args.mode=='previous' else INPUT))
s=bpy.context.scene
for o in list(s.objects):
    if o.type in ('LIGHT','CAMERA'):
        bpy.data.objects.remove(o,do_unlink=True)
    # Retain hidden superseded guide objects from accepted1C.
def character_bounds():
    bpy.context.view_layer.update()
    objects=[o for o in s.objects if o.type=='MESH' and not o.hide_render and not o.get('authoringGuide')]
    return [[min((o.matrix_world@Vector(v))[i] for o in objects for v in o.bound_box),max((o.matrix_world@Vector(v))[i] for o in objects for v in o.bound_box)] for i in range(3)]
source_bounds=character_bounds()
receipt=dict(status='Owner review pending; proposed CG character',mode=args.mode,
             attempt=args.attempt,era=args.era,geometry_input=str(INPUT.relative_to(ROOT)),
             input_sha256=input_sha,previous_detailed_sha256=old_sha,changes={})
def module(name):
    path=ROOT/f'scripts/cinematic-cg-2a-{name}.py'
    spec=importlib.util.spec_from_file_location('cg1c_'+name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
if args.mode=='candidate':
    receipt['changes']['head']=module('head').apply(s,None,args.era)
    receipt['changes']['body']=module('body').apply(s,None,args.era)
    receipt['changes']['surface']=module('surface').apply(s,ASSET,args.era,ROOT)
    detailed_bounds=character_bounds()
    assert all(a[0]>=b[0]-.075 and a[1]<=b[1]+.075 for a,b in zip(detailed_bounds,source_bounds)), ('Unexpected detail scale',detailed_bounds,source_bounds)
    receipt['detail_bounds_guard']={'source':source_bounds,'candidate':detailed_bounds,'maximum_envelope_expansion_allowed':.075,'status':'PASS'}

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
    if name=='cinematic':
        bg.inputs[1].default_value=.045
        for d,power,c,size in zip(lights,[520,125,550],[(1,.83,.65),(.52,.65,.85),(1,.73,.47)],[2.0,3.0,1.6]):d.energy=power;d.color=c;d.size=size
    elif name=='neutral':
        bg.inputs[1].default_value=.4
        for d,(_,power,size) in zip(lights,neutral):d.energy=power;d.color=(1,1,1);d.size=size
    else:
        bg.inputs[1].default_value=.08
        for d,p,c,(_,_,size) in zip(lights,[450,65,150],[(1,.82,.65),(.62,.74,.85),(1,.7,.45)],neutral):d.energy=p;d.color=c;d.size=size
def render(name,size,position=None,target=None,scale=None,registration=None,light='neutral'):
    lighting(light)
    s.render.resolution_x,s.render.resolution_y=size;s.render.resolution_percentage=100
    data.shift_x=data.shift_y=0
    if registration:
        cam.location=registration['location'];cam.rotation_euler=registration['rotation_euler']
        data.ortho_scale=registration['ortho_scale'];data.shift_x=registration['shift_x'];data.shift_y=registration['shift_y']
    else:
        cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();
        if scale is not None:data.ortho_scale=scale
    s.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
    receipt.setdefault('cameras',{})[name]=dict(location=list(cam.location),rotation_euler=list(cam.rotation_euler),ortho_scale=data.ortho_scale,shift_x=data.shift_x,shift_y=data.shift_y,resolution=list(size),lighting=light,projection=data.type,lens_mm=data.lens)

# Aspect and projection exactly match the registered low-res/source layers.
w=args.resolution;landscape=(w,round(w*853/1280));portrait=(round(w*.75),w)
if not args.stage_only:render('canon-neutral',landscape,registration=canon)
if not args.stage_only:render('canon-workshop',landscape,registration=canon,light='workshop')
# Old 1b camera uses its original scale, target and illumination for both assets.
# A common exposure/look is used when 1b is re-rendered by this script.
legacy=(-6,-3.5,2.75);target=(0,-.08,.87)
if not args.stage_only:render('legacy-neutral',portrait,legacy,target,2.25)

# Separate cinematic rig: actual grounded shadows, same setup for before/candidate.
# Stage geometry is explicitly excluded from character GLB exports.
min_z=character_bounds()[2][0]
bpy.ops.mesh.primitive_plane_add(size=14,location=(0,0,min_z))
stage=bpy.context.object;stage.name='2a cinematic ground proposal';stage['authoringGuide']=True
floor=bpy.data.materials.new('2a matte workshop floor proposal');floor.use_nodes=True
nt=floor.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.043,.036,.029,1);bs.inputs['Roughness'].default_value=.93
noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=48;noise.inputs['Detail'].default_value=3
bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.004
nt.links.new(noise.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal']);stage.data.materials.append(floor)
data.type='PERSP';data.lens=65
render('cinematic-hero',portrait,(-3.0,-3.9,1.32),(0,-.04,.93),light='cinematic')
render('cinematic-profile',portrait,(-4.35,-1.875,1.31),(0,-.01,.95),light='cinematic')
stage.hide_render=True;data.type='ORTHO'
receipt['cinematic_stage']={'ground_height':min_z,'ground_source':'Original procedural stage proposal; no reference pixels','lens_mm':65,'projection':'perspective','stage_in_character_glb':False,'lighting_comparison':'same rig for previous and candidate'}

if args.final and not args.stage_only:
    render('legacy-workshop',portrait,legacy,target,2.25,light='workshop')
    for i in range(8):
        a=math.radians(i*45);center=Vector((0,-.04,.92))
        pos=center+Vector((6*math.sin(a),-6*math.cos(a),1.02))
        render(f'angle-{i*45:03d}',portrait,pos,center,2.10)
    for i in range(8):
        a=math.radians(i*45);center=Vector((0,-.04,.92));pos=center+Vector((6*math.sin(a),-6*math.cos(a),1.02))
        render(f'exhibit-{i*45:03d}',portrait,pos,center,2.10,light='workshop')
    render('head-closeup',portrait,(-6,-2.14,2.15),(0,-.28,1.58),.77,light='workshop')
    render('body-closeup',portrait,(-6,-2.14,1.55),(0,.01,.98),1.22,light='workshop')
    render('side-profile',portrait,(-6,0,.94),(0,0,.94),2.08)
if args.final and not args.stage_only:
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
if args.mode=='candidate' and not args.stage_only:
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
    bpy.ops.export_scene.gltf(filepath=str(ASSET/f'murderbird-cg-2a-{args.era}.glb'),export_format='GLB',use_selection=True,export_extras=False,export_apply=True,export_materials='EXPORT')
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
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET/f'murderbird-cg-2a-{args.era}.blend'))
assert SHA(INPUT)==input_sha and SHA(OLD)==old_sha
receipt['source_preserved']=True
receipt['created_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
receipt['image_hashes']={p.name:SHA(p) for p in OUT.glob('*.png')}
if args.stage_only and (OUT/'receipt.json').exists():
    old=json.loads((OUT/'receipt.json').read_text());old.setdefault('cameras',{}).update(receipt['cameras']);old['cinematic_stage']=receipt['cinematic_stage'];old['image_hashes']=receipt['image_hashes'];old['framing_corrected_utc']=receipt['created_utc'];receipt=old
(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('CG2A_COMPLETE',OUT)
