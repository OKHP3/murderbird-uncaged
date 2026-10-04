import json,struct,array,math,hashlib,ast,re
from pathlib import Path
from types import SimpleNamespace
R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');P=R/'assets/audit/cg-recursive-three-loop01/loop01'
rep={'glbs':{},'dist':{},'guards':{},'views':{}}
for era in ['builder','maker','mechanic']:
 p=P/f'delivery/retained02/{era}/murderbird-recursive-{era}.glb';blob=p.read_bytes();magic,ver,total=struct.unpack_from('<III',blob);assert magic==0x46546c67 and ver==2 and total==len(blob)
 off=12;chunks=[]
 while off<len(blob):
  n,t=struct.unpack_from('<II',blob,off);chunks.append((t,blob[off+8:off+8+n]));off+=8+n
 assert off==len(blob) and [t for t,b in chunks]==[0x4e4f534a,0x004e4942]
 d=json.loads(chunks[0][1]);binary=chunks[1][1];assert len(d['buffers'])==1 and 'uri' not in d['buffers'][0] and d['buffers'][0]['byteLength']<=len(binary)
 assert not d.get('animations') and not d.get('skins');images=[]
 for im in d['images']:
  assert 'uri' not in im and im['mimeType']=='image/png';v=d['bufferViews'][im['bufferView']];b=binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']];assert b[:8]==b'\x89PNG\r\n\x1a\n';w,h=struct.unpack_from('>II',b,16);images.append({'name':im['name'],'width':w,'height':h,'sha256':hashlib.sha256(b).hexdigest()})
 accs=[]
 for a in d['accessors']:
  assert 'sparse' not in a;v=d['bufferViews'][a['bufferView']];off=v.get('byteOffset',0)+a.get('byteOffset',0);n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];fmt={5126:'f',5125:'I',5123:'H',5121:'B'}[a['componentType']];sz=struct.calcsize(fmt);assert v.get('byteStride',sz*n)==sz*n;end=off+a['count']*n*sz;assert end<=v.get('byteOffset',0)+v['byteLength'];arr=array.array(fmt);arr.frombytes(binary[off:end]);assert all(math.isfinite(x) for x in arr);accs.append(arr)
 tris={};primitive_count=0
 for m in d['meshes']:
  for x in m['primitives']:
   assert x.get('mode',4)==4;at=x['attributes'];assert {'POSITION','NORMAL','TEXCOORD_0'}.issubset(at);n=d['accessors'][at['POSITION']]['count'];assert d['accessors'][at['NORMAL']]['count']==n and d['accessors'][at['TEXCOORD_0']]['count']==n;ind=accs[x['indices']];assert len(ind)%3==0 and max(ind)<n;name=d['materials'][x['material']]['name'];tris[name]=tris.get(name,0)+len(ind)//3;primitive_count+=1
 receipt=json.loads((P/f'delivery/retained02/{era}/receipt.json').read_text());expected=receipt['browser_export']['triangles_by_material'];assert tris==expected
 roles=[];role_errors=[]
 for m in d['materials']:
  extras=m.get('extras',{});name=m['name'];met=extras.get('cgMetal05Family');optic=extras.get('opticEra');pbs=m.get('pbrMetallicRoughness',{})
  if met:assert extras.get('cgMetal05Era')==era
  bind={}
  for key,x,ending in [('color',pbs.get('baseColorTexture'),'-color'),('orm',pbs.get('metallicRoughnessTexture'),'-orm'),('normal',m.get('normalTexture'),'-normal'),('emissive',m.get('emissiveTexture'),None)]:
   if x:
    t=d['textures'][x['index']];im=d['images'][t['source']];bind[key]=im['name'];assert x.get('texCoord',0) in (0,1)
    if met and ending and not im['name'].endswith(ending):role_errors.append({'material':name,'role':key,'image':im['name']})
  if optic:
   assert optic==era
   if extras.get('cgOptic13Role')=='core':
    if era=='builder':assert m.get('emissiveFactor')==[1,1,1] and m.get('extensions',{}).get('KHR_materials_emissive_strength',{}).get('emissiveStrength')==5
    else:assert not m.get('emissiveTexture') and m.get('emissiveFactor',[0,0,0])==[0,0,0]
  roles.append({'name':name,'family':met,'era':extras.get('cgMetal05Era'),'optic_era':optic,'bindings':bind,'emissiveFactor':m.get('emissiveFactor'),'emissiveStrength':m.get('extensions',{}).get('KHR_materials_emissive_strength',{}).get('emissiveStrength')})
 assert not role_errors
 rep['glbs'][era]={'sha256':hashlib.sha256(blob).hexdigest(),'bytes':len(blob),'embedded_images':len(images),'meshes':len(d['meshes']),'primitives':primitive_count,'triangles':sum(tris.values()),'triangles_by_material':tris,'producer_triangle_receipt_matches':True,'finite_accessor_values_valid_indices':True,'skins':0,'animations':0,'external_uri':0,'role_bindings':roles,'images':images}
 for kind in ['matched02','retained02']:
  paths=sorted((P/f'delivery/{kind}/{era}').glob('*.png'));views=[]
  for q in paths:
   b=q.read_bytes();assert b[:8]==b'\x89PNG\r\n\x1a\n';wh=struct.unpack_from('>II',b,16);expected=(1280,1280) if q.stem in ('body-detail','head-neck','feet-detail') else (960,1280) if q.stem=='hero' else (1280,853);assert wh==expected;views.append(q.stem)
  assert len(paths)==23;rep['views'][kind+'-'+era]={'count':len(paths),'dimensions':{'whole_profile_turntable':[1280,853],'detail':[1280,1280],'hero':[960,1280]},'names':views}
