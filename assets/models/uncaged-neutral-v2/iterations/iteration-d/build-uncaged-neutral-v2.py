"""Neutral correction study v2. Rigid, region-owned mechanical geometry.

Authoring conventions are metres, X anatomical left, -Y forward, Z up.
Art is perspective evidence, not a dimensioned drawing. No finished surfaces.
The historical source supplies only compatible assembly pivots and internals.
"""
from pathlib import Path
import bpy, bmesh, math, json, hashlib, ast
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/models/uncaged-neutral-v2';OUT.mkdir(parents=True,exist_ok=True)
BASE=ROOT/'assets/models/uncaged-structure-v1/murderbird-structure-v1.blend'
BASE_SHA='9859c1044fe035f140448b23cef477eb9fb3cc4daa8aaf42837ebb8d7dba7541'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(BASE)==BASE_SHA
receipt=OUT/'neutral-inventory.json'
if receipt.exists():
 for f in json.loads(receipt.read_text()).get('generatedFiles',[]):
  p=ROOT/f['path']
  assert not p.exists() or sha(p)==f['sha256'],f'Manual output changed. Preserve a new version first: {p}'
bpy.ops.wm.open_mainfile(filepath=str(BASE))
for o in bpy.data.objects:o.animation_data_clear()
for a in list(bpy.data.actions):bpy.data.actions.remove(a)
def under(o,p):
 while o.parent:
  o=o.parent
  if o==p:return True
 return False
for o in list(bpy.data.objects):
 if o.type=='MESH' and not any(under(o,bpy.data.objects[n]) for n in ['processing','power-core']):bpy.data.objects.remove(o,do_unlink=True)
helpers={'material','group','mesh','bevel','rod','ring','tube'}
source=ast.parse((ROOT/'scripts/build-uncaged-presence-study.py').read_text())
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in helpers],type_ignores=[]),'<preserved-primitives>','exec'))
mat={k:material('Neutral / '+k,col,metal,rough) for k,col,metal,rough in [
 ('plate',(.42,.435,.445),.12,.65),('edge',(.32,.34,.355),.25,.58),('frame',(.19,.21,.225),.25,.61),
 ('recess',(.037,.045,.05),.08,.8),('bearing',(.27,.285,.295),.35,.5),('repair',(.31,.32,.33),.15,.72),
 ('optic',(.23,.12,.034),.20,.48),('inner',(.25,.26,.27),.1,.75)]}
ALL='maker,mechanic,builder'
region='back';era=ALL;role='plate'
parts=[]
# A shorter upper/lower leg convention restores body-to-leg proportions.
# Foot/ground pivots remain at their original world coordinates.
for label in ['left','right']:
 bpy.data.objects[label+'-thigh'].location.z-=.08
 bpy.data.objects[label+'-shin'].location.z+=.04
 bpy.data.objects[label+'-foot'].location.z+=.04
bpy.context.view_layer.update()
def tag(o,parent,reg,rl='plate',eras=ALL):
 o['region']=reg;o['surfaceRole']=rl;o['exteriorEras']=eras;o['constructionClass']='inherited-passive' if eras==ALL else 'later-repair' if eras=='mechanic,builder' else 'advanced-system'
 o['proposal']=True
 parts.append({'name':o.name,'parent':parent.name,'region':reg,'role':rl,'eras':eras.split(','),'class':o['constructionClass']})
 return o
def wm(name,vertices,faces,parent,reg,rl='plate',eras=ALL,bevel_width=0):
 inv=parent.matrix_world.inverted()
 o=mesh(name,[inv@Vector(p) for p in vertices],faces,mat[rl],parent)
 tag(o,parent,reg,rl,eras)
 if bevel_width:bevel(o,bevel_width)
 return o
def wr(name,a,b,r,parent,reg,rl='frame',eras=ALL,end=None,sides=12):
 inv=parent.matrix_world.inverted();o=rod(name,a,b,r,mat[rl],None,sides,end)
 for v in o.data.vertices:v.co=inv@v.co
 o.parent=parent
 return tag(o,parent,reg,rl,eras)
def wt(name,points,radii,parent,reg,rl='frame',eras=ALL,sides=12):
 inv=parent.matrix_world.inverted();o=tube(name,points,radii,mat[rl],None,sides)
 for v in o.data.vertices:v.co=inv@v.co
 o.parent=parent
 return tag(o,parent,reg,rl,eras)
def world_group(name,p,parent):
 g=group(name,parent);g.location=parent.matrix_world.inverted()@Vector(p);bpy.context.view_layer.update();return g
