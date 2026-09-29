"""Single neutral rest-only cross-owner screen, unchanged strict triangle method."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
R=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');A=R/'assets/audit/whole-character-v34/regional-studies/leg-mass/coarse05-repair04'
BASE=R/'assets/models/whole-character-v33/attempt-form06/murderbird-whole-character-v33.blend';NEW=R/'assets/models/whole-character-v34/regional-studies/leg-mass/coarse05-repair04/murderbird-v34-leg-mass.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(BASE)=='5fdfe66693db848fcf624b28484c3eaba220a8d7f389248390a4f21a571d108d';assert sha(NEW)=='a5fff80ae87dd5383fc1ec75da3babbaace7269a0e2648e9d55c93cf78146d80'
# Exact functions copied from frozen neck strict checker, no pose manipulation.
def inside(p,tri):
 x,y,z=tri;v0=y-x;v1=z-x;v2=p-x;d00=v0.dot(v0);d01=v0.dot(v1);d11=v1.dot(v1);den=d00*d11-d01*d01
 if abs(den)<1e-18:return False
 u=(d11*v2.dot(v0)-d01*v2.dot(v1))/den;v=(d00*v2.dot(v1)-d01*v2.dot(v0))/den
 return min(u,v,1-u-v)>1e-6
def edge(p,q,tri):
 n=(tri[1]-tri[0]).cross(tri[2]-tri[0])
 if n.length<1e-12:return False
 n.normalize();d0=n.dot(p-tri[0]);d1=n.dot(q-tri[0])
 if not(d0*d1<0 and abs(d0)>1e-7 and abs(d1)>1e-7):return False
 direction=q-p;hit=intersect_ray_tri(*tri,direction,p,True)
 if hit is None:return False
 t=(hit-p).dot(direction)/max(direction.length_squared,1e-30)
 return 1e-6<t<1-1e-6 and inside(hit,tri)
C=Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)))
POSE_PATH=A.parent/'controller-poses/pose-matrices.json'
POSE_DATA=json.loads(POSE_PATH.read_text())
REVISED=json.loads((A/'receipt.json').read_text())['result'];FOOT_CHANGED=set(REVISED['changedFootOwnedMeshes']);BODY_CHANGED=set(REVISED['additionalChangedBodyMeshes'])
def screen(path,pose):
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update()
 if pose['id']!='exported-rest':
  transforms={row['name']:C.inverted()@Matrix([row['worldMatrix'][i::4] for i in range(4)])@C for row in pose['transforms']}
  nodes=[o for o in bpy.data.objects if o.type=='EMPTY' and not o.get('authoringGuide')]
  def depth(o):
   i=0
   while o.parent:i+=1;o=o.parent
   return i
  for o in sorted(nodes,key=depth):
   assert o.name in transforms,o.name
   o.matrix_world=transforms[o.name];bpy.context.view_layer.update()
  error=max(abs(o.matrix_world[i][j]-transforms[o.name][i][j]) for o in nodes for i in range(4) for j in range(4));assert error<1e-6,error
 else:error=0
 dg=bpy.context.evaluated_depsgraph_get();items=[]
 for o in bpy.data.objects:
  if o.type!='MESH' or not o.parent or o.get('authoringGuide') is True:continue
  if 'builder' not in o.get('exteriorEras','maker,mechanic,builder').split(','):continue
  ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@x.co for x in m.vertices];tri=[tuple(f.vertices) for f in m.loop_triangles];ev.to_mesh_clear()
  if not v:continue
  scope=o.parent.name in ('left-thigh','left-shin','right-thigh','right-shin') or o.name in FOOT_CHANGED or o.name in BODY_CHANGED
  bounds=[[min(pt[k] for pt in v) for k in range(3)],[max(pt[k] for pt in v) for k in range(3)]]
  items.append((o.name,o.parent.name,scope,v,tri,bounds,BVHTree.FromPolygons(v,tri,all_triangles=True)))
 pairs=[]
 for i,x in enumerate(items):
  for y in items[i+1:]:
   if x[1]==y[1] or not(x[2] or y[2]) or any(x[5][1][k]<y[5][0][k] or y[5][1][k]<x[5][0][k] for k in range(3)):continue
   for ix,iy in x[6].overlap(y[6]):
    tx=[x[3][j] for j in x[4][ix]];ty=[y[3][j] for j in y[4][iy]]
    if any(edge(tx[k],tx[(k+1)%3],ty) or edge(ty[k],ty[(k+1)%3],tx) for k in range(3)):
     pairs.append({'a':x[0],'b':y[0],'owners':[x[1],y[1]],'firstTrianglePair':[ix,iy],'witnessTriangles':[[list(v) for v in tx],[list(v) for v in ty]]});break
 return {'pose':pose['id'],'actualMatrixInstallationMaxError':error,'nativeSHA256':sha(path),'allVisibleMeshes':len(items),'screenedLegMeshes':sum(x[2] for x in items),'pairCount':len(pairs),'pairs':pairs}

result={'scope':'Focused actual runtime hip/knee/ankle neighboring-owner screen. All140 thigh/shin meshes plus34 revised foot-owned ankle/truss/instep meshes and4 revised passive body receivers vs every builder-visible exported neighbor; no procedural hardware. Ten discrete poses, no continuous collision or physics proof.','method':'Same strict edge-through-face,1e-7m plane and1e-6barycentric/edge margin; no pair exemptions; native authored rest +9 actual runtime samples.','sourceSHA256':sha(Path(__file__)),'actualPoseFileSHA256':sha(POSE_PATH),'sourceGLBSHA256':POSE_DATA['sourceGLBSHA256'],'nativeSHA256':sha(NEW),'baselineSHA256':sha(BASE),'poses':[]}
key=lambda p:tuple(sorted((p['a'],p['b'])))
for pose in POSE_DATA['poses']:
 before=screen(BASE,pose);after=screen(NEW,pose);b={key(p):p for p in before['pairs']};c={key(p):p for p in after['pairs']}
 row={'pose':pose['id'],'baseline':before,'candidate':after,'introduced':[c[k] for k in sorted(c.keys()-b.keys())],'retained':[c[k] for k in sorted(c.keys()&b.keys())],'resolved':[b[k] for k in sorted(b.keys()-c.keys())]}
 result['poses'].append(row);(A/'focused-joint-screen.json').write_text(json.dumps(result,indent=2)+'\n')
 print(pose['id'],len(b),len(c),'introduced',len(row['introduced']),flush=True)
# Render actual joint arrangements at Maker peak and jump landing; complete
# geometry remains visible and the same camera parameters are recorded.
views=json.loads((A/'camera-contract.json').read_text())['views']
for poseid in ('maker-leg-peak','advanced-jump-landing'):
 pose=next(p for p in POSE_DATA['poses'] if p['id']==poseid);screen(NEW,pose)
 scene=bpy.context.scene
 for o in bpy.data.objects:
  if o.get('authoringGuide') is True:o.hide_render=True
  elif o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
  elif o.type=='CURVE':o.hide_render=True
 scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14)
 scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 data=bpy.data.cameras.new('V34 actual motion review camera');data.type='ORTHO';cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);scene.camera=cam
 root=bpy.data.objects['murderbird'].matrix_world.translation.copy()
 for name,pos,target,scale in [v for v in views if v[0] in ('reference-angle','leg-close')]:
  cam.location=Vector(pos)+root;cam.rotation_euler=(Vector(target)+root-cam.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=scale
  scene.render.filepath=str(A/f'{poseid}-{name}.png');bpy.ops.render.render(write_still=True)
assert sha(BASE)==result['baselineSHA256'] and sha(NEW)==result['nativeSHA256']
