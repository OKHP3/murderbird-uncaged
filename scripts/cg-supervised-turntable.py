"""Render-only supplement from an immutable packed native; no asset writes."""
import argparse,datetime,hashlib,importlib.util,json,math,sys
from pathlib import Path
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
p=argparse.ArgumentParser();p.add_argument('--native',required=True);p.add_argument('--out',required=True);p.add_argument('--samples',type=int,default=32);p.add_argument('--resolution',type=int,default=1280);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
r=Path(__file__).resolve().parents[1];source=r/a.native;out=r/a.out;out.mkdir(parents=True,exist_ok=True)
if any(out.glob('*.png')):raise RuntimeError('Write-once rendered supplement; choose another output')
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();pin=sha(source)
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;cam=s.camera
sp=importlib.util.spec_from_file_location('supervised_light',r/'scripts/cg-supervised-lighting02.py');lighting=importlib.util.module_from_spec(sp);sp.loader.exec_module(lighting);profiles=lighting.profiles()
lights=[o for o in s.objects if o.type=='LIGHT'];assert len(lights)==3
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=a.samples;s.cycles.use_denoising=True;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA'
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0;s.view_settings.gamma=1
receipt={'native':a.native,'native_sha256':pin,'scope':'Render-only supplement; immutable packed native; estimated comparison camera; owner acceptance not claimed','cameras':{},'render_settings':{'engine':'CYCLES','samples':a.samples,'denoise':True,'view_transform':'AgX','look':'AgX - Medium High Contrast','exposure':0,'gamma':1}}
def render(name,pos,target,scale=3.2,profile='neutral',projection='ORTHO',resolution=None):
 rig=profiles[profile];b=s.world.node_tree.nodes['Background'];b.inputs[0].default_value=(*rig['world_color'][:3],1);b.inputs[1].default_value=rig['world_strength']
 for obj,spec in zip(lights,rig['areas']):
  obj.location=spec['position'];obj.rotation_euler=(Vector(spec['target'])-obj.location).to_track_quat('-Z','Y').to_euler();obj.data.energy=spec['power'];obj.data.color=spec['color'];obj.data.size=spec['size']
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type=projection;cam.data.ortho_scale=scale;cam.data.shift_x=cam.data.shift_y=0
 w,h=resolution or (a.resolution,round(a.resolution*853/1280));s.render.resolution_x,s.render.resolution_y=w,h;bpy.context.view_layer.update()
 bounds=None
 if name.startswith(('neutral-','workshop-')) or name=='hero':
  pts=[world_to_camera_view(s,cam,o.matrix_world@Vector(c)) for o in s.objects if o.type=='MESH' and not o.hide_render and not o.get('authoringGuide') for c in o.bound_box];bounds=[min(v.x for v in pts),min(v.y for v in pts),max(v.x for v in pts),max(v.y for v in pts)];assert bounds[0]>=0 and bounds[1]>=0 and bounds[2]<=1 and bounds[3]<=1,(name,bounds)
 s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 receipt['cameras'][name]={'location':list(cam.location),'rotation_euler':list(cam.rotation_euler),'projection':projection,'ortho_scale':scale,'shift':[0,0],'resolution':[w,h],'lighting':profile,'bounds':bounds,'areas':rig['areas'],'world_color':rig['world_color'],'world_strength':rig['world_strength']}
for profile in ['neutral','workshop']:
 for i in range(8):
  angle=math.radians(i*45);center=Vector((0,-.04,.97));pos=center+Vector((6*math.sin(angle),-6*math.cos(angle),1.02));render(f'{profile}-{i*45:03d}',pos,center,profile=profile)
render('body-detail',(-6,-2.4,1.50),(0,-.04,1.13),1.28,resolution=(a.resolution,a.resolution))
render('feet-detail',(-2.8,-3.6,1.02),(0,-.03,.14),.92,resolution=(a.resolution,a.resolution))
render('hero',(-3,-3.9,1.32),(0,-.04,.99),profile='cinematic',projection='PERSP',resolution=(int(a.resolution*.75),a.resolution))
assert sha(source)==pin;receipt['native_preserved']=True;receipt['created_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();receipt['image_hashes']={f.name:sha(f) for f in out.glob('*.png')};(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('SUPERVISED_TURNTABLE_COMPLETE',out)
