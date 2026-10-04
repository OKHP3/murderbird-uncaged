import bpy
for o in bpy.context.scene.objects:
 if o.type=='MESH' and not o.hide_render and any(w in o.name.lower() for w in ('brow','forehead','dorsal','bill')):
  print('OBJECT',o.name,[u.name for u in o.data.uv_layers])
  for i,s in enumerate(o.material_slots):
   m=s.material;print('MAT',i,m.name if m else None,dict(m.items()) if m else {})
   if m and m.use_nodes:
    print('BASE',[(n.name,n.inputs['Base Color'].default_value[:],n.inputs['Metallic'].default_value,n.inputs['Roughness'].default_value) for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'])
    print('TEX',[(n.name,n.label,n.image.name if n.image else None) for n in m.node_tree.nodes if n.type=='TEX_IMAGE'])
