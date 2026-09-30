"""V38 body-study02: one repair of preserved study01 on exact V37. No pivot/finish change."""
import bpy, bmesh, math
from mathutils import Vector, Matrix

ERAS='maker,mechanic,builder'
TORSO_ALLOWLIST=(
 ['V30 continuous tapered breast liner','V30 continuous dorsal pelvic liner','V23 lower sternal return']
 +[f'V34 formed breast course {row} plate {col}' for row,count in ((4,6),(5,5),(6,4)) for col in range(1,count+1)]
 +[f'V35 oblique thoracic side guard {side} {row}' for side in (-1,1) for row in (2,3,4)])
THIGH_ALLOWLIST=[f'V25 {label} thigh {kind} {side}' for label in ('left','right') for kind in ('primary load member','rear return member') for side in (-1,1)]
ALLOWLIST=tuple(TORSO_ALLOWLIST+THIGH_ALLOWLIST)

def smooth(t):
 t=max(0,min(1,t));return t*t*(3-2*t)

def mesh(name,verts,faces,owner,mat,role):
 data=bpy.data.meshes.new(name+' mesh');data.from_pydata(verts,[],faces);data.update()
 bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
 data.materials.append(mat);obj=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(obj)
 parent=bpy.data.objects[owner];obj.parent=parent;obj.matrix_parent_inverse.identity();obj.matrix_basis.identity()
 inv=parent.matrix_world.inverted()
 for v in data.vertices:v.co=inv@v.co
 obj['region']='lower-body-mass';obj['surfaceRole']=role;obj['exteriorEras']=ERAS
 obj['constructionClass']='proposed-passive';obj['geometryStatus']='V38 body-study02 rigid formed stock; likeness and engineering acceptance pending'
 return obj

def shell(name,stations,a0,a1,owner,mat,role,wall=.007,segments=24):
 # Closed finite-wall strip with explicit segmented formed sections, not tissue.
 verts=[];faces=[];n=segments+1;count=len(stations)*n
 for layer in (0,1):
  for z,rx,front,back in stations:
   for j in range(n):
    angle=a0+(a1-a0)*j/segments;c=math.cos(angle)
    x=(rx-layer*wall)*math.sin(angle)
    y=(front+layer*wall if c>=0 else back-layer*wall)*abs(c)
    verts.append((x,y,z))
 for k in range(len(stations)-1):
  for j in range(segments):
   i=k*n+j;faces.extend([(i,i+1,i+n+1,i+n),(count+i+n,count+i+n+1,count+i+1,count+i)])
  for j in (0,segments):
   i=k*n+j;faces.append((i,i+n,count+i+n,count+i))
 for k in (0,len(stations)-1):
  for j in range(segments):
   i=k*n+j;faces.append((i,count+i,count+i+1,i+1))
 return mesh(name,verts,faces,owner,mat,role)

def guards(label,side,outer,mat):
 # Three tapered, discrete longitudinal C-stock segments around each paired
 # load channel. Open anterior service faces prevent a continuous bowl/cup.
 result=[]
 for segment,(top,bottom) in enumerate(((.634,.589),(.586,.536),(.533,.486)),1):
  verts=[];faces=[]
  for z in (top,(top+bottom)/2,bottom):
   t=max(0,min(1,(.634-z)/.148));shape=.78+.22*math.sin(math.pi*t)
   center=side*((.323 if outer else .185)+(.021 if outer else .025)*t)
   cy=-.013-.042*t;wx=(.048 if outer else .036)*shape;depth=.059*shape;wall=.010
   # U stock opens toward -Y/front; a finite rear web carries two flange lips.
   cross=[(-wx,-depth),(wx,-depth),(wx,depth),(-wx,depth),
          (-wx,depth-wall),(wx-wall,depth-wall),(wx-wall,-depth+wall),
          (-wx+wall,-depth+wall),(-wx+wall,depth-wall)]
   # Simple non-self-intersecting U-section boundary, clockwise around stock.
   cross=[(-wx,-depth),(-wx,depth),(wx,depth),(wx,-depth),
          (wx-wall,-depth),(wx-wall,depth-wall),(-wx+wall,depth-wall),(-wx+wall,-depth)]
   for x,y in cross:verts.append((center+x,cy+y,z))
  n=8
  for row in range(2):
   for j in range(n):
    i=row*n+j;k=row*n+(j+1)%n;faces.append((i,k,k+n,i+n))
  faces.extend([tuple(reversed(range(n))),tuple(range(2*n,3*n))])
  result.append(mesh(f'V38 {label} thigh {"outer" if outer else "inner"} formed load channel {segment}',
                     verts,faces,label+'-thigh',mat,'plate'))
 return result

def evaluated_points(obj):
 ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());data=ev.to_mesh()
 points=[ev.matrix_world@v.co for v in data.vertices];ev.to_mesh_clear();return points

