import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');J=Path('/tmp/cg-cranial-projection-diagnosis15.json');d=json.loads(J.read_text());N=R/'assets/audit/cg-supervised-head13/attempt02/formed-head13.blend';bpy.ops.wm.open_mainfile(filepath=str(N));s=bpy.context.scene;frame=s.objects['CG2b head frame'].matrix_world.copy()
for o in s.objects:
 if o.get('cgSupervisedHead13'):o.hide_render=True
ps={k:Vector(v) for k,v in d['hypothetical_points'].items()};ps['far_crest_apex'].z=.12
ps.update({'roof_near_rear':Vector((-.06,.11,.11)),'roof_far_rear':Vector((.06,.11,.11)),'roof_near_front':Vector((-.06,-.02,.08)),'roof_far_front':Vector((.06,-.02,.08)),'far_crest_front_join':Vector((.10,.08,.105)),'far_rear_support':Vector((.09,.08,.105))})
edges=[('near_crest_apex','near_crest_rear_support'),('near_crest_apex','near_crest_front_join'),('near_crest_front_join','near_crest_rear_support'),('near_crest_front_join','near_brow'),('near_brow','bill_root'),('far_crest_apex','far_crest_front_join'),('far_crest_apex','far_rear_support'),('far_crest_front_join','far_rear_support'),('far_crest_front_join','far_brow'),('roof_near_rear','roof_far_rear'),('roof_near_rear','roof_near_front'),('roof_far_rear','roof_far_front'),('roof_far_front','roof_near_front')]
curve=bpy.data.curves.new('HYPOTHETICAL sparse point edges only','CURVE');curve.dimensions='3D';curve.bevel_depth=.0012;curve.resolution_u=1;curve.bevel_resolution=1
for a,b in edges:
 sp=curve.splines.new('POLY');sp.points.add(1);sp.points[0].co=(*ps[a],1);sp.points[1].co=(*ps[b],1)
o=bpy.data.objects.new('HYPOTHETICAL crest blades and compact roof wire, no finished surface',curve);s.collection.objects.link(o);o.matrix_world=frame
mat=bpy.data.materials.new('HYPOTHETICAL wire orange');mat.diffuse_color=(1,.25,.01,1);mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(1,.25,.01,1);bs.inputs['Emission Color'].default_value=(1,.12,.005,1);bs.inputs['Emission Strength'].default_value=.5;curve.materials.append(mat)
clay=bpy.data.materials.new('diagnosis only clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.42,.42,.42,1);bs.inputs['Roughness'].default_value=.75
# Keep existing source lighting, use receiving geometry PBR so orange guide remains visible.
s.render.engine='CYCLES';s.cycles.samples=4;s.cycles.use_denoising=True;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
r=json.loads((R/'assets/audit/cg-supervised-head12/attempt02/receipt.json').read_text())['cameras'];out={}
for name in ['after-clay-source-full-bird','after-clay-head-profile']:
 c=r[name];s.camera.matrix_world=Matrix(c['matrix']);s.camera.data.ortho_scale=c['scale'];s.camera.data.shift_x,s.camera.data.shift_y=c['shift'];s.render.resolution_x,s.render.resolution_y=c['resolution'];bpy.context.view_layer.update();p='/tmp/cg-diagnosis15-hypothetical-'+('whole' if 'full' in name else 'profile')+'.png';s.render.filepath=p;bpy.ops.render.render(write_still=True);out[name]=p;print('HYPOTHETICAL_RENDERED',p,flush=True)
d['hypothetical_render_paths']=out;d['checks_not_run']=[x for x in d['checks_not_run'] if x!='No hypothetical Blender render'];d['checks_not_run'].append('Sparse edge visualization only, no roof surfaces or continuous visibility proof');d['hypothetical_native_saved']=False;d['hypothetical_geometry']='Single unsaved sparse bevel wire for localized blades and compact roof; no new skin/detail';J.write_text(json.dumps(d,indent=2))
