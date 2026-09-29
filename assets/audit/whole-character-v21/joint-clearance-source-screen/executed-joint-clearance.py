"""Proposed native-X cervical receiving sectors and linked intermediate guard.
Loaded envelope03 only. Native metres/Z-up/-Y-front; no render/export/save.
"""
import bpy,bmesh,math
from mathutils import Vector,Matrix
AXIS=Vector((0,-.240,1.455))
ERAS='maker,mechanic,builder'

def ease(t):
 t=max(0.,min(1.,t));return t*t*(3-2*t)
def world_points(o):return [o.matrix_world@v.co for v in o.data.vertices]
def normals(mesh,closed=False):
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if closed and bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(mesh);bm.free()
def replace(o,verts,faces,closed=False):
 inv=o.matrix_world.inverted();mesh=bpy.data.meshes.new(o.name+' V21 receiving construction')
 mesh.from_pydata([inv@Vector(v) for v in verts],[],faces);mesh.update()
 for m in o.data.materials:mesh.materials.append(m)
 normals(mesh,closed);o.data=mesh;o.modifiers.clear()
 for f in mesh.polygons:f.use_smooth=True
 return o
def new_object(name,verts,faces,owner,material,role,closed=False):
 mesh=bpy.data.meshes.new(name+' mesh');mesh.from_pydata(verts,[],faces);mesh.update();mesh.materials.append(material);normals(mesh,closed)
 obj=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(obj);obj.parent=bpy.data.objects[owner];obj.matrix_parent_inverse=obj.parent.matrix_world.inverted()
 obj['region']='neck';obj['surfaceRole']=role;obj['exteriorEras']=ERAS;obj['constructionClass']='proposed-passive';obj['geometryStatus']='V21 discrete articulated joint proposal; no engineering or likeness acceptance'
 for f in mesh.polygons:f.use_smooth=True
 return obj
def sheet(o,normal):
 avg=sum((f.normal for f in o.data.polygons),Vector())
 if avg.dot(normal)<0:
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
 mod=o.modifiers.new('Finite receiving guard wall','SOLIDIFY');mod.thickness=.005;mod.offset=-1;mod.use_even_offset=False
 # Receiving free edges are left square for a measurable finite lap.
 return o
def grid_faces(rows,cols):
 return [(j*(cols+1)+k,j*(cols+1)+k+1,(j+1)*(cols+1)+k+1,(j+1)*(cols+1)+k) for j in range(rows) for k in range(cols)]
