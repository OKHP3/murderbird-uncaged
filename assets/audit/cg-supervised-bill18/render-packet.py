"""Read-only render packet from final saved18 native; same17 cameras/lights."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Matrix
O=Path(__file__).resolve().parent/'attempt02';H=Path('/Users/okh/.codex/worktrees/cg-supervised-layered-crown17/murderbird-uncaged/assets/audit/cg-supervised-head17/attempt02')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();native=O/'formed-bill18.blend';pin=sha(native)
bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;c=s.camera
refs=json.loads((H/'receipt.json').read_text())['cameras'];angles=json.loads((H/'diagnostic-cameras.json').read_text())['cameras'];receipt=json.loads((O/'receipt.json').read_text())
s.render.engine='CYCLES';s.cycles.samples=4;s.cycles.use_denoising=True;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
clay=bpy.data.materials.new('CGH18 temporary diagnostic clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.42,.42,.42,1);bs.inputs['Roughness'].default_value=.75
for name,rc in list(refs.items())+[(n,rc) for n,rc in angles.items() if n.startswith('turntable')]:
 c.matrix_world=Matrix(rc['matrix']);c.data.ortho_scale=rc['scale'];c.data.shift_x,c.data.shift_y=rc['shift'];s.render.resolution_x,s.render.resolution_y=rc['resolution'];s.view_layers[0].material_override=clay if 'clay' in name else None;s.render.filepath=str(O/(name+'.png'));bpy.context.view_layer.update();bpy.ops.render.render(write_still=True);receipt['cameras'][name]=rc;receipt['native_sha256']=pin;receipt['image_hashes']={p.name:sha(p) for p in O.glob('*.png')};(O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('BILL18_PACKET',name,flush=True)
assert sha(native)==pin;receipt['native_unchanged_during_render']=True;(O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('BILL18_PACKET_DONE',flush=True)
