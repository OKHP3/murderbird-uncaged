"""Orbital-frame02: newly constructed rail and three rearward cheek courses.
Actual breast-course02 input. Twelve existing identities, new finite geometry;
actual temporal wall used only for declared receiving lands, never allheadpool.
"""
from pathlib import Path
import bpy,bmesh,math,runpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
BROWS=[f'V33 diagonal brow receiver {s} {i}'for s in(-1,1)for i in range(3)]
SHIELDS=[f'V38 optic cheek shield {s} {i}'for s in(-1,1)for i in range(3)]
NAMES=BROWS+SHIELDS
EYE=Vector((0,-.577800006,1.725484014));WALL=.0045
RAIL=[(-.644,1.766,.022),(-.610,1.802,.030),(-.550,1.829,.041),(-.470,1.835,.044),(-.398,1.825,.037),(-.355,1.801,.026)]
SEGMENTS=[(.64,1),(.31,.70),(0,.35)]
CHEEKS=[(-.535,1.781,-.378,1.780,.048),(-.518,1.693,-.394,1.726,.043),(-.516,1.671,-.429,1.689,.026)]
def ease(u):u=max(0,min(1,u));return u*u*(3-2*u)
def sample(rows,t):
 u=max(0,min(1,t))*(len(rows)-1);i=min(int(u),len(rows)-2);s=u-i;a,b,c,d=rows[max(0,i-1)],rows[i],rows[i+1],rows[min(i+2,len(rows)-1)]
 return [.5*(2*b[k]+(-a[k]+c[k])*s+(2*a[k]-5*b[k]+4*c[k]-d[k])*s*s+(-a[k]+3*b[k]-3*c[k]+d[k])*s*s*s)for k in range(len(b))]
def sheet(points,nu,nv):
 half=len(points);v=points+[p-Vector((WALL if p.x>0 else -WALL,0,0))for p in points];f=[];stride=nv+1
 for row in range(nu):
  for col in range(nv):a=row*stride+col;b=a+stride;f +=[(a,a+1,b+1,b),(half+b,half+b+1,half+a+1,half+a)]
 boundary=list(range(stride))+[i*stride+nv for i in range(1,nu+1)]+[nu*stride+j for j in range(nv-1,-1,-1)]+[i*stride for i in range(nu-1,0,-1)]
 for a,b in zip(boundary,boundary[1:]+boundary[:1]):f.append((a,b,b+half,a+half))
 return v,f
