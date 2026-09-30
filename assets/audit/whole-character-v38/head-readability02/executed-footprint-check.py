"""Read-only preserved finite shield endfoot witnesses, no attachment approval."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
base,candidate,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not out.exists();reports=[]
for label,path in [('source',base),('candidate',candidate)]:
 bpy.ops.wm.open_mainfile(filepath=str(path));rows=[]
 for side in(-1,1):
  for course in range(3):
   o=bpy.data.objects[f'V38 optic cheek shield {side} {course}'];pts=[o.matrix_world@v.co for v in o.data.vertices];ends=[]
   for end,indices in [(0,range(21)),(1,range(70,91))]:
    name=f'V33 diagonal brow receiver {side} 0'if course==0 and end==0 else f'V31 fixed temporal receiving wall {side}';q=bpy.data.objects[name];q.data.calc_loop_triangles();tree=BVHTree.FromPolygons([q.matrix_world@v.co for v in q.data.vertices],[tuple(t.vertices)for t in q.data.loop_triangles],all_triangles=True);samples=[]
    for i in indices:
     point=pts[i+91];hit=tree.find_nearest(point);samples.append({'innerFootVertex':i+91,'world':list(point),'nearestFinitePoint':list(hit[0]),'normal':list(hit[1]),'distanceM':hit[3],'triangle':hit[2]})
    ends.append({'end':end,'target':name,'samples':samples,'gapRangeM':[min(x['distanceM']for x in samples),max(x['distanceM']for x in samples)]})
   rows.append({'name':o.name,'ends':ends})
 reports.append({'label':label,'rows':rows})
delta=[]
for a,b in zip(reports[0]['rows'],reports[1]['rows']):
 maxmove=max(sum((x-y)**2 for x,y in zip(p['world'],q['world']))**.5 for e,f in zip(a['ends'],b['ends'])for p,q in zip(e['samples'],f['samples']));maxgap=max(abs(p['distanceM']-q['distanceM'])for e,f in zip(a['ends'],b['ends'])for p,q in zip(e['samples'],f['samples']));assert maxmove==0
 delta.append({'name':a['name'],'actualFootPositionDeltaM':maxmove,'maximumNearestFiniteGapDeltaM':maxgap})
out.write_text(json.dumps({'status':'Actual endfoot witnesses preserved, not supportedwholeface/fastening certificate','models':reports,'delta':delta,'limits':['42pairedstockfootvertices/shield, actualnearestfinitewall/brow point+normal; no centroidproxy.','Pointgap does not certify interveningfoot triangles or manufacturing/motion fit. Strictfullpool contacts reported separately.']},indent=2)+'\n')
