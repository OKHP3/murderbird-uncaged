"""Inspect final exterior GLBs, UV/material contracts and exact Vite boundary."""
from pathlib import Path
import hashlib,json,struct,datetime,math
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/audit/exterior-v1';OUT.mkdir(exist_ok=True,parents=True)
MODEL=ROOT/'assets/models/uncaged-exterior-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inspect(p):
 b=p.read_bytes();assert b[:4]==b'glTF' and struct.unpack_from('<I',b,8)[0]==len(b)
 n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);bin_start=28+n
 assert not j.get('skins');assert j.get('animations');assert not any(x.get('uri') for x in j.get('buffers',[]))
 names={x.get('name') for x in j['nodes']}
 for x in ['body','neck','head','upper-bill','jaw','breastplate','cranial-cover','left-mantle','right-mantle','left-wing-shield','right-wing-shield','power-core','processing','builder-optics','bill-contact']:assert x in names,x
 variants={}
 for node in j['nodes']:
  if 'mesh' not in node:continue
  e=node.get('extras',{});assert e.get('exteriorEras') in ['maker','mechanic','builder'],node['name']
  variants[e['exteriorEras']]=variants.get(e['exteriorEras'],0)+1
 for m in j['meshes']:
  for primitive in m['primitives']:
   assert 'TEXCOORD_0' in primitive['attributes'],m['name']
   assert 'TANGENT' in primitive['attributes'],m['name']
   for semantic,index in primitive['attributes'].items():
    accessor=j['accessors'][index]
    if accessor['componentType']!=5126:continue
    components={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[accessor['type']]
    view=j['bufferViews'][accessor['bufferView']]
    start=bin_start+view.get('byteOffset',0)+accessor.get('byteOffset',0)
    stride=view.get('byteStride',components*4)
    for vertex in range(accessor['count']):
     assert all(math.isfinite(v) for v in struct.unpack_from('<'+'f'*components,b,start+vertex*stride)),(m['name'],semantic,'non-finite attribute')
   mat=j['materials'][primitive['material']];pbr=mat['pbrMetallicRoughness']
   assert 'baseColorTexture' in pbr and 'metallicRoughnessTexture' in pbr and 'normalTexture' in mat,mat['name']
 textures=[]
 for image in j['images']:
  assert 'bufferView' in image and not image.get('uri')
  bv=j['bufferViews'][image['bufferView']];start=bin_start+bv.get('byteOffset',0);raw=b[start:start+bv['byteLength']]
  assert raw[:8]==b'\x89PNG\r\n\x1a\n'
  width,height=struct.unpack_from('>II',raw,16);assert width==height==1024
  textures.append({'name':image.get('name'),'width':width,'height':height,'bytes':len(raw)})
 assert len(textures)<=7
 assert len(b)<18*1024*1024
 triangles=sum(j['accessors'][p['indices']]['count']//3 for m in j['meshes'] for p in m['primitives'])
 return {'path':str(p.relative_to(ROOT)),'bytes':len(b),'sha256':sha(p),'nodes':len(j['nodes']),'meshes':len(j['meshes']),'trianglesAllVariants':triangles,'variants':variants,'images':textures,'decodedTextureMiBWithMips':len(textures)*1024*1024*4*4/3/1024**2}
def main():
 reports=[inspect(MODEL/'murderbird-exterior-v1.glb')]+[inspect(MODEL/f'murderbird-exterior-{e}-v1.glb') for e in ['maker','mechanic','builder']]
 assert set(reports[0]['variants'])=={'maker','mechanic','builder'}
 for era,r in zip(['maker','mechanic','builder'],reports[1:]):assert set(r['variants'])=={era}
 assert sha(ROOT/'assets/models/uncaged-structure-v1/murderbird-structure-v1.blend')=='9859c1044fe035f140448b23cef477eb9fb3cc4daa8aaf42837ebb8d7dba7541'
 assert (MODEL/'murderbird-exterior-v1.blend').stat().st_size>100000
 files=sorted(p for p in (ROOT/'dist').rglob('*') if p.is_file());assert len(files)==28,len(files)
 forbidden=['.blend','provenance','audit','context','story','private','archive','regional-color','regional-orm','normal.png']
 for p in files:
  name=str(p.relative_to(ROOT/'dist'));assert not any(t in name for t in forbidden),name
  assert not p.read_bytes().startswith(b'version https://git-lfs'),name
 glbs=[p for p in files if p.suffix=='.glb'];assert len(glbs)==1 and sha(glbs[0])==reports[0]['sha256']
 result={'generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'passed','models':reports,'runtimeFiles':[str(p.relative_to(ROOT/'dist')) for p in files],'buildBytes':sum(p.stat().st_size for p in files),'scope':'GLB and output contracts, not artistic acceptance or continuous collision proof'}
 (OUT/'asset-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'passed','bundleMiB':round(reports[0]['bytes']/1024**2,2),'textures':len(reports[0]['images']),'runtimeFiles':len(files)},indent=2))
if __name__=='__main__':main()
