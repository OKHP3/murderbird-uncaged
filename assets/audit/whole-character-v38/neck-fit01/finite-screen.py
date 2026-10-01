import bpy,json,hashlib,runpy,bmesh
from pathlib import Path
from mathutils import Matrix,Vector
from mathutils.bvhtree import BVHTree
P=Path(__file__).resolve().parent;R=P.parents[3];S=R/'assets/models/whole-character-v38/neck-profile01/attempt02/murderbird-v38-neck-profile01-attempt02.blend';C=R/'assets/models/whole-character-v38/neck-fit01/murderbird-v38-neck-fit01.blend';scope=json.loads((P/'scope.json').read_text());STOCK=scope['changed'];SHELL=[f'V38 neck-profile rigid silhouette stage {i}'for i in range(1,6)]
# Reuse strict finite predicate ONLY; do not execute historical broad diagnostic.
text=(R/'assets/audit/whole-character-v38/neck-envelope01/finite-screen.py').read_text();ns={};exec(text[text.index('def inside'):text.index('def load')],{'intersect_ray_tri':__import__('mathutils.geometry',fromlist=['intersect_ray_tri']).intersect_ray_tri},ns);edge=ns['edge'];edge.__globals__['inside']=ns['inside']
def shape(o):
 m=o.data;m.calc_loop_triangles();v=[o.matrix_world@x.co for x in m.vertices];f=[tuple(t.vertices)for t in m.loop_triangles];return {'v':v,'f':f,'b':BVHTree.FromPolygons(v,f,all_triangles=True,epsilon=0),'owner':o.parent.name}
def compare(path,pose):
 bpy.ops.wm.open_mainfile(filepath=str(path))
 if pose!='neutral':
  for n in ['neck','cervical-mid-a','cervical-mid-b','cervical-upper']:o=bpy.data.objects[n];o.matrix_basis=o.matrix_basis@Matrix.Rotation(.1625 if pose=='authoredMaxPitch'else-.035,4,'X')
  if pose=='authoredMaxPitch':o=bpy.data.objects['head'];o.matrix_basis=o.matrix_basis@Matrix.Rotation(-.5090505059024657,4,'X')
 bpy.context.view_layer.update();items={n:shape(bpy.data.objects[n])for n in STOCK+SHELL};pairs=[]
 for n in STOCK:
  a=items[n]
  for name in SHELL:
   b=items[name];strict=[]
   for ia,ib in a['b'].overlap(b['b']):
    x=[a['v'][i]for i in a['f'][ia]];y=[b['v'][i]for i in b['f'][ib]]
    if any(edge(x[k],x[(k+1)%3],y)or edge(y[k],y[(k+1)%3],x)for k in range(3)):strict.append((ia,ib))
   if strict:pairs.append({'stock':n,'shell':name,'owners':[a['owner'],b['owner']],'strictTrianglePairs':len(strict),'stockTriangles':len({x[0]for x in strict}),'shellTriangles':len({x[1]for x in strict})})
 return pairs
out={'method':'Strict finite world-triangle edge-through-face crossing of9changedstock×5shells only; coplanar/grazing/containment and allotherparts omitted. No exemption for sameowner.','poses':{},'poseQualification':'Neutral plus authored endpoint body-rest pitch slices: four localX+.1625/head-.5090505059 and four-.035/head0. These are diagnostic samples, NOT complete captured runtime actions.','limits':['No yaw/sweep/service/strength/otherstock fit certification.','Intended same-owner stock unions screened separately; positive commonvolume not strength proof.']}
for pose in ['neutral','authoredMaxPitch','authoredMakerPitch']:
 a=compare(S,pose);b=compare(C,pose);da={(x['stock'],x['shell']):x for x in a};db={(x['stock'],x['shell']):x for x in b};out['poses'][pose]={'source':a,'candidate':b,'new':[db[k]for k in db.keys()-da.keys()],'removed':[da[k]for k in da.keys()-db.keys()],'inheritedCountChanges':[{'stock':k[0],'shell':k[1],'source':da[k]['strictTrianglePairs'],'candidate':db[k]['strictTrianglePairs']}for k in da.keys()&db.keys()if da[k]['strictTrianglePairs']!=db[k]['strictTrianglePairs']]};(P/'finite-screen.json').write_text(json.dumps(out,indent=2)+'\n');print('POSE',pose,len(a),len(b),flush=True)
# Actual finite same-owner endpoint stock intersection using Exact Boolean. No source geometry write.
def common(a,b):
 obj=a.copy();obj.data=a.data.copy();bpy.context.scene.collection.objects.link(obj);mod=obj.modifiers.new('diagnostic finite commonstock','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=b;dg=bpy.context.evaluated_depsgraph_get();ev=obj.evaluated_get(dg);m=ev.to_mesh();bm=bmesh.new();bm.from_mesh(m);value={'volumeM3':abs(bm.calc_volume(signed=True)),'faces':len(bm.faces),'nonmanifoldEdges':sum(not e.is_manifold for e in bm.edges)};bm.free();ev.to_mesh_clear();bpy.data.objects.remove(obj,do_unlink=True);return value
out['receivingStock']={}
for label,path in [('source',S),('candidate',C)]:
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();rows=[]
 for side in [-1,1]:
  for a,b in [(f'V23 cervical 3 load link {side}',f'V23 cervical 3 distal race {side}'),(f'V23 cervical 3 load link {side}','V23 cervical 2 captive pin'),(f'V31 passive cranial load bow {side}',f'V31 cranial load bow shaft seat {side}')]:rows.append({'stock':a,'receiver':b,'owners':[bpy.data.objects[a].parent.name,bpy.data.objects[b].parent.name],'actualFiniteCommonStock':common(bpy.data.objects[a],bpy.data.objects[b])})
 out['receivingStock'][label]=rows
# Explicit protected5shell geometry/owner/matrix proof.
out['protectedShells']={}
for label,path in [('source',S),('candidate',C)]:
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();out['protectedShells'][label]={n:{'geometrySHA256':hashlib.sha256(json.dumps({'v':[list(v.co)for v in bpy.data.objects[n].data.vertices],'f':[list(f.vertices)for f in bpy.data.objects[n].data.polygons]},sort_keys=True).encode()).hexdigest(),'owner':bpy.data.objects[n].parent.name,'matrixWorld':[list(row)for row in bpy.data.objects[n].matrix_world]}for n in SHELL}
assert out['protectedShells']['source']==out['protectedShells']['candidate'];out['pinExtensionQualification']='Axial extension beyond race changes source5.5mm to proposed8.5mm equally bothsides; symmetry preserved, exact sourceextension not preserved.';(P/'finite-screen.json').write_text(json.dumps(out,indent=2)+'\n');print('FINITE_READY',flush=True)
