"""Read-only role-contrast views: clarify frame/armor, not a finish proposal."""
from pathlib import Path
import argparse,hashlib,json,shutil,sys
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--native',required=True);p.add_argument('--sha256',required=True);p.add_argument('--out',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
native=ROOT/a.native;out=ROOT/a.out;assert sha(native)==a.sha256 and not out.exists();out.mkdir(parents=True);shutil.copyfile(__file__,out/'executed-renderer.py');bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene
colors={'structure':(.085,.095,.105,1),'bearing':(.22,.24,.26,1),'armor':(.40,.42,.44,1),'optic':(.06,.07,.08,1)};inventory={}
for obj in bpy.data.objects:
 if obj.animation_data:obj.animation_data_clear()
 if obj.type=='CURVE':obj.hide_render=True
 if obj.type!='MESH':continue
 obj.hide_render='builder' not in obj.get('exteriorEras','maker,mechanic,builder').split(',');role=obj.get('surfaceRole','')
 category='optic' if 'optic' in role else 'bearing' if 'bearing' in role else 'structure' if role in ('frame','inner','recess','edge') else 'armor';obj.color=colors[category];inventory[obj.name]={'sourceRole':role,'displayCategory':category}
scene.render.engine='BLENDER_WORKBENCH';sh=scene.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='OBJECT';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.curvature_ridge_factor=1.3;sh.curvature_valley_factor=1.8;sh.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
data=bpy.data.cameras.new('Read-only role contrast camera');data.type='ORTHO';camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera);scene.camera=camera
views=[]
for name,pos,target,scale in [('reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5),('front',(0,-7,1.65),(0,-.08,1.02),2.5),('side',(-7,0,1.35),(0,-.08,1.02),2.5),('neck',(-6,-3.5,2.45),(0,-.27,1.48),1.30)]:
 camera.location=pos;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=scale;scene.render.filepath=str(out/f'{name}.png');bpy.ops.render.render(write_still=True);views.append({'file':str(Path(scene.render.filepath).relative_to(ROOT)),'sha256':sha(scene.render.filepath),'camera':{'position':pos,'target':target,'scale':scale}})
assert sha(native)==a.sha256
(out/'manifest.json').write_text(json.dumps({'status':'ephemeral neutral category colors; not era materials, finish proposal, browser export or artistic acceptance','native':{'path':a.native,'sha256':a.sha256},'rendererSha256':sha(__file__),'colors':colors,'classification':inventory,'views':views,'nativeUnchanged':True},indent=2)+'\n')
