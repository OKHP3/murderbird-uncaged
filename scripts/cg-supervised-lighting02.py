"""Readable warm-key/cool-fill original area rig, normal exposure; no HDRI.
profiles() is compatible with the supervised renderer. stage() adds only ground.
"""
def profiles():
 def area(position,target,power,color,size):return dict(position=position,target=target,power=power,color=color,size=size)
 return {
  'neutral':dict(world_color=(.08,.08,.08),world_strength=.4,areas=[
   area((-3,-4,5),(0,0,1),700,(1,1,1),4),area((4,-1,3),(0,0,1),250,(1,1,1),4),area((0,4,4),(0,0,1),500,(1,1,1),3)]),
  'workshop':dict(world_color=(.09,.10,.115),world_strength=.32,areas=[
   area((-3,-4,4.5),(0,-.05,1),900,(1,.86,.70),3.5),area((3,-2,2.5),(0,-.05,.9),480,(.70,.82,1),4),area((1,3,4),(0,0,1),600,(1,.78,.57),2.5)]),
  'cinematic':dict(world_color=(.09,.10,.115),world_strength=.30,areas=[
   area((-3,-3,4.2),(0,-.05,1.05),950,(1,.85,.68),3),area((3,-2,2.5),(0,0,.85),460,(.68,.80,1),3.5),area((2,2.5,4),(0,.08,1.1),650,(1,.77,.57),2.3)])}

def stage(scene,min_z):
 import bpy
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,min_z-.0005))
 o=bpy.context.object;o.name='Finish02 review contact ground';o['authoringGuide']=True
 m=bpy.data.materials.new('Finish02 matte warm charcoal ground');m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.055,.048,.039,1);bs.inputs['Roughness'].default_value=.94
 o.data.materials.append(m);return o
