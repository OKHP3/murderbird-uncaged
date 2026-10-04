"""Disposable flat-ID/read-only native inspection. No native saved."""
import bpy,json,hashlib,colorsys,collections
from pathlib import Path
from mathutils import Vector
BASE=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
INPUT=BASE/'assets/audit/cg-recursive-three-loop01/loop01/integrated/body01/builder/murderbird-recursive-builder.blend'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
original_sha=sha(INPUT);bpy.ops.wm.open_mainfile(filepath=str(INPUT));scene=bpy.context.scene
rc=json.loads((BASE/'assets/audit/cg-supervised01/attempt09/builder/receipt.json').read_text())['cameras']['head-neck'];cam=scene.camera
cam.location=rc['location'];cam.rotation_euler=rc['rotation_euler'];cam.data.type=rc['projection'];cam.data.ortho_scale=rc['ortho_scale'];cam.data.lens=rc['lens_mm'];cam.data.shift_x,cam.data.shift_y=rc['shift']
scene.render.resolution_x=scene.render.resolution_y=640;scene.render.resolution_percentage=100;bpy.context.view_layer.update()
inventory=[]
for o in scene.objects:
 if o.type!='MESH':continue
 o.color=(.06,.06,.06,1)
 if not o.hide_render and (o.name.startswith('CGH') or o.get('cg2bRegion')=='head'):
  index=len(inventory);rgb=tuple(.16+.16*((index//(5**a))%5) for a in range(3));o.color=(*rgb,1)
  counts=collections.Counter(f.material_index for f in o.data.polygons)
  bounds=[o.matrix_world@Vector(c) for c in o.bound_box]
  inventory.append({'name':o.name,'color':list(rgb),'hide_render':o.hide_render,'hide_get':o.hide_get(),'tags':{k:v for k,v in o.items() if k.startswith('cg') or k=='surfaceRole'},'materials':[{'index':i,'name':m.name if m else None,'family':m.get('cgMetal05Family') if m else None,'era':m.get('cgMetal05Era') if m else None,'faces_using':counts.get(i,0)} for i,m in enumerate(o.data.materials)],'bounds_world':{'min':[min(v[a] for v in bounds) for a in range(3)],'max':[max(v[a] for v in bounds) for a in range(3)]}})
dg=bpy.context.evaluated_depsgraph_get();inv=cam.calc_matrix_camera(dg,x=640,y=640).inverted();direction=cam.matrix_world.to_3x3()@Vector((0,0,-1));samples=[]
for py in range(160,331,5):
 for px in range(250,531,5):
  q=inv@Vector((px/640*2-1,1-py/640*2,-1,1));origin=cam.matrix_world@(Vector(q[:3])/q.w)
  hit,loc,n,face,obj,matrix=scene.ray_cast(dg,origin,direction)
  if hit:
   # Native ray_cast can include explicitly render-hidden historical surfaces;
   # the disposable render below is the final visibility evidence.
   samples.append({'pixel':[px,py],'object':obj.name,'face':face,'hide_render':obj.hide_render,'hit_world':list(loc)})
mat=bpy.data.materials.new('TEMP ONLY head02 flat ID');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');em=nt.nodes.new('ShaderNodeEmission');info=nt.nodes.new('ShaderNodeObjectInfo');nt.links.new(info.outputs['Color'],em.inputs['Color']);nt.links.new(em.outputs[0],out.inputs['Surface']);scene.view_layers[0].material_override=mat
scene.render.engine='CYCLES';scene.cycles.samples=1;scene.cycles.use_denoising=False;scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False;scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.render.filepath='/tmp/cg-recursive-head02-flat-id.png';bpy.ops.render.render(write_still=True)
report={'input':str(INPUT),'input_sha256':original_sha,'input_unchanged':sha(INPUT)==original_sha,'native_saved':False,'temporary_diagnostic_only':True,'camera':rc,'render_resolution':[640,640],'visible_head_inventory':inventory,'ray_samples_including_render_hidden':samples,'flat_id_path':scene.render.filepath}
Path('/tmp/cg-recursive-head02-visible-inventory.json').write_text(json.dumps(report,indent=2)+'\n');print('READ_ONLY_HEAD02_PROBE_COMPLETE',len(inventory),original_sha,flush=True)
