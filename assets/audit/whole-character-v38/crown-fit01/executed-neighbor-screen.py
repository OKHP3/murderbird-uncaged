"""Blender FILE -- BASE CANDIDATE OUTPUT. Actual rest triangles, same1e-7epsilon.
Changed trailing leaves against all builder-eligible rigid meshes; no same-owner exclusion.
"""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
base,candidate,output=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not output.exists()
def screen(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();rows=[]
 for o in bpy.data.objects:
  if o.type!='MESH' or not len(o.data.vertices) or o.get('authoringGuide') is True or 'builder' not in str(o.get('exteriorEras','maker,mechanic,builder')).split(','):continue
  o.data.calc_loop_triangles();p=[o.matrix_world@v.co for v in o.data.vertices]
  rows.append({'name':o.name,'owner':o.parent.name if o.parent else None,'points':p,'triangles':[tuple(t.vertices) for t in o.data.loop_triangles],'lo':[min(v[k] for v in p) for k in range(3)],'hi':[max(v[k] for v in p) for k in range(3)],'bvh':None})
 selected=[r for r in rows if r['name'].startswith('V38 swept crown course ') and r['name'].endswith(' leaf 2')];assert len(selected)==29;pairs={};tested=0;aabb=0
 for a in selected:
  for b in rows:
   if a is b or (b in selected and a['name']>b['name']):continue
   tested+=1
   if any(a['hi'][k]<b['lo'][k] or b['hi'][k]<a['lo'][k] for k in range(3)):continue
   aabb+=1
   for row in (a,b):
    if row['bvh'] is None:row['bvh']=BVHTree.FromPolygons(row['points'],row['triangles'],all_triangles=True,epsilon=1e-7)
   hits=a['bvh'].overlap(b['bvh'])
   if hits:
    names=sorted((a['name'],b['name']));key=' | '.join(names)
    partner=a['name'].rsplit(' leaf ',1)[0]+' leaf 1';category='paired lap' if b['name']==partner else 'neighboring crown course' if b['name'].startswith('V38 swept crown course ') else 'fixed seat/backing/other rigid neighbor'
    pairs[key]={'a':names[0],'b':names[1],'triangleSurfaceCandidates':len(hits),'category':category,'owners':[a['owner'],b['owner']]}
 return {'selectedTrailingLeaves':len(selected),'testedObjectPairs':tested,'aabbCandidates':aabb,'surfacePairs':pairs}
before=screen(base);after=screen(candidate);old=before['surfacePairs'];new=after['surfacePairs'];delta={'introducedPairs':[new[k] for k in sorted(set(new)-set(old))],'retainedPairs':[{'before':old[k],'after':new[k]} for k in sorted(set(new)&set(old))],'removedPairs':[old[k] for k in sorted(set(old)-set(new))]}
report={'status':'actual rest-surface diagnostic; inspect all neighboring/backing dispositions before acceptance','inputs':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (base,candidate)],'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'epsilonM':1e-7,'baseline':before,'candidate':after,'delta':delta,'limits':['Actual raw triangulated surfaces, identical1e-7BVH epsilon as root paired screen. AABB prefilter only; includes same-owner neighboring courses and fixed seats/backing.','Counts do not measure penetration or containment. A retained pair can change depth/severity; no absence-of-interference or full collision PASS follows.','Rest pose only. No self-intersection, continuous sweep, tolerances, forces or engineering certification.']}
output.write_text(json.dumps(report,indent=2)+'\n');print('NEIGHBOR_DELTA',json.dumps({'old':len(old),'new':len(new),'introduced':len(delta['introducedPairs']),'removed':len(delta['removedPairs']),'introducedRows':delta['introducedPairs']}),flush=True)
