"""One rigid jaw-owned side-blade reconstruction; actual root/socket and cap exact.
Construction parameter rows are not new texture UV work. Authored dimensions.
"""
import bpy,bmesh,math,json,hashlib
from mathutils import Vector
NAME='V32 formed mandibular bowl'
def ease(x):
 x=max(0,min(1,x));return x*x*(3-2*x)
def curve(knots,t):
 xs=[x for x,y in knots];ys=[y for x,y in knots];ds=[(ys[i+1]-ys[i])/(xs[i+1]-xs[i])for i in range(len(xs)-1)];ms=[ds[0]]
 for i in range(1,len(xs)-1):
  if ds[i-1]*ds[i]<=0:ms.append(0)
  else:
   h0=xs[i]-xs[i-1];h1=xs[i+1]-xs[i];w0=2*h1+h0;w1=h1+2*h0;ms.append((w0+w1)/(w0/ds[i-1]+w1/ds[i]))
 ms.append(ds[-1]);i=min(next((i for i in range(len(xs)-1)if t<=xs[i+1]),len(xs)-2),len(xs)-2);h=xs[i+1]-xs[i];u=(t-xs[i])/h
 return(2*u**3-3*u*u+1)*ys[i]+(u**3-2*u*u+u)*h*ms[i]+(-2*u**3+3*u*u)*ys[i+1]+(u**3-u*u)*h*ms[i+1]
def apply():
 o=bpy.data.objects[NAME];world=o.matrix_world.copy();inv=world.inverted();old=[v.co.copy()for v in o.data.vertices];points=[world@v for v in old]
 keys=[(r,k)for r in range(53)for k in range(33)if r<=5 or k<=6 or k>=26 or r>=49];lookup={k:i for i,k in enumerate(keys)};half=len(keys);assert len(old)==2*half==1864 and lookup[(12,1)]==283
 outer=points[:half].copy();sections=[]
 for r in range(15,49):
  t=(r-14)/35
  for side in (-1,1):
   topcol=0 if side<0 else 32;bottomcol=6 if side<0 else 26;start=points[lookup[(14,topcol)]];startbottom=points[lookup[(14,bottomcol)]];end=points[lookup[(49,topcol)]];endbottom=points[lookup[(49,bottomcol)]]
   top=points[lookup[(r,topcol)]];width=abs(top.x);band=curve([(0,abs(start.x-startbottom.x)),(.28,.044),(.52,.033),(.75,.020),(1,abs(end.x-endbottom.x))],t);depth=curve([(0,start.z-startbottom.z),(.28,.045),(.52,.038),(.75,.026),(1,end.z-endbottom.z)],t)
   assert 0<band<width and depth>0
   for k in range(7):
    c=k if side<0 else 32-k;s=k/6
    # Broad bowed blade face descends from actual outer cutting rim into a narrow open-mouth inside edge.
    x=side*(width-band*s+.0025*math.sin(math.pi*s)*math.sin(math.pi*t));z=top.z-depth*s-.0020*math.sin(math.pi*s)*math.sin(math.pi*t)
    outer[lookup[(r,c)]]=Vector((x,top.y,z))
   if r in(20,30,40,48):sections.append({'row':r,'side':side,'topNative':list(outer[lookup[(r,topcol)]]),'lowerInsideNative':list(outer[lookup[(r,bottomcol)]]),'bladeLateralBandM':band,'bladeVerticalDepthM':depth})
 inner=points[half:].copy();stock=[]
 for i,(r,c)in enumerate(keys):
  if not 15<=r<=48:continue
  cp=max(0,c-1)if c<=6 else max(26,c-1);cn=min(6,c+1)if c<=6 else min(32,c+1)
  long=outer[lookup[(r+1,c)]]-outer[lookup[(r-1,c)]];across=outer[lookup[(r,cn)]]-outer[lookup[(r,cp)]];n=long.cross(across).normalized();source=points[half+i]-points[i]
  assert n.length>.9
  if n.dot(source)<0:n=-n
  fade=ease((r-14)/5)*ease((49-r)/5);v=source*(1-fade)+n*.0035*fade;inner[i]=outer[i]+v;stock.append(v.length)
 mesh=bpy.data.meshes.new(NAME+' substantive finite convex side blades');faces=[tuple(p.vertices)for p in o.data.polygons];mesh.from_pydata([inv@v for v in outer+inner],[],faces);mesh.update()
 for mat in o.data.materials:mesh.materials.append(mat)
 for p,source in zip(mesh.polygons,o.data.polygons):p.material_index=source.material_index;p.use_smooth=source.use_smooth
 bm=bmesh.new();bm.from_mesh(mesh);volume=bm.calc_volume(signed=True);closed=sum(not e.is_manifold for e in bm.edges);bm.free();assert closed==0 and volume>0
 protected=[i for i,(r,c)in enumerate(keys)if r<=14 or r>=49];assert all((mesh.vertices[i].co-old[i]).length<1e-7 and(mesh.vertices[i+half].co-old[i+half]).length<1e-7 for i in protected)
 # Restore original bytes on protected receiving stock after world/local conversion.
 for i in protected:mesh.vertices[i].co=old[i];mesh.vertices[i+half].co=old[i+half]
 assert mesh.vertices[283].co==old[283];o.data=mesh;mesh.update()
 o['v38MandibleBlades']='Free rows15..48 rebuilt as substantial convex tapered side blade sections; root/socket283 through14 and distal cap49..52 exact. Open central gape. Authored dimensions, fit/likeness pending.'
 components=[];seen=set();adj={i:set()for i in range(len(mesh.vertices))}
 for e in mesh.edges:a,b=e.vertices;adj[a].add(b);adj[b].add(a)
 for i in adj:
  if i in seen:continue
  todo=[i];seen.add(i);count=0
  while todo:
   q=todo.pop();count+=1
   for j in adj[q]:
    if j not in seen:seen.add(j);todo.append(j)
  components.append(count)
 socket=json.loads(bpy.data.objects['jaw']['makerControlSocketV1']);return {'changedMeshes':[NAME],'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'construction':'One jaw-owned finite shell with newly authored transverse blade sections; upper rim source curve retained, broad convex side face tapers into exact distal cap; central mouth remains genuinely open. No rigid fixed-head bridge.','ownership':{'name':NAME,'parent':o.parent.name,'eras':o.get('exteriorEras'),'class':o.get('constructionClass')},'protected':'Actual paired root rows0..14/socket283 and distal receiving cap rows49..52 byte-exact; upper bill/contact, all hardware/joints/owners/rest/materials/other regions exact.','actualSocket':{'index':283,'local':list(old[283]),'nativeWorld':list(world@old[283]),'metadata':socket},'sectionSamples':sections,'authoredControls':'Lateral bands44/33/20mm and vertical depths45/38/26mm at normalized longitudinal .28/.52/.75, smoothly interpolated to actual boundary stock; no raster metrology.','finiteStock':{'connectedComponentsVertexCounts':components,'nonManifoldEdges':closed,'signedVolumeM3':volume,'freePairedVectorLengthM':[min(stock),max(stock)],'meaning':'Nominal3.5mm normal loft stock blended to exact inherited receiving vectors; length/closed topology not full thickness/clearance certification.'},'limits':['Previous bill-shell/jaw-fit/bill-relationship changes are inherited; this reconstruction broadens actual blade side section, not another axial shortening or marker move.','Actual root/end faces retained; load/fastener or swept fit not established.','Finite screen and actual neutral/jaw-open visual review determine status.']}
