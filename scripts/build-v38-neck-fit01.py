from pathlib import Path
import bpy,json,hashlib,runpy,shutil,struct
from mathutils import Vector
R=Path(__file__).resolve().parents[1];A=R/'assets/audit/whole-character-v38/neck-fit01/attempt02';O=R/'assets/models/whole-character-v38/neck-fit01/attempt02';N=O/'murderbird-v38-neck-fit01-attempt02.blend';G=N.with_name(N.stem+'-rigid.glb');SN=R/'assets/models/whole-character-v38/neck-fit01/murderbird-v38-neck-fit01.blend';SG=SN.with_name(SN.stem+'-rigid.glb');REG=R/'scripts/regions/v38-neck-fit01.py'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(SN)=='96afe776d8631c21d5b7b2be9ac98d5fc09a5ac2c64ef3fa8ed91804e0eef426';assert sha(SG)=='1d2c7ace96f8f107d85494602d5d4f2c81d879189093d80ce44bdd8266dba010';assert not N.exists()and not G.exists()
O.mkdir(parents=True,exist_ok=True);A.mkdir(parents=True,exist_ok=True);shutil.copy2(__file__,A/'executed-builder.py');shutil.copy2(REG,A/'executed-region.py')
def glb(p):
 raw=p.read_bytes();chunks=[];i=12
 while i<len(raw):n,k=struct.unpack_from('<II',raw,i);i+=8;chunks.append((k,raw[i:i+n]));i+=n
 return chunks,json.loads(chunks[0][1])
def sig():
 return {o.name:hashlib.sha256(json.dumps({'v':[list(v.co)for v in o.data.vertices],'f':[list(f.vertices)for f in o.data.polygons],'m':[m.name if m else None for m in o.data.materials]},sort_keys=True).encode()).hexdigest()for o in bpy.data.objects if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(SN));bpy.context.view_layer.update();before=sig();trans={o.name:list(sum((list(row)for row in o.matrix_local),[]))for o in bpy.data.objects};contract=runpy.run_path(str(REG))['apply']();after=sig();changed=sorted(n for n in before if before[n]!=after[n]);assert set(changed)==set(contract['changedMeshes']);assert all(trans[o.name]==list(sum((list(row)for row in o.matrix_local),[]))for o in bpy.data.objects)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(N),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(N));_,source=glb(SG);names={n['name']for n in source['nodes']};bpy.ops.object.select_all(action='DESELECT')
for name in names:o=bpy.data.objects[name];o.hide_set(False);o.hide_viewport=False;o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(G),export_format='GLB',use_selection=True,export_yup=True,export_apply=False,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT');chunks,doc=glb(G);mm={m['name']:m for m in source['materials']};doc['materials']=[mm[m['name']]for m in doc['materials']];j=json.dumps(doc,separators=(',',':')).encode();j+=b' '*((-len(j))%4);raw=bytearray(struct.pack('<4sII',b'glTF',2,0))
for k,c in chunks:d=j if k==0x4e4f534a else c;raw+=struct.pack('<II',len(d),k)+d
struct.pack_into('<I',raw,8,len(raw));G.write_bytes(raw)
scope={'changed':changed,'added':{},'removed':[],'changedNodes':[],'allowedTranslation':[],'allowedReparent':{},'allowedExtras':{n:['v38NeckFit01']for n in changed},'baselineNativeSHA256':sha(SN),'baselineGLBSHA256':sha(SG),'candidateNativeSHA256':sha(N),'candidateGLBSHA256':sha(G)};(A/'scope.json').write_text(json.dumps(scope,indent=2)+'\n');(A/'contract.json').write_text(json.dumps(contract,indent=2)+'\n');print('FROZEN',str(N),sha(N),str(G),sha(G),flush=True)
scene=bpy.context.scene
for o in bpy.data.objects:
 if o.type=='MESH':o.hide_render=o.get('silhouetteStudyHistoricalHidden')is True or o.get('authoringGuide')is True or 'builder'not in str(o.get('exteriorEras','maker,mechanic,builder')).split(',')
 elif o.type=='CURVE':o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';data=bpy.data.cameras.new('temporary neckfit camera');data.type='ORTHO';cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);scene.camera=cam;images=[]
for name,pos,target,scale in [('neck-profile',(-6,0,1.95),(0,-.35,1.41),.68),('full-bird-three-quarter',(-6,-3.5,2.75),(0,-.08,1.03),2.4),('full-bird-profile',(-7,0,2.75),(0,-.08,1.03),2.4),('full-bird-front',(0,-7,2.75),(0,-.08,1.03),2.4),('full-bird-rear',(0,7,2.75),(0,-.08,1.03),2.4)]:
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=scale;path=A/('candidate-'+name+'.png');scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);images.append({'path':str(path.relative_to(R)),'sha256':sha(path)});print('MEDIA',path,flush=True)
receipt={'status':'Frozen structural fit proposal; actual visual/finite screen pending','native':str(N.relative_to(R)),'nativeSHA256':sha(N),'glb':str(G.relative_to(R)),'glbSHA256':sha(G),'sourceNativeSHA256':sha(SN),'sourceGLBSHA256':sha(SG),'geometryChanged':changed,'allTransformsExact':True,'allFiveShellsExact':True,'materialsCopiedExactly':len(doc['materials']),'images':images,'contract':'contract.json','baselineImages':'neck-profile01/attempt02 candidate images, same cameras reused','limits':contract['limits']};(A/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('READY',flush=True)
