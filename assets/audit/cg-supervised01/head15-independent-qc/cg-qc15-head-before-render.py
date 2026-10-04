import bpy,json
from pathlib import Path
from mathutils import Matrix
R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
W=Path('/Users/okh/.codex/worktrees/cg-supervised-localized-crown15/murderbird-uncaged')
bpy.ops.wm.open_mainfile(filepath=str(R/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend'))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=4;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_percentage=50;s.render.image_settings.file_format='PNG'
r=json.loads((W/'assets/audit/cg-supervised-head15/attempt02/receipt.json').read_text())
for v in ['source-full-bird','head-profile','head-front','head-grazing']:
 c=r['cameras']['after-pbr-'+v];s.camera.matrix_world=Matrix(c['matrix']);s.camera.data.ortho_scale=c['scale'];s.camera.data.shift_x,s.camera.data.shift_y=c['shift'];s.render.resolution_x,s.render.resolution_y=c['resolution'];s.render.filepath='/tmp/cg-qc15-head-before06-'+v+'.png';bpy.context.view_layer.update();bpy.ops.render.render(write_still=True)
print('READONLY_BASE_RENDER_DONE',flush=True)
