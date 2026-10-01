"""Verify only the declared Advanced optic material differs; no visual acceptance."""
from pathlib import Path
import hashlib,json,struct,sys

def read(path):
 raw=Path(path).read_bytes(); chunks=[]; pos=12
 while pos<len(raw):
  length,kind=struct.unpack_from('<II',raw,pos);pos+=8;chunks.append((kind,raw[pos:pos+length]));pos+=length
 return json.loads(chunks[0][1]),chunks[1:]
source,candidate,output=map(Path,sys.argv[1:4]);a,ab=read(source);b,bb=read(candidate)
assert ab==bb,'Binary geometry buffers differ'
ma=a.pop('materials');mb=b.pop('materials');assert a==b,'Non-material JSON differs'
assert len(ma)==len(mb)==12
changed=[i for i,(x,y)in enumerate(zip(ma,mb))if x!=y];assert changed==[5],changed
m=mb[5];assert m['name']=='V38 contrast / optic'
assert set(m['extras']['eraFinishes'])=={'builder'}
p=m['extras']['eraFinishes']['builder'];assert p==dict(m['pbrMetallicRoughness'],emissiveFactor=m['emissiveFactor'])
users=[n for n in a['nodes'] if 'mesh'in n and any(p.get('material')==5 for p in a['meshes'][n['mesh']]['primitives'])]
assert {n['name'] for n in users}=={'V31 Advanced optical aperture 1','V31 Advanced optical aperture -1'}
assert all(n['extras']['exteriorEras']=='builder' for n in users)
r={'status':'PASS','sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'candidateSHA256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'onlyChangedMaterial':m['name'],'binaryChunksExact':True,'nonMaterialJSONExact':True,'other11MaterialsExact':True,'builderOnlyUsers':[n['name']for n in users],'candidateProfile':p,'scope':'Preservation and era eligibility only; not appearance or owner acceptance.'}
output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
