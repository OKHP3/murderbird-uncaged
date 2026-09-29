"""Read-only component attribution on frozen input solids; no candidate saved."""
from pathlib import Path
import bpy,runpy,json,shutil
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=Path('/tmp/v27-wing-terminal/coarse01');BASE=ROOT/'assets/models/whole-character-v26/attempt-form01/murderbird-whole-character-v26.blend';mod=runpy.run_path(str(OUT/'executed-region.py'));h=runpy.run_path(str(OUT/'triangle-screen-helper.py'),run_name='helper');bpy.ops.wm.open_mainfile(filepath=str(BASE));bpy.context.view_layer.update();rest={n:bpy.data.objects[n].matrix_local.copy() for n in ['left-mantle','right-mantle','left-wing-shield','right-wing-shield']};owners={n:bpy.data.objects[n].matrix_world.copy() for n in ['left-wing-shield','right-wing-shield']};raw={}
for label in ['left','right']:
 n=f'{label} profiled mantle backing v4 {label}-wing-shield';o=bpy.data.objects[n];assert not list(o.modifiers);raw[n]=([o.matrix_world@v.co for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons])
def tris(v,faces):
 m=bpy.data.meshes.new('temporary attribution triangles');m.from_pydata(v,[],faces);m.update();m.calc_loop_triangles();t=[tuple(f.vertices) for f in m.loop_triangles];bpy.data.meshes.remove(m);return v,t,BVHTree.FromPolygons(v,t,all_triangles=True)
def evalpart(n):
 o=bpy.data.objects[n];ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@p.co for p in m.vertices];t=[tuple(p.vertices) for p in m.loop_triangles];ev.to_mesh_clear();return v,t,BVHTree.FromPolygons(v,t,all_triangles=True)
def hits(a,b):
 count=0
 for i,j in a[2].overlap(b[2]):
  A=[a[0][n] for n in a[1][i]];B=[b[0][n] for n in b[1][j]]
  if h['straddle'](A,B) and h['straddle'](B,A):count+=1
 return count
rows=[]
for state in [('maker-wing',0,-.38,0,.16),('short-shove',.07,-.64,.18,.72)]:
 for n,angle in zip(rest,state[1:]):bpy.data.objects[n].matrix_local=rest[n]@Matrix.Rotation(angle,4,'X')
 bpy.context.view_layer.update()
 for label,side in [('left',1),('right',-1)]:
  owner=label+'-wing-shield';name=f'{label} profiled mantle backing v4 {owner}';v,faces=raw[name];joint=owners[owner].translation;transform=bpy.data.objects[owner].matrix_world@owners[owner].inverted();near={n:evalpart(n) for n in [f'V21 refined {label} mantle course 6 plate 3',f'V21 refined {label} mantle course 6 plate 4']}
  for axes in ['', 'x','y','z','xy','xz','yz','xyz']:
   pts=[]
   for p in v:
    q,w=mod['warp'](p,side,joint);a=p.copy()
    for k,axis in enumerate('xyz'):
     if axis in axes:a[k]=q[k]
    pts.append(transform@a)
   part=tris(pts,faces);rows.append({'pose':state[0],'liner':name,'enabledDisplacementAxes':axes or 'none','nativeAxisMeaning':{'x':'inboard taper','y':'aft sweep','z':'fore lift / aft drop'},'hits':[{'mantle':n,'strictTriangleWitnesses':hits(part,b)} for n,b in near.items()]})
(OUT/'component-attribution.json').write_text(json.dumps({'status':'Read-only diagnostic; no implemented variant or saved native.','method':'Actual closed unmodified baseline liner polygons transformed by subsets of the authored warp axes, triangulated independently and tested against actual posed unchanged mantle solids. Full xyz is checked against the frozen candidate screen.','rows':rows},indent=2)+'\n');shutil.copyfile(__file__,OUT/'executed-attribution.py');print(json.dumps(rows),flush=True)
