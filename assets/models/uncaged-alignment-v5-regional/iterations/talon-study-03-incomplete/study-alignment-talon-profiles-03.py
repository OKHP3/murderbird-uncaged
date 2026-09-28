"""Refine six talon sheaths from talon-study-02: broader, flatter forged blades."""
from __future__ import annotations
import bpy, hashlib, json, math, shutil, struct
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'assets/models/uncaged-alignment-v5-regional/iterations/talon-study-02/murderbird-talon-profile-study-02.blend'
SRC_GLB=ROOT/'assets/models/uncaged-alignment-v5-regional/iterations/talon-study-02/murderbird-talon-profile-study-02.glb'
SRC_MANIFEST=ROOT/'assets/models/uncaged-alignment-v5-regional/iterations/talon-study-02/study-manifest.json'
C8_BLEND=ROOT/'assets/models/uncaged-alignment-v5-regional/candidate/input-snapshots/c8-limb-compatibility-source/murderbird-alignment-v5.blend'
C8_INV=ROOT/'assets/models/uncaged-alignment-v5-regional/candidate/input-snapshots/c8-limb-compatibility-source/alignment-inventory.json'
OUT=ROOT/'assets/models/uncaged-alignment-v5-regional/iterations/talon-study-03'
OUT_BLEND=OUT/'murderbird-talon-profile-study-03.blend'; OUT_GLB=OUT/'murderbird-talon-profile-study-03.glb'; MAN=OUT/'study-manifest.json'; SNAP=OUT/'study-alignment-talon-profiles-03.py'
SHA_SRC='40322c404bef7a1d281658d80f315e36c87efdd981d8358cdc43fd32af49655c'; SHA_SRC_GLB='c0c98700bfd7b043e20a85d7e65132fd363ce68dfc1b4cd87ac0c6650ebc5765'; SHA_C8='cc6bfafc9ab044bba1abcbec86761afb9ef67ee60e252ec7ee838948ea7dfd04'; SHA_C8_INV='5fda3638038b0a5d4c040544a2b419962cd33c55c9a3f0edc416aef4c18b7ee0'
TALONS=[f'{s} digit {d} tapered claw sheath' for s in ('left','right') for d in (1,2,3)]
RING=16

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p): return {'path':Path(p).relative_to(ROOT).as_posix(),'bytes':Path(p).stat().st_size,'sha256':sha(p)}
def need(x,m):
 if not x: raise RuntimeError('talon study 03 refused: '+m)
def mat(o): return [round(float(o.matrix_world[r][c]),10) for r in range(4) for c in range(4)]
def xf(o): return {'parent':o.parent.name if o.parent else None,'matrix':mat(o),'location':tuple(float(x) for x in o.location),'rotation':tuple(float(x) for x in o.rotation_euler),'scale':tuple(float(x) for x in o.scale)}
def sig(o):
 h=hashlib.sha256();h.update(o.name.encode());h.update((o.parent.name if o.parent else '').encode());h.update(struct.pack('<II',len(o.data.vertices),len(o.data.polygons)))
 for v in o.data.vertices:h.update(struct.pack('<3f',*v.co))
 for p in o.data.polygons:h.update(struct.pack('<I',len(p.vertices)));h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices));h.update(struct.pack('<i?',p.material_index,p.use_smooth))
 for m in o.modifiers:h.update((m.name+':'+m.type).encode())
 return h.hexdigest()
def walk_rings(obj, expected):
 mesh=obj.data; caps=[list(p.vertices) for p in mesh.polygons if len(p.vertices)==RING]
 need(len(caps)==2,f'{obj.name}: expected two 16-vertex cap rings')
 cy=[sum((obj.matrix_world@mesh.vertices[i].co).y for i in cap)/RING for cap in caps]
 start=caps[max(range(2),key=lambda i:cy[i])]; end=set(caps[min(range(2),key=lambda i:cy[i])])
 quads=[list(p.vertices) for p in mesh.polygons if len(p.vertices)==4]; rings=[start]; seen=set(start); cur=start
 for _ in range(expected-1):
  mapping={}
  for k,a in enumerate(cur):
   b=cur[(k+1)%RING]; matches=[]
   for q in quads:
    if any({q[j],q[(j+1)%4]}=={a,b} for j in range(4)) and not (set(q)-{a,b})&seen: matches.append(q)
   need(len(matches)==1,f'{obj.name}: ambiguous ring transition')
   q=matches[0]
   for j in range(4):
    qa,qb=q[j],q[(j+1)%4]
    if qa==a and qb==b: mapping[a],mapping[b]=q[(j+3)%4],q[(j+2)%4];break
    if qa==b and qb==a: mapping[a],mapping[b]=q[(j+2)%4],q[(j+3)%4];break
  nxt=[mapping.get(i,-1) for i in cur]
  need(min(nxt)>=0 and len(set(nxt))==RING and not set(nxt)&seen,f'{obj.name}: invalid ring walk')
  rings.append(nxt);seen.update(nxt);cur=nxt
 need(set(rings[-1])==end and len(rings)==expected,f'{obj.name}: terminal cap/ring count mismatch')
 return rings
