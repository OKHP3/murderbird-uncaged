"""Generate tiny per-primitive triangle runs from native component provenance at rest."""
import bpy, json, struct, re, hashlib
import numpy as np
from pathlib import Path
import sys
from collections import defaultdict, Counter
from mathutils import Vector, Matrix, Quaternion
from mathutils.kdtree import KDTree

atelier = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(atelier / 'three-eras' / 'normal-correction'))
from check_normals import GLB_SHA, NATIVE_HASHES

out = Path(sys.argv[sys.argv.index('--') + 1])
out.mkdir(parents=True, exist_ok=True)
glb = atelier / 'delivery' / 'first-choice.glb'
bs = glb.read_bytes()
assert hashlib.sha256(bs).hexdigest() == GLB_SHA
assert hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest() in NATIVE_HASHES
size=struct.unpack_from('<I',bs,12)[0];j=json.loads(bs[20:20+size]);data=memoryview(bs)[28+size:]

def accessor(i):
 a=j['accessors'][i]; bv=j['bufferViews'][a['bufferView']]; width={'VEC3':3,'SCALAR':1}[a['type']]; typ=np.dtype({5123:'<u2',5125:'<u4',5126:'<f4'}[a['componentType']]);return np.ndarray((a['count'],width),dtype=typ,buffer=data,offset=bv.get('byteOffset',0)+a.get('byteOffset',0),strides=(bv.get('byteStride',width*typ.itemsize),typ.itemsize))

bpy.context.scene.frame_set(0); dg=bpy.context.evaluated_depsgraph_get(); clouds=defaultdict(list); cat=Counter();
for ob in bpy.context.scene.objects:
 if ob.type!='MESH' or ob.hide_render or not ob.parent:continue
 region=ob.get('first_choice_region') or ob.get('cg1cRegion') or ob.get('fc_region');region=region.lower(); n=ob.name.lower()
 if region not in ('foot','leg','head','body','torso'):continue
 label=0
 if region in ('foot','leg'):
  side=0 if 'left' in n else 4
  if not ('left' in n or 'right' in n):raise ValueError(n)
  if 'distal cuff' in n:part=3
  elif region=='foot':part=4
  elif 'upper' in n or 'thigh' in n or 'hip' in n or 'knee' in n:part=1
  elif 'shank' in n or 'hock' in n:part=2
  elif 'tarsus' in n or 'ankle' in n:part=3
  else:raise ValueError(n)
  label=side+part
  if region=='foot' and n.startswith('fc '):
   for idx,digit in enumerate(['outer','central','inner','hallux']):
    if ' '+digit+' ' in n:
     label=11+(8 if 'right' in n else 0)+2*idx+int('keeled talon' in n);break
 elif region=='head' and ('mandib' in n or 'lower jaw' in n):label=9
 elif region in ('body','torso') and 'compact posterior' in n and ('1 irregular breast leaf 05' in n or 'compact rear inlet rail' in n):label=10
 ev=ob.evaluated_get(dg); me=ev.to_mesh(); me.calc_loop_triangles(); count=len(me.loop_triangles)
 if count:
  v=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',v);v=v.reshape(-1,3)
  t=np.empty(count*3,np.int32);me.loop_triangles.foreach_get('vertices',t);t=t.reshape(-1,3);center=v[t].mean(axis=1);mm=np.array(ob.matrix_world)
  center=center@mm[:3,:3].T+mm[:3,3]; center=center[:,[0,2,1]];center[:,2]*=-1
  clouds[region].append((center,label));cat[label]+=count
 ev.to_mesh_clear()
print('Native classification',cat,flush=True)
trees={}
for region,arrays in clouds.items():
 total=sum(len(a) for a,l in arrays);tree=KDTree(total)
 for centers,l in arrays:
  for p in centers:tree.insert(p,l)
 tree.balance();trees[region]=tree
parents={k:i for i,n in enumerate(j['nodes']) for k in n.get('children',[])}
world={}
def world_at(i):
 if i not in world:
  n=j['nodes'][i]; q=n.get('rotation',[0,0,0,1]);m=Matrix.LocRotScale(Vector(n.get('translation',[0,0,0])),Quaternion([q[3],*q[:3]]),Vector(n.get('scale',[1,1,1])));world[i]=(world_at(parents[i])@m if i in parents else m)
 return world[i]
streams={}; stats={}; nclass=Counter()
for i,node in enumerate(j['nodes']):
 region=node.get('extras',{}).get('region','');
 if region not in trees:continue
 mesh=j['meshes'][node['mesh']];worldmat=np.array(world_at(i));tree=trees[region]; dev=[]
 for prim in mesh['primitives']:
  matname=j['materials'][prim['material']]['name'];v=accessor(prim['attributes']['POSITION']);ix=accessor(prim['indices']).reshape(-1,3);points=v[ix].mean(axis=1)@worldmat[:3,:3].T+worldmat[:3,3]; labels=[]
  for pt in points:
   _,label,dist=tree.find(pt);dev.append(dist);labels.append(label);nclass[label]+=1
  # Preserve all remaining triangles in their former material and hierarchy.
  spans=[];start=0
  for k,label in enumerate([*labels,None]):
   if k>0 and label!=labels[start]:
    spans.extend([k-start,labels[start]]);start=k
  if any(labels):streams[region+'|'+matname]=[len(labels),spans]
 stats[region]={'triangles':len(dev),'worst_centroid_m':float(np.max(dev)),'p99_m':float(np.quantile(dev,.99)),'within_1e-5':int(np.sum(np.array(dev)<1.e-5))}
print(stats,nclass,flush=True)
# Provenance attachment on GPU uses these runs rather than runtime heuristics or duplicate positions/textures.
(out/'rig-bindings.mjs').write_text('// Frozen first-choice.glb source mesh triangle runs. Each pair is [triangle count, rigid part ID].\nexport const rigidRuns='+json.dumps(streams,ensure_ascii=False,separators=(',',':'))+';\n')
(out/'binding-evidence.json').write_text(json.dumps({'native_objects':1790,'class_ids':{'1-4':'left upper, shank, tarsus, foot','5-8':'right upper, shank, tarsus, foot','9':'mandible','10':'compact posterior lap and rails','11-18':'left outer/central/inner/hallux pairs, separate foot pad plus covers and blade','19-26':'right four matching digit pairs','0':'unchanged'},'mesh_provenance_centroid_matching':stats,'triangle_counts':nclass,'streams':len(streams)},indent=2)+'\n')
