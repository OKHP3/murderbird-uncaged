import bpy,bmesh,math,json,runpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];curve=runpy.run_path(str(R/'scripts/regions/v38-mandible-blades01.py'))['curve']
NAMES=[f'V32 returned upper bill course {i}'for i in range(3)]+['V32 formed mandibular bowl'];COURSES=[(0,.36),(.36,.72),(.72,1)]
# Native world profiles: q, dorsalY/Z, cuttingY/Z, sidehalfwidth. Authored contour proposal.
PROFILE=[(0,-.671200,1.784440,-.616700,1.628,.094),(.08,-.692,1.773,-.635,1.628,.091),(.20,-.735,1.748,-.672,1.628,.081),(.36,-.779,1.710,-.726,1.626,.066),(.52,-.823,1.655,-.754,1.602,.048),(.72,-.842,1.565,-.781,1.543,.029),(.90,-.832,1.485,-.800,1.454,.013),(1,-.806,1.424,-.789,1.417,.006)]
def section(q):return [curve([(p[0],p[j])for p in PROFILE],q)for j in range(1,6)]
def ring(q,t,inner=False):
 y,z,cy,cz,w=section(q);span=math.hypot(cy-y,cz-z);wall=min(.003,.2*span,.3*w);eta=wall/span if inner else 0;w-=wall if inner else 0;k=t*4;i=int(k)%4;u=k-int(k)
 if i==0:v=u;x=w*(.8+.2*math.sin(math.pi*u))
 elif i==1:v=1;x=.8*w*(1-2*u)
 elif i==2:v=1-u;x=-w*(.8+.2*math.sin(math.pi*u))
 else:v=0;x=.8*w*(-1+2*u)
 v=eta+(1-2*eta)*v;return Vector((x,y*(1-v)+cy*v,z*(1-v)+cz*v))
def install(o,world,faces,old,protected):
 inv=o.matrix_world.inverted();m=bpy.data.meshes.new(o.name+' bill-gape coherent rigid stock');m.from_pydata([inv@p for p in world],[],faces);m.update()
 for mat in o.data.materials:m.materials.append(mat)
 for i in protected:m.vertices[i].co=old[i]
 bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),o.name
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 volume=bm.calc_volume(signed=True);assert volume>0;bm.to_mesh(m);bm.free()
 for f in m.polygons:f.use_smooth=True
 o.data=m;o['constructionDescription']='Rigid independent bill/gape contour proposal; actual pivot/root preserved, free hooked upperblade and convex lowerreturn rebuilt. Current shape and interface fit qualified separately.';o['v38BillGape01']='Root-to-tip silhouette reconstruction; true open mouth, original owners/era/materials, no rigid head-jaw bridge or neck/crown change'
 return {'name':o.name,'owner':o.parent.name,'nonmanifoldEdges':0,'signedVolumeM3':volume,'protectedLocalVertexCount':len(protected)}
def contact():
 pts=[(o.name,o.matrix_world@v.co)for o in bpy.data.objects if o.type=='MESH'and o.parent and o.parent.name=='upper-bill'for v in o.data.vertices];return min(pts,key=lambda x:x[1].y)
