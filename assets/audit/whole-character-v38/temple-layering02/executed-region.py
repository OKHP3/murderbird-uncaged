"""Temple-layering02: smooth shared lateral field and true multi-triangle lands.
Repair input cheek-supported02,28 passive meshes only; source wall exact.
"""
import bpy,bmesh,math,numpy as np
from mathutils import Vector
BROWS=[f'V33 diagonal brow receiver {s} {i}'for s in(-1,1)for i in range(3)]
SHIELDS=[f'V38 optic cheek shield {s} {i}'for s in(-1,1)for i in range(3)]
LEAVES=[f'V33 swept temporal leaf {s} {i}'for s in(-1,1)for i in range(7)]
ROOTS=[f'V31 temporal fitting root {s} {i}'for s in(-1,1)for i in range(3)]
FITTINGS=[f'V31 passive temporal fitting {s} {i}'for s in(-1,1)for i in range(3)]
WALLS=[f'V31 fixed temporal receiving wall {s}'for s in(-1,1)]
NAMES=WALLS+BROWS+SHIELDS+LEAVES+ROOTS+FITTINGS

def install(name,world,faces,kind,records):
 o=bpy.data.objects[name];mesh=bpy.data.meshes.new(name+' compatible finite interface');inv=o.matrix_world.inverted();mesh.from_pydata([inv@p for p in world],[],faces);mesh.update()
 for mat in o.data.materials:mesh.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 volume=bm.calc_volume(signed=True);assert volume>0;bm.to_mesh(mesh);bm.free();o.data=mesh
 for f in mesh.polygons:f.use_smooth=True
 o['v38TempleLayering']='Passive smooth finite surface/receiving interface repair proposal'
 records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'kind':kind,'closedEdges':True,'positiveVolumeM3':volume,'materials':[m.name if m else None for m in mesh.materials]})

def sample(rows,t):
 q=max(0,min(1,t))*(len(rows)-1);i=min(int(q),len(rows)-2);u=q-i;a,b,c,d=rows[max(0,i-1)],rows[i],rows[i+1],rows[min(i+2,len(rows)-1)]
 return [.5*(2*b[k]+(-a[k]+c[k])*u+(2*a[k]-5*b[k]+4*c[k]-d[k])*u*u+(-a[k]+3*b[k]-3*c[k]+d[k])*u*u*u)for k in range(len(b))]
OUTER=[(-.630,1.820),(-.530,1.890),(-.395,1.880),(-.275,1.815),(-.235,1.720),(-.280,1.625),(-.370,1.590),(-.470,1.638)]

