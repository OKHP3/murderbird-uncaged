import bpy,runpy,json
from pathlib import Path
from mathutils import Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[4]
POSE={'neck':.10675220489501955,'cervical-mid-a':.10675220489501955,'cervical-mid-b':.10675220489501955,'cervical-upper':.10675220489501955,'head':-.5090505059024657}
def scan():
 bpy.context.view_layer.update();data={};neck=[]
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  anc=[];p=o.parent
  while p:anc.append(p.name);p=p.parent
  if any(n in anc for n in POSE):neck.append(o.name)
  o.data.calc_loop_triangles();data[o.name]=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(t.vertices)for t in o.data.loop_triangles],all_triangles=True,epsilon=0)
 return [{'a':a,'b':b,'pairs':len(hit)}for a in ['V30 continuous tapered breast liner']+[f'V34 formed breast course {r} plate {c}'for r,n in[(1,5),(2,6)]for c in range(1,n+1)]for b in neck if(hit:=data[a].overlap(data[b]))]
def pose():
 for n,a in POSE.items():o=bpy.data.objects[n];o.matrix_basis=o.matrix_basis@Matrix.Rotation(a,4,'X')
p=ROOT/'assets/models/whole-character-v38/lower-support02/murderbird-v38-lower-support02.blend';bpy.ops.wm.open_mainfile(filepath=str(p));pose();before=scan();bpy.ops.wm.open_mainfile(filepath=str(p));c=runpy.run_path(str(ROOT/'scripts/regions/v38-breast-envelope02.py'))['apply']();pose();after=scan();out={'source':before,'candidate':after,'actualReturnRefit':c['actualReturnRefit']};(Path(__file__).parent/'pre-save-contact.json').write_text(json.dumps(out,indent=2));print('CONTACT',json.dumps(out))
