from pathlib import Path
import bpy
from mathutils import Vector
R=Path('/Users/okh/.codex/worktrees/v38-cervical-envelope/murderbird-uncaged');A=R/'assets/audit/whole-character-v38/facial-shell01'
for pre,rel in[('candidate','facial-shell01/murderbird-v38-facial-shell01.blend'),('source','bill-vault01/attempt02/murderbird-v38-bill-vault01-attempt02.blend')]:
 bpy.ops.wm.open_mainfile(filepath=str(R/'assets/models/whole-character-v38'/rel));s=bpy.context.scene
 for o in bpy.data.objects:
  if o.type=='MESH':o.hide_render=o.get('silhouetteStudyHistoricalHidden')is True or o.get('authoringGuide')is True or 'builder'not in str(o.get('exteriorEras','maker,mechanic,builder')).split(',')
  elif o.type in['CURVE','LIGHT']:o.hide_render=True
 s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True;s.render.resolution_x=s.render.resolution_y=800;s.render.resolution_percentage=100;s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.11,.12,.14,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
 for name,pos,power,size in [('key',(-3,-4,5),500,4),('fill',(3,-2,3),300,3),('rear',(-1,2,4),350,3)]:
  d=bpy.data.lights.new('study '+name,'AREA');d.energy=power;d.shape='DISK';d.size=size;l=bpy.data.objects.new(d.name,d);s.collection.objects.link(l);l.location=pos;l.rotation_euler=(Vector((0,-.63,1.63))-l.location).to_track_quat('-Z','Y').to_euler()
 d=bpy.data.cameras.new('study matched material camera');d.type='ORTHO';d.ortho_scale=.60;o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);s.camera=o;o.location=(-6,-3.5,2.15);o.rotation_euler=(Vector((0,-.63,1.63))-o.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(A/(pre+'-head-three-quarter-material.png'));bpy.ops.render.render(write_still=True)
