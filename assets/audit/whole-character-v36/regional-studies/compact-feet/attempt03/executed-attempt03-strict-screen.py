"""Read-only three-state foot/digit/shin strict screen with independently sampled baseline poses."""
import bpy,json,hashlib,math,bmesh
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
R=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');A=R/'assets/audit/whole-character-v36/regional-studies/compact-feet/attempt03'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
PATHS={'35':R/'assets/models/whole-character-v36/attempt-form01/murderbird-whole-character-v36.blend','36':R/'assets/models/whole-character-v36/regional-studies/compact-feet/attempt03/murderbird-whole-character-v36-compact-feet-fit-form01-eval.blend'}
SHAS={'35':'9b0072375fee116864954e882f5ed8ec023cf8d400783fb96947ce4c57bf151f','36':'289d1839801b7823d3a304ae89e48d34a3556f10a7d450c8d1fe9705aae2b79c'}
for v,p in PATHS.items():assert sha(p)==SHAS[v]
NEW=json.loads((A/'form01-evaluation-receipt.json').read_text())['changedFootMeshes'];CHANGED={x['name'] for x in NEW}
PACKET=json.loads((R/'assets/audit/whole-character-v36/attempt-form01/foot-motion-screen/v36-pose-matrices.json').read_text());PACKETS={'35':PACKET,'36':PACKET}
C=Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)))
def belongs(o):
 while o:
  if o.name in ('left-foot','right-foot','left-shin','right-shin'):return True
  o=o.parent
 return False
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

def screen(v,pose,render=False):
 bpy.ops.wm.open_mainfile(filepath=str(PATHS[v]));bpy.context.view_layer.update()
 scene=bpy.context.scene;scene.frame_set(1)
 for o in bpy.data.objects:
  if o.animation_data:o.animation_data_clear()
 transforms={row['name']:C.inverted()@Matrix([row['worldMatrix'][i::4] for i in range(4)])@C for row in pose['transforms']}
 nodes=[o for o in bpy.data.objects if o.type=='EMPTY' and not o.get('authoringGuide')]
 def depth(o):
  i=0
  while o.parent:i+=1;o=o.parent
  return i
 restParity=max(abs(o.matrix_world[i][j]-transforms[o.name][i][j]) for o in nodes for i in range(4) for j in range(4)) if pose['id']=='exported-rest' else None
 for o in sorted(nodes,key=depth):
  assert o.name in transforms,o.name
  o.matrix_world=transforms[o.name];bpy.context.view_layer.update()
 error=max(abs(o.matrix_world[i][j]-transforms[o.name][i][j]) for o in nodes for i in range(4) for j in range(4));assert error<1e-6,error
 if restParity is not None:assert restParity<1e-6,restParity
 dg=bpy.context.evaluated_depsgraph_get();items=[];geometry=[]
 for o in sorted(bpy.data.objects,key=lambda o:o.name):
  if o.type!='MESH' or not belongs(o) or o.get('authoringGuide'):continue
  if 'builder' not in o.get('exteriorEras','maker,mechanic,builder').split(','):continue
  ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();verts=[ev.matrix_world@x.co for x in m.vertices];tri=[tuple(f.vertices) for f in m.loop_triangles]
  assert all(math.isfinite(x) for p in verts for x in p),o.name
  if o.name in CHANGED:
   bm=bmesh.new();bm.from_mesh(m);boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free()
   geometry.append({'name':o.name,'owner':o.parent.name,'vertices':len(verts),'triangles':len(tri),'finite':True,'boundaryEdges':boundary,'nonmanifoldEdges':nonmanifold,'degenerateTrianglesLe1e14':sum((verts[t[1]]-verts[t[0]]).cross(verts[t[2]]-verts[t[0]]).length*.5<=1e-14 for t in tri)})
  ev.to_mesh_clear()
  bounds=[[min(pt[k] for pt in verts) for k in range(3)],[max(pt[k] for pt in verts) for k in range(3)]]
  items.append((o.name,o.parent.name,o.name in CHANGED,verts,tri,bounds,BVHTree.FromPolygons(verts,tri,all_triangles=True)))
 assert len(geometry)==len(CHANGED),(len(geometry),len(CHANGED))
 pairs=[];tested=0
 for i,x in enumerate(items):
  for y in items[i+1:]:
   if not(x[2] or y[2]):continue
   tested+=1
   if any(x[5][1][k]<y[5][0][k] or y[5][1][k]<x[5][0][k] for k in range(3)):continue
   for ix,iy in x[6].overlap(y[6]):
    tx=[x[3][j] for j in x[4][ix]];ty=[y[3][j] for j in y[4][iy]]
    if any(edge(tx[k],tx[(k+1)%3],ty) or edge(ty[k],ty[(k+1)%3],tx) for k in range(3)):
     pairs.append({'a':x[0],'b':y[0],'owners':[x[1],y[1]],'sameOwner':x[1]==y[1],'firstTrianglePair':[ix,iy],'witnessTriangles':[[list(p) for p in tx],[list(p) for p in ty]],'overlapBounds':[[max(x[5][0][k],y[5][0][k]) for k in range(3)],[min(x[5][1][k],y[5][1][k]) for k in range(3)]]});break
 row={'pose':pose['id'],'nativeSHA256':SHAS[v],'poseGLBSHA256':PACKETS[v]['sourceGLBSHA256'],'nodes':len(nodes),'matrixInstallationMaxErrorM':error,'exportedRestParityMaxError':restParity,'adjacentScopeMeshes':len(items),'changedMeshesScreened':len(geometry),'eligiblePairCombinations':tested,'geometry':geometry,'pairs':pairs,'pairCount':len(pairs)}
 if render:
  for o in bpy.data.objects:
   if o.get('authoringGuide') or o.type=='CURVE':o.hide_render=True
   elif o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
  scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14)
  scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
  data=bpy.data.cameras.new('Temporary exact foot motion screen camera');data.type='ORTHO';cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);scene.camera=cam
  roots=[bpy.data.objects[n].matrix_world.translation for n in ('left-foot','right-foot')];target=(roots[0]+roots[1])*.5+Vector((0,-.14,-.08));cam.location=target+Vector((-1.35,-2.6,.7));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=1.15
  scene.render.filepath=str(A/f'v36-{pose["id"]}-feet.png');bpy.ops.render.render(write_still=True)
  row['view']={'path':str(Path(scene.render.filepath).relative_to(R)),'sha256':sha(scene.render.filepath),'cameraPosition':list(cam.location),'target':list(target),'orthoScale':data.ortho_scale,'engine':'BLENDER_WORKBENCH'}
 return row
