"""Read-only four-state motion and overlap review of cervical/breast V2.

Uses frozen Node-derived 21-state controller packet and 41-state inspection
packet. Changes only in-memory pivots and render settings; never saves a blend.
"""
from pathlib import Path
import hashlib, json, shutil
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / 'assets/models/uncaged-cervical-breast-transition-study-v2/murderbird-cervical-breast-transition-study-v2.blend'
SOURCE14 = ROOT / 'assets/models/uncaged-cervical-construction-study-v1/attempt-14/murderbird-cervical-construction-study-v1.blend'
SOURCE07 = ROOT / 'assets/models/uncaged-cervical-construction-study-v1/attempt-07/murderbird-cervical-construction-study-v1.blend'
RUNTIME = ROOT / 'assets/audit/cervical-runtime-study-v1/expanded-runtime-poses/pose-snapshot.json'
INSPECTION = ROOT / 'assets/audit/cervical-joint-drive-study-v1/inspection-contract-v1/pose-snapshot.json'
OUT = ROOT / 'assets/audit/cervical-breast-transition-study-v2/independent-envelope-v1'
EXPECTED = {
 'native':'f98d4a5a3dbed932b82ac1abc82e51dc79356321a3a9292ed718749387c403a8',
 'source14':'ef9e28ddbce9d62aabc8181a058640ea1e8b7a339b673df37b913d96699f9440',
 'source07':'751d8149032941774c6ba31824c76f6fa840bb0d767e433bae8000535f3a2b98',
 'runtime':'1cb4a2f75ecae625a44c768ba543e9b99e1caa9791a3056e20f5d88bd73d2f26',
 'inspection':'3ae1b5a0f81adcb70a567e66c906c4631eebf75758171fc7aeddc7bdf8033781',
}
CHANGED = {
 *(f'Throat formed lamina {i}' for i in range(1,7)),
 *(f'Cervical flank lamina {s} {i}' for s in (-1,1) for i in range(1,7)),
 'Upper breast cervical yoke front','Upper breast cervical yoke left','Upper breast cervical yoke right',
}
POSE_IDS = ['runtime-rest','advanced-contact','advanced-recovery-entry','inspection-open-1-separation-0']
C = Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)))
REGION_OWNERS = {'neck','cervical-upper','head','jaw','breastplate','body'}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def bound(path,key):
 assert path.is_file(), f'missing input: {path}'
 actual=sha(path);assert actual==EXPECTED[key], f'{key} hash changed: {actual}'
 return {'path':str(path.relative_to(ROOT)),'bytes':path.stat().st_size,'sha256':actual}
def mat_error(a,b): return max(abs(a[r][c]-b[r][c]) for r in range(4) for c in range(4))
def hierarchy():
 empties={o.name:o for o in bpy.data.objects if o.type=='EMPTY'}
 assert len(empties)==52, f'expected 52 pivots, got {len(empties)}'
 out={}
 for n,o in empties.items():
  out[n]={'parent':o.parent.name if o.parent else None,
          'basis':[[float(o.matrix_basis[r][c]) for c in range(4)] for r in range(4)],
          'world':[[float(o.matrix_world[r][c]) for c in range(4)] for r in range(4)]}
 return out,empties
def converted(flat):
 assert len(flat)==16
 browser=Matrix([[flat[col*4+row] for col in range(4)] for row in range(4)])
 return C.inverted() @ browser @ C
def pose_map(packet): return {p['id']:p for p in packet['poses']}
def set_pose(pose,pivots):
 rows=pose['pivotMatrices']
 if isinstance(rows,list):
  rows={row['name']:row for row in rows if row.get('kind')!='mesh'}
 assert set(pivots)<=set(rows), f"pose missing native pivots {pose['id']}: {set(pivots)-set(rows)}"
 for name,obj in sorted(pivots.items(),key=lambda kv:depth(kv[1])):
  row=rows[name]
  obj.matrix_world=converted(row['worldMatrix'])
  bpy.context.view_layer.update()
 err=max(mat_error(obj.matrix_world,converted(rows[name]['worldMatrix'])) for name,obj in pivots.items())
 assert err<2e-6,(pose['id'],err)
 return err
def depth(o):
 n=0
 while o.parent:n+=1;o=o.parent
 return n