def mix(a,b,t):return tuple(a[i]+(b[i]-a[i])*t for i in range(len(a)))
def sample(sections,z):
 for a,b in zip(sections,sections[1:]):
  if a[0]<=z<=b[0]:return mix(a[1:],b[1:],(z-a[0])/(b[0]-a[0]))
 return sections[0][1:] if z<sections[0][0] else sections[-1][1:]
def envelope(sections,z,a,offset=0):
 cy,rx,ry=sample(sections,z)
 return Vector((math.sin(a)*(rx+offset),cy-math.cos(a)*(ry+offset),z))
def patch(name,outline,project,parent,reg,rl='plate',thickness=.006,eras=ALL,sub=3):
 # Radial tessellation follows curved support, not an n-gon chord through it.
 outline=[mix(a,b,k/5) for a,b in zip(outline,outline[1:]+outline[:1]) for k in range(5)]
 centre=tuple(sum(p[i] for p in outline)/len(outline) for i in range(2));verts=[];faces=[];edge=[]
 sub=7
 verts.append(project(*centre))
 for level in range(1,sub+1):
  f=level/sub
  for p in outline:verts.append(project(*mix(centre,p,f)))
 n=len(outline)
 for j in range(n):faces.append((0,1+j,1+(j+1)%n))
 for level in range(sub-1):
  aa=1+level*n;bb=aa+n
  for j in range(n):faces.append((aa+j,bb+j,bb+(j+1)%n,aa+(j+1)%n))
 o=wm(name,verts,faces,parent,reg,rl,eras)
 solid=o.modifiers.new('Rigid wall / inner face','SOLIDIFY');solid.thickness=thickness;solid.offset=-1
 bevel(o,.0012)
 for p in o.data.polygons:p.use_smooth=True
 return o
def shell(name,sections,parent,reg,start=-math.pi,end=math.pi,rl='frame',offset=0):
 verts=[];faces=[];n=48
 for z,*_ in sections:
  for i in range(n+1):verts.append(envelope(sections,z,start+(end-start)*i/n,offset))
 for j in range(len(sections)-1):
  for i in range(n):k=j*(n+1)+i;faces.append((k,k+1,k+n+2,k+n+1))
 o=wm(name,verts,faces,parent,reg,rl)
 for p in o.data.polygons:p.use_smooth=True
 m=o.modifiers.new('Inner shell thickness','SOLIDIFY');m.thickness=.006
 return o
def fastener(name,p,n,parent,reg,r=.0035,eras=ALL):
 p=Vector(p);n=Vector(n).normalized();return wr(name,p-n*.002,p+n*.003,r,parent,reg,'bearing',eras,sides=10)
body=bpy.data.objects['body'];breast=bpy.data.objects['breastplate'];neck=bpy.data.objects['neck'];head=bpy.data.objects['head'];crown=bpy.data.objects['cranial-cover'];jaw=bpy.data.objects['jaw'];bill=bpy.data.objects['upper-bill']
# F01: shaped breast with a low taper and narrowed upper transition, continuous
# with a separately moving curved cervical envelope. No spherical barrel.
body_sections=[(.76,.09,.11,.13),(.84,.075,.18,.20),(.96,.045,.255,.265),(1.10,.005,.305,.305),(1.24,-.04,.325,.305),(1.36,-.09,.282,.255),(1.45,-.125,.22,.205)]
shell('Breast inner access shell',body_sections,breast,'breast',-1.44,1.44,'inner')
shell('Short dorsal shell',body_sections,body,'back',1.42,math.tau-1.42,'frame')
# Lower-down overlapping laid courses, each individual plate has a variable
# pointed end and crowned face; no broad circumferential breast bands.
for row in range(8):
 ztop=1.445-row*.081;length=.135 if row<5 else .118
 count=5 if row<6 else 4
 width=2.94/count
 for col in range(count):
  a=-1.44+width*(col+.5)+(0.035 if row%2 else -.035)
  z=ztop+.01*math.sin(col*1.8+row)
  outline=[(a-width*.50,z),(a+width*.50,z+.004),(a+width*.49,z-length*.56),(a+width*.29,z-length*.88),(a+.035,z-length),(a-width*.40,z-length*.77),(a-width*.49,z-length*.36)]
  outline=[(aa,max(.763,zz)) for aa,zz in outline]
  project=lambda aa,zz:envelope(body_sections,zz,aa,.028-.022*(zz-(z-length))/length)
  patch(f'Breast course {row+1} panel {col+1}',outline,project,breast,'breast')
  for aa in [a-width*.31,a+width*.31]:fastener('Breast peened anchor',project(aa,z-.021),(math.sin(aa),-math.cos(aa),.12),breast,'breast')
