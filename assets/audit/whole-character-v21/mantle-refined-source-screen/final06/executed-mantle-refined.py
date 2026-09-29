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
SHOULDER=((0,.300,-.018,1.418,.065,.150),(.18,.315,-.010,1.378,.145,.200),
 (.40,.328,.015,1.310,.155,.232),(.65,.350,.070,1.223,.155,.235),
 (.86,.375,.125,1.145,.138,.214),(1,.390,.185,1.078,.122,.190),
 (1.25,.385,.255,.950,.088,.170))
SHIELD=((0,.350,.120,1.172,.118,.210),(.45,.355,.190,1.082,.108,.205),
 (1,.353,.255,.950,.080,.150))
# Short shoulder caps, longer middle coverts and modest trailing tips. Each
# course has an authored footprint and count, not a uniform rectangular grid.
COURSES=((.015,.155,7,-1.48,1.48,.035),(.115,.340,9,-1.40,1.43,.030),
 (.275,.525,10,-1.29,1.40,.025),(.455,.715,10,-1.28,1.43,.020),
 (.645,.875,9,-1.22,1.42,.015),(.825,.995,7,-1.10,1.36,.010))
SHIELD_COURSES=((.025,.400,6,-1.00,1.40,.014),(.300,.710,6,-.92,1.41,.009),
 (.635,.985,5,-.76,1.38,.004))

def ease(x):x=max(0.,min(1.,x));return x*x*(3-2*x)
def sample(table,t):
 t=max(table[0][0],min(table[-1][0],t));index=min(next((i for i in range(len(table)-1) if table[i][0]<=t<=table[i+1][0]),len(table)-2),len(table)-2)
 a,b=table[index],table[index+1];h=b[0]-a[0];u=(t-a[0])/h;result=[]
 for k in range(1,6):
  sec=[(table[j+1][k]-table[j][k])/(table[j+1][0]-table[j][0]) for j in range(len(table)-1)]
  slopes=[sec[0]]
  for j in range(1,len(table)-1):
   if sec[j-1]*sec[j]<=0:slopes.append(0.)
   else:
    ha=table[j][0]-table[j-1][0];hb=table[j+1][0]-table[j][0];w1=2*hb+ha;w2=hb+2*ha
    slopes.append((w1+w2)/(w1/sec[j-1]+w2/sec[j]))
  slopes.append(sec[-1])
  result.append((2*u**3-3*u*u+1)*a[k]+(u**3-2*u*u+u)*h*slopes[index]+(-2*u**3+3*u*u)*b[k]+(u**3-u*u)*h*slopes[index+1])
 return result
def shared_point(side,station,angle):
 x,y,z,rx,ry=sample(SHOULDER,station)
 p=Vector((side*(x+rx*math.cos(angle)),y+ry*math.sin(angle),z-.008*math.sin(angle)*math.sin(math.pi*station)))
 return p
def point(kind,side,t,angle):
 # One coordinated guard section across the two owners; child shield seats
 # outside that section along its actual surface normal, not an unrelated
 # shifted fore/aft ellipse. Receiving construction is shared at the seam.
 station=t if kind=='shoulder' else .81+.43*t
 p=shared_point(side,station,angle)
 if kind=='shield':
  e=.0005;along=shared_point(side,station+e,angle)-shared_point(side,station-e,angle);across=shared_point(side,station,angle+e)-shared_point(side,station,angle-e)
  n=across.cross(along).normalized()
  if n.dot(Vector((side*math.cos(angle),math.sin(angle),.1)))<0:n.negate()
  p+=n*.030
 return p
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
  taper=1 if role=='frame' else (.94-.20*ease(t)) if role=='guard' else ((.85+.15*math.sin(math.pi*min(1,t/.68))) if t<.68 else (.85-(t-.68)/.32*.24))
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