listed=json.loads((P/'local-build-inspection.json').read_text())['files'];actual={q.relative_to(R/'dist').as_posix():q for q in (R/'dist').rglob('*') if q.is_file()};assert set(actual)=={x['path'] for x in listed};bad=[]
for f in listed:
 q=actual[f['path']]
 if q.stat().st_size!=f['bytes'] or hashlib.sha256(q.read_bytes()).hexdigest()!=f['sha256']:bad.append(f['path'])
assert not bad
rep['dist']={'file_count':len(actual),'matches_frozen_local_build_list':True,'glbs':[k for k in actual if k.endswith('.glb')],'unintended_path_matches':[k for k in actual if any(x in k.split('/') for x in ['audit','.local','archives','provenance'])],'npm_not_rerun_by_qa':True}
a=ast.parse((R/'scripts/cg-recursive-delivery02.py').read_text());fn=next(n for n in a.body if isinstance(n,ast.FunctionDef) and n.name=='run');start=next(i for i,n in enumerate(fn.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='parent' for t in n.targets));end=next(i for i,n in enumerate(fn.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='marker' for t in n.targets));test=compile(ast.fix_missing_locations(ast.Module(body=fn.body[start:end],type_ignores=[])),'actual_runner02_path_guards','exec')
for label,path,ident in [('actual_approved_parent',P/'delivery','safe-test'),('public',R/'public','safe-test'),('private',R/'.local/archives','safe-test'),('frozenmodels',R/'assets/models/cg-supervised01','safe-test'),('frozenaudit',R/'assets/audit/cg-supervised01','safe-test'),('dist_unprotected',R/'dist','safe-test'),('otherhistory_unprotected',R/'assets/models/exterior-v1','safe-test'),('bad_identifier',P/'delivery','../bad')]:
 try:exec(test,{'Path':Path,'re':re,'root':R,'args':SimpleNamespace(output_root=str(path),checkpoint_id=ident)});status='ACCEPTS_PATH_NO_WRITE_EXECUTED'
 except Exception as e:status='REJECTS '+type(e).__name__+': '+str(e)
 rep['guards'][label]=status
Path('/tmp/cg-recursive-loop01-final-safety-static.json').write_text(json.dumps(rep,indent=2));print(json.dumps({k:({e:{a:b for a,b in v.items() if a not in ('images','role_bindings','triangles_by_material')} for e,v in x.items()} if k=='glbs' else x) for k,x in rep.items()},indent=2))
