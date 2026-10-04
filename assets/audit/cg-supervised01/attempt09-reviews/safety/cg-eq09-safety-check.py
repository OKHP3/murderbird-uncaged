import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,struct,math,urllib.request,datetime
R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=R/'assets/audit/cg-supervised01/attempt09/frozen-manifest.json'
m=json.loads(manifest.read_text());bad=[]
for x in m['files']:
 p=R/x['path']
 if not p.is_file() or p.stat().st_size!=x['bytes'] or sha(p)!=x['sha256']:bad.append(x['path'])
print('MANIFEST',len(m['files']),'BAD',bad,flush=True)
result={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manifest_file_count':len(m['files']),'manifest_mismatches':bad,'manifest_sha256':sha(manifest),'contract_sha256':sha(R/'assets/audit/cg-supervised01/attempt09/review-contract.json'),'glbs':{},'dist':{},'local_http':{}}
for era in ('builder','maker','mechanic'):
 p=R/f'assets/models/cg-supervised01/attempt09/murderbird-supervised-{era}.glb';b=p.read_bytes();magic,version,size=struct.unpack_from('<4sII',b);assert magic==b'glTF' and version==2 and size==len(b)
 pos=12;chunks=[]
 while pos<len(b):
  n,t=struct.unpack_from('<II',b,pos);pos+=8;chunks.append((t,memoryview(b)[pos:pos+n]));pos+=n
 assert pos==len(b) and len(chunks)==2 and chunks[0][0]==0x4e4f534a and chunks[1][0]==0x004e4942
 j=json.loads(bytes(chunks[0][1]));bin=chunks[1][1];assert j['buffers'][0]['byteLength']<=len(bin)
 uris=[]
 def walk(v):
  if isinstance(v,dict):
   uris.extend(x for k,x in v.items() if k=='uri')
   for x in v.values():walk(x)
  elif isinstance(v,list):
   for x in v:walk(x)
 walk(j)
 assert not uris and not j.get('animations') and not j.get('skins')
 assert all('bufferView' in i and i['mimeType'] in ('image/png','image/jpeg') for i in j['images'])
 failed=[];finite_count=0;access=[]
 for i,a in enumerate(j['accessors']):
  assert 'sparse' not in a
  view=j['bufferViews'][a['bufferView']];components={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];format={5126:'f',5125:'I',5123:'H',5121:'B',5122:'h',5120:'b'}[a['componentType']];component_size=struct.calcsize('<'+format);width=components*component_size;stride=view.get('byteStride',width);off=view.get('byteOffset',0)+a.get('byteOffset',0);end=off+(a['count']-1)*stride+width
  assert end<=view.get('byteOffset',0)+view['byteLength'] and end<=len(bin)
  vals=[]
  if format=='f':
   if stride==width:
    assert all(math.isfinite(v[0]) for v in struct.iter_unpack('<f',bin[off:off+a['count']*width])),i
   else:
    for n in range(a['count']):assert all(math.isfinite(x) for x in struct.unpack_from('<'+format*components,bin,off+n*stride)),i
   finite_count+=a['count']*components
  access.append((a,view,components,format,width,stride,off))
 triangles=0;primitive_count=0;index_max=[]
 for mesh in j['meshes']:
  for pr in mesh['primitives']:
   primitive_count+=1;assert pr.get('mode',4)==4;assert 0<=pr['material']<len(j['materials']);assert 'POSITION' in pr['attributes'] and 'NORMAL' in pr['attributes'] and 'TEXCOORD_0' in pr['attributes'];count=j['accessors'][pr['attributes']['POSITION']]['count'];assert all(j['accessors'][a]['count']==count for a in pr['attributes'].values());a,v,c,f,w,s,o=access[pr['indices']];assert c==1 and a['count']%3==0
   mx=max(x[0] for x in struct.iter_unpack('<'+f,bin[o:o+a['count']*w]));assert mx<count;triangles+=a['count']//3;index_max.append(mx)
 # Only exported material batches are named; check known guide identifiers absent.
 names=[n.get('name','') for n in j.get('nodes',[])]+[n.get('name','') for n in j['meshes']]
 forbidden=[n for n in names if any(s in n.lower() for s in ('authoringguide','contact ground','review floor'))]
 assert not forbidden
 result['glbs'][era]={'path':str(p.relative_to(R)),'sha256':sha(p),'bytes':len(b),'materials':len(j['materials']),'images':len(j['images']),'meshes':len(j['meshes']),'accessors':len(j['accessors']),'finite_float_values':finite_count,'primitives':primitive_count,'triangles':triangles,'uri_count':len(uris),'skins':len(j.get('skins',[])),'animations':len(j.get('animations',[])),'embedded_image_bounds':all(j['bufferViews'][i['bufferView']]['byteOffset']+j['bufferViews'][i['bufferView']]['byteLength']<=len(bin) for i in j['images']),'forbidden_guide_name_matches':forbidden,'guide_limit':'Name scan alone cannot establish no guide geometry; export filter and receipt inspected separately.'}
 print('GLB',era,result['glbs'][era],flush=True)
receipt=json.loads((R/'assets/audit/cg-supervised01/build-verification-final09.json').read_text());files=sorted(p for p in (R/'dist').rglob('*') if p.is_file());bad=[]
for x in receipt['file_hashes']:
 p=R/x['path']
 if not p.is_file() or sha(p)!=x['sha256']:bad.append(x['path'])
forbidden=[str(p.relative_to(R)) for p in files if any(s in str(p.relative_to(R)).lower() for s in ('cg-supervised','attempt09','provenance','archives','music-session','\.blend'))]
result['dist']={'file_count':len(files),'receipt_hash_mismatches':bad,'forbidden_name_matches':forbidden,'runtime_glbs':[str(p.relative_to(R)) for p in files if p.suffix=='.glb'],'localbuild_receipt_sha256':sha(R/'assets/audit/cg-supervised01/build-verification-final09.json'),'build_execution':'Read receipt and verified existing output; reviewer did not run npm or modify dist.'}
for rel in ['assets/audit/cg-supervised01/browser09-review.html','scripts/cg-supervised-browser05.js','assets/audit/cg-supervised01/attempt09/browser-camera.json']+[f'assets/audit/cg-supervised01/{part}/{era}/canon-{mode}.png' for era in ('builder','maker','mechanic') for mode in ('neutral','workshop') for part in ('attempt09','attempt09-baseline')]+['assets/img/library/'+n for n in ('murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg','murderbird-unified-maker-clean-candidate-2026-09-06.png','murderbird-unified-mechanic-candidate-2026-09-06.png')]:
 try:
  with urllib.request.urlopen('http://127.0.0.1:5188/'+rel,timeout=10) as response:
   data=response.read();item={'status':response.status,'bytes':len(data),'content_type':response.headers.get('Content-Type'),'same_as_local':hashlib.sha256(data).hexdigest()==sha(R/rel)}
 except Exception as e:item={'error':str(e)}
 result['local_http'][rel]=item
print('DIST',result['dist'],flush=True);print('HTTP',len(result['local_http']),[k for k,v in result['local_http'].items() if v.get('status')!=200 or not v.get('same_as_local')],flush=True)
Path('/tmp/cg-eq09-safety-checks.json').write_text(json.dumps(result,indent=2))