def shoulder_root_bonnet(side,label,material):
 # Finite upper journal bonnet connects the plate cap to its real retained
 # saddle/journal. Open axial ends preserve access to the bearing face.
 owner=label+'-mantle';verts=[];faces=[];rows=12;cols=24
 for j in range(rows+1):
  x=side*(.262+.116*j/rows)
  for k in range(cols+1):
   angle=.12+(math.pi-.24)*k/cols
   verts.append(Vector((x,.059479+.070*math.cos(angle),1.333501+.070*math.sin(angle))))
 for j in range(rows):
  for k in range(cols):i=j*(cols+1)+k;faces.append((i,i+1,i+cols+2,i+cols+1))
 name=f'V21 refined {label} shoulder journal bonnet';obj=bpy.data.objects.new(name,bpy.data.meshes.new(name+' placeholder'));bpy.context.scene.collection.objects.link(obj);obj.parent=bpy.data.objects[owner];obj.matrix_parent_inverse=obj.parent.matrix_world.inverted();install(obj,verts,faces,material)
 expected=Vector((0,0,1));normal=obj.data.polygons[len(obj.data.polygons)//2].normal
 if normal.dot(expected)<0:
  bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
 mod=obj.modifiers.new('Finite open journal bonnet wall','SOLIDIFY');mod.thickness=.003;mod.offset=-1;mod.use_even_offset=False
 obj['region']='shoulder';obj['surfaceRole']='guard';obj['exteriorEras']=ERAS;obj['constructionClass']='proposed-passive';obj['wallM']=.003;obj['authoringRole']='Open upper native-X shoulder journal bonnet seated on retained shoulder saddle; bearing faces remain exposed';obj['geometryStatus']='V21 compact mantle proposal; moving clearance pending'
 return obj

def receive_elbow_journal(obj,side):
 # Subtract the actual journal access/sweep passage from finite skins at its
 # interface. A shared circular receiving edge replaces clamped/folded cages.
 pts=[obj.matrix_world@v.co for v in obj.data.vertices];cy=.042604;cz=1.094982;r=.066
 lo=[min(p[k] for p in pts) for k in range(3)];hi=[max(p[k] for p in pts) for k in range(3)]
 dy=max(lo[1]-cy,0,cy-hi[1]);dz=max(lo[2]-cz,0,cz-hi[2])
 if dy*dy+dz*dz>(r+.006)**2:return False
 bpy.context.view_layer.objects.active=obj;obj.select_set(True)
 for mod in list(obj.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=r,depth=.60,location=(side*.45,cy,cz),rotation=(0,math.pi/2,0))
 cutter=bpy.context.object;data=cutter.data;bpy.context.view_layer.objects.active=obj
 mod=obj.modifiers.new('Finite retained elbow journal receiving passage','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
 bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True);bpy.data.meshes.remove(data);obj.select_set(False)
 obj['jointReceivingPassageRadiusM']=r;obj['jointReceivingPurpose']='actual retained native-X elbow journal/races and moving-owner seam; no hardware removal'
 return True

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
  formed_sheet(backing.name,owner,kind,side,.015,.992,.03,1.45,0,backing.data.materials[0],role='frame',existing=backing,rows=32,cols=24,sweep=.035,crown=0,tip=0);changed.append(backing.name)
  bonnet=shoulder_root_bonnet(side,label,material);added.append({'name':bonnet.name,'owner':owner,'role':'guard','eras':ERAS,'wallM':.003});counts[owner]+=1
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
  obj=formed_sheet(f'V21 refined {label} stout shoulder leading guard',owner,kind,side,.070,.950,-1.34,.205,.039,material,role='guard',rows=28,cols=10,sweep=.045,crown=.002,tip=.008);added.append({'name':obj.name,'owner':owner,'role':'guard','eras':ERAS,'layerM':.039});counts[owner]+=1
  obj=formed_sheet(f'V21 refined {label} curved shoulder sideguard',owner,kind,side,.110,.995,.05,.66,.005,material,role='guard',rows=28,cols=18,sweep=.035,crown=.001,tip=0);added.append({'name':obj.name,'owner':owner,'role':'guard','eras':ERAS,'layerM':.005});counts[owner]+=1
  owner=label+'-wing-shield';kind='shield'
  backing=bpy.data.objects[f'{label} profiled mantle backing v4 {owner}']
  formed_sheet(backing.name,owner,kind,side,.005,.985,.18,1.22,-.006,backing.data.materials[0],role='frame',existing=backing,rows=24,cols=20,sweep=.045,crown=0,tip=0);changed.append(backing.name)
  for course,(start,end,count,a,b,layer) in enumerate(SHIELD_COURSES):
   width=(b-a)/count
   for index in range(count):
    center=a+(index+.5)*width+(.17*width if course%2 else -.08*width)
    obj=formed_sheet(f'V21 refined {label} compact shield course {course+1} plate {index+1}',owner,kind,side,start+.008*math.sin(index+course),end-.018*index/max(1,count-1),center,width*.48,layer,shieldmat,sweep=.10+.025*math.cos(index),tip=.008)
    added.append({'name':obj.name,'owner':owner,'role':'plate','eras':ERAS,'layerM':layer});counts[owner]+=1
  obj=formed_sheet(f'V21 refined {label} elbow leading return',owner,kind,side,.015,.860,-1.08,.16,.019,shieldmat,role='guard',rows=20,cols=10,sweep=.05,crown=.001,tip=.006);added.append({'name':obj.name,'owner':owner,'role':'guard','eras':ERAS,'layerM':.019});counts[owner]+=1
  obj=formed_sheet(f'V21 refined {label} curved elbow sideguard',owner,kind,side,.008,.980,.12,.69,-.001,shieldmat,role='guard',rows=24,cols=18,sweep=.05,crown=.001,tip=0);added.append({'name':obj.name,'owner':owner,'role':'guard','eras':ERAS,'layerM':-.001});counts[owner]+=1
 bpy.context.view_layer.update();receiving=[]
 for obj in bpy.data.objects:
  if obj.type=='MESH' and obj.parent and obj.parent.name in OWNERS and (obj.name in changed or obj.name.startswith('V21 refined')):
   if receive_elbow_journal(obj,1 if obj.parent.name.startswith('left-') else -1):receiving.append(obj.name)
 bpy.context.view_layer.update()
 assert nodes=={o.name:(o.parent.name if o.parent else None,[list(r) for r in o.matrix_world],dict(o.items())) for o in bpy.data.objects if o.type=='EMPTY'}
 for name,snapshot in outside.items():
  obj=bpy.data.objects[name];assert snapshot==([list(r) for r in obj.matrix_world],obj.parent.name if obj.parent else None,tuple(tuple(v.co) for v in obj.data.vertices)),name
 return {'region':'mantle','status':'reference-directed finite construction proposal; no visual/motion/owner acceptance','changed':changed,'stagedOut':removed,'removed':removed,'added':added,'ownerPlateCounts':counts,'plateCountPerWing':counts['left-mantle']+counts['left-wing-shield'],'journalReceivingSurfaces':receiving,'changedPivots':{},'preservedOriginalNodes':len(nodes),'preservedOutsideMeshes':len(outside),'construction':'Remove84obsolete broad skins and84associated root pins; replace four closed backing sacs with broad open compact formed load liners. Short proximal shoulder caps, staggered coverts with rounded wider ends and stout curved sideguards share a continuous authored folded-guard section. Elbow shield starts within the shoulder terminal overlap and continues that section30mm outboard along the actual normal, with native-X finite journal receiving passages around retained hardware. Shoulder upper journal bonnet seats the fan on its saddle while leaving axial bearing faces accessible. Each finite plate attaches to one of four retained rigid owners, never across the moving shoulder/elbow seam. Longitudinal plate rows have5mm radial steps for3mm wall plus rest allowance.','shapeControls':{'sharedShoulderSection':SHOULDER,'shieldLongitudinalMap':[.81,.43],'shieldOutboardNormalSeatM':.030,'shoulderCourses':COURSES,'shieldCourses':SHIELD_COURSES,'journalReceivingRadiusM':.066,'wallM':.003,'radialCourseStepM':.005},'preserved':['all named node hierarchy/world rests/properties','left travel stop and repair restriction','actual shoulder/elbow bearings/races/load members and oblique saddles','all outside four-owner meshes, material definitions and guide curves'],'limits':['Finite owner smoke required; geometry layer spacing is an authored parameter, not a proven whole moving clearance.','Open liner/frame attachment and invisible plate roots are proposed construction.','Neutral clay silhouette must be judged before any selected runtime or engineering claim.']}
