"""Identify only the later splice and later fasteners on the shared, twice-fitted left plate."""
from pathlib import Path
import sys,hashlib,json,struct
import numpy as np
import bpy
from mathutils.kdtree import KDTree
atelier = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(atelier / 'mantle'))
sys.path.insert(0, str(atelier / 'three-eras' / 'normal-correction'))
from mantle import Hardware, place_repair
from check_normals import GLB_SHA, NATIVE_HASHES

out = Path(sys.argv[sys.argv.index('--') + 1])
out.mkdir(parents=True, exist_ok=True)
glb = atelier / 'delivery' / 'first-choice.glb'
assert hashlib.sha256(glb.read_bytes()).hexdigest() == GLB_SHA
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest() in NATIVE_HASHES
bpy.context.scene.frame_set(0);objs=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('first_choice_region','').lower()=='wing.l']; panels=[o for o in objs if o.name.startswith('CGB05 -1 shield curved feather ') or 'small shoulder covert' in o.name or o.name=='CG supervised left compact shield recess'];
class Audit(Hardware):
 def __init__(self):super().__init__('wing.L',None);self.calls=[]
 def surface(self,*a,**kw):
  old=len(self.faces);super().surface(*a,**kw);self.calls.append((old,len(self.faces)))
a=Audit();assert place_repair(None,panels,a);assert len(a.calls)==12
ob=bpy.data.objects['FC wing.L | plate lips, rivets and fittings'];start=len(ob.data.polygons)-len(a.faces);newer=set();
for op in (1,6,7,8,9,10,11):newer.update(range(start+a.calls[op][0],start+a.calls[op][1]))
dg=bpy.context.evaluated_depsgraph_get();records=[]
for o in objs:
 ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();verts=np.empty(len(m.vertices)*3,np.float32);m.vertices.foreach_get('co',verts);tri=np.empty(len(m.loop_triangles)*3,np.int32);m.loop_triangles.foreach_get('vertices',tri);poly=np.empty(len(m.loop_triangles),np.int32);m.loop_triangles.foreach_get('polygon_index',poly)
 c=verts.reshape(-1,3)[tri.reshape(-1,3)].mean(axis=1);mat=np.array(o.matrix_world);c=c@mat[:3,:3].T+mat[:3,3];c=c[:,[0,2,1]];c[:,2]*=-1
 tags=np.isin(poly,list(newer)) if o==ob else np.zeros(len(c),np.bool_);records.append((c,tags));ev.to_mesh_clear()
tree=KDTree(sum(len(c) for c,t in records));
for c,t in records:
 for p,l in zip(c,t):tree.insert(p,int(l))
tree.balance();raw=glb.read_bytes();size=struct.unpack_from('<I',raw,12)[0];j=json.loads(raw[20:20+size]);b=memoryview(raw)[28+size:]
def access(i):
 a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];w={'VEC3':3,'SCALAR':1}[a['type']];dt=np.dtype({5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']]);return np.ndarray((a['count'],w),dtype=dt,buffer=b,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',w*dt.itemsize),dt.itemsize))
node=next(n for n in j['nodes'] if n.get('extras',{}).get('region')=='wing.l');spans={};count=0;maxdist=0
for p in j['meshes'][node['mesh']]['primitives']:
 c=access(p['attributes']['POSITION'])[access(p['indices']).reshape(-1,3)].mean(axis=1);name=j['materials'][p['material']]['name'];runs=[];begin=None
 for i,pt in enumerate(c):
  _,lab,dist=tree.find(pt);maxdist=max(maxdist,dist)
  if lab and begin is None:begin=i
  if not lab and begin is not None:runs.extend([begin,i-begin]);count+=i-begin;begin=None
 if begin is not None:runs.extend([begin,len(c)-begin]);count+=len(c)-begin
 if runs:spans[name]={'total':len(c),'remove':runs}
assert maxdist<1e-5 and count>50
print('Omitted triangles',count,'matching error',maxdist,spans)
(out/'maker-shoulder.json').write_text(json.dumps({'removed_triangles':count,'native_centroid_max_delta':maxdist,'spans':spans},ensure_ascii=False,indent=2)+'\n')
