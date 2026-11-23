"""Read a binary glTF locally and record the review rig, packed payload and accessor checks."""
import argparse
from pathlib import Path
import collections
import hashlib
import json
import struct
import numpy as np

parser=argparse.ArgumentParser()
parser.add_argument("glb",type=Path)
parser.add_argument("receipt",type=Path)
opt=parser.parse_args()
raw=opt.glb.read_bytes()
magic,version,total=struct.unpack_from('<4sII',raw)
assert magic==b'glTF' and version==2 and total==len(raw)
length,typ=struct.unpack_from('<I4s',raw,12)
assert typ==b'JSON'
gltf=json.loads(raw[20:20+length])
packed_size,typ=struct.unpack_from('<I4s',raw,20+length);assert typ==b'BIN\x00'
binary=memoryview(raw)[28+length:]
assert len(binary)==packed_size
types={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'}
widths={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}
def array(i):
    a=gltf['accessors'][i];v=gltf['bufferViews'][a['bufferView']]
    dtype=np.dtype(types[a['componentType']]); width=widths[a['type']]
    stride=v.get('byteStride',dtype.itemsize*width)
    ofs=v.get('byteOffset',0)+a.get('byteOffset',0)
    assert ofs+stride*(a['count']-1)+width*dtype.itemsize<=v.get('byteOffset',0)+v['byteLength']<=len(binary)
    values=np.ndarray((a['count'],width),dtype=dtype,buffer=binary,offset=ofs,strides=(stride,dtype.itemsize))
    assert np.isfinite(values).all()
    return values
for i in range(len(gltf['accessors'])): array(i)
nodes=gltf['nodes']
parents={c:i for i,n in enumerate(nodes) for c in n.get('children',[])}
names=[n['name'] for n in nodes]
rig=[]
for i,n in enumerate(nodes):
    if 'fc_region' not in n.get('extras',{}):continue
    # At rest all six pivot empties have identity orientations. Leaf mesh transforms vary.
    pos=np.zeros(3);j=i
    while True:
        t=nodes[j];assert t.get('rotation',[0,0,0,1])==[0,0,0,1] and t.get('scale',[1,1,1])==[1,1,1]
        pos+=t.get('translation',[0,0,0])
        if j not in parents:break
        j=parents[j]
    rig.append(dict(name=names[i],node_index=i,fc_region=n['extras']['fc_region'],
               parent=names[parents[i]] if i in parents else None,
               local_translation=n.get('translation',[0,0,0]),world_rest_pivot=pos.tolist()))
stats=collections.Counter()
normal_range=[1.,1.]
for mesh in gltf['meshes']:
    for p in mesh['primitives']:
        assert p.get('mode',4)==4
        pos=array(p['attributes']['POSITION']);ind=array(p['indices']).reshape(-1,3)
        assert ind.min()>=0 and ind.max()<len(pos)
        stats['indexed_vertices_in_primitives']+=len(pos)
        stats['triangles']+=len(ind)
        stats['draw_primitives']+=1
        ns=array(p['attributes']['NORMAL'])
        nl=np.linalg.norm(ns,axis=1)
        normal_range=[min(normal_range[0],float(nl.min())),max(normal_range[1],float(nl.max()))]
        stats['near_zero_normals']+=int((nl<.001).sum())
        tris=pos[ind];area=np.linalg.norm(np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0]),axis=1)
        stats['triangles_double_area_below_1e-12']+=int((area<1e-12).sum())
anims=[]
for an in gltf['animations']:
    chans=[]
    for c in an['channels']:
        sampler=an['samplers'][c['sampler']]
        times=array(sampler['input']).ravel()
        assert (np.diff(times)>0).all()
        chans.append(dict(node=names[c['target']['node']],property=c['target']['path'],start=float(times.min()),
                          end=float(times.max()),samples=len(times),interpolation=sampler.get('interpolation','LINEAR')))
    anims.append(dict(name=an['name'],channels=chans))
out=dict(asset=opt.glb.name,sha256=hashlib.sha256(raw).hexdigest(),byte_length=len(raw),gltf_version=version,
         stats=dict(stats),normal_length_range=normal_range,scene_count=len(gltf['scenes']),node_count=len(nodes),
         mesh_count=len(gltf['meshes']),material_count=len(gltf['materials']),image_count=len(gltf['images']),
         embedded_only=all('bufferView' in i and 'uri' not in i for i in gltf['images']) and all('uri' not in b for b in gltf['buffers']),
         extensions=gltf.get('extensionsUsed',[]),animations=anims,rig=rig)
assert out['embedded_only']
opt.receipt.write_text(json.dumps(out,indent=2)+'\n')
print(out['stats'],out['normal_length_range'],out['sha256'])
