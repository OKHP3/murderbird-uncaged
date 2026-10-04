"""Blender controlled transfer and frozen03 material-only neutral verification."""
import bpy, importlib.util, json, hashlib, struct, sys
from pathlib import Path
import numpy as np
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'assets/audit/cg-supervised-finish04'
SOURCE=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
NATIVE=SOURCE/'assets/models/cg-supervised01/attempt03/murderbird-supervised-builder.blend'
assert hashlib.sha256(NATIVE.read_bytes()).hexdigest()=='01103e35bcf16f03fc4a7b7d157bbe89d7267b8d0ca5ca8cd3f6167a6fcb8fce'
def module(name):
 spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/name);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
new=module('cg-supervised-finish04.py');old=module('cg-supervised-finish02.py')
report={'source_native':str(NATIVE),'source_sha256':hashlib.sha256(NATIVE.read_bytes()).hexdigest(),'status':'Technical transfer correction only; no artistic acceptance'}
# Swatch checks exported PNG raw byte stats externally plus rendered emission.
bpy.ops.wm.read_factory_settings(use_empty=True)
scene=bpy.context.scene
known=np.zeros((8,8,3),np.float32);known[:]=(.05,.073,.04)
(OUT/'swatch').mkdir(exist_ok=True)
images=[old.write(OUT/'swatch/generated-old.png',known,False),new.write(OUT/'swatch/file-corrected.png',known,False),new.write(OUT/'swatch/non-color.png',known,True)]
report['swatch']={'intended_linear':known[0,0].tolist(),'expected_srgb':new.linear_to_srgb(known[0,0]).tolist(),'images':[{'name':im.name,'source':im.source,'colorspace':im.colorspace_settings.name,'api_pixel':list(im.pixels[:3])} for im in images]}
for i,im in enumerate(images[:2]):
 bpy.ops.mesh.primitive_plane_add(size=1,location=((i-.5)*1.1,0,0));o=bpy.context.object
 mat=bpy.data.materials.new('Swatch '+str(i));mat.use_nodes=True;n=mat.node_tree.nodes;n.clear()
 tex=n.new('ShaderNodeTexImage');tex.image=im;em=n.new('ShaderNodeEmission');out=n.new('ShaderNodeOutputMaterial')
 mat.node_tree.links.new(tex.outputs['Color'],em.inputs['Color']);mat.node_tree.links.new(em.outputs[0],out.inputs['Surface']);o.data.materials.append(mat)
camd=bpy.data.cameras.new('Swatch camera');cam=bpy.data.objects.new('Swatch camera',camd);scene.collection.objects.link(cam);cam.location=(0,0,3);camd.type='ORTHO';camd.ortho_scale=2.3;scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=1;scene.render.resolution_x=256;scene.render.resolution_y=128;scene.render.resolution_percentage=100;scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.render.filepath=str(OUT/'swatch/emission.png');bpy.ops.render.render(write_still=True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'swatch/swatch.glb'),export_format='GLB',export_image_format='AUTO')
# Preserve frozen03 camera and neutral rig from its evidence receipt.
bpy.ops.wm.open_mainfile(filepath=str(NATIVE));scene=bpy.context.scene
for o in list(scene.objects):
 if o.type in ('CAMERA','LIGHT'):bpy.data.objects.remove(o,do_unlink=True)
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.cycles.use_denoising=True
scene.render.resolution_x=600;scene.render.resolution_y=400;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=0;scene.view_settings.gamma=1
prior=json.loads((SOURCE/'assets/audit/cg-supervised01/attempt03/builder/receipt.json').read_text())['cameras']['canon-neutral']
camd=bpy.data.cameras.new('Finish04 fixed neutral');cam=bpy.data.objects.new(camd.name,camd);scene.collection.objects.link(cam);scene.camera=cam
cam.location=prior['location'];cam.rotation_euler=prior['rotation_euler'];camd.type=prior['projection'];camd.ortho_scale=prior['ortho_scale'];camd.shift_x,camd.shift_y=prior['shift']
world=bpy.data.worlds.new('Finish04 fixed neutral');world.use_nodes=True;scene.world=world
world.node_tree.nodes['Background'].inputs[0].default_value=prior['world_color'];world.node_tree.nodes['Background'].inputs[1].default_value=prior['world_strength']
for spec in prior['areas']:
 d=bpy.data.lights.new('Finish04 fixed area','AREA');o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.location=spec['location'];o.rotation_euler=spec['rotation_euler'];d.energy=spec['power'];d.color=spec['color'];d.size=spec['size']
report['neutral_setup']=prior
report['actual_render_settings']={'engine':'CYCLES','device':'CPU','samples':8,'denoising':True,'resolution':[600,400],'view_transform':'AgX','look':'AgX - Medium High Contrast','exposure':0,'gamma':1}
scene.render.filepath=str(OUT/'neutral-old.png');bpy.ops.render.render(write_still=True)
report['finish']=new.apply(scene,OUT,'builder',SOURCE)
scene.render.filepath=str(OUT/'neutral-corrected.png');bpy.ops.render.render(write_still=True)
bpy.context.preferences.filepaths.save_version=0
saved=Path('/tmp/murderbird-finish04-verification.blend');bpy.ops.wm.save_as_mainfile(filepath=str(saved));report['reopen_native_path']=str(saved);report['reopen_native_sha256']=hashlib.sha256(saved.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(saved));scene=bpy.context.scene
report['reopen_meshes_match']=report['finish']['mesh_digests_after']=={o.name:new.digest(o) for o in scene.objects if o.type=='MESH' and not o.get('authoringGuide')}
report['reopened_corrected_images']=[{'name':im.name,'source':im.source,'colorspace':im.colorspace_settings.name,'packed':bool(im.packed_file)} for im in bpy.data.images if 'finish04-' in im.name]
scene.render.filepath=str(OUT/'neutral-reopened.png');bpy.ops.render.render(write_still=True)
# Standard glTF extraction on entire preserved character for exact PNG transfer evidence.
report['export']=module('cg-supervised-export.py').export(scene,OUT/'verification.glb')
report['era_smoke']={}
for era in ('maker','mechanic'):
 bpy.ops.wm.open_mainfile(filepath=str(NATIVE))
 report['era_smoke'][era]=new.apply(bpy.context.scene,OUT/'era-smoke',era,SOURCE)
(OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print('FINISH04_VERIFIED')
