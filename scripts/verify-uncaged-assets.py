"""Validate the study's real binaries, named assembly contract and build boundary."""
from pathlib import Path
import hashlib,json,struct
ROOT=Path(__file__).resolve().parents[1]
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
model=ROOT/'assets/models/uncaged-shield-study/murderbird-shield-study.glb'
data=model.read_bytes()
assert data[:4]==b'glTF','GLB is missing or an LFS pointer'
magic,version,size=struct.unpack_from('<III',data)
assert version==2 and size==len(data)
length,kind=struct.unpack_from('<II',data,12)
assert kind==0x4e4f534a
gltf=json.loads(data[20:20+length])
required=['body','neck','head','jaw','breastplate','cranial-cover','winding-drive','power-core','processing','industrial-repairs','builder-optics','left-mantle','right-mantle','left-wing-shield','right-wing-shield']
names=[n.get('name') for n in gltf['nodes']]
for name in required:assert names.count(name)==1,name
for side in ['left','right']:
    child=names.index(side+'-wing-shield'); parent=names.index(side+'-mantle')
    assert child in gltf['nodes'][parent].get('children',[]),'Shield must articulate from its own shoulder'
assert not any(x.get('uri') for x in gltf.get('buffers',[])+gltf.get('images',[])),'GLB must be self-contained'
assert all(a['count']>0 for a in gltf['accessors'])
triangles=sum(gltf['accessors'][p['indices']]['count']//3 for m in gltf['meshes'] for p in m['primitives'])
blend=ROOT/'assets/models/uncaged-shield-study/murderbird-shield-study.blend'
assert len(blend.read_bytes())>10000 and not blend.read_bytes().startswith(b'version https://git-lfs')
files=sorted(p for p in (ROOT/'dist').rglob('*') if p.is_file())
assert files,'Build first'
public={p.relative_to(ROOT/'public').as_posix() for p in (ROOT/'public').rglob('*') if p.is_file()}
allowed=['index-','theme-player-','murderbird-shield-study-','murderbird-unified-master-03-2026-09-06-960-']
for p in files:
    rel=p.relative_to(ROOT/'dist').as_posix()
    assert rel in public or rel=='index.html' or (rel.startswith('assets/') and any(p.name.startswith(x) for x in allowed)),f'Unapproved build path: {rel}'
    assert not p.read_bytes().startswith(b'version https://git-lfs'),f'LFS pointer in build: {rel}'
    assert p.suffix not in ['.blend','.py','.md','.zip'],f'Source artifact in build: {rel}'
models=[p for p in files if p.suffix=='.glb'];assert len(models)==1 and digest(models[0])==digest(model),'Built model differs from source export'
report={'status':'verified-local','date':'2026-09-27','model':{'path':str(model.relative_to(ROOT)),'bytes':len(data),'sha256':digest(model),'nodes':len(gltf['nodes']),'meshes':len(gltf['meshes']),'triangles':triangles,'assemblies':required,'selfContained':True},'editableSource':{'path':str(blend.relative_to(ROOT)),'bytes':blend.stat().st_size,'sha256':digest(blend)},'build':{'totalBytes':sum(p.stat().st_size for p in files),'files':[{'path':p.relative_to(ROOT/'dist').as_posix(),'bytes':p.stat().st_size,'sha256':digest(p)} for p in files]},'limits':['Does not prove remote LFS retrieval, deployed behavior, owner acceptance, or mechanical simulation.']}
out=ROOT/'assets/audit/uncaged-shield-review/asset-validation.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'modelBytes':len(data),'uniqueTriangles':triangles,'buildFiles':len(files),'totalBuildBytes':report['build']['totalBytes'],'status':'verified-local'},indent=2))
