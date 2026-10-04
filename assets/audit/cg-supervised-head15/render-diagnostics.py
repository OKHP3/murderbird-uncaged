"""Read frozen native15; temporary wire/eight-angle render diagnostics only."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
W=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent/'attempt02';bpy.ops.wm.open_mainfile(filepath=str(O/'localized-head15.blend'));s=bpy.context.scene;c=s.camera
ref=json.loads((Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged/assets/audit/cg-supervised-head13/attempt02/receipt.json')).read_text());new=[o for o in s.objects if o.get('cgSupervisedHead15')]
s.render.engine='CYCLES';s.cycles.samples=8;s.cycles.use_denoising=True;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
clay=bpy.data.materials.new('CGH15 temporary diagnostic clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.42,.42,.42,1);bs.inputs['Roughness'].default_value=.75
receipt={'native':'localized-head15.blend','cameras':{},'native_mutated':False}
def render(name,rc,mode):
 c.matrix_world=Matrix(rc['matrix']);c.data.ortho_scale=rc['scale'];c.data.shift_x,c.data.shift_y=rc['shift'];s.render.resolution_x,s.render.resolution_y=rc['resolution'];s.view_layers[0].material_override=clay if mode=='clay' else None;s.render.filepath=str(O/(name+'.png'));bpy.context.view_layer.update();receipt['cameras'][name]=rc;bpy.ops.render.render(write_still=True);print('HEAD15_DIAGNOSTIC',name,flush=True)
for o in new:
 for m in o.modifiers:m.show_render=False
 w=o.modifiers.new('temporary wire diagnostic','WIREFRAME');w.thickness=.0012;w.use_replace=True
for v in ['source-full-bird','head-profile','head-grazing','head-far-profile','head-front']:render('wire-'+v,ref['cameras']['after-clay-'+v],'clay')
for o in new:
 o.modifiers.remove(o.modifiers.get('temporary wire diagnostic'))
 for m in o.modifiers:m.show_render=True
for i in range(8):
 a=2*math.pi*i/8;target=Vector((0,-.03,.96));c.location=target+Vector((-6*math.cos(a),-6*math.sin(a),.65));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.data.shift_x=c.data.shift_y=0;c.data.ortho_scale=2.34;bpy.context.view_layer.update();rc={'matrix':list(map(list,c.matrix_world)),'scale':2.34,'shift':[0,0],'resolution':[800,900],'turntable_degrees':i*45,'scope':'supplemental whole bird diagnostic; no source-camera inference'}
 for m in ['clay','pbr']:render('turntable-%03d-'%(i*45)+m,rc,m)
(O/'diagnostic-cameras.json').write_text(json.dumps(receipt,indent=2));print('HEAD15_DIAGNOSTIC_COMPLETE',flush=True)
