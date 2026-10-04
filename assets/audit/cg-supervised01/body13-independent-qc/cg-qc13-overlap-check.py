import bpy,json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=Path('/Users/okh/.codex/worktrees/cg-supervised-breast-planform13/murderbird-uncaged/assets/audit/cg-supervised-body13/attempt01');bpy.ops.wm.open_mainfile(filepath=str(p/'murderbird-body13.blend'));s=bpy.context.scene;panels=[o for o in s.objects if o.get('cgSupervisedBody13') or o.get('cgSupervisedBody12')];deps=bpy.context.evaluated_depsgraph_get();trees={}
for o in panels:
 ev=o.evaluated_get(deps);mesh=ev.to_mesh();trees[o.name]=BVHTree.FromPolygons([o.matrix_world@v.co for v in mesh.vertices],[tuple(f.vertices) for f in mesh.polygons]);ev.to_mesh_clear()
records=[]
for name in ['CGB13 narrow formed panel 0-0','CGB13 narrow formed panel 3-0','CGB13 narrow formed panel 4-1','CGB13 narrow formed panel 8-2']:
 o=s.objects[name];nu,nv=json.loads(o['body13Grid']);row=int(name.rsplit('-',1)[1]);col=int(name.rsplit(' ',1)[1].split('-')[0]);r=dict(object=name,rootSamples=0,rootCovered=0,longitudinalRootSamples=0,freeEndSamples=0,freeEndBuried=0)
 for f in o.data.polygons:
  v=sum(i//nu/(nv-1) for i in f.vertices)/len(f.vertices)
  if .25<v<.82:continue
  co=o.matrix_world@(sum((o.data.vertices[i].co for i in f.vertices),Vector())/len(f.vertices));n=(o.matrix_world.to_3x3()@f.normal).normalized();n=-n if n.y>0 else n;hits=[]
  for other,t in trees.items():
   if other==name:continue
   h,hn,idx,d=t.ray_cast(co+n*.035,-n,.075)
   if h is not None and .035-d>.0002:hits.append(other)
  if v<=.25:
   r['rootSamples']+=1;r['rootCovered']+=bool(hits);r['longitudinalRootSamples']+=any((x.startswith(f'CGB13 narrow formed panel {col}-') and int(x.rsplit('-',1)[1])<row) or (row==0 and x.startswith('CGB12')) for x in hits)
  else:r['freeEndSamples']+=1;r['freeEndBuried']+=bool(hits)
 records.append(r)
prior={r['object']:r for r in json.loads((p/'extra-preservation-and-overlap.json').read_text())['overlapPanels']};out=dict(method='Independent saved-native read-only selected panel quad-center BVH local-normal probes against 51 evaluated neighboring plates',panels=records,workerProbeCountsMatch=all(all(prior[r['object']][k]==v for k,v in r.items()) for r in records),limits='Sparse static samples; root coverage and side-seam free-end burial are not visible-pixel fractions or animation assurance')
Path('/tmp/cg-qc13-overlap-check.json').write_text(json.dumps(out,indent=2));print('QC13_OVERLAP',json.dumps(out),flush=True)
