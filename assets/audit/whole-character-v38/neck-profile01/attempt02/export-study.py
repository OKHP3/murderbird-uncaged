import bpy,json,hashlib,struct
from pathlib import Path
R=Path(__file__).resolve().parents[5];A=Path(__file__).resolve().parent
N=R/'assets/models/whole-character-v38/neck-profile01/attempt02/murderbird-v38-neck-profile01-attempt02.blend';G=N.with_name(N.stem+'-rigid.glb');SN=R/'assets/models/whole-character-v38/cervical-laps01/attempt02/murderbird-v38-cervical-laps01-attempt02.blend';SG=SN.with_name(SN.stem+'-rigid.glb')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(N)=='5ca3fc5c2f8da2057c60c5a7e904e7abe441d632b6e24c559d3ebee03218f3ab';assert sha(SG)=='4e3e721040cdde3316eb84f19051829e771a93f80e243975e572e5707a6f007c';assert not G.exists()
def glb(p):
 raw=p.read_bytes();assert raw[:4]==b'glTF';chunks=[];i=12
 while i<len(raw):
  n,k=struct.unpack_from('<II',raw,i);i+=8;chunks.append((k,raw[i:i+n]));i+=n
 return chunks,json.loads(chunks[0][1])
def sig():
 return {o.name:hashlib.sha256(json.dumps({'vertices':[list(v.co)for v in o.data.vertices],'faces':[list(f.vertices)for f in o.data.polygons],'materials':[m.name if m else None for m in o.data.materials],'smooth':[f.use_smooth for f in o.data.polygons]},sort_keys=True).encode()).hexdigest()for o in bpy.data.objects if o.type=='MESH'}
_,source=glb(SG);srcnames={n['name']for n in source['nodes']};bpy.ops.wm.open_mainfile(filepath=str(SN));before=sig();bpy.ops.wm.open_mainfile(filepath=str(N));after=sig()
removed=sorted(o.name for o in bpy.data.objects if o.type=='MESH'and o.get('silhouetteStudyHistoricalHidden')is True);assert len(removed)==68 and set(removed)<=srcnames
added=sorted(n for n in after if n not in before);assert len(added)==5
changed=sorted(n for n in before.keys()&after.keys()if before[n]!=after[n]and n not in removed)
select=(srcnames-set(removed))|set(added);assert all(n in bpy.data.objects for n in select)
bpy.ops.object.select_all(action='DESELECT')
for n in select:
 o=bpy.data.objects[n];o.hide_set(False);o.hide_viewport=False;o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(G),export_format='GLB',use_selection=True,export_yup=True,export_apply=False,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT')
chunks,doc=glb(G);materialmap={m['name']:m for m in source['materials']}
assert not source.get('images')and not source.get('textures')
for i,m in enumerate(doc['materials']):doc['materials'][i]=materialmap[m['name']]
rawdoc=json.dumps(doc,separators=(',',':')).encode();rawdoc+=b' '*((-len(rawdoc))%4);raw=bytearray(struct.pack('<4sII',b'glTF',2,0))
for k,c in chunks:
 d=rawdoc if k==0x4e4f534a else c;raw+=struct.pack('<II',len(d),k)+d
struct.pack_into('<I',raw,8,len(raw));G.write_bytes(raw)
old={n['name']:n for n in source['nodes']};new={n['name']:n for n in doc['nodes']};assert set(new)==select
parents=lambda d:{d['nodes'][c]['name']:n['name']for n in d['nodes']for c in n.get('children',[])}
op=parents(source);np=parents(doc);assert all(np.get(n)==op.get(n)for n in srcnames-set(removed))
tr=[];extras={}
for name in srcnames-set(removed):
 a=old[name];b=new[name]
 if any(a.get(k)!=b.get(k)for k in ['translation','rotation','scale','matrix']):tr.append(name)
 ea=a.get('extras',{});eb=b.get('extras',{});fields=[k for k in ea.keys()|eb.keys()if ea.get(k)!=eb.get(k)]
 if fields:extras[name]=fields
scope={'changed':changed,'added':{n:{'parent':np[n],'exteriorEras':new[n].get('extras',{}).get('exteriorEras'),'constructionClass':'proposed-passive-silhouette-proxy'}for n in added},'removed':removed,'changedNodes':tr,'allowedTranslation':tr,'allowedExtras':extras,'allowedReparent':{},'status':'Simple rigid silhouette study, visual direction only.68historical native skins explicitly excluded from export, not deleted from native.','baselineNativeSHA256':sha(SN),'baselineGLBSHA256':sha(SG),'candidateNativeSHA256':sha(N),'candidateGLBSHA256':sha(G)}
(A/'scope.json').write_text(json.dumps(scope,indent=2)+'\n');report={'native':{'path':str(N.relative_to(R)),'sha256':sha(N)},'glb':{'path':str(G.relative_to(R)),'sha256':sha(G)},'sourceGLB':{'path':str(SG.relative_to(R)),'sha256':sha(SG)},'changedGeometryCount':len(changed),'added':5,'explicitExcludedHistoricalNodes':68,'compensationTransformCount':len(tr),'sameParentForRetainedNodes':True,'materialsCopiedExactly':len(doc['materials']),'nativeNotRewritten':True,'notClaimed':['No collision/lap/bodyphysics/supportengineering or fullarmor acceptance. Root independent unchangedgeometry/worldrest/actualcontact validation separate.','Round stock visible through narrowed upper shell is an interference. No third geometry correction.']}
(A/'export-receipt.json').write_text(json.dumps(report,indent=2)+'\n');print('EXPORT_READY',json.dumps(report),flush=True)
