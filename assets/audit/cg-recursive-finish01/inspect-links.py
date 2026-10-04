import bpy
for name in ('CGRF01 CGH18 formed dorsal bill root cuff','CGRF01 CGH17 broad curved brow course near 0','CGRF01 CGRB01 rounded course 0-0'):
 o=bpy.context.scene.objects.get(name)
 if not o:continue
 print('OBJECT',name)
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());print('OBJMATS',[s.material.name for s in o.material_slots]);print('EVMATS',[m.name for m in ev.data.materials]);print('DATA',[m.name for m in o.data.materials])
 for s in o.material_slots:
  m=s.material
  print('LINKS',m.name,[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links]);print('IMAGES',[(n.label,n.image.name,n.image.size[:]) for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image])
