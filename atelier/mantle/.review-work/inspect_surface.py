import bpy
for name in ['CGB05 -1 shield curved feather 05-3','CGRB01 rounded course 2-2','CGB05 cervical curved lamina 0-0','CG supervised left compact shield recess']:
 o=bpy.data.objects.get(name)
 if not o: continue
 m=o.data;print('MESH',name,len(m.vertices),len(m.polygons),len(m.uv_layers),o.matrix_world)
 print('CO',[(v.index,tuple(round(x,4) for x in (o.matrix_world@v.co))) for v in list(m.vertices)[:45]])
 print('POLY',[(list(p.vertices),p.material_index) for p in list(m.polygons)[:9]])
 print('MAT',[(s.name,s.material.diffuse_color[:]) for s in o.material_slots])
