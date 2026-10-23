"""Render exact appearance candidates in neutral and intended exhibition light."""
from pathlib import Path
import argparse,hashlib,json,math,sys
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
p=argparse.ArgumentParser();p.add_argument('--iteration',required=True);p.add_argument('--quick',action='store_true');p.add_argument('--samples',type=int,default=32);opts=p.parse_args(args)
source=ROOT/'assets/models/uncaged-appearance-v1/iterations'/opts.iteration/'murderbird-appearance.blend'
OUT=ROOT/'assets/audit/appearance-v1'/opts.iteration;OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene
for o in list(scene.objects):
    if o.type in {'CAMERA','LIGHT'}:bpy.data.objects.remove(o,do_unlink=True)
scene.render.engine='CYCLES';scene.cycles.samples=opts.samples;scene.cycles.use_denoising=True
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
    for device in prefs.devices:device.use=device.type=='METAL'
    scene.cycles.device='GPU' if any(d.use for d in prefs.devices) else 'CPU'
except Exception:scene.cycles.device='CPU'
scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.world.use_nodes=True;scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.18,.20,.23,1);scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.35
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.2
camdata=bpy.data.cameras.new('Appearance review camera');cam=bpy.data.objects.new('Appearance review camera',camdata);scene.collection.objects.link(cam);scene.camera=cam
def area(name,pos,power,size,color):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color
    o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=pos;o.rotation_euler=(Vector((0,0,1.1))-o.location).to_track_quat('-Z','Y').to_euler();return o
key=area('Broad key',(-3,-4.5,5),700,4,(1,.91,.78));fill=area('Cool fill',(3,-1,3.3),500,3,(.70,.84,1));rim=area('Back edge',(.6,3,3.5),850,2,(1,.78,.46))
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.018));floor=bpy.context.object;floor.name='Review floor';floor['reviewOnly']=True
floor_mat=bpy.data.materials.new('Review floor');floor_mat.diffuse_color=(.12,.135,.14,1);floor_mat.use_nodes=True;bs=floor_mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.12,.135,.14,1);bs.inputs['Roughness'].default_value=.8;floor.data.materials.append(floor_mat)
records=[]
def era(value):
    for o in scene.objects:
        if o.type=='MESH' and not o.get('reviewOnly'):
            o.hide_set(False);o.hide_render=value not in o.get('exteriorEras','maker,mechanic,builder').split(',')
def render(name,pos,target,scale=2.25):
    cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=scale
    scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
    records.append({'path':str(Path(scene.render.filepath).relative_to(ROOT)),'camera':list(pos),'target':list(target),'scale':scale,'sha256':hashlib.sha256(Path(scene.render.filepath).read_bytes()).hexdigest()})
era('builder')
render('advanced-head',(-3.8,-6,2.0),(0,-.30,1.72),.77)
render('advanced-three-quarter',(-4.7,-6.5,2.30),(0,-.1,1.0),2.23)
if not opts.quick:
    render('advanced-side',(-6,0,1.2),(0,-.1,1.0),2.23)
    render('advanced-front',(0,-6,1.2),(0,-.1,1.0),2.23)
    render('advanced-rear',(0,6,1.4),(0,.05,1.0),2.23)
    render('advanced-feet',(-3,-5,.8),(0,-.1,.32),.86)
    for e in ['maker','mechanic']:
        era(e);render(e+'-three-quarter',(-4.7,-6.5,2.30),(0,-.1,1.0),2.23);render(e+'-head',(-3.8,-6,2.0),(0,-.30,1.72),.77)
(OUT/'authoring-views.json').write_text(json.dumps({'source':str(source.relative_to(ROOT)),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'engine':'Cycles','device':scene.cycles.device,'samples':opts.samples,'status':'rendered evidence; likeness not automatically accepted','views':records},indent=2)+'\n')