def evaluated(o):
 ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
 try:
  pts=[tuple(float(x) for x in v.co) for v in m.vertices]
  return {'vertices':len(m.vertices),'triangles':sum(max(0,len(p.vertices)-2) for p in m.polygons),'bounds':{'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)]},'finite':all(math.isfinite(x) for p in pts for x in p)}
 finally:ev.to_mesh_clear()
def glb(path):
 raw=Path(path).read_bytes();need(raw[:4]==b'glTF','invalid GLB');n,t=struct.unpack_from('<I4s',raw,12);need(t==b'JSON','missing GLB JSON');doc=json.loads(raw[20:20+n].decode().rstrip(' \0')); out={}
 for node in doc.get('nodes',[]):
  if 'mesh' not in node:continue
  mesh=doc['meshes'][node['mesh']];tris=0;pos=[]
  for prim in mesh['primitives']:
   a=doc['accessors'][prim['attributes']['POSITION']];pos.append({'count':a['count'],'min':a.get('min'),'max':a.get('max')})
   if 'indices' in prim:tris+=doc['accessors'][prim['indices']]['count']//3
  out[node['name']]={'triangles':tris,'position':pos}
 return out
def axes_fit(vals,lo,hi):
 mean=sum(vals)/len(vals); q=[x-mean for x in vals];high=max(q);low=min(q);scale=1.0
 if high>1e-12:scale=min(scale,hi/high)
 if low<-1e-12:scale=min(scale,lo/low)
 scale=max(0.0,min(1.0,scale));return [x*scale for x in q]
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)

need(SRC.is_file() and SRC_GLB.is_file() and SRC_MANIFEST.is_file() and C8_BLEND.is_file() and C8_INV.is_file(),'source file missing')
need(sha(SRC)==SHA_SRC and sha(SRC_GLB)==SHA_SRC_GLB,'talon02 source identity mismatch')
need(sha(C8_BLEND)==SHA_C8 and sha(C8_INV)==SHA_C8_INV,'c8 compatibility source mismatch')
need(not OUT.exists(),'refusing existing output')
need(Path(bpy.data.filepath).resolve()==SRC.resolve(),'Blender must open exact talon02 native input')
src_manifest=json.loads(SRC_MANIFEST.read_text()); c8_inventory=json.loads(C8_INV.read_text());parts={p['name']:p for p in c8_inventory.get('parts',[])}
objects={o.name:o for o in bpy.data.objects};need(set(TALONS)<=set(objects),'talon objects missing')
for name in TALONS:
 o=objects[name]; p=parts.get(name)
 need(o.type=='MESH' and o.parent and o.parent.name==p['parent'],f'{name}: owner disagrees with c8 inventory')
 need(o.get('region')==p['region'] and o.get('surfaceRole')==p['role'],f'{name}: region/role mismatch')
 need(not o.modifiers and not o.data.uv_layers,f'{name}: unsupported modifier/UV topology')
# Bring in immutable c8 talon meshes and exact owners as a temporary comparison reference.
owner_names=sorted({parts[n]['parent'] for n in TALONS})
requested_names=tuple(TALONS+owner_names)
with bpy.data.libraries.load(str(C8_BLEND),link=False) as (src,dst):
 need(set(requested_names)<=set(src.objects),'c8 source object names missing');dst.objects=list(requested_names)
imported={}
for name,obj in zip(requested_names,dst.objects):
 need(obj is not None,f'could not append c8 reference {name}');bpy.context.scene.collection.objects.link(obj);imported[name]=obj
bpy.context.view_layer.update()
source_c8={n:imported[n] for n in TALONS}
for n in TALONS:need(len(source_c8[n].data.vertices)==272,f'{n}: c8 ring topology mismatch')
# Capture source scene identities before removing temporary reference objects.
pivots_before={o.name:xf(o) for o in bpy.data.objects if o.type=='EMPTY' and o not in imported.values()}
mesh_before={o.name:sig(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in TALONS and o not in imported.values()}
scene_mesh_count=sum(o.type=='MESH' for o in bpy.data.objects)-len(TALONS)
results=[]
for name in TALONS:
 obj=objects[name]; ref=source_c8[name]; input_mesh_signature=sig(obj)
 need(obj.parent.name==ref.parent.name.removesuffix('.001'),f'{name}: imported c8 owner differs')
 cand_rings=walk_rings(obj,18); c8_rings=walk_rings(ref,17)
 need(len(obj.data.vertices)==288 and len(ref.data.vertices)==272,f'{name}: unexpected talon vertex topology')
 c8_world=[ref.matrix_world@v.co for v in ref.data.vertices]
 cand_world=[obj.matrix_world@v.co for v in obj.data.vertices]
 c8_centers=[sum((c8_world[i] for i in ring),Vector())/RING for ring in c8_rings]
 cand_centers=[sum((cand_world[i] for i in ring),Vector())/RING for ring in cand_rings]
 for ri in range(14):need((cand_centers[ri]-c8_centers[ri]).length<2e-6,f'{name}: talon02 changed ring centerline at {ri}')
 for ri in range(14):need(set(cand_rings[ri])==set(c8_rings[ri]),f'{name}: pre-tip ring vertex correspondence changed')
 src_coords=[v.co.copy() for v in obj.data.vertices]
 source_terminal=[(i,src_coords[i].copy()) for ring in cand_rings[14:] for i in ring]
 max_delta=0.0;center_err=[];lat_over=[];floor_over=[];changed=[]
 inv=obj.matrix_world.inverted()
 for ri in range(14):
  t=ri/16.0
  center=c8_centers[ri]
  tangent=(c8_centers[min(ri+1,16)]-c8_centers[max(ri-1,0)]).normalized()
  normal=Vector((0.0,-tangent.z,tangent.y));need(normal.length>1e-8,f'{name}: degenerate section normal');normal.normalize()
  base_pts=[c8_world[i] for i in c8_rings[ri]]
  cur_pts=[cand_world[i] for i in cand_rings[ri]]
  base_u=[(p-center).x for p in base_pts];base_v=[(p-center).dot(normal) for p in base_pts]
  cur_v=[(p-center).dot(normal) for p in cur_pts]
  ur=max(abs(min(base_u)),abs(max(base_u))); vr=max(abs(min(base_v)),abs(max(base_v))); cr=max(abs(min(cur_v)),abs(max(cur_v)))
  need(ur>1e-6 and vr>1e-6 and cr>1e-6,f'{name}: degenerate source section')
  x=[max(-1,min(1,u/ur)) for u in base_u]
  # Broad lateral shoulders fill the c8 source width while the axis fit keeps every point inside it.
  shaped_u=axes_fit([(math.copysign(abs(a)**.70,a) if abs(a)>1e-12 else 0.0)*ur for a in x],min(base_u),max(base_u))
  # Flatten both faces around the unchanged centerline; the dorsal crest is shallow and narrow.
  root_thickness=.58+.17*smooth(t/.68)
  shaped_v=[]
  for (v,uu) in zip(cur_v,base_u):
   y=max(-1,min(1,v/cr)); xx=max(-1,min(1,uu/ur))
   ridge=.010*vr*max(0.0,y*normal.z)**3*math.exp(-((xx/.32)**2))
   shaped_v.append(y*vr*root_thickness+ridge)
  mean=sum(shaped_v)/len(shaped_v);shaped_v=[v-mean for v in shaped_v]
  shaped_v=axes_fit(shaped_v,min(base_v),max(base_v))
  # Fade back to the exact c8 surface across the last two proximal rings; t>=.85 stays byte-identical to input geometry.
  weight=1.0 if t<=.68 else 1.0-smooth((t-.68)/(.17))
  for k,index in enumerate(cand_rings[ri]):
   old=cand_world[index];target=center+Vector((shaped_u[k],0,0))+normal*shaped_v[k]
   new=old.lerp(target,weight)
   obj.data.vertices[index].co=inv@new
   delta=(new-old).length;max_delta=max(max_delta,delta)
   if delta>1e-9:changed.append(index)
  now=[obj.matrix_world@obj.data.vertices[i].co for i in cand_rings[ri]]
  after=sum(now,Vector())/RING
  center_err.append((after-cand_centers[ri]).length)
  base_lo=min(p.z for p in base_pts);base_xlo=min((p-center).x for p in base_pts);base_xhi=max((p-center).x for p in base_pts)
  for p in now:
   lat_over.append(max(base_xlo-(p-center).x,(p-center).x-base_xhi,0.0))
   floor_over.append(max(0.0,base_lo-p.z))
 obj.data.update();bpy.context.view_layer.update()
 # The rings from exact t=.85 to the tip, including all terminal vertices, remain exactly talon02 source bytes.
 terminal_exact=all((obj.data.vertices[i].co-co).length<1e-9 for i,co in source_terminal)
 need(terminal_exact,f'{name}: exact t=.85/tip rings changed')
 ev=evaluated(obj);need(ev['finite'] and ev['triangles']>0,f'{name}: evaluated mesh invalid')
 need(max(center_err)<2e-6,f'{name}: centerline shifted')
 need(max(lat_over)<2e-6,f'{name}: lateral c8 envelope exceeded')
 need(max(floor_over)<2e-6,f'{name}: ventral c8 ground envelope extended')
 results.append({'name':name,'parent':obj.parent.name,'region':obj.get('region'),'role':obj.get('surfaceRole'),'inputStudy02MeshSha256':input_mesh_signature,'topology':{'inputVertices':len(src_coords),'outputVertices':len(obj.data.vertices),'rings':18,'verticesPerRing':RING,'terminalRingsUntouched':True},'profile':{'method':'cross-section swept broad forged blade; lateral profile exponent .70 fitted inside c8 envelope; normal section height 58% at root rising smoothly then fading to exact c8 surface at t=.85','rootNormalThicknessFactor':.58,'distalNormalThicknessFactorBeforeFade':.75,'dorsalCrestFractionOfC8SectionRadius':.010,'modifiedCandidateRingIndices':list(range(14)),'exactInputRingIndices':list(range(14,18))},'changedOriginalVertexIndices':sorted(set(changed)),'maxVertexDisplacementM':max_delta,'centerlineMaxErrorM':max(center_err),'maxLateralEnvelopeOverrunM':max(lat_over),'maxVentralEnvelopeOverrunM':max(floor_over),'evaluatedBeforeSave':ev,'_terminalVertices':[(i,tuple(float(c) for c in co)) for i,co in source_terminal]})
# Remove appended c8 geometry and owner objects; do not export duplicated refs.
for o in imported.values(): bpy.data.objects.remove(o,do_unlink=True)
bpy.context.view_layer.update()
need(sum(o.type=='MESH' for o in bpy.data.objects)==scene_mesh_count,'temporary source refs leaked into native scene')
for n,s in mesh_before.items():need(sig(objects[n])==s,'non-talon mesh changed '+n)
need({o.name:xf(o) for o in bpy.data.objects if o.type=='EMPTY'}==pivots_before,'pivot transforms changed before save')
OUT.mkdir(parents=True);SNAP.write_bytes(Path(__file__).read_bytes())
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND),check_existing=False)
# Reopen exact saved native and verify all non-target geometry, rig empties, and terminal arrays.
bpy.ops.wm.open_mainfile(filepath=str(OUT_BLEND));objects={o.name:o for o in bpy.data.objects}
for n,s in mesh_before.items():need(sig(objects[n])==s,'saved native changed non-talon mesh '+n)
need({o.name:xf(o) for o in bpy.data.objects if o.type=='EMPTY'}==pivots_before,'saved native changed pivots')
for row in results:
 obj=objects[row['name']];need(obj.parent.name==row['parent'],'saved owner mismatch')
 for i,co in row['_terminalVertices']:need((obj.data.vertices[i].co-Vector(co)).length<1e-9,'saved native moved exact t=.85/tip vertex')
 row['savedNativeTerminalRingsExact']=True
