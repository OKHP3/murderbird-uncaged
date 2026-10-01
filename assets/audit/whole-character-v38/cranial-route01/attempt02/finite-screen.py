import bpy,json,hashlib,math,struct,bmesh,shutil
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;R=P.parents[4];S=R/'assets/models/whole-character-v38/neck-fit01/attempt02/murderbird-v38-neck-fit01-attempt02.blend';C=R/'assets/models/whole-character-v38/cranial-route01/attempt02/murderbird-v38-cranial-route01-attempt02.blend';SG=S.with_name(S.stem+'-rigid.glb');raw=SG.read_bytes();sz=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+sz]);gltf={n['name']:n for n in doc['nodes']};packetSource=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/audit/whole-character-v38/cranial-route-integration01/source-runtime-poses.json');packet=json.loads(packetSource.read_text());assert packet['modelSHA256']==hashlib.sha256(SG.read_bytes()).hexdigest();shutil.copy2(packetSource,P/'source-runtime-poses.json')
BOW=[f'V31 passive cranial load bow {s}'for s in [-1,1]];SOCKET=[f'V23 cervical 4 distal race {s}'for s in [-1,1]];SHELL=[f'V38 neck-profile rigid silhouette stage {i}'for i in range(1,6)];STEM='V23 cervical 4 captive pin';PARTS=BOW+SOCKET+SHELL+[STEM];basis=Matrix.Rotation(-math.pi/2,4,'X')
text=(R/'assets/audit/whole-character-v38/neck-envelope01/finite-screen.py').read_text();ns={};exec(text[text.index('def inside'):text.index('def load')],{'intersect_ray_tri':__import__('mathutils.geometry',fromlist=['intersect_ray_tri']).intersect_ray_tri},ns);edge=ns['edge'];edge.__globals__['inside']=ns['inside']
def trs(n):
 p=n.get('position',n.get('translation',[0,0,0]));q=n.get('quaternion',n.get('rotation',[0,0,0,1]));return Matrix.LocRotScale(Vector(p),Quaternion((q[3],q[0],q[1],q[2])),Vector(n.get('scale',[1,1,1])))
def shape(o):
 m=o.data;m.calc_loop_triangles();v=[o.matrix_world@x.co for x in m.vertices];f=[tuple(t.vertices)for t in m.loop_triangles];return {'v':v,'f':f,'b':BVHTree.FromPolygons(v,f,all_triangles=True,epsilon=0),'owner':o.parent.name}
def crossing(a,b,selftest=False):
 strict=[]
 for ia,ib in a['b'].overlap(b['b']):
  if selftest and(ia>=ib or set(a['f'][ia])&set(b['f'][ib])):continue
  x=[a['v'][i]for i in a['f'][ia]];y=[b['v'][i]for i in b['f'][ib]]
  if any(edge(x[k],x[(k+1)%3],y)or edge(y[k],y[(k+1)%3],x)for k in range(3)):strict.append((ia,ib))
 return {'strictTrianglePairs':len(strict),'aTriangles':len({x[0]for x in strict}),'bTriangles':len({x[1]for x in strict})}
def screen(path,sample):
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();basisErrors={}
 if sample:
  for name,n in sample['nodes'].items():
   o=bpy.data.objects[name];original=basis.inverted()@trs(gltf[name])@basis;error=max(abs(o.matrix_local[i][j]-original[i][j])for i in range(4)for j in range(4));basisErrors[name]=error;assert error<2e-6,(name,error,'glTF/native rest basis mismatch')
  # Node order from controller is hierarchy order; matrix_parent_inverse remains source exact.
  for name,n in sample['nodes'].items():o=bpy.data.objects[name];o.matrix_basis=o.matrix_parent_inverse.inverted()@basis.inverted()@trs(n)@basis;bpy.context.view_layer.update()
  for name,n in sample['nodes'].items():
   expected=basis.inverted()@trs(n)@basis;actual=bpy.data.objects[name].matrix_local;assert max(abs(actual[i][j]-expected[i][j])for i in range(4)for j in range(4))<3e-6
 items={n:shape(bpy.data.objects[n])for n in PARTS};pairs=[]
 for name in BOW+SOCKET+[STEM]:
  targets=SHELL if name in SOCKET else SOCKET+(SHELL if name in BOW else[])
  for other in targets:
   rec=crossing(items[name],items[other])
   if rec['strictTrianglePairs']:pairs.append({'stock':name,'other':other,'owners':[items[name]['owner'],items[other]['owner']],**rec})
 rec=crossing(items[BOW[0]],items[BOW[1]])
 if rec['strictTrianglePairs']:pairs.append({'stock':BOW[0],'other':BOW[1],'owners':['head','head'],**rec})
 return {'pairs':pairs,'basisRestMaximumErrorM':max(basisErrors.values(),default=0),'sampleLocalTransformCheck':True}
