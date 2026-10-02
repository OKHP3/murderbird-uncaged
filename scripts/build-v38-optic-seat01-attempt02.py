"""One-pass passive optic-seat/cheek-bridge proposal from frozen hanging-breast01 attempt02."""
from pathlib import Path
import bpy, bmesh, hashlib, json, math, shutil, struct
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'assets/audit/whole-character-v38/optic-seat01/attempt02'
OUT=ROOT/'assets/models/whole-character-v38/optic-seat01/attempt02'
BASE=ROOT/'assets/models/whole-character-v38/hanging-breast01/attempt02/murderbird-v38-hanging-breast01-attempt02.blend'
BASE_GLB=BASE.with_name(BASE.stem+'-rigid.glb')
NATIVE=OUT/'murderbird-v38-optic-seat01.blend'
GLB=OUT/'murderbird-v38-optic-seat01-rigid.glb'
RECEIPT=AUDIT/'receipt.json'
REFERENCE=ROOT/'context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
EXPECTED_NATIVE='d32f187f98e34827f31828035d81324ee3af9f28a2aeb21e9d869e16d8d5192d'
EXPECTED_GLB='051477ffcf62a4e08a3f1968d6cec7fd7f8b0677661cd72dde6ad7bbd5514650'
assert sha(BASE)==EXPECTED_NATIVE and sha(BASE_GLB)==EXPECTED_GLB, 'Frozen hanging-breast02 input identity mismatch'
assert REFERENCE.is_file() and REFERENCE.stat().st_size>1000, 'Actual July head reference unavailable'
assert not NATIVE.exists() and not GLB.exists() and not RECEIPT.exists(), 'Write-once optic-seat01 output already exists; preserve it'
OUT.mkdir(parents=True,exist_ok=True)

TARGETS=[f'V31 optic recessed receiving cup {s}' for s in (-1,1)]+[f'V38 facial-shell cheek bridge {s}' for s in (-1,1)]
VIEWS=[
 ('head-three-quarter',(-6,-3.5,2.55),(0,-.47,1.73),.76),
 ('head-profile',(-7,0,1.76),(0,-.47,1.73),.76),
 ('whole-bird-three-quarter',(-6,-3.5,2.75),(0,-.08,1.03),2.4),
]
CY,CZ=-.5958000421524048,1.6904840469360352

def matrix(m): return [list(row) for row in m]
def props(o): return {k:json.loads(json.dumps(v,default=str)) for k,v in o.items()}
def mesh_sig(o):
 d={'verts':[list(v.co) for v in o.data.vertices], 'faces':[(list(p.vertices),p.material_index,p.use_smooth) for p in o.data.polygons], 'materials':[m.name if m else None for m in o.data.materials]}
 return hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
def snapshot():
 bpy.context.view_layer.update()
 return {o.name:{'type':o.type,'parent':o.parent.name if o.parent else None,'matrixWorld':matrix(o.matrix_world),'matrixLocal':matrix(o.matrix_local),'mesh':mesh_sig(o) if o.type=='MESH' else None,'visibility':[o.hide_render,o.hide_viewport,o.hide_get()],'props':props(o),'materials':[m.name if m else None for m in o.data.materials] if o.type=='MESH' else []} for o in bpy.data.objects}

def read_glb(path):
 raw=Path(path).read_bytes(); magic,version,total=struct.unpack_from('<4sII',raw)
 assert magic==b'glTF' and version==2 and total==len(raw), 'Malformed GLB'
 chunks=[];off=12
 while off<len(raw):
  size,kind=struct.unpack_from('<II',raw,off);off+=8;chunks.append((kind,raw[off:off+size]));off+=size
 return chunks,json.loads(chunks[0][1])

def art(path): return {'path':str(Path(path).relative_to(ROOT)),'bytes':Path(path).stat().st_size,'sha256':sha(path)}

def set_neutral_render():
 scene=bpy.context.scene
 for o in bpy.data.objects:
  if o.type=='MESH': o.hide_render=o.get('silhouetteStudyHistoricalHidden') is True or o.get('authoringGuide') is True or 'builder' not in str(o.get('exteriorEras','maker,mechanic,builder')).split(',')
  elif o.type=='CURVE': o.hide_render=True
 scene.render.engine='BLENDER_WORKBENCH'; shade=scene.display.shading;shade.light='STUDIO';shade.studio_light='paint.sl';shade.color_type='SINGLE';shade.single_color=(.56,.58,.60);shade.show_shadows=False;shade.show_cavity=True;shade.cavity_type='BOTH';shade.background_type='WORLD';scene.world.color=(.12,.13,.14)
 scene.render.resolution_x=scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 return scene