# Evaluated mesh export contract: apply modifiers, mesh+empty only.
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
 if o.type in {'MESH','EMPTY'}:o.hide_set(False);o.select_set(True)
r=bpy.ops.export_scene.gltf(filepath=str(OUT_GLB),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_extras=True,export_animations=True,export_animation_mode='ACTIONS',export_frame_range=True,export_cameras=False,export_lights=False)
need('FINISHED' in r and OUT_GLB.is_file(),'GLB export failed')
out_meshes=glb(OUT_GLB)
for row in results:
 row.pop('_terminalVertices',None)
 m=out_meshes.get(row['name']);need(m is not None,'changed talon absent from GLB '+row['name'])
 ev=row['evaluatedBeforeSave'];need(m['triangles']==ev['triangles'],row['name']+': evaluated/export triangle count mismatch')
 b=ev['bounds'];expected={'min':[b['min'][0],b['min'][2],-b['max'][1]],'max':[b['max'][0],b['max'][2],-b['min'][1]]};actual=m['position'][0]
 need(all(abs(expected[k][i]-actual[k][i])<1e-5 for k in ('min','max') for i in range(3)),row['name']+': evaluated/export bounds mismatch')
 row['exported']={'triangles':m['triangles'],'position':m['position'],'evaluatedModifierGeometryMatched':True}
