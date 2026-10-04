from pathlib import Path
import bpy, json, importlib.util, hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
INPUT=ROOT/'assets/models/cinematic-cg-milestone02b/murderbird-cg-2b-builder.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def module(path):
    spec=importlib.util.spec_from_file_location('m',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
bpy.ops.wm.open_mainfile(filepath=str(INPUT));s=bpy.context.scene
inputsha=sha(INPUT)
def body():
    return {o.name:dict(transform=[list(r) for r in o.matrix_world],visible=not o.hide_render,vertices=len(o.data.vertices),materials=[m.name for m in o.data.materials]) for o in s.objects if o.type=='MESH' and o.get('cg1cRegion') not in ('head','neck')}
oldbody=body();oldanchors={o.name:[list(r) for r in o.matrix_world] for o in s.objects if o.type=='EMPTY'}
for o in s.objects:
    if o.get('authoringGuide'):o.hide_render=True
profiles=module(ROOT/'scripts/cinematic-cg-2b-lighting.py').profiles();profile=profiles['neutral']
for o in list(s.objects):
    if o.type=='LIGHT':bpy.data.objects.remove(o,do_unlink=True)
for i,a in enumerate(profile['areas']):
    d=bpy.data.lights.new('head01 matched neutral '+str(i),'AREA');d.energy=a['power'];d.color=a['color'];d.size=a['size']
    o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=a['position'];o.rotation_euler=(Vector(a['target'])-o.location).to_track_quat('-Z','Y').to_euler()
bg=s.world.node_tree.nodes.get('Background');bg.inputs[0].default_value=(*profile['world_color'],1);bg.inputs[1].default_value=profile['world_strength']
s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True;s.cycles.device='CPU'
s.render.image_settings.file_format='PNG';s.render.resolution_percentage=100
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
cam=s.camera;cam.data.type='ORTHO';reg=json.loads((ROOT/'assets/audit/cinematic-cg-milestone02b/construction01/receipt.json').read_text())['cameras']['canon-neutral']
cameras={}
def render(prefix,kind):
    if kind=='whole':
        cam.location=reg['location'];cam.rotation_euler=reg['rotation_euler'];cam.data.ortho_scale=reg['ortho_scale'];cam.data.shift_x=reg['shift_x'];cam.data.shift_y=reg['shift_y'];s.render.resolution_x=850;s.render.resolution_y=566
    else:
        cam.location=(-6,-2.14,2.15);cam.rotation_euler=(Vector((0,-.22,1.60))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.81;cam.data.shift_x=cam.data.shift_y=0;s.render.resolution_x=800;s.render.resolution_y=800
    cameras[kind]=dict(location=list(cam.location),rotation_euler=list(cam.rotation_euler),ortho_scale=cam.data.ortho_scale,shift_x=cam.data.shift_x,shift_y=cam.data.shift_y,resolution=[s.render.resolution_x,s.render.resolution_y],lighting=profile,estimate=True)
    s.render.filepath=str(OUT/(prefix+'-'+kind+'.png'));bpy.ops.render.render(write_still=True)
render('before','head');render('before','whole')
receipt=module(ROOT/'scripts/cg-supervised-head-neck.py').apply(s,ROOT,'builder')
assert oldbody==body(),'Body changed'
assert all(oldanchors[n]==[list(r) for r in s.objects[n].matrix_world] for n in oldanchors),'Anchor changed'
render('after','head');render('after','whole')
receipt.update(input=str(INPUT.relative_to(ROOT)),inputSha256=inputsha,unchangedBodyMeshes=len(oldbody),allOriginalAnchorsPreserved=True,cameras=cameras,sourceHashes={p:sha(ROOT/p) for p in ['assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg','context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png']})
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'murderbird-supervised-head01.blend'))
assert sha(INPUT)==inputsha
receipt['renderHashes']={p.name:sha(p) for p in OUT.glob('*.png')};receipt['nativeSha256']=sha(OUT/'murderbird-supervised-head01.blend')
(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('HEAD01_COMPLETE')
