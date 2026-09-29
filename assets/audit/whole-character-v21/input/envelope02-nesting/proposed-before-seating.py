"""V21 shared neck/upper-breast S-envelope and coarse passive construction.
Authorial rest-shape study in native metres/Z-up/-Y-front, not an engineering model.
"""
import bpy,bmesh,math,json
from mathutils import Vector,Matrix
PROFILE=((.80,-.175,.130,.205),(.88,-.235,.160,.240),(1.00,-.370,.150,.285),(1.16,-.445,.120,.285),
 (1.30,-.420,.050,.255),(1.40,-.385,-.095,.170),(1.48,-.360,-.155,.120),
 (1.56,-.385,-.175,.105),(1.63,-.400,-.170,.110))
PIVOTS={'neck':(0,-.170,1.300),'cervical-upper':(0,-.240,1.455),'head':(0,-.280,1.580)}
ERAS='maker,mechanic,builder'

def ease(t):t=max(0.,min(1.,t));return t*t*(3-2*t)
def sample(z,k):
 x=[r[0] for r in PROFILE];y=[r[k] for r in PROFILE]
 if z<=x[0]:return y[0]
 if z>=x[-1]:return y[-1]
 h=[b-a for a,b in zip(x,x[1:])];d=[(b-a)/hh for a,b,hh in zip(y,y[1:],h)];m=[d[0]]
 for i in range(1,len(x)-1):
  if d[i-1]*d[i]<=0:m.append(0.)
  else:
   w1=2*h[i]+h[i-1];w2=h[i]+2*h[i-1];m.append((w1+w2)/(w1/d[i-1]+w2/d[i]))
 m.append(d[-1])
 for i in range(len(x)-1):
  if x[i]<=z<=x[i+1]:
   t=(z-x[i])/h[i];return (2*t**3-3*t*t+1)*y[i]+(t**3-2*t*t+t)*h[i]*m[i]+(-2*t**3+3*t*t)*y[i+1]+(t**3-t*t)*h[i]*m[i+1]

def envelope_point(z,angle,off=0):
 front,rear,w=[sample(z,k) for k in (1,2,3)];cy=(front+rear)/2;ry=(rear-front)/2
 return Vector(((w+off)*math.sin(angle),cy-(ry+off)*math.cos(angle),z))

def mesh_object(name,verts,faces,owner,mat,role,construction):
 mesh=bpy.data.meshes.new(name+' mesh');mesh.from_pydata(verts,[],faces);mesh.update();mesh.materials.append(mat)
 obj=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(obj);obj.parent=bpy.data.objects[owner];obj.matrix_parent_inverse=obj.parent.matrix_world.inverted()
 obj['region']='neck' if owner in ('neck','cervical-upper','head') else 'breast';obj['surfaceRole']=role;obj['exteriorEras']=ERAS;obj['constructionClass']='proposed-passive';obj['authoringRole']=construction;obj['geometryStatus']='V21 coarse shared-envelope visual study; no engineering or likeness acceptance'
 return obj

