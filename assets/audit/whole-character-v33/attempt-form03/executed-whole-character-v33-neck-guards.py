"""V33 directional rigid guard receiving underlaps, actual-model reconstruction.

The existing curved rest surfaces remain the governing silhouette. Upper
parent-course material forms inward behind the actual child's sampled finite
shell, rather than introducing full spherical rings. Each finite guard slides
past its independently rigid neighbour; no stretch, owner or motion-law change.
"""
import bpy,bmesh,math,json
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree

CHAIN=['neck','cervical-mid-a','cervical-mid-b','cervical-upper']
PITCHES=sorted(set([-.035,.1625,.020,-.0175,0]+[-.035+.1975*i/24 for i in range(25)]))
GAP=.008;WALL=.0035
CHEEKS=[f'V24 rising thoracic receiving cheek {s}' for s in (-1,1)]

def signature(o):
 return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),json.dumps(dict(o.items()),sort_keys=True,default=lambda x:list(x)),tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(f.vertices) for f in o.data.polygons),tuple(m.name if m else None for m in o.data.materials),tuple((q.name,q.type) for q in o.modifiers),o.hide_render,o.hide_viewport)

def points(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();m.calc_loop_triangles();v=[e.matrix_world@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.loop_triangles];e.to_mesh_clear();return v,f

def sweep_bvh(names,joint):
 verts=[];faces=[];pivot=bpy.data.objects[joint].matrix_world.copy()
 for name in names:
  v,f=points(bpy.data.objects[name])
  for angle in PITCHES:
   transform=pivot@Matrix.Rotation(angle,4,'X')@pivot.inverted();start=len(verts);verts.extend(transform@p for p in v);faces.extend(tuple(start+i for i in tri) for tri in f)
 return BVHTree.FromPolygons(verts,faces,all_triangles=True)

def closed_sheet(o,world):
 # Preserve authored directional grid connectivity, with an inward finite
 # wall. No lip/core object remains hidden beneath a replacement skin.
 faces=[tuple(p.vertices) for p in o.data.polygons];m=bpy.data.meshes.new(o.name+' V33 rigid receiving wall');m.from_pydata(world,[],faces);m.update();bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.normal_update();bm.verts.ensure_lookup_table()
 center=sum(world,Vector())/len(world);cy=center.y
 radial=Vector((center.x,center.y-bpy.data.objects[o.parent.name].matrix_world.translation.y,0))
 if bm.faces[len(bm.faces)//2].normal.dot(radial)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.normal_update()
 normals=[v.normal.copy() for v in bm.verts];bm.free();n=len(world);v=world+[p-WALL*normal for p,normal in zip(world,normals)];f=faces+[tuple(n+i for i in reversed(face)) for face in faces];edges={}
 for face in faces:
  for a,b in zip(face,face[1:]+face[:1]):key=tuple(sorted((a,b)));edges.setdefault(key,[]).append((a,b))
 for rows in edges.values():
  if len(rows)==1:a,b=rows[0];f.append((b,a,n+a,n+b))
 m.clear_geometry();inv=o.matrix_world.inverted();m.from_pydata([inv@p for p in v],[],f);m.update()
 for mat in o.data.materials:m.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),o.name
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 volume=bm.calc_volume(signed=True);assert volume>0,o.name;bm.to_mesh(m);bm.free();o.data=m;o.modifiers.clear()
 for p in m.polygons:p.use_smooth=len(p.vertices)==4
 return volume

def convex(points,name):
 bm=bmesh.new()
 for p in points:bm.verts.new(p)
 result=bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False);unused=set(result['geom_interior'])|set(result['geom_unused'])
 if unused:bmesh.ops.delete(bm,geom=list(unused),context='VERTS')
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));m=bpy.data.meshes.new(name);bm.to_mesh(m);bm.free();return m