def render_set(prefix):
 scene=set_neutral_render(); camdata=bpy.data.cameras.new('optic-seat01 matched review camera');camdata.type='ORTHO';cam=bpy.data.objects.new(camdata.name,camdata);scene.collection.objects.link(cam);scene.camera=cam;records=[]
 for name,pos,target,scale in VIEWS:
  cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();camdata.ortho_scale=scale
  p=AUDIT/f'{prefix}-{name}.png';assert not p.exists(),f'Preserve existing image: {p}';scene.render.filepath=str(p);bpy.ops.render.render(write_still=True)
  records.append({**art(p),'size':[720,720],'camera':{'position':pos,'target':target,'orthoScale':scale},'lighting':'neutral Workbench, matched source/candidate'})
  print('IMAGE',p,flush=True)
 bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(camdata);scene.camera=None
 return records

def assign_mesh(obj,world_vertices,faces):
 oldmats=[m for m in obj.data.materials]
 mesh=bpy.data.meshes.new(obj.name+' optic-seat01 formed proposal');mesh.from_pydata([obj.matrix_world.inverted()@Vector(v) for v in world_vertices],[],faces);mesh.update()
 for mat in oldmats: mesh.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));volume=bm.calc_volume(signed=True)
 if volume<0: bmesh.ops.reverse_faces(bm,faces=list(bm.faces));volume=-volume
 nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.to_mesh(mesh);bm.free();obj.data=mesh
 for face in mesh.polygons: face.use_smooth=False
 assert volume>0 and nonmanifold==0,(obj.name,volume,nonmanifold)
 return {'signedVolumeM3':volume,'nonmanifoldEdges':nonmanifold,'vertices':len(mesh.vertices),'faces':len(mesh.polygons)}

def rebuild_cup(obj,side):
 # Tapered, shouldered cross-section seats beneath the cheek plate; its through-aperture and lens stay fixed.
 profile=[(.1320,.0410),(.1340,.0475),(.1370,.0510),(.1405,.0492),(.1470,.0462),(.1510,.0448),(.1530,.0426),(.1510,.0400),(.1470,.0388),(.1370,.0388),(.1330,.0395)]
 n=96;verts=[];faces=[]
 for x,r in profile:
  for i in range(n):
   a=2*math.pi*i/n;verts.append((side*x,CY+r*math.cos(a),CZ+r*math.sin(a)))
 for k in range(len(profile)):
  kn=(k+1)%len(profile)
  for i in range(n):
   j=(i+1)%n;faces.append((k*n+i,k*n+j,kn*n+j,kn*n+i))
 rec=assign_mesh(obj,verts,faces);obj['opticSeat01']='Proposal: tapered passive receiver seated beneath formed cheek bridge; optic center, lens and control socket unchanged';obj['surfaceRole']='optic-receiving-seat';obj['constructionDescription']='Finite rigid head-owned machined seat with a stepped outer land and unchanged open optic aperture; reconstructed proposal, not engineering evidence.'
 return rec

def seat_bridge(obj,side):
 # Pull only the orbital rim of the existing continuous cheek plate inward to nest over the receiver shoulder.
 before=[obj.matrix_world@v.co for v in obj.data.vertices];after=[];touched=0
 for p in before:
  r=math.hypot(p.y-CY,p.z-CZ)
  if .0395<=r<.0575:
   t=max(0.0,min(1.0,(.0575-r)/(.0575-.0395)));smooth=t*t*(3-2*t);delta=.0032*smooth
   q=Vector((p.x,CY+(p.y-CY)*(r-delta)/r,CZ+(p.z-CZ)*(r-delta)/r));touched+=1
  else:q=p.copy()
  after.append(tuple(q))
 rec=assign_mesh(obj,after,[list(poly.vertices) for poly in obj.data.polygons]);obj['opticSeat01']='Proposal: existing continuous head cheek plate formed into a shallow socket land; open cheek window retained.';obj['constructionDescription']='Existing passive cheek bridge with a locally formed receiving shoulder nested over the optic seat; remaining contour retained. Surface fit is a reconstruction proposal, not an engineering claim.'
 return {**rec,'locallyReformedVertices':touched,'maximumRadialSetbackM':.0032,'openingTargetRadiusM':.040}