def guard(name,top,bottom,center,half,owner,mat,off=.003,sweep=0,wall=.005):
 rows=32;cols=24;verts=[];faces=[]
 for j in range(rows+1):
  t=j/rows
  for k in range(cols+1):
   u=2*k/cols-1
   # Long directional guards have formed rounded free edges, not horizontal rings.
   z=top+(bottom-top)*t-.014*(1-u*u)**2*ease(t)-.015*math.sin(center)*u*ease(t)
   width=half*(1.00-.05*ease(t))
   angle=center+sweep*ease(t)+width*u
   verts.append(tuple(envelope_point(z,angle,off)))
 for j in range(rows):
  for k in range(cols):
   i=j*(cols+1)+k;faces.append((i,i+cols+1,i+cols+2,i+1))
 obj=mesh_object(name,verts,faces,owner,mat,'plate','Directional finite guard sampled from ONE shared breast/throat/nape envelope; free lower edge and rigid single-owner mounting')
 bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
 normal=obj.data.polygons[(rows//2)*cols+cols//2].normal
 if normal.dot(Vector((math.sin(center),-math.cos(center),0)))<0:
  bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
 for p in obj.data.polygons:p.use_smooth=True
 mod=obj.modifiers.new('Finite coarse formed wall','SOLIDIFY');mod.thickness=wall;mod.offset=-1;mod.use_even_offset=True
 mod=obj.modifiers.new('Formed guard free edge','BEVEL');mod.width=.0007;mod.segments=2
 return obj

def tube(name,path,r,owner,mat,role='frame'):
 pts=[Vector(p) for p in path];verts=[];faces=[];n=16
 for j,p in enumerate(pts):
  tangent=(pts[min(j+1,len(pts)-1)]-pts[max(0,j-1)]).normalized();a=Vector((1,0,0))
  if abs(a.dot(tangent))>.95:a=Vector((0,1,0))
  a=(a-tangent*a.dot(tangent)).normalized();b=tangent.cross(a).normalized()
  for k in range(n):ang=2*math.pi*k/n;verts.append(tuple(p+r*(a*math.cos(ang)+b*math.sin(ang))))
 for j in range(len(pts)-1):
  for k in range(n):l=(k+1)%n;i=j*n;faces.append((i+k,i+l,i+n+l,i+n+k))
 faces.extend([tuple(reversed(range(n))),tuple((len(pts)-1)*n+k for k in range(n))])
 obj=mesh_object(name,verts,faces,owner,mat,role,'Finite passive curved load member; endpoint ownership follows retained named rigid articulation')
 bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(obj.data);bm.free()
 for p in obj.data.polygons:p.use_smooth=True
 return obj

def bearing(name,x,y,z,ro,ri,owner,mat,thick=.018):
 verts=[];faces=[];n=32
 for xx in (x-thick/2,x+thick/2):
  for r in (ri,ro):
   for k in range(n):a=2*math.pi*k/n;verts.append((xx,y+r*math.cos(a),z+r*math.sin(a)))
 for k in range(n):
  l=(k+1)%n;faces.extend([(k,l,n+l,n+k),(2*n+k,3*n+k,3*n+l,2*n+l),(k,2*n+k,2*n+l,l),(n+k,n+l,3*n+l,3*n+k)])
 obj=mesh_object(name,verts,faces,owner,mat,'bearing','Passive native-X annular journal with actual captive shaft passage; no invented sensor')
 bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(obj.data);bm.free();return obj

def apply():
 skinmat=bpy.data.objects['V17 breast directional lamina 1 1 left'].data.materials[0];frame=bpy.data.objects['Curved thoracic load rail'].data.materials[0];bmat=bpy.data.objects['Cervical intermediate axle -1'].data.materials[0]
 oldworld={o.name:o.matrix_world.copy() for o in bpy.data.objects};oldnodes={o.name:{'parent':o.parent.name if o.parent else None,'world':[list(r) for r in o.matrix_world],'local':[list(r) for r in o.matrix_local]} for o in bpy.data.objects if o.type=='EMPTY'}
 staged=[]
 for o in list(bpy.data.objects):
  if o.type=='MESH' and o.parent and (o.parent.name in ('neck','cervical-upper','breastplate') or (o.parent.name=='body' and o.get('region')=='breast')):
   staged.append({'name':o.name,'owner':o.parent.name,'region':o.get('region'),'role':o.get('surfaceRole'),'eras':o.get('exteriorEras')});bpy.data.objects.remove(o,do_unlink=True)
 assert len(staged)==171
 # New centres fit the shared contour; restore every other object's world rest deliberately.
 for name in ('neck','cervical-upper','head'):
  m=oldworld[name].copy();m.translation=Vector(PIVOTS[name]);bpy.data.objects[name].matrix_world=m;bpy.context.view_layer.update()
  # Stop inherited children from following a pivot edit at rest. Apply later pivot edits separately.
  for o in list(bpy.data.objects[name].children):
   if o.name not in PIVOTS or o.name=='head':o.matrix_world=oldworld[o.name]
 # The head pivot itself must retain its new centre; child geometry stays at exact old world rest.
 m=oldworld['head'].copy();m.translation=Vector(PIVOTS['head']);bpy.data.objects['head'].matrix_world=m;bpy.context.view_layer.update()
 for o in bpy.data.objects:
  if o.name not in PIVOTS and o.name in oldworld:o.matrix_world=oldworld[o.name]
 bpy.context.view_layer.update();added=[]
 def add(o):added.append({'name':o.name,'owner':o.parent.name,'region':o.get('region'),'role':o.get('surfaceRole'),'eras':o.get('exteriorEras')});return o
 # Front opening cover: long keels run breastward, independent of the cervical moving guards.
 add(guard('V21 breast central opening keel',1.395,.890,0,.46,'breastplate',skinmat,off=.012))
 for side in (-1,1):
  add(guard('V21 anterior breast guard '+str(side),1.360,.900,side*.72,.44,'breastplate',skinmat,off=0,sweep=side*.04))
  add(guard('V21 fixed shoulder breast return '+str(side),1.340,.895,side*1.58,.82,'body',skinmat,off=-.012,sweep=side*.04))
  add(guard('V21 ascending root yoke '+str(side),1.490,1.255,side*1.50,.83,'neck',skinmat,off=-.018,sweep=side*.03))
  add(guard('V21 upper cervical directional guard '+str(side),1.640,1.445,side*1.50,.83,'cervical-upper',skinmat,off=0,sweep=side*.03))
 add(guard('V21 lower swept throat keel',1.490,1.315,0,.79,'neck',skinmat,off=-.009))
 add(guard('V21 upper swept throat keel',1.635,1.450,0,.79,'cervical-upper',skinmat,off=.009))
 add(guard('V21 lower swept nape return',1.480,1.270,math.pi,.99,'neck',skinmat,off=-.009))
 add(guard('V21 upper swept nape return',1.650,1.440,math.pi,.99,'cervical-upper',skinmat,off=.009))
 # Fixed lower torso seats behind the free opening-cover edges; it is not a
 # moving armor bridge across the access seam or a monolithic throat backing.
 add(guard('V21 fixed lower sternal pan',.945,.800,0,1.42,'body',skinmat,off=-.026,wall=.005))
 # Coarse frame shares the contour and seats articulated journals at the new centres.
 for side in (-1,1):
  x=side*.065
  # Body-fixed root journal and clevis branches seat the articulated neck into
  # both torso spines and shoulder load links, rather than leaving a floating bow.
  add(bearing('V21 body fixed cervical root journal '+str(side),side*.078,-.170,1.300,.023,.010,'body',bmat))
  root_seat=(side*.078,-.170,1.277)
  add(tube('V21 neck root breast support bridge '+str(side),[root_seat,(side*.135,-.230,1.280),tuple(envelope_point(1.315,side*.92,-.040))],.012,'body',frame))
  add(tube('V21 neck root shoulder support bridge '+str(side),[root_seat,(side*.130,-.115,1.290),(side*.170,-.080,1.310)],.012,'body',frame))
  add(tube('V21 cervical root load bow '+str(side),[(x,-.170,1.300),(x,-.205,1.350),(x,-.235,1.410),(x,-.240,1.455)],.014,'neck',frame))
  add(tube('V21 cervical upper load bow '+str(side),[(x,-.240,1.455),(x,-.255,1.490),(x,-.272,1.545),(x,-.280,1.580)],.012,'cervical-upper',frame))
  add(bearing('V21 intermediate passive journal '+str(side),side*.078,-.240,1.455,.023,.010,'neck',bmat))
  add(bearing('V21 head passive journal '+str(side),side*.072,-.280,1.580,.022,.010,'cervical-upper',bmat))
  add(tube('V21 breast internal curved spine '+str(side),[tuple(envelope_point(z,side*.92,-.040)) for z in (.940,1.040,1.160,1.260,1.315)],.014,'body',frame))
  # Fixed wing rests are not moved; a passive saddle link connects the new breast root to them.
  mantle=oldworld['left-mantle' if side>0 else 'right-mantle'].translation
  add(tube('V21 shoulder root load link '+str(side),[(side*.17,-.08,1.310),(side*.245,-.015,1.310),tuple(mantle)],.015,'body',frame))
 add(tube('V21 lower torso support crossbow',[tuple(envelope_point(.925,a,-.045)) for a in (-1.12,-.60,0,.60,1.12)],.012,'body',frame))
 # Captive pins attach at one articulation owner each; no guard is fixed to two owners.
 add(tube('V21 neck root captive shaft',[(-.096,-.170,1.300),(.096,-.170,1.300)],.008,'neck',bmat,'bearing'))
 add(tube('V21 intermediate captive shaft',[(-.096,-.240,1.455),(.096,-.240,1.455)],.008,'cervical-upper',bmat,'bearing'))
 add(tube('V21 head captive shaft',[(-.090,-.280,1.580),(.090,-.280,1.580)],.008,'head',bmat,'bearing'))
 hinge=oldworld['breastplate'].translation;y,z=hinge.y,hinge.z
 for side in (-1,1):
  add(bearing('V21 fixed breast door bearing '+str(side),side*.16,y,z,.020,.009,'body',bmat))
  add(tube('V21 breast door bearing support '+str(side),[(side*.16,y+.024,z),(side*.185,-.035,.930)],.011,'body',frame))
  end=envelope_point(.965,side*.47,-.010)
  add(tube('V21 moving breast door root return '+str(side),[(side*.12,y,z),tuple(end)],.009,'breastplate',frame))
 add(tube('V21 moving captive breast door shaft',[(-.180,y,z),(.180,y,z)],.006,'breastplate',bmat,'bearing'))
 nesting={'neckLowerFlankM':-.018,'neckLowerFrontNapeM':-.009,'neckUpperFlankM':0,'neckUpperFrontNapeM':.009,'breastCentreM':.012,'breastAnteriorM':0,'breastFixedSideM':-.012,'lowerFixedPanM':-.026,'wallM':.005,'status':'authored rest nesting; sampled evaluated bands required before clearance claim'}
 bpy.data.objects['body']['sharedEnvelopeV21']=json.dumps({'profile':PROFILE,'pivots':PIVOTS,'nesting':nesting,'status':'coarse visual study; retained V20 mechanism sockets stale under new rests'},separators=(',',':'))
 bpy.context.view_layer.update()
 contract={n:{'parent':r['parent'],'oldWorld':r['world'],'oldLocal':r['local'],'newWorld':[list(x) for x in bpy.data.objects[n].matrix_world],'newLocal':[list(x) for x in bpy.data.objects[n].matrix_local]} for n,r in oldnodes.items()}
 return {'status':'V21 shared-envelope coarse visual study; no runtime, likeness or engineering acceptance','profile':PROFILE,'interpolation':'shape-preserving cubic Hermite; one continuous breast/throat/nape surface','nesting':nesting,'stagedOut':staged,'added':added,'changedPivots':PIVOTS,'rigContract':contract,'construction':'Breast fullness lies below the rearward throat tuck; the nape sweeps into shoulder. Long directional passive finite guards and coarse load bows share the same envelope. Layered radial offsets nest finite walls at neck and longitudinal breast seams; widths taper only5percent to retain overlap. A fixed lower sternal pan and support crossbow seat behind the opening-cover free edges, continuing the lower torso taper. The body-fixed root journals have two support branches into breast spines and shoulder load links, with a neck-owned captive shaft. Lower/upper rigid guards underlap at the intermediate hinge and do not attach across two owners. Opening breast keels retain native-X basal hinge, two finite annular support bearings, captive shaft and finite root returns. All new coarse parts are passive in all three eras.','preserved':['all source copies and binaries','52rigid names/parents','source head world geometry','legs, feet, wings and retained posterior torso meshes','material definitions and historical guides'], 'limits':['Rest-silhouette construction only; joint underlaps, door opening and mechanism sockets require fresh checks after the visual gate.','Retained V20 mechanismLayoutV1 local socket metadata is not validated under3new rests and must be derived anew before runtime selection.','Proposed supports and unseen surfaces are authorial construction, not historical evidence.']}
