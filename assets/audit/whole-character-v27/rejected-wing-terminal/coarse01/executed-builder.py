from pathlib import Path
import bpy,bmesh,runpy,json,hashlib,math,shutil
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=Path('/tmp/v27-wing-terminal/coarse01');OUT.mkdir(exist_ok=False);BASE=ROOT/'assets/models/whole-character-v26/attempt-form01/murderbird-whole-character-v26.blend';SRC=ROOT/'scripts/regions/whole-character-v27-wing-terminal.py';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(BASE)=='f897b3310af0c9d8b5e079484bcd9b8863e35c12e6b2be26601ad56700b65564'
for p,n in [(SRC,'executed-region.py'),(Path(__file__),'executed-builder.py'),(ROOT/'scripts/build-uncaged-alignment-v7.py','snapshot.py'),(ROOT/'assets/audit/whole-character-v25/rejected-neck-source-screen/baseline.py','triangle-screen-helper.py')]:shutil.copyfile(p,OUT/n)
h=runpy.run_path(str(OUT/'snapshot.py'));tools=runpy.run_path(str(OUT/'triangle-screen-helper.py'),run_name='tooling');bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']();mats={m.name:h['material_signature'](m) for m in bpy.data.materials};mod=runpy.run_path(str(OUT/'executed-region.py'));owned=set(sum((mod['names'](label) for label in ['left','right']),[]))
def evaluated(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@p.co for p in m.vertices];t=[tuple(p.vertices) for p in m.loop_triangles];ev.to_mesh_clear();return v,t
root_samples={}
for n in owned:
 o=bpy.data.objects[n];points=[o.matrix_world@v.co for v in o.data.vertices];cut=max(p.z for p in points)-.008;root_samples[n]=[i for i,p in enumerate(points) if p.z>=cut]
def attachments():
 out=[]
 for label in ['left','right']:
  back=bpy.data.objects[f'{label} profiled mantle backing v4 {label}-wing-shield'];v,t=evaluated(back);bv=BVHTree.FromPolygons(v,t,all_triangles=True)
  for n in mod['names'](label):
   if n==back.name:continue
   o=bpy.data.objects[n];points=[o.matrix_world@o.data.vertices[i].co for i in root_samples[n]];dist=[bv.find_nearest(p)[3] for p in points];out.append({'name':n,'rootSamples':len(points),'minimumRootToLinerM':min(dist),'maximumRootToLinerM':max(dist),'meanRootToLinerM':sum(dist)/len(dist)})
 return out
beforeattach=attachments();result=mod['apply']();after=h['scene_snapshot']();assert before['empties']==after['empties'];assert before['curves']==after['curves'];assert all(before['meshes'][n]==after['meshes'][n] for n in before['meshes'] if n not in owned);assert mats=={m.name:h['material_signature'](m) for m in bpy.data.materials};afterattach=attachments();solids=[];protected_receivers=[]
for n in owned:
 o=bpy.data.objects[n];ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();bm=bmesh.new();bm.from_mesh(m);solids.append({'name':n,'finite':all(math.isfinite(c) for v in m.vertices for c in v.co),'closed':all(e.is_manifold for e in bm.edges),'signedVolumeM3':bm.calc_volume(signed=True)});bm.free();ev.to_mesh_clear()
