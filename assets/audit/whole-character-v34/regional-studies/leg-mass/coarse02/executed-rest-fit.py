"""Single neutral rest-only cross-owner screen, unchanged strict triangle method."""
import bpy,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
R=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');A=R/'assets/audit/whole-character-v34/regional-studies/leg-mass/coarse02'
BASE=R/'assets/models/whole-character-v33/attempt-form06/murderbird-whole-character-v33.blend';NEW=R/'assets/models/whole-character-v34/regional-studies/leg-mass/coarse02/murderbird-v34-leg-mass.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(BASE)=='5fdfe66693db848fcf624b28484c3eaba220a8d7f389248390a4f21a571d108d';assert sha(NEW)=='8f368d4ab123d89be68b7ccecef5367264f82935b1e4591e31697d10c915db38'
# Exact functions copied from frozen neck strict checker, no pose manipulation.
def inside(p,tri):
 x,y,z=tri;v0=y-x;v1=z-x;v2=p-x;d00=v0.dot(v0);d01=v0.dot(v1);d11=v1.dot(v1);den=d00*d11-d01*d01
 if abs(den)<1e-18:return False
 u=(d11*v2.dot(v0)-d01*v2.dot(v1))/den;v=(d00*v2.dot(v1)-d01*v2.dot(v0))/den
 return min(u,v,1-u-v)>1e-6
def edge(p,q,tri):
 n=(tri[1]-tri[0]).cross(tri[2]-tri[0])
 if n.length<1e-12:return False
 n.normalize();d0=n.dot(p-tri[0]);d1=n.dot(q-tri[0])
 if not(d0*d1<0 and abs(d0)>1e-7 and abs(d1)>1e-7):return False
 direction=q-p;hit=intersect_ray_tri(*tri,direction,p,True)
 if hit is None:return False
 t=(hit-p).dot(direction)/max(direction.length_squared,1e-30)
 return 1e-6<t<1-1e-6 and inside(hit,tri)
def screen(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();items=[]
 for o in bpy.data.objects:
  if o.type!='MESH' or not o.parent or o.get('authoringGuide') is True:continue
  if 'builder' not in o.get('exteriorEras','maker,mechanic,builder').split(','):continue
  ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@x.co for x in m.vertices];tri=[tuple(f.vertices) for f in m.loop_triangles];ev.to_mesh_clear()
  if not v:continue
  scope=o.parent.name in ('left-thigh','left-shin','right-thigh','right-shin')
  bounds=[[min(pt[k] for pt in v) for k in range(3)],[max(pt[k] for pt in v) for k in range(3)]]
  items.append((o.name,o.parent.name,scope,v,tri,bounds,BVHTree.FromPolygons(v,tri,all_triangles=True)))
 pairs=[]
 for i,x in enumerate(items):
  for y in items[i+1:]:
   if x[1]==y[1] or not(x[2] or y[2]) or any(x[5][1][k]<y[5][0][k] or y[5][1][k]<x[5][0][k] for k in range(3)):continue
   for ix,iy in x[6].overlap(y[6]):
    tx=[x[3][j] for j in x[4][ix]];ty=[y[3][j] for j in y[4][iy]]
    if any(edge(tx[k],tx[(k+1)%3],ty) or edge(ty[k],ty[(k+1)%3],tx) for k in range(3)):
     pairs.append({'a':x[0],'b':y[0],'owners':[x[1],y[1]],'firstTrianglePair':[ix,iy],'witnessTriangles':[[list(v) for v in tx],[list(v) for v in ty]]});break
 return {'nativeSHA256':sha(path),'allVisibleMeshes':len(items),'screenedLegMeshes':sum(x[2] for x in items),'pairCount':len(pairs),'pairs':pairs}
r={'scope':'Neutral rest only, all140 thigh/shin meshes vs builder-visible other owners. Same-owner junction overlaps excluded; no whole-motion, coverage, containment or physics proof.','method':'Strict edge-through-face; 1e-7m plane and1e-6barycentric/edge margin, first witness per identity.','sourceSHA256':sha(Path(__file__)),'baseline':screen(BASE),'candidate':screen(NEW)}
key=lambda p:tuple(sorted((p['a'],p['b'])))
b={key(p):p for p in r['baseline']['pairs']};c={key(p):p for p in r['candidate']['pairs']}
r['introduced']=[c[k] for k in sorted(c.keys()-b.keys())];r['retained']=[c[k] for k in sorted(c.keys()&b.keys())];r['resolved']=[b[k] for k in sorted(b.keys()-c.keys())]
(A/'rest-fit-screen.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'before':len(b),'after':len(c),'introduced':len(r['introduced']),'retained':len(r['retained']),'resolved':len(r['resolved'])}))
