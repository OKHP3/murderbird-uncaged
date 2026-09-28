import bpy,json,math,statistics
from pathlib import Path
from mathutils import Vector
p='/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/models/uncaged-head-construction-study-v2/iterations/attempt-05/murderbird-head-construction-study-v2-partial.blend';bpy.ops.wm.open_mainfile(filepath=p)
names=['Forged orbital brow -1','Forged orbital brow 1','Cere root transition -1','Cere root transition 1','Broad swept cheek band -1','Broad swept cheek band 1']; rows=[]
for n in names:
 o=bpy.data.objects[n]; c=[tuple(v.co) for v in o.data.vertices]; N=57*13; dirs={'alongOuter':[],'acrossOuter':[],'thickness':[],'alongInner':[],'acrossInner':[]}
 for skin in (0,1):
  base=skin*N
  for j in range(57):
   for k in range(13):
    i=base+j*13+k
    if j<56:dirs['alongOuter' if skin==0 else 'alongInner'].append((i,i+13,j,k))
    if k<12:dirs['acrossOuter' if skin==0 else 'acrossInner'].append((i,i+1,j,k))
    if skin==0:dirs['thickness'].append((i,i+N,j,k))
 out={'name':n}
 for key,eds in dirs.items():
  vals=[(math.dist(c[i],c[q]),j,k,i,q) for i,q,j,k in eds]
  out[key]={'count':len(vals),'zeroBelow1e-7':sum(x[0]<1e-7 for x in vals),'below1e-5':sum(x[0]<1e-5 for x in vals),'maxM':max(x[0] for x in vals),'maxEdge':max(vals)[:3]}
 rows.append(out)
print(json.dumps(rows,indent=2))
