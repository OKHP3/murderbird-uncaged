from pathlib import Path
import bpy,json
from mathutils import Quaternion,Vector
out=Path('/tmp/v31-head-reconstruction/attempt04/screen');p=(out/'executed-pose-input.py').read_text();bpy.ops.wm.open_mainfile(filepath='/tmp/v31-head-reconstruction/attempt04/head-reconstruction.blend');exec(p[p.index('CHAIN='):p.index('def inside')]);pose(STATES[3]);inv=bpy.data.objects['head'].matrix_world.inverted();r=json.loads((out/'receiving-poses.json').read_text())['models'][1]['poses'][3]
for pair in r['pairs']:
 print(pair['active'], 'local witness', [list(inv@Vector(x)) for x in pair['firstWitness']['activeTriangle']])
o=bpy.data.objects['V23 cervical 4 directional guard 10'];ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();v=[inv@(ev.matrix_world@x.co) for x in m.vertices];print('neck 10 local radial bounds',min((x.y*x.y+x.z*x.z)**.5 for x in v),max((x.y*x.y+x.z*x.z)**.5 for x in v));print('near hood root',[(list(x),(x.y*x.y+x.z*x.z)**.5) for x in v if abs(x.x)<.1 and x.z>-.06][:20])
