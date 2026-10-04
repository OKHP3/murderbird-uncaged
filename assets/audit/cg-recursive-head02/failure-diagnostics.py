"""Read-only profile/far/rear evidence for the stopped second geometry design."""
import bpy,json,hashlib,sys,argparse,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
p=argparse.ArgumentParser();p.add_argument('--receiving-root',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);BASE=Path(a.receiving_root)
out=ROOT/'assets/audit/cg-recursive-head02/attempt02/builder';native=ROOT/'assets/models/cg-recursive-head02/attempt02/murderbird-head02-builder.blend';sha=lambda x:hashlib.sha256(Path(x).read_bytes()).hexdigest();expected=sha(native)
bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene;cam=scene.camera;rc=json.loads((BASE/'assets/audit/cg-supervised01/attempt09/builder/receipt.json').read_text())['cameras'];r=json.loads((out/'receipt.json').read_text())
clay=bpy.data.materials.new('HEAD02 failure diagnostic clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.42,.42,.42,1);bs.inputs['Roughness'].default_value=.75
for view in ['head-neck','side-profile','neutral-090','neutral-180','canon-workshop']:
 c=rc[view];cam.location=c['location'];cam.rotation_euler=c['rotation_euler'];cam.data.type=c['projection'];cam.data.ortho_scale=c['ortho_scale'];cam.data.lens=c['lens_mm'];cam.data.shift_x,cam.data.shift_y=c['shift'];bg=scene.world.node_tree.nodes['Background'];bg.inputs[0].default_value=c['world_color'];bg.inputs[1].default_value=c['world_strength']
 lights=sorted([o for o in scene.objects if o.type=='LIGHT'],key=lambda o:o.name);assert len(lights)==len(c['areas'])
 for o,l in zip(lights,c['areas']):o.location=l['location'];o.rotation_euler=l['rotation_euler'];o.data.energy=l['power'];o.data.color=l['color'];o.data.size=l['size']
 scene.render.engine='CYCLES';scene.cycles.samples=4;scene.cycles.use_denoising=True;scene.render.resolution_x,scene.render.resolution_y=[round(v*.5) for v in c['resolution']];scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=0;scene.view_settings.gamma=1
 for mode in ['clay','pbr']:
  scene.view_layers[0].material_override=clay if mode=='clay' else None;key='after-'+view+'-'+mode;scene.render.filepath=str(out/(key+'.png'));bpy.context.view_layer.update();bpy.ops.render.render(write_still=True);r['cameras'][key]=dict(c,resolution=[scene.render.resolution_x,scene.render.resolution_y],samples=4);print('HEAD02_FAILURE_DIAGNOSTIC',key,flush=True)
r['image_hashes']={p.name:sha(p) for p in out.glob('*.png')};r['diagnostic_native_unchanged']=sha(native)==expected;r['failure_diagnostics_authoring_sha256']=sha(Path(__file__));r['diagnostic_completed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();assert r['diagnostic_native_unchanged'];(out/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
