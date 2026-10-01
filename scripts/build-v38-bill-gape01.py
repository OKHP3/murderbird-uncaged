from pathlib import Path
import bpy,json,hashlib,runpy,shutil,struct,sys
from mathutils import Vector
R=Path(__file__).resolve().parents[1];A=R/'assets/audit/whole-character-v38/bill-gape01';O=R/'assets/models/whole-character-v38/bill-gape01';N=O/'murderbird-v38-bill-gape01.blend';G=N.with_name(N.stem+'-rigid.glb');SN=R/'assets/models/whole-character-v38/cranial-route01/attempt02/murderbird-v38-cranial-route01-attempt02.blend';SG=SN.with_name(SN.stem+'-rigid.glb');REG=R/'scripts/regions/v38-bill-gape01.py'
SECOND='--attempt02' in sys.argv
if SECOND:
 A=A/'attempt02';O=O/'attempt02';N=O/'murderbird-v38-bill-gape01-attempt02.blend';G=N.with_name(N.stem+'-rigid.glb');SN=R/'assets/models/whole-character-v38/bill-gape01/murderbird-v38-bill-gape01.blend';SG=SN.with_name(SN.stem+'-rigid.glb')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(SN)==('88db35258409b4c967098e3b5a5d01111c99ae9d3568514876732d043e3628a1' if SECOND else '036848c78ad166784851dd9f5916bcd470233dcf4c1bec588c060ec8322c572d');assert sha(SG)==('8e4ba16443db2748ff6b58f8d081ac953be6c4ce709e70bfefe48d2dc8e29adb' if SECOND else '9228b309b84a897051fa381fea0422050fba2013f50b4fc43d5f955dfd99894b');assert not N.exists()and not G.exists()
O.mkdir(parents=True,exist_ok=True);A.mkdir(parents=True,exist_ok=True);shutil.copy2(__file__,A/'executed-builder.py');shutil.copy2(REG,A/'executed-region.py')
def glb(p):
 raw=p.read_bytes();chunks=[];i=12
 while i<len(raw):n,k=struct.unpack_from('<II',raw,i);i+=8;chunks.append((k,raw[i:i+n]));i+=n
 return chunks,json.loads(chunks[0][1])
def sig():
 return {o.name:hashlib.sha256(json.dumps({'v':[list(v.co)for v in o.data.vertices],'f':[list(f.vertices)for f in o.data.polygons],'m':[m.name if m else None for m in o.data.materials]},sort_keys=True).encode()).hexdigest()for o in bpy.data.objects if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(SN));bpy.context.view_layer.update();before=sig();trans={o.name:list(sum((list(row)for row in o.matrix_local),[]))for o in bpy.data.objects};contract=runpy.run_path(str(REG))['apply'](second=SECOND);after=sig();changed=sorted(n for n in before if before[n]!=after[n]);assert set(changed)==set(contract['changedMeshes']);assert all(trans[o.name]==list(sum((list(row)for row in o.matrix_local),[]))for o in bpy.data.objects if o.name!='bill-contact')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(N),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(N));_,source=glb(SG);names={n['name']for n in source['nodes']};bpy.ops.object.select_all(action='DESELECT')
for name in names:o=bpy.data.objects[name];o.hide_set(False);o.hide_viewport=False;o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(G),export_format='GLB',use_selection=True,export_yup=True,export_apply=False,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT');chunks,doc=glb(G);mm={m['name']:m for m in source['materials']};doc['materials']=[mm[m['name']]for m in doc['materials']];j=json.dumps(doc,separators=(',',':')).encode();j+=b' '*((-len(j))%4);raw=bytearray(struct.pack('<4sII',b'glTF',2,0))
for k,c in chunks:d=j if k==0x4e4f534a else c;raw+=struct.pack('<II',len(d),k)+d
struct.pack_into('<I',raw,8,len(raw));G.write_bytes(raw)
scope={'changed':changed,'netOriginalChanged':['V32 formed mandibular bowl']+[f'V32 returned upper bill course {i}'for i in range(3)],'derivation':'first bill-gape01; upper three meshes exact' if SECOND else 'cranial-route02','added':{},'removed':[],'changedNodes':['bill-contact'],'allowedTranslation':['bill-contact'],'allowedReparent':{},'allowedExtras':{n:['constructionDescription','v38BillGape01']for n in changed},'baselineNativeSHA256':sha(SN),'baselineGLBSHA256':sha(SG),'candidateNativeSHA256':sha(N),'candidateGLBSHA256':sha(G)};(A/'scope.json').write_text(json.dumps(scope,indent=2)+'\n');(A/'contract.json').write_text(json.dumps(contract,indent=2)+'\n');print('FROZEN',str(N),sha(N),str(G),sha(G),flush=True)
images=[]
for prefix,model in ([('candidate',N)] if SECOND else [('source',SN),('candidate',N)]):
 bpy.ops.wm.open_mainfile(filepath=str(model));scene=bpy.context.scene
 for o in bpy.data.objects:
  if o.type=='MESH':o.hide_render=o.get('silhouetteStudyHistoricalHidden')is True or o.get('authoringGuide')is True or 'builder'not in str(o.get('exteriorEras','maker,mechanic,builder')).split(',')
  elif o.type=='CURVE':o.hide_render=True
 scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';data=bpy.data.cameras.new('temporary matched headgape camera');data.type='ORTHO';cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);scene.camera=cam
 for name,pos,target,scale in [('head-profile',(-6,0,1.95),(0,-.63,1.63),.55),('head-three-quarter',(-6,-3.5,2.15),(0,-.63,1.63),.60),('full-bird-three-quarter',(-6,-3.5,2.75),(0,-.08,1.03),2.4)]:
  cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=scale;path=A/(prefix+'-'+name+'.png');scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);images.append({'path':str(path.relative_to(R)),'sha256':sha(path)});print('MEDIA',path,flush=True)
receipt={'status':'Frozen deeper hooked bill and open convex mandible proposal; visual/fit pending','native':str(N.relative_to(R)),'nativeSHA256':sha(N),'glb':str(G.relative_to(R)),'glbSHA256':sha(G),'sourceNativeSHA256':sha(SN),'sourceGLBSHA256':sha(SG),'geometryChanged':changed,'allTransformsExactExceptBillContactTranslation':True,'allFiveNeckShellsExact':True,'materialsCopiedExactly':len(doc['materials']),'images':images,'contract':'contract.json','baselineImages':'Matchedsource/currentimages inthis audit; noexisting headcamera frame claimed','limits':contract['limits'],'attempt': 'attempt02' if SECOND else 'attempt01','upperThreeExactAgainstFirst':SECOND};(A/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('READY',flush=True)
