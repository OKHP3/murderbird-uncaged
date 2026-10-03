"""Bounded CG likeness study. Preserved prop input, fixed comparison cameras."""
from pathlib import Path
import bpy, json, math, hashlib, importlib.util, sys, argparse, datetime
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
P=R/'assets/models/whole-character-v38/hanging-breast01/attempt02/murderbird-v38-hanging-breast01-attempt02-rigid.glb'
O=R/'assets/audit/cinematic-cg-milestone01b'; A=R/'assets/models/cinematic-cg-milestone01b'
parser=argparse.ArgumentParser(); parser.add_argument('--final',action='store_true'); parser.add_argument('--attempt',default='attempt01');parser.add_argument('--era',default='builder');parser.add_argument('--baseline',action='store_true');parser.add_argument('--resolution',type=int,default=768)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
T=O/args.attempt;T.mkdir(parents=True,exist_ok=True);A.mkdir(parents=True,exist_ok=True)
assert hashlib.sha256(P.read_bytes()).hexdigest()=='051477ffcf62a4e08a3f1968d6cec7fd7f8b0677661cd72dde6ad7bbd5514650'
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(P))
s=bpy.context.scene
for o in s.objects:
 if o.type=='MESH':
  o.hide_render=bool(o.get('authoringGuide')) or args.era not in o.get('exteriorEras','maker,mechanic,builder').split(',')
  o.hide_viewport=o.hide_render
receipt={'input':str(P.relative_to(R)),'inputSHA256':hashlib.sha256(P.read_bytes()).hexdigest(),'era':args.era,'changes':{},'scope':'Unapproved CG likeness study; no engineering certification; preserved source input.'}
def module(name):
 p=R/f'scripts/cinematic-cg-1b-{name}.py';spec=importlib.util.spec_from_file_location('cg1b_'+name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
if not args.baseline:
 receipt['changes']['head']=module('head').apply(s)
 receipt['changes']['body']=module('body').apply(s)
 # glTF mesh selection and PBR projection also cover rolled-edge curves.
 for o in list(s.objects):
  if o.type=='CURVE' and o.get('cg1bRegion'):
   bpy.ops.object.select_all(action='DESELECT');o.hide_viewport=False;o.select_set(True);bpy.context.view_layer.objects.active=o
   bpy.ops.object.convert(target='MESH')
 receipt['changes']['surface']=module('surface').apply(s,A,args.era)
s.render.engine='CYCLES';s.cycles.samples=32 if args.final else 12;s.cycles.use_denoising=True
s.render.resolution_x=args.resolution;s.render.resolution_y=round(args.resolution*4/3);s.render.resolution_percentage=100
s.view_settings.view_transform='AgX';s.render.image_settings.file_format='PNG';s.render.film_transparent=False
s.world=bpy.data.worlds.new('Fixed comparison world');s.world.use_nodes=True
bg=s.world.node_tree.nodes['Background'];bg.inputs[0].default_value=(.08,.08,.08,1);bg.inputs[1].default_value=.4
lights=[((-3,-4,5),700,4),((4,-1,3),250,4),((0,4,4),500,3)]
for i,(pos,power,size) in enumerate(lights):
 d=bpy.data.lights.new(f'comparison-{i}','AREA');d.energy=power;d.size=size;o=bpy.data.objects.new(f'comparison-{i}',d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('Locked milestone1a camera');d.type='ORTHO';d.ortho_scale=2.25;c=bpy.data.objects.new('Locked milestone1a camera',d);s.collection.objects.link(c);s.camera=c
target=(0,-.08,.87)
views=[('hero-reference',(-6,-3.5,2.75)),('hero-front',(0,-7,1.65))]
if args.final:views += [(f'angle-{i*45:03d}',(7*math.sin(math.radians(i*45)),-7*math.cos(math.radians(i*45)),2.3)) for i in range(8)]
receipt['camera']={'type':'ORTHO','scale':2.25,'target':target,'resolution':[s.render.resolution_x,s.render.resolution_y],'views':views,'authority':'Milestone1a estimated camera; unchanged for before/after; not claimed exact target camera'}
receipt['lighting']={'neutral':lights,'workshopEnergies':[450,65,150],'workshopColors':[(1,.82,.65),(.62,.74,.85),(1,.7,.45)],'workshopWorldStrength':.08}
for name,pos in views:
 c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(T/(name+'.png'));bpy.ops.render.render(write_still=True)
for i in range(3):
 d=bpy.data.lights[f'comparison-{i}'];d.energy=receipt['lighting']['workshopEnergies'][i];d.color=receipt['lighting']['workshopColors'][i]
bg.inputs[1].default_value=.08
c.location=(-6,-3.5,2.75);c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(T/'hero-workshop.png');bpy.ops.render.render(write_still=True)
if args.final:
 # Close-ups use separately labelled cameras, never replace the fixed full-bird comparisons.
 for name,targ,scale in [('head-closeup',(0,-.5,1.58),.8),('body-closeup',(0,-.10,1.08),1.18)]:
  c.data.ortho_scale=scale;c.rotation_euler=(Vector(targ)-c.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(T/(name+'.png'));bpy.ops.render.render(write_still=True)
 c.data.ortho_scale=2.25;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler()
 if not args.baseline:
  # Hidden source alternatives remain in native study, excluded from exported candidate.
  bpy.ops.object.select_all(action='DESELECT')
  for o in s.objects:
   if o.type=='MESH' and not o.hide_render:
    o.hide_viewport=False;o.select_set(True)
  bpy.ops.export_scene.gltf(filepath=str(A/f'murderbird-cg-1b-{args.era}.glb'),export_format='GLB',use_selection=True,export_extras=False,export_apply=True,export_materials='EXPORT')
  # Native source includes editable geometry, image materials and preserved hidden source.
  for img in bpy.data.images:
   if img.source=='FILE':
    try:img.pack()
    except RuntimeError:pass
  bpy.ops.wm.save_as_mainfile(filepath=str(A/f'murderbird-cg-1b-{args.era}.blend'))
receipt['renderHashes']={p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in T.glob('*.png')}
receipt['createdUTC']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(T/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('CG1B_COMPLETE',str(T))