def apply():
 bpy.context.view_layer.update();oldcontact=contact();records=[]
 for c,(lo,hi)in enumerate(COURSES):
  o=bpy.data.objects[NAMES[c]];old=[v.co.copy()for v in o.data.vertices];half=49*48;assert len(old)==half*2;out=[];inn=[]
  for r in range(49):
   q=lo+(hi-lo)*r/48
   for j in range(48):out.append(ring(q,j/48));inn.append(ring(q,j/48,True))
  protected=[layer*half+r*48+j for layer in[0,1]for r in range(5)for j in range(48)]if c==0 else[]
  records.append(install(o,out+inn,[tuple(f.vertices)for f in o.data.polygons],old,protected))
 o=bpy.data.objects[NAMES[-1]];world=o.matrix_world.copy();old=[v.co.copy()for v in o.data.vertices];v=[world@p for p in old];keys=[(r,k)for r in range(53)for k in range(33)if r<=5 or k<=6 or k>=26 or r>=49];idx={k:i for i,k in enumerate(keys)};half=len(keys);assert len(v)==1864 and idx[(12,1)]==283;out=v[:half].copy();inn=v[half:].copy();start=v[idx[(14,0)]];bottom=v[idx[(14,6)]];width0=abs(start.x);band0=abs(start.x-bottom.x);depth0=start.z-bottom.z
 contours=[(0,start.y,start.z,width0,band0,depth0),(.16,-.658,1.552,.117,.050,.048),(.42,-.706,1.494,.078,.035,.037),(.68,-.743,1.454,.039,.019,.023),(.88,-.757,1.447,.016,.009,.009),(1,-.759,1.464,.009,.005,.003)]
 for i,(r,c)in enumerate(keys):
  if r<=14:continue
  t=(r-14)/38;y,z,w,band,depth=[curve([(p[0],p[j])for p in contours],t)for j in range(1,6)];assert 0<band<w and depth>0
  if c<=6:s=c/6;x=-(w-band*s)
  elif c>=26:s=(32-c)/6;x=w-band*s
  else:s=1;x=(w-band)*(c-16)/10
  x+=(-1 if c<16 else 1)*.0020*math.sin(math.pi*s)*math.sin(math.pi*t);out[i]=Vector((x,y,z-depth*s-.0015*math.sin(math.pi*s)*math.sin(math.pi*t)))
 for i,(r,c)in enumerate(keys):
  if r<=14:continue
  pr=r-1 if(r-1,c)in idx else r;nr=min(52,r+1);pc=max(0,c-1)if(r,c-1)in idx else c;nc=min(32,c+1)if(r,c+1)in idx else c;along=out[idx[(nr,c)]]-out[idx[(pr,c)]];across=out[idx[(r,nc)]]-out[idx[(r,pc)]];n=along.cross(across).normalized();assert n.length>.9,(r,c)
  source=v[half+i]-v[i]
  if n.dot(source)<0:n=-n
  t=(r-14)/5;fade=max(0,min(1,t));fade=fade*fade*(3-2*fade);stock=.0035 if r<49 else .0020;inn[i]=out[i]+source*(1-fade)+n*stock*fade
 protected=[i+layer*half for i,(r,c)in enumerate(keys)if r<=14 for layer in[0,1]];records.append(install(o,out+inn,[tuple(f.vertices)for f in o.data.polygons],old,protected));assert tuple(o.data.vertices[283].co)==tuple(old[283])
 newcontact=contact();marker=bpy.data.objects['bill-contact'];before=list(marker.matrix_world.translation);m=marker.matrix_world.copy();m.translation=newcontact[1];marker.matrix_world=m;bpy.context.view_layer.update()
 return {'status':'Substantive deeper hook/open-gape head contour PROPOSAL; visual/fit/owner acceptance unresolved','changedMeshes':NAMES,'changedNodes':['bill-contact'],'construction':records,'upperNativeProfiles':PROFILE,'jawNativeProfiles':contours,'trueJawSocketIndex283Exact':True,'jawRootRows0to14Exact':True,'upperBillRootRows0to4Exact':True,'contactBeforeNative':before,'contactAfterNative':list(newcontact[1]),'actualLeadingSurface':newcontact[0],'ownership':'Threeupper courses rigid upper-bill, lowerbowl rigidjaw; inheritedpassive all3eras; no cross-joint bridge','limits':['Authored30–60mm contour change, not reference measurement.','Jawfreecap is deliberately reconstructed, no stale claim ofcapexactness.','True root/socket/pivots preserved; sourceinheritance is not completeengineering fit.','Neck/crown/optic/body and cranialroute geometry exact; pendingneckoutline independent.']}
