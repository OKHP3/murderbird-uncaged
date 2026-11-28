"""Derive a first-draw texture tier, and the exact byte reconstruction of the full model."""
import gzip,hashlib,io,json,struct,sys
from pathlib import Path
from PIL import Image
src=Path(sys.argv[1]).read_bytes();folder=Path(sys.argv[2]);n=struct.unpack_from('<I',src,12)[0];base=28+n
doc=json.loads(src[20:20+n]);old=json.loads(src[20:20+n]);image_ids={e['bufferView'] for e in doc['images']}
small=bytearray();textures=bytearray();rebuild=bytearray(len(src));rebuild[:base]=src[:base]
for i,v in enumerate(doc['bufferViews']):
 start=v['byteOffset']+base;payload=src[start:start+v['byteLength']];rebuild[start:start+len(payload)]=payload
 if i in image_ids:
  textures.extend(payload);image=Image.open(io.BytesIO(payload));fmt=image.format;image.thumbnail((192,192),Image.Resampling.LANCZOS)
  out=io.BytesIO();image.save(out,format=fmt,**({'quality':84}if fmt=='JPEG' else {'optimize':True}));payload=out.getvalue()
 small.extend(b'\0'*(-len(small)%4));v['byteOffset']=len(small);v['byteLength']=len(payload);small.extend(payload)
small.extend(b'\0'*(-len(small)%4));doc['buffers'][0]['byteLength']=len(small)
def enc(j):return json.dumps(j,separators=(',',':'),ensure_ascii=False).encode()
js=enc(doc);js+=b' '*(-len(js)%4)
new=struct.pack('<4sIIII',b'glTF',2,28+len(js)+len(small),len(js),0x4e4f534a)+js+struct.pack('<II',len(small),0x004e4942)+small
assert rebuild==src, 'Unknown GLB padding must be preserved explicitly'
(folder/'first-draw.glb').write_bytes(new)
(folder/'detail.pack').write_bytes(gzip.compress(src[:base]+textures,mtime=0))
print('first draw SHA',hashlib.sha256(new).hexdigest(),'bytes',len(new),'detail pack', (folder/'detail.pack').stat().st_size)