def snap_open(path):
 bpy.ops.wm.open_mainfile(filepath=str(path))
 return hierarchy()[0]
def surface(o,dg):
 ev=o.evaluated_get(dg); me=ev.to_mesh();me.calc_loop_triangles()
 points=[ev.matrix_world@v.co for v in me.vertices]
 tris=[tuple(t.vertices) for t in me.loop_triangles]
 ev.to_mesh_clear()
 if not tris:return None
 return {'tree':BVHTree.FromPolygons(points,tris,all_triangles=True,epsilon=0.0),'points':points,'tris':tris,
         'lo':[min(v[i] for v in points) for i in range(3)],'hi':[max(v[i] for v in points) for i in range(3)]}
def bbox_overlap(a,b):return all(a['lo'][i]<=b['hi'][i] and b['lo'][i]<=a['hi'][i] for i in range(3))
def world_bounds(o):
 corners=[o.matrix_world@Vector(c) for c in o.bound_box]
 return {'lo':[min(p[i] for p in corners) for i in range(3)],'hi':[max(p[i] for p in corners) for i in range(3)]}
def configure(scene):
 scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.54,.56,.58);s.show_shadows=True;s.show_cavity=True;s.cavity_type='BOTH';s.curvature_ridge_factor=1.2;s.curvature_valley_factor=1.15;s.background_type='WORLD';scene.world.color=(.12,.13,.14)
 scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
