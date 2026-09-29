"""Compose one frozen neck proposal on the exact V22 frame04; no runtime export."""
from pathlib import Path
import argparse,hashlib,json,math,runpy,shutil,sys
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'assets/models/whole-character-v22/attempt-frame04/murderbird-whole-character-v22.blend';BASE_SHA='b3ac4677d2e76a0e08544323306c07f2ed7e61cd381d274a944d8e5b87031d1f'
p=argparse.ArgumentParser();p.add_argument('--attempt',required=True);p.add_argument('--module-sha256',required=True);p.add_argument('--cassette',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);assert a.attempt.replace('-','').isalnum()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def art(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}
source=ROOT/('scripts/regions/whole-character-v22-neck-cassette.py' if a.cassette else 'scripts/regions/whole-character-v22-neck-guards.py');AUDIT=ROOT/f'assets/audit/whole-character-v22/attempt-{a.attempt}';OUT=ROOT/f'assets/models/whole-character-v22/attempt-{a.attempt}';assert sha(BASE)==BASE_SHA and sha(source)==a.module_sha256 and not AUDIT.exists() and not OUT.exists();AUDIT.mkdir(parents=True);OUT.mkdir(parents=True);shutil.copyfile(__file__,AUDIT/'executed-composer.py');shutil.copyfile(source,AUDIT/'executed-region.py')
h=runpy.run_path(str(ROOT/'scripts/build-uncaged-alignment-v7.py'));bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']();materials={m.name:h['material_signature'](m) for m in bpy.data.materials};protected={o.name for o in bpy.data.objects if o.type=='MESH' and o.get('surfaceRole') in ('frame','bearing','bearing-frame')};region=runpy.run_path(str(AUDIT/'executed-region.py'));protected|={o.name for o in bpy.data.objects['head'].children_recursive if o.type=='MESH' and o.name!='V4 cranial inner shell'};result=region['apply']();bpy.context.view_layer.update();after=h['scene_snapshot']();assert all(after['empties'].get(n)==v for n,v in before['empties'].items());assert set(after['empties'])-set(before['empties'])==({'cervical-root-cover','cervical-skull-cover'} if a.cassette else set());assert before['curves']==after['curves'];assert materials=={m.name:h['material_signature'](m) for m in bpy.data.materials}
allowed={'neck','cervical-upper','cervical-joint-cover','body','breastplate'}|({'head','cervical-root-cover','cervical-skull-cover'} if a.cassette else set());altered=[]
for n in set(before['meshes'])|set(after['meshes']):
 if before['meshes'].get(n)!=after['meshes'].get(n):
  altered.append(n);assert n not in protected,('Protected frame/bearing/head-exterior changed',n)
  if a.cassette and n in before['meshes']:assert n in region['OLD']+region['BOUNDARIES'],('Outside named cassette scope',n)
  for r in [before['meshes'].get(n),after['meshes'].get(n)]:
   if r:assert r['parent'] in allowed,(n,r['parent'])
finite=[];deps=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
 if o.type=='MESH':
  e=o.evaluated_get(deps);m=e.to_mesh();assert all(math.isfinite(c) for v in m.vertices for c in v.co),o.name;finite.append(o.name);e.to_mesh_clear()
native=OUT/'murderbird-whole-character-v22.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
receipt={'status':'neck construction proposal; artistic and full motion acceptance unproven','base':art(BASE),'native':art(native),'module':art(AUDIT/'executed-region.py'),'composer':art(AUDIT/'executed-composer.py'),'construction':result,'alteredMeshes':sorted(altered),'checks':{'namedRestPivotsExact':len(before['empties']),'newCoverOwners':sorted(set(after['empties'])-set(before['empties'])),'protectedFrameBearingMeshesExact':len(protected),'materialsExact':True,'finiteEvaluatedMeshes':len(finite),'saveReopenExact':True},'limits':['V22 runtime sockets remain inactive; no runtime derivative or motion envelope acceptance.','Neutral pose illustrations use discrete joint angles, not physical simulation.'],'views':[]};receipt_path=AUDIT/'receipt.json'
views=[('reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5),('front',(0,-7,1.65),(0,-.08,1.02),2.5),('side',(-7,0,1.35),(0,-.08,1.02),2.5),('rear',(0,7,1.65),(0,-.08,1.02),2.5),('neck',(-6,-3.5,2.45),(0,-.27,1.48),1.3)]
for label,path in [('after',native),('before',BASE)]:
 bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene
 for o in bpy.data.objects:
  if o.animation_data:o.animation_data_clear()
  if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
  elif o.type=='CURVE':o.hide_render=True
 scene.render.engine='BLENDER_WORKBENCH';sh=scene.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='SINGLE';sh.single_color=(.56,.58,.60);sh.show_shadows=False;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';data=bpy.data.cameras.new('V22 temporary neutral camera');data.type='ORTHO';camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera);scene.camera=camera
 for name,pos,target,scale in views:
  camera.location=pos;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=scale;scene.render.filepath=str(AUDIT/f'{label}-{name}.png');bpy.ops.render.render(write_still=True);receipt['views'].append({**art(Path(scene.render.filepath)),'camera':{'position':pos,'target':target,'scale':scale},'lighting':'neutral Workbench no cast shadows'})
 if label=='after' and not a.cassette:
  rests={n:bpy.data.objects[n].rotation_euler.copy() for n in ('neck','cervical-upper','cervical-joint-cover','head')}
  for name,pitch in [('dip',.65),('extension',-.65)]:
   for n,fraction in [('neck',.35),('cervical-upper',.65),('cervical-joint-cover',.325),('head',-1)]:bpy.data.objects[n].rotation_euler=rests[n];bpy.data.objects[n].rotation_euler.x+=fraction*pitch
   bpy.context.view_layer.update();expected={n:bpy.data.objects[n].matrix_world.copy() for n in rests};camera.location=(-7,0,1.65);camera.rotation_euler=(Vector((0,-.27,1.48))-camera.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=1.55;scene.render.filepath=str(AUDIT/f'native-neck-{name}.png');bpy.ops.render.render(write_still=True);err=max(abs(bpy.data.objects[n].matrix_world[r][c]-mat[r][c]) for n,mat in expected.items() for r in range(4) for c in range(4));assert err<2e-6;receipt['views'].append({**art(Path(scene.render.filepath)),'totalPitch':pitch,'postRenderMatrixError':err,'status':'discrete native joint illustration, not full movement clearance'})
 receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
assert sha(BASE)==BASE_SHA and sha(native)==receipt['native']['sha256'];print(json.dumps({'native':receipt['native'],'checks':receipt['checks'],'views':len(receipt['views'])}))
