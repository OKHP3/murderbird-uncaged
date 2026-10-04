import bpy,json,numpy as np
s=bpy.context.scene
for name in ('CGRF01 CGH18 formed dorsal bill root cuff','CGRF01 CGRB01 rounded course 0-0','CGH18 formed dorsal bill root cuff','CGRB01 rounded course 0-0'):
 o=s.objects.get(name)
 if not o:continue
 print('OBJECT',name,'hide',o.hide_render,o.hide_get(),o.visible_get(),'parents',o.parent.name if o.parent else None,'modifier',[(m.type,m.show_render) for m in o.modifiers])
 for slot in o.material_slots:
  m=slot.material
  for n in m.node_tree.nodes:
   if n.type=='TEX_IMAGE' and n.label=='color':
    a=np.array(n.image.pixels[:]).reshape(-1,4);print('COLOR',m.name,n.image.filepath,n.image.name,n.image.colorspace_settings.name,a[:,:3].mean(0).tolist())
print('SCENE VISIBLE COUNTS',len([o for o in s.objects if o.type=='MESH' and not o.hide_render]),len([o for o in s.objects if o.get('cgRecursiveFinish01')]))
