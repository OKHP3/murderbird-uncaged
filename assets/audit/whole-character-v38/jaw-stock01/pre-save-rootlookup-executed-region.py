"""One finite jaw-wall repair: immutable exterior and socket, ordered vertical stock."""
import bpy,bmesh,hashlib,json
from mathutils import Vector
NAME='V32 formed mandibular bowl'
KEYS=[(r,c)for r in range(53)for c in range(33)if r<=5 or c<=6 or c>=26 or r>=49]
def digest(v):return hashlib.sha256(json.dumps([list(p)for p in v]).encode()).hexdigest()
def apply():
 bpy.context.view_layer.update();o=bpy.data.objects[NAME];old=[v.co.copy()for v in o.data.vertices];half=len(KEYS);assert half==932 and len(old)==1864;idx={k:i for i,k in enumerate(KEYS)};assert idx[(12,1)]==283;M=o.matrix_world.copy();inv=M.inverted();world=[M@p for p in old];new=old.copy();blend=[]
 for i,(r,c)in enumerate(KEYS):
  if r<=14:continue
  t=min(1,(r-14)/8);t=t*t*(3-2*t);root=idx[(14,c)];delta=(world[half+root]-world[root])*(1-t)+Vector((0,0,.0035))*t
  new[half+i]=inv@(world[i]+delta)
  if r<=22:blend.append({'row':r,'column':c,'rootWeight':1-t})
 m=bpy.data.meshes.new('V38 jaw-stock01 ordered finite wall');m.from_pydata(new,[],[tuple(p.vertices)for p in o.data.polygons]);m.update()
 for mat in o.data.materials:m.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));vol=bm.calc_volume(signed=True)
 if vol<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces));vol=bm.calc_volume(signed=True)
 assert vol>0 and all(e.is_manifold for e in bm.edges)
 unseen=set(bm.verts);components=0
 while unseen:
  components+=1;stack=[unseen.pop()]
  while stack:
   v=stack.pop()
   for e in v.link_edges:
    w=e.other_vert(v)
    if w in unseen:unseen.remove(w);stack.append(w)
 bm.to_mesh(m);bm.free()
 for f in m.polygons:f.use_smooth=True
 assert all(tuple(m.vertices[i].co)==tuple(old[i])for i in range(half));protected=[i+l*half for i,(r,c)in enumerate(KEYS)if r<=14 for l in[0,1]];assert all(tuple(m.vertices[i].co)==tuple(old[i])for i in protected)
 o.data=m;o['constructionDescription']='Jaw-owned finite rigid stock study: original complete outer surface and paired root/socket rows0–14 exact. Free inner wall is an ordered +nativeZ3.5mm extrusion, with original actual root-vector blend rows15–22; ordered existing rim/cap closes stock. No pervertex normal-sign inset. Sampled self/interface qualification separate.';o['v38JawStock01']='Stock repair only; fullouter932vertices and jawSocket283 exact; current3.5mm is vertical separation, not uniform normal thickness or engineering acceptance.'
 return {'status':'Jaw stock repair proposal; outer/head silhouette exact, finite fit qualification pending','changedMeshes':[NAME],'changedNodes':[],'construction':[{'name':NAME,'owner':o.parent.name,'nonmanifoldEdges':0,'signedVolumeM3':vol,'connectedComponents':components,'outerVertices':half,'outerLocalSHA256Before':digest(old[:half]),'outerLocalSHA256After':digest([v.co for v in m.vertices[:half]]),'pairedRootVerticesExact':len(protected),'socketIndex283Exact':True}],'actualConstruction':'Nativeworld +Z3.5mm consistent inner graph; inherited root delta blended C1 via smoothstep rows15–22; full wall/rim/cap same ordered connectivity. No new sign-inset rule.','ownership':'Original rigidjaw owner/material/era remains; no new node or head-jaw bridge','limits':['3.5mm vertical stock is not uniform normal thickness.','Exact source outer shape preserved; no new silhouette design or likeness approval.','Preserved receivingroot retains inherited contacts; not a new seating certification.','Rest/Maker endpoint sample only; no continuous sweep or final strike claim.']}
