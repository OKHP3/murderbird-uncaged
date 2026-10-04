"""HEAD03 Design02: fitted enclosure and physical side-view optic protection.
Import is inert. Exact retained02 payload stays intact except 51 declared hides.
"""
import bpy,json,math,hashlib,importlib.util,datetime,sys,argparse,base64
from pathlib import Path
from mathutils import Vector,Euler,Matrix
ROOT=Path(__file__).resolve().parents[1]
MANIFEST='assets/audit/cg-recursive-three-loop01/loop02-preparation/receiving-manifest-loop02.json'
MANIFEST_SHA='47ed3ee74f0a06a9c470a427f8151dd032b0b48e1c68083f50d092cd1ec3308f'
PLAN='assets/audit/cg-recursive-three-loop01/loop02/source-head03-preparation/plan.json'
PLAN_SHA='2d718104144d7e8339e3bffcdd58f2f13f648849ef9993983fbb5585ee014e9b'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(path):
 s=importlib.util.spec_from_file_location('head03_'+path.stem.replace('-','_'),path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def apply(scene,root_path,era='builder',proof_dir=None):
 base=Path(root_path);assert sha(base/PLAN)==PLAN_SHA
 plan=json.loads((base/PLAN).read_text());retire=plan['proposed_exact_visible_retirements'];assert len(retire)==51
 assert not any(o.get('cgRecursiveSourceHead03') for o in scene.objects)
 for n in retire:assert n in scene.objects and not scene.objects[n].hide_render and not scene.objects[n].hide_get(),n
 for n in plan['protected_exact_objects']:assert n in scene.objects,n
 camera_path=base/f'assets/audit/cg-supervised01/attempt09/{era}/receipt.json';spec=json.loads(camera_path.read_text())['cameras']['canon-neutral'];w,h=spec['resolution'];scale=spec['ortho_scale'];cm=Matrix.Translation(Vector(spec['location']))@Euler(spec['rotation_euler'],'XYZ').to_matrix().to_4x4();ci=cm.inverted();ray=cm.to_3x3()@Vector((0,0,-1));assert abs(ray.x)>.1
 frame=scene.objects['CG2b head frame'];fm=frame.matrix_world.copy();fi=fm.inverted();source=scene.objects['CGH17 frontal crown root'];mats={'head-armor':source.data.materials[0],'black-iron':source.data.materials[1],'worn-bronze':source.data.materials[2]};assert all(m.get('cgMetal05Era')==era for m in mats.values())
 def project(q):
  v=ci@q;return Vector(((v.x/scale+.5-spec['shift'][0])*w,(.5-v.y/(scale*h/w)+spec['shift'][1]*w/h)*h))
 def on_ray(uv,depth):
  # Invert exact orthographic projection, intersect existing scaffold X plane.
  p=cm@Vector(((uv[0]/w-.5+spec['shift'][0])*scale,(.5-uv[1]/h+spec['shift'][1]*w/h)*scale*h/w,0));return p+ray*((depth-p.x)/ray.x)
 def center(o):return sum((o.matrix_world@Vector(q) for q in o.bound_box),Vector())/8
 cores=[project(center(scene.objects['CGO13 small recessed awakened core '+side])) for side in ('L','R')]
 ellipses=[(cores[0],Vector((24,28)))]
 # Opposing camera is a reflected diagnostic of the exact held canon camera,
 # not a new authored receiving rig. Its physical near eye is original far R.
 reflect=Matrix.Diagonal((-1,1,1,1));fcm=reflect@cm@reflect;fci=fcm.inverted()
 def far_project(q):
  v=fci@q;return Vector(((v.x/scale+.5+spec['shift'][0])*w,(.5-v.y/(scale*h/w)+spec['shift'][1]*w/h)*h))
 far_core=center(scene.objects['CGO13 small recessed awakened core R']);far_guard=(far_project(far_core),Vector((24,28)));far_core_depth=-(fci@far_core).z
 def guard_reason(vertices):
  if intersect([project(v) for v in vertices],cores[0],Vector((24,28))):return 'unchanged canon near optic 24x28 guard'
  # Only foreground surfaces relative to the far core in its own opposing view
  # need its aperture cutout. Near-side anterior skin is behind it in this view.
  far_depths=[-(fci@v).z for v in vertices]
  if min(far_depths)<far_core_depth+.001 and intersect([far_project(v) for v in vertices],*far_guard):return 'opposing far optic 24x28 guard with foreground depth'
  return None
 def intersect(poly,c,r):
  ps=[Vector(((p.x-c.x)/r.x,(p.y-c.y)/r.y)) for p in poly]
  if any(p.length_squared<=1 for p in ps):return True
  inside=False
  for a,b in zip(ps,ps[1:]+ps[:1]):
   ab=b-a;t=max(0,min(1,-a.dot(ab)/max(ab.length_squared,1e-12)))
   if (a+ab*t).length_squared<=1:return True
   if (a.y>0)!=(b.y>0) and 0<(b.x-a.x)*(-a.y)/(b.y-a.y)+a.x:inside=not inside
  return inside
 made=[];geometry_proofs=[];skipped=[]
 def mesh(label,vs,faces,role='head-armor',stock=.0018):
  # All panels retain a conservative optical aperture before receiving hides.
  fs=[];removed=0
  for f in faces:
   poly=[project(vs[i]) for i in f]
   if guard_reason([vs[i] for i in f]):removed+=1;continue
   fs.append(f)
  if not fs:
   skipped.append({'name':'CGRS03D02 '+label,'reason':'Entire proposed decorative patch intersects protected optic guard','removed_faces':removed});return None
  name='CGRS03D02 '+label;data=bpy.data.meshes.new(name);data.from_pydata([fi@p for p in vs],[],fs);data.update();obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.parent=frame;obj.matrix_parent_inverse=Matrix.Identity(4);obj.matrix_basis=Matrix.Identity(4)
  for m in (mats[role],mats['black-iron'],mats['worn-bronze']):data.materials.append(m)
  uv=data.uv_layers.new(name='head03-local-normalized');ys=[p.co.y for p in data.vertices];zs=[p.co.z for p in data.vertices];lo=(min(ys),min(zs));hi=(max(ys),max(zs))
  for f in data.polygons:
   f.use_smooth=True
   for li in f.loop_indices:
    q=data.vertices[data.loops[li].vertex_index].co;uv.data[li].uv=((q.y-lo[0])/max(hi[0]-lo[0],1e-7),(q.z-lo[1])/max(hi[1]-lo[1],1e-7))
  so=obj.modifiers.new('formed inward metal thickness','SOLIDIFY');so.thickness=stock;so.offset=-1;so.material_offset=1;so.material_offset_rim=2
  be=obj.modifiers.new('fine formed edge','BEVEL');be.width=.00045;be.segments=2
  for k,v in {'cgRecursiveSourceHead03':True,'cg1cRegion':'head','cg2bRegion':'head','surfaceRole':role,'cgSurfaceFamilies':json.dumps([role,'black-iron','worn-bronze']),'constructionStatus':'Actual-camera scaffold/ray proposal; source contours observed, registration/depth inferred; likeness pending','sourcePlanSHA':PLAN_SHA,'exteriorEras':'maker,mechanic,builder'}.items():obj[k]=v
  made.append(obj);geometry_proofs.append({'name':name,'camera_projected_vertices':[list(project(p)) for p in vs],'opposing_projected_vertices':[list(far_project(p)) for p in vs],'canon_camera_depths':[-(ci@p).z for p in vs],'opposing_camera_depths':[-(fci@p).z for p in vs],'faces':fs,'removed_optic_crossing_faces':removed,'role':role});return obj
 def ribbon(label,rows,depth,role='head-armor',stock=.0018,mirror=True,camber=.002):
  vs=[];nu=7
  for j,(a,b) in enumerate(rows):
   for k in range(nu):
    u=k/(nu-1);q=Vector(a)*(1-u)+Vector(b)*u;vs.append(on_ray(q,depth-camber*math.sin(math.pi*u)))
  fs=[(j*nu+k,j*nu+k+1,(j+1)*nu+k+1,(j+1)*nu+k) for j in range(len(rows)-1) for k in range(nu-1)]
  o=mesh(label+' L',vs,fs,role,stock)
  if mirror:mesh(label+' R',[Vector((-q.x,q.y,q.z)) for q in vs],[tuple(reversed(f)) for f in fs],role,stock)
  return o
 # Connected inner support, fitted to existing head scaffold; never a exposed
 # generic skull exterior. Lofted near/far panels cover crown/orbit/root seams.
 top=[(778,43),(800,44),(827,53),(853,68),(876,88),(895,110)];low=[(770,105),(800,110),(827,130),(853,151),(876,163),(902,157)]
 ribbon('covered cranial side backing',list(zip(top,low)),-.113,'black-iron',.0022)
 vs=[];nu=13
 for a in top:
  near=on_ray(a,-.112);far=Vector((-near.x,near.y,near.z))
  for k in range(nu):
   u=k/(nu-1);q=near*(1-u)+far*u;q.z+=.011*math.sin(math.pi*u);vs.append(q)
 mesh('covered cranial top bridge',vs,[(j*nu+k,j*nu+k+1,(j+1)*nu+k+1,(j+1)*nu+k) for j in range(len(top)-1) for k in range(nu-1)],'black-iron',.0022)
 ribbon('connected posterior cheek backing',[((776,137),(807,153)),((775,155),(823,171)),((782,177),(840,190)),((795,198),(858,212)),((816,211),(876,224))],-.121,'black-iron',.0022)
 # Frontal covered vault joins the inherited dorsal bill root without a false
 # socket. Near skin may physically occlude the far eye in the canon view.
 ribbon('covered brow to bill root join',[((834,66),(850,91)),((852,79),(868,108)),((875,96),(888,124)),((891,113),(903,140)),((905,131),(919,151))],-.119,'black-iron',.0022)
 ribbon('short fitted frontal exterior return',[((841,67),(857,78)),((855,81),(877,96)),((871,97),(895,115)),((887,114),(906,131)),((899,130),(918,151))],-.145,'head-armor',.0018,camber=.002)
 # Connected rear wrap is support rather than a suspended open box: its side
 # boundaries come from held posterior contour rays, depth from existing frame.
 rear_uv=[(771,53),(765,78),(764,105),(770,137),(780,165),(792,185),(804,199)]
 def wrap(label,rows,role,stock=.002):
  vertices=[];nu=17
  for j,uv in enumerate(rows):
   q=on_ray(uv,-.112);far=Vector((-q.x,q.y,q.z))
   for k in range(nu):
    u=k/(nu-1);v=q*(1-u)+far*u;v.y+=.020*math.sin(math.pi*u);vertices.append(v)
  return mesh(label,vertices,[(j*nu+k,j*nu+k+1,(j+1)*nu+k+1,(j+1)*nu+k) for j in range(len(rows)-1) for k in range(nu-1)],role,stock)
 wrap('covered continuous posterior return',rear_uv,'black-iron',.0022)
 for i in range(0,len(rear_uv)-2,2):wrap('short overlapping posterior enclosure %02d'%i,rear_uv[i:i+3],'head-armor',.0018)
 # An outer orbital shoulder is formed from unequal source-directed returns.
 # Conservative cutout keeps complete original optical coating/core readable.
 c=cores[0];inner=[];outer=[]
 for i in range(33):
  a=math.tau*i/32;inner.append((c.x+27*math.cos(a),c.y+32*math.sin(a)));outer.append((c.x+(42+5*math.sin(a))*math.cos(a),c.y+(47+4*math.cos(a))*math.sin(a)))
 ribbon('formed orbital temple return',list(zip(inner,outer)),-.168,'head-armor',.0018,camber=.002)
 # Crown plate silhouettes reuse observed source directions. Their scale is
 # bounded to measured existing head contributors, not the uncertain two-point
 # global trace extension. Plates join the covered backing and one another.
 canonical=plan['observed_source_traces']['canon']['curves'];src_dims=(1280,853)
 axes=[]
 for name in ('crown_plate_direction_1','crown_plate_direction_2','crown_plate_direction_3','crown_plate_direction_4'):
  pts=canonical[name]['normalized'];a=Vector((pts[0][0]*1280,pts[0][1]*853));b=Vector((pts[-1][0]*1280,pts[-1][1]*853));axes.append((b-a).normalized())
 def blade(label,basept,tippt,width,depth,mirror=True):
  a=Vector(basept);b=Vector(tippt);v=b-a;n=Vector((-v.y,v.x)).normalized();rows=[]
  for i in range(13):
   t=i/12;mid=a+v*t+n*(3*math.sin(math.pi*t));half=width*(.42+.37*math.sin(math.pi*t))*(1-t)**.72+.35;rows.append((mid+n*half,mid-n*half))
  ribbon(label,rows,depth,'head-armor',.00155,mirror,camber=.0035)
 roots=[(798,55),(815,66),(824,89),(816,115),(804,139)]
 for i,point in enumerate(roots):
  direction=axes[min(i,3)];length=[36,44,49,43,34][i];tip=Vector(point)+direction*length
  blade('swept posterior crown blade %02d'%i,point,tip,12+i%3,-.146)
 for i,point in enumerate([(824,44),(846,56),(864,72),(878,91)]):
  direction=axes[min(i,3)];tip=Vector(point)+direction*[35,42,44,36][i];blade('overlapping upper crown blade %02d'%i,point,tip,14,-.081,mirror=True)
 # Cross-head overlapping top sheets cover the backing without a pale roof.
 for i,(a,b) in enumerate([((796,42),(830,48)),((819,51),(850,65)),((840,65),(872,85)),((860,84),(888,105))]):
  near=on_ray(a,-.080);far=Vector((-near.x,near.y,near.z));endnear=on_ray(b,-.083);endfar=Vector((-endnear.x,endnear.y,endnear.z));vs=[];nu,nv=13,9
  for j in range(nv):
   t=j/(nv-1);left=near*(1-t)+endnear*t;right=far*(1-t)+endfar*t
   for k in range(nu):
    u=k/(nu-1);q=left*(1-u)+right*u;q.z+=.007*math.sin(math.pi*u)+.003*math.sin(math.pi*t);vs.append(q)
  mesh('interlocking top crown sheet %02d'%i,vs,[(j*nu+k,j*nu+k+1,(j+1)*nu+k+1,(j+1)*nu+k) for j in range(nv-1) for k in range(nu-1)],'head-armor',.00155)
 # Narrow source accent segmented into three connected courses. It ends at
 # retained upper bill seam, never expands to cover the entire cranial support.
 brow=[((786,40),(786,46)),((809,48),(805,56)),((834,60),(829,69)),((860,75),(854,85)),((884,91),(880,100)),((902,104),(899,113)),((918,113),(912,123))]
 for i,(a,b) in enumerate([(0,3),(2,5),(4,6)]):ribbon('narrow supraoptic accent %02d'%i,brow[a:b+1],-.158,'worn-bronze',.0014,camber=.001)
 ribbon('formed bill root interface',[((851,103),(863,109)),((868,115),(884,126)),((885,131),(907,145)),((900,142),(921,153))],-.153,'head-armor',.0018,camber=.002)
 # A shaped lip and recessed return replace the padded exterior jaw. Original
 # deeper internal mechanism and all four receiving upper bill meshes remain.
 jaw=[((782,144),(773,152)),((803,153),(791,167)),((826,167),(813,184)),((847,186),(834,201)),((861,201),(851,211)),((874,209),(867,216)),((882,208),(880,214))]
 ribbon('shaped recessed lower cheek lip',jaw,-.162,'head-armor',.0017,camber=.002)
 ribbon('posterior cheek lip return',[((784,147),(773,152)),((786,166),(777,175)),((795,188),(784,193)),((816,208),(802,215))],-.151,'head-armor',.0017,camber=.002)
 ribbon('short cheek to throat return',[((782,178),(795,189)),((795,195),(809,203)),((803,207),(817,214))],-.146,'head-armor',.0017,camber=.002)
 bpy.context.view_layer.update()
 proof={'plan_sha256':PLAN_SHA,'camera_receipt_sha256':sha(camera_path),'camera':spec,'source_contours':'Frozen plan observed normalized curves; source views/registration are not calibration','regional_registration':'Crown blade directions from canon curves; footprints bounded to held09 scaffold; no blind two-anchor rear enlargement','depth_method':'Inverse actual-camera orthographic rays intersect regional world-X planes near/behind preserved head/optic scaffold; far side mirrored physically','optic_centers_pixels':[list(q) for q in cores],'protected_optic_guard_radii_pixels':[24,28],'revised_visibility_rule':'Unchanged canon near-eye guard; far-eye guard in reflected opposing held-canon view applies only to geometry forward of original far core. Near anterior skin may cover far optic in canon without hiding/rebinding its original object. No arbitrary guard shrinking.','opposing_camera_matrix':[list(row) for row in fcm],'opposing_camera_shift':[-spec['shift'][0],spec['shift'][1]],'opposing_far_guard_center':list(far_guard[0]),'opposing_far_core_depth':far_core_depth,'new_objects':geometry_proofs,'fully_guard_clipped_patches_omitted':skipped,'original_objects_still_visible_before_proof':all(not scene.objects[n].hide_render for n in retire),'prehide_new_face_optic_intersections':sum(any(intersect([Vector(r['camera_projected_vertices'][i]) for i in f],c,rad) for c,rad in ellipses) or (min(r['opposing_camera_depths'][i] for i in f)<far_core_depth+.001 and intersect([Vector(r['opposing_projected_vertices'][i]) for i in f],*far_guard)) for r in geometry_proofs for f in r['faces'])}
 assert proof['prehide_new_face_optic_intersections']==0
 if proof_dir:
  out=Path(proof_dir);assert not (out/'prehide-projected-boundaries.json').exists();(out/'prehide-projected-boundaries.json').write_text(json.dumps(proof,indent=2)+'\n')
  image=base/f'assets/audit/cg-recursive-three-loop01/loop01/delivery/retained02/{era}/canon-neutral.png';svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="853" viewBox="0 0 1280 853"><image width="1280" height="853" href="data:image/png;base64,{base64.b64encode(image.read_bytes()).decode()}"/>']
  for r in geometry_proofs:
   for f in r['faces']:
    ps=[r['camera_projected_vertices'][i] for i in f];svg.append('<polygon fill="none" stroke="#fd75cd" stroke-width=".22" points="'+' '.join(f'{p[0]:.2f},{p[1]:.2f}' for p in ps)+'"/>')
  for c,rad in ellipses:svg.append(f'<ellipse cx="{c.x}" cy="{c.y}" rx="{rad.x}" ry="{rad.y}" fill="none" stroke="#50dffe" stroke-width="1"/>')
  svg.append('<text x="20" y="830" fill="white" font-size="16">Before retirement: new projected boundaries, cyan protected optic guard. Existing image remains unchanged.</text></svg>');(out/'prehide-projected-boundaries.svg').write_text(''.join(svg))
  bg=out/'before/canon-opposite.png';fsvg=['<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="853" viewBox="0 0 1280 853">']
  if bg.exists():fsvg.append(f'<image width="1280" height="853" href="data:image/png;base64,{base64.b64encode(bg.read_bytes()).decode()}"/>')
  for record in geometry_proofs:
   for face in record['faces']:
    points=[record['opposing_projected_vertices'][i] for i in face];forward=min(record['opposing_camera_depths'][i] for i in face)<far_core_depth+.001
    fsvg.append('<polygon fill="none" stroke="'+('#fd75cd' if forward else '#fee365')+'" stroke-width=".22" points="'+' '.join(f'{pt[0]:.2f},{pt[1]:.2f}' for pt in points)+'"/>')
  c,rad=far_guard;fsvg.append(f'<ellipse cx="{c.x}" cy="{c.y}" rx="{rad.x}" ry="{rad.y}" fill="none" stroke="#50dffe" stroke-width="1"/><text x="20" y="830" fill="white" font-size="16">Opposing far eye: unchanged guard. Pink foreground surfaces; yellow surfaces behind core. Actual source rig preserved.</text></svg>');(out/'prehide-opposing-boundaries.svg').write_text(''.join(fsvg))

 hidden={}
 for n in retire:
  o=scene.objects[n];hidden[n]={'before':[o.hide_render,o.hide_viewport,o.hide_get()],'after':[True,o.hide_viewport,True],'hide_set':True};o.hide_render=True;o.hide_set(True)
 return {'module':'cg-recursive-source-head03-design02','design':2,'era':era,'newMeshes':[o.name for o in made],'hideOverrides':hidden,'protected_objects':plan['protected_exact_objects'],'prehide_proof':proof,'kept_bill_objects':[n for n in plan['protected_exact_objects'] if n.startswith('CGH18')],'material_graph_changes':False,'source_likeness':'pending root Design02 pixel gate'}
def run():
 p=argparse.ArgumentParser();p.add_argument('--source-root',required=True);p.add_argument('--era',choices=('builder','maker','mechanic'),default='builder');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);base=Path(a.source_root);era=a.era;assert era=='builder','Other eras require root visible gate'
 manifest=base/MANIFEST;assert sha(manifest)==MANIFEST_SHA;receiver=json.loads(manifest.read_text())['natives'][era];native=base/receiver['path'];assert sha(native)==receiver['sha256']
 out=ROOT/f'assets/audit/cg-recursive-source-head03/attempt02/{era}';assert not out.exists();out.mkdir(parents=True);models=ROOT/'assets/models/cg-recursive-source-head03/attempt02';models.mkdir(parents=True,exist_ok=False)
 delivery=load(base/'scripts/cg-recursive-delivery02.py');assert sha(base/'scripts/cg-recursive-delivery02.py')=='f621f9eb0271071a2ee02828e01de34f527ac5aec1803315a4d8fd61b5df4091';strong=load(base/'scripts/cg-supervised-head17.py');payload=load(base/'scripts/cg-supervised-body12.py');pres=load(base/'scripts/cg-supervised-preservation.py')
 bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene
 def rig():return {'objects':{o.name:{'matrix':[list(r) for r in o.matrix_world],'objectRNA':strong.rna(o),'dataRNA':strong.rna(o.data)} for o in scene.objects if o.type in ('CAMERA','LIGHT')},'world':{'name':scene.world.name,'nodes':[(n.name,n.type,[(i.name,delivery.value(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in scene.world.node_tree.nodes]},'render':{k:getattr(scene.render,k) for k in ['engine','resolution_x','resolution_y','resolution_percentage','filepath','film_transparent']},'view':{k:getattr(scene.view_settings,k) for k in ['view_transform','look','exposure','gamma']},'override':scene.view_layers[0].material_override.name if scene.view_layers[0].material_override else None}
 original_rig=rig();before=delivery.snapshot(scene,strong,payload);assert len(before['payload'])==7644 and len(before['materials'])==62
 report={'status':'IN_PROGRESS','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input':str(native),'input_sha256':sha(native),'receiving_manifest_sha256':MANIFEST_SHA,'plan_sha256':PLAN_SHA,'authoring_sha256':sha(__file__),'era':era,'rig_captured_before_before_renders':original_rig,'receiving_counts':receiver['custody_counts'],'visible_gate':'not yet reviewed','scope':'Design02 final focused correction; source likeness pending; no exports/runtime/publication'}
 def write():(out/'receipt.json').write_text(json.dumps(report,indent=2,default=str)+'\n')
 write();(out/'receiving-snapshot.json').write_text(json.dumps(before,indent=2)+'\n');camera=json.loads((base/f'assets/audit/cg-supervised01/attempt09/{era}/receipt.json').read_text())
 # These are temporary reflected diagnostic specs, preserving every saved rig.
 import copy
 camera['cameras']['canon-opposite']=copy.deepcopy(camera['cameras']['canon-neutral'])
 original_spec=camera['cameras']['canon-neutral'];reflection=Matrix.Diagonal((-1,1,1,1));ocm=Matrix.Translation(Vector(original_spec['location']))@Euler(original_spec['rotation_euler'],'XYZ').to_matrix().to_4x4();opm=reflection@ocm@reflection
 camera['cameras']['canon-opposite']['location']=list(opm.to_translation());camera['cameras']['canon-opposite']['rotation_euler']=list(opm.to_euler('XYZ'));camera['cameras']['canon-opposite']['shift'][0]*=-1
 camera['cameras']['head-neck-opposite']=copy.deepcopy(camera['cameras']['head-neck'])
 camera['cameras']['head-neck-opposite']['location'][0]*=-1;camera['cameras']['head-neck-opposite']['rotation_euler'][1]*=-1;camera['cameras']['head-neck-opposite']['rotation_euler'][2]*=-1
 report['additional_view_method']='Opposing head diagnostic reflects saved09 head camera across worldX; neutral090/270 and rear use exact saved09 specs'
 args=argparse.Namespace(samples=4,resolution=640);baseline=out/'before';baseline.mkdir();report['before_renders']=delivery.render_views(scene,camera,['canon-neutral','canon-neutral-clay','canon-workshop','canon-opposite','head-neck','head-neck-opposite','neutral-090','neutral-270','neutral-180'],baseline,args);assert rig()==original_rig;write()
 report['changes']=apply(scene,base,era,proof_dir=out);declared={n:{'name':n,'hide_set':True} for n in report['changes']['hideOverrides']};report['before_save_custody']=delivery.verify(scene,before,strong,payload,declared);pres.retain_packed_image_ids(scene);assert rig()==original_rig
 output=models/f'murderbird-source-head03-{era}.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(output),relative_remap=False);bpy.ops.wm.open_mainfile(filepath=str(output));scene=bpy.context.scene;report['save_reopen_custody']=delivery.verify(scene,before,strong,payload,declared);report['native']=str(output);report['native_sha256']=sha(output);report['original_rig_restored_before_save']=True;assert rig()==original_rig;write()
 candidate=out/'candidate';candidate.mkdir();report['candidate_renders']=delivery.render_views(scene,camera,['canon-neutral','canon-neutral-clay','canon-workshop','canon-opposite','head-neck','head-neck-opposite','side-profile','neutral-090','neutral-270','neutral-180'],candidate,args);report['after_render_custody']=delivery.verify(scene,before,strong,payload,declared);assert rig()==original_rig;assert sha(native)==receiver['sha256'] and sha(output)==report['native_sha256'];report['status']='PRESERVATION_TECHNICAL_PASS_PAUSED_FOR_ROOT_DESIGN02_GATE';report['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();write();print('CG_RECURSIVE_SOURCE_HEAD03_DESIGN02_COMPLETE',str(out),flush=True)
if __name__=='__main__':
 try:run()
 except Exception:
  import traceback;traceback.print_exc();print('CG_RECURSIVE_SOURCE_HEAD03_FAILED',flush=True);sys.exit(1)
