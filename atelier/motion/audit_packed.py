"""Audit the artifact's image/custody surface without copying reference pixels."""
import bpy,json,hashlib,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
NATIVE=Path(bpy.data.filepath)
GLB=Path(sys.argv[sys.argv.index('--')+1]).resolve()
SOURCE=HERE.parent.parent/'media'
refs=list(SOURCE.glob('cg-references-*'))
refs.extend((SOURCE/'art-murderbird-first-choice-opening-candidate-2026-09-06.png',SOURCE/'murderbird-first-choice-635f0e15.mp4'))
refs_by_sha={hashlib.sha256(p.read_bytes()).hexdigest():p.name for p in refs}
packed=[];external=[];uris=[]
for i in bpy.data.images:
 if i.type in {'RENDER_RESULT','COMPOSITING'}:continue
 data=i.packed_file
 if data:
  b=data.data;h=hashlib.sha256(b).hexdigest()
  packed.append({'name':i.name,'size':len(b),'sha256':h,'same_as_master':refs_by_sha.get(h)})
 elif i.source!='GENERATED':
  external.append(i.name)
g=GLB.read_bytes();n=struct.unpack_from('<I',g,12)[0];j=json.loads(g[20:20+n]);start=28+n
emb=[]
for i in j.get('images',[]):
 if 'bufferView' not in i:uris.append(i.get('uri'));continue
 view=j['bufferViews'][i['bufferView']];offset=start+view.get('byteOffset',0);b=g[offset:offset+view['byteLength']];h=hashlib.sha256(b).hexdigest()
 emb.append({'name':i.get('name',''),'size':len(b),'sha256':h,'same_as_master':refs_by_sha.get(h)})
categories={c:len(getattr(bpy.data,c,[])) for c in ('texts','sounds','movieclips','libraries','cache_files')}
r={'native_sha256':hashlib.file_digest(NATIVE.open('rb'),'sha256').hexdigest(),'glb_sha256':hashlib.sha256(g).hexdigest(),'reference_hash_count':len(refs_by_sha),'native_packed_count':len(packed),'native_packed_bytes':sum(i['size'] for i in packed),'external_native_deps':external,'other_native_resource_types':categories,'glb_embedded_images':len(emb),'glb_external_uris':uris,'full_reference_digest_matches':[i for i in packed+emb if i['same_as_master']],'native_images':packed,'glb_images':emb}
(HERE/'packed-images-check.json').write_text(json.dumps(r,indent=2))
print({k:v for k,v in r.items() if k not in {'native_images','glb_images'}})
