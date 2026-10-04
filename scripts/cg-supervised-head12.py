"""Fresh sparse posterior cranial cage. No prior vault fitting or source textures."""
import bpy, json, math, hashlib, sys, importlib.util, datetime
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
INPUT=BASE/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend'
EXPECTED='72e7e53daf40b7128cdf9b173006c639bcf123952547a2576fb2de29130f06d4'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def p(x,y,d):return (d,(788-x)*.0012+.005,(188-y)*.0012+.020)
def apply(scene,root_path=None,era='builder',attempt=1):
 frame=scene.objects['CG2b head frame'].matrix_world.copy(); made=[]; hidden=[]
 material=scene.objects['CGH06 swept overlapping dorsal brow plate L0'].data.materials[0]
 for o in list(scene.objects):
  if o.hide_render:continue
  if (o.get('cgSupervisedHead05') and 'curved recessed vault' in o.name) or (o.get('cgSupervisedHead06') and any(k in o.name for k in ['dorsal brow','bill saddle','crown sheet','dorsal sheet','frontal saddle'])):
   hidden.append(o.name);o.hide_render=True;o.hide_set(True)
 def mesh(name,vs,fs,controls):
  d=bpy.data.meshes.new(name);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.matrix_world=frame
  o['cgSupervisedHead12']=True;o['cg1cRegion']='head';o['cg2bRegion']='head';o['cgSurfaceFamilies']='["head-armor"]';o['cageControls']=json.dumps(controls);o['constructionStatus']='Fresh source-inspired sparse cage; depth and unseen back proposal; no owner acceptance'
  d.materials.append(material);uv=d.uv_layers.new(name='head12-local-plate-uv')
  for f in d.polygons:
   f.use_smooth=True
   for li in f.loop_indices:
    q=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=((q.y-min(v.co.y for v in d.vertices))/(max(v.co.y for v in d.vertices)-min(v.co.y for v in d.vertices)),(q.z-min(v.co.z for v in d.vertices))/(max(v.co.z for v in d.vertices)-min(v.co.z for v in d.vertices)))
  s=o.modifiers.new('editable sparse Catmull Clark cage','SUBSURF');s.levels=2;s.render_levels=2
  made.append(o);return o
 # Sparse independent posterior crown and two localized orbital brows.
 # Source-coordinate labels aid diagnosis only; July is not exact metrology.
 controls=[(560,156,260,.030),(580,132,264,.045),(615,89,258,.062),(635,72,242,.073),(670,90,220,.092),(710,112,197,.115),(742,128,156,.129),(765,135,145,.131)]
 if attempt==2:controls.extend([(791,142,161,.113),(817,151,178,.098),(842,163,196,.085),(867,187,220,.076),(895,220,247,.081),(919,249,261,.079)])
 vs=[]
 for x,top,bot,w in controls:
  for dep,y in [(0,top),(.6*w,top+3),(w,top+14),(.92*w,bot-8),(0,bot),(-.92*w,bot-8),(-w,top+14),(-.6*w,top+3)]:vs.append(p(x,y,dep))
 fs=[(j*8+k,j*8+(k+1)%8,(j+1)*8+(k+1)%8,(j+1)*8+k) for j in range(len(controls)-1) for k in range(8)];fs.extend([tuple(range(7,-1,-1)),tuple((len(controls)-1)*8+k for k in range(8))]);mesh('CGH12 physical posterior crest cage',vs,fs,controls)
 lines={}
 for side,label in [(-1,'near'),(1,'far')]:
  # The far edge is deliberately lower and inset, separately constrained.
  delta=9 if side==1 else 0
  line=[(665,101+delta,.081),(700,114+delta,.106),(745,130+delta,.130),(780,135+delta,.141),(817,141+delta,.140),(845,158+delta,.133),(867,183+delta,.119),(897,219,.102),(915,243,.091)]
  lines[label]=line;vs=[];fs=[]
  for x,y,d in line:
   for dy,dd in [(-4,-.004),(-4,0),(4,.001),(5,-.003),(4,-.006),(-3,-.007)]:vs.append(p(x,y+dy,side*(d+dd)))
  fs.extend((j*6+k,j*6+(k+1)%6,(j+1)*6+(k+1)%6,(j+1)*6+k) for j in range(len(line)-1) for k in range(6));fs.extend([tuple(k for k in range(5,-1,-1)),tuple((len(line)-1)*6+k for k in range(6))])
  mesh('CGH12 physical '+label+' localized diagonal brow',vs,fs,line)
 # Compact front hood meets the retained bill. Entire optic-adjacent roof is
 # inset medial to the original seat; no transverse visor crosses the crown.
 fore=[(848,161,.074),(862,174,.084),(885,207,.096),(909,235,.093),(919,253,.085)]
 vs=[]
 for x,y,w in fore:
  for u in (-1,-.5,0,.5,1):vs.append(p(x,y+10*u*u,u*w))
 fs=[(j*5+k,j*5+k+1,(j+1)*5+k+1,(j+1)*5+k) for j in range(len(fore)-1) for k in range(4)]
 fo=mesh('CGH12 physical compact foredeck bill root',vs,fs,fore)
 so=fo.modifiers.new('inward shell return','SOLIDIFY');so.thickness=.003;so.offset=-1
 bpy.context.view_layer.update()
 return {'hidden_originals':hidden,'new_objects':[o.name for o in made],'controls':{'posterior_crest':controls,'near_brow':lines['near'],'far_brow':lines['far'],'foredeck':fore},'receiving_material':material.name,'no_pose_change':True,'attempt':attempt}
