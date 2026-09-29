from pathlib import Path
import bpy,bmesh,json,hashlib,runpy,shutil,math
from mathutils import Vector
R=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
A=R/'assets/audit/whole-character-v34/regional-studies/leg-mass/coarse04-repair01';O=R/'assets/models/whole-character-v34/regional-studies/leg-mass/coarse04-repair01'
assert not A.exists() and not O.exists();A.mkdir(parents=True);O.mkdir(parents=True)
S=R/'scripts/regions/whole-character-v34-leg-mass.py';B=R/'assets/models/whole-character-v33/attempt-form06/murderbird-whole-character-v33.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def art(p):return {'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)}
assert sha(B)=='5fdfe66693db848fcf624b28484c3eaba220a8d7f389248390a4f21a571d108d'
shutil.copyfile(__file__,A/'executed-build.py');shutil.copyfile(S,A/'executed-leg-mass.py');shutil.copyfile(R/'scripts/build-uncaged-alignment-v7.py',A/'executed-snapshot-helper.py')
h=runpy.run_path(str(A/'executed-snapshot-helper.py'))
bpy.ops.wm.open_mainfile(filepath=str(B));bpy.context.view_layer.update();before=h['scene_snapshot']();mats={m.name:h['material_signature'](m) for m in bpy.data.materials}
result=runpy.run_path(str(A/'executed-leg-mass.py'))['apply']();after=h['scene_snapshot']();changed=set(result['changedMeshes'])
assert before['empties']==after['empties'];assert set(before['meshes'])==set(after['meshes'])
for n,r in before['meshes'].items():
 if n not in changed:assert after['meshes'][n]==r,n
 else:
  now=after['meshes'][n]
  for k in ('parent','matrix','modifiers','props','visibility'):assert now[k]==r[k],(n,k)
assert mats=={m.name:h['material_signature'](m) for m in bpy.data.materials}
vol=[]
for n in changed:
 o=bpy.data.objects[n];bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges),n
 v=bm.calc_volume(signed=True);assert v>0,n;bm.free();vol.append({'name':n,'volumeM3':v})
N=O/'murderbird-v34-leg-mass.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(N),check_existing=False)
bpy.ops.wm.open_mainfile(filepath=str(N));assert h['scene_snapshot']()==after
foot=[n for n,r in before['meshes'].items() if 'foot' in (r['parent'] or '') or 'toe' in (r['parent'] or '') or 'digit' in (r['parent'] or '')]
receipt={'status':'One coarse passive leg mass proposal; not movement, likeness or engineering acceptance','base':art(B),'native':art(N),'module':art(S),'executedModule':art(A/'executed-leg-mass.py'),'result':result,'checks':{'changedFiniteClosedPositiveSolids':len(vol),'unchangedNamedRestNodes':len(before['empties']),'outsideChangedMeshesExact':len(before['meshes'])-len(changed),'footToeDigitMeshesExact':len([n for n in foot if n not in changed]),'changedFootOwnedMeshes':result['changedFootOwnedMeshes'],'objectTransformsMetadataMaterialsExact':True,'saveReopenExact':True},'volumes':vol,'views':[],'fitWarning':'Members have broader midspans near existing joint envelopes. Actual articulated clearance has not been screened; unchanged journals do not establish receiver clearance under movement.'}
(A/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
views=[('reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5),('front',(0,-7,1.65),(0,-.08,1.02),2.5),('side',(-7,0,1.35),(0,-.08,1.02),2.5),('leg-close',(-3,-4,1.15),(-.23,-.015,.48),.82),('leg-side',(-7,0,.67),(-.27,-.015,.48),.82)]
(A/'camera-contract.json').write_text(json.dumps({'views':views,'engine':'BLENDER_WORKBENCH','light':'paint.sl','singleColor':[.56,.58,.60],'size':[900,900]},indent=2)+'\n')
for phase,path in (('before',B),('after',N)):
 bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene
 for o in bpy.data.objects:
  if o.animation_data:o.animation_data_clear()
  if o.get('authoringGuide') is True:o.hide_render=True
  elif o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
  elif o.type=='CURVE':o.hide_render=True
 scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14)
 scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 d=bpy.data.cameras.new('V34 temporary matched camera');d.type='ORTHO';c=bpy.data.objects.new(d.name,d);scene.collection.objects.link(c);scene.camera=c
 for name,pos,target,scale in views:
  c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale
  path=A/f'{phase}-{name}.png';scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);receipt['views'].append(art(path))
  (A/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
assert sha(S)==sha(A/'executed-leg-mass.py');print(json.dumps({'native':art(N),'module':art(S),'checks':receipt['checks']}))
