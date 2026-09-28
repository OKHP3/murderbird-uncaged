"""Isolated instep surface refinement from canonical guard-study-05."""
from __future__ import annotations
import bpy, hashlib, json, math, struct
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'assets/models/uncaged-alignment-v5-regional/iterations/guard-study-05/murderbird-limb-profile-study.blend'
SRC_GLB=ROOT/'assets/models/uncaged-alignment-v5-regional/iterations/guard-study-05/murderbird-limb-profile-study.glb'
SRC_MANIFEST=ROOT/'assets/models/uncaged-alignment-v5-regional/iterations/guard-study-05/manifest.json'
OUT=ROOT/'assets/models/uncaged-alignment-v5-regional/iterations/guard-study-06'
OUT_BLEND=OUT/'murderbird-limb-profile-study-06.blend'; OUT_GLB=OUT/'murderbird-limb-profile-study-06.glb'; OUT_MANIFEST=OUT/'manifest.json'; SNAP=OUT/'generator-script-at-build.py'
EXPECTED_SRC='c1ea75d32edcc2a356589549651553b52fc7b641a17de9a2b9c532ce7050dcc1'; EXPECTED_GLB='d7074699b566dac07d40b226865db766c48cb36be104b0845cec5c2ddf059268'
TARGETS=['left curved instep guard','right curved instep guard']

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def record(p): return {'path':Path(p).relative_to(ROOT).as_posix(),'bytes':Path(p).stat().st_size,'sha256':sha(p)}
def require(x,m):
 if not x: raise RuntimeError('guard study 06 refused: '+m)
def sig(o):
 h=hashlib.sha256(); h.update(o.name.encode()); h.update((o.parent.name if o.parent else '').encode()); h.update(struct.pack('<II',len(o.data.vertices),len(o.data.polygons)))
 for v in o.data.vertices: h.update(struct.pack('<3f',*v.co))
 for p in o.data.polygons: h.update(struct.pack('<I',len(p.vertices))); h.update(struct.pack('<'+'I'*len(p.vertices),*p.vertices)); h.update(struct.pack('<i?',p.material_index,p.use_smooth))
 for m in o.modifiers: h.update((m.name+':'+m.type).encode())
 return h.hexdigest()
def matrix(o): return [round(float(o.matrix_world[r][c]),10) for r in range(4) for c in range(4)]
def evaluated(o):
 deps=bpy.context.evaluated_depsgraph_get(); ev=o.evaluated_get(deps); mesh=ev.to_mesh()
 try:
  pts=[tuple(float(c) for c in v.co) for v in mesh.vertices]
  return {'vertices':len(mesh.vertices),'triangles':sum(max(0,len(p.vertices)-2) for p in mesh.polygons),'bounds':{'min':[min(v[i] for v in pts) for i in range(3)],'max':[max(v[i] for v in pts) for i in range(3)]},'finite':all(math.isfinite(c) for v in pts for c in v)}
 finally: ev.to_mesh_clear()
def glb_meshes(path):
 raw=Path(path).read_bytes(); require(raw[:4]==b'glTF','invalid GLB'); n,typ=struct.unpack_from('<I4s',raw,12); require(typ==b'JSON','GLB JSON missing'); gltf=json.loads(raw[20:20+n].decode().rstrip(' \0'))
 out={}
 for node in gltf.get('nodes',[]):
  if 'mesh' not in node: continue
  mesh=gltf['meshes'][node['mesh']]; triangles=0; pos=[]
  for prim in mesh['primitives']:
   a=gltf['accessors'][prim['attributes']['POSITION']]; pos.append({'min':a.get('min'),'max':a.get('max'),'count':a['count']})
   if 'indices' in prim: triangles+=gltf['accessors'][prim['indices']]['count']//3
  out[node['name']]={'triangles':triangles,'position':pos}
 return out

