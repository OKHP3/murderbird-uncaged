"""Lossless HTTP transport. Rebuild the input GLB byte for byte before parsing."""
import argparse, ctypes as C, glob, gzip, hashlib, json, os, struct
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument("source",type=Path);parser.add_argument("destination",type=Path);parser.add_argument("--library")
args=parser.parse_args();src=args.source.read_bytes();size=C.c_size_t;ptr=C.c_void_p
lib=C.CDLL(args.library or glob.glob('/Applications/Blender.app/Contents/Resources/*/scripts/addons_core/io_scene_gltf2/libbf_intern_meshopt_bridge.dylib')[0])
for n,types in [('encodeVertexBufferBound',[size,size]),('encodeVertexBuffer',[ptr,size,ptr,size,size]),('encodeIndexSequenceBound',[size,size]),('encodeIndexSequence',[ptr,size,ptr,size])]:
 fn=getattr(lib,n);fn.argtypes=types;fn.restype=size
lib.encodeVertexVersion(0);lib.encodeIndexVersion(1)
n=struct.unpack_from('<I',src,12)[0];g=json.loads(src[20:20+n]);offset=28+n
views=g['bufferViews']; records=[]; chunks=[]; cur=0; access={a.get('bufferView'):a for a in g['accessors']}
def write(start,lim,mode='raw',stride=0):
 chunk=src[start:lim];length=len(chunk)
 if not length:return
 if mode=='v':
  count=length//stride;bound=lib.encodeVertexBufferBound(count,stride);buf=C.create_string_buffer(bound);used=lib.encodeVertexBuffer(buf,bound,chunk,count,stride);chunk=buf.raw[:used]
 elif mode=='i':
  count=length//stride;ids=struct.unpack('<'+('H' if stride==2 else 'I')*count,chunk);arr=(C.c_uint32*count)(*ids);bound=lib.encodeIndexSequenceBound(count,max(ids)+1);buf=C.create_string_buffer(bound);used=lib.encodeIndexSequence(buf,bound,arr,count);chunk=buf.raw[:used]
 records.append([length,len(chunk),mode,stride]);chunks.append(chunk)
for i,v in sorted(enumerate(views),key=lambda x:x[1]['byteOffset']):
 a=access.get(i);start=offset+v['byteOffset'];end=start+v['byteLength']
 if start<cur:raise ValueError('Overlapping buffer views')
 write(cur,start)
 if a and v.get('target') in (34962,34963) and (end-start)%a['count']==0:
  stride=(end-start)//a['count']
  mode='i' if v['target']==34963 and stride in [2,4] else 'v' if stride%4==0 and stride<=256 else 'raw'
  write(start,end,mode,stride)
 else: write(start,end)
 cur=end
write(cur,len(src));header=json.dumps({'sha256':hashlib.sha256(src).hexdigest(),'bytes':len(src),'ranges':records},separators=(',',':')).encode()
payload=struct.pack('<I',len(header))+header+b''.join(chunks)
args.destination.write_bytes(gzip.compress(payload,compresslevel=6,mtime=0))
print(len(src),len(payload),args.destination.stat().st_size)
