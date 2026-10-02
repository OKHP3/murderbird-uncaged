"""Milestone 1 render-only camera lock. No model changes or fit analysis."""
from pathlib import Path
import bpy,json,math,hashlib
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'assets/audit/cinematic-cg-milestone01'
p=R/'assets/models/whole-character-v38/hanging-breast01/attempt02/murderbird-v38-hanging-breast01-attempt02-rigid.glb'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='051477ffcf62a4e08a3f1968d6cec7fd7f8b0677661cd72dde6ad7bbd5514650'
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p))
s=bpy.context.scene
for o in s.objects:
 if o.type=='MESH':o.hide_render=bool(o.get('authoringGuide')) or 'builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True
s.render.resolution_x=512;s.render.resolution_y=640;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
s.world=bpy.data.worlds.new('Baseline world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.08,.08,.08,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
lights=[((-3,-4,5),700,4),((4,-1,3),250,4),((0,4,4),500,3)]
for i,(pos,power,size) in enumerate(lights):
 d=bpy.data.lights.new(str(i),'AREA');d.energy=power;d.size=size;o=bpy.data.objects.new(str(i),d);s.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('locked-camera');d.type='ORTHO';d.ortho_scale=2.6;c=bpy.data.objects.new('locked-camera',d);s.collection.objects.link(c);s.camera=c
views=[('hero-reference',(-6,-3.5,2.75)),('hero-front',(0,-7,1.65))]+[(f'angle-{i*45:03d}',(7*math.sin(math.radians(i*45)), -7*math.cos(math.radians(i*45)),2.3)) for i in range(8)]
receipt={'base':str(p.relative_to(R)),'cameraType':'ORTHO','scale':2.6,'target':[0,-.08,1.02],'resolution':[512,640],'lights':lights,'views':views,'scope':'Approximate reference-angle framing; artwork has no recoverable exact camera. Other angles reconstruct unseen views. Original GLB materials, no model changes.'}
(O/'cameras.json').write_text(json.dumps(receipt,indent=2)+'\n')
for name,pos in views:
 c.location=pos;c.rotation_euler=(Vector(receipt['target'])-c.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(O/(name+'.png'));bpy.ops.render.render(write_still=True)
