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
  o['cgSupervisedHead10']=True;o['cg1cRegion']='head';o['cg2bRegion']='head';o['cgSurfaceFamilies']='["head-armor"]';o['cageControls']=json.dumps(controls);o['constructionStatus']='Fresh source-inspired sparse cage; depth and unseen back proposal; no owner acceptance'
  d.materials.append(material);uv=d.uv_layers.new(name='head10-local-plate-uv')
  for f in d.polygons:
   f.use_smooth=True
   for li in f.loop_indices:
    q=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=((q.y-min(v.co.y for v in d.vertices))/(max(v.co.y for v in d.vertices)-min(v.co.y for v in d.vertices)),(q.z-min(v.co.z for v in d.vertices))/(max(v.co.z for v in d.vertices)-min(v.co.z for v in d.vertices)))
  s=o.modifiers.new('editable sparse Catmull Clark cage','SUBSURF');s.levels=2;s.render_levels=2
  made.append(o);return o
 # Independent hand-authored 8-corner transverse control rings; lower body
 # stays posterior of optic. Flattened diagonal roof, not prior ellipsoid.
 controls=[(565,145,245,.038),(575,132,251,.055),(625,55,239,.110),(645,48,225,.131),(686,65,203,.149),(741,99,156,.168),(780,123,139,.179),(806,141,158,.177),(850,175,204,.157),(890,213,231,.115),(901,229,239,.104)]
 vs=[]
 for x,top,bot,w in controls:
  for dep,y in [(0,top+5),(.80*w,top+1),(w,top+6),(.94*w,bot-5),(0,bot),(-.94*w,bot-5),(-w,top+6),(-.80*w,top+1)]:vs.append(p(x,y,dep))
 fs=[(j*8+k,j*8+(k+1)%8,(j+1)*8+(k+1)%8,(j+1)*8+k) for j in range(len(controls)-1) for k in range(8)];fs.extend([tuple(range(7,-1,-1)),tuple((len(controls)-1)*8+k for k in range(8))]);mesh('CGH10 posterior cranial wedge',vs,fs,controls)
 # Two true folded narrow strips with finite transverse depth, one editable
 # object. They flank the optic; no complete anterior transverse foredeck.
 line=[(644,55,.130),(654,57,.137),(710,86,.158),(759,116,.174),(801,143,.178),(836,170,.164),(858,190,.148),(885,215,.119),(901,234,.102),(903,239,.099)]
 vs=[];fs=[]
 for side in (-1,1):
  off=len(vs)
  for x,y,d in line:
   for dy,dd in [(-6,-.006),(-6,0),(5,.002),(7,-.003),(5,-.007),(-4,-.01)]:vs.append(p(x,y+dy,side*(d+dd)))
  fs.extend((off+j*6+k,off+j*6+(k+1)%6,off+(j+1)*6+(k+1)%6,off+(j+1)*6+k) for j in range(len(line)-1) for k in range(6));fs.extend([tuple(off+k for k in range(5,-1,-1)),tuple(off+(len(line)-1)*6+k for k in range(6))])
 mesh('CGH10 narrow diagonal brow root bridge',vs,fs,line)
 bpy.context.view_layer.update()
 return {'hidden_originals':hidden,'new_objects':[o.name for o in made],'controls':{'wedge':controls,'bridge':line},'receiving_material':material.name,'no_pose_change':True,'attempt':attempt}
def run():
 attempt=int(sys.argv[-1]) if sys.argv[-1].isdigit() else 1
 out=ROOT/'assets/audit/cg-supervised-head10'/('attempt%02d'%attempt);out.mkdir(parents=True,exist_ok=True)
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
 new=[o for o in scene.objects if o.get('cgSupervisedHead10')]
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
 clay=bpy.data.materials.new('CGH10 diagnostic clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.42,.42,.42,1);bs.inputs['Roughness'].default_value=.75
 def render(name,w,h,override=False):
  scene.render.resolution_x=w;scene.render.resolution_y=h;scene.view_layers[0].material_override=clay if override else None;scene.render.filepath=str(out/(name+'.png'));bpy.context.view_layer.update();report['cameras'][name]={'matrix':list(map(list,camera.matrix_world)),'scale':camera.data.ortho_scale,'shift':[camera.data.shift_x,camera.data.shift_y],'resolution':[w,h]};bpy.ops.render.render(write_still=True);(out/'receipt.json').write_text(json.dumps(report,indent=2));print('HEAD10_RENDERED',name,flush=True)
 render('after-pbr-source-full-bird',1280,853)
 target=scene.objects['CG2b head frame'].matrix_world@Vector((0,.005,-.025))
 def close(loc):
  camera.location=target+Vector(loc);camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.shift_x=camera.data.shift_y=0;camera.data.ortho_scale=.84
 close((-6,0,0));render('after-clay-head-profile',800,800,True)
 close((-5,-4,1.4));render('after-clay-head-grazing',800,800,True)
 close((0,-6,.35));render('after-clay-head-front',800,800,True)
 scene.view_layers[0].material_override=None
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'formed-head10.blend'))
 report['native_sha256']=sha(out/'formed-head10.blend');report['input_preserved']=sha(INPUT)==EXPECTED;report['image_hashes']={f.name:sha(f) for f in out.glob('*.png')};(out/'receipt.json').write_text(json.dumps(report,indent=2));print('HEAD10_COMPLETE',out,flush=True)
if __name__=='__main__':run()
