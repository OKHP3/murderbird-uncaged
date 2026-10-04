from pathlib import Path
import bpy,json,importlib.util,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent/'attempt02';OUT.mkdir(exist_ok=True)
if (OUT/'before-neutral.png').exists():raise RuntimeError('Write-once proof exists; preserve it')
INPUT=ROOT/'assets/models/cg-supervised01/surface01/murderbird-supervised-builder.blend'
def mod(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
finish=mod('cg-supervised-finish02.py');light=mod('cg-supervised-lighting02.py');oldlight=mod('cinematic-cg-2b-lighting.py')
bpy.ops.wm.open_mainfile(filepath=str(INPUT));scene=bpy.context.scene
for o in list(scene.objects):
 if o.type in ('LIGHT','CAMERA'):bpy.data.objects.remove(o,do_unlink=True)
 elif o.get('authoringGuide'):o.hide_render=True
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
scene.render.resolution_x=960;scene.render.resolution_y=640;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=0
scene.world=bpy.data.worlds.new('Finish02 matched proof world');scene.world.use_nodes=True
canon=json.loads((ROOT/'assets/audit/cg-supervised01/surface01/builder/receipt.json').read_text())['cameras']['canon-neutral']
d=bpy.data.cameras.new('Finish02 frozen camera');o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);scene.camera=o
o.location=canon['location'];o.rotation_euler=canon['rotation_euler'];d.type='ORTHO';d.ortho_scale=canon['ortho_scale'];d.shift_x,d.shift_y=canon['shift'];lights=[]
for i in range(3):
 l=bpy.data.lights.new('Finish02 area '+str(i),'AREA');ob=bpy.data.objects.new(l.name,l);scene.collection.objects.link(ob);lights.append(ob)
# Same ground appears in all matched comparisons, only lighting and material differ.
verts=[o.matrix_world@Vector(c) for o in scene.objects if o.type=='MESH' and not o.hide_render and not o.get('authoringGuide') for c in o.bound_box]
light.stage(scene,min(v.z for v in verts))
receipts=[]
def render(label,rig):
 bg=scene.world.node_tree.nodes.get('Background');bg.inputs[0].default_value=(*rig['world_color'],1);bg.inputs[1].default_value=rig['world_strength']
 for ob,s in zip(lights,rig['areas']):
  ob.location=s['position'];ob.rotation_euler=(Vector(s['target'])-ob.location).to_track_quat('-Z','Y').to_euler();ob.data.energy=s['power'];ob.data.color=s['color'];ob.data.size=s['size']
 scene.render.filepath=str(OUT/(label+'.png'));bpy.ops.render.render(write_still=True)
 receipts.append({'image':label+'.png','sha256':hashlib.sha256((OUT/(label+'.png')).read_bytes()).hexdigest()})
render('before-neutral',light.profiles()['neutral']);render('before-workshop-original',oldlight.profiles()['workshop'])
finish.apply(scene,OUT,'builder',ROOT)
render('candidate-neutral',light.profiles()['neutral']);render('candidate-workshop-original',oldlight.profiles()['workshop']);render('candidate-workshop-readable',light.profiles()['workshop'])
# Editable native proof is confined to audit, no runtime artifact promotion.
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'finish02-builder-proof.blend'))
(OUT/'proof-receipt.json').write_text(json.dumps({'input_sha256':hashlib.sha256(INPUT.read_bytes()).hexdigest(),'camera':canon,'exposure':0,'samples':16,'captures':receipts,'geometry':'Validated by finish.apply before ground excluded','artistic_acceptance':'pending'},indent=2))
print('PROOF_READY',flush=True)
