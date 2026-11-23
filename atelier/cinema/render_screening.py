"""Render a private fixed-camera screening from the frozen First Choice native scene."""
from pathlib import Path
import argparse, hashlib, json, math, sys, time
import bpy
from mathutils import Vector

parser=argparse.ArgumentParser()
parser.add_argument('--out',required=True,type=Path)
parser.add_argument('--draft',action='store_true')
parser.add_argument('--source-sha',default='1e59785a11aadf491714ef1b5aa682ff1b9efa0a6a3b421414f3bb7de053a05b')
parser.add_argument('--camera',choices=['hero','detail'],default='hero')
parser.add_argument('--frame',type=int,action='append')
parser.add_argument('--width',type=int,default=1920)
parser.add_argument('--height',type=int,default=1080)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
args.out.mkdir(parents=True,exist_ok=True)
source_sha=args.source_sha
with open(bpy.data.filepath,'rb') as f:
    if hashlib.file_digest(f,'sha256').hexdigest()!=source_sha:
        raise RuntimeError("Opening a different native would invalidate the screening.")
sc=bpy.context.scene
prefs=bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type='METAL'
prefs.refresh_devices()
for device in prefs.devices:
    device.use=device.type=='METAL'
devices=[device.name for device in prefs.devices if device.use]
if not devices or not any('m4 max' in n.lower() for n in devices):
    raise RuntimeError(f"Expected local M4 Max Metal GPU, found {devices!r}")
print('Rendering on Metal:',devices,flush=True)
sc.render.engine='CYCLES'
sc.cycles.device='GPU'
sc.render.use_persistent_data=True
sc.cycles.samples=16 if args.draft else 80
sc.cycles.use_denoising=True
sc.cycles.denoiser='OPENIMAGEDENOISE'
sc.cycles.denoising_input_passes='RGB_ALBEDO_NORMAL'
sc.cycles.use_adaptive_sampling=True
sc.cycles.adaptive_threshold=.028 if args.draft else .012
sc.cycles.adaptive_min_samples=8 if args.draft else 24
sc.cycles.use_animated_seed=False
sc.cycles.seed=708
sc.cycles.max_bounces=6
sc.cycles.diffuse_bounces=3
sc.cycles.glossy_bounces=4
sc.cycles.transparent_max_bounces=3
sc.cycles.sample_clamp_indirect=4.
sc.render.image_settings.file_format='PNG'
sc.render.image_settings.color_mode='RGB'
sc.render.image_settings.color_depth='8'
sc.render.image_settings.compression=15
sc.render.resolution_x=args.width;sc.render.resolution_y=args.height
sc.render.resolution_percentage=100
sc.render.fps=24
sc.render.film_transparent=False
sc.render.use_motion_blur=False
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
sc.view_settings.exposure=-.11
bg=sc.world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value=(.155,.200,.215,1)
bg.inputs['Strength'].default_value=.36
for name, power, color, pos, dims in [
    ('High north window',198,(1,.84,.65),(-2.35,-1.85,3.38),(1.78,2.40)),
    ('Cool overhead rake',166,(.68,.81,1),(-1.18,1.75,2.96),(1.3,2.45)),
    ('Brass edge light',246,(1,.67,.39),(1.36,.64,2.77),(1.45,.41)),
    ('Low reflected strip',65,(.87,.93,1),(.03,-2.36,.88),(1.55,.43))]:
    obj=bpy.data.objects[name]
    obj.location=pos
    obj.rotation_euler=(Vector((0,-.06,1.06))-obj.location).to_track_quat('-Z','Y').to_euler()
    obj.data.energy=power;obj.data.color=color;obj.data.size=dims[0];obj.data.size_y=dims[1]
# The cove remains part of the supplied native scene. Reduce the floor's
# albedo and color cast while keeping enough bounce and texture under the toes.
floor=bpy.data.objects.get('Studio floor • native staging')
for node in floor.data.materials[0].node_tree.nodes:
    if node.type=='VALTORGB':
        node.color_ramp.elements[0].color=(.012,.014,.016,1)
        node.color_ramp.elements[-1].color=(.033,.032,.030,1)
cam=sc.camera
cam.data.sensor_fit='VERTICAL'
cam.data.type='PERSP'
if args.camera=='hero':
    cam.location=(-3.62,-2.20,1.36)
    aim=Vector((0,-.135,.915))
    cam.data.lens=44.5
else:
    cam.location=(-3.12,-1.38,1.65)
    aim=Vector((-.04,-.235,1.37))
    cam.data.lens=65
cam.rotation_euler=(aim-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.dof.use_dof=False
sc.frame_start=0;sc.frame_end=251
frames=args.frame if args.frame else list(range(252))
t0=time.monotonic()
for num,f in enumerate(frames):
    file=args.out/f'{args.camera}-{f:04d}.png'
    if file.exists():
        continue
    sc.frame_set(f)
    temporary=file.with_suffix('.pending.png')
    sc.render.filepath=str(temporary)
    t1=time.monotonic()
    bpy.ops.render.render(write_still=True)
    temporary.replace(file)
    print(f'RENDER_FRAME {f} {time.monotonic()-t1:.3f}s {time.monotonic()-t0:.1f}s',flush=True)
receipt={'input_sha256':source_sha,'devices':devices,'engine':'Cycles Metal','camera':args.camera,'dimensions':[args.width,args.height],
         'fps':24,'frames':frames,'max_samples':sc.cycles.samples,'adaptive_threshold':sc.cycles.adaptive_threshold,
         'denoiser':sc.cycles.denoiser,'static_noise_seed':sc.cycles.seed,'elapsed_seconds':round(time.monotonic()-t0,2)}
(args.out/(args.camera+'-render.json')).write_text(json.dumps(receipt,indent=2)+'\n')