# Compare unmodified export payloads only as evidence; report packaging differences without treating them as a mesh-edit claim.
src_meshes=glb(SRC_GLB); common=sorted(set(src_meshes)&set(out_meshes)-set(TALONS)); exact=[]
for n in common:
 if src_meshes[n]==out_meshes[n]:exact.append(n)
manifest={'schema':'alignment-talon-profile-study/v2','status':'isolated six-talon profile refinement; visual/contact review pending','scope':'Only the six existing distal talon sheath meshes changed relative to talon-study-02. No knuckle, digit link, hinge, owner, joint, pivot, guard, or non-talon geometry changed. Full candidate04 composition remains separate.','source':{'native':rec(SRC),'glb':rec(SRC_GLB),'studyManifest':rec(SRC_MANIFEST),'c8CompatibilityNative':rec(C8_BLEND),'c8Inventory':rec(C8_INV)},'executedScriptSnapshot':rec(SNAP),'outputs':{'native':rec(OUT_BLEND),'glb':rec(OUT_GLB)},'replacementContract':{'originalSourceIteration':'c8a7a7e14253','baseSource':'talon-study-02','changedObjects':TALONS,'count':6,'ownersPreserved':True,'pivotsPreserved':True,'originalC8TipContactRingsPreserved':True,'c8EnvelopeReferenceNativeSha256':SHA_C8},'profileMethod':{'description':'Wider flattened cross-section fitted per ring to the c8 lateral and ventral envelope; reduces swollen dorsal section near sheath root, preserving sampled centerline and exact study02 rings at/after t=.85.','terminal15PercentExactAgainstStudy02':True,'centerlineSamplesExact':True,'lateralEnvelopeExpandedAgainstC8':False,'ventralEnvelopeExtendedAgainstC8':False,'rootThicknessFactor':.58,'dorsalRidgeFraction':.010,'ringTopologyDerived':True},'changedTalons':results,'pivotCheck':{'inputEmptyCount':len(pivots_before),'outputEmptyCount':sum(o.type=='EMPTY' for o in bpy.data.objects),'allParentAndTransformSignaturesExact':True},'unmodifiedNativeMeshes':{'count':len(mesh_before),'allGeometrySignaturesExact':True},'export':{'selectedTypes':['MESH','EMPTY'],'exportApply':True,'camerasAndLights':False,'changedTalonsEvaluatedTriangleAndBoundsExact':True,'sourceGLBMeshCount':len(src_meshes),'outputGLBMeshCount':len(out_meshes),'sameNamedUntouchedExactPayloadMatches':len(exact),'sameNamedUntouchedCompared':len(common)},'limitations':['No likeness acceptance, dimensional metrology, or mechanical certification. Root owns the repeat claw-contact and kinematic checks.']}
MAN.write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'status':manifest['status'],'native':manifest['outputs']['native'],'glb':manifest['outputs']['glb'],'manifest':rec(MAN),'changed':[{k:r[k] for k in ('name','maxVertexDisplacementM','centerlineMaxErrorM','maxLateralEnvelopeOverrunM','maxVentralEnvelopeOverrunM','evaluatedBeforeSave','exported')} for r in results]},indent=2))
