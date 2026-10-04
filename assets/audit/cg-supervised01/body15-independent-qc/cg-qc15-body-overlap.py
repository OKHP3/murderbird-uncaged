import bpy,json,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');WT=Path('/Users/okh/.codex/worktrees/cg-supervised-oblique-breast15/murderbird-uncaged')
def probe(path,version,offset):
 bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene;s.render.threads_mode='FIXED';s.render.threads=2;deps=bpy.context.evaluated_depsgraph_get();panels=[o for o in s.objects if o.get('cgSupervisedBody12') or o.get('cgSupervisedBody'+version)];trees={}
 for o in panels:
  ev=o.evaluated_get(deps);md=ev.to_mesh();trees[o.name]=BVHTree.FromPolygons([o.matrix_world@v.co for v in md.vertices],[tuple(p.vertices) for p in md.polygons]);ev.to_mesh_clear()
 records=[]
 for o in panels:
  if not o.get('cgSupervisedBody'+version):continue
  nu,nv=json.loads(o['body'+version+'Grid']);rc=rt=tc=tt=0;locations=[]
  for p in list(o.data.polygons)[offset::2]:
   co=sum((o.matrix_world@o.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices);v=sum(i//nu/(nv-1) for i in p.vertices)/len(p.vertices);n=(o.matrix_world.to_3x3().inverted().transposed()@p.normal).normalized();n=-n if n.y>0 else n;hits=[]
   for name,t in trees.items():
    if name==o.name:continue
    h,hn,idx,d=t.ray_cast(co+n*.035,-n,.075)
    if h is not None and .035-d>.0002:hits.append(dict(occluder=name,burial=.035-d))
   if v<=.25:rt+=1;rc+=bool(hits)
   elif v>=.82:
    tt+=1;tc+=bool(hits)
    if hits:locations.append(dict(face=p.index,worldCenter=list(co),normal=list(n),localV=v,hits=hits))
  records.append(dict(object=o.name,rootCovered=rc,rootSamples=rt,tipBuried=tc,tipSamples=tt,tipLocations=locations))
 return dict(version=version,offset=offset,panelsWithRootCoverage=sum(x['rootCovered']>0 for x in records),rootCovered=sum(x['rootCovered'] for x in records),rootSamples=sum(x['rootSamples'] for x in records),panelsWithTipBurial=sum(x['tipBuried']>0 for x in records),tipBuried=sum(x['tipBuried'] for x in records),tipSamples=sum(x['tipSamples'] for x in records),records=records)
a=probe(WT/'assets/audit/cg-supervised-body15/attempt01/murderbird-body15.blend','15',0);b=probe(ROOT/'assets/audit/cg-supervised-body13/attempt01/murderbird-body13.blend','13',1)
Path('/tmp/cg-qc15-body-overlap.json').write_text(json.dumps(dict(method='Fresh independent BVH definitions matching native check; even15 reproduces worker subset; odd13 supplies comparable same quad-index subset baseline. Root/tip param bands are local panel UV, not source visible coverage.',even15=a,odd13=b),indent=2));print(json.dumps({k:{j:w for j,w in v.items() if j!='records'} for k,v in [('even15',a),('odd13',b)]}),flush=True)
