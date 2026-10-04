import bpy,json,hashlib,importlib.util,math,time
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');WT=Path('/Users/okh/.codex/worktrees/cg-supervised-oblique-breast15/murderbird-uncaged');OUT=WT/'assets/audit/cg-supervised-body15/attempt01';R=json.loads((OUT/'receipt.json').read_text());start=time.time()
spec=importlib.util.spec_from_file_location('shared_body12',ROOT/'scripts/cg-supervised-body12.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def metadata():
 return {i.name:dict(items=dict(i.items()),size=list(i.size),channels=i.channels,alphaMode=i.alpha_mode,colorSpace=i.colorspace_settings.name,fileFormat=i.file_format,source=i.source,filepath=i.filepath,filepathRaw=i.filepath_raw,fakeUser=i.use_fake_user,packedSHA256=hashlib.sha256(bytes(i.packed_file.data)).hexdigest()) for i in bpy.data.images if i.packed_file}
def mods(o):
 records=[]
 for mod in o.modifiers:
  rec={'type':mod.type,'name':mod.name}
  for p in mod.bl_rna.properties:
   if p.identifier=='rna_type' or p.is_readonly:continue
   try:
    v=getattr(mod,p.identifier)
    if p.type=='POINTER':v=v.name if v else None
    elif p.type=='COLLECTION':continue
    elif p.is_array:v=list(v)
    rec[p.identifier]=v
   except:pass
  records.append(rec)
 return hashlib.sha256(repr(records).encode()).hexdigest()
def snapshot():
 s=bpy.context.scene
 return {'payload':{o.name:m.digest(o) for o in s.objects if o.type in ('MESH','EMPTY')},'mods':{o.name:mods(o) for o in s.objects if o.type=='MESH'},'vis':{o.name:[o.hide_render,o.hide_viewport,o.hide_get()] for o in s.objects},'graphs':m.material_digest(),'packed':metadata()}
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend'));a=snapshot();print('ROOT06_SNAPSHOT',len(a['payload']),flush=True)
before=ROOT/'assets/audit/cg-supervised-body13/attempt01/murderbird-body13.blend';bpy.ops.wm.open_mainfile(filepath=str(before));b=snapshot();lower13={o.name for o in bpy.context.scene.objects if o.get('cgSupervisedBody13')};upper13={o.name:m.digest(o) for o in bpy.context.scene.objects if o.get('cgSupervisedBody12')};print('BODY13_SNAPSHOT',len(b['payload']),flush=True)
native=OUT/'murderbird-body15.blend';bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=2;c=snapshot();print('BODY15_SNAPSHOT',len(c['payload']),flush=True)
changed06=[n for n,h in a['payload'].items() if c['payload'].get(n)!=h];mods06=[n for n,h in a['mods'].items() if c['mods'].get(n)!=h];outside13=[n for n,h in b['payload'].items() if n not in lower13 and c['payload'].get(n)!=h];mods13=[n for n,h in b['mods'].items() if n not in lower13 and c['mods'].get(n)!=h]
vc=[n for n,v in a['vis'].items() if n not in m.HIDE_MANIFEST and c['vis'].get(n)!=v];allhide={n:c['vis'].get(n) for n in m.HIDE_MANIFEST};panels=[o for o in s.objects if o.get('cgSupervisedBody12') or o.get('cgSupervisedBody15')];new=[o for o in panels if o.get('cgSupervisedBody15')];deps=bpy.context.evaluated_depsgraph_get();points=[];uvbad=[];uvmissing=[];conventionbad=[];geomnonfinite=[];trees={}
for o in panels:
 ev=o.evaluated_get(deps);md=ev.to_mesh();vs=[o.matrix_world@v.co for v in md.vertices];points.extend(vs)
 if any(not all(math.isfinite(c) for c in v) for v in vs):geomnonfinite.append(o.name)
 if not md.uv_layers:uvmissing.append(o.name)
 if any(not math.isfinite(c) or c< -1e-6 or c>1.000001 for l in md.uv_layers for uv in l.data for c in uv.uv):uvbad.append(o.name)
 trees[o.name]=BVHTree.FromPolygons(vs,[tuple(p.vertices) for p in md.polygons]);ev.to_mesh_clear()
 key='body15Grid' if o.get('cgSupervisedBody15') else 'body12Grid';nu,nv=json.loads(o[key]);lay=o.data.uv_layers.active
 if any(abs(lay.data[li].uv.x-((o.data.loops[li].vertex_index%nu)/(nu-1)))>1e-6 or abs(lay.data[li].uv.y-((o.data.loops[li].vertex_index//nu)/(nv-1)))>1e-6 for li in range(len(o.data.loops))):conventionbad.append(o.name)
# Independent fresh run with same geometric definition, complementary odd quad subset.
records=[]
for o in new:
 nu,nv=json.loads(o['body15Grid']);rec=dict(object=o.name,rootSamples=0,rootCovered=0,tipSamples=0,tipBuried=0,tipOccluders={},maxTipBurial=0)
 for p in list(o.data.polygons)[1::2]:
  co=sum((o.matrix_world@o.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices);v=sum(i//nu/(nv-1) for i in p.vertices)/len(p.vertices);n=(o.matrix_world.to_3x3().inverted().transposed()@p.normal).normalized();n=-n if n.y>0 else n;origin=co+n*.035;hits=[]
  for name,t in trees.items():
   if name==o.name:continue
   h,hn,idx,d=t.ray_cast(origin,-n,.075)
   if h is not None and .035-d>.0002:hits.append((name,.035-d))
  if v<=.25:rec['rootSamples']+=1;rec['rootCovered']+=bool(hits)
  elif v>=.82:
   rec['tipSamples']+=1;rec['tipBuried']+=bool(hits)
   for name,d in hits:rec['tipOccluders'][name]=rec['tipOccluders'].get(name,0)+1;rec['maxTipBurial']=max(rec['maxTipBurial'],d)
 records.append(rec)
frames=[]
for name,q in R['cameras'].items():
 if not ('whole' in name or 'turn' in name):continue
 cam=s.camera;cam.location=q['location'];cam.rotation_euler=q['rotation_euler'];cam.data.type='ORTHO';cam.data.ortho_scale=q['scale'];cam.data.shift_x,cam.data.shift_y=q.get('shift',[0,0]);s.render.resolution_x,s.render.resolution_y=q['resolution'];bpy.context.view_layer.update();coords=[]
 for o in s.objects:
  if o.type=='MESH' and not o.hide_render and o.get('cg1cRegion'):coords.extend(world_to_camera_view(s,cam,o.matrix_world@Vector(v)) for v in o.bound_box)
 mi=[min(v[i] for v in coords) for i in (0,1)];ma=[max(v[i] for v in coords) for i in (0,1)];frames.append(dict(image=name,min=mi,max=ma,inFrame=min(mi)>=0 and max(ma)<=1))
result=dict(method='Fresh independent Blender process CPU2; shared body12 payload/material digest helpers disclosed; independent modifier RNA supplement; metadata directly reconstructed from ROOT06; complementary odd face subset BVH',seconds=time.time()-start,nativeSHA256=sha(native),body13SHA256=sha(before),originalCount=len(a['payload']),changed06=changed06,modifierChanges06=mods06,outsideLower26Changes13=outside13,outsideLower26ModifierChanges13=mods13,upper25Count=len(upper13),upper25Changed=[n for n,h in upper13.items() if c['payload'].get(n)!=h],visibilityOutside149Changes=vc,hideWhitelistCount=len(allhide),hideWhitelistActual=allhide,hideWhitelistAll=[True,False,True]==next(iter(allhide.values())) and all(v[0] and v[2] for v in allhide.values()),graphsCount=len(a['graphs']),graphsExact=a['graphs']==c['graphs'],packedCount=len(a['packed']),packedFullBytesMetadataExact=a['packed']==c['packed'],panelCount=len(panels),newPanelCount=len(new),uvNonfiniteOrUnnormalized=uvbad,uvMissing=uvmissing,cornerConventionBad=conventionbad,geometryNonfinite=geomnonfinite,envelope=dict(min=[min(v[i] for v in points) for i in range(3)],max=[max(v[i] for v in points) for i in range(3)]),overlap=dict(method='Odd indexed actual quad centers vs all51 evaluated plate BVHs, world transformed normals, .035 outward origin .075 inward ray, burial>.0002; rootv<=.25 tipv>=.82; static subsample',records=records,panelsWithRootCoverage=sum(x['rootCovered']>0 for x in records),panelsWithTipBurial=sum(x['tipBuried']>0 for x in records),tipSamples=sum(x['tipSamples'] for x in records),tipBuried=sum(x['tipBuried'] for x in records)),frames=frames)
Path('/tmp/cg-qc15-body-native.json').write_text(json.dumps(result,indent=2));print('QC15_NATIVE_DONE',json.dumps({k:v for k,v in result.items() if k not in ['hideWhitelistActual','frames','overlap']}),flush=True)