result={'method':'Actual finite triangles:2bows against5shells+2sockets, bowpair and inherited headstem against2sockets. Strict edge-through-face, same-owner counted; containment/coplanar/grazing/sweep/strength omitted.','poseQualification':packet['scope'],'gltfToNativeBasis':'C=Rx(-pi/2); native local M=C^-1*glTF M*C. Source glTF local TRS verified against exact native matrix_local before applying every actual sample, actual local matrix verified after. Source matrix_parent_inverse retained.','poses':{},'runtimePacketSHA256':hashlib.sha256(packetSource.read_bytes()).hexdigest()}
for sample in [None]+packet['samples']:
 label='neutral'if sample is None else sample['label'];a=screen(S,sample);b=screen(C,sample);da={(x['stock'],x['other']):x for x in a['pairs']};db={(x['stock'],x['other']):x for x in b['pairs']};result['poses'][label]={'source':a,'candidate':b,'new':[db[k]for k in db.keys()-da.keys()],'removed':[da[k]for k in da.keys()-db.keys()],'inheritedCountChanges':[{'stock':k[0],'other':k[1],'source':da[k]['strictTrianglePairs'],'candidate':db[k]['strictTrianglePairs']}for k in da.keys()&db.keys()if da[k]['strictTrianglePairs']!=db[k]['strictTrianglePairs']]};(P/'finite-screen.json').write_text(json.dumps(result,indent=2)+'\n');print('POSE',label,len(a['pairs']),len(b['pairs']),flush=True)
# Connection and stock proofs at actual neutral, no binary write.
def common(a,b):
 obj=a.copy();obj.data=a.data.copy();bpy.context.scene.collection.objects.link(obj);mod=obj.modifiers.new('diagnostic finite commonstock','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=b;dg=bpy.context.evaluated_depsgraph_get();ev=obj.evaluated_get(dg);m=ev.to_mesh();bm=bmesh.new();bm.from_mesh(m);value={'volumeM3':abs(bm.calc_volume(signed=True)),'faces':len(bm.faces),'nonmanifoldEdges':sum(not e.is_manifold for e in bm.edges)}
 for item in [a,b]:
  check=bmesh.new();check.from_mesh(item.data);value.setdefault('participatingSolidVolumesM3',[]).append(abs(check.calc_volume(signed=True)));check.free()
 value['commonStockBoundedByBothVolumes']=value['volumeM3']<=min(value['participatingSolidVolumesM3'])*1.0001+1e-12
 value['qualifiedPositiveFiniteContact']=value['volumeM3']>1e-12 and value['faces']>0 and value['nonmanifoldEdges']==0 and value['commonStockBoundedByBothVolumes'];bm.free();ev.to_mesh_clear();bpy.data.objects.remove(obj,do_unlink=True);return value
result['stockProof']={}
for label,path in [('source',S),('candidate',C)]:
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();rows=[]
 for side in [-1,1]:
  o=bpy.data.objects[f'V31 passive cranial load bow {side}'];bm=bmesh.new();bm.from_mesh(o.data);unseen=set(bm.verts);components=0
  while unseen:
   components+=1;todo=[unseen.pop()]
   while todo:
    v=todo.pop()
    for e in v.link_edges:
     n=e.other_vert(v)
     if n in unseen:unseen.remove(n);todo.append(n)
  row={'name':o.name,'components':components,'nonmanifoldEdges':sum(not e.is_manifold for e in bm.edges),'signedVolumeM3':bm.calc_volume(signed=True),'nonAdjacentSelfStrictTrianglePairs':crossing(shape(o),shape(o),True)['strictTrianglePairs'],'commonStock':[]};bm.free()
  for target in [f'V31 cranial load bow shaft seat {side}','V21 head captive shaft',STEM]:row['commonStock'].append({'receiver':target,'owner':'head',**common(o,bpy.data.objects[target])})
  rows.append(row)
 for side in [-1,1]:
  o=bpy.data.objects[f'V23 cervical 4 distal race {side}'];bm=bmesh.new();bm.from_mesh(o.data);rows.append({'name':o.name,'nonmanifoldEdges':sum(not e.is_manifold for e in bm.edges),'signedVolumeM3':bm.calc_volume(signed=True),'nonAdjacentSelfStrictTrianglePairs':crossing(shape(o),shape(o),True)['strictTrianglePairs'],'actualLoadLinkCommonStock':common(o,bpy.data.objects[f'V23 cervical 4 load link {side}'])});bm.free()
 result['stockProof'][label]=rows
# Exact cap/upper row local-byte correspondence, plus protected5shell hashes.
bpy.ops.wm.open_mainfile(filepath=str(S));old={n:[tuple(v.co)for v in bpy.data.objects[n].data.vertices]for n in BOW+SOCKET};bpy.ops.wm.open_mainfile(filepath=str(C));result['protectedRows']={}
for n in BOW:
 ids=[layer*561+row*11+j for layer in[0,1]for row in[0]+list(range(35,51))for j in range(11)];actual=[tuple(v.co)for v in bpy.data.objects[n].data.vertices];assert all(old[n][i]==actual[i]for i in ids);result['protectedRows'][n]={'rootRow0AndRows35to50LocalVertexExact':True,'retainedVertexCount':len(ids)}
for n in SOCKET:
 ids=[layer*425+row*25+j for layer in[0,1]for row in range(4,17)for j in range(25)];actual=[tuple(v.co)for v in bpy.data.objects[n].data.vertices];assert all(old[n][i]==actual[i]for i in ids);result['protectedRows'][n]={'rows4to16LocalVertexExact':True,'retainedVertexCount':len(ids)}
(P/'finite-screen.json').write_text(json.dumps(result,indent=2)+'\n');print('FINITE_READY',flush=True)