key=lambda p:tuple(sorted((p['a'],p['b'])))
result={'status':'Regional attempt03 exact Form01 base-to-fit discrete strict-crossing comparison; not complete motion or physics acceptance','sourceSHA256':sha(__file__),'changedMeshCount':len(CHANGED),'nativeHashes':SHAS,'posePacket':{'path':str((R/'assets/audit/whole-character-v36/attempt-form01/foot-motion-screen/v36-pose-matrices.json').relative_to(R)),'sha256':sha(R/'assets/audit/whole-character-v36/attempt-form01/foot-motion-screen/v36-pose-matrices.json'),'sourceGLBSHA256':PACKET['sourceGLBSHA256']},'method':'Fresh V36 Form01 actual-GLB rest/scrape/landing matrix packet, applied to the exact Form01 native and a vertex-only fit derivative with unchanged node matrices. Existing strict edge-through-face kernel, 1e-7m plane and 1e-6 barycentric/edge margins. One actual witness per identity, no pair exemptions. Includes same-owner distinct meshes separately. Each model uses its own fresh actual-GLB matrices.','limits':['Three discrete states only; no swept/continuous collision, physics, containment, tangent/coplanar or within-mesh selfintersection claim.','Adjacent scope is meshes descended from feet/digits and shin owners; torso/thigh and procedural era hardware excluded.','Pair counts are identities, not penetration depth or independent defect counts.'],'poses':[]}
for idx,pose in enumerate(PACKETS['36']['poses']):
 basepose=PACKETS['35']['poses'][idx];assert basepose['id']==pose['id']
 before=screen('35',basepose);after=screen('36',pose,True);b={key(p):p for p in before['pairs']};c={key(p):p for p in after['pairs']}
 row={'pose':pose['id'],'baseline':before,'candidate':after,'introduced':[c[k] for k in sorted(c.keys()-b.keys())],'inherited':[c[k] for k in sorted(c.keys()&b.keys())],'resolved':[b[k] for k in sorted(b.keys()-c.keys())]};result['poses'].append(row)
 (A/'attempt03-strict-foot-motion-screen.json').write_text(json.dumps(result,indent=2)+'\n');print('RESULT',pose['id'],'base',len(b),'fit',len(c),'introduced',len(row['introduced']),'same-owner',sum(p['sameOwner'] for p in after['pairs']),flush=True)
for v,p in PATHS.items():assert sha(p)==SHAS[v]
