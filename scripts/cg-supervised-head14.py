"""HEAD14 source-formed cranial exterior, deterministic from immutable06.
HEAD13 is retained hidden as authoring scaffold, never the rendered cap.
No owner acceptance, continuous lens proof, or source-depth metrology.
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
 sp=importlib.util.spec_from_file_location('h14_'+path.stem,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def apply(scene,root_path=None,era='builder',attempt=2):
 if any(o.get('cgSupervisedHead14') for o in scene.objects):raise RuntimeError('Reload immutable06 before apply14')
 root=Path(root_path) if root_path else ROOT
 guide=modload(root/'scripts/cg-supervised-head13.py');guide.ROOT=root
 gr=guide.apply(scene,root,era,attempt=2)
 frame=scene.objects['CG2b head frame'].matrix_world.copy();made=[]
 materials=list(scene.objects['CGH06 swept overlapping dorsal brow plate L0'].data.materials)
 for n in gr['new_objects']:
  o=scene.objects[n];o.hide_render=True;o.hide_set(True);o['cgAuthoringGuide']=True;o['authoringGuide']=True
 crest=scene.objects['CGH13 physical posterior crest cage'];c=[Vector(v.co) for v in crest.data.vertices]
 def mesh(name,vs,fs,controls):
  d=bpy.data.meshes.new(name);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.matrix_world=frame
  o['cgSupervisedHead14']=True;o['cg1cRegion']='head';o['cg2bRegion']='head';o['cgSurfaceFamilies']='["head-armor","black-iron","worn-bronze"]';o['surfaceRole']='head-armor';o['constructionStatus']='Source-inspired overlapping thin formed roof; unseen depth proposal; owner likeness pending';o['cageControls']=json.dumps(controls)
  for m in materials:d.materials.append(m)
  uv=d.uv_layers.new(name='head14-normalized-local');lo=[min(v.co[a] for v in d.vertices) for a in (1,2)];hi=[max(v.co[a] for v in d.vertices) for a in (1,2)]
  for f in d.polygons:
   f.use_smooth=True
   for li in f.loop_indices:
    q=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=((q.y-lo[0])/max(hi[0]-lo[0],1e-5),(q.z-lo[1])/max(hi[1]-lo[1],1e-5))
  sub=o.modifiers.new('editable sparse formed sheet','SUBSURF');sub.levels=sub.render_levels=2
  so=o.modifiers.new('thin inward dark sidewall','SOLIDIFY');so.thickness=.0020;so.offset=-1;so.material_offset=1;so.material_offset_rim=1
  made.append(o);return o
 def roof(name,inds,offset,narrow=1):
  vs=[]
  for j,idx in enumerate(inds):
   # Five coupled cross-rails from the solved posterior/forward guide. Ends
   # taper unequally in depth and longitudinally, avoiding a transverse visor.
   for k,ring in enumerate((6,7,0,1,2)):
    q=c[idx*8+ring].copy();q.x=c[idx*8].x+(q.x-c[idx*8].x)*narrow;q.z+=offset
    if j==0:q.y+=.008*(1 if k in (0,4) else -.3);q.z-=.002*abs(k-2)
    if j==len(inds)-1:q.y-=.004*(1 if k in (0,4) else 0)
    vs.append(q)
  fs=[(j*5+k,j*5+k+1,(j+1)*5+k+1,(j+1)*5+k) for j in range(len(inds)-1) for k in range(4)]
  return mesh(name,vs,fs,{'guide_stations':inds,'lift':offset,'width_scale':narrow})
 roof('CGH14 swept posterior crown origin',([1,2,3,4,5,6] if attempt==1 else [2,3,4,5,6]),.0008,.97)
 roof('CGH14 overlapping orbital cranial roof',[4,5,6,7,8,9,10],.0030,.98)
 roof('CGH14 formed bill root hood',[8,9,10,11,12,13],.0050,1.04)
 # Formed local brow lips, rather than full length thin parallel rails.
 for side,label in [(-1,'near'),(1,'far')]:
  rows=[]
  for i in ([4,5,6,7,8,9,10,11] if attempt==1 else [5,6,7,8,9,10,11]):
   edge=c[i*8+(6 if side<0 else 2)].copy();center=c[i*8].copy()
   inner=edge.lerp(center,.19);inner.z+=.002
   outer=edge.copy();outer.x+=side*.011;outer.z-=.007 if side<0 else .009
   # Edge follows the head roof, but is inset medial to original optic seat.
   fold=outer.copy();fold.x-=side*.002;fold.z-=.003
   rows.append([inner,edge+Vector((0,0,.001)),outer,fold])
  vs=[v for r in rows for v in r];fs=[(j*4+k,j*4+k+1,(j+1)*4+k+1,(j+1)*4+k) for j in range(len(rows)-1) for k in range(3)]
  mesh('CGH14 localized turned brow lip '+label,vs,fs,{'guide_station_span':[4,11],'side':side,'medial_to_optic':True})
  if attempt==2:
   # One swept posterior roof return per side joins the upper roof to the
   # rear cheek root. Variable edge width and a tapered broken end are a
   # macro source-formed course, not an array of cards or fastener detail.
   p=guide.p;return_rows=[(708,133,.128,8),(692,143,.135,14),(674,161,.143,17),(652,184,.139,18),(631,209,.128,12),(612,234,.113,2)]
   rv=[]
   for x,y,d,w in return_rows:
    for u in [-1,-.5,0,.5,1]:rv.append(p(x+u*w*.60,y+u*w,side*(d+.003*(1-u*u))))
   rf=[(j*5+k,j*5+k+1,(j+1)*5+k+1,(j+1)*5+k) for j in range(len(return_rows)-1) for k in range(4)]
   mesh('CGH14 tapered posterior roof cheek return '+label,rv,rf,return_rows)
  # Existing06 cheek is kept; a short hood return overlaps its bill-root end,
  # framing the retained jaw opening instead of filling it.
  p=guide.p;stations=[(865,194,.116,8),(884,215,.109,11),(903,239,.098,12),(916,256,.090,7)]
  vs=[]
  for x,y,d,w in stations:
   for u in [-1,0,1]:vs.append(p(x+2*u,y+w*u,side*(d+.002*(1-u*u))))
  fs=[(j*3+k,j*3+k+1,(j+1)*3+k+1,(j+1)*3+k) for j in range(3) for k in range(2)]
  mesh('CGH14 bill root cheek return '+label,vs,fs,stations)
 bpy.context.view_layer.update()
 return {'hidden_originals':gr['hidden_originals'],'hidden_authoring_guides':gr['new_objects'],'new_objects':[o.name for o in made],'guide_report':gr,'attempt':attempt,'receiving_materials':[m.name for m in materials],'no_pose_change':True,'source_interpretation':'Roof uses upper guide envelope only; no posterior full-depth fin. Unequal overlapping roof courses follow posterior crest through orbital rim into retained bill, short returns meet existing cheek. Unseen depth and exact plate layout proposal.'}

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
 out=ROOT/'assets/audit/cg-supervised-head14'/('attempt%02d'%attempt);out.mkdir(parents=True,exist_ok=True);assert sha(INPUT)==EXPECTED
 bpy.ops.wm.open_mainfile(filepath=str(INPUT));before=snap();scene=bpy.context.scene
 preserve=modload(BASE/'scripts/cg-supervised-preservation.py');maps=preserve.packed_image_snapshot();preserve.retain_packed_image_ids(scene)
 report=apply(scene,ROOT,attempt=attempt);report.update(input_sha256=EXPECTED,shared_main_sha='251f2f0243181e97140179c2aff6eb057e165438',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 native=out/'formed-head14.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),relative_remap=False);bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene;after=snap()
 report['early_preservation']={'objects':len(before['objects']),'materials':len(before['materials']),'image_ids':len(before['images']),'packed':preserve.verify_receiving_images(maps),'payload_changes':[n for n,h in before['objects'].items() if after['objects'].get(n)!=h],'material_changes':[n for n,h in before['materials'].items() if after['materials'].get(n)!=h],'image_changes':[n for n,h in before['images'].items() if h['source']=='FILE' and after['images'].get(n)!=h],'file_image_ids':sum(h['source']=='FILE' for h in before['images'].values()),'transient_viewer_ids':[n for n,h in before['images'].items() if h['source']=='VIEWER' and after['images'].get(n)!=h]}
 assert not any(report['early_preservation'][k] for k in ['payload_changes','material_changes','image_changes'])
 (out/'receipt.json').write_text(json.dumps(report,indent=2));print('HEAD14_EARLY_PRESERVATION',report['early_preservation'],flush=True)
 reference=json.loads((ROOT/'assets/audit/cg-supervised-head13/attempt02/receipt.json').read_text());report['cameras']={};report['mesh_checks']=[]
 for n in report['new_objects']:
  o=scene.objects[n];e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();uv=[v for d in m.uv_layers.active.data for v in d.uv];report['mesh_checks'].append({'name':n,'cage_vertices':len(o.data.vertices),'evaluated_vertices':len(m.vertices),'finite':all(math.isfinite(v) for q in m.vertices for v in q.co) and all(math.isfinite(v) for v in uv),'uv_range':[min(uv),max(uv)]});e.to_mesh_clear()
 camera=scene.camera;scene.render.engine='CYCLES';scene.cycles.samples=8;scene.cycles.use_denoising=True;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 clay=bpy.data.materials.new('CGH14 diagnostic clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.42,.42,.42,1);bs.inputs['Roughness'].default_value=.75
 def render(view,mode):
  key='after-'+mode+'-'+view;rc=reference['cameras'][key];camera.matrix_world=Matrix(rc['matrix']);camera.data.ortho_scale=rc['scale'];camera.data.shift_x,camera.data.shift_y=rc['shift'];scene.render.resolution_x,scene.render.resolution_y=rc['resolution'];scene.view_layers[0].material_override=clay if mode=='clay' else None;scene.render.filepath=str(out/(key+'.png'));bpy.context.view_layer.update();report['cameras'][key]=rc;bpy.ops.render.render(write_still=True);(out/'receipt.json').write_text(json.dumps(report,indent=2));print('HEAD14_RENDERED',key,flush=True)
 views=['source-full-bird','head-profile','head-grazing','head-far-profile','head-front']
 for v in views:
  render(v,'clay')
  if v=='head-profile':print('HEAD14_FIRST_PAIR_COMPLETE',flush=True)
 for v in views:render(v,'pbr')
 scene.view_layers[0].material_override=None
 # Keep exact camera35 in the editable saved native.
 rc=reference['cameras']['after-pbr-source-full-bird'];camera.matrix_world=Matrix(rc['matrix']);camera.data.ortho_scale=rc['scale'];camera.data.shift_x,camera.data.shift_y=rc['shift'];scene.render.resolution_x,scene.render.resolution_y=rc['resolution'];bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(native),relative_remap=False)
 report['native_sha256']=sha(native);report['image_hashes']={p.name:sha(p) for p in out.glob('*.png')};(out/'receipt.json').write_text(json.dumps(report,indent=2));print('HEAD14_COMPLETE',flush=True)
if __name__=='__main__':run()
