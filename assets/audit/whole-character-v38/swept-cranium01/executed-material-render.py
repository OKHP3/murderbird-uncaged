import bpy,json,struct,sys
from pathlib import Path
from mathutils import Vector
model,glb,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(model));raw=glb.read_bytes();n=struct.unpack_from('<I',raw,12)[0];d=json.loads(raw[20:20+n])
for mat in d['materials']:
 m=bpy.data.materials.get(mat['name']);m.use_nodes=True;shader=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p=mat['extras']['eraFinishes'].get('builder');f=p['baseColorFactor']
 for key,val in [('Base Color',f),('Metallic',p['metallicFactor']),('Roughness',p['roughnessFactor'])]:
  sock=shader.inputs[key]
  for link in list(sock.links):m.node_tree.links.remove(link)
  sock.default_value=val
for o in bpy.data.objects:
 if o.type=='MESH':o.hide_render=o.get('authoringGuide')is True or 'builder'not in str(o.get('exteriorEras','maker,mechanic,builder')).split(',')
 elif o.type=='CURVE':o.hide_render=True
scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE';scene.render.resolution_x=scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.world.use_nodes=True;bg=scene.world.node_tree.nodes.get('Background');bg.inputs['Color'].default_value=(.18,.18,.18,1);bg.inputs['Strength'].default_value=.6
for pos,power in [((-3,-4,5),1600),((3,-1,3),1100),((0,4,5),1300)]:
 data=bpy.data.lights.new('temporary material comparison','AREA');data.energy=power;data.shape='DISK';data.size=4;o=bpy.data.objects.new(data.name,data);scene.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,-.55,1.7))-o.location).to_track_quat('-Z','Y').to_euler()
data=bpy.data.cameras.new('temporary actual PBR head');data.type='ORTHO';data.ortho_scale=.68;o=bpy.data.objects.new(data.name,data);scene.collection.objects.link(o);o.location=(-5,-3.8,2.1);o.rotation_euler=(Vector((0,-.55,1.70))-o.location).to_track_quat('-Z','Y').to_euler();scene.camera=o;scene.render.filepath=str(out);bpy.ops.render.render(write_still=True)
print('Actual exported Builder standard linear PBR values rendered in Blender EEVEE; not browser or owner acceptance. Native file not modified.')