def render(scene,cam,camdata,poseid,view,target):
 off={'profile':Vector((-5.8,0,.08)),'neck-close':Vector((-3.6,-4.8,.75))}[view]
 cam.location=target+off;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale={'profile':1.50,'neck-close':.90}[view];scene.camera=cam;bpy.context.view_layer.update()
 p=OUT/f'{poseid}-{view}.png';assert not p.exists(),f'preserve existing {p}';scene.render.filepath=str(p);bpy.ops.render.render(write_still=True)
 return {'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p),'pose':poseid,'view':view,'location':[float(x) for x in cam.location],'target':[float(x) for x in target],'orthoScale':camdata.ortho_scale,'resolution':[1100,1100]}
def main():
 for k,p in [('native',NATIVE),('source14',SOURCE14),('source07',SOURCE07),('runtime',RUNTIME),('inspection',INSPECTION)]:bound(p,k)
 OUT.mkdir(parents=True,exist_ok=True)
 snapshot=OUT/'executed-review.py'
 if snapshot.exists():raise RuntimeError(f'refusing overwrite {snapshot}')
 shutil.copy2(__file__,snapshot)
 runtime=json.loads(RUNTIME.read_text());inspection=json.loads(INSPECTION.read_text())
 assert runtime['poseCount']==21 and len(runtime['poses'])==21
 assert len(inspection['poses'])==41
 rm=pose_map(runtime);im=pose_map(inspection)
 assert set(POSE_IDS)<=set(rm)|set(im)
 # Verify source14/source07/native rest parentage and transforms before movement.
 snap14=snap_open(SOURCE14);snap07=snap_open(SOURCE07);snap_native=snap_open(NATIVE)
 def compare_hier(a,b,label):
  assert set(a)==set(b),(label,'pivot set differs',set(a)^set(b))
  parent_diff=[];basis_diff=[];world_diff=[]
  for n in a:
   if a[n]['parent']!=b[n]['parent']:parent_diff.append(n)
   if mat_error(Matrix(a[n]['basis']),Matrix(b[n]['basis']))>1e-7:basis_diff.append(n)
   if mat_error(Matrix(a[n]['world']),Matrix(b[n]['world']))>1e-7:world_diff.append(n)
  return {'compared':len(a),'parentDifferences':parent_diff,'localRestMatrixDifferences':basis_diff,'worldRestMatrixDifferences':world_diff}
 h14=compare_hier(snap14,snap_native,'attempt14-to-v2');h07=compare_hier(snap07,snap_native,'attempt07-to-v2')
 assert not h14['parentDifferences'] and not h14['localRestMatrixDifferences'] and not h14['worldRestMatrixDifferences'],h14
 # V2 must preserve the current source14 transform contract. Record any
 # source07 divergence precisely instead of assigning it to the V2 edit.
 bpy.ops.wm.open_mainfile(filepath=str(NATIVE));scene=bpy.context.scene;configure(scene)
 _,pivots=hierarchy()
 meshobjs={o.name:o for o in bpy.data.objects if o.type=='MESH'}
 assert CHANGED<=set(meshobjs),sorted(CHANGED-set(meshobjs))
 changed={n:meshobjs[n] for n in CHANGED}
 inherited={o.name:o for o in meshobjs.values() if o.name not in CHANGED and o.parent and o.parent.name in REGION_OWNERS}
 # Mesh triangle BVHs for the focused local neighborhood only.
 camdata=bpy.data.cameras.new('V2 independent envelope camera');cam=bpy.data.objects.new(camdata.name,camdata);scene.collection.objects.link(cam)
 pose_records=[];renders=[];collision_records=[]
 selected=[(rm[x],x) if x in rm else (im[x],x) for x in POSE_IDS]
 for pose,pid in selected:
  err=set_pose(pose,pivots);dg=bpy.context.evaluated_depsgraph_get()
  pose_records.append({'id':pid,'category':pose.get('category',pose.get('source')),'matrixMaxError':err,'inspectionOpen':pose.get('open'),'controllerState':pose.get('controller',{}).get('state')})
  # One BVH per changed/inherited mesh at each state. Exact triangle-surface
  # overlap candidate counts are reported; solid containment and physical
  # interference are outside this diagnostic.
  bvh={}
  for n,o in {**inherited,**changed}.items():
   s=surface(o,dg)
   if s:bvh[n]=s
  pairs=[]
  names=sorted(bvh)
  for i,a in enumerate(names):
   for b in names[i+1:]:
    if a in changed and b in changed:pass
    elif (a in changed) != (b in changed):pass
    else:continue
    if not bbox_overlap(bvh[a],bvh[b]):continue
    hits=bvh[a]['tree'].overlap(bvh[b]['tree'])
    if hits:
     pairs.append({'a':a,'b':b,'overlappingTrianglePairs':len(hits),'scope':'changed-vs-changed lap candidates' if a in changed and b in changed else 'changed-vs-inherited regional candidates'})
  collision_records.append({'pose':pid,'candidatePairCount':len(pairs),'pairs':sorted(pairs,key=lambda x:(-x['overlappingTrianglePairs'],x['a'],x['b']))[:40],
   'testedChangedMeshes':len(changed),'testedInheritedRegionalMeshes':len(inherited),'algorithm':'BVHTree triangle overlap at exact pose; no broad phase padding; lap/contact candidates retained'})
  if pid in ('advanced-contact','inspection-open-1-separation-0'):
   # Use pivot midpoint as a camera target; pair profile and close view.
   target=(pivots['neck'].matrix_world.translation+pivots['breastplate'].matrix_world.translation)*.5
   for view in ('profile','neck-close'):renders.append(render(scene,cam,camdata,pid,view,target))
 bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(camdata)
 def record(p):return {'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)}
 result={'schema':'cervical-breast-transition-independent-envelope/v1','native':record(NATIVE),'source14':record(SOURCE14),'source07':record(SOURCE07),'runtimePacket':record(RUNTIME),'inspectionPacket':record(INSPECTION),
  'hierarchyComparison':{'attempt14ToV2':h14,'attempt07ToV2':h07},'selectedPoses':pose_records,'renderedViews':renders,'triangleOverlapCandidates':collision_records,
  'changedMeshes':sorted(CHANGED),'inheritedNeighborhoodOwners':sorted(REGION_OWNERS),
  'limits':['Four discrete states only; no continuous swept-volume result.','BVHTree triangle overlap candidates include intended lap/contact and are not classified as harmful without spatial/visual interpretation.','Surface triangle crossings do not detect one closed solid wholly contained in another; no physical clearance or load-path certification.','Neutral Workbench renders support visual review only, not browser/WebGL or art acceptance.','No native save, geometry edit, app edit, or export was performed.']}
 (OUT/'review.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'poses':pose_records,'renderCount':len(renders),'collisionPairCounts':{r['pose']:r['candidatePairCount'] for r in collision_records},'attempt14ToV2':h14,'attempt07ToV2':h07},indent=2))
if __name__=='__main__':main()