def apply():
 bpy.context.view_layer.update();guards=[f'V23 cervical {i+1} directional guard {k+1}' for i in range(3) for k in range(10)];changed=guards+CHEEKS
 protected={o.name:signature(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in changed};nodes={o.name:(o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),json.dumps(dict(o.items()),sort_keys=True,default=lambda x:list(x))) for o in bpy.data.objects if o.type=='EMPTY'};records=[]
 for i in reversed(range(3)):
  hinge=bpy.data.objects[CHAIN[i+1]].matrix_world.translation.copy();bvh=sweep_bvh([f'V23 cervical {i+2} directional guard {k+1}' for k in range(10)],CHAIN[i+1])
  for k in range(10):
   o=bpy.data.objects[f'V23 cervical {i+1} directional guard {k+1}'];assert o.parent.name==CHAIN[i] and len(o.data.vertices)==399,o.name
   original=[o.matrix_world@v.co for v in o.data.vertices];delta=[];axes=[]
   for p in original:
    origin=Vector((p.x,hinge.y,hinge.z));direction=p-origin;r=direction.length;direction.normalize();hit=bvh.ray_cast(origin,direction,r+GAP*2)
    d=max(0,r-hit[3]+GAP) if hit[0] is not None and hit[3]<r+GAP else 0
    delta.append(d);axes.append(direction)
   # Conservatively spread abrupt local returns by two grid-neighbour rings;
   # clearance displacement only increases, never relaxed to ease a check.
   for iteration in range(2):
    old=delta.copy()
    for row in range(21):
     for col in range(19):
      p=row*19+col;neighbours=[old[rr*19+cc] for rr,cc in [(row-1,col),(row+1,col),(row,col-1),(row,col+1)] if 0<=rr<21 and 0<=cc<19];delta[p]=max(old[p],.5*(max(neighbours)+old[p]))
   world=[p-d*axis for p,d,axis in zip(original,delta,axes)];volume=closed_sheet(o,world);records.append({'name':o.name,'owner':o.parent.name,'receivingJoint':CHAIN[i+1],'finiteClosed':True,'positiveVolumeM3':volume,'changedSurfaceVertices':sum(d>1e-7 for d in delta),'maximumInwardReceivingDisplacementM':max(delta),'sameOwner':True})
  bpy.context.view_layer.update()
 # The body-fixed root cheeks receive the full actual first-course envelope,
 # including intermediate yaw samples. Adjacent body/door panels are exact.
 pivot=bpy.data.objects['neck'].matrix_world.copy();raw=[]
 rootpoints=[p for k in range(10) for p in points(bpy.data.objects[f'V23 cervical 1 directional guard {k+1}'])[0]]
 yaws=sorted(set([-.45,-.30,-.15,0,.15,.30,.45,.288]));rootPitch=[-.035,-.0175,0,.02,.08125,.1625]
 for pitch in rootPitch:
  for yaw in yaws:
   transform=pivot@Matrix.Rotation(pitch,4,'X')@Matrix.Rotation(yaw,4,'Z')@pivot.inverted();raw.extend(transform@p for p in rootpoints)
 cm=convex(raw,'V33 temporary actual root envelope');offsets=[Vector((x,y,z))*.004 for x,y,z in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]];expanded=convex([v.co+d for v in cm.vertices for d in offsets],'V33 root receiving margin');bpy.data.meshes.remove(cm);tool=bpy.data.objects.new('V33 temporary receiving tool',expanded);bpy.context.scene.collection.objects.link(tool);bpy.context.view_layer.update()
 for name in CHEEKS:
  o=bpy.data.objects[name];v,f=points(o);materials=list(o.data.materials);m=bpy.data.meshes.new(name+' V33 receiving mesh');m.from_pydata([o.matrix_world.inverted()@p for p in v],[],f);m.update()
  for mat in materials:m.materials.append(mat)
  o.data=m;o.modifiers.clear();bm=bmesh.new();bm.from_mesh(m);initial=abs(bm.calc_volume(signed=True));bm.free();q=o.modifiers.new('Finite actual root receiving space','BOOLEAN');q.operation='DIFFERENCE';q.solver='EXACT';q.object=tool
  with bpy.context.temp_override(object=o,active_object=o,selected_objects=[o],selected_editable_objects=[o]):bpy.ops.object.modifier_apply(modifier=q.name)
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name;volume=bm.calc_volume(signed=True)
  if volume<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces));volume=-volume
  assert volume>0,name;bm.to_mesh(o.data);bm.free();records.append({'name':name,'owner':'body','finiteClosed':True,'positiveVolumeM3':volume,'retainedVolumeFraction':volume/initial,'rootReceivingGapM':.004})
 bpy.data.objects.remove(tool,do_unlink=True);bpy.data.meshes.remove(expanded);bpy.context.view_layer.update()
 assert protected=={o.name:signature(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in changed};assert nodes=={o.name:(o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),json.dumps(dict(o.items()),sort_keys=True,default=lambda x:list(x))) for o in bpy.data.objects if o.type=='EMPTY'}
 return {'region':'directional neck guard receiving underlaps','status':'Coarse actual-solid receiving proposal; appearance and strict seven-pose gate required','changedMeshes':changed,'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'records':records,'outsideMeshesExact':len(protected),'nodesExact':len(nodes),'structuralContract':{'wallM':WALL,'adjacentGuardReceivingGapM':GAP,'relativeChildPitchSamplesRad':PITCHES,'rootPitchSamplesRad':rootPitch,'rootYawSamplesRad':yaws,'guardOwnersAndMotionLimitsExact':True,'headEyesShaftsFrameExact':True,'course4AndRootUnderlapsExact':True,'materialsAndEraTagsRetained':True},'limits':['Finite sampled receiver geometry, not continuous collision/containment or physics proof.','Inward forming preserves directional grids but full rendered curved protection requires visual review.','No new slide actuator: original rigid hinges cause passive independent guard motion.']}
