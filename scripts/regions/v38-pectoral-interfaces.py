"""Pectoral-interfaces02: direct shared finite boundary extrusion and seated panels.
Actual compact-mantle02 input; no Boolean join/carving, no historical plate warp.
"""
from pathlib import Path
import bpy,bmesh,math,runpy
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
LINER='V30 continuous tapered breast liner'
NAMES=[f'V34 formed breast course {r} plate {i}'for r,n in[(1,5),(2,6)]for i in range(1,n+1)]
SEAM=1.11
OUTER=[]
PROFILE=[(1.11,.303,-.39048),(1.18,.293,-.389),(1.24,.265,-.388),(1.285,.231,-.385)]
def ease(u):u=max(0,min(1,u));return u*u*(3-2*u)
def section(z):
 if z<=PROFILE[0][0]:return PROFILE[0][1:]
 if z>=PROFILE[-1][0]:return PROFILE[-1][1:]
 i=next(i for i in range(len(PROFILE)-1)if PROFILE[i][0]<=z<=PROFILE[i+1][0]);a,b=PROFILE[i:i+2];u=(z-a[0])/(b[0]-a[0]);out=[]
 for k in[1,2]:
  d=(b[k]-a[k])/(b[0]-a[0]);m0=d if i==0 else(b[k]-PROFILE[i-1][k])/(b[0]-PROFILE[i-1][0]);m1=d if i+2==len(PROFILE)else(PROFILE[i+2][k]-a[k])/(PROFILE[i+2][0]-a[0]);h=b[0]-a[0];out.append((2*u**3-3*u*u+1)*a[k]+(u**3-2*u*u+u)*h*m0+(-2*u**3+3*u*u)*b[k]+(u**3-u*u)*h*m1)
 return out

def upper(a,z):
 rx,y=section(z)
 if not OUTER:return Vector((rx*math.sin(a),y*math.cos(a),z))
 aa=max(OUTER[0][0],min(OUTER[-1][0],a));q0,q1=next((p,q)for p,q in zip(OUTER,OUTER[1:])if p[0]<=aa<=q[0]);u=(aa-q0[0])/max(1e-10,q1[0]-q0[0]);base=q0[1].lerp(q1[1],u)
 return Vector((base.x*rx/.303,base.y+(y-PROFILE[0][2])*math.cos(aa),z))
def top(a):return 1.285-.042*ease(abs(a)/.90)
def bvh(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();m.calc_loop_triangles();t=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[tuple(f.vertices)for f in m.loop_triangles],all_triangles=True);e.to_mesh_clear();return t

def topology(o):
 m=o.data;bm=bmesh.new();bm.from_mesh(m);closed=all(e.is_manifold for e in bm.edges);vol=abs(bm.calc_volume(signed=True));bm.free();adj={i:set()for i in range(len(m.vertices))}
 for e in m.edges:a,b=e.vertices;adj[a].add(b);adj[b].add(a)
 todo=set(adj);comps=[]
 while todo:
  q=[todo.pop()];count=0
  while q:
   i=q.pop();count+=1
   for j in adj[i]&todo:todo.remove(j);q.append(j)
  comps.append(count)
 return {'closedEdgeManifold':closed,'positiveVolumeM3':vol,'connectedComponentVertexCounts':sorted(comps)}

def install(o,v,f):
 mesh=bpy.data.meshes.new(o.name+' directly constructed finite stock');inv=o.matrix_world.inverted();mesh.from_pydata([inv@p for p in v],[],f);mesh.update()
 for mat in o.data.materials:mesh.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=2e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-9);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(mesh);bm.free();o.data=mesh
 for face in mesh.polygons:face.use_smooth=True
 o['v38PectoralInterfaces']='Direct finite shared-boundary upper backing and curved panel receiving construction; passive inherited proposal'

