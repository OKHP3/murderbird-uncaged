"""Upper bill transverse vault proposal; longitudinal extrema and actual roots retained."""
import bpy,bmesh,math
from mathutils import Vector
NAMES=[f'V32 returned upper bill course {i}' for i in range(3)]
COURSES=[(0,.36),(.36,.72),(.72,1)]
def ease(t):
 t=max(0,min(1,t));return t*t*(3-2*t)
def apply(second=False):
 bpy.context.view_layer.update();records=[]
 for c,(lo,hi) in enumerate(COURSES):
  o=bpy.data.objects[NAMES[c]];mw=o.matrix_world.copy();inv=mw.inverted();old=[v.co.copy() for v in o.data.vertices];src=[mw@v for v in old];half=49*48;assert len(src)==half*2;formed=[];stocks=[]
  for layer in range(2):
   for r in range(49):
    q=lo+(hi-lo)*r/48;D=src[r*48];C=src[r*48+12];w=abs(D.x)/.8;span=math.hypot(C.y-D.y,C.z-D.z);wall=min(.003,.2*span,.3*w)
    strength=(ease((q-.03)/.33)*ease((1-q)/.06) if second else ease((q-.03)/.09)*ease(abs(q-.72)/.10)*ease((1-q)/.06))
    width=w*(1-(.08 if second else .16)*strength);eta=wall/span if layer else 0;width-=wall if layer else 0
    for j in range(48):
     k=j//12;u=(j%12)/12
     if k==0:v=(.06+.88*u if second else .12+.76*u);x=width*((.82+.18*math.sin(math.pi*u)) if second else (.5+.5*math.sin(math.pi*u)))
     elif k==1:v=(.94+.06*(1-abs(1-2*u)) if second else .88+.12*math.sin(math.pi*u));x=(width*.82*(1-2*u) if second else width*.5*math.cos(math.pi*u))
     elif k==2:v=(.94-.88*u if second else .88-.76*u);x=-width*((.82+.18*math.sin(math.pi*u)) if second else (.5+.5*math.sin(math.pi*u)))
     else:v=(.06*abs(1-2*u) if second else .12-.12*math.sin(math.pi*u));x=(width*.82*(-1+2*u) if second else -width*.5*math.cos(math.pi*u))
     v=eta+(1-2*eta)*v;target=Vector((x,D.y+(C.y-D.y)*v,D.z+(C.z-D.z)*v));index=layer*half+r*48+j;p=src[index].lerp(target,strength)
     formed.append(old[index] if (c==0 and r<=4) or strength==0 else inv@p)
  m=bpy.data.meshes.new(o.name+' ordered vaulted stock');m.from_pydata(formed,[],[tuple(f.vertices) for f in o.data.polygons]);m.update()
  for mat in o.data.materials:m.materials.append(mat)
  bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));nonmanifold=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True)
  if volume<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces));volume=bm.calc_volume(signed=True)
  assert nonmanifold==0 and volume>0,(o.name,nonmanifold,volume);bm.to_mesh(m);bm.free()
  for f in m.polygons:
   indices=[i%half for i in f.vertices];bridge=all(36<=i%48<=42 for i in indices) or all(42<=i%48<=47 or i%48==0 for i in indices)
   f.use_smooth=not(second and bridge)
  o.data=m;o['constructionDescription']='Rigid upper-bill transverse vault with ordered dorsal ridge/shoulder/side faces and finite paired stock; source longitudinal extrema and course0 actual root retained; proposal fit qualified separately.';o['v38BillVault01']='Transverse geometry reconstruction only; no hook extension, jaw, pivot, era or material change'
  world=[mw@v.co for v in m.vertices];stocks=[(world[i]-world[i+half]).length for i in range(half)]
  assert c!=0 or all(m.vertices[i].co==old[i] for layer in range(2) for r in range(5) for j in range(48) for i in [layer*half+r*48+j])
  records.append({'name':o.name,'owner':o.parent.name,'nonmanifoldEdges':nonmanifold,'signedVolumeM3':volume,'pairedStockVectorMinMaxM':[min(stocks),max(stocks)],'maxActualVertexDisplacementM':max((m.vertices[i].co-old[i]).length for i in range(len(old)))})
 points=[o.matrix_world@v.co for o in bpy.data.objects if o.name in NAMES for v in o.data.vertices];markerObject=bpy.data.objects['bill-contact'];marker=markerObject.matrix_world.translation.copy();lead=min(points,key=lambda p:p.y)
 if second:
  matrix=markerObject.matrix_world.copy();matrix.translation=lead;markerObject.matrix_world=matrix;bpy.context.view_layer.update()
 assert lead.y>=marker.y-1e-7
 return {'changedMeshes':NAMES,'construction':records,'scheme':('Shallow two-plane formed dorsal vault/near-flat lateral faces, 6% span shoulder depth, 8% nominal width reduction, gradual entirecourse0 root transition, no preserved full contact ring.' if second else 'Deep curved first vault,12% span shoulder depth,16% nominal reduction; full contact ring preserved.'),'pairedWall':'Same ordered3mm max paired inner domain, no independently signed normal inset','rootRows0to4OuterInnerExact':True,'contactLandQ072Exact':not second,'contactBeforeNative':list(marker),'contactAfterNative':list(markerObject.matrix_world.translation),'changedNodes':['bill-contact'] if second else [],'noVertexMoreForwardThanMarker':True,'contactMarkerNativeXYZ':list(marker),'protected':'Jaw/root receivers, all owner transforms/control/era tags/materials, body/neck/crown/optic unchanged.','limits':['Width/section dimensions are authored proposals, not reference measurements.','Manifold positive stock and paired lengths do not prove self/interface clearance or manufacturing fit.','Vault keeps dorsal/cutting longitudinal extrema; projected non-centerline thickness and apparent profile may change.','Existing course butt seats remain construction inheritance, not new supported lap acceptance.']}
