"""Bounded rest radial-band check; not a triangle collision/motion acceptance test."""
import bpy,json,runpy,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
BASE=ROOT/'assets/models/whole-character-v20/attempt-runtime02/murderbird-whole-character-v20.blend'
SOURCE=Path(__file__).parent/'checked-envelope.py'
bpy.ops.wm.open_mainfile(filepath=str(BASE));module=runpy.run_path(str(SOURCE));result=module['apply']()
dg=bpy.context.evaluated_depsgraph_get();trees={}
for r in result['added']:
 o=bpy.data.objects[r['name']];ev=o.evaluated_get(dg);mesh=ev.to_mesh()
 trees[o.name]=BVHTree.FromPolygons([o.matrix_world@v.co for v in mesh.vertices],[tuple(p.vertices) for p in mesh.polygons])
 ev.to_mesh_clear()
def interval(name,z,a):
 cy=(module['sample'](z,1)+module['sample'](z,2))/2
 origin=Vector((0,cy,z));d=Vector((math.sin(a),-math.cos(a),0));hits=[];p=origin.copy()
 for i in range(10):
  loc,norm,index,dist=trees[name].ray_cast(p,d,.8)
  if loc is None:break
  t=(loc-origin).dot(d)
  if not hits or abs(t-hits[-1])>1e-6:hits.append(t)
  p=loc+d*2e-6
 return (min(hits),max(hits)) if len(hits)>=2 else None
pairs=[]
for s in (-1,1):
 pairs.extend([
 ('V21 lower swept throat keel','V21 ascending root yoke '+str(s),(1.34,1.38,1.42,1.46),(.65,.85)),
 ('V21 lower swept nape return','V21 ascending root yoke '+str(s),(1.30,1.34,1.38,1.42,1.46),(2.1,2.5)),
 ('V21 upper swept throat keel','V21 upper cervical directional guard '+str(s),(1.47,1.51,1.55,1.59),(.65,.85)),
 ('V21 upper swept nape return','V21 upper cervical directional guard '+str(s),(1.47,1.51,1.55,1.59),(2.1,2.5)),
 ('V21 upper cervical directional guard '+str(s),'V21 lower swept throat keel',(1.46,1.47,1.48),(.65,.85)),
 ('V21 upper cervical directional guard '+str(s),'V21 ascending root yoke '+str(s),(1.46,1.47,1.48),(.9,2.1)),
 ('V21 upper cervical directional guard '+str(s),'V21 lower swept nape return',(1.46,1.47),(2.1,2.5)),
 ('V21 lower swept nape return','V21 fixed shoulder breast return '+str(s),(1.28,1.30,1.32),(2.1,2.5)),
 ('V21 anterior breast guard '+str(s),'V21 lower swept throat keel',(1.33,1.35),(.3,.8)),
 ('V21 breast central opening keel','V21 anterior breast guard '+str(s),(.93,1.0,1.16,1.30),(.25,.5)),
 ('V21 anterior breast guard '+str(s),'V21 fixed shoulder breast return '+str(s),(.93,1.0,1.16,1.30),(.8,1.2)),
 ('V21 fixed shoulder breast return '+str(s),'V21 ascending root yoke '+str(s),(1.28,1.30,1.32),(1.0,2.1)),
 ('V21 fixed shoulder breast return '+str(s),'V21 fixed lower sternal pan',(.91,.925,.94),(.8,1.35)),
 ('V21 anterior breast guard '+str(s),'V21 fixed lower sternal pan',(.91,.925,.94),(.35,1.0)),
 ])
pairs.extend([
 ('V21 upper swept throat keel','V21 lower swept throat keel',(1.46,1.47,1.48),(0,.7)),
 ('V21 upper swept nape return','V21 lower swept nape return',(1.46,1.47),(2.5,3.14)),
 ('V21 breast central opening keel','V21 lower swept throat keel',(1.33,1.35,1.38),(0,.45)),
 ('V21 breast central opening keel','V21 fixed lower sternal pan',(.90,.925,.94),(0,.43)),
 ])
records=[]
for i,(outer,inner,zs,angles) in enumerate(pairs):
 s=-1 if ('-1' in outer or '-1' in inner) else 1;checks=[]
 for z in zs:
  for j in range(41):
   a=s*(angles[0]+(angles[1]-angles[0])*j/40);o=interval(outer,z,a);n=interval(inner,z,a)
   if o and n:checks.append({'z':z,'angle':a,'outerBand':o,'innerBand':n,'radialGapM':o[0]-n[1]})
 worst=min(checks,key=lambda r:r['radialGapM']) if checks else None
 records.append({'outer':outer,'inner':inner,'sampledOverlapRays':len(checks),'minimumRadialGapM':worst['radialGapM'] if worst else None,'worstSample':worst})
report={'status':'Discrete radial bands only; not continuous strict clearance or motion acceptance','sourceSHA256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'baseSHA256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'pairs':records,'negativeGapPairs':sum(bool(r['minimumRadialGapM'] is not None and r['minimumRadialGapM']<0) for r in records)}
(Path(__file__).parent/'bands.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
