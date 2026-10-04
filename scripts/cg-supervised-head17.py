"""HEAD17 broad swept crown courses on exact receiving06; no other regions edited."""
import bpy,json,math,hashlib,sys,importlib.util,datetime
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
INPUT=BASE/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend'
EXPECTED='72e7e53daf40b7128cdf9b173006c639bcf123952547a2576fb2de29130f06d4'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def modload(path):
 sp=importlib.util.spec_from_file_location('h17_'+path.stem,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def apply(scene,root_path=None,era='builder'):
 if era not in ('maker','mechanic','builder','advanced'):raise ValueError(era)
 if any(o.get('cgSupervisedHead17') for o in scene.objects):raise RuntimeError('Reload immutable06 before apply17')
 frame=scene.objects['CG2b head frame'].matrix_world.copy();made=[];hidden=[]
 materials=list(scene.objects['CGH06 swept overlapping dorsal brow plate L0'].data.materials)
 for o in scene.objects:
  if not o.hide_render and ((o.get('cgSupervisedHead05') and 'curved recessed vault' in o.name) or (o.get('cgSupervisedHead06') and any(k in o.name for k in ['dorsal brow','dorsal sheet','frontal saddle']))):
   hidden.append(o.name);o.hide_render=True;o.hide_set(True)
 def mesh(name,vs,fs,controls,bronze=False):
  d=bpy.data.meshes.new(name);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.matrix_world=frame
  o['cgSupervisedHead17']=True;o['cg1cRegion']='head';o['cg2bRegion']='head';o['cgSurfaceFamilies']='["head-armor","black-iron","worn-bronze"]';o['surfaceRole']='head-armor';o['constructionStatus']='Broad swept overlapping formed crown course; depth proposal; posterior receiving06 plates retained';o['cageControls']=json.dumps(controls)
  for m in materials:d.materials.append(m)
  uv=d.uv_layers.new(name='head17-normalized-local');lo=[min(v.co[a] for v in d.vertices) for a in (1,2)];hi=[max(v.co[a] for v in d.vertices) for a in (1,2)]
  for f in d.polygons:
   f.use_smooth=True;f.material_index=2 if bronze else 0
   for li in f.loop_indices:
    q=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=(max(0,min(1,(q.y-lo[0])/max(hi[0]-lo[0],1e-5))),max(0,min(1,(q.z-lo[1])/max(hi[1]-lo[1],1e-5))))
  sm=o.modifiers.new('formed metal crown cage smoothing','SUBSURF');sm.levels=sm.render_levels=2
  so=o.modifiers.new('thin inward metal formed return','SOLIDIFY');so.thickness=.0025;so.offset=-1;so.material_offset=1;so.material_offset_rim=1
  made.append(o);return o
 # Main roof is three separately curved, overlapping longitudinal metal courses.
 # Cross-section has actual downturned shoulders. Rear broad pointed course
 # joins the retained side layers instead of making an isolated antenna.
 courses=[('posterior swept crest',[(.267,.182,.022),(.247,.191,.052),(.215,.203,.097),(.171,.183,.126),(.132,.170,.131),(.101,.155,.125)]),
 ('middle overlapping crest',[(.178,.170,.025),(.155,.168,.075),(.127,.153,.128),(.085,.150,.140),(.042,.140,.142),(-.015,.125,.130)]),
 ('frontal crown root',[(.112,.161,.025),(.088,.160,.092),(.056,.155,.132),(.019,.149,.146),(-.023,.134,.140),(-.064,.104,.122),(-.104,.064,.104),(-.145,.028,.085)])]
 for label,rr in courses:
  vs=[]
  for j,(y,z,w) in enumerate(rr):
   for u in [-1,-.97,-.82,-.5,0,.5,.82,.97,1]:
    # Curved cross section carries its shoulder into existing head depth;
    # edge return is geometrically formed, not a flat floating card.
    side_drop=(.030 if label=='frontal crown root' else .058)*abs(u)**2.1;return_drop=.006*max(0,(abs(u)-.94)/.06)
    vs.append((u*w,y-.014*abs(u),z-side_drop-return_drop))
  fs=[(j*9+k,(j+1)*9+k,(j+1)*9+k+1,j*9+k+1) for j in range(len(rr)-1) for k in range(8)]
  mesh('CGH17 '+label,vs,fs,rr,bronze=(label=='frontal crown root'))
 # Broad unequal brow face panels form a segmented swept rim above the optic.
 # Each curves from the roof shoulder to its folded outer edge; no optic moves.
 for side,label in [(-1,'near'),(1,'far')]:
  stations=[(.188,.182,.087),(.151,.178,.122),(.108,.165,.148),(.065,.156,.153),(.018,.139,.153),(-.033,.119,.142),(-.082,.068,.122),(-.134,.005,.104)]
  for panel,(a,b) in enumerate([(0,3),(2,5),(4,7)]):
   rr=stations[a:b+1];vs=[]
   for j,(y,z,x) in enumerate(rr):
    for u in [0,.12,.42,.76,1]:
     vs.append((side*(x+.012*math.sin(math.pi*u)-.004*u),y-.008*u,z-.020*u-.005*math.sin(math.pi*u)+.004*panel))
   fs=[(j*5+k,(j+1)*5+k,(j+1)*5+k+1,j*5+k+1) for j in range(len(rr)-1) for k in range(4)]
   if side==1:fs=[tuple(reversed(f)) for f in fs]
   mesh('CGH17 broad curved brow course '+label+' '+str(panel),vs,fs,rr,True)
 bpy.context.view_layer.update()
 return {'hidden_originals':hidden,'new_objects':[o.name for o in made],'attempt':2,'receiving_materials':[m.name for m in materials],'no_pose_change':True,'retained_posterior_06':28,'source_interpretation':'Broad swept overlapping top courses with real curved shoulder returns and segmented broad brow panels, retaining06 posterior layers. NoHEAD15 geometry; depth is proposal; whole-character gain requires independent review.'}

import numpy as np
def val(x):
 if isinstance(x,(str,int,float,bool,type(None))):return x
 if hasattr(x,'name'):return {'id_name':x.name}
 if hasattr(x,'to_dict'):return x.to_dict()
 if hasattr(x,'to_list'):return x.to_list()
 try:return [val(v) for v in x]
 except:return str(x)
def properties(x):return {k:val(v) for k,v in sorted(x.items())}
def rna(x):
 r={}
 for p in x.bl_rna.properties:
  if not p.is_readonly and p.identifier not in ['rna_type','name']:
   try:r[p.identifier]=val(getattr(x,p.identifier))
   except:pass
 return r
def digest(o):
 h=hashlib.sha256();h.update(repr([o.type,val(o.matrix_world),val(o.matrix_local),o.parent.name if o.parent else None,properties(o),[(m.name,m.type,rna(m)) for m in o.modifiers]]).encode())
 if o.type=='MESH':
  m=o.data;h.update(repr([properties(m),[s.name if s else None for s in m.materials],[(tuple(f.vertices),f.material_index,f.use_smooth) for f in m.polygons],[(tuple(e.vertices),e.use_edge_sharp) for e in m.edges]]).encode())
  a=np.empty(len(m.vertices)*3,dtype=np.float32);m.vertices.foreach_get('co',a);h.update(a.tobytes())
  for a in m.attributes:
   h.update(repr([a.name,a.domain,a.data_type]).encode());field={'FLOAT':'value','INT':'value','BOOLEAN':'value','FLOAT_VECTOR':'vector','FLOAT_COLOR':'color','BYTE_COLOR':'color','FLOAT2':'vector'}.get(a.data_type)
   if field:h.update(repr([val(getattr(d,field)) for d in a.data]).encode())
 return h.hexdigest()
def snap():
 s=bpy.context.scene
 return {'objects':{o.name:digest(o) for o in s.objects if o.type in ['MESH','EMPTY']},'images':{i.name:{'file':i.filepath,'size':list(i.size),'source':i.source,'colorspace':i.colorspace_settings.name,'props':properties(i),'fake_user':i.use_fake_user,'packed':hashlib.sha256(bytes(i.packed_file.data)).hexdigest() if i.packed_file else None} for i in bpy.data.images},'materials':{m.name:hashlib.sha256(repr([properties(m),m.diffuse_color[:],m.use_nodes,[(n.name,n.type,[(i.name,val(i.default_value)) for i in n.inputs if hasattr(i,'default_value')],n.image.name if n.type=='TEX_IMAGE' and n.image else None,properties(n)) for n in m.node_tree.nodes] if m.use_nodes else [],[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links] if m.use_nodes else []]).encode()).hexdigest() for m in bpy.data.materials},'visibility':{o.name:[o.hide_render,o.hide_get()] for o in s.objects if o.type in ['MESH','EMPTY']}}
def run():
 attempt=2
 if sys.argv[-1].isdigit() and int(sys.argv[-1])!=2:raise ValueError('FinalAPI reproduces02 only; immutable01 API is in audit/attempt01')
 out=ROOT/'assets/audit/cg-supervised-head17'/('attempt%02d'%attempt);out.mkdir(parents=True,exist_ok=True);assert sha(INPUT)==EXPECTED
 bpy.ops.wm.open_mainfile(filepath=str(INPUT));before=snap();scene=bpy.context.scene
 preserve=modload(BASE/'scripts/cg-supervised-preservation.py');maps=preserve.packed_image_snapshot();preserve.retain_packed_image_ids(scene)
 report=apply(scene,ROOT,era='builder');report.update(input_sha256=EXPECTED,root_goal_sha256=sha(BASE/'goal.md'),root_goal_last_updated='2026-10-04T04:26:19.270994+00:00',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 native=out/'layered-head17.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),relative_remap=False);bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene;after=snap()
 report['early_preservation']={'objects':len(before['objects']),'materials':len(before['materials']),'image_ids':len(before['images']),'packed':preserve.verify_receiving_images(maps),'payload_changes':[n for n,h in before['objects'].items() if after['objects'].get(n)!=h],'material_changes':[n for n,h in before['materials'].items() if after['materials'].get(n)!=h],'image_changes':[n for n,h in before['images'].items() if h['source']=='FILE' and after['images'].get(n)!=h],'file_image_ids':sum(h['source']=='FILE' for h in before['images'].values()),'transient_viewer_ids':[n for n,h in before['images'].items() if h['source']=='VIEWER' and after['images'].get(n)!=h]}
 assert not any(report['early_preservation'][k] for k in ['payload_changes','material_changes','image_changes'])
 (out/'receipt.json').write_text(json.dumps(report,indent=2));print('HEAD17_EARLY_PRESERVATION',report['early_preservation'],flush=True)
 reference=json.loads((BASE/'assets/audit/cg-supervised-head13/attempt02/receipt.json').read_text());report['cameras']={};report['mesh_checks']=[]
 for n in report['new_objects']:
  o=scene.objects[n];e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();uv=[v for d in m.uv_layers.active.data for v in d.uv];report['mesh_checks'].append({'name':n,'cage_vertices':len(o.data.vertices),'evaluated_vertices':len(m.vertices),'finite':all(math.isfinite(v) for q in m.vertices for v in q.co) and all(math.isfinite(v) for v in uv),'uv_range':[min(uv),max(uv)]});e.to_mesh_clear()
 camera=scene.camera;scene.render.engine='CYCLES';scene.cycles.samples=4;scene.cycles.use_denoising=True;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 clay=bpy.data.materials.new('CGH17 diagnostic clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.42,.42,.42,1);bs.inputs['Roughness'].default_value=.75
 def render(view,mode):
  key='after-'+mode+'-'+view;rc=reference['cameras'][key];camera.matrix_world=Matrix(rc['matrix']);camera.data.ortho_scale=rc['scale'];camera.data.shift_x,camera.data.shift_y=rc['shift'];scene.render.resolution_x,scene.render.resolution_y=rc['resolution'];scene.view_layers[0].material_override=clay if mode=='clay' else None;scene.render.filepath=str(out/(key+'.png'));bpy.context.view_layer.update();report['cameras'][key]=rc;bpy.ops.render.render(write_still=True);(out/'receipt.json').write_text(json.dumps(report,indent=2));print('HEAD17_RENDERED',key,flush=True)
 views=['source-full-bird','head-profile','head-grazing','head-far-profile','head-front']
 for v in views[:2]:
  render(v,'clay');render(v,'pbr')
 print('HEAD17_FIRST_PAIR_COMPLETE',flush=True)
 for v in views[2:]:
  render(v,'clay');render(v,'pbr')
 scene.view_layers[0].material_override=None
 # Keep exact camera35 in the editable saved native.
 rc=reference['cameras']['after-pbr-source-full-bird'];camera.matrix_world=Matrix(rc['matrix']);camera.data.ortho_scale=rc['scale'];camera.data.shift_x,camera.data.shift_y=rc['shift'];scene.render.resolution_x,scene.render.resolution_y=rc['resolution'];bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(native),relative_remap=False)
 report['native_sha256']=sha(native);report['image_hashes']={p.name:sha(p) for p in out.glob('*.png')};(out/'receipt.json').write_text(json.dumps(report,indent=2));print('HEAD17_COMPLETE',flush=True)
if __name__=='__main__':run()
