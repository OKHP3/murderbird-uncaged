"""Independent hanging rigid shields; authored proportions are proposals."""
import bpy,bmesh,math,sys
SECOND='--attempt02' in sys.argv
from mathutils import Vector
from mathutils.bvhtree import BVHTree
COUNTS=[5,6,7,6,5,4]
OLD=[f'V34 formed breast course {r} plate {c}'for r,n in enumerate(COUNTS,1)for c in range(1,n+1)]
LINER='V30 continuous tapered breast liner'
def apply():
 bpy.context.view_layer.update();liner=bpy.data.objects[LINER];liner.data.calc_loop_triangles();tree=BVHTree.FromPolygons([liner.matrix_world@v.co for v in liner.data.vertices],[tuple(t.vertices)for t in liner.data.loop_triangles],all_triangles=True)
 template=bpy.data.objects[OLD[0]];added=[];records=[]
 def skin(z,a):
  axis=Vector((math.sin(a),-math.cos(a),0));hit=tree.ray_cast(Vector((0,-.08,z))+axis*.9,-axis,1.2)
  assert hit[0] is not None,(z,a)
  return hit[0],axis
 # Each entry has its own centreline sweep/width/section, not a shared tile grid.
 specs=[]
 for k,(a,z,L,w,sweep)in enumerate([(-.76,1.239,.220,.103,.13),(-.37,1.246,.239,.128,.08),(.05,1.248,.225,.125,-.04),(.45,1.235,.225,.117,-.12),(.80,1.222,.219,.091,-.15)]):specs.append(('upper hanging '+str(k+1),a,z,L,w,sweep,'upper',.022))
 for k,(a,z,L,w,sweep)in enumerate([(-.87,1.100,.174,.095,.12),(-.55,1.078,.164,.114,.10),(-.18,1.088,.181,.118,.09),(.20,1.074,.163,.121,-.09),(.57,1.065,.168,.105,-.12),(.89,1.062,.167,.083,-.13)]):specs.append(('oblique middle '+str(k+1),a,z,L,w,sweep,'middle',.021))
 for k,(a,z,L,w,sweep)in enumerate([(-.83,.951,.161,.086,.13),(-.48,.934,.158,.105,.13),(-.08,.939,.169,.108,.08),(.34,.918,.149,.119,-.13),(.74,.932,.159,.092,-.12)]):specs.append(('belly access '+str(k+1),a,z,L,w,sweep,'lower',.017))
 for k,(a,z,L,w,sweep)in enumerate([(-.63,.804,.101,.083,.17),(-.18,.801,.111,.097,.14),(.30,.788,.098,.097,-.12),(.70,.802,.105,.072,-.14)]):specs.append(('pelvic transition '+str(k+1),a,z,L,w,sweep,'pelvic',.014))
 for side in [-1,1]:
  specs.append(('narrow flank '+str(side),side*.94,1.176,.230,.058,-side*.10,'flank',.017))
 for index,(label,a,top,length,width,sweep,kind,lift)in enumerate(specs):
  if SECOND:
   # Explicit final shape correction: own swept course, varied convex face and tapered free end.
   width*=.90 if kind=='upper' else .96
   sweep*=1.85 if kind in ('upper','middle','lower') else 1.25
   length*=1+[-.025,.015,-.01,.02,-.018][index%5]
  rows=28 if SECOND else 22;cols=16 if SECOND else 12;outer=[];inner=[];roots=[]
  for i in range(rows+1):
   u=i/rows;z=top-length*u;ang=a+sweep*u;center,n=skin(z,ang);t=Vector((math.cos(ang),math.sin(ang),0));root=.36 if kind=='upper'else .64
   # Narrow roots, broad face, rounded/tapered finite ends; region-specific profile.
   knots=[(0,root),(.18,.86),(.38,1),(.72,.96),(.86,.77),(1,.16 if kind=='upper'else .34)]
   for (x,y),(xx,yy)in zip(knots,knots[1:]):
    if x<=u<=xx:tlocal=(u-x)/(xx-x);blend=(.5-.5*math.cos(math.pi*tlocal))if SECOND else tlocal;factor=y+(yy-y)*blend;break
   half=width*factor/2;offset=.0038+lift*(math.sin(math.pi*u/2)**1.3);R=.17+(.045*(index%4));roll=(index%3-1)*.09
   if SECOND:
    offset+=.0045*math.sin(math.pi*u)**2
    R=.15+.035*(index%4)
    roll=(index%3-1)*.035
   for j in range(cols+1):
    v=(j/cols-.5)*2;cross=v*half;camber=R-math.sqrt(max(.001,R*R-cross*cross));tipturn=.003*max(0,(u-.89)/.11)
    if SECOND:
     # Asymmetric downward-and-across tip; broad convex metal face, compact finite edge.
     cross+=.008*math.sin(math.pi*u)*(1 if index%2 else -1)
     tipturn=.002*(max(0,(u-.90)/.10)**2)
    p=center+t*cross+n*(offset-camber+roll*cross-tipturn)
    # Corresponding inner stock along the per-section normal, deterministic indices.
    nn=(n+t*(cross/math.sqrt(max(.001,R*R-cross*cross))-roll)).normalized();outer.append(p);inner.append(p-nn*.0038)
    if i==0:roots.append({'outerNative':list(p),'innerNative':list(inner[-1]),'nominalLinerGapM':offset-.0038})
  N=len(outer);f=[]
  for i in range(rows):
   for j in range(cols):
    k=i*(cols+1)+j;b=k+1;c=b+cols+1;d=k+cols+1;f.extend([(k,b,c,d),(N+d,N+c,N+b,N+k)])
  edge=list(range(cols+1))+[i*(cols+1)+cols for i in range(1,rows+1)]+[rows*(cols+1)+j for j in range(cols-1,-1,-1)]+[i*(cols+1)for i in range(rows-1,0,-1)]
  f.extend((x,N+x,N+y,y)for x,y in zip(edge,edge[1:]+edge[:1]));name='V38 hanging breast shield '+label;o=template.copy();o.name=name;bpy.context.scene.collection.objects.link(o);bpy.context.view_layer.update();m=bpy.data.meshes.new(name+' formed stock');inv=o.matrix_world.inverted();m.from_pydata([inv@p for p in outer+inner],[],f);m.update()
  for mat in template.data.materials:m.materials.append(mat)
  bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));vol=bm.calc_volume(signed=True)
  if vol<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces));vol=bm.calc_volume(signed=True)
  bad=sum(not e.is_manifold for e in bm.edges);bm.to_mesh(m);bm.free();o.data=m
  for k,poly in enumerate(m.polygons):poly.use_smooth=SECOND and k<rows*cols*2
  if SECOND:m.set_sharp_from_angle(angle=.55)
  for key in list(o.keys()):
   if key not in ['region','surfaceRole','exteriorEras','constructionClass','constructionOwner','articulatesAcrossJoint','proposal']:del o[key]
  o['constructionDescription']='Independent rigid hanging shield, region-specific swept centreline, own cambered cross-section and rolled face; narrow source-liner root, finite3.8mm wall, stepped freeedge. Reconstruction proposal; finite seating/overlap/motion unproven.';o['hangingBreastRevision']='hanging-breast01-attempt02' if SECOND else 'hanging-breast01';o['wallM']=.0038;added.append(name)
  records.append({'name':name,'parent':o.parent.name,'exteriorEras':o.get('exteriorEras'),'kind':kind,'topNativeZM':top,'lengthM':length,'widthM':width,'sweepRadians':sweep,'freeReliefM':lift,'transverseRadiusM':R,'attempt':2 if SECOND else 1,'broadFaceSmoothNormals':SECOND,'wallM':.0038,'rootSectionEndpoints':[roots[0],roots[-1]],'nonManifoldEdges':bad,'signedVolumeM3':vol,'qualification':'Root nominal section matches actual liner centreline, not finite full-area seat proof. Closed stock does not prove self/lap clearance.'})
 for name in OLD:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
 return {'status':'Hanging-breast01 final directional/convex plate proposal; acceptance pending' if SECOND else 'First hanging-breast01 visual proposal; acceptance pending','changedMeshes':[],'addedMeshes':added,'removedMeshes':OLD,'changedNodes':[],'construction':records,'referenceAuthority':'Actual Master03 SHA538c51bcdbf5bfce95a0932fdbbb0f5868b446f4985346d15e6cacd32430e633; exact plate dimensions inferred, not raster measurements.','mechanism':'22 independently formed hanging shields:5longupper,6obliquemiddle,5loweraccess,4pelvic,2narrowflank. Final mode gives stronger individual diagonal sweep, asymmetric staggered taper, C1 width transitions, own convex camber and restrained face roll; broad face smooth normals/hard finite edges. Same breastplate opening owner, no new joint bridge.' if SECOND else '22 independently formed hanging shields with individual transverse camber and face roll, stepped free edges; same breastplate owner.','protected':'Actual liner/frame, head/neck/wings/legs, all surviving geometry/transforms/materials and era eligibility exact. Local armor relief changes exterior within supporting body direction.','limits':['Visual proposal only; no owner likeness approval.','No self/finite lap/motion/strength certification from closed boundaries.','Narrow source-liner root correspondence is sampled; finite receiving area not yet proved.','No new UV/textures/material finishing/app/runtime/publication.']}
