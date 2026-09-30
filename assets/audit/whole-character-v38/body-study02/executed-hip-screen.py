"""Narrow actual triangle diagnostic on preserved V37/body-study02; no full collision claim."""
import bpy,json
from pathlib import Path
from mathutils import Matrix
from mathutils.bvhtree import BVHTree
R=Path(__file__).resolve().parents[4];A=Path(__file__).resolve().parent
r=json.loads((A/'receipt.json').read_text());N=R/r['outputs']['native']['path'];B=Path(r['inputs']['native']['path'])
changed=set(r['actualChangedMeshes']);added=set(r['addedMeshes'])
protected_supports={f'V28 {kind} {side}' for kind in ('sternal to hip load bow','posterior pelvic load rail') for side in (-1,1)}|{'V28 transverse pelvic load bridge'}
ANGLES=[-.45,-.30,-.15,0,.15,.30,.45]
def tree(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();m.calc_loop_triangles();pts=[e.matrix_world@v.co for v in m.vertices];tris=[tuple(p.vertices) for p in m.loop_triangles];e.to_mesh_clear()
 return BVHTree.FromPolygons(pts,tris,all_triangles=True,epsilon=0),[min(p[k] for p in pts) for k in range(3)],[max(p[k] for p in pts) for k in range(3)]
def screen(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update()
 body=[o for o in bpy.data.objects if o.name in changed|added|protected_supports and o.type=='MESH' and o.parent and o.parent.name=='body']
 bodies={o.name:tree(o) for o in body};results=[]
 for side in ('left','right'):
  owner=bpy.data.objects[side+'-thigh'];rest=owner.matrix_basis.copy();thigh=[o for o in bpy.data.objects if o.type=='MESH' and o.parent==owner]
  for angle in ANGLES:
   owner.matrix_basis=rest@Matrix.Rotation(angle,4,'X');bpy.context.view_layer.update()
   for o in thigh:
    tb,lo,hi=tree(o)
    for name,(bb,blo,bhi) in bodies.items():
     if any(hi[k]<blo[k] or bhi[k]<lo[k] for k in range(3)):continue
     overlaps=bb.overlap(tb)
     if overlaps:results.append({'body':name,'thigh':o.name,'rotationXRad':angle,'trianglePairCount':len(overlaps)})
  owner.matrix_basis=rest;bpy.context.view_layer.update()
 return results
base=screen(B);candidate=screen(N)
keys=lambda rows:{(x['body'],x['thigh'],x['rotationXRad']) for x in rows}
introduced=keys(candidate)-keys(base);retained=keys(candidate)&keys(base)
report={'status':'PASS within this narrow triangle screen' if not candidate else 'WARN: pair-samples remain; inspect before adoption',
 'scope':'Modified/new body-owned stock plus five unchanged V28 supports vs actual direct thigh-owner meshes at seven authored local-X samples',
 'sampleAnglesRad':ANGLES,'protectedSupportNames':sorted(protected_supports),'baselinePairSamples':len(base),'candidatePairSamples':len(candidate),
 'introducedPairSamples':len(introduced),'retainedPairSamples':len(retained),'candidateIntersections':candidate,
 'introducedIntersections':[x for x in candidate if (x['body'],x['thigh'],x['rotationXRad']) in introduced],
 'limits':['BVH triangle overlaps include stock mating or exact contacts; no tolerance classification or containment test',
 'No breast-opening, knee/foot, all-axis hip, continuous motion or physical-load certification']}
(A/'body-thigh-pitch-screen.json').write_text(json.dumps(report,indent=2)+'\n')
print('PITCH_SCREEN',json.dumps({k:report[k] for k in ['status','baselinePairSamples','candidatePairSamples','introducedPairSamples','retainedPairSamples']}),flush=True)
