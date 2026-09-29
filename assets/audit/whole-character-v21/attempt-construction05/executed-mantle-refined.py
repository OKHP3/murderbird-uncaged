"""Reference-directed compact layered mantle on the incoming envelope03 scene.
Authored proposal in native metres/Z-up. Four existing rigid owners only.
No rig, material, application, save, render or export edits.
"""
import bpy,bmesh,math
from mathutils import Vector
OWNERS={'left-mantle','right-mantle','left-wing-shield','right-wing-shield'}
ERAS='maker,mechanic,builder'
# Editable construction cage: longitudinal station, centreX, centreY, Z,
# outward section depth and fore/aft section width. This is an OPEN folded
# fan surface, not the old closed ellipsoid, and does not bridge elbow owners.
SHOULDER=((0,.329,-.020,1.413,.040,.070),(.18,.331,-.015,1.382,.105,.170),
 (.40,.333,.020,1.317,.142,.225),(.65,.338,.075,1.245,.148,.223),
 (.86,.350,.130,1.180,.136,.204),(1,.371,.180,1.130,.105,.170))
SHIELD=((0,.370,.200,1.085,.115,.190),(.45,.360,.245,1.033,.095,.160),
 (1,.345,.290,.960,.065,.095))
# Short shoulder caps, longer middle coverts and modest trailing tips. Each
# course has an authored footprint and count, not a uniform rectangular grid.
COURSES=((.015,.155,7,-1.18,1.22,.035),(.115,.340,9,-1.27,1.33,.030),
 (.275,.525,10,-1.29,1.40,.025),(.455,.715,10,-1.28,1.43,.020),
 (.645,.875,9,-1.22,1.42,.015),(.825,.995,7,-1.10,1.36,.010))
SHIELD_COURSES=((.035,.400,6,-.32,1.35,.021),(.300,.710,6,-.30,1.39,.016),
 (.635,.985,5,-.20,1.35,.011))

def ease(x):x=max(0.,min(1.,x));return x*x*(3-2*x)
def sample(table,t):
 t=max(table[0][0],min(table[-1][0],t));index=min(next((i for i in range(len(table)-1) if table[i][0]<=t<=table[i+1][0]),len(table)-2),len(table)-2)
 a,b=table[index],table[index+1];u=(t-a[0])/(b[0]-a[0]);u=ease(u)
 return [a[k]+(b[k]-a[k])*u for k in range(1,6)]
def point(kind,side,t,angle):
 x,y,z,rx,ry=sample(SHOULDER if kind=='shoulder' else SHIELD,t)
 return Vector((side*(x+rx*math.cos(angle)),y+ry*math.sin(angle),z-.008*math.sin(angle)*math.sin(math.pi*t)))
def normal(kind,side,t,angle):
 e=.0005;along=point(kind,side,t+e,angle)-point(kind,side,t-e,angle);across=point(kind,side,t,angle+e)-point(kind,side,t,angle-e)
 n=across.cross(along).normalized()
 if n.dot(Vector((side*math.cos(angle),math.sin(angle),.1)))<0:n.negate()
 return n

def install(obj,verts,faces,material):
 mesh=bpy.data.meshes.new(obj.name+' formed fan mesh');inv=obj.matrix_world.inverted();mesh.from_pydata([inv@v for v in verts],[],faces);mesh.update();mesh.materials.append(material)
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();obj.data=mesh;obj.modifiers.clear()
 for p in mesh.polygons:p.use_smooth=True
 return obj