def add_formed_orbital_arch(obj,side):
 # One finite C-shaped shell is an extension of the existing cheek-bridge mesh. Its open lower-front quadrant preserves the cheek window.
 na,nr=80,8;start,end=math.radians(38),math.radians(230);inner=.046;verts=[];faces=[]
 def outer(t): return .062+.010*math.sin(math.pi*t)
 def front_x(u):
  q=u*u*(3-2*u);return .136+.019*q
 # Two closed surface skins sweep from a tucked receiver foot to the visible outer cheek.
 for layer in (0,1):
  for j in range(nr+1):
   u=j/nr
   for i in range(na+1):
    t=i/na;a=start+(end-start)*t;rad=inner+(outer(t)-inner)*u;x=front_x(u)-(.006 if layer else 0)
    verts.append((side*x,CY+rad*math.cos(a),CZ+rad*math.sin(a)))
 stride=na+1;sheet=(nr+1)*stride;total=2*sheet
 for layer in (0,1):
  base=layer*sheet
  for j in range(nr):
   for i in range(na):
    a=base+j*stride+i;b=a+1;c=a+stride+1;d=a+stride;faces.append((a,b,c,d) if layer==0 else (d,c,b,a))
 # Close radial sides and both ends to retain finite stock.
 for j in range(nr):
  for i in (0,na):
   a=j*stride+i;b=(j+1)*stride+i;faces.append((a,b,sheet+b,sheet+a))
 for i in range(na):
  a=i;b=i+1;faces.append((a,sheet+a,sheet+b,b))
  a=nr*stride+i;b=a+1;faces.append((a,b,sheet+b,sheet+a))
 old=obj.data;oldv=[obj.matrix_world@v.co for v in old.vertices];oldf=[list(p.vertices) for p in old.polygons];offset=len(oldv)
 allv=[tuple(p) for p in oldv]+verts;allf=oldf+[tuple(offset+q for q in f) for f in faces]
 rec=assign_mesh(obj,allv,allf)
 obj['opticSeat01']='Proposal: continuous cheek bridge with a seated C-shaped orbital arch; open lower-front cheek window retained.'
 obj['constructionDescription']='Existing head cheek bridge extended into a finite flared arch that nests beneath the passive optic receiver. Lower-front opening remains clear; contact is proposed geometry, not engineering evidence.'
 return {**rec,'formedArch':{'angularExtentDegrees':[38,230],'innerRadiusM':inner,'outerRadiusM':[.062,.072],'wallM':.006,'openCheekWindowDegrees':168}}

def surface_overlap(a,b):
 # Blender's per-object BVHs can be object-local; explicitly transform evaluated triangles into world space first.
 dg=bpy.context.evaluated_depsgraph_get()
 def world_tree(obj):
  evaluated=obj.evaluated_get(dg);mesh=evaluated.to_mesh();mesh.calc_loop_triangles();world=evaluated.matrix_world.copy()
  verts=[world@v.co for v in mesh.vertices];tris=[tuple(t.vertices) for t in mesh.loop_triangles]
  tree=BVHTree.FromPolygons(verts,tris,all_triangles=True);evaluated.to_mesh_clear();return tree
 return len(world_tree(a).overlap(world_tree(b)))

def jaw_checks():
 jaw=bpy.data.objects['jaw'];base=jaw.matrix_basis.copy();targets=[bpy.data.objects[n]for n in TARGETS];deps=[]
 def belongs(o):
  p=o.parent
  while p:
   if p==jaw:return True
   p=p.parent
  return False
 jaw_meshes=[o for o in bpy.data.objects if o.type=='MESH' and belongs(o)]
 assert jaw_meshes,'No jaw-owned mesh descendants found for scoped pose checks'
 for ang in (0,.16,.32):
  jaw.matrix_basis=base@Matrix.Rotation(ang,4,'X');bpy.context.view_layer.update();pairs=[]
  for target in targets:
   count=sum(surface_overlap(target,part) for part in jaw_meshes)
   if count:pairs.append({'target':target.name,'intersectingTrianglePairs':count})
  deps.append({'jawLocalXRad':ang,'status':'NO_TRIANGLE_OVERLAP' if not pairs else 'OVERLAP_REVIEW','overlaps':pairs,'scope':'jaw versus four edited optic seat/cheek meshes'})
 jaw.matrix_basis=base;bpy.context.view_layer.update();return deps

# Freeze and show source state first so the paired view exists before geometry work proceeds.
bpy.ops.wm.open_mainfile(filepath=str(BASE));source_images=render_set('source');bpy.ops.wm.open_mainfile(filepath=str(BASE));before=snapshot()
source_names={n.get('name') for n in read_glb(BASE_GLB)[1]['nodes']}
assert set(TARGETS)<=set(before) and set(TARGETS)<=source_names,'A required active node is absent from the retained source'
material_names=[m.get('name') for m in read_glb(BASE_GLB)[1]['materials']]
assert len(material_names)==12 and len(set(material_names))==12,'Expected exact original twelve-material source profile'

changed_records={}
for side in (-1,1):
 cup=bpy.data.objects[f'V31 optic recessed receiving cup {side}'];bridge=bpy.data.objects[f'V38 facial-shell cheek bridge {side}']
 changed_records[cup.name]=rebuild_cup(cup,side);changed_records[bridge.name]=seat_bridge(bridge,side);changed_records[bridge.name].update(add_formed_orbital_arch(bridge,side))
 assert cup.parent.name=='head' and bridge.parent.name=='head'
 for ob in (cup,bridge):
  assert ob.get('exteriorEras')=='maker,mechanic,builder' and ob.get('constructionClass')=='inherited-passive'

