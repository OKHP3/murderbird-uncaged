"""Render exact receiving06 baseline in the same fixed whole-bird camera."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Matrix
W=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent;R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');B=R/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend'
bpy.ops.wm.open_mainfile(filepath=str(B));s=bpy.context.scene;c=s.camera;ref=json.loads((R/'assets/audit/cg-supervised-head13/attempt02/receipt.json').read_text());s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
clay=bpy.data.materials.new('HEAD15 comparison temporary clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.42,.42,.42,1);bs.inputs['Roughness'].default_value=.75
for mode in ['clay','pbr']:
 rc=ref['cameras']['after-'+mode+'-source-full-bird'];c.matrix_world=Matrix(rc['matrix']);c.data.ortho_scale=rc['scale'];c.data.shift_x,c.data.shift_y=rc['shift'];s.render.resolution_x,s.render.resolution_y=rc['resolution'];s.view_layers[0].material_override=clay if mode=='clay' else None;s.render.filepath=str(O/('before06-'+mode+'-source-full-bird.png'));bpy.context.view_layer.update();bpy.ops.render.render(write_still=True)
(O/'before06-receipt.json').write_text(json.dumps({'native_sha256':hashlib.sha256(B.read_bytes()).hexdigest(),'camera':rc,'native_saved':False,'scope':'actual immutable06 with zero new HEAD15 geometry'},indent=2))
