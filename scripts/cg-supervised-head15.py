"""HEAD15 compact connected posterior envelope and independent swept crest blades.
Fresh source-inspired cages from immutable06. Source depth remains proposal.
"""
import bpy,json,math,hashlib,sys,importlib.util,datetime
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
INPUT=BASE/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend'
EXPECTED='72e7e53daf40b7128cdf9b173006c639bcf123952547a2576fb2de29130f06d4'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def modload(path):
 sp=importlib.util.spec_from_file_location('h15_'+path.stem,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def apply(scene,root_path=None,era='builder',attempt=2):
 if any(o.get('cgSupervisedHead15') for o in scene.objects):raise RuntimeError('Reload immutable06 before apply15')
 frame=scene.objects['CG2b head frame'].matrix_world.copy();made=[];hidden=[]
 materials=list(scene.objects['CGH06 swept overlapping dorsal brow plate L0'].data.materials)
 for o in list(scene.objects):
  if o.hide_render:continue
  if (o.get('cgSupervisedHead05') and 'curved recessed vault' in o.name) or (o.get('cgSupervisedHead06') and any(k in o.name for k in ['dorsal brow','bill saddle','crown sheet','dorsal sheet','frontal saddle'])):
   hidden.append(o.name);o.hide_render=True;o.hide_set(True)
 def mesh(name,vs,fs,controls,sub=True):
  d=bpy.data.meshes.new(name);d.from_pydata(vs,[],[tuple(reversed(f)) for f in fs]);d.update();o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.matrix_world=frame
  o['cgSupervisedHead15']=True;o['cg1cRegion']='head';o['cg2bRegion']='head';o['cgSurfaceFamilies']='["head-armor","black-iron","worn-bronze"]';o['surfaceRole']='head-armor';o['constructionStatus']='Fresh compact connected cranial envelope; independent swept blade; unknown source depth proposal';o['cageControls']=json.dumps(controls)
  for m in materials:d.materials.append(m)
  uv=d.uv_layers.new(name='head15-normalized-local');lo=[min(v.co[a] for v in d.vertices) for a in (1,2)];hi=[max(v.co[a] for v in d.vertices) for a in (1,2)]
  for f in d.polygons:
   f.use_smooth=True
   for li in f.loop_indices:
    q=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=((q.y-lo[0])/max(hi[0]-lo[0],1e-5),(q.z-lo[1])/max(hi[1]-lo[1],1e-5))
  if sub:
   sm=o.modifiers.new('sparse formed cranial cage','SUBSURF');sm.levels=sm.render_levels=2
  so=o.modifiers.new('inward thin formed metal dark edges','SOLIDIFY');so.thickness=.002;so.offset=-1;so.material_offset=1;so.material_offset_rim=1
  made.append(o);return o
 # Connected posterior shell has actual side depth, ending behind optic. Roof
 # then narrows into brow and bill-root hood. No old vault/guide deformation.
 rows=[(.200,.073,-.014,.065),(.180,.103,-.060,.108),(.150,.121,-.081,.126),(.120,.130,-.091,.137),(.092,.121,-.078,.143),(.073,.111,-.046,.144),(.059,.106,.079,.144),(.030,.102,.091,.143),(.000,.095,.085,.139),(-.030,.077,.064,.132),(-.060,.055,.039,.121),(-.092,.032,.009,.108),(-.124,.011,-.014,.092)]
 if attempt==2:rows.extend([(-.142,-.014,-.041,.087),(-.158,-.046,-.065,.078)])
 vs=[]
 for y,top,bottom,w in rows:
  # Nine rails explicitly connect rear sidewalls to the same roof cage.
  for u,zf in [(-1,0),(-1,.30),(-.94,.72),(-.60,.95),(0,1),(.60,.92),(.94,.65),(1,.26),(1,0)]:
   z=bottom+(top-bottom)*zf
   if u>0:z-=.014*zf
   vs.append((u*w,y,z))
 fs=[(j*9+k,j*9+k+1,(j+1)*9+k+1,(j+1)*9+k) for j in range(len(rows)-1) for k in range(8)]
 if attempt==1:mesh('CGH15 continuous descending posterior cranial envelope',vs,fs,rows)
 else:
  for label,a,b,lift in [('descending rear cranial course',0,7,0),('overlapping orbital roof course',4,11,.0015),('overlapping bill root hood course',8,15,.0030)]:
   vv=[(x,y,z+lift) for x,y,z in vs[a*9:b*9]];ff=[(j*9+k,j*9+k+1,(j+1)*9+k+1,(j+1)*9+k) for j in range(b-a-1) for k in range(8)];mesh('CGH15 '+label,vv,ff,rows[a:b])
 # Local brow overlays continue to the bill root; their width changes so the
 # orbital rim remains a recessed circular landmark rather than a long shelf.
 for side,label in [(-1,'near'),(1,'far')]:
  brow=[(.087,.104,.139,.010),(.060,.106,.144,.014),(.030,.103,.146,.014),(.000,.095,.141,.012),(-.030,.078,.133,.010),(-.060,.055,.123,.009),(-.093,.028,.108,.008),(-.122,.004,.094,.004)]
  if attempt==2:brow.extend([(-.141,-.022,.088,.003),(-.155,-.052,.080,.001)])
  vs=[]
  for y,z,d,w in brow:
   z-=.014 if side>0 else 0
   for u in [-1,0,1]:vs.append((side*(d+u*w*.28),y+u*w*.55,z-u*w*.65))
  fs=[(j*3+k,j*3+k+1,(j+1)*3+k+1,(j+1)*3+k) for j in range(len(brow)-1) for k in range(2)]
  mesh('CGH15 localized orbital brow and root return '+label,vs,fs,brow)
 # Separate formed crest blade, full width tapers toward the actual apex.
 # Both are welded surfaces anchored along posterior roof, not floating pivots.
 near=[(-.156244924,.163848178,.186432607,.0002),(-.150,.152,.176,.008),(-.141,.129,.153,.013),(-.132,.105,.129,.017),(-.123,.080,.111,.020),(-.120,.055,.102,.015),(-.119,.044,.098,.004)]
 far=[(.105,.105,.120,.0002),(.107,.099,.117,.006),(.109,.087,.110,.012),(.111,.066,.101,.017),(.115,.043,.094,.015),(.117,.021,.087,.005)]
 for label,rr in [('near',near),('far',far)]:
  if attempt==1:
   vs=[]
   for x,y,z,w in rr:
    for u in [-1,0,1]:vs.append((x+u*w,y-abs(u)*w*.18,z-abs(u)*w*.35))
   fs=[(j*3+k,j*3+k+1,(j+1)*3+k+1,(j+1)*3+k) for j in range(len(rr)-1) for k in range(2)]
  else:
   vs=[rr[0][:3]]
   for x,y,z,w in rr[1:]:
    for u in [-1,0,1]:vs.append((x+u*w*.55,y-abs(u)*w*.18,z-(u+1)*w*.60))
   fs=[(0,2,1),(0,3,2)]+[(1+j*3+k,1+j*3+k+1,1+(j+1)*3+k+1,1+(j+1)*3+k) for j in range(len(rr)-2) for k in range(2)]
  mesh('CGH15 independent swept crest blade '+label,vs,fs,rr,False)
 bpy.context.view_layer.update()
 return {'hidden_originals':hidden,'new_objects':[o.name for o in made],'attempt':attempt,'receiving_materials':[m.name for m in materials],'no_pose_change':True,'source_interpretation':'Fresh connected posterior roof and descending sides, local brow/root hood, independently swept near/far blades. Side depth and asymmetry are proposals; numeric point fit is not likeness.'}

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
 attempt=int(sys.argv[-1]) if sys.argv[-1].isdigit() else 2
 out=ROOT/'assets/audit/cg-supervised-head15'/('attempt%02d'%attempt);out.mkdir(parents=True,exist_ok=True);assert sha(INPUT)==EXPECTED
 bpy.ops.wm.open_mainfile(filepath=str(INPUT));before=snap();scene=bpy.context.scene
 preserve=modload(BASE/'scripts/cg-supervised-preservation.py');maps=preserve.packed_image_snapshot();preserve.retain_packed_image_ids(scene)
 report=apply(scene,ROOT,attempt=attempt);report.update(input_sha256=EXPECTED,shared_main_sha='251f2f0243181e97140179c2aff6eb057e165438',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 native=out/'localized-head15.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),relative_remap=False);bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene;after=snap()
 report['early_preservation']={'objects':len(before['objects']),'materials':len(before['materials']),'image_ids':len(before['images']),'packed':preserve.verify_receiving_images(maps),'payload_changes':[n for n,h in before['objects'].items() if after['objects'].get(n)!=h],'material_changes':[n for n,h in before['materials'].items() if after['materials'].get(n)!=h],'image_changes':[n for n,h in before['images'].items() if h['source']=='FILE' and after['images'].get(n)!=h],'file_image_ids':sum(h['source']=='FILE' for h in before['images'].values()),'transient_viewer_ids':[n for n,h in before['images'].items() if h['source']=='VIEWER' and after['images'].get(n)!=h]}
 assert not any(report['early_preservation'][k] for k in ['payload_changes','material_changes','image_changes'])
 (out/'receipt.json').write_text(json.dumps(report,indent=2));print('HEAD15_EARLY_PRESERVATION',report['early_preservation'],flush=True)
 reference=json.loads((BASE/'assets/audit/cg-supervised-head13/attempt02/receipt.json').read_text());report['cameras']={};report['mesh_checks']=[]
 for n in report['new_objects']:
  o=scene.objects[n];e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();uv=[v for d in m.uv_layers.active.data for v in d.uv];report['mesh_checks'].append({'name':n,'cage_vertices':len(o.data.vertices),'evaluated_vertices':len(m.vertices),'finite':all(math.isfinite(v) for q in m.vertices for v in q.co) and all(math.isfinite(v) for v in uv),'uv_range':[min(uv),max(uv)]});e.to_mesh_clear()
 camera=scene.camera;scene.render.engine='CYCLES';scene.cycles.samples=8;scene.cycles.use_denoising=True;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 clay=bpy.data.materials.new('CGH15 diagnostic clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.42,.42,.42,1);bs.inputs['Roughness'].default_value=.75
 def render(view,mode):
  key='after-'+mode+'-'+view;rc=reference['cameras'][key];camera.matrix_world=Matrix(rc['matrix']);camera.data.ortho_scale=rc['scale'];camera.data.shift_x,camera.data.shift_y=rc['shift'];scene.render.resolution_x,scene.render.resolution_y=rc['resolution'];scene.view_layers[0].material_override=clay if mode=='clay' else None;scene.render.filepath=str(out/(key+'.png'));bpy.context.view_layer.update();report['cameras'][key]=rc;bpy.ops.render.render(write_still=True);(out/'receipt.json').write_text(json.dumps(report,indent=2));print('HEAD15_RENDERED',key,flush=True)
 views=['source-full-bird','head-profile','head-grazing','head-far-profile','head-front']
 for v in views[:2]:
  render(v,'clay');render(v,'pbr')
 print('HEAD15_FIRST_PAIR_COMPLETE',flush=True)
 for v in views[2:]:
  render(v,'clay');render(v,'pbr')
 scene.view_layers[0].material_override=None
 # Keep exact camera35 in the editable saved native.
 rc=reference['cameras']['after-pbr-source-full-bird'];camera.matrix_world=Matrix(rc['matrix']);camera.data.ortho_scale=rc['scale'];camera.data.shift_x,camera.data.shift_y=rc['shift'];scene.render.resolution_x,scene.render.resolution_y=rc['resolution'];bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(native),relative_remap=False)
 report['native_sha256']=sha(native);report['image_hashes']={p.name:sha(p) for p in out.glob('*.png')};(out/'receipt.json').write_text(json.dumps(report,indent=2));print('HEAD15_COMPLETE',flush=True)
if __name__=='__main__':run()