def run():
 attempt=int(sys.argv[-1]) if sys.argv[-1].isdigit() else 1
 out=ROOT/'assets/audit/cg-supervised-head12'/('attempt%02d'%attempt);out.mkdir(parents=True,exist_ok=True)
 assert sha(INPUT)==EXPECTED
 bpy.ops.wm.open_mainfile(filepath=str(INPUT));scene=bpy.context.scene
 def digest(o):
  h=hashlib.sha256();h.update(str((list(map(list,o.matrix_world)),o.parent.name if o.parent else None,sorted(o.items()))).encode())
  if o.type=='MESH':
   h.update(str([(tuple(v.co)) for v in o.data.vertices]).encode());h.update(str([(tuple(f.vertices),f.material_index) for f in o.data.polygons]).encode());h.update(str([(u.name,[tuple(d.uv) for d in u.data]) for u in o.data.uv_layers]).encode());h.update(str([m.name if m else None for m in o.data.materials]).encode())
  return h.hexdigest()
 originals={o.name:digest(o) for o in scene.objects if o.type in ('MESH','EMPTY')};vis={o.name:[o.hide_render,o.hide_get()] for o in scene.objects}
 report=apply(scene,attempt=attempt);report.update(input_sha256=EXPECTED,shared_main_sha='251f2f0243181e97140179c2aff6eb057e165438',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),frame_matrix=list(map(list,scene.objects['CG2b head frame'].matrix_world)))
 report['original_payload_changes']=[n for n,h in originals.items() if digest(scene.objects[n])!=h];assert not report['original_payload_changes']
 report['original_visibility_changes']={n:{'before':v,'after':[scene.objects[n].hide_render,scene.objects[n].hide_get()]} for n,v in vis.items() if [scene.objects[n].hide_render,scene.objects[n].hide_get()]!=v}
 report['original_count']=len(originals);report['sources']={r:sha(BASE/r) for r in ['assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg','context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png']}
 new=[o for o in scene.objects if o.get('cgSupervisedHead12')]
 report['mesh_checks']=[]
 for o in new:
  e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=e.to_mesh();uv=[v for d in me.uv_layers.active.data for v in d.uv];coords=[c for v in me.vertices for c in v.co]
  report['mesh_checks'].append({'name':o.name,'cage_vertices':len(o.data.vertices),'cage_faces':len(o.data.polygons),'evaluated_vertices':len(me.vertices),'finite':all(math.isfinite(v) for v in coords+uv),'uv_range':[min(uv),max(uv)]});e.to_mesh_clear()
 def mod(name):
  sp=importlib.util.spec_from_file_location('h10_'+name,ROOT/'scripts'/name);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
 # Exact saved06 workshop rig retained; camera04 global35 restored explicitly.
 camera=scene.camera;canon=mod('cg-supervised-camera04.py').camera(ROOT);camera.location=canon['location'];camera.rotation_euler=canon['rotation_euler'];camera.data.type=canon['projection'];camera.data.ortho_scale=canon['ortho_scale'];camera.data.shift_x,camera.data.shift_y=canon['shift'];camera.data.lens=canon['lens_mm']
 scene.render.engine='CYCLES';scene.cycles.samples=8;scene.cycles.use_denoising=True;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 report['rig']={'world':[(n.name,[(i.name,str(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in scene.world.node_tree.nodes],'lights':[{'name':o.name,'matrix':list(map(list,o.matrix_world)),'energy':o.data.energy,'color':list(o.data.color),'size':o.data.size} for o in scene.objects if o.type=='LIGHT'],'exposure':scene.view_settings.exposure,'look':scene.view_settings.look,'transform':scene.view_settings.view_transform};report['cameras']={}
 clay=bpy.data.materials.new('CGH12 diagnostic clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.42,.42,.42,1);bs.inputs['Roughness'].default_value=.75
 def render(name,w,h,override=False):
  scene.render.resolution_x=w;scene.render.resolution_y=h;scene.view_layers[0].material_override=clay if override else None;scene.render.filepath=str(out/(name+'.png'));bpy.context.view_layer.update();report['cameras'][name]={'matrix':list(map(list,camera.matrix_world)),'scale':camera.data.ortho_scale,'shift':[camera.data.shift_x,camera.data.shift_y],'resolution':[w,h]};bpy.ops.render.render(write_still=True);(out/'receipt.json').write_text(json.dumps(report,indent=2));print('HEAD12_RENDERED',name,flush=True)
 bpy.context.view_layer.update()
 canonical_matrix=camera.matrix_world.copy();canonical_scale=camera.data.ortho_scale;canonical_shift=(camera.data.shift_x,camera.data.shift_y)
 target=scene.objects['CG2b head frame'].matrix_world@Vector((0,.005,-.025))
 def close(loc):
  camera.location=target+Vector(loc);camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.shift_x=camera.data.shift_y=0;camera.data.ortho_scale=.84
 def visibility(before):
  for o in new:o.hide_render=before;o.hide_set(before)
  for n in report['hidden_originals']:
   scene.objects[n].hide_render=vis[n][0] if before else True;scene.objects[n].hide_set(vis[n][1] if before else True)
  bpy.context.view_layer.update()
 def pair(name,w,h,clay_mode):
  visibility(True);render('before-'+name,w,h,clay_mode)
  visibility(False);render('after-'+name,w,h,clay_mode)
 pair('clay-source-full-bird',1280,853,True)
 close((-6,0,0));pair('clay-head-profile',800,800,True)
 print('HEAD12_FIRST_PAIR_COMPLETE',flush=True)
 close((-5,-4,1.4));pair('clay-head-grazing',800,800,True)
 close((0,-6,.35));pair('clay-head-front',800,800,True)
 camera.matrix_world=canonical_matrix;camera.data.ortho_scale=canonical_scale;camera.data.shift_x,camera.data.shift_y=canonical_shift;pair('pbr-source-full-bird',1280,853,False)
 close((-5,-4,1.4));pair('clay-head-oblique',800,800,True)
 # Sparse wire guide with original geometry preserved. Wire renders only new
 # cages; material override keeps lighting fixed.
 for o in new:
  for m in o.modifiers:
   if m.type=='SUBSURF':m.show_render=False
  w=o.modifiers.new('diagnostic wire only','WIREFRAME');w.thickness=.0012;w.use_replace=True
 render('wire-head-oblique',800,800,True)
 for o in new:
  o.modifiers.remove(o.modifiers.get('diagnostic wire only'))
  for m in o.modifiers:
   if m.type=='SUBSURF':m.show_render=True
 scene.view_layers[0].material_override=None
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'formed-head12.blend'),relative_remap=False)
 report['native_sha256']=sha(out/'formed-head12.blend');report['input_preserved']=sha(INPUT)==EXPECTED;report['image_hashes']={f.name:sha(f) for f in out.glob('*.png')};(out/'receipt.json').write_text(json.dumps(report,indent=2));print('HEAD12_COMPLETE',out,flush=True)
if __name__=='__main__':run()
