from pathlib import Path
import bpy,bmesh,json,math,runpy
from mathutils import Vector
OUT=Path('/tmp/v25-leg-structure/final-fit02')
receipt=json.loads((OUT/'receipt.json').read_text());names=receipt['result']['added']
records=[]
bpy.context.view_layer.update()
for name in names:
 o=bpy.data.objects[name];m=o.matrix_world.to_3x3()
 assert o.parent and o.parent.name in ('left-thigh','right-thigh','left-shin','right-shin')
 assert max(abs(m.col[i].length-1) for i in range(3))<1e-6
 assert max(abs(m.col[i].dot(m.col[j])) for i in range(3) for j in range(i))<1e-6
 assert abs(m.determinant()-1)<1e-6
 bm=bmesh.new();bm.from_mesh(o.data);volume=bm.calc_volume(signed=True)
 assert all(e.is_manifold for e in bm.edges) and volume>0 and math.isfinite(volume);bm.free()
 records.append({'name':name,'owner':o.parent.name,'closed':True,'positiveVolumeM3':volume,'unitRigidWorldBasis':True})
rests={c['owner']:c for c in receipt['result']['structuralContract']}
centers=[]
for n,c in rests.items():
 for end,label in enumerate(('proximal journal','distal captive cheek')):
  p=Vector(c['jointCentersWorld'][end])
  for lateral in (-1,1):
   o=bpy.data.objects[f'V25 {n.replace("-"," ")} {label} {lateral}']
   points=[o.matrix_world@v.co for v in o.data.vertices];centroid=sum(points,Vector())/len(points)
   assert abs(centroid.y-p.y)<1e-6 and abs(centroid.z-p.z)<1e-6
   centers.append({'name':o.name,'rigPivotWorld':list(p),'journalYZCenterErrorM':max(abs(centroid.y-p.y),abs(centroid.z-p.z))})
(OUT/'closed-rigid-joint-center-validation.json').write_text(json.dumps({'status':'PASS static construction properties only','solids':records,'journalCenters':centers,'limits':['Not continuous swept clearance, load analysis or owner likeness acceptance.']},indent=2))