def shaft_passage(obj,side):
 # Actual intermediate shaft passage through this finite cheek, not an
 # intersection exemption or an unrelated cosmetic opening.
 bpy.context.view_layer.objects.active=obj;obj.select_set(True)
 bpy.ops.object.modifier_apply(modifier=obj.modifiers[0].name)
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.012,depth=.050,location=(side*.096,AXIS.y,AXIS.z),rotation=(0,math.pi/2,0))
 cutter=bpy.context.object;cutter_mesh=cutter.data
 bpy.context.view_layer.objects.active=obj
 mod=obj.modifiers.new('Intermediate captive shaft clearance bore','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
 bpy.ops.object.modifier_apply(modifier=mod.name)
 bpy.data.objects.remove(cutter,do_unlink=True);bpy.data.meshes.remove(cutter_mesh)
 obj.select_set(False)
 obj['authoringRole']='Linked finite side cheek with real12mm native-X passage around8mm intermediate captive shaft'
def cylinder_eye(name,x,y,z,owner,material,ro=.023,ri=.010,width=.014,existing=None):
 pts=[];faces=[];n=48
 for xx in (x-width/2,x+width/2):
  for r in (ri,ro):
   for k in range(n):a=math.tau*k/n;pts.append((xx,y+r*math.cos(a),z+r*math.sin(a)))
 for k in range(n):
  l=(k+1)%n;faces.extend([(k,l,n+l,n+k),(2*n+k,3*n+k,3*n+l,2*n+l),(k,2*n+k,2*n+l,l),(n+k,n+l,3*n+l,3*n+k)])
 return replace(existing,pts,faces,True) if existing else new_object(name,pts,faces,owner,material,'bearing',True)
def member(o,path,r):
 pts=[];faces=[];n=20;path=[Vector(p) for p in path]
 for j,p in enumerate(path):
  tangent=(path[min(j+1,len(path)-1)]-path[max(0,j-1)]).normalized();a=Vector((1,0,0));a=(a-tangent*a.dot(tangent)).normalized();b=tangent.cross(a)
  for k in range(n):q=math.tau*k/n;pts.append(p+r*(a*math.cos(q)+b*math.sin(q)))
 for j in range(len(path)-1):
  for k in range(n):i=j*n;kk=(k+1)%n;faces.append((i+k,i+kk,i+n+kk,i+n+k))
 faces.extend([tuple(reversed(range(n))),tuple((len(path)-1)*n+k for k in range(n))]);return replace(o,pts,faces,True)
def reshape_guard(o,kind,upper):
 old=world_points(o);assert len(old)==33*25,o.name;pts=[]
 for j in range(33):
  t=j/32
  for k in range(25):
   p=old[j*25+k].copy();u=2*k/24-1
   if kind in ('front','nape'):
    radius=(.145 if kind=='front' else .095)*(1-(.20 if kind=='front' else .15)*u*u)
    terminal=AXIS.z+radius*math.sin(.25 if upper else -.25)
   else:terminal=AXIS.z+(.044 if upper else -.044)+.004*u
   # Restore the away-from-joint edge; remove the mutual terminal skirt.
   boundary=old[32*25+k].z if upper else old[k].z
   p.z+=(terminal-boundary)*(t if upper else 1-t)
   near=1-ease((abs(p.z-AXIS.z)-.125)/.035)
   if kind in ('front','nape'):
    x=.140*math.sin((.78*u) if kind=='front' else (math.pi+.84159*u))
    p.x=p.x*(1-near)+x*near
    dz=p.z-AXIS.z
    if abs(dz)<radius:
     yy=AXIS.y+(-1 if kind=='front' else 1)*math.sqrt(radius*radius-dz*dz)
     p.y=p.y*(1-near)+yy*near
   else:
    side=1 if p.x>0 else -1;angle=(.78+(2.30-.78)*k/24) if side>0 else (-2.30+(2.30-.78)*k/24)
    p.x=p.x*(1-near)+side*.110*near
    # Constant side receiving plane around the hinge; rounded front/rear
    # corners keep the original longitudinal seam relationship.
    cy=-.263;ry=.102
    p.y=p.y*(1-near)+(cy-ry*math.cos(angle))*near
   pts.append(p)
 faces=grid_faces(32,24);replace(o,pts,faces)
 return sheet(o,Vector((0,-1,0)) if kind=='front' else Vector((0,1,0)) if kind=='nape' else Vector((1 if o.name.endswith('1') and not o.name.endswith('-1') else -1,0,0)))
def cover(kind,side,mat):
 rows=32;cols=24;pts=[]
 for j in range(rows+1):
  t=j/rows
  for k in range(cols+1):
   u=2*k/cols-1
   if kind in ('front','nape'):
    radius=(.145 if kind=='front' else .095)*(1-(.20 if kind=='front' else .15)*u*u)-.012
    a=(-.72+1.44*t)*(1-.10*u*u)
    x=.128*math.sin(.78*u if kind=='front' else math.pi+.84159*u)
    p=(x,AXIS.y+(-1 if kind=='front' else 1)*radius*math.cos(a),AXIS.z+radius*math.sin(a))
   else:
    s=k/cols;angle=side*(.78+(2.30-.78)*s)
    phi=(-.72+1.44*t)*(1-.10*u*u)
    # Rounded side cheek joins front/nape cylindrical cover corners, rather
    # than a rectangular side plate projecting through those receivers.
    rz=.104*(1-s)+.06875*s+.020*math.sin(math.pi*s)
    ry=(.104/math.cos(.78))*(1-s)+(.06875/abs(math.cos(2.30)))*s
    p=(side*.098,AXIS.y-ry*math.cos(angle)*math.cos(phi),AXIS.z+rz*math.sin(phi))
   pts.append(p)
 name='V21 linked joint '+kind+(' '+str(side) if side else '')
 obj=new_object(name,pts,grid_faces(rows,cols),'cervical-joint-cover',mat,'plate')
 sheet(obj,Vector((0,-1,0)) if kind=='front' else Vector((0,1,0)) if kind=='nape' else Vector((side,0,0)))
 if kind=='side':shaft_passage(obj,side)
 return obj
def apply():
 original_nodes={o.name:(o.parent.name if o.parent else None,[list(r) for r in o.matrix_world],dict(o.items())) for o in bpy.data.objects if o.type=='EMPTY'}
 assert 'cervical-joint-cover' not in bpy.data.objects
 cover_node=bpy.data.objects.new('cervical-joint-cover',None);bpy.context.scene.collection.objects.link(cover_node);cover_node.parent=bpy.data.objects['neck'];cover_node.matrix_world=Matrix.Translation(AXIS)
 cover_node['linkedMotion']='local nativeX = 0.5 * cervical-upper local nativeX displacement from rest';cover_node['region']='neck';cover_node['exteriorEras']=ERAS
 bpy.context.view_layer.update();changed=[];added=['cervical-joint-cover']
 mapping=[('V21 lower swept throat keel','front',False),('V21 upper swept throat keel','front',True),('V21 lower swept nape return','nape',False),('V21 upper swept nape return','nape',True)]
 for side in (-1,1):mapping.extend([(f'V21 ascending root yoke {side}','side',False),(f'V21 upper cervical directional guard {side}','side',True)])
 for name,kind,upper in mapping:reshape_guard(bpy.data.objects[name],kind,upper);changed.append(name)
 mat=bpy.data.objects['V21 lower swept throat keel'].data.materials[0];bearingmat=bpy.data.objects['V21 intermediate passive journal 1'].data.materials[0]
 for kind,side in (('front',0),('nape',0),('side',-1),('side',1)):added.append(cover(kind,side,mat).name)
 for side in (-1,1):
  name=f'V21 intermediate passive journal {side}';cylinder_eye(name,side*.082,-.240,1.455,'neck',bearingmat,width=.012,existing=bpy.data.objects[name]);changed.append(name)
  added.append(cylinder_eye(f'V21 upper captive intermediate eye {side}',side*.054,-.240,1.455,'cervical-upper',bearingmat).name)
  added.append(cylinder_eye(f'V21 neck captive root eye {side}',side*.052,-.170,1.300,'neck',bearingmat,ro=.022).name)
  name=f'V21 cervical root load bow {side}';member(bpy.data.objects[name],[(side*.052,-.170,1.322),(side*.058,-.203,1.355),(side*.078,-.235,1.407),(side*.082,-.240,1.432)],.009);changed.append(name)
  name=f'V21 cervical upper load bow {side}';member(bpy.data.objects[name],[(side*.054,-.240,1.478),(side*.055,-.255,1.494),(side*.066,-.272,1.538),(side*.072,-.280,1.558)],.009);changed.append(name)
 bpy.context.view_layer.update()
 for name,previous in original_nodes.items():
  obj=bpy.data.objects[name];assert previous==(obj.parent.name if obj.parent else None,[list(r) for r in obj.matrix_world],dict(obj.items())),name
 return {'region':'neck-joint','status':'finite linked joint proposal; discrete posed BVH screen required; no continuous/engineering/likeness acceptance','changed':changed,'added':added,'removed':[],'preservedOriginalNodes':len(original_nodes),'newNode':{'name':'cervical-joint-cover','parent':'neck','worldRestNativeM':list(AXIS),'localMotion':'native X displacement = 0.5 * cervical-upper native X displacement from captured rest','runtimeBrowserAxis':'x','runtimeBrowserSign':'same as cervical-upper X','existingFractions':'neck .35 * pitch, cervical-upper .65 * pitch, head -pitch unchanged'},'construction':'Four separate partial directional cover sectors recessed12mm under opposed finite receiving terminals, not a closed 360-degree cuff. Circular front/nape receiving surfaces are centred on intermediate native-X axis. Side receivers share constant axial seating near hinge. Existing solid bow/shaft endpoint overlaps replaced by bored eyes in separated axial stacks and bows ending at journal outer shoulders. All additions passive Maker/Mechanic/Builder.','parameters':{'wallM':.005,'coverRecessionM':.012,'frontReceiverRadiusM':.145,'napeReceiverRadiusM':.095,'terminalAngleRad':.25,'coverHalfSweepRad':.72,'sideReceiverTerminalHalfZM':.044,'journalBoreRadiusM':.010,'shaftRadiusM':.008},'limits':['Rigid geometry proposed; motion samples and all broader neighborhoods remain unvalidated until evaluated checks.','Cover linked actuator/half-angle coupling is proposed mechanical construction; existing runtime does not yet drive it.']}