# Rear construction is a reconstruction; short overlapping panels, no tail.
for row in range(5):
 z=1.43-row*.12
 for col in range(5):
  a=1.49+(col+.5)*(math.tau-2.98)/5;w=.68
  patch(f'Dorsal lap {row} {col}',[(a-w/2,z),(a+w/2,z),(a+w*.40,z-.13),(a,z-.18),(a-w*.45,z-.14)],lambda aa,zz:envelope(body_sections,max(.765,zz),aa,.009),body,'back')
# Passive frame follows the exterior and supports actual joints/access.
for s in [-1,1]:
 wt('Curved thoracic load rail',[(s*.13,.11,.79),(s*.24,.12,.98),(s*.26,.06,1.21),(s*.20,-.04,1.40),(s*.11,-.1,1.46)],[.024,.029,.027,.024,.019],body,'breast')
for z in [.91,1.06,1.22,1.35]:
 ps=[envelope(body_sections,z,-1.45+math.tau*i/40,-.026) for i in range(41)]
 wt('Passive rib behind access cover',ps,[.011]*len(ps),body,'breast')
# Neck: bowed front and broad rear frame, intermediate guard courses each
# carried by the neck assembly; skull-side collar overlaps without bridging.
neck_sections=[(1.33,-.095,.215,.213),(1.405,-.12,.192,.202),(1.49,-.20,.163,.183),(1.58,-.255,.141,.166),(1.665,-.275,.129,.150),(1.75,-.235,.139,.155),(1.81,-.215,.135,.153)]
shell('Cervical articulated inner guards',neck_sections,neck,'neck',-.98,.98,'frame')
for row in range(6):
 z=1.806-row*.075
 for col in range(7):
  a=(col-3)*.55
  outline=[(a-.33,z),(a+.31,z-.002),(a+.30,z-.068),(a+.12,z-.117),(a-.27,z-.092)]
  patch(f'Cervical overlapping guard {row} {col}',outline,lambda aa,zz:envelope(neck_sections,zz,aa,.007+.019*(z-zz)/.117),neck,'neck')
  fastener('Neck guard pin',envelope(neck_sections,z-.020,a,.014),(math.sin(a),-math.cos(a),0),neck,'neck',.003)
for s in [-1,1]:
 wt('Bowed passive cervical fork',[(s*.095,-.08,1.35),(s*.105,-.085,1.47),(s*.085,-.10,1.59),(s*.075,-.13,1.73),(s*.065,-.24,1.80)],[.019,.02,.022,.021,.022],neck,'neck')
 for z in [1.43,1.52,1.61,1.70]:
  y=sample(neck_sections,z)[0]+sample(neck_sections,z)[2]*.72
  wr('Cervical transverse pin',(s*.07,y,z),(s*.128,y,z),.025,neck,'neck','bearing',sides=20)
# F02: actual convex hooked bill and swept layered crown.
head_sections=[(1.70,-.09,.018,.035),(1.765,-.13,.09,.15),(1.84,-.19,.147,.225),(1.94,-.225,.160,.22),(2.025,-.23,.14,.192),(2.072,-.19,.105,.16),(2.106,-.13,.025,.07)]
shell('Cranial inner canopy',head_sections,crown,'head',1.78,math.tau-1.78,'recess')
# Four swept ridge courses close the crown apex, with a stepped rear sweep.
for course in range(4):
 y0=-.40+course*.105;y1=y0+.135
 def ridge(x,y):
  z=2.04+.072*math.sin((y+.40)/.46*math.pi)-.12*x*x
  return (x,y,z)
 patch('Crown swept ridge '+str(course),[(-.078,y0),(.078,y0),(.062,y1-.018),(0,y1),(-.062,y1-.018)],ridge,crown,'head',thickness=.006)
# Crown plate overlap is directed backwards and down, with a swept silhouette.
for row in range(5):
 z=2.084-row*.058
 for col in range(9):
  a=-math.pi+(col+.5)*math.tau/9;w=.78
  if row>1 and abs(a)<.80:continue
  drift=(.14 if a>0 else -.14)
  outline=[(a-w*.5,z),(a+w*.5,z+.003),(a+w*.42+drift,z-.048),(a+drift,z-.111),(a-w*.44+drift,z-.078)]
  def crown_project(aa,zz):
   v=envelope(head_sections,max(1.707,zz),aa,.009+.019*(z-zz)/.111)
   ey=Vector((v.y+.334,v.z-1.938));distance=ey.length
   if distance<.082 and abs(v.x)>.09:
    ey.normalize();v.y=-.334+ey.x*.082;v.z=1.938+ey.y*.082
   return v
  patch(f'Swept crown lamina {row} {col}',outline,crown_project,crown,'head',thickness=.005)
  fastener('Crown lap pin',envelope(head_sections,z-.019,a,.016),(math.sin(a),-math.cos(a),.25),crown,'head',.003)
