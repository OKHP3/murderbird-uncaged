"""Compact finite shoulder plates sampled from the exact body-finish01 envelopes.
No other geometry, owners, joints, rests, repair landmark or material changes.
"""
import bpy,bmesh,math
from mathutils import Vector,Matrix

REPLACEMENTS=tuple(f'V37 {side} {kind} silhouette shell' for side in ('left','right') for kind in ('shoulder','tucked elbow'))
ROWS=40;COLS=34

def samples(obj):
 n=(ROWS+1)*(COLS+1)
 if len(obj.data.vertices)!=2*n:raise ValueError('Source shell is not the pinned regular grid: '+obj.name)
 points=[obj.matrix_world@v.co for v in obj.data.vertices[:n]]
 def point(t,u):
  t=max(0,min(1,t));u=max(0,min(1,u));row=t*ROWS;col=u*COLS;i=min(ROWS-1,int(row));j=min(COLS-1,int(col));v=row-i;w=col-j;k=i*(COLS+1)+j
  return points[k].lerp(points[k+1],w).lerp(points[k+COLS+1].lerp(points[k+COLS+2],w),v)
 def normal(t,u):
  dt=point(min(1,t+.001),u)-point(max(0,t-.001),u);du=point(t,min(1,u+.001))-point(t,max(0,u-.001))
  n=du.cross(dt).normalized();side=1 if 'left' in obj.name else -1
  if n.dot(Vector((side*math.cos(-1.52+3.04*u),math.sin(-1.52+3.04*u),0)))<0:n.negate()
  return n
 return point,normal

def plate(source,parent,mat,point,normal,label,row,col,start,end,center,half,offset,side):
 nr,nc=12,10;verts=[];normals=[]
 for i in range(nr+1):
  t=i/nr
  for j in range(nc+1):
   across=2*j/nc-1
   # Broad receiving crown, tapered free trailing edge and a rounded central
   # overhang make actual varied plate outlines, not seams on a smooth cap.
   width=1-.37*t*t
   u=center+half*across*width+.019*side*t*t
   station=start+(end-start)*t+.018*(1-across*across)*t*t
   n=normal(station,u);p=point(station,u)
   lift=offset+.005*t*t*(1-across*across)
   verts.append(p+n*lift);normals.append(n)
 count=len(verts);wall=.005
 verts += [p-n*wall for p,n in zip(verts.copy(),normals)];faces=[]
 for i in range(nr):
  for j in range(nc):
   k=i*(nc+1)+j;q=(k,k+1,k+nc+2,k+nc+1);faces += [q,tuple(count+x for x in reversed(q))]
 boundary=list(range(nc+1))+[i*(nc+1)+nc for i in range(1,nr+1)]+[nr*(nc+1)+j for j in range(nc-1,-1,-1)]+[i*(nc+1) for i in range(nr-1,0,-1)]
 for i,a in enumerate(boundary):b=boundary[(i+1)%len(boundary)];faces.append((a,b,count+b,count+a))
 name=f'V38 {label} {"mantle" if "tucked elbow" not in source.name else "elbow"} layered course {row+1} plate {col+1}'
 data=bpy.data.meshes.new(name+' finite stock');data.from_pydata(verts,[],faces);data.materials.append(mat);data.update()
 bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 if not all(e.is_manifold for e in bm.edges) or bm.calc_volume(signed=True)<=0:raise ValueError('Invalid closed finite plate: '+name)
 bm.to_mesh(data);bm.free()
 for polygon in data.polygons:polygon.use_smooth=True
 obj=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(obj);obj.parent=parent;obj.matrix_parent_inverse=Matrix.Identity(4);obj.matrix_basis=Matrix.Identity(4);bpy.context.view_layer.update()
 inverse=obj.matrix_world.inverted()
 for vertex in data.vertices:vertex.co=inverse@vertex.co
 obj['region']='shoulder';obj['surfaceRole']='plate';obj['exteriorEras']=source.get('exteriorEras');obj['constructionClass']='proposed-passive'
 obj['sourceEnvelope']=source.name;obj['wallM']=wall;obj['geometryStatus']='V38 shoulder-study01 compact layered rigid proposal; likeness and full motion clearance unaccepted'
 obj['authoringRole']='Finite tapered formed plate; one retained mantle/elbow owner; no flight surface or cross-joint bridge'
 data.update();return obj

def apply():
 bpy.context.view_layer.update();added=[];attachments=[]
 for name in REPLACEMENTS:
  source=bpy.data.objects.get(name)
  if source is None or source.type!='MESH' or not source.parent:raise ValueError('Pinned shell missing: '+name)
  label='left' if 'left' in name else 'right';side=1 if label=='left' else -1;parent=source.parent;mat=source.data.materials[0]
  if parent.name not in (label+'-mantle',label+'-wing-shield'):raise ValueError('Source owner mismatch')
  if not mat.get('eraFinishes'):raise ValueError('Source shoulder material lacks era profiles')
  point,normal=samples(source)
  courses=[(.014,.253,5,.011),(.194,.449,6,.008),(.393,.645,6,.005),(.590,.829,5,.002),(.782,.967,4,0)] if 'tucked elbow' not in name else [(.150,.564,4,.009),(.488,.929,4,.003)]
  for row,(start,end,num,layer) in enumerate(courses):
   spacing=.984/num
   for col in range(num):
    center=.008+(col+.5)*spacing+(.12 if row%2 else -.055)*spacing
    center=max(spacing*.48,min(1-spacing*.48,center));half=spacing*.49
    obj=plate(source,parent,mat,point,normal,label,row,col,start+.010*math.sin(row+col*1.7),end-.009*col/max(1,num-1),center,half,layer,side)
    added.append(obj.name);attachments.append({'name':obj.name,'owner':parent.name,'sourceEnvelope':name,'role':'passive formed plate','eras':obj.get('exteriorEras'),'material':mat.name})
  bpy.data.objects.remove(source,do_unlink=True)
 bpy.context.view_layer.update()
 return {'removedMeshes':list(REPLACEMENTS),'addedMeshes':added,'changedMeshes':[],
 'attachments':attachments,'method':'Bilinear samples from actual regular outer grids of four frozen source envelopes; discrete closed 5mm finite plates with tapered trailing edges, staggered leading edges and physical row offsets. No painted seams.',
 'confirmation':'Owner motion direction is flightless compact balance/shield/shove; actual selected raster references show overlapping near-wing courses.',
 'reconstruction':'Exact segment outlines, thickness, row ordering, unseen far side and receiving gap remain authored proposals.'}
