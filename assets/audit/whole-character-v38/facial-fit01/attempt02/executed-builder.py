from pathlib import Path
import bpy,json,hashlib,runpy,shutil,struct,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[1];A=R/'assets/audit/whole-character-v38/facial-fit01';O=R/'assets/models/whole-character-v38/facial-fit01';N=O/'murderbird-v38-facial-fit01.blend';G=N.with_name(N.stem+'-rigid.glb');SN=R/'assets/models/whole-character-v38/facial-shell01/attempt02/murderbird-v38-facial-shell01-attempt02.blend';SG=SN.with_name(SN.stem+'-rigid.glb');REG=R/'scripts/regions/v38-facial-fit01.py'
SECOND='--attempt02' in sys.argv
if SECOND:
 A=A/'attempt02';O=O/'attempt02';N=O/'murderbird-v38-facial-fit01-attempt02.blend';G=N.with_name(N.stem+'-rigid.glb')
if SECOND:
 SN=R/'assets/models/whole-character-v38/facial-fit01/murderbird-v38-facial-fit01.blend';SG=SN.with_name(SN.stem+'-rigid.glb')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(SN)==('3c779529e3fe86dc4964b85c39180a009ee8bcae394c3b17840a09b067234fae'if SECOND else'0dd74d039c007e01f6fce17639ee9382aad2280464e935d5276c38eaa175f9c9');assert sha(SG)==('ccf6e3b6444a940af221555c0250725696a6a72a06466b6408d4dd1c836eed1f'if SECOND else'390617a4b645e31e1dbc92110eeab20777251286d86f5c129315a2522ee3b53f');assert not N.exists()and not G.exists()
O.mkdir(parents=True,exist_ok=True);A.mkdir(parents=True,exist_ok=True);shutil.copy2(__file__,A/'executed-builder.py');shutil.copy2(REG,A/'executed-region.py')
def glb(p):
 raw=p.read_bytes();chunks=[];i=12
 while i<len(raw):n,k=struct.unpack_from('<II',raw,i);i+=8;chunks.append((k,raw[i:i+n]));i+=n
 return chunks,json.loads(chunks[0][1])
def sig():
 return {o.name:hashlib.sha256(json.dumps({'v':[list(v.co)for v in o.data.vertices],'f':[list(f.vertices)for f in o.data.polygons],'m':[m.name if m else None for m in o.data.materials]},sort_keys=True).encode()).hexdigest()for o in bpy.data.objects if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(SN));bpy.context.view_layer.update();before=sig();trans={o.name:list(sum((list(row)for row in o.matrix_local),[]))for o in bpy.data.objects};contract=runpy.run_path(str(REG))['apply'](second=SECOND);after=sig();changed=sorted(n for n in before.keys()&after.keys() if before[n]!=after[n]);assert set(changed)==set(contract['changedMeshes']);assert before.keys()-after.keys()==set(contract['removed']);assert after.keys()-before.keys()==set(contract['added']);assert all(bpy.data.objects[n].parent.name=='head' for n in changed+list(contract['added']));assert all(trans[o.name]==list(sum((list(row)for row in o.matrix_local),[]))for o in bpy.data.objects if o.name in trans )
precheck=runpy.run_path(str(R/'assets/audit/whole-character-v38/facial-fit01/pre-freeze-screen.py'))['screen']();(A/'pre-freeze-screen.json').write_text(json.dumps(precheck,indent=2)+'\n');print('PREFREEZE',json.dumps(precheck['summary']),flush=True)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(N),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(N));_,source=glb(SG);names=({n['name']for n in source['nodes']}-set(contract['removed']))|set(contract['added']);bpy.ops.object.select_all(action='DESELECT')
for name in names:o=bpy.data.objects[name];o.hide_set(False);o.hide_viewport=False;o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(G),export_format='GLB',use_selection=True,export_yup=True,export_apply=False,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT');chunks,doc=glb(G);mm={m['name']:m for m in source['materials']};doc['materials']=[mm[m['name']]for m in doc['materials']];j=json.dumps(doc,separators=(',',':')).encode();j+=b' '*((-len(j))%4);raw=bytearray(struct.pack('<4sII',b'glTF',2,0))
for k,c in chunks:d=j if k==0x4e4f534a else c;raw+=struct.pack('<II',len(d),k)+d
struct.pack_into('<I',raw,8,len(raw));G.write_bytes(raw)
scope={'changed':changed,'added':contract['added'],'removed':contract['removed'],'changedNodes':contract.get('changedNodes',[]),'allowedTranslation':contract.get('changedNodes',[]),'allowedReparent':{},'allowedExtras':{n:['constructionDescription','v38FacialFit01']for n in changed},'baselineNativeSHA256':sha(SN),'baselineGLBSHA256':sha(SG),'candidateNativeSHA256':sha(N),'candidateGLBSHA256':sha(G)};(A/'scope.json').write_text(json.dumps(scope,indent=2)+'\n');(A/'contract.json').write_text(json.dumps(contract,indent=2)+'\n');print('FROZEN',str(N),sha(N),str(G),sha(G),flush=True)
images=[]
for prefix,model in [('candidate',N),('source',SN)]:
 bpy.ops.wm.open_mainfile(filepath=str(model));scene=bpy.context.scene
 for o in bpy.data.objects:
  if o.type=='MESH':o.hide_render=o.get('silhouetteStudyHistoricalHidden')is True or o.get('authoringGuide')is True or 'builder'not in str(o.get('exteriorEras','maker,mechanic,builder')).split(',')
  elif o.type=='CURVE':o.hide_render=True
 scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';data=bpy.data.cameras.new('temporary matched headgape camera');data.type='ORTHO';cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);scene.camera=cam
 for name,pos,target,scale in [('head-profile',(-6,0,1.95),(0,-.63,1.63),.55),('head-three-quarter',(-6,-3.5,2.15),(0,-.63,1.63),.60),('full-bird-three-quarter',(-6,-3.5,2.75),(0,-.08,1.03),2.4)]:
  cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=scale;path=A/(prefix+'-'+name+'.png');scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);images.append({'path':str(path.relative_to(R)),'sha256':sha(path)});print('MEDIA',path,flush=True)
receipt={'status':'Frozen facial support and opening-clearance fit proposal; visual/fit pending','native':str(N.relative_to(R)),'nativeSHA256':sha(N),'glb':str(G.relative_to(R)),'glbSHA256':sha(G),'sourceNativeSHA256':sha(SN),'sourceGLBSHA256':sha(SG),'geometryChanged':changed,'allTransformsExactIncludingBillContact':True,'allFiveNeckShellsExact':True,'materialsCopiedExactly':len(doc['materials']),'images':images,'contract':'contract.json','baselineImages':'Matched source facial-shell01/attempt02 and candidate cameras in this audit','limits':contract['limits']};(A/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('READY',flush=True)