# Broad ridge plates from the cere over the crown; scalloped eye aperture below.
for s in [-1,1]:
 def side_project(y,z):
  cy,rx,ry=sample(head_sections,z);q=(y-cy)/max(.03,ry)
  return (s*(rx*math.sqrt(max(.14,1-q*q))+.016),y,z)
 brow=[(-.438,1.980),(-.395,2.040),(-.27,2.091),(-.14,2.102),(-.026,2.071),(-.145,2.042),(-.265,2.015),(-.358,1.955)]
 patch('Cere to swept brow plate '+str(s),brow,side_project,crown,'head',thickness=.01)
 eye=Vector((s*.148,-.334,1.938));radius=.055
 verts=[];faces=[];n=48
 for layer in range(2):
  for i in range(n):
   t=i*math.tau/n;r=(.081+.008*math.cos(t*3)) if layer==0 else .060
   verts.append((s*.154,eye.y+r*math.cos(t),eye.z+r*math.sin(t)))
 for i in range(n):faces.append((i,(i+1)%n,n+(i+1)%n,n+i))
 o=wm('Fitted polygonal optic surround '+str(s),verts,faces,head,'head','plate');m=o.modifiers.new('Optic surround wall','SOLIDIFY');m.thickness=.009
 # A recessed circular housing is integrated into a broad irregular cheek
 # plate; cylinder cap sits behind both nested lips, not on top like a button.
 wr('Dark passive optic well',(s*.121,eye.y,eye.z),(s*.130,eye.y,eye.z),radius,head,'optic','recess',sides=40)
 for r,x0,x1 in [(.067,.146,.160),(.057,.154,.163),(.046,.142,.147)]:
  verts=[];faces=[];n=48
  for x,rr in [(x0,r),(x1,r),(x1,r-.007),(x0,r-.007)]:
   for i in range(n):t=i*math.tau/n;verts.append((s*x,eye.y+rr*math.cos(t),eye.z+rr*math.sin(t)))
  for layer in range(4):
   for i in range(n):faces.append((layer*n+i,layer*n+(i+1)%n,((layer+1)%4)*n+(i+1)%n,((layer+1)%4)*n+i))
  wm('Recessed optic machined lip',verts,faces,head,'optic','bearing')
 # Upper and lower cheek rail protect the socket and frame the real aperture.
 cheek=[(-.295,1.907),(-.345,1.875),(-.421,1.872),(-.457,1.885),(-.448,1.842),(-.376,1.828),(-.298,1.859),(-.268,1.892)]
 patch('Constructed cheek socket surround '+str(s),cheek,lambda y,z:(s*(.142 if y>-.37 else .118),y,z),head,'head',thickness=.014)
 for y,z in [(-.295,1.887),(-.353,1.853),(-.420,1.854)]:fastener('Cheek access bolt',(s*.149,y,z),(s,0,0),head,'head',.004)
 wr('Jaw hinge journal',(s*.10,-.275,1.812),(s*.148,-.275,1.812),.032,head,'head','bearing',sides=24)
 wr('Advanced seated optic',(s*.143,eye.y,eye.z),(s*.147,eye.y,eye.z),.034,bpy.data.objects['builder-optics'],'optic','optic','builder',sides=40)
