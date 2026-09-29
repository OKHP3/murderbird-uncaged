import bpy,json
from collections import defaultdict
bpy.ops.wm.open_mainfile(filepath='assets/models/whole-character-v27/attempt-form01/murderbird-whole-character-v27.blend')
for name in ['left digit 2 tapered claw sheath','left digit 1 tapered claw sheath','left digit 3 tapered claw sheath','left digit 2 proximal dorsal guard']:
 o=bpy.data.objects[name]; groups=defaultdict(list)
 for v in o.data.vertices: groups[round(v.co.y,5)].append(v.co)
 print('\n',name,'groups',len(groups))
 for y,vs in sorted(groups.items(),reverse=True):
  print(y, tuple(round(sum(v[i] for v in vs)/len(vs),4) for i in range(3)), 'n',len(vs), 'xr',round(min(v.x for v in vs),4),round(max(v.x for v in vs),4),'zr',round(min(v.z for v in vs),4),round(max(v.z for v in vs),4))