def formed_sheet(name,owner,kind,side,start,end,center,half,offset,material,role='plate',existing=None,rows=16,cols=10,sweep=.12,crown=.0015,tip=.015):
 verts=[];faces=[];outward=[]
 for j in range(rows+1):
  t=j/rows
  # Broad rounded root shoulder, stout middle, narrow rounded formed free tip.
  # Finite tip width avoids zero-length edges or ornamental needle feathers.
  taper=(.77+.23*math.sin(math.pi*min(1,t/.68))) if t<.68 else (.77-(t-.68)/.32*.43)
  for k in range(cols+1):
   u=2*k/cols-1
   station=max(.0005,min(.9995,start+(end-start)*t+tip*(1-u*u)*ease(t)))
   angle=center+sweep*ease(t)+half*taper*u
   p=point(kind,side,station,angle);n=normal(kind,side,station,angle)
   # Downstream lip stays above the following course by the explicit layer
   # step; only mild forming crown, not a padded dome over an intact blanket.
   verts.append(p+n*(offset+crown*(1-u*u)*math.sin(math.pi*t)));outward.append(n)
 for j in range(rows):
  for k in range(cols):i=j*(cols+1)+k;faces.append((i,i+1,i+cols+2,i+cols+1))
 if existing:obj=existing
 else:
  obj=bpy.data.objects.new(name,bpy.data.meshes.new(name+' construction placeholder'));bpy.context.scene.collection.objects.link(obj);obj.parent=bpy.data.objects[owner];obj.matrix_parent_inverse=obj.parent.matrix_world.inverted()
 install(obj,verts,faces,material)
 # Open sheets need an outward witness; closed-volume orientation is inapplicable.
 p=obj.data.polygons[len(obj.data.polygons)//2]
 nm=obj.matrix_world.to_3x3().inverted().transposed()
 if (nm@p.normal).dot(outward[len(outward)//2])<0:
  bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
 mod=obj.modifiers.new('Finite formed mantle wall','SOLIDIFY');mod.thickness=.003 if role=='plate' else .004;mod.offset=-1;mod.use_even_offset=False
 mod=obj.modifiers.new('Rounded manufactured free edge','BEVEL');mod.width=.00055;mod.segments=2
 obj['region']='shoulder' if kind=='shoulder' else 'wing';obj['surfaceRole']=role;obj['exteriorEras']=ERAS;obj['constructionClass']='proposed-passive';obj['radialLayerM']=offset;obj['wallM']=.003 if role=='plate' else .004;obj['authoringRole']='Directional formed guard on one rigid owner; root attaches behind open liner, not across articulated seam';obj['geometryStatus']='V21 refined folded mantle proposal; visual and motion acceptance pending'
 return obj

def apply():
 nodes={o.name:(o.parent.name if o.parent else None,[list(r) for r in o.matrix_world],dict(o.items())) for o in bpy.data.objects if o.type=='EMPTY'}
 outside={o.name:([list(r) for r in o.matrix_world],o.parent.name if o.parent else None,tuple(tuple(v.co) for v in o.data.vertices)) for o in bpy.data.objects if o.type=='MESH' and (not o.parent or o.parent.name not in OWNERS)}
 material=bpy.data.objects['left shoulder covert 1 3'].data.materials[0];shieldmat=bpy.data.objects['left distal mantle plume 0 3'].data.materials[0]
 removed=[];changed=[];added=[];counts={n:0 for n in OWNERS}
 for obj in list(bpy.data.objects):
  if obj.type!='MESH' or not obj.parent or obj.parent.name not in OWNERS:continue
  skin=(' shoulder covert ' in obj.name or ' distal mantle plume ' in obj.name)
  fastener=obj.name.startswith(('Shoulder covert root pin','Distal mantle root pin'))
  if skin or fastener:
   removed.append({'name':obj.name,'owner':obj.parent.name,'role':obj.get('surfaceRole'),'reason':'obsolete selected skin' if skin else 'obsolete selected skin fixing; removed with its plate, not left floating'})
   bpy.data.objects.remove(obj,do_unlink=True)
 assert len(removed)==168,(len(removed),'expected84skins+84skinfixings')
 for side,label in ((1,'left'),(-1,'right')):
  owner=label+'-mantle';kind='shoulder'
  # Re-form the old giant backing identity as a finite open central load liner.
  # Its old closed shoulder sac is gone; retained saddle/frame/bearings stay exact.
  backing=bpy.data.objects[f'{label} profiled mantle backing v4 {owner}']
  formed_sheet(backing.name,owner,kind,side,.055,.930,.03,1.08,0,backing.data.materials[0],role='frame',existing=backing,rows=32,cols=24,sweep=.08,crown=0,tip=0);changed.append(backing.name)
  for course,(start,end,count,a,b,layer) in enumerate(COURSES):
   width=(b-a)/count
   for index in range(count):
    # Nonuniform, staggered fan roots and swept tip direction are authored
    # within each course; leading tips remain stout, posterior ones shorter.
    center=a+(index+.5)*width+(.20*width if course%2 else -.10*width)
    start_i=start+.009*math.sin(index*1.71+course*.8)
    end_i=end-.020*(index/max(1,count-1))+.012*math.sin(index*1.23+course)
    sweep=.09+.035*math.cos(index*.7+course)
    obj=formed_sheet(f'V21 refined {label} mantle course {course+1} plate {index+1}',owner,kind,side,start_i,end_i,center,width*.48,layer,material,sweep=sweep,tip=.014 if course<4 else .008)
    added.append({'name':obj.name,'owner':owner,'role':'plate','eras':ERAS,'layerM':layer});counts[owner]+=1
  obj=formed_sheet(f'V21 refined {label} stout shoulder leading guard',owner,kind,side,.140,.780,-1.31,.145,.039,material,role='guard',rows=28,cols=10,sweep=.045,crown=.002,tip=.010);added.append({'name':obj.name,'owner':owner,'role':'guard','eras':ERAS,'layerM':.039});counts[owner]+=1
  owner=label+'-wing-shield';kind='shield'
  backing=bpy.data.objects[f'{label} profiled mantle backing v4 {owner}']
  formed_sheet(backing.name,owner,kind,side,.04,.91,.50,.83,0,backing.data.materials[0],role='frame',existing=backing,rows=24,cols=20,sweep=.10,crown=0,tip=0);changed.append(backing.name)
  for course,(start,end,count,a,b,layer) in enumerate(SHIELD_COURSES):
   width=(b-a)/count
   for index in range(count):
    center=a+(index+.5)*width+(.17*width if course%2 else -.08*width)
    obj=formed_sheet(f'V21 refined {label} compact shield course {course+1} plate {index+1}',owner,kind,side,start+.008*math.sin(index+course),end-.018*index/max(1,count-1),center,width*.48,layer,shieldmat,sweep=.10+.025*math.cos(index),tip=.008)
    added.append({'name':obj.name,'owner':owner,'role':'plate','eras':ERAS,'layerM':layer});counts[owner]+=1
  obj=formed_sheet(f'V21 refined {label} elbow leading return',owner,kind,side,.070,.775,-.355,.11,.026,shieldmat,role='guard',rows=20,cols=10,sweep=.05,crown=.001,tip=.006);added.append({'name':obj.name,'owner':owner,'role':'guard','eras':ERAS,'layerM':.026});counts[owner]+=1
 bpy.context.view_layer.update()
 assert nodes=={o.name:(o.parent.name if o.parent else None,[list(r) for r in o.matrix_world],dict(o.items())) for o in bpy.data.objects if o.type=='EMPTY'}
 for name,snapshot in outside.items():
  obj=bpy.data.objects[name];assert snapshot==([list(r) for r in obj.matrix_world],obj.parent.name if obj.parent else None,tuple(tuple(v.co) for v in obj.data.vertices)),name
 return {'region':'mantle','status':'reference-directed finite construction proposal; no visual/motion/owner acceptance','changed':changed,'stagedOut':removed,'removed':removed,'added':added,'ownerPlateCounts':counts,'plateCountPerWing':counts['left-mantle']+counts['left-wing-shield'],'changedPivots':{},'preservedOriginalNodes':len(nodes),'preservedOutsideMeshes':len(outside),'construction':'Remove84obsolete broad skins and84associated root pins; replace the four closed backing sacs with open compact formed load liners. New short proximal shoulder caps, staggered varied tapered coverts and stout leading guards sit on a new authored folded-fan cage. Shorter trailing shield courses keep the elbow journal/load frame exposed. Each finite plate attaches to one of four retained rigid owners, never across the moving shoulder/elbow seam. Longitudinal rows have5mm radial steps for3mm wall plus rest allowance; lateral edges intentionally leave fitted seams rather than coplanar overlaps.','shapeControls':{'shoulder':SHOULDER,'shield':SHIELD,'shoulderCourses':COURSES,'shieldCourses':SHIELD_COURSES,'wallM':.003,'radialCourseStepM':.005},'preserved':['all named node hierarchy/world rests/properties','left travel stop and repair restriction','actual shoulder/elbow bearings/races/load members and oblique saddles','all outside four-owner meshes, material definitions and guide curves'],'limits':['Finite owner smoke required; geometry layer spacing is an authored parameter, not a proven whole moving clearance.','Open liner/frame attachment and invisible plate roots are proposed construction.','Neutral clay silhouette must be judged before any selected runtime or engineering claim.']}
