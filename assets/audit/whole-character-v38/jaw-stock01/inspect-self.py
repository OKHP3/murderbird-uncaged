import bpy,json,hashlib,runpy
from pathlib import Path
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree
R=Path('/Users/okh/.codex/worktrees/v38-cervical-envelope/murderbird-uncaged');A=R/'assets/audit/whole-character-v38/jaw-stock01';S=R/'assets/models/whole-character-v38/bill-gape01/attempt02/murderbird-v38-bill-gape01-attempt02.blend'
assert hashlib.sha256(S.read_bytes()).hexdigest()=='7665bf8a14e6a2b95cd311d8c1d4b8938d08a1a730a50a91265dbfd83f01a784'
f=(R/'assets/audit/whole-character-v38/bill-gape01/attempt02/finite-screen.py').read_text();exec(f[f.index('def inside'):f.index('def load')])
bpy.ops.wm.open_mainfile(filepath=str(S));o=bpy.data.objects['V32 formed mandibular bowl'];m=o.data;m.calc_loop_triangles();v=[o.matrix_world@x.co for x in m.vertices];faces=[tuple(t.vertices)for t in m.loop_triangles];keys=[(r,c)for r in range(53)for c in range(33)if r<=5 or c<=6 or c>=26 or r>=49];half=len(keys);assert len(v)==2*half
b=BVHTree.FromPolygons(v,faces,all_triangles=True);pairs=[]
def tri(i):
 inds=faces[i];layers=sorted({int(j>=half)for j in inds});rc=[keys[j%half]for j in inds];return {'triangle':i,'polygon':m.loop_triangles[i].polygon_index,'indices':inds,'layers':layers,'rows':sorted({p[0]for p in rc}),'cols':sorted({p[1]for p in rc}),'region':'outer'if layers==[0]else('inner'if layers==[1]else'wall/cap'),'centerNative':list(sum((v[j]for j in inds),v[inds[0]]*0)/3)}
for ia,ib in b.overlap(b):
 if ia>=ib or set(faces[ia])&set(faces[ib]):continue
 x=[v[j]for j in faces[ia]];y=[v[j]for j in faces[ib]]
 if any(edge(x[k],x[(k+1)%3],y)or edge(y[k],y[(k+1)%3],x)for k in range(3)):pairs.append({'a':tri(ia),'b':tri(ib)})
summary={}
for p in pairs:
 k='/'.join(sorted([p['a']['region'],p['b']['region']]));summary[k]=summary.get(k,0)+1
out={'sourceSHA256':hashlib.sha256(S.read_bytes()).hexdigest(),'mesh':o.name,'modifiers':[(x.name,x.type)for x in o.modifiers],'halfVertexCount':half,'strictSelfPairs':len(pairs),'classification':summary,'rowRanges':sorted({r for p in pairs for t in [p['a'],p['b']]for r in t['rows']}),'pairs':pairs};(A/'inspect-self.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='pairs'},indent=2));print('FIRST',json.dumps(pairs[0] if pairs else{}))
