"""Fitted layered cranial/orbital enclosure on exact retained delivery02.

Import is inert. No receiving payload, graph, image or rig is edited. Only the
37 explicitly listed visible surfaces are retired. Source depth is a CG proposal.
"""
import bpy,json,math,hashlib,importlib.util,datetime,sys,argparse
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
DESIGN=1
MANIFEST_SHA='47ed3ee74f0a06a9c470a427f8151dd032b0b48e1c68083f50d092cd1ec3308f'
RECEIVING={'builder':('assets/audit/cg-recursive-three-loop01/loop01/delivery/retained02/builder/murderbird-recursive-builder.blend','7539b8968f9e82cc8c1dfb569203bd60b134ba841871b99bf67124552fd7004d'),'maker':('assets/audit/cg-recursive-three-loop01/loop01/delivery/retained02/maker/murderbird-recursive-maker.blend','9ec2eddc423fd7e6bb3d6b52ea68dd22ea66533b6a521160c3529968b269754f'),'mechanic':('assets/audit/cg-recursive-three-loop01/loop01/delivery/retained02/mechanic/murderbird-recursive-mechanic.blend','ed5e74e8094f394fa37afb79263c5cbba05894db3f085ec72f3ff4d07c173ccf')}
RETIRE=tuple(['CGH06 '+part+' '+side+suffix for side in ('L','R') for part,suffixes in [('connected under-eye bill-root cheek sheet',['']),('recessed cheek lower plated mechanism',['']),('substantial swept plated mandible',['']),('nested dark jaw upper folded plate',['']),('interleaved jaw face panel',['0','1','2']),('thin orbital cheek sheet',['0','1','2','3','4'])] for suffix in suffixes]+['CGH17 posterior swept crest','CGH17 middle overlapping crest','CGH17 frontal crown root']+['CGH17 broad curved brow course '+side+' '+str(i) for side in ('near','far') for i in range(3)]+['CGH18 formed dorsal bill root cuff','CGH18 formed distal hooked bill plate','CGH18 compact posterior bill root return L','CGH18 compact posterior bill root return R'])
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(path):
 sp=importlib.util.spec_from_file_location(path.stem.replace('-','_'),path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def apply(scene,root_path,era='builder'):
 if root_path is None:raise ValueError('Explicit receiving root required')
 if era=='advanced':era='builder'
 if era not in RECEIVING:raise ValueError(era)
 if any(o.get('cgRecursiveHead02') for o in scene.objects):raise RuntimeError('Reload exact delivery02 before applying')
 assert len(RETIRE)==37
 for name in RETIRE:
  o=scene.objects.get(name)
  if not o or o.hide_render or o.hide_get():raise RuntimeError('Expected actual visible contributor '+name)
 frame=scene.objects['CG2b head frame'].matrix_world.copy();made=[]
 src=scene.objects['CGH17 frontal crown root'];mats={r:src.data.materials[i] for i,r in enumerate(['head-armor','black-iron','worn-bronze'])};mats['machined-steel']=scene.objects['CGH18 formed distal hooked bill plate'].data.materials[0]
 assert all(m.get('cgMetal05Era')==era for m in mats.values())
 def p(x,y,d):return Vector((d,(788-x)*.0012+.005,(188-y)*.0012+.020))
 def mesh(label,vs,fs,role='head-armor',stock=.002):
  name='CGRH02 '+label;d=bpy.data.meshes.new(name);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.matrix_world=frame.copy()
  for r in (role,'black-iron','worn-bronze'):d.materials.append(mats[r])
  for k,v in dict(cgRecursiveHead02=True,cg1cRegion='head',cg2bRegion='head',surfaceRole=role,cgSurfaceFamilies=json.dumps([role,'black-iron','worn-bronze']),exteriorEras='maker,mechanic,builder',constructionStatus='Fitted source-contour cranial/orbital enclosure; hidden depths proposed; likeness pending').items():o[k]=v
  uv=d.uv_layers.new(name='head02-local-normalized');lo=[min(v.co[a] for v in d.vertices) for a in (1,2)];hi=[max(v.co[a] for v in d.vertices) for a in (1,2)]
  for f in d.polygons:
   f.use_smooth=True
   for li in f.loop_indices:
    q=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=((q.y-lo[0])/max(hi[0]-lo[0],1e-6),(q.z-lo[1])/max(hi[1]-lo[1],1e-6))
  if stock:
   so=o.modifiers.new('inward formed metal lip','SOLIDIFY');so.thickness=stock;so.offset=-1;so.material_offset=1;so.material_offset_rim=2
  b=o.modifiers.new('formed edge chamfer','BEVEL');b.width=.0004;b.segments=2
  made.append(o);return o
 def spline(rr,n=5):
  ss=[]
  for i in range(len(rr)-1):
   a,b,c,d=rr[max(0,i-1)],rr[i],rr[i+1],rr[min(len(rr)-1,i+2)]
   for j in range(n):
    t=j/n;ss.append([.5*(2*bb+(-aa+cc)*t+(2*aa-5*bb+4*cc-dd)*t*t+(-aa+3*bb-3*cc+dd)*t**3) for aa,bb,cc,dd in zip(a,b,c,d)])
  return ss+[rr[-1]]
 def plate(label,rr,side,role='head-armor',camber=.006,stock=.0025):
  ss=spline(rr,5);n=13;vs=[]
  for ax,ay,ad,bx,by,bd in ss:
   for k in range(n):
    u=k/(n-1);vs.append(p(ax*(1-u)+bx*u,ay*(1-u)+by*u,side*(ad*(1-u)+bd*u+camber*math.sin(math.pi*u))))
  fs=[(j*n+k,j*n+k+1,(j+1)*n+k+1,(j+1)*n+k) for j in range(len(ss)-1) for k in range(n-1)]
  if side<0:fs=[tuple(reversed(f)) for f in fs]
  o=mesh(label,vs,fs,role,stock);o['pairedSourceContourControls']=json.dumps(rr);return o
 # Curved skull sections taper from posterior feather roots toward bill saddle.
 # There is no single broad forward roof. Unequal courses are cut around the
 # unchanged recessed optic aperture before any crown/cheek/brow is layered.
 sections=spline([(576,161,41,.044),(620,146,68,.086),(672,137,87,.132),(724,140,89,.149),(777,154,78,.147),(827,169,57,.135),(865,191,38,.108),(892,211,22,.083)],5)
 def sec(x):
  for aa,bb in zip(sections,sections[1:]):
   if x<=bb[0]:
    t=max(0,min(1,(x-aa[0])/(bb[0]-aa[0])));return [aa[k]+(bb[k]-aa[k])*t for k in [1,2,3]]
  return sections[-1][1:]
 # Crown panels follow asymmetric tapered contour courses on the enclosing
 # curved envelope. The hole is geometrically absent, exposing retained seat.
 for row,(start,end) in enumerate([(883,777),(836,705),(775,638),(707,570)]):
  for col in range(7):
   a0=-math.pi/2+col*math.pi/7-.08;a1=a0+math.pi/7+.13;nu,nv=11,23;vs=[];coords=[]
   for j in range(nv):
    t=j/(nv-1);xx=start+(end-start)*t+7*math.sin(math.pi*t+col*.7);cy,rad,w=sec(xx)
    for k in range(nu):
     u=k/(nu-1);width=max(.055,1-.62*t**2);ang=(a0+a1)/2+(u-.5)*(a1-a0)*width+.04*math.sin(math.pi*t)
     py=cy-rad*math.cos(ang);depth=w*math.sin(ang);lift=.0028+.005*(1-t)+.007*t**1.8
     vs.append(p(xx,py,depth+math.copysign(lift,depth or 1)));coords.append((xx,py,depth))
   fs=[]
   for j in range(nv-1):
    for k in range(nu-1):
     q=(j*nu+k,j*nu+k+1,(j+1)*nu+k+1,(j+1)*nu+k)
     # Delete any face crossing aperture in side quadrants; preserve optical
     # housing rather than laying a dome/slab across its visible opening.
     if any((x-788)**2+(y-188)**2<59**2 and abs(d)>.095 for x,y,d in [coords[z] for z in q]):continue
     fs.append(q)
   if fs:mesh('fitted cranial course %d-%d'%(row,col),vs,fs,stock=.0016)
 for side,label in [(-1,'L'),(1,'R')]:
  # A fitted continuous upper orbit shoulder fills the old disconnected ring
  # gap. This is curved into the skull and cheek, not a floating annular tube.
  plate('posterior fitted orbital enclosure '+label,[(658,121,.121,696,139,.155),(674,158,.136,726,155,.166),(675,196,.142,734,188,.174),(691,223,.144,746,226,.175),(721,246,.147,783,243,.173),(765,265,.147,821,252,.166),(815,269,.140,855,239,.151)],side,camber=.004)
  # Narrow source pale accent above optic; cheek/root never occludes it because
  # it is explicitly outboard of its enclosing dark support at these contours.
  plate('narrow scalloped supraoptic accent '+label,[(673,53,.105,678,72,.127),(714,69,.139,706,97,.163),(755,91,.161,743,117,.178),(795,116,.176,785,129,.181),(825,137,.174,832,164,.177),(847,156,.157,852,180,.165),(863,174,.137,871,184,.148)],side,'worn-bronze',.003,.0018)
  plate('curved bill-root orbital shoulder '+label,[(848,155,.143,856,180,.155),(870,177,.132,863,208,.153),(893,202,.117,875,231,.143),(921,232,.096,896,260,.124),(938,263,.077,919,284,.102)],side,'machined-steel',.006)
  # Broad two-contour cheek panels enclose a deliberate smaller recess and
  # overlap to the throat. Source void is retained as shaped negative space.
  plate('recessed posterior cheek bridge '+label,[(664,225,.134,696,211,.156),(680,250,.143,721,239,.162),(706,272,.145,753,258,.163),(731,294,.141,776,286,.157),(749,319,.131,791,321,.147)],side,camber=.004)
  jaw=[(695,259,.139,720,249,.161),(721,287,.143,750,273,.162),(753,318,.134,787,302,.151),(780,350,.117,811,340,.131),(803,383,.091,830,382,.101),(834,409,.054,855,413,.057),(868,422,.013,879,416,.010)]
  plate('nested formed lower mandible '+label,jaw,side,'head-armor',.005)
  plate('inset dark cheek cavity wall '+label,[(701,257,.119,734,248,.139),(731,285,.121,765,280,.140),(759,314,.110,794,316,.126),(783,349,.094,810,359,.109),(813,389,.064,839,401,.074),(861,421,.016,872,420,.018)],side,'black-iron',.002)
  # Short throat overlap remains above retained breast; no long new bib.
  plate('lower posterior cheek throat return '+label,[(678,254,.125,701,257,.143),(689,285,.125,723,300,.142),(706,315,.115,744,342,.131),(727,350,.103,753,372,.115)],side,camber=.004)
 # Bill is one coherent deep hook split into source shoulder/distal plates,
 # with an actual recessed root scallop, not cosmetic stripes on old bill.
 def shell(label,rr):
  ss=spline(rr,5);n=49;vs=[]
  for py,px,r,w in ss:
   for k in range(n):
    a=-math.pi+math.tau*k/(n-1);vs.append(p(px+r*math.cos(a),py,w*math.sin(a)))
  return mesh(label,vs,[(j*n+k,j*n+k+1,(j+1)*n+k+1,(j+1)*n+k) for j in range(len(ss)-1) for k in range(n-1)],'machined-steel',.002)
 shell('formed upper bill root',[(192,902,9,.066),(219,914,21,.094),(250,923,33,.103),(279,925,39,.090)])
 shell('continuous deep hooked distal bill',[(264,924,38,.098),(295,924,47,.083),(328,923,47,.063),(360,930,36,.044),(393,927,27,.029),(423,912,17,.014),(451,888,.9,.0013)])
 for side,label in [(-1,'L'),(1,'R')]:
  plate('recessed scalloped posterior bill shoulder '+label,[(902,238,.103,923,232,.085),(918,256,.103,943,249,.078),(908,280,.095,951,273,.065),(913,304,.082,954,300,.058),(928,324,.067,950,325,.048)],side,'machined-steel',.004)
  plate('bill notch inner wall '+label,[(903,246,.081,914,244,.095),(914,269,.078,927,266,.089),(907,287,.071,920,287,.083),(917,308,.061,933,310,.072)],side,'black-iron',.001,stock=.0014)
 hidden=[]
 for name in RETIRE:
  o=scene.objects[name];hidden.append({'name':name,'before':{'hide_render':o.hide_render,'hide_get':o.hide_get(),'hide_viewport':o.hide_viewport},'after':{'hide_render':True,'hide_get':True,'hide_viewport':o.hide_viewport}});o.hide_render=True;o.hide_set(True)
 bpy.context.view_layer.update()
 bounds=[o.matrix_world@v.co for o in made for v in o.data.vertices]
 return {'module':'cg-recursive-head02','design':DESIGN,'era':era,'new_objects':[o.name for o in made],'added_objects':[o.name for o in made],'hidden_originals':list(RETIRE),'visibility_overrides':hidden,'visibility_contract':'render hide + explicit per-view-layer hide_set; global hide_viewport unchanged','receiving_materials':{k:v.name for k,v in mats.items()},'world_bounds':{'min':[min(v[a] for v in bounds) for a in range(3)],'max':[max(v[a] for v in bounds) for a in range(3)]},'optics':'Receiving05/13 optical seat/core/era graphs unchanged','source_depth':'inferred','likeness_acceptance':'pending'}
def run():
 parser=argparse.ArgumentParser();parser.add_argument('--receiving-root',required=True);parser.add_argument('--era',default='builder',choices=list(RECEIVING));parser.add_argument('--whole-only',action='store_true');parser.add_argument('--api-only',action='store_true');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);base=Path(args.receiving_root);era=args.era
 manifest=base/'assets/audit/cg-recursive-three-loop01/loop02-preparation/receiving-manifest-loop02.json';assert sha(manifest)==MANIFEST_SHA
 rel,expected=RECEIVING[era];inp=base/rel;assert sha(inp)==expected
 out=ROOT/f'assets/audit/cg-recursive-head02/attempt{DESIGN:02d}/{era}';out.mkdir(parents=True,exist_ok=True);assets=ROOT/f'assets/models/cg-recursive-head02/attempt{DESIGN:02d}';assets.mkdir(parents=True,exist_ok=True)
 bpy.ops.wm.open_mainfile(filepath=str(inp));scene=bpy.context.scene;h=load(base/'scripts/cg-supervised-head17.py');pres=load(base/'scripts/cg-supervised-preservation.py');before=h.snap();images=pres.packed_image_snapshot();pres.retain_packed_image_ids(scene)
 assert len(before['objects'])==7644 and len(before['materials'])==62
 for n in RETIRE:assert scene.objects[n] and not scene.objects[n].hide_render and not scene.objects[n].hide_get()
 report={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input':rel,'input_sha256':expected,'manifest_sha256':MANIFEST_SHA,'goal_revision':'251f2f0243181e97140179c2aff6eb057e165438','design':DESIGN,'cameras':{},'authoring_sha256':sha(Path(__file__)),'receiving_census':{'mesh_empty':len(before['objects']),'materials':len(before['materials']),'packed_images':len(images)},'pre_apply_visible_manifest_count':len(RETIRE),'protected_anchor_names':['CG2b head frame','CGH05 integrated optical seat L','CGH05 integrated optical seat R'],'source_scopes':{'July':'head only','locked Sept22':'full bird','First Choice':'surface continuity retained; no new frame extraction'}}
 rc=json.loads((base/f'assets/audit/cg-supervised01/attempt09/{era}/receipt.json').read_text())['cameras'];cam=scene.camera
 def write():(out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
 def claymat():
  m=bpy.data.materials.new('CGRH02 disposable clay');m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.42,.42,.42,1);bs.inputs['Roughness'].default_value=.75;return m
 clay=claymat()
 def render(state,view,mode):
  r=rc[view];cam.location=r['location'];cam.rotation_euler=r['rotation_euler'];cam.data.type=r['projection'];cam.data.ortho_scale=r['ortho_scale'];cam.data.lens=r['lens_mm'];cam.data.shift_x,cam.data.shift_y=r['shift'];bg=scene.world.node_tree.nodes['Background'];bg.inputs[0].default_value=r['world_color'];bg.inputs[1].default_value=r['world_strength']
  lights=sorted([o for o in scene.objects if o.type=='LIGHT'],key=lambda o:o.name);assert len(lights)==len(r['areas'])
  for o,a in zip(lights,r['areas']):o.location=a['location'];o.rotation_euler=a['rotation_euler'];o.data.energy=a['power'];o.data.color=a['color'];o.data.size=a['size']
  scene.render.engine='CYCLES';scene.cycles.samples=4;scene.cycles.use_denoising=True;scene.render.image_settings.file_format='PNG';scene.render.resolution_x,scene.render.resolution_y=[round(v*.5) for v in r['resolution']];scene.render.resolution_percentage=100;scene.view_layers[0].material_override=clay if mode=='clay' else None
  scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=0;scene.view_settings.gamma=1
  key=state+'-'+view+'-'+mode;scene.render.filepath=str(out/(key+'.png'));bpy.context.view_layer.update();bpy.ops.render.render(write_still=True);report['cameras'][key]=dict(r,resolution=[scene.render.resolution_x,scene.render.resolution_y],samples=4);write();print('HEAD02_RENDERED',key,flush=True)
 if not args.api_only:
  for mode in ['clay','pbr']:render('before','canon-neutral',mode)
 report['changes']=apply(scene,base,era);write()
 if not args.api_only:
  for mode in ['clay','pbr']:render('after','canon-neutral',mode)
  report['first_whole_pair_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();write();print('HEAD02_FIRST_WHOLE_PAIR_COMPLETE',flush=True)
 # Restore original rig/camera/world and render settings before saved native.
 # Only the declared receiving object hides survive into the successor.
 scene.view_layers[0].material_override=None
 saved_render_cameras=dict(report['cameras'])
 native=assets/f'murderbird-head02-{era}.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),relative_remap=False);bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene;cam=scene.camera;after=h.snap();clay=claymat()
 report['preservation']={'original_mesh_empty':len(before['objects']),'original_materials':len(before['materials']),'payload_changes':[n for n,v in before['objects'].items() if after['objects'].get(n)!=v],'material_graph_changes':[n for n,v in before['materials'].items() if after['materials'].get(n)!=v],'file_image_changes':[n for n,v in before['images'].items() if v['source']=='FILE' and after['images'].get(n)!=v],'packed_images':pres.verify_receiving_images(images),'visibility_changes':[n for n,v in before['visibility'].items() if after['visibility'].get(n)!=v],'global_viewport_changes':[n for n in RETIRE if scene.objects[n].hide_viewport!=report['changes']['visibility_overrides'][list(RETIRE).index(n)]['before']['hide_viewport']]}
 assert not any(report['preservation'][k] for k in ['payload_changes','material_graph_changes','file_image_changes','global_viewport_changes']);assert set(report['preservation']['visibility_changes'])==set(RETIRE)
 report['native_sha256']=sha(native);report['input_unchanged']=sha(inp)==expected;write();print('HEAD02_SAVE_REOPEN_PASS',era,flush=True)
 if not args.whole_only and not args.api_only:
  for view in ['head-neck','side-profile','neutral-090','neutral-180','canon-workshop']:
   for mode in ['clay','pbr']:render('after',view,mode)
 report['image_hashes']={p.name:sha(p) for p in out.glob('*.png')};report['completed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();write()
if __name__=='__main__':run()