def apply():
 bpy.context.view_layer.update();liner=bpy.data.objects[LINER];source=bvh(liner);before=[liner.matrix_world@v.co for v in liner.data.vertices];h=runpy.run_path(str(ROOT/'scripts/regions/whole-character-v30-breast-form.py'));sheet=h['solid_sheet'];records=[]
 # Work in native world coordinates so the retained seam vertices become
 # the exact first ring of continuous new outer/inner/side walls.
 bm=bmesh.new();bm.from_mesh(liner.data)
 for v in bm.verts:v.co=liner.matrix_world@v.co
 result=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=Vector((0,0,SEAM)),plane_no=Vector((0,0,1)),clear_outer=True,clear_inner=False)
 edges=[e for e in result['geom_cut']if isinstance(e,bmesh.types.BMEdge)and e.is_boundary];assert edges
 start=edges[0].verts[0];ring=[start];prev=None;cur=start
 while True:
  options=[e.other_vert(cur)for e in cur.link_edges if e in edges and e.other_vert(cur)!=prev];assert options
  nxt=options[0]
  if nxt==start:break
  assert nxt not in ring;ring.append(nxt);prev,cur=cur,nxt
 assert len(ring)==len(edges)==38,'Actual finite seam loop changed; inspect instead of guessing'
 base=[v.co.copy()for v in ring]
 # Actual source finite seam has two arc paths joined by side returns.
 # Select the anterior outer path, preserving its real ordinate geometry.
 lo=min(range(len(base)),key=lambda i:base[i].x);hi=max(range(len(base)),key=lambda i:base[i].x)
 path1=[];j=lo
 while True:
  path1.append(base[j])
  if j==hi:break
  j=(j+1)%len(base)
 path2=[];j=lo
 while True:
  path2.append(base[j])
  if j==hi:break
  j=(j-1)%len(base)
 outer=min([path1,path2],key=lambda p:sum(v.y for v in p)/len(p))
 global OUTER
 OUTER=sorted([(math.asin(max(-1,min(1,p.x/.303))),p)for p in outer],key=lambda v:v[0]);assert len(OUTER)>5
 previous=ring;levels=[]
 for step in range(1,41):
  u=step/40;new=[]
  for p in base:
   angle=math.asin(max(-1,min(1,p.x/.303)));z=SEAM+(top(angle)-SEAM)*u;rx,y=section(z);co=Vector((p.x*rx/.303,p.y+(y-PROFILE[0][2])*math.cos(angle),z));new.append(bm.verts.new(co))
  for j in range(len(ring)):bm.faces.new((previous[j],previous[(j+1)%len(ring)],new[(j+1)%len(ring)],new[j]))
  levels.append([v.co.copy()for v in new]);previous=new
 # The finite cross-section ring spans outer,inner and short side returns.
 # Its top cap closes the stock section; no extra overlapping union solids.
 bm.faces.new(tuple(reversed(previous)));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 assert all(e.is_manifold for e in bm.edges),'Connected backing must be manifold before export/render'
 inv=liner.matrix_world.inverted()
 for v in bm.verts:v.co=inv@v.co
 mesh=bpy.data.meshes.new('Pectoral shared38vertex seam finite liner');bm.to_mesh(mesh);bm.free()
 for mat in liner.data.materials:mesh.materials.append(mat)
 liner.data=mesh;liner['v38PectoralInterfaces']='One continuous source-lower/shared38vertex-seam/formedupper backing with explicit inner outer sidewalls and topstockcap'
 actual=topology(liner);assert actual['closedEdgeManifold']and len(actual['connectedComponentVertexCounts'])==1
 liner.data.update();receiving=bvh(liner);landings=[]
 # Actual receiving tessellation supplies each panel inner wall, with
 # clipped patch vertices barycentric on named backing triangles.
 liner.data.calc_loop_triangles();world=[liner.matrix_world@v.co for v in liner.data.vertices];triangles=[]
 for tri in liner.data.loop_triangles:
  vv=[world[i] for i in tri.vertices];n=(vv[1]-vv[0]).cross(vv[2]-vv[0]);n.normalize();mid=sum(vv,Vector())/3;radial=Vector((mid.x,mid.y,0)).normalized()
  if n.dot(radial)>.35 and mid.y<-.14 and max(p.z for p in vv)>1.03:triangles.append((tri.index,tuple(tri.vertices),vv,n))
 lowerNames=[f'V34 formed breast course 3 plate {i}'for i in range(1,8)];lower=[bvh(bpy.data.objects[n])for n in lowerNames]
 def angle(p):return math.atan2(p.x,-p.y)
 def clip(poly,fn):
  if not poly:return []
  output=[]
  for a,b in zip(poly,poly[1:]+poly[:1]):
   va,vb=fn(a),fn(b)
   if va>=0:output.append(a)
   if (va>=0)!=(vb>=0):
    lo,hi=0.,1.
    for _ in range(28):
     t=(lo+hi)/2;value=fn(a.lerp(b,t))
     if (value>=0)==(va>=0):lo=t
     else:hi=t
    output.append(a.lerp(b,(lo+hi)/2))
  return output
 for r,count,bottom in[(1,5,1.155),(2,6,1.047)]:
  for c in range(1,count+1):
   o=bpy.data.objects[f'V34 formed breast course {r} plate {c}'];center=-.65+(c-.5)*1.3/count;width=1.3/count*.965;points=[];faces=[];pointMap={};receivingTriangles=[]
   def topz(p):return (top(angle(p))-.010)if r==1 else 1.182-.009*abs(angle(p))
   def bottomz(p):return bottom+.016*(1 if center>0 else -1 if center<0 else 0)*(angle(p)-center)/max(.01,width)-.008*(1-((angle(p)-center)/max(.01,width))**2)
   def left(p):return angle(p)-(center-width/2)*(1-.08*ease((topz(p)-p.z)/max(.01,topz(p)-bottom)))
   def right(p):return (center+width/2)*(1-.08*ease((topz(p)-p.z)/max(.01,topz(p)-bottom)))-angle(p)
   for tid,indices,vv,n in triangles:
    poly=clip(vv,lambda p:topz(p)-p.z);poly=clip(poly,lambda p:p.z-bottomz(p));poly=clip(poly,left);poly=clip(poly,right)
    if len(poly)<3:continue
    ids=[]
    for p in poly:
     key=tuple(round(float(x),7)for x in p)
     if key not in pointMap:pointMap[key]=len(points);points.append(p)
     ids.append(pointMap[key])
    for j in range(1,len(ids)-1):
     if len({ids[0],ids[j],ids[j+1]})==3:faces.append((ids[0],ids[j],ids[j+1]));receivingTriangles.append(tid)
   assert faces,('No actual finite receiving patch',o.name)
   # Clipped shared triangle endpoints can differ belowfloatprecision.
   # Weld the RECEIVING surface first, before stock/sidewalls; welding only
   # the final solid creates doubled internal side returns/nonmanifold fans.
   baseMesh=bpy.data.meshes.new('temporary exact receiving patch');baseMesh.from_pydata(points,[],faces);baseMesh.update();patch=bmesh.new();patch.from_mesh(baseMesh);bmesh.ops.remove_doubles(patch,verts=list(patch.verts),dist=2e-7);bmesh.ops.dissolve_degenerate(patch,edges=list(patch.edges),dist=1e-9);patch.verts.ensure_lookup_table();patch.verts.index_update();points=[v.co.copy()for v in patch.verts];faces=[tuple(v.index for v in f.verts)for f in patch.faces];patch.free();bpy.data.meshes.remove(baseMesh)
   # Shared clipped tessellation is continuous, so inner root faces remain
   # coplanar within exact backing triangles rather than crossing facets.
   normals=[Vector()for p in points]
   for face in faces:
    n=(points[face[1]]-points[face[0]]).cross(points[face[2]]-points[face[0]])
    for j in face:normals[j]+=n
   inner=[];outer=[];feet=[];lap=[]
   for idx,(p,n)in enumerate(zip(points,normals)):
    n.normalize();u=max(0,min(1,(topz(p)-p.z)/max(.01,topz(p)-bottomz(p))));root=u<.12
    # Actual backing-derived inner land stays exact at the root. Curved
    # exterior rise follows connected01 instead of a flat translated strip.
    faceOffset=.006+.014*ease(u);gap=0 if root else max(0,faceOffset-.0035)*ease((u-.12)/.18)
    innerPoint=p+gap*n;outerPoint=p+faceOffset*n
    # Receiving correction is restricted to the terminal free margin;
    # the full C2 face is not translated into a horizontal shelf.
    if r==2 and u>.88:
     hits=[tree.ray_cast(Vector((p.x,-1.,p.z)),Vector((0,1,0)),1.5)[0]for tree in lower];hits=[q for q in hits if q is not None]
     if hits:
      w=ease((u-.88)/.12);target=min(q.y for q in hits)-.0015
      innerPoint.y+=(min(innerPoint.y,target)-innerPoint.y)*w
      outerPoint.y=min(outerPoint.y,innerPoint.y-.0035)
      lap.append({'innerPoint':list(innerPoint),'sourceC3FrontY':min(q.y for q in hits),'declaredTerminalInnerGapM':.0015,'terminalWeight':w})
    inner.append(innerPoint);outer.append(outerPoint)
    if root:feet.append({'innerVertexIndex':idx,'actualBackingTriangleSubset':sorted(set(receivingTriangles)),'nearestFiniteSurfaceDistanceM':receiving.find_nearest(innerPoint)[3],'rootStockM':(outerPoint-innerPoint).length})
   countVertices=len(points);v=inner+outer;f=[tuple(reversed(face))for face in faces]+[tuple(j+countVertices for j in face)for face in faces];edges={}
   for face in faces:
    for a,b in zip(face,face[1:]+face[:1]):key=tuple(sorted((a,b)));edges.setdefault(key,[]).append((a,b))
   for items in edges.values():
    if len(items)==1:
     a,b=items[0];f.append((a,b,b+countVertices,a+countVertices))
   print('BASE_PATCH_EDGE_COUNTS',o.name,{n:sum(len(items)==n for items in edges.values())for n in range(1,5)},flush=True)
   install(o,v,f)
   debug=bmesh.new();debug.from_mesh(o.data);bad=[e for e in debug.edges if not e.is_manifold];print('BAD_EDGE_COUNTS',o.name,{n:sum(len(e.link_faces)==n for e in bad)for n in range(5)},'badlength',[(e.calc_length(),len(e.link_faces))for e in bad[:20]],flush=True);debug.free()
   o['wallM']=.0035;t=topology(o);print('ACTUAL_PATCH_TOPOLOGY',o.name,t,flush=True);assert t['closedEdgeManifold']and len(t['connectedComponentVertexCounts'])==1,o.name
   landings.append({'name':o.name,'actualBackingTriangleIds':sorted(set(receivingTriangles)),'finiteRootPatchVertices':len(feet),'maxRootVertexFiniteGapM':max(p['nearestFiniteSurfaceDistanceM']for p in feet)if feet else None,'actualLowerLapSamples':lap[::max(1,len(lap)//12)],'construction':'Actual backing triangles clipped/subdivided barycentrically supply matching inner land tessellation;3.5mm free stock with6mm thickened root and connected edge returns. Only terminal C2 underside margin receives against actual C3 with1.5mm nominal gap; curved external faces retained; strict crossing evidence governs disposition.','limits':'Exact rootface tessellation and vertexgap are checked by unchanged full finite strict screen; finite wall/edge compatibility remains evidence-gated.'})
 for name in NAMES+[LINER]:
  o=bpy.data.objects[name];records.append({'name':name,'owner':o.parent.name,'surfaceRole':o.get('surfaceRole'),'constructionClass':o.get('constructionClass'),'eras':o.get('exteriorEras'),'materials':[m.name if m else None for m in o.data.materials],'usedFaceMaterialValid':all(q.material_index<len(o.data.materials)and o.data.materials[q.material_index]is not None for q in o.data.polygons),'wallM':o.get('wallM'),**topology(o)})
 return {'changedMeshes':NAMES+[LINER],'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'attachmentAndEraMap':records,'sharedBoundary':{'worldZ':SEAM,'vertexCount':38,'exactSourceBoundaryWorldVertices':[list(p)for p in base],'newExtrudedWallRings':40,'stockMethod':'Continuous actual finite source crosssection includes outer/inner/side walls; topcap closes same connected stock. Source crosssection thickness carried into tapered swept section; actual sample checks separate, not nominalalone.'},'panelRootLandings':landings,'authoredProfile':PROFILE,'supportCoherence':'Exact retained lower liner shares38boundaryvertices with directly constructed upper wall. Original moving return seats/tabs, shaft and inspection hinge exact; no frame carve or Boolean fragments.','rigidVsFlexible':'Finite rigid passive cover/backing, one breastplate owner; no flexiblebody or powered addition.','confirmed':'Actual Master03/Maker-clean deep avian breast with curved overlapping courses joining neck/shoulder. July excluded body.','reconstruction':'New hidden support/topology/profile are authored proposals, not engineering or art metrology.','limits':['Manifold/onecomponent is necessary but not universal physicalstock/selfintersection/clearance acceptance.','Root/cervical receiving geometry protected; strict actual rest/open surface checks still required. Existing16.25mm fixed receiving warning remains.']}