# Catmull interpolation through deliberate profile landmarks gives thickness
# and a hooked cutting end; section gaps form actual plate divisions.
bill_sections=[(-.412,1.998,1.871,.088),(-.479,1.982,1.848,.100),(-.551,1.947,1.805,.092),(-.615,1.885,1.753,.073),(-.650,1.807,1.693,.049),(-.644,1.714,1.641,.024),(-.592,1.615,1.615,.0008)]
def curve(points,t):
 x=t*(len(points)-1);i=min(len(points)-2,int(x));u=x-i
 p0=points[max(0,i-1)];p1=points[i];p2=points[i+1];p3=points[min(len(points)-1,i+2)]
 return tuple(.5*((2*p1[k])+(-p0[k]+p2[k])*u+(2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*u*u+(-p0[k]+3*p1[k]-3*p2[k]+p3[k])*u**3) for k in range(len(p1)))
# A constructed bill uses an explicit curved side outline, thick at its
# root and tapering into the hook. This avoids the circular nozzle impression
# of a chain of elliptical cones. Both sides and its cutting edge are closed.
from mathutils.geometry import tessellate_polygon
profile=[(-.403,1.993),(-.473,1.985),(-.548,1.949),(-.610,1.891),(-.650,1.820),(-.661,1.746),(-.646,1.676),(-.603,1.616),(-.622,1.691),(-.592,1.750),(-.537,1.795),(-.470,1.828),(-.403,1.846)]
outline=[]
for i in range(len(profile)):
 p0=profile[(i-1)%len(profile)];p1=profile[i];p2=profile[(i+1)%len(profile)];p3=profile[(i+2)%len(profile)]
 for j in range(5):
  t=j/5
  outline.append(tuple(.5*(2*p1[k]+(-p0[k]+p2[k])*t+(2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*t*t+(-p0[k]+3*p1[k]-3*p2[k]+p3[k])*t*t*t) for k in range(2)))
def bill_width(y,z):return max(.0015,(.102-.21*max(0,-y-.44))*min(1,max(.015,(z-1.615)/.16)))
verts=[];faces=[];n=len(outline)
for side in [-1,1]:
 for y,z in outline:verts.append((side*bill_width(y,z),y,z))
tri=tessellate_polygon([[Vector((y,z,0)) for y,z in outline]])
lookup={(round(y,6),round(z,6)):i for i,(y,z) in enumerate(outline)}
for t in tri:
 ids=tuple(v if isinstance(v,int) else lookup[(round(v.x,6),round(v.y,6))] for v in t)
 faces.append(tuple(reversed(ids)));faces.append(tuple(n+i for i in ids))
for i in range(n):faces.append((i,(i+1)%n,n+(i+1)%n,n+i))
wm('Constructed convex hook with hard cutting edge',verts,faces,bill,'head','plate',bevel_width=.003)
# Separate root-side cheek plates overlap the blade, leaving a genuine edge.
for side in [-1,1]:
 shape=[(-.407,1.976),(-.472,1.969),(-.526,1.944),(-.512,1.891),(-.462,1.856),(-.407,1.864)]
 patch('Bill root forged side plate '+str(side),shape,lambda y,z:(side*(bill_width(y,z)+.006),y,z),bill,'head',thickness=.006)
 for y,z in [(-.433,1.961),(-.484,1.927)]:fastener('Bill root fixing',(side*(bill_width(y,z)+.009),y,z),(side,0,0),bill,'head',.004)
# Curved lower mandible fork converges beneath the upper cutting profile;
# enclosed thickness is geometry and the central cheek opening stays empty.
for s in [-1,1]:
 path=[(s*.116,-.279,1.813),(s*.12,-.337,1.781),(s*.101,-.418,1.744),(s*.068,-.48,1.69),(s*.032,-.538,1.683),(s*.008,-.572,1.694)]
 wt('Curved mandible lower fork',path,[.011,.013,.013,.011,.008,.002],jaw,'head','edge',sides=14)
 outline=[(-.285,1.823),(-.353,1.791),(-.415,1.762),(-.47,1.710),(-.539,1.691),(-.485,1.660),(-.420,1.685),(-.350,1.714),(-.282,1.765)]
 patch('Mandible side blade '+str(s),outline,lambda y,z:(s*max(.012,.119-(max(0,-y-.34))*.44),y,z),jaw,'head',thickness=.009)
# A contact marker lies on a visible bill vertex (foremost section); runtime
# uses the actual triangle surface for a selected rail, not this point alone.
verts=[o.matrix_world@v.co for o in bpy.data.objects if o.type=='MESH' and under(o,bill) for v in o.data.vertices]
p=min(verts,key=lambda v:v.y);contact=bpy.data.objects['bill-contact'];contact.parent=bill;contact.matrix_parent_inverse=Matrix.Identity(4);contact.location=bill.matrix_world.inverted()@p;contact.scale=(1,1,1)
# F03: broad compact mantle wrapping the shoulder/elbow chain. Its outer
# ellipsoidal cap is divided between the two rigid owners at the elbow.
wing_sections=[(.86,.27,.035,.025),(.96,.235,.105,.18),(1.09,.155,.165,.27),(1.23,.08,.19,.29),(1.38,.035,.172,.235),(1.48,.03,.12,.17),(1.525,.035,.024,.055)]
def wing_point(s,a,z,lift=0):
 cy,rx,ry=sample(wing_sections,z)
 return (s*(.315+math.cos(a)*(rx+lift)),cy+math.sin(a)*(ry+lift),z)
for s,label in [(1,'left'),(-1,'right')]:
 upper=bpy.data.objects[label+'-mantle'];lower=bpy.data.objects[label+'-wing-shield']
 for top,bottom,parent in [(1.522,1.135,upper),(1.19,.868,lower)]:
  verts=[];faces=[];rows=14;n=28
  for j in range(rows+1):
   z=top+(bottom-top)*j/rows
   for k in range(n+1):verts.append(wing_point(s,-math.pi+math.tau*k/n,z,-.007 if parent==lower else 0))
  for j in range(rows):
   for k in range(n):i=j*(n+1)+k;faces.append((i,i+1,i+n+2,i+n+1))
  o=wm(label+' mantle fitted backing '+parent.name,verts,faces,parent,'shoulder' if parent==upper else 'wing','frame');solid=o.modifiers.new('Guard inner surface','SOLIDIFY');solid.thickness=.005
  for p in o.data.polygons:p.use_smooth=True
 for row in range(9):
  z=1.504-row*.066;length=.12 if row<4 else .15
  parent=upper if row<5 else lower;reg='shoulder' if row<5 else 'wing'
  for col in range(7):
   a=-1.36+(col+.5)*2.72/7+(.06 if row%2 else 0);w=.43
   if z-length<.87 and abs(a)>.92:continue
   outline=[(a-w*.5,z),(a+w*.5,z),(a+w*.48,z-length*.5),(a+w*.22,z-length*.87),(a-.06,z-length),(a-w*.44,z-length*.62)]
   patch(label+f' folded mantle lamina {row} {col}',outline,lambda aa,zz:wing_point(s,aa,max(.861,zz),.036-.026*(zz-z+length)/length),parent,reg,thickness=.005)
   if row<7:fastener('Mantle root rivet',wing_point(s,a,z-.018,.014),(s,0,.15),parent,reg,.0032)
 # Shoulder saddle seals the top of the formed guard around its load joint.
 patch(label+' shoulder saddle',[(-1.5,1.475),(1.5,1.475),(1.55,1.525),(0,1.537),(-1.55,1.525)],lambda aa,zz:wing_point(s,aa,min(1.525,zz),.008),upper,'shoulder',thickness=.007)
 # Actual pivot axle, passive short links concealed by the guard but readable
 # inside. No large exposed elbow knob/human forearm outside the mantle.
 a=upper.matrix_world.translation;b=lower.matrix_world.translation
 wr(label+' shoulder pivot',(s*.282,a.y,a.z),(s*.353,a.y,a.z),.050,upper,'shoulder','bearing',sides=28)
 wr(label+' short wing load member',a,b,.024,upper,'shoulder','frame')
 wr(label+' elbow pivot',(b.x-s*.023,b.y,b.z),(b.x+s*.020,b.y,b.z),.039,lower,'wing','bearing',sides=28)
 if s==1:
  wr('Original anatomical-left travel stop',(.327,.015,1.385),(.364,.015,1.385),.018,upper,'shoulder','frame')
  # Proposed later service strap remains separate from original stop.
  repair=bpy.data.objects['industrial-repairs']
  wt('Proposed later left bearing strap',[(.352,-.005,1.45),(.367,-.016,1.38),(.352,.008,1.31)],[.012,.013,.012],repair,'shoulder','repair','mechanic,builder')
# F04: selective protective channels over paired passive load members.
# Keep compatible leg joint centres; reduce bulky axles and vary toes/talons.
for s,label in [(1,'left'),(-1,'right')]:
 thigh=bpy.data.objects[label+'-thigh'];shin=bpy.data.objects[label+'-shin'];foot=bpy.data.objects[label+'-foot'];toes=bpy.data.objects[label+'-toes']
 hip=thigh.matrix_world.translation.copy();knee=shin.matrix_world.translation.copy();ankle=foot.matrix_world.translation.copy()
 for point,parent,rad in [(hip,thigh,.063),(knee,shin,.062),(ankle,foot,.047)]:
  wr(label+' stepped bearing barrel',point-Vector((.040,0,0)),point+Vector((.040,0,0)),rad,parent,'leg','frame',sides=28)
  for side in [-1,1]:
   wr(label+' bearing side plate',point+Vector((side*.040,0,0)),point+Vector((side*.049,0,0)),rad*.86,parent,'leg','bearing',sides=28)
   wr(label+' recessed bearing pin',point+Vector((side*.049,0,0)),point+Vector((side*.053,0,0)),rad*.39,parent,'leg','edge',sides=24)
 for a,b,parent,wide in [(hip,knee,thigh,.057),(knee,ankle,shin,.047)]:
  direction=(b-a).normalized();l=(b-a).length
  for dx in [-wide,wide]:
   aa=a+direction*.038+Vector((dx,0,0));bb=b-direction*.033+Vector((dx,0,0))
   wr(label+' passive paired load rail',aa,bb,.027 if parent==thigh else .022,parent,'leg','frame',end=.023 if parent==thigh else .019)
  # Tapered channel guards are interrupted at each bearing, never a cylinder.
  for j in range(3):
   p0=a.lerp(b,.16+j*.21);p1=a.lerp(b,.16+j*.21+.24)
   outline=[(-wide,p0.z), (wide,p0.z), (wide*.90,p1.z),(-wide*.85,p1.z)]
   def proj(x,z):
    f=(z-a.z)/(b.z-a.z);p=a.lerp(b,f);return (p.x+x,p.y-.047,z)
   patch(label+' shaped leg channel '+str(j)+parent.name,outline,proj,parent,'leg',thickness=.006)
   for dx in [-wide*.6,wide*.6]:fastener('Channel fixing',proj(dx,p0.z-.016),(0,-1,.1),parent,'leg',.003)
  # Hollow side channels expose the paired rails at the rear while giving
  # the load member a substantial rectangular/forged section in profile.
  for side in [-1,1]:
   length=(b-a).length;axis=(b-a).normalized()
   p0=a.lerp(b,.14);p1=a.lerp(b,.86)
   corners=[p0+Vector((side*(wide+.012),-.042,0)),p0+Vector((side*(wide+.012),.028,0)),p1+Vector((side*(wide+.004),.022,0)),p1+Vector((side*(wide+.004),-.034,0))]
   o=wm(label+' open load channel side',corners,[(0,1,2,3)],parent,'leg','plate');solid=o.modifiers.new('Forged channel wall','SOLIDIFY');solid.thickness=.008;bevel(o,.003)
   for t in [.22,.75]:
    pt=a.lerp(b,t)+Vector((side*(wide+.018),-.006,0));fastener('Leg channel transverse fixing',pt,(side,0,0),parent,'leg',.0045)
 # Metatarsal channel anchored to foot with passive paired side struts.
 base=Vector((ankle.x,-.13,.068))
 for dx in [-.031,.031]:wt(label+' metatarsal passive rail',[ankle+Vector((dx,0,-.027)),Vector((ankle.x+dx,-.045,.14)),base+Vector((dx,0,0))],[.019,.017,.024],foot,'foot')
 for j in range(5):
  t=j/5;z=.233-t*.153;y=.012-t*.15
  patch(label+' overlapping ankle instep '+str(j),[(-.05,z),(.05,z),(.052,z-.038),(0,z-.052),(-.052,z-.038)],lambda x,zz:(ankle.x+x,y+(zz-z)*.55-.020,zz),foot,'foot',thickness=.005)
 # Three independently hinged digits, distinct length and spread. Each has
 # proximal/distal ownership ready for a later supported claw action.
 for digit,(spread,length) in enumerate([(-.083,.235),(0,.28),(.09,.215)],1):
  root=Vector((ankle.x+spread*.70,-.13,.058));end=Vector((ankle.x+spread*1.45,-.13-length,.039))
  mid=root.lerp(end,.54);mid.z=.041
  pro=world_group(f'{label}-digit-{digit}-proximal',root,toes)
  dis=world_group(f'{label}-digit-{digit}-distal',mid,pro)
  for aa,bb,parent,rad in [(root,mid,pro,.034),(mid,end,dis,.028)]:
   wt('Digit inner link',[aa,bb],[rad*.80,rad*.65],parent,'foot','frame')
   for j in range(3):
    p=aa.lerp(bb,j/3);q=aa.lerp(bb,min(1,j/3+.42));w=rad*(1-j*.09)
    verts=[];faces=[]
    for center,ww in [(p,w),(q,w*.78)]:
     for k in range(9):
      angle=-1.3+2.6*k/8;verts.append((center.x+math.sin(angle)*ww,center.y,center.z+math.cos(angle)*ww))
    for k in range(8):faces.append((k,k+1,k+10,k+9))
    o=wm(f'{label} digit {digit} knuckle guard',verts,faces,parent,'foot','plate');m=o.modifiers.new('Toe cover thickness','SOLIDIFY');m.thickness=.004;bevel(o,.001)
   wr('Toe hinge',aa-Vector((rad,0,0)),aa+Vector((rad,0,0)),rad*.66,parent,'foot','bearing',sides=16)
  # Hook sweeps down to floor and has a wider root/flattened cutting tip.
  clawlength=[.090,.113,.077][digit-1]
  pts=[end+Vector((0,.017,.017)),end+Vector((spread*.08,-clawlength*.32,.036)),end+Vector((spread*.12,-clawlength*.76,.022)),end+Vector((spread*.15,-clawlength,-.032))]
  claw_pts=[curve(pts,t/16) for t in range(17)]
  claw_r=[.031*(1-t/17)**.9 for t in range(17)];claw_r[-1]=.0017
  wt(f'{label} digit {digit} curved talon',claw_pts,claw_r,dis,'foot','edge',sides=16)
 # Rear hallux is short and follows foot, not a dinosaur sickle.
 wt(label+' rear hallux load link',[base,(ankle.x,.014,.058)],[.042,.035],foot,'foot','frame')
 wt(label+' rear hallux',[(ankle.x,.014,.058),(ankle.x+s*.046,.08,.039),(ankle.x+s*.065,.115,.008)],[.028,.022,.002],foot,'foot','edge',sides=14)
# Retained inner power/processing are Advanced-only, separately inspectable.
for name,reg in [('power-core','breast'),('processing','head')]:
 obj=bpy.data.objects[name]
 if name=='power-core':
  ps=[o.matrix_world@Vector(c) for o in obj.children_recursive if o.type=='MESH' for c in o.bound_box]
  centre=Vector(tuple((min(p[i] for p in ps)+max(p[i] for p in ps))/2 for i in range(3)))
  obj.matrix_world.translation+=Vector((0,-.075,1.16))-centre
 for o in obj.children_recursive:
  if o.type=='MESH':
   o.data.materials.clear();o.data.materials.append(mat['inner']);tag(o,o.parent,reg,'inner','builder')
body.location.z-=.08
bpy.context.view_layer.update()
# Cut each crown lamina against the optic aperture before export. The
# subtraction affects only rigid head plates and is recorded as construction.
for side in [-1,1]:
 cutter=rod('Temporary optic clearance cutter',(side*.085,-.334,1.858),(side*.23,-.334,1.858),.074,mat['recess'],None,48)
 for obj in list(bpy.data.objects):
  if obj.type=='MESH' and obj.name.startswith('Swept crown lamina'):
   mod=obj.modifiers.new('Optic aperture clearance','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cutter;mod.solver='EXACT'
   bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
   for modifier in list(obj.modifiers):bpy.ops.object.modifier_apply(modifier=modifier.name)
 bpy.data.objects.remove(cutter,do_unlink=True)
# Save editable independent pieces before export batching. Each rigid part
# carries eligibility, role and source/reconstruction information.
root=bpy.data.objects['murderbird'];root['status']='neutral-v2 Stage B proposal; not artistically accepted';root['basePivots']=BASE_SHA
head.rotation_euler.z=0;bpy.context.scene.render.fps=30;bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=31
for frame,angle in [(1,0),(16,.12),(31,0)]:head.rotation_euler.z=angle;head.keyframe_insert(data_path='rotation_euler',frame=frame)
head.animation_data.action.name='attention-export-proof';bpy.context.scene.frame_set(1)
# Bake authored modifiers and remove degenerate faces without merging owners.
for o in list(bpy.context.scene.objects):
 if o.type!='MESH':continue
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
 bm=bmesh.new();bm.from_mesh(o.data);bad=[f for f in bm.faces if f.calc_area()<1e-12]
 if bad:bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
 for attr in list(o.data.color_attributes):o.data.color_attributes.remove(attr)
bpy.context.view_layer.update()
pivots=[{'name':o.name,'parent':o.parent.name if o.parent else None,'local':list(o.location),'world':list(o.matrix_world.translation),'scale':list(o.scale)} for o in bpy.data.objects if o.type=='EMPTY']
blend=OUT/'murderbird-neutral-v2.blend';pending=OUT/'.building-neutral.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(pending));pending.replace(blend)
# Group by rigid attachment, eligibility, region AND material role. Role
# metadata stays truthful rather than inheriting one arbitrary source role.
groups={}
for o in list(bpy.context.scene.objects):
 if o.type=='MESH':groups.setdefault((o.parent,o.get('exteriorEras',ALL),o.get('region','back'),o.get('surfaceRole','frame')),[]).append(o)
for (parent,eras,reg,rl),objects in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=f'{parent.name}-{reg}-{rl}';o['exteriorEras']=eras;o['region']=reg;o['surfaceRole']=rl
path=OUT/'murderbird-neutral-v2.glb';pending=OUT/'.building-neutral.glb'
bpy.ops.export_scene.gltf(filepath=str(pending),export_format='GLB',export_yup=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False,export_animations=True,export_animation_mode='ACTIONS',export_frame_range=True);pending.replace(path)
manifest={'status':'neutral geometry proposal awaiting owner review','startingRevision':'4b1c726f5d9bbd1ba1048f89049a5b422001c506','base':{'path':str(BASE.relative_to(ROOT)),'sha256':BASE_SHA},'conventions':'metres; X anatomical left, -Y forward, Z up; dimensions authored not recovered','parts':parts,'pivots':pivots,'billContact':list(contact.matrix_world.translation),'newDigitInterfaces':'left/right-digit-1/2/3-proximal/distal; rigid hinges, not yet active grip choreography','generatedFiles':[{'path':str(f.relative_to(ROOT)),'bytes':f.stat().st_size,'sha256':sha(f)} for f in [blend,path]]}
receipt.write_text(json.dumps(manifest,indent=2)+'\n')
print('NEUTRAL_V2_SAVED',len(parts),sha(path))
