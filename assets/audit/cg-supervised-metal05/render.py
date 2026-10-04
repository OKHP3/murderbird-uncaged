import bpy,importlib.util,json,hashlib,sys,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3];INP=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');OUT=Path(__file__).resolve().parent/('attempt02' if '--attempt02' in sys.argv else 'attempt01');OUT.mkdir(parents=True,exist_ok=True)
def mod(name):
 p=INP/'scripts'/('cg-supervised-'+name+'.py') if name!='metal05' else ROOT/'scripts/cg-supervised-metal05.py'
 sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
native=INP/'assets/audit/cg-supervised-body05/attempt02/murderbird-body05.blend';assert sha(native)=='2b093217f3c76abf37b60041248ceaf99a2c85e716628984f04f5555949e8bfe'
refs={'fullbird':('assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg','645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114'),'maker':('assets/img/library/murderbird-unified-maker-clean-candidate-2026-09-06.png','93966eb269ae9f8d8d00e05e913cbb23f7656204e6f3fdf7fd26e8a39ca0cbb9'),'mechanic':('assets/img/library/murderbird-unified-mechanic-candidate-2026-09-06.png','0bd7c79510be9eeef024f8861a7576b777a7f5de5710523e8d2ab039d03c65f9'),'builder':('assets/img/library/murderbird-unified-heart-candidate-2026-09-06.png','9430f91e3cd3fc8223297720a0f57ec1c46e9c8245cfba91495e9c362029fea9'),'julyheadonly':('context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png','47658dba6496f2c8594a40ad412a8bfaa087939e90044d1597329a27ca68d4e9')}
for rel,h in refs.values():assert sha(INP/rel)==h,rel
bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene
mod('surface03').apply(s,OUT/'baseline-surface','builder',ROOT);mod('finish04').apply(s,OUT/'baseline-finish','builder',INP)
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=6;s.cycles.use_denoising=True;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.film_transparent=True
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0;s.view_settings.gamma=1
for o in list(s.objects):
 if o.type=='LIGHT':o.hide_render=True
lighting=mod('lighting02').profiles();rig=[]
for i in range(3):
 d=bpy.data.lights.new('Metal05 diagnostic area '+str(i),'AREA');o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);rig.append(o)
world=bpy.data.worlds.new('Metal05 diagnostic world');world.use_nodes=True;s.world=world
q=mod('camera04').camera(INP);cam=s.camera
clay=bpy.data.materials.new('Metal05 fixed clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.23,.23,.23,1);bs.inputs['Roughness'].default_value=.64
cameras={};lights={}
def render(name,profile='neutral',view='whole',claypass=False):
 cfg=lighting[profile];world.node_tree.nodes['Background'].inputs[0].default_value=(*cfg['world_color'],1);world.node_tree.nodes['Background'].inputs[1].default_value=cfg['world_strength']
 for o,a in zip(rig,cfg['areas']):
  o.location=a['position'];o.rotation_euler=(Vector(a['target'])-o.location).to_track_quat('-Z','Y').to_euler();o.data.energy=a['power'];o.data.color=a['color'];o.data.size=a['size']
 cam.location=q['location'];cam.rotation_euler=q['rotation_euler'];cam.data.type=q['projection'];cam.data.ortho_scale=q['ortho_scale'];cam.data.shift_x,cam.data.shift_y=q['shift'];cam.data.lens=q['lens_mm']
 s.render.resolution_x=768;s.render.resolution_y=512
 if view!='whole':
  target={'armor':(0,-.05,1.21),'leg':(0,-.025,.42)}[view];cam.location=(-6,-2.4,1.8 if view=='armor' else 1.05);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.91 if view=='armor' else 1.20;cam.data.shift_x=cam.data.shift_y=0
 s.view_layers[0].material_override=clay if claypass else None
 cameras[name]={'location':list(cam.location),'rotation':list(cam.rotation_euler),'scale':cam.data.ortho_scale,'shift':[cam.data.shift_x,cam.data.shift_y],'resolution':[768,512],'clay':claypass};lights[name]=cfg
 s.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True);print('METAL05_RENDERED',name,flush=True)
render('before-whole-neutral');receipt=mod('metal05').apply(s,OUT,'builder',INP);render('after-whole-neutral');print('FIRST_VISIBLE_COMPLETE',flush=True)
# Restore only old slot references for remaining matched baselines.
current={o.name:list(o.data.materials) for o in s.objects if o.type=='MESH'}
# Before maps are retained in material datablocks. Map each copy back by family,
# preserving routing rather than replacing slots wholesale.
baseline={}
for o in s.objects:
 if o.type!='MESH':continue
 baseline[o.name]=[]
 for m in o.data.materials:
  if m and m.get('cgMetal05Family'):
   fam=m['cgMetal05Family'];prior=next(x for x in bpy.data.materials if x.get('cgFinish04Family')==fam and not x.get('cgMetal05Family'));baseline[o.name].append(prior)
  else:baseline[o.name].append(m)
def assign(rows):
 for name,mats in rows.items():
  for i,m in enumerate(mats):s.objects[name].data.materials[i]=m
for stage,rows in [('before',baseline),('after',current)]:
 assign(rows)
 for profile in ('neutral','cinematic'):
  for view in ('whole','armor','leg'):
   if profile=='neutral' and view=='whole':continue
   render(f'{stage}-{view}-{profile}',profile,view)
 render(stage+'-whole-clay','neutral','whole',True)
assign(current);s.view_layers[0].material_override=None
(OUT/'render-receipt.json').write_text(json.dumps({'input_path':str(native.relative_to(INP)),'input_sha256':sha(native),'input_unchanged':sha(native)=='2b093217f3c76abf37b60041248ceaf99a2c85e716628984f04f5555949e8bfe','references':refs,'goal_revision':'251f2f0243181e97140179c2aff6eb057e165438','cameras':cameras,'lighting':lights,'view_transform':'AgX','look':'AgX - Medium High Contrast','samples':6,'native_saved':False,'full_geometry_export':False,'images':{p.name:sha(p) for p in OUT.glob('*.png')}},indent=2)+'\n')
print('METAL05_DIAGNOSTIC_COMPLETE',flush=True)
