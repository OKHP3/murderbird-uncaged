from pathlib import Path
import bpy,bmesh,runpy,json,hashlib,math,shutil
from mathutils import Vector,Matrix
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=Path('/tmp/v29-wing-interface/coarse02');OUT.mkdir(exist_ok=False);BASE=ROOT/'assets/models/whole-character-v28/attempt-form02/murderbird-whole-character-v28.blend';SRC=ROOT/'scripts/regions/whole-character-v29-wing-interface.py';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(BASE)=='838a86b16766ddd4491c9f1cbe6a7aa0039c2b9e8514a04eb710d1e9b2f9bd9d'
for p,n in [(SRC,'executed-region.py'),(Path(__file__),'executed-builder.py'),(ROOT/'scripts/build-uncaged-alignment-v7.py','snapshot.py')]:shutil.copyfile(p,OUT/n)
h=runpy.run_path(str(OUT/'snapshot.py'));bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']();mats={m.name:h['material_signature'](m) for m in bpy.data.materials};result=runpy.run_path(str(OUT/'executed-region.py'))['apply']();after=h['scene_snapshot']();assert before['empties']==after['empties'];assert before['curves']==after['curves'];assert mats=={m.name:h['material_signature'](m) for m in bpy.data.materials}
solids=[]
for n in result['added']+result['changedMeshes']:
 o=bpy.data.objects[n];ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();bm=bmesh.new();bm.from_mesh(m);solids.append({'name':n,'finite':all(math.isfinite(c) for v in m.vertices for c in v.co),'closedEdges':all(e.is_manifold for e in bm.edges),'signedVolumeM3':bm.calc_volume(signed=True),'looseVertices':sum(not v.link_edges for v in bm.verts)});bm.free();ev.to_mesh_clear()
native=OUT/'murderbird-v29-wing-interface.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
receipt={'status':'V29 coarse02 receiving window render; no detailed clearance or engineering acceptance','baseSha256':sha(BASE),'sourceSha256':sha(OUT/'executed-region.py'),'nativeSha256':sha(native),'result':result,'finiteSolids':solids,'saveReopenExact':True,'materialsExact':True,'outsideExact':True,'views':[],'poseScope':'Actual named rigid owner Rx values from current controller wing limits; neutral body native proof, not full runtime execution.','validationGate':'No detailed strict crossing or attachment screen executed before appearance review.'};(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
STATES=[('folded',0,0,0,0),('guard',.065,-.24,.18,.38),('short-shove',.07,-.64,.18,.72)]
def configure(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();rest={n:bpy.data.objects[n].matrix_local.copy() for n in ['left-mantle','right-mantle','left-wing-shield','right-wing-shield']}
 for o in bpy.data.objects:
  if o.animation_data:o.animation_data_clear()
  if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
  elif o.type=='CURVE':o.hide_render=True
 scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';d=bpy.data.cameras.new('V29 nested interface comparison');d.type='ORTHO';cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam;return rest,scene,d,cam
for stage,path in [('after',native),('before',BASE)]:
 rest,scene,d,cam=configure(path)
 for state in STATES:
  for n,angle in zip(['left-mantle','right-mantle','left-wing-shield','right-wing-shield'],state[1:]):bpy.data.objects[n].matrix_local=rest[n]@Matrix.Rotation(angle,4,'X')
  bpy.context.view_layer.update()
  views=[('reference-angle',(-6,-3.5,2.45),(0,-.10,1.05),2.35),('right-wing-closeup',(-3,-1,1.35),(-.40,.09,1.15),1.06),('left-wing-closeup',(3,-1,1.35),(.40,.09,1.15),1.06)]
  if state[0]=='folded':views.extend([('front',(0,-6,1.05),(0,-.10,1.05),2.35),('side',(-6,0,1.05),(0,-.10,1.05),2.35)])
  for label,pos,target,scale in views:
   d.ortho_scale=scale;cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/f'{stage}-{state[0]}-{label}.png');bpy.ops.render.render(write_still=True);receipt['views'].append({'stage':stage,'pose':state[0],'wingAnglesRad':list(state[1:]),'view':label,'path':scene.render.filepath,'sha256':sha(Path(scene.render.filepath))});(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
  print('VIEWS_READY',stage,state[0],flush=True)
print('FROZEN',receipt['sourceSha256'],receipt['nativeSha256'], 'SOLIDS',len(solids),'WARNINGS',[s for s in solids if not(s['finite'] and s['closedEdges'] and s['signedVolumeM3']>0)],flush=True)