after=snapshot();changed={n for n in set(before)&set(after) if before[n]!=after[n]};assert changed==set(TARGETS),f'Unexpected changes outside four target meshes: {sorted(changed-set(TARGETS))}'
assert set(before)==set(after),'Object inventory changed'
for n in set(before)-set(TARGETS): assert before[n]==after[n],f'Unrelated source object changed: {n}'

bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(NATIVE),check_existing=False)
bpy.ops.wm.open_mainfile(filepath=str(NATIVE));assert snapshot()==after,'Saved native does not match declared geometry/attachment snapshot'

# Export exactly the retained source GLB node set; do not reintroduce native-only historical hidden geometry.
bpy.ops.object.select_all(action='DESELECT');selected=[]
for name in sorted(source_names):
 ob=bpy.data.objects.get(name)
 if ob and ob.type in ('EMPTY','MESH'):
  ob.hide_set(False);ob.hide_viewport=False;ob.select_set(True);selected.append(ob)
bpy.ops.export_scene.gltf(filepath=str(GLB),export_format='GLB',use_selection=True,export_yup=True,export_apply=False,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_materials='EXPORT')
chunks,doc=read_glb(GLB);_,base_doc=read_glb(BASE_GLB);source_mats={m['name']:m for m in base_doc['materials']}
for i,m in enumerate(doc['materials']):
 name=m.get('name');assert name in source_mats,f'Unexpected material {name}';doc['materials'][i]=json.loads(json.dumps(source_mats[name]))
payload=json.dumps(doc,separators=(',',':')).encode();payload+=b' '*((-len(payload))%4);raw=bytearray(struct.pack('<4sII',b'glTF',2,0))
for kind,data in chunks:
 value=payload if kind==0x4e4f534a else data;raw+=struct.pack('<II',len(value),kind)+value
struct.pack_into('<I',raw,8,len(raw));GLB.write_bytes(raw)
_,exported=read_glb(GLB);export_names={n['name'] for n in exported['nodes']};assert export_names==source_names,'Export node identities changed outside geometry payload'
export_materials=[m['name'] for m in exported['materials']];assert set(export_materials)==set(material_names) and len(export_materials)==12,'Source material identities changed'

bpy.ops.wm.open_mainfile(filepath=str(NATIVE));candidate_images=render_set('candidate');pose_checks=jaw_checks()
for p,label in ((Path(__file__),'executed-builder.py'),):
 shutil.copy2(p,AUDIT/label)
mesh_after={n:mesh_sig(bpy.data.objects[n]) for n in TARGETS}
receipt={
 'status':'Single-pass optic receiver and cheek-bridge construction proposal; integration/visual review pending',
 'inputs':{'native':art(BASE),'rigidGlb':art(BASE_GLB),'julyHeadReference':art(REFERENCE)},
 'outputs':{'native':art(NATIVE),'rigidGlb':art(GLB)},
 'scope':{'changedExistingMeshNodes':sorted(TARGETS),'addedNodes':[],'removedNodes':[],'allOtherNativeObjectsExact':True,'headParentAndAllEraEligibilityPreserved':True,'originalTwelveMaterialsExact':True,'sourceGlbEligibleNodeSetPreserved':True,'historicalNativeOnlyNodesReintroduced':False},
 'geometry':changed_records,
 'signatures':{'before':{n:before[n]['mesh'] for n in sorted(TARGETS)},'after':mesh_after,'preservedOwnersTransformsEras':{n:{'parent':after[n]['parent'],'matrixWorld':after[n]['matrixWorld'],'exteriorEras':after[n]['props'].get('exteriorEras'),'constructionClass':after[n]['props'].get('constructionClass')} for n in sorted(TARGETS)}},
 'views':{'source':source_images,'candidate':candidate_images},
 'jawPoseChecks':pose_checks,
 'visualScope':'July view used for head identity only. Deep hooked bill, jaw mesh/pivot/socket, optic lens/center, crown, neck, breast and body are preserved. The local cheek opening remains through the changed outer seat land.',
 'limits':['All new seating geometry and contact intent are proposals; Blender geometry is not engineering simulation.','Only the three requested neutral matched views and jaw local-X samples at 0, 0.16, and 0.32 radians were captured.','No owner likeness approval, runtime integration, full build, publication, or deployment is claimed.']
}
RECEIPT.write_text(json.dumps(receipt,indent=2)+'\n');print('CHECKPOINT',json.dumps({'native':receipt['outputs']['native'],'rigidGlb':receipt['outputs']['rigidGlb'],'changed':sorted(changed),'images':[r['path'] for r in source_images+candidate_images],'jawPoseChecks':pose_checks}),flush=True)
