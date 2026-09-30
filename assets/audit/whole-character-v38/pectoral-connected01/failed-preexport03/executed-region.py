"""Pectoral-connected01: direct shared finite boundary extrusion and seated panels.
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
PROFILE=[(1.11,.303,-.39048),(1.18,.293,-.389),(1.24,.265,-.370),(1.285,.231,-.342)]
def ease(u):u=max(0,min(1,u));return u*u*(3-2*u)
def section(z):
 if z<=PROFILE[0][0]:return PROFILE[0][1:]
 if z>=PROFILE[-1][0]:return PROFILE[-1][1:]
 i=next(i for i in range(len(PROFILE)-1)if PROFILE[i][0]<=z<=PROFILE[i+1][0]);a,b=PROFILE[i:i+2];u=(z-a[0])/(b[0]-a[0]);out=[]
 for k in[1,2]:
  d=(b[k]-a[k])/(b[0]-a[0]);m0=d if i==0 else(b[k]-PROFILE[i-1][k])/(b[0]-PROFILE[i-1][0]);m1=d if i+2==len(PROFILE)else(PROFILE[i+2][k]-a[k])/(PROFILE[i+2][0]-a[0]);h=b[0]-a[0];out.append((2*u**3-3*u*u+1)*a[k]+(u**3-2*u*u+u)*h*m0+(-2*u**3+3*u*u)*b[k]+(u**3-u*u)*h*m1)
 return out

def upper(a,z):
 rx,y=section(z);return Vector((rx*math.sin(a),y*math.cos(a),z))
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
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(mesh);bm.free();o.data=mesh
 for face in mesh.polygons:face.use_smooth=True
 o['v38PectoralConnected']='Direct finite shared-boundary upper backing and curved panel receiving construction; passive inherited proposal'

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
 base=[v.co.copy()for v in ring];previous=ring;levels=[]
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
 liner.data=mesh;liner['v38PectoralConnected']='One continuous source-lower/shared38vertex-seam/formedupper backing with explicit inner outer sidewalls and topstockcap'
 actual=topology(liner);assert actual['closedEdgeManifold']and len(actual['connectedComponentVertexCounts'])==1
 liner.data.update();receiving=bvh(liner);landings=[]
 # Plate stock rests outside the actual finite backing, with source third
 # course as a separate lower receiving surface. No arbitrary mount pool.
 lowerNames=[f'V34 formed breast course 3 plate {i}'for i in range(1,8)];lower=[bvh(bpy.data.objects[n])for n in lowerNames]
 for r,count,bottom in[(1,5,1.155),(2,6,1.047)]:
  for c in range(1,count+1):
   o=bpy.data.objects[f'V34 formed breast course {r} plate {c}'];center=-1+(c-.5)*2/count;step=2/count;seats=[]
   def fn(u,v):
    t=2*v-1;a=(center+.5*step*.96*t)*(1-.12*ease(u))*.875;root=top(a)-.008 if r==1 else 1.179-.010*abs(a);z=root+(bottom-root)*u+.014*(1 if center>0 else -1 if center<0 else 0)*t*ease(u)-.010*(1-t*t)*ease(u)
    p=upper(a,z);direction=Vector((math.sin(a),-math.cos(a),0));hit=receiving.ray_cast(p+.080*direction,-direction,.16)
    if hit[0]is not None:p=hit[0]
    elif z<SEAM:
     q=source.ray_cast(p+.080*direction,-direction,.16)
     if q[0]is not None:p=q[0]
    off=.006+.014*ease(u)
    # Carry lower free-margin receiving lap outside actual third-course
    # triangles. Sampling its real surface differs from guessed frontplane.
    if r==2 and u>.45:
     candidates=[tree.ray_cast(p+.080*direction,-direction,.16)[0]for tree in lower];candidates=[q for q in candidates if q is not None]
     if candidates:
      q=max(candidates,key=lambda q:q.dot(direction));desired=q+.005*direction
      if desired.dot(direction)> (p+off*direction).dot(direction):p=p.lerp(desired-off*direction,ease((u-.45)/.45))
    if u==0:seats.append({'backingPoint':list(p),'radialOffsetM':off,'angle':a})
    return p+off*direction
   v,f=sheet(fn,30,20,.0035)
   # Form a connected thickened receiving land at the root inside this same
   # finite panel, reaching the actual named backing rather than floating.
   # Original3.5mm free stock remains outside the short root-return patch.
   half=len(v)//2;foot=[]
   for row in range(3):
    for col in range(21):
     idx=row*21+col;outer=v[idx];t=2*(col/20)-1;angle=(center+.5*step*.96*t)*(1-.12*ease(row/30))*.875;direction=Vector((math.sin(angle),-math.cos(angle),0));hit=receiving.ray_cast(outer+.030*direction,-direction,.060)
     assert hit[0]is not None,('Actual root land misses finite backing',o.name,row,col)
     w=1 if row<2 else .35;v[half+idx]=v[half+idx].lerp(hit[0],w)
     if row<2:foot.append({'innerVertexIndex':half+idx,'actualReceivingPoint':list(hit[0]),'actualSurfaceNormal':list(hit[1]),'actualReceivingTriangleIndex':hit[2],'nearestFiniteSurfaceDistanceM':receiving.find_nearest(v[half+idx])[3],'rootStockDistanceM':(v[idx]-v[half+idx]).length})
   install(o,v,f);o['wallM']=.0035;t=topology(o);assert t['closedEdgeManifold']and len(t['connectedComponentVertexCounts'])==1,o.name;landings.append({'name':o.name,'actualBackingRootSamples':seats[::max(1,len(seats)//5)],'finiteRootLand42CornerPerimeterGridSamples':foot,'construction':'3.5mm finite formed shield with connected nominal6mm thickened root-return lands meeting actual backing;3.5mm free stock; shaped free lap increases to20mm, actual retained third-course receives lower free margin.','limits':'Actual42 rootfoot vertex samples meet finite named backing; between-sample triangles and strictcontact adjacency are checked separately, not weld/engineering certificate; strict same-owner surfaces checked separately.'})
 for name in NAMES+[LINER]:
  o=bpy.data.objects[name];records.append({'name':name,'owner':o.parent.name,'surfaceRole':o.get('surfaceRole'),'constructionClass':o.get('constructionClass'),'eras':o.get('exteriorEras'),'materials':[m.name if m else None for m in o.data.materials],'usedFaceMaterialValid':all(q.material_index<len(o.data.materials)and o.data.materials[q.material_index]is not None for q in o.data.polygons),'wallM':o.get('wallM'),**topology(o)})
 return {'changedMeshes':NAMES+[LINER],'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'attachmentAndEraMap':records,'sharedBoundary':{'worldZ':SEAM,'vertexCount':38,'exactSourceBoundaryWorldVertices':[list(p)for p in base],'newExtrudedWallRings':40,'stockMethod':'Continuous actual finite source crosssection includes outer/inner/side walls; topcap closes same connected stock. Source crosssection thickness carried into tapered swept section; actual sample checks separate, not nominalalone.'},'panelRootLandings':landings,'authoredProfile':PROFILE,'supportCoherence':'Exact retained lower liner shares38boundaryvertices with directly constructed upper wall. Original moving return seats/tabs, shaft and inspection hinge exact; no frame carve or Boolean fragments.','rigidVsFlexible':'Finite rigid passive cover/backing, one breastplate owner; no flexiblebody or powered addition.','confirmed':'Actual Master03/Maker-clean deep avian breast with curved overlapping courses joining neck/shoulder. July excluded body.','reconstruction':'New hidden support/topology/profile are authored proposals, not engineering or art metrology.','limits':['Manifold/onecomponent is necessary but not universal physicalstock/selfintersection/clearance acceptance.','Root/cervical receiving geometry protected; strict actual rest/open surface checks still required. Existing16.25mm fixed receiving warning remains.']}
