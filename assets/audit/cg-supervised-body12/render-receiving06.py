"""Two matched receiving06 full-character baseline renders; native read only."""
import bpy,json,hashlib,argparse,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--input-root',required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);root=Path(__file__).resolve().parents[3];inp=Path(a.input_root);out=root/'assets/audit/cg-supervised-body12/attempt02';r=json.loads((out/'receipt.json').read_text());native=inp/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();h=sha(native);assert h=='72e7e53daf40b7128cdf9b173006c639bcf123952547a2576fb2de29130f06d4'
bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;cam=s.camera;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=r['renderSettings']['samples'];s.cycles.use_denoising=True;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
clay=bpy.data.materials.new('BODY12 receiving06 diagnostic clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.23,.23,.23,1);bs.inputs['Roughness'].default_value=.64
records={};images={}
for mode in ('pbr','clay'):
 c=r['cameras']['before-whole-'+mode];cam.location=c['location'];cam.rotation_euler=c['rotation_euler'];cam.data.type='ORTHO';cam.data.ortho_scale=c['scale'];cam.data.shift_x,cam.data.shift_y=c['shift'];s.render.resolution_x,s.render.resolution_y=c['resolution']
 for q in c['lights']:
  o=s.objects[q['name']];o.location=q['location'];o.rotation_euler=q['rotation'];o.data.energy=q['power'];o.data.color=q['color'];o.data.size=q['size']
 s.view_layers[0].material_override=clay if mode=='clay' else None
 file=out/('receiving06-whole-'+mode+'.png');s.render.filepath=str(file);bpy.ops.render.render(write_still=True);images[file.name]=sha(file);records[mode]=c
assert sha(native)==h
(out/'receiving06-comparison.json').write_text(json.dumps(dict(sourceSHA256=h,nativeSaved=False,originalSourceUnchanged=True,camerasAndLightsExactlyCopiedFromFinalPairedBefore=records,renderSettings=r['renderSettings'],images=images,comparisonMeaning='receiving06 original exterior vs final02; primary before-whole images are BODY11 smooth guide'),indent=2)+'\n')