def apply():
 bpy.context.view_layer.update();records=[];lands=[];surfaces=[]
 for side in(-1,1):
  lip=bpy.data.objects[f'V33 recessed optic retaining lip {side}'];lp=[lip.matrix_world@v.co for v in lip.data.vertices];cy=(max(p.y for p in lp)+min(p.y for p in lp))*.5;cz=(max(p.z for p in lp)+min(p.z for p in lp))*.5;radius=max(math.hypot(p.y-cy,p.z-cz)for p in lp)+.003
  def lateral(y,z):return .132+.012*math.exp(-((y+.40)/.18)**2-((z-1.75)/.20)**2)
  def field(u,v):
   y,z=sample(OUTER,u);dy,dz=y-cy,z-cz;rr=math.hypot(dy,dz);assert rr>radius+.008
   r=radius+(rr-radius)*v;return Vector((side*lateral(cy+dy/rr*r,cz+dz/rr*r),cy+dy/rr*r,cz+dz/rr*r))
  # Direct finite side-domain shell; no Boolean cavity or old arbitrary cubic.
  def plate(name,fn,nu,nv,stock,kind,offset):
   outer=[fn(i/nu,j/nv)+Vector((side*offset,0,0))for i in range(nu+1)for j in range(nv+1)];n=len(outer);verts=outer+[p-Vector((side*stock,0,0))for p in outer];faces=[];stride=nv+1;signs=[]
   for i in range(nu):
    for j in range(nv):
     a=i*stride+j;b=a+stride;faces.extend([(a,a+1,b+1,b),(n+b,n+b+1,n+a+1,n+a)]);p,q,w=outer[a],outer[a+1],outer[b];jac=(q.y-p.y)*(w.z-p.z)-(q.z-p.z)*(w.y-p.y);signs.append(jac)
   assert max(signs)<-1e-10 or min(signs)>1e-10,(name,min(signs),max(signs))
   boundary=list(range(stride))+[i*stride+nv for i in range(1,nu+1)]+[nu*stride+j for j in range(nv-1,-1,-1)]+[i*stride for i in range(nu-1,0,-1)]
   for i,a in enumerate(boundary):b=boundary[(i+1)%len(boundary)];faces.append((a,b,n+b,n+a))
   install(name,verts,faces,kind,records);surfaces.append({'part':name,'parameterRows':nu,'parameterColumns':nv,'axialStockM':stock,'outerOffsetFromSupportM':offset,'discreteNativeYZJacobianRange':[min(signs),max(signs)]})
  plate(f'V31 fixed temporal receiving wall {side}',field,96,24,.004,'Direct connected compound-curved backing enclosing skull behind actual optic lip, shaped rim/outerreturn, no cubic projection residual',0)
  def strap(name,curve,width,stock,offset,a=0,b=1,nu=40):
   def fn(t,v):
    u=a+(b-a)*t;y,z=sample(curve,u);q=sample(curve,max(0,u-.001));w=sample(curve,min(1,u+.001));dy,dz=w[0]-q[0],w[1]-q[1];length=math.hypot(dy,dz);taper=.65+.35*math.sin(math.pi*t)**.8;yy=y-dz/length*(v-.5)*width*taper;zz=z+dy/length*(v-.5)*width*taper
    # Actual coherent lateral field shared by backing and armor, with
    # integral finite return ends meeting it, no floating entire plate.
    lift=stock+(offset-stock)*math.sin(math.pi*t)**2
    return Vector((side*(lateral(yy,zz)+lift),yy,zz))
   plate(name,fn,nu,10,stock,'Asymmetric swept compact curved strap/guard with finite integral receiving ends on declared support field',0)
  brow=[(-.617,1.810),(-.568,1.843),(-.500,1.841),(-.433,1.824)]
  for i,(a,b)in enumerate([(0,.35),(.34,.70),(.69,1)]):strap(f'V33 diagonal brow receiver {side} {2-i}',brow,.023,.0045,.010+i*.003,a,b)
  strap(f'V38 optic cheek shield {side} 0',[(-.439,1.817),(-.450,1.770),(-.480,1.725),(-.450,1.673),(-.391,1.647)],.022,.0045,.022,nu=64)
  strap(f'V38 optic cheek shield {side} 1',[(-.415,1.770),(-.390,1.737),(-.350,1.700)],.036,.0045,.014)
  strap(f'V38 optic cheek shield {side} 2',[(-.364,1.702),(-.331,1.665),(-.292,1.636)],.039,.0045,.013)
  guards=[([(-.465,1.850),(-.410,1.831),(-.350,1.793)],.032),([(-.397,1.829),(-.350,1.796),(-.304,1.752)],.038),([(-.340,1.788),(-.299,1.748),(-.270,1.690)],.041),([(-.297,1.734),(-.264,1.690),(-.253,1.642)],.038),([(-.282,1.680),(-.298,1.636),(-.336,1.600)],.034),([(-.330,1.665),(-.357,1.624),(-.397,1.613)],.038),([(-.397,1.660),(-.439,1.649),(-.471,1.630)],.027)]
  for i,(curve,width)in enumerate(guards):strap(f'V33 swept temporal leaf {side} {i}',curve,width,.003,.010+.003*(i%2))
  # Complete actual receiving triangles + exact planar annular fitting bases.
  for i,(target,rr,cc)in enumerate([(f'V38 optic cheek shield {side} 1',20,5),(f'V38 optic cheek shield {side} 2',20,5),(f'V33 swept temporal leaf {side} 5',20,5)]):
   o=bpy.data.objects[target];o.data.calc_loop_triangles();pts=[o.matrix_world@v.co for v in o.data.vertices];stride=11;ids={row*stride+col for row in range(rr-3,rr+4)for col in range(cc-3,cc+4)};tri=[tuple(t.vertices)for t in o.data.loop_triangles if set(t.vertices)<=ids];assert len(tri)==72
   used=sorted(ids);mp={k:j for j,k in enumerate(used)};base=[pts[k]for k in used];ff=[tuple(mp[k]for k in t)for t in tri];n=len(base);plane=max(abs(p.x)for p in base)+.004;verts=base+[Vector((side*plane,p.y,p.z))for p in base];faces=[tuple(reversed(t))for t in ff]+[tuple(n+k for k in t)for t in ff]
   from collections import Counter
   ec=Counter(tuple(sorted((t[j],t[(j+1)%3])))for t in ff for j in range(3))
   for t in ff:
    for j in range(3):
     a,b=t[j],t[(j+1)%3]
     if ec[tuple(sorted((a,b)))]==1:faces.append((a,b,b+n,a+n))
   root=f'V31 temporal fitting root {side} {i}';install(root,verts,faces,'Actual72 triangle receiving land and complete planar outer mount, integral finite return',records)
   cy0,cz0=pts[rr*stride+cc].y,pts[rr*stride+cc].z;count=48;profile=[(plane,.0055),(plane+.001,.0055),(plane+.004,.005),(plane+.004,.0022),(plane,.0022)];fv=[Vector((side*x,cy0+rad*math.cos(2*math.pi*j/count),cz0+rad*math.sin(2*math.pi*j/count)))for x,rad in profile for j in range(count)];faces=[]
   for row in range(len(profile)):
    nxt=(row+1)%len(profile)
    for j in range(count):k=(j+1)%count;faces.append((row*count+j,row*count+k,nxt*count+k,nxt*count+j))
   fit=f'V31 passive temporal fitting {side} {i}';install(fit,fv,faces,'Passive11mm annular fitting with full planar return/base correspondence',records)
   lands.append({'root':root,'fitting':fit,'receiver':target,'receiverGridRows':[rr-3,rr+3],'receiverGridColumns':[cc-3,cc+3],'actualFullPatchYZExtentsM':[max(p.y for p in base)-min(p.y for p in base),max(p.z for p in base)-min(p.z for p in base)],'fittingFootDiameterM':.011,'returnOuterNativeSignedX':side*plane,'actualInnerTriangles':72,'minimumAxialReturnDepthM':.004})
  surfaces.append({'side':side,'actualRetainedLipCenterNativeYZ':[cy,cz],'actualInnerSupportRimRadiusM':radius,'outerSkullArcControlsNativeYZ':OUTER,'construction':'Recessed connected skull sector; asymmetric Cartesian swept plate footprints and finite return ends using same smooth lateral field; optic lip/bill/journal/cranialgeometry unchanged. Support rim offset3mm from actual lip radialextent, not a full seat proof.'})
 return {'changedMeshes':NAMES,'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'attachmentAndEraMap':records,'actualFootlands':surfaces,'pairedFittingSeats':lands,'construction':'Internal recessed finite skull support around actual optic lip, Asymmetric S-like rising cheekstrap and individually swept tapered rear guards over recessed support field. Full72triangle mounting returns andannularbases retained. No cubic projection/patchedslab/lattice.','rigidVsFlexible':'All40 existing passive objects headownedMaker/Mechanic/Builder, no poweredhardware.','confirmation':'Actual July headonly +Master03/Makerclean, regional shape reconstruction not dimensions.','reconstruction':'Skull outerarc/supports/guard courses authored proposal; no owner/physicalcertification.','protected':'True optics/bill/jaw/source283socket/journals andindependentcranialplusbody/leftrestriction exact.','limits':['Actual entire changed40 versusfull finiteheadpool screen after firstvisual.','Commonparametric faces differ in finite lapstock; no automaticattachment or clearanceclaim from commonfamily.','Full fittingbases useactual trianglelands butfiniteunderside containment is separatelychecked.']}