def apply():
 bpy.context.view_layer.update();records=[]
 for side in(-1,1):
  target=bpy.data.objects[f'V31 fixed temporal receiving wall {side}'];target.data.calc_loop_triangles();tree=BVHTree.FromPolygons([target.matrix_world@v.co for v in target.data.vertices],[tuple(t.vertices)for t in target.data.loop_triangles],all_triangles=True)
  for family,names in [('brow',BROWS),('cheek',SHIELDS)]:
   for course in range(3):
    name=f'V33 diagonal brow receiver {side} {course}'if family=='brow'else f'V38 optic cheek shield {side} {course}';o=bpy.data.objects[name];points=[];lands=[];nu,nv=40,12
    for row in range(nu+1):
     u=row/nu
     for col in range(nv+1):
      v=col/nv
      if family=='brow':
       lo,hi=SEGMENTS[course];t=lo+(hi-lo)*u;y,z,width=sample(RAIL,t);qa=sample(RAIL,max(0,t-.001));qb=sample(RAIL,min(1,t+.001));dy,dz=qb[0]-qa[0],qb[1]-qa[1];length=math.hypot(dy,dz);taper=1-.15*ease((u-.6)/.4);y-=dz/length*(v-.5)*width*taper;z+=dy/length*(v-.5)*width*taper;freeX=.163+.004*math.sin(math.pi*v)**2+.0015*(2-course)
       root=col>=nv-2 and ((course==2 and u>.64)or(course!=2 and .15<u<.86))
      else:
       ya,za,yb,zb,width=CHEEKS[course];y=ya+(yb-ya)*u+(v-.5)*.014*(1-.45*ease(u));z=za+(zb-za)*u+.008*math.sin(math.pi*u)+(v-.5)*width*(1-.42*ease(u));freeX=.176+course*.005+.003*math.sin(math.pi*v)**2
       root=(row<=4 or row>=nu-4)
      radius=math.hypot(y-EYE.y,z-EYE.z)
      if radius<.063:
       ratio=.063/radius;y=EYE.y+(y-EYE.y)*ratio;z=EYE.z+(z-EYE.z)*ratio
      hit=tree.ray_cast(Vector((side*.8,y,z)),Vector((-side,0,0)))if root else(None,None,None,None)
      x=freeX
      if hit[0]is not None:
       # Integral wall-facing return: real receiving point, finite stock;
       # only actual supported outer-root zones approach the fixed wall.
       blend=1 if family=='cheek'and(row<=2 or row>=nu-2)else ease((v-.72)/.28)if family=='brow'else .5
       x=freeX*(1-blend)+(abs(hit[0].x)+.0015+WALL)*blend
       lands.append({'outerVertex':len(points),'target':target.name,'finiteReceivingPoint':list(hit[0]),'normal':list(hit[1]),'receivingTriangle':hit[2],'blend':blend})
      points.append(Vector((side*x,y,z)))
    assert all(.10<abs(p.x)<.23 and -.70<p.y<-.30 and 1.60<p.z<1.90 for p in points),('Reconstructed panel escaped actual head-region bounds',name)
    assert len(lands)>8,('No actual finite wallland',name)
    verts,faces=sheet(points,nu,nv);m=bpy.data.meshes.new(name+' reconstructed orbital finite panel');inv=o.matrix_world.inverted();m.from_pydata([inv@p for p in verts],[],faces);m.update()
    for mat in o.data.materials:m.materials.append(mat)
    bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
    if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
    volume=bm.calc_volume(signed=True);assert volume>0;bm.to_mesh(m);bm.free();o.data=m
    for f in m.polygons:f.use_smooth=True
    o['v38OrbitalFrame']='Reconstructed angled rearward orbital rail/short temple courses with integral finite receiving returns; proposal'
    actual=[o.matrix_world@v.co for v in m.vertices];half=len(points);measured=[]
    for q in lands:
     p=actual[q['outerVertex']+half];hit=tree.find_nearest(p);measured.append({**q,'actualInnerPoint':list(p),'nearestFinitePoint':list(hit[0]),'actualFiniteGapM':hit[3]})
    records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'constructionClass':o.get('constructionClass'),'materials':[m.name if m else None for m in o.data.materials],'newVertexCount':len(m.vertices),'newFaceCount':len(m.polygons),'closedEdgeManifold':True,'positiveVolumeM3':volume,'axialStockM':WALL,'actualStockErrorM':max(abs((actual[i]-actual[i+half]).length-WALL)for i in range(half)),'wallReceivingWitnesses':measured,'receivingGapRangeM':[min(q['actualFiniteGapM']for q in measured),max(q['actualFiniteGapM']for q in measured)],'limits':'Integral stock/return points meet named finite support with nominal1.5mm gap where blend1; partialtransition faces/contacts separately screen. Not fastener/load/wholepatch guarantee.'})
 return {'changedMeshes':NAMES,'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'attachmentAndEraMap':records,'actualRailNativeYZWidth':RAIL,'actualCheekNativeControls':CHEEKS,'construction':'Newly tessellated finite angled rail in3overlapping sections plus3short down/rear courses per side.4.5mm axial stock, integral return zones onto actual fixed temporal wall; no inherited concentricstrip displacement or allheadprojection.','rigidVsFlexible':'Twelve passive rigid head-owned panels, no cover/jaw rigid bridge or powered earlierhardware.','confirmed':'ActualJuly HEAD ONLY dominant swept brow and descending cheekcourses; Master03/Maker-clean fullbird crosscheck.','reconstruction':'Exact unseen panel/receiving geometry and dimensions authored, not rastermetrology/manufacturing acceptance.','protected':'Opticcups/floors/lips/apertures,seats/centers,billactualtriangles/extrema,jawaxis/bowl397/socket,cranialcoverroots/crown/allbody/pivots/materials unchanged. Sourcebreastcourse02+ninecontacts retained.','limits':['Finite receivingpoint/stock and manifold tests do not certify continuoussurface fit; strict regionfullpool diagnostic after firstvisual.','Orbital keepout derivedfromactual sourcecenter with63mm authored radius, not visibility/clearance acceptance.']}