require(SRC.is_file() and SRC_GLB.is_file() and SRC_MANIFEST.is_file(),'guard05 source triplet missing')
require(sha(SRC)==EXPECTED_SRC and sha(SRC_GLB)==EXPECTED_GLB,'guard05 source hash mismatch')
require(not OUT.exists(),'refusing existing output directory')
source_manifest=json.loads(SRC_MANIFEST.read_text())
require(len(source_manifest.get('newObjects',[]))==10 and len(source_manifest.get('replacedObjects',[]))==26,'guard05 replacement contract differs')
require(Path(bpy.data.filepath).resolve()==SRC.resolve(),'Blender must open exact guard05 native input')
OUT.mkdir(parents=True); SNAP.write_bytes(Path(__file__).read_bytes())
objects={o.name:o for o in bpy.data.objects}
require(set(TARGETS)<=set(objects),'instep surfaces missing')
empty_before={o.name:matrix(o) for o in bpy.data.objects if o.type=='EMPTY'}
mesh_before={o.name:sig(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in TARGETS}
changes=[]
for name in TARGETS:
 obj=objects[name]; owner=obj.parent
 require(owner and owner.name.endswith('-foot'),'instep owner changed')
 require(len(obj.data.vertices)==17*17,'instep must remain regular 17x17 editable grid')
 original=[v.co.copy() for v in obj.data.vertices]
 ankle=owner.matrix_world.translation.copy()
 max_delta=0.0
 for j in range(17):
  u=j/16
  y0=ankle.y-.018-.128*u
  z0=ankle.z-.020-.185*u+.014*math.sin(math.pi*u)
  width=.027+.010*u
  for k in range(17):
   theta=-1.25+2.5*k/16
   old_arch=.021*math.cos(theta)*(.94-.16*u)
   old_return=.0045*math.exp(-(((abs(theta)-.86)/.19)**2))
   old_channel=.0028*math.exp(-((theta/.16)**2))
   old_crown=old_arch+old_return-old_channel
   rel=min(1.0,u/.24); eased=rel*rel*(3-2*rel); old_hinge=.024*(1-eased)
   expected=Vector((ankle.x+math.sin(theta)*width,y0-old_crown,z0+old_crown-old_hinge))
   idx=j*17+k
   require((original[idx]-expected).length<2e-5,f'{name}: source grid/profile identity mismatch at vertex {idx}')
   # One broad smooth cap, with a subtle center spine. No paired flutes, edge rolls or troughs.
   half=max(0.0,math.cos(theta*1.25))
   broad=.0175*(half**1.25)*(.96-.10*u)
   crest=.0010*math.exp(-((theta/.22)**2))*(.92-.08*u)
   crown=broad+crest
   new=Vector((expected.x,y0-crown,z0+crown-old_hinge))
   obj.data.vertices[idx].co=new
   max_delta=max(max_delta,(new-expected).length)
 obj.data.update(); bpy.context.view_layer.update()
 ev=evaluated(obj); require(ev['finite'] and ev['triangles']>0,'invalid evaluated instep surface')
 changes.append({'name':name,'owner':owner.name,'role':obj.get('surfaceRole'),'region':obj.get('region'),'vertexCount':len(obj.data.vertices),'maxSourceProfileVertexDeltaM':max_delta,'evaluatedBeforeSave':ev,'profile':{'method':'17x17 monotonic crowned panel; single shallow center crest; removed paired raised returns and center channel','domePeakM':.0175,'crestPeakM':.0010,'crestWidthTheta':.22,'widthEnvelopePreserved':True,'rowCentersAndHingeReliefPreserved':True}})
for name,s in mesh_before.items(): require(sig(objects[name])==s,f'unrelated mesh changed: {name}')
require({o.name:matrix(o) for o in bpy.data.objects if o.type=='EMPTY'}==empty_before,'empty/pivot transform changed')
# Save editable native first, then export evaluated modifier geometry.
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND),check_existing=False)
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
 if o.type in {'MESH','EMPTY'}: o.hide_set(False); o.select_set(True)
r=bpy.ops.export_scene.gltf(filepath=str(OUT_GLB),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_extras=True,export_animations=True,export_cameras=False,export_lights=False)
require('FINISHED' in r and OUT_GLB.is_file(),'GLB export failed')
exported=glb_meshes(OUT_GLB)
for item in changes:
 mesh=exported.get(item['name']); require(mesh is not None,'changed instep absent from GLB: '+item['name'])
 ev=item['evaluatedBeforeSave']; require(mesh['triangles']==ev['triangles'],f"evaluated/export triangle mismatch for {item['name']}")
 # Export local coordinates apply Blender z-up to GLTF y-up (x,z,-y).
 b=ev['bounds']; expected={'min':[b['min'][0],b['min'][2],-b['max'][1]],'max':[b['max'][0],b['max'][2],-b['min'][1]]}
 actual=mesh['position'][0]
 require(all(abs(expected[k][i]-actual[k][i])<1e-5 for k in ('min','max') for i in range(3)),f"evaluated/export bounds mismatch for {item['name']}")
 item['exported']={'triangles':mesh['triangles'],'position':mesh['position'],'evaluatedModifierGeometryMatched':True}
# Reopen saved native and independently confirm mesh/pivot ownership + signatures.
bpy.ops.wm.open_mainfile(filepath=str(OUT_BLEND)); reopened={o.name:o for o in bpy.data.objects}
require({o.name:matrix(o) for o in bpy.data.objects if o.type=='EMPTY'}==empty_before,'saved native changed pivots')
for name,s in mesh_before.items(): require(sig(reopened[name])==s,'saved native changed unrelated mesh '+name)
for item in changes: require(reopened[item['name']].parent.name==item['owner'],'saved native changed instep owner')
manifest={'schema':'alignment-limb-profile-study/v2','status':'isolated instep refinement; review and motion checks pending','scope':'Exactly two existing curved instep guard meshes changed relative to guard-study-05. No rig empties or pivots moved. The complete original c8 replacement contract remains 26 replaced guard/sheath names and 10 new guard objects; this study adds a two-mesh delta only.','source':{'native':record(SRC),'glb':record(SRC_GLB),'manifest':record(SRC_MANIFEST)},'executedScriptSnapshot':record(SNAP),'outputs':{'native':record(OUT_BLEND),'glb':record(OUT_GLB)},'baseReplacementContract':{'sourceIteration':'c8a7a7e14253','replacedObjects':source_manifest['replacedObjects'],'newObjects':[x['name'] for x in source_manifest['newObjects']],'changedNewObjects':[]},'deltaFromGuardStudy05':{'changedObjects':TARGETS,'count':len(TARGETS),'replacementAllowlistFromC8Unchanged':True},'changes':changes,'unchangedMeshes':{'count':len(mesh_before),'allSourceSignaturesExact':True},'pivots':{'emptyCount':len(empty_before),'allWorldMatricesExact':True},'exportContract':{'selectedTypes':['MESH','EMPTY'],'exportApply':True,'camerasAndLights':False,'evaluatedModifierTriangleAndBoundsChecks':True},'limitations':['No likeness acceptance, dimensional metrology, collision clearance or mechanical certification. Runtime motion/contact review remains outstanding.']}
OUT_MANIFEST.write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'status':manifest['status'],'native':manifest['outputs']['native'],'glb':manifest['outputs']['glb'],'manifest':record(OUT_MANIFEST),'changed':changes},indent=2))
