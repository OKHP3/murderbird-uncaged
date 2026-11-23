import bpy, math
s=bpy.context.scene
print(s.render.engine,s.camera.name if s.camera else '',s.render.resolution_x,s.render.resolution_y,s.world.name if s.world else '',s.view_settings.view_transform)
for o in s.objects:
 if o.type in ('CAMERA','LIGHT','EMPTY') or o.name.startswith('CGB05 cervical') and not o.hide_render and o.name.endswith('0'):
  print(o.name, o.type,o.location[:],tuple(round(math.degrees(v),3) for v in o.rotation_euler),o.hide_render)
for n in ['CGB05 -1 shield curved feather 05-3','CGB12 longitudinal formed panel 2-2','CGRB01 rounded course 2-2']:
 o=bpy.data.objects[n];m=o.data
 print(n,'vcount',len(m.vertices),'normal',m.vertices[len(m.vertices)//4].normal[:])
 for i in (0,4,8,63,113,144,148,152,153,157,len(m.vertices)-1):
  if i<len(m.vertices):print(i,tuple(round(x,4) for x in m.vertices[i].co))
 print('mod',[(mod.name,mod.type) for mod in o.modifiers])
for m in bpy.data.materials:
 if m.name.startswith('CG metal05 /') and ('local0' in m.name or 'retained-uv' in m.name) and m.users>0: print(m.name)