assert all(r['finite'] and r['closed'] and r['signedVolumeM3']>0 for r in solids),[r for r in solids if not(r['finite'] and r['closed'] and r['signedVolumeM3']>0)]
native=OUT/'murderbird-v27-wing-terminal.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
receipt={'status':'one coarse wing terminal review proposal; stop for root gate','baseSha256':sha(BASE),'sourceSha256':sha(SRC),'nativeSha256':sha(native),'result':result,'finiteSolids':solids,'saveReopenExact':True,'materialsExact':True,'outsideExact':True,'beforeAttachments':beforeattach,'afterAttachments':afterattach,'attachmentDeltas':[{'name':a['name'],'meanGapDeltaM':b['meanRootToLinerM']-a['meanRootToLinerM'],'maxGapDeltaM':b['maximumRootToLinerM']-a['maximumRootToLinerM']} for a,b in zip(beforeattach,afterattach)],'poses':{},'views':[]}
STATES=[('folded',0,0,0,0),('maker-wing',0,-.38,0,.16),('guard',.065,-.24,.18,.38),('short-shove',.07,-.64,.18,.72)]
def configure(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();rest={n:bpy.data.objects[n].matrix_local.copy() for n in ['left-mantle','right-mantle','left-wing-shield','right-wing-shield']}
 for o in bpy.data.objects:
  if o.animation_data:o.animation_data_clear()
  if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
  elif o.type=='CURVE':o.hide_render=True
 scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';d=bpy.data.cameras.new('V27 terminal comparison camera');d.type='ORTHO';cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam;return rest,scene,d,cam
def pose(state,rest):
 for n,angle in zip(['left-mantle','right-mantle','left-wing-shield','right-wing-shield'],state[1:]):bpy.data.objects[n].matrix_local=rest[n]@Matrix.Rotation(angle,4,'X')
 bpy.context.view_layer.update()
def screen(state,rest):
 pose(state,rest);items=[]
 for o in bpy.data.objects:
  if o.type!='MESH' or not o.parent:continue
  if o.name not in owned and o.parent.name not in ['left-mantle','right-mantle','body','breastplate','left-wing-shield','right-wing-shield']:continue
  if 'builder' not in o.get('exteriorEras','maker,mechanic,builder').split(','):continue
  v,t=evaluated(o);items.append((o.name,o.parent.name,tools['bounds'](v),v,t,BVHTree.FromPolygons(v,t,all_triangles=True)))
 pairs=[]
 for i,a in enumerate(items):
  for b in items[i+1:]:
   if a[1]==b[1] or not(a[0] in owned or b[0] in owned) or any(a[2][1][k]<b[2][0][k] or b[2][1][k]<a[2][0][k] for k in range(3)):continue
   hits=0
   for x,y in a[5].overlap(b[5]):
    A=[a[3][n] for n in a[4][x]];B=[b[3][n] for n in b[4][y]]
    if tools['straddle'](A,B) and tools['straddle'](B,A):hits+=1
   if hits:pairs.append({'a':a[0],'b':b[0],'owners':[a[1],b[1]],'strictTriangleWitnesses':hits})
 return {'pose':state[0],'wingAnglesRad':list(state[1:]),'strictPairCount':len(pairs),'pairs':pairs}
for stage,path in [('before',BASE),('after',native)]:
 rest,scene,d,cam=configure(path)
 for state in STATES:
  pose(state,rest)
  if state[0] in ['folded','short-shove']:
   for label,pos,target,scale in [('front',(0,-6,1.05),(0,-.10,1.05),2.35),('side',(-6,0,1.05),(0,-.10,1.05),2.35),('reference-angle',(-6,-3.5,2.45),(0,-.10,1.05),2.35),('wing-closeup',(-3,-1,1.35),(-.42,.13,1.02),.90)]:
    d.ortho_scale=scale;cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/f'{stage}-{state[0]}-{label}.png');bpy.ops.render.render(write_still=True);receipt['views'].append({'stage':stage,'pose':state[0],'view':label,'path':scene.render.filepath,'sha256':sha(Path(scene.render.filepath))})
  (OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print('VIEWS_READY',stage,flush=True)
 # Bounded sampled diagnostic, not continuous collision proof.
 states=STATES+[(f'shove-fraction-{i/10:.1f}',.07*i/10,-.64*i/10,.18*i/10,.72*i/10) for i in range(1,10)]
 receipt['poses'][stage]=[screen(state,rest) for state in states];(OUT/f'{stage}-strict-screen.json').write_text(json.dumps(receipt['poses'][stage],indent=2)+'\n');(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('SCREEN_READY',stage,[(r['pose'],r['strictPairCount']) for r in receipt['poses'][stage]],flush=True)
print(json.dumps({'source':sha(SRC),'native':sha(native),'solids':len(solids),'attachments':receipt['attachmentDeltas']}),flush=True)
