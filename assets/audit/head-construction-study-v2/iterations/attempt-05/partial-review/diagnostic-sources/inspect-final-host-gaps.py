import bpy,statistics,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
source=root/'assets/models/uncaged-alignment-v7/murderbird-alignment-v7.blend'; cand=root/'assets/models/uncaged-head-construction-study-v2/iterations/attempt-05/murderbird-head-construction-study-v2-partial.blend'
def sig(o):
 if o.type!='MESH': return (o.type,tuple(o.location),tuple(o.rotation_euler),tuple(o.scale),o.parent.name if o.parent else None)
 return (o.type,tuple(o.location),tuple(o.rotation_euler),tuple(o.scale),o.parent.name if o.parent else None,tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(p.vertices) for p in o.data.polygons))
bpy.ops.wm.open_mainfile(filepath=str(source)); base={o.name:sig(o) for o in bpy.data.objects}
bpy.ops.wm.open_mainfile(filepath=str(cand)); cur={o.name:sig(o) for o in bpy.data.objects}; changed=[n for n in base.keys()|cur.keys() if base.get(n)!=cur.get(n)]
print('PARTIAL_SHA256',hashlib.sha256(cand.read_bytes()).hexdigest(),'BYTES',cand.stat().st_size)
print('CHANGED',json.dumps(changed))
print('MISSING_MATERIALS',json.dumps([n for n in ['Neutral / edge.001','Neutral / plate.001'] if bpy.data.materials.get(n) is None]))
checks=[]
for kind,side in [('brow',-1),('brow',1),('cheek',-1),('cheek',1),('cere',-1),('cere',1)]:
 band=bpy.data.objects[{'brow':f'Forged orbital brow {side}','cheek':f'Broad swept cheek band {side}','cere':f'Cere root transition {side}'}[kind]]
 if kind=='brow': names=[f'Rounded swept crown lamina {i}' for i in range(4)]+[f'Swept temporal lamina {side} 0 0',f'Swept temporal lamina {side} 0 1',f'Forged orbital mounting plate {side}','Overlapping nasal hood']
 elif kind=='cheek': names=[f'Forged orbital mounting plate {side}']
 else: names=['Overlapping nasal hood','Profiled upper bill blade 0','Profiled upper bill blade 1']
 vs=[]; fs=[]; offset=0
 for n in names:
  o=bpy.data.objects[n]; v=[o.matrix_world@x.co for x in o.data.vertices]; f=[tuple(offset+i for i in p.vertices) for p in o.data.polygons]; vs.extend(v); fs.extend(f); offset+=len(v)
 tree=BVHTree.FromPolygons(vs,fs); pts=[band.matrix_world@v.co for v in band.data.vertices[:741]]
 rows=[tree.find_nearest(p) for p in pts]; ds=[r[3] for r in rows]; dots=[side*r[1].normalized().x if r[1] else None for r in rows]
 out={'kind':kind,'side':side,'n':len(ds),'gapM':{'min':min(ds),'median':statistics.median(ds),'p90':sorted(ds)[int(.9*len(ds))],'max':max(ds)},'normalSideDot':{'min':min(x for x in dots if x is not None),'median':statistics.median(x for x in dots if x is not None),'p10':sorted(x for x in dots if x is not None)[int(.1*len(dots))]}}
 checks.append(out)
print('FINAL_HOST_GAPS',json.dumps(checks))
