"""Coupled source-contour brow, cheek, bill study; immutable receiving09.

All depth, hidden construction and bilateral extension are CG proposals. July
controls head identity only; locked composite controls the full character.
Import is inert. apply() adds successors and explicit visibility overrides.
"""
import bpy, json, math, hashlib, importlib.util, sys, datetime
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
EXPECTED='c39a2fefcc9b4d277540a0406522e69b06975c14a0b8e281f183d1fca20dc2fc'
INPUT=BASE/'assets/models/cg-supervised01/attempt09/murderbird-supervised-builder.blend'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(path):
 s=importlib.util.spec_from_file_location(path.stem.replace('-','_'),path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def apply(scene,root_path=None,era='builder'):
 if era=='advanced':era='builder'
 if era not in ('maker','mechanic','builder'):raise ValueError(era)
 if any(o.get('cgRecursiveHead01') for o in scene.objects):raise RuntimeError('Reload receiving09 before apply')
 frame=scene.objects['CG2b head frame'].matrix_world.copy();made=[];hidden=[]
 def family(role):
  preferred='CGH18 formed distal hooked bill plate' if role=='machined-steel' else 'CGH17 frontal crown root'
  source=scene.objects[preferred];families=json.loads(source.get('cgSurfaceFamilies','[]'))
  if role in families:
   material=source.data.materials[families.index(role)]
   if material.get('cgMetal05Era')!=era:raise RuntimeError('Receiving visible graph era mismatch '+material.name)
   return material
  choices=[m for m in bpy.data.materials if m.get('cgMetal05Family')==role and m.get('cgMetal05Era')==era]
  if not choices:raise RuntimeError('Missing receiving era graph '+role+' '+era)
  return choices[0]
 mats={r:family(r) for r in ['head-armor','black-iron','machined-steel','worn-bronze']}
 for o in scene.objects:
  if o.hide_render:continue
  if ((o.get('cgSupervisedHead17') and ('frontal crown root' in o.name or 'broad curved brow' in o.name)) or o.get('cgSupervisedBill18') or
      (o.get('cgSupervisedHead06') and any(s in o.name for s in ('connected under-eye','thin orbital cheek','substantial swept plated mandible','nested dark jaw','interleaved jaw face','recessed cheek lower')))):
   hidden.append({'object':o.name,'before':[o.hide_render,o.hide_get()],'after':[True,True]});o.hide_render=True;o.hide_set(True)
 def p(x,y,d):return (d,(788-x)*.0012+.005,(188-y)*.0012+.020)
 def mesh(label,vs,fs,role='head-armor',thick=.0024):
  name='CGRH01 '+label;d=bpy.data.meshes.new(name);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.matrix_world=frame.copy()
  for r in (role,'black-iron','worn-bronze'):d.materials.append(mats[r])
  for k,v in {'cgRecursiveHead01':True,'cg1cRegion':'head','cg2bRegion':'head','surfaceRole':role,'cgSurfaceFamilies':json.dumps([role,'black-iron','worn-bronze']),'exteriorEras':'maker,mechanic,builder','constructionStatus':'Source-contour coupled facial successor; depth and hidden construction proposed; owner likeness pending'}.items():o[k]=v
  uv=d.uv_layers.new(name='recursive-head01-local-plate');lo=[min(v.co[a] for v in d.vertices) for a in (1,2)];hi=[max(v.co[a] for v in d.vertices) for a in (1,2)]
  for f in d.polygons:
   f.use_smooth=True
   for li in f.loop_indices:
    q=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=((q.y-lo[0])/max(hi[0]-lo[0],1e-6),(q.z-lo[1])/max(hi[1]-lo[1],1e-6))
  if thick:
   s=o.modifiers.new('pressed metal inward return','SOLIDIFY');s.thickness=thick;s.offset=-1;s.material_offset=1;s.material_offset_rim=2
  b=o.modifiers.new('small visible edge break','BEVEL');b.width=.00045;b.segments=2
  made.append(o);return o
 def spline(rr,n=5):
  result=[]
  for i in range(len(rr)-1):
   a,b,c,d=rr[max(0,i-1)],rr[i],rr[i+1],rr[min(len(rr)-1,i+2)]
   for j in range(n):
    t=j/n;result.append([.5*(2*bb+(-aa+cc)*t+(2*aa-5*bb+4*cc-dd)*t*t+(-aa+3*bb-3*cc+dd)*t**3) for aa,bb,cc,dd in zip(a,b,c,d)])
  return result+[rr[-1]]
 def patch(label,rr,side,role='head-armor',camber=.007):
  # Paired actual source contour landmarks, not centerline swept rectangles.
  ss=spline(rr,4);vs=[];n=11
  for ax,ay,ad,bx,by,bd in ss:
   for k in range(n):
    t=k/(n-1);dep=ad*(1-t)+bd*t+camber*math.sin(math.pi*t)-.003*max(0,1-t/.13)**2
    vs.append(p(ax*(1-t)+bx*t,ay*(1-t)+by*t,side*dep))
  fs=[(j*n+k,j*n+k+1,(j+1)*n+k+1,(j+1)*n+k) for j in range(len(ss)-1) for k in range(n-1)]
  if side<0:fs=[tuple(reversed(f)) for f in fs]
  o=mesh(label,vs,fs,role);o['sourceContourControls']=json.dumps(rr);return o
 # Smaller segmented front roof carries inward to the bill; retains the two
 # useful broad posterior swept crests and all pointed posterior layers.
 rr=[(703,52,.103),(729,62,.126),(763,82,.141),(803,108,.145),(838,134,.134),(866,161,.118),(892,191,.097)]
 for i,(begin,end) in enumerate([(0,3),(2,5),(4,6)]):
  ss=spline(rr[begin:end+1],5);vs=[];n=17
  for x,y,w in ss:
   for k in range(n):
    u=k/(n-1)*2-1;vs.append(p(x,y+24*abs(u)**2+.8*i,u*w*.82))
  mesh('segmented frontal cranial plate '+str(i),vs,[(j*n+k,j*n+k+1,(j+1)*n+k+1,(j+1)*n+k) for j in range(len(ss)-1) for k in range(n-1)],'head-armor')
 for side,label in [(-1,'L'),(1,'R')]:
  # Source's bronze supraoptic course is a diagonal pressed plate with a
  # convex outer ridge and concave lower edge meeting the actual optic seat.
  patch('source scalloped supraoptic brow '+label,[(669,50,.094,678,76,.118),(706,64,.119,703,101,.150),(744,83,.135,733,117,.164),(783,104,.147,779,130,.177),(817,126,.148,823,174,.174),(845,149,.137,847,183,.161),(862,167,.123,873,176,.134)],side,'worn-bronze',.005)
  # Posterior cheek bracket widens around real optic recess and narrows into
  # source's rising lower orbital return. No optic or seat relocation.
  patch('posterior orbital cheek bracket '+label,[(685,177,.125,719,169,.165),(675,204,.128,726,191,.176),(689,229,.134,742,223,.177),(716,248,.139,774,244,.174),(755,264,.145,807,253,.168),(803,267,.143,841,235,.151),(847,257,.131,865,215,.139)],side)
  patch('bill-root interlocking orbital plate '+label,[(840,138,.152,853,166,.153),(860,157,.142,863,194,.147),(883,181,.127,873,220,.140),(914,211,.102,883,246,.128),(937,239,.078,898,267,.111),(948,268,.067,919,285,.094)],side,'machined-steel',.010)
  # Lower cheek follows paired July contour edges and descends into existing
  # throat, preserving open mouth rather than creating a hanging bib.
  jaw=[(674,235,.132,711,231,.156),(687,265,.138,736,260,.160),(720,291,.139,764,277,.152),(752,321,.130,792,308,.143),(778,362,.111,818,359,.124),(803,398,.080,842,404,.083),(838,422,.039,866,425,.034),(873,425,.005,884,421,.004)]
  patch('broad recessed lower cheek and jaw '+label,jaw,side,'head-armor',.009)
  patch('nested jaw cavity lip '+label,[(692,256,.124,710,250,.140),(722,281,.125,743,269,.144),(756,309,.117,775,299,.134),(789,355,.096,803,345,.115),(824,405,.057,834,400,.074),(869,424,.010,875,421,.013)],side,'black-iron',.003)
  # Throat only above current breast: broad unequal short overlapping returns.
  patch('lower cheek throat return '+label,[(690,280,.123,722,281,.139),(701,311,.116,735,321,.132),(710,342,.107,749,358,.120),(726,371,.099,761,390,.107)],side,'head-armor')
  patch('anterior throat return '+label,[(731,326,.113,766,338,.128),(748,362,.104,788,375,.117),(760,398,.092,799,422,.103),(768,422,.087,794,444,.089)],side,'head-armor')
 # Three unequal formed bill sections. Posterior free edge scallops reveal an
 # inner wall, breaking the oversized smooth uninterrupted bill panel.
 def bill(label,rr):
  ss=spline(rr,4);vs=[];n=41
  for j,(y,x,r,w) in enumerate(ss):
   t=j/(len(ss)-1)
   for k in range(n):
    a=-math.pi+math.tau*k/(n-1);vs.append(p(x+r*math.cos(a),y,w*math.sin(a)))
  return mesh(label,vs,[(j*n+k,j*n+k+1,(j+1)*n+k+1,(j+1)*n+k) for j in range(len(ss)-1) for k in range(n-1)],'machined-steel',.0022)
 bill('upper bill root saddle',[(184,904,8,.067),(207,908,17,.085),(235,920,27,.096),(260,924,31,.094)])
 bill('interlocking middle bill plate',[(245,923,29,.097),(272,927,35,.090),(300,927,37,.072),(319,927,34,.060)])
 bill('lower deep hooked bill plate',[(306,926,36,.070),(336,930,35,.056),(365,932,28,.040),(393,925,20,.026),(421,909,10,.012),(445,888,.8,.0012)])
 for side,label in [(-1,'L'),(1,'R')]:
  # Source's recessed posterior scallop breaks the bill-to-root join as a
  # genuine layered plate opening, with an inset dark inner surface.
  patch('bill posterior scalloped shoulder '+label,[(901,235,.099,924,229,.078),(917,257,.100,941,248,.073),(916,280,.092,949,274,.066),(908,297,.080,949,297,.061),(918,316,.071,950,319,.053),(925,339,.056,948,343,.042)],side,'machined-steel',.006)
 bpy.context.view_layer.update()
 return {'module':'cg-recursive-head01','era':era,'added_objects':[o.name for o in made],'visibility_overrides':hidden,'hidden_originals':[h['object'] for h in hidden],'new_objects':[o.name for o in made],'preserved_optics':'All receiving optical seats and interiors unchanged','interface_bounds_head_local':{'min':[min(v.co[a] for o in made for v in o.data.vertices) for a in range(3)],'max':[max(v.co[a] for o in made for v in o.data.vertices) for a in range(3)]},'below_breast_interface_changes':False,'original_payload_mutation':False,'original_material_graph_mutation':False,'proposal_only':True}
def run():
 out=ROOT/'assets/audit/cg-recursive-head01/attempt02';out.mkdir(parents=True,exist_ok=True);assets=ROOT/'assets/models/cg-recursive-head01';assets.mkdir(parents=True,exist_ok=True)
 assert sha(INPUT)==EXPECTED
 h=load(BASE/'scripts/cg-supervised-head17.py');pres=load(BASE/'scripts/cg-supervised-preservation.py')
 bpy.ops.wm.open_mainfile(filepath=str(INPUT));scene=bpy.context.scene;before=h.snap();images=pres.packed_image_snapshot();pres.retain_packed_image_ids(scene)
 report={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input_path':str(INPUT),'input_sha256':EXPECTED,'goal_revision':'251f2f0243181e97140179c2aff6eb057e165438','reference_scopes':{'locked_composite':'full bird','July':'head only','First Choice':'surface continuity retained; no new frame extraction'},'cameras':{},'samples':4,'resolution_factor':.5}
 rc=json.loads((BASE/'assets/audit/cg-supervised01/attempt09/builder/receipt.json').read_text())['cameras'];cam=scene.camera
 clay=bpy.data.materials.new('CGRH01 temporary diagnostic clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.42,.42,.42,1);bs.inputs['Roughness'].default_value=.75
 def write():(out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
 def render(state,view,mode):
  r=rc[view];cam.location=r['location'];cam.rotation_euler=r['rotation_euler'];cam.data.type=r['projection'];cam.data.ortho_scale=r['ortho_scale'];cam.data.lens=r['lens_mm'];cam.data.shift_x,cam.data.shift_y=r['shift']
  bg=scene.world.node_tree.nodes['Background'];bg.inputs[0].default_value=r['world_color'];bg.inputs[1].default_value=r['world_strength']
  lights=[o for o in scene.objects if o.type=='LIGHT'];assert len(lights)==len(r['areas'])
  for o,a in zip(lights,r['areas']):o.location=a['location'];o.rotation_euler=a['rotation_euler'];o.data.energy=a['power'];o.data.color=a['color'];o.data.size=a['size']
  scene.render.engine='CYCLES';scene.cycles.samples=4;scene.cycles.use_denoising=True;scene.render.resolution_x,scene.render.resolution_y=[round(v*.5) for v in r['resolution']];scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_layers[0].material_override=clay if mode=='clay' else None
  key=state+'-'+view+'-'+mode;scene.render.filepath=str(out/(key+'.png'));bpy.context.view_layer.update();bpy.ops.render.render(write_still=True);report['cameras'][key]=dict(r,resolution=[scene.render.resolution_x,scene.render.resolution_y],samples=4);write();print('HEAD01_RENDERED',key,flush=True)
 for mode in ['clay','pbr']:render('before','canon-neutral',mode)
 report['changes']=apply(scene,ROOT,'builder');write()
 for mode in ['clay','pbr']:render('after','canon-neutral',mode)
 print('HEAD01_FIRST_WHOLE_PAIR_COMPLETE',flush=True)
 scene.view_layers[0].material_override=None
 native=assets/'murderbird-recursive-head01-attempt02-builder.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),relative_remap=False);bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene;cam=scene.camera;after=h.snap()
 clay=bpy.data.materials.new('CGRH01 temporary readback diagnostic clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.42,.42,.42,1);bs.inputs['Roughness'].default_value=.75
 report['preservation']={'receiving_object_count':len(before['objects']),'object_payload_changes':[n for n,v in before['objects'].items() if after['objects'].get(n)!=v],'material_graph_changes':[n for n,v in before['materials'].items() if after['materials'].get(n)!=v],'file_image_changes':[n for n,v in before['images'].items() if v['source']=='FILE' and after['images'].get(n)!=v],'packed_images':pres.verify_receiving_images(images),'visibility_changes':[n for n,v in before['visibility'].items() if after['visibility'].get(n)!=v]}
 assert not any(report['preservation'][k] for k in ['object_payload_changes','material_graph_changes','file_image_changes']);assert set(report['preservation']['visibility_changes'])==set(report['changes']['hidden_originals'])
 report['native_sha256']=sha(native);report['input_preserved']=sha(INPUT)==EXPECTED;write();print('HEAD01_PRESERVATION_READBACK',report['preservation'],flush=True)
 # Whole gain is reviewed before these optional diagnostics are commissioned.
 if '--whole-only' not in sys.argv:
  for view in ['head-neck','side-profile','neutral-180']:
   for mode in ['clay','pbr']:render('after',view,mode)
 report['interface_world_bounds']={'min':[min((o.matrix_world@v.co)[a] for n in report['changes']['added_objects'] for o in [scene.objects[n]] for v in o.data.vertices) for a in range(3)],'max':[max((o.matrix_world@v.co)[a] for n in report['changes']['added_objects'] for o in [scene.objects[n]] for v in o.data.vertices) for a in range(3)]}
 report['authoring_script']='scripts/cg-recursive-head01.py';report['authoring_sha256']=sha(Path(__file__));report['image_hashes']={p.name:sha(p) for p in out.glob('*.png')};report['completed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();write()
if __name__=='__main__':run()