def receiving_cut(body_objects,label,angles):
 # Actual direct thigh-owner solids at authored sample rotations, expanded by
 # 4mm. A convex receiving tool is conservative for these samples, not a sweep.
 thigh=bpy.data.objects[label+'-thigh'];rest=thigh.matrix_world.copy()
 source=[o for o in bpy.data.objects if o.type=='MESH' and o.parent==thigh]
 points=[]
 for angle in angles:
  transform=rest@Matrix.Rotation(angle,4,'X')@rest.inverted()
  for obj in source:points.extend(transform@p for p in evaluated_points(obj))
 bm=bmesh.new()
 for p in points:bm.verts.new(p)
 bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
 unused=[v for v in bm.verts if not v.link_faces]
 if unused:bmesh.ops.delete(bm,geom=unused,context='VERTS')
 center=sum((v.co for v in bm.verts),Vector())/len(bm.verts)
 for v in bm.verts:
  delta=v.co-center
  if delta.length:v.co+=delta.normalized()*.004
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 data=bpy.data.meshes.new('temporary sampled actual-thigh receiving stock');bm.to_mesh(data);bm.free()
 tool=bpy.data.objects.new(data.name,data);bpy.context.scene.collection.objects.link(tool)
 bpy.context.view_layer.update()
 for obj in body_objects:
  mod=obj.modifiers.new('V38 sampled actual thigh receiving clearance','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool
  with bpy.context.temp_override(object=obj,active_object=obj,selected_objects=[obj],selected_editable_objects=[obj]):bpy.ops.object.modifier_apply(modifier=mod.name)
  if not len(obj.data.polygons):raise ValueError('Receiving tool consumed rigid stock: '+obj.name)
 bpy.data.objects.remove(tool,do_unlink=True);bpy.data.meshes.remove(data)
 return {'joint':label+'-thigh','sourceMeshes':[o.name for o in source],'rotationXSamplesRad':angles,'expansionProposalM':.004,'receivingMeshes':[o.name for o in body_objects],'method':'Convex actual direct-owner solid samples, expanded radially; finite cut into added body stock and changed existing dorsal liner only','limits':'No continuous sweep, strict triangle collision screen, structural load or engineering claim'}

def apply():
 for name in ALLOWLIST:
  obj=bpy.data.objects.get(name)
  if obj is None or obj.type!='MESH' or obj.parent.name not in ('body','breastplate','left-thigh','right-thigh'):
   raise ValueError('Allowlisted source/owner missing: '+name)
  # Prevent another object's mesh datablock from inheriting a sculpt.
  obj.data=obj.data.copy()
 for name in TORSO_ALLOWLIST:
  obj=bpy.data.objects[name];world=obj.matrix_world.copy();inv=world.inverted()
  for vertex in obj.data.vertices:
   p=world@vertex.co;weight=smooth((1.070-p.z)/.260)
   # Fuller lower abdomen, with upper thorax unchanged and a low keel rather
   # than a cylindrical barrel. Existing plate segmentation remains legible.
   p.x*=1+.40*weight
   p.y=-.09+(p.y+.09)*(1+.10*weight)
   p.z-=.030*weight*smooth((.880-p.z)/.160)
   vertex.co=inv@p
  obj.data.update()
 for name in THIGH_ALLOWLIST:
  obj=bpy.data.objects[name];world=obj.matrix_world.copy();inv=world.inverted();side=1 if 'left' in name else -1
  points=[world@v.co for v in obj.data.vertices]
  cx=sum(p.x for p in points)/len(points);cy=sum(p.y for p in points)/len(points)
  lo=min(p.z for p in points);hi=max(p.z for p in points)
  for vertex,p in zip(obj.data.vertices,points):
   t=max(0,min(1,(p.z-lo)/(hi-lo)));weight=math.sin(math.pi*t)**2
   p.x=cx+(p.x-cx)*(1+.55*weight)+side*.012*weight
   p.y=cy+(p.y-cy)*(1+.65*weight)
   vertex.co=inv@p
  obj.data.update()
 skin=bpy.data.objects['V30 continuous dorsal pelvic liner'].data.materials[0]
 frame=bpy.data.objects['V25 left thigh primary load member -1'].data.materials[0]
 added=[]
 # Central rigid underbody and outboard shoulders of the pelvis are formed
 # together, then receive the actual retained rotating thigh stock.
 stations=[(.790,.229,-.259,.218),(.746,.221,-.251,.216),(.691,.169,-.219,.175),(.620,.105,-.142,.103)]
 for index,(a,b) in enumerate(((-1.30,-.43),(-.40,.40),(.43,1.30),(1.33,2.22),(2.25,3.14),(3.17,4.06),(4.09,4.95))):
  added.append(shell(f'V38 tapered pelvic return course {index+1}',stations,a,b,'body',skin,'plate'))
 for label,side in (('left',1),('right',-1)):
  added += guards(label,side,True,skin)+guards(label,side,False,skin)
  # Fixed formed side rail receives the shell loads above the retained hip.
  poly=[(side*.14,-.02,.805),(side*.25,.015,.816),(side*.256,.056,.790),(side*.14,.060,.760)]
  verts=[(x,y-.014,z) for x,y,z in poly]+[(x,y+.014,z) for x,y,z in poly]
  faces=[(0,1,2,3),(7,6,5,4)]+[(j,(j+1)%4,(j+1)%4+4,j+4) for j in range(4)]
  added.append(mesh(f'V38 {label} fixed pelvic formed load web',verts,faces,'body',frame,'frame'))
 bpy.context.view_layer.update()
 receivers=[o for o in added if o.parent.name=='body']+[bpy.data.objects['V30 continuous dorsal pelvic liner']]
 cuts=[receiving_cut(receivers,label,[-.45,-.30,-.15,0,.15,.30,.45]) for label in ('left','right')]
 bpy.context.view_layer.update()
 return {'changedMeshes':list(ALLOWLIST),'addedMeshes':[o.name for o in added],'removedMeshes':[],
 'construction':'Broadened lower segmented torso, finite formed tapered pelvic courses and fixed load webs; heavier paired thigh channels and separately thigh-owned open segmented C-stock; V28 supports and hip/knee journals exact.',
 'attachments':[{'name':o.name,'owner':o.parent.name,'role':o.get('surfaceRole'),'eras':o.get('exteriorEras')} for o in added],
 'receivingCuts':cuts,'limits':['Authored construction and proportion proposal; references are appearance guidance, not dimensions.','Body and thigh pieces remain separate rigid owners. Sampled receiving cuts do not prove full joint clearance.']}
