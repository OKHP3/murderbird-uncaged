import bpy,json,hashlib,sys
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree
ROOT=Path('/Users/okh/.codex/worktrees/v38-cervical-envelope/murderbird-uncaged');p=ROOT/'assets/models/whole-character-v38/breast-study02/murderbird-v38-breast-study02.blend';assert hashlib.sha256(p.read_bytes()).hexdigest()=='4171e23e33b6795d170ccdf44a2014aa321b73c1dbedc13d4d8c4d3668237e97';bpy.ops.wm.open_mainfile(filepath=str(p));bpy.context.view_layer.update();code=(ROOT/'scripts/validate-neck-guard-envelope.py').read_text();n={'Vector':Vector,'intersect_ray_tri':intersect_ray_tri};exec(code[code.index('def inside('):code.index('def screen(')],n);edge=n['edge']
def surf(o):
 o.data.calc_loop_triangles();v=[o.matrix_world@q.co for q in o.data.vertices];t=[tuple(q.vertices) for q in o.data.loop_triangles];return v,t,BVHTree.FromPolygons(v,t,all_triangles=True)
liner=bpy.data.objects['V30 continuous tapered breast liner'];v,t,tree=surf(liner);rows=[]
for name in ['V24 rising thoracic receiving cheek -1','V24 rising thoracic receiving cheek 1','V35 oblique thoracic side guard -1 0','V35 oblique thoracic side guard 1 0']:
 o=bpy.data.objects[name];w,u,other=surf(o);indices=set();witnesses=[]
 for i,j in tree.overlap(other):
  a=[v[k] for k in t[i]];b=[w[k] for k in u[j]]
  if any(edge(a[k],a[(k+1)%3],b) or edge(b[k],b[(k+1)%3],a) for k in range(3)):indices.update(u[j]);witnesses.append([i,j])
 pts=[w[i] for i in indices];h=len(w)//2;half=[(w[i]-w[i+h]).length for i in range(h)] if len(w)%2==0 else []
 row={'name':name,'owner':o.parent.name,'props':dict(o.items()),'materials':[m.name if m else None for m in o.data.materials],'strictTrianglePairs':len(witnesses),'receiverFootprintVertexIndices':sorted(indices),'footprintBounds':[[min(p[k] for p in pts),max(p[k] for p in pts)] for k in range(3)],'halfPairRange':(min(half),max(half)) if half else None,'unchangedPosteriorAttachmentVertexIndices':[i for i,p in enumerate(w) if p.y>=-.18],'sourceWitnessPairs':witnesses};rows.append(row);print(name,row['strictTrianglePairs'],row['footprintBounds'],row['halfPairRange'],len(row['unchangedPosteriorAttachmentVertexIndices']))
Path('/tmp/murderbird-breast-receiver-inventory.json').write_text(json.dumps({'inputSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'receivers':rows},indent=2))
