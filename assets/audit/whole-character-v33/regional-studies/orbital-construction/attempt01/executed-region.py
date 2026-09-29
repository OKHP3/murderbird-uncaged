"""V33 reference-led recessed orbital/cheek construction proposal.

Native metres, Z up, negative Y anterior. July is head-only authority;
owner whole-bird controls neutral closed impression. Profiles are authored
construction, not dimensions recovered from unmatched reference cameras.
"""
from pathlib import Path
import bpy,bmesh,runpy,math,hashlib
from mathutils import Vector,Matrix

ROOT=Path(globals().get('SOURCE_ROOT','/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged'))
EYE=(-.220,.260)
BROW_OUT=[(.130,-.128,.296),(.127,-.154,.333),(.116,-.216,.350),(.118,-.266,.340),(.123,-.301,.291)]
CHEEK_OUT=[(.126,-.304,.256),(.139,-.289,.219),(.143,-.246,.192),(.140,-.198,.186),(.142,-.151,.191),(.134,-.127,.224),(.125,-.137,.263)]

def apply():
 helper=ROOT/'scripts/regions/whole-character-v31-head-reconstruction.py'
 assert hashlib.sha256(helper.read_bytes()).hexdigest()=='76c8bad1825ede7cf3fac5d068ab60f29a4e8e5059a78dfc5a9cabfd03d39022'
 h=runpy.run_path(str(helper));bpy.context.view_layer.update()
 head=bpy.data.objects['head'];origin=head.matrix_world.translation.copy()
 names=[f'V32 {label} {side}' for side in (-1,1) for label in ('slanted orbital brow','swept orbital cheek','recessed optic bearing')]
 names += [f'V31 formed throat receiving guard {side}' for side in (0,-1,1)]
 assert all(n in bpy.data.objects and bpy.data.objects[n].parent==head for n in names)
 protected={o.name:h['snap'](o) for o in bpy.data.objects if o.type=='MESH' and o.name not in names}
 nodes={o.name:h['node'](o) for o in bpy.data.objects if o.type=='EMPTY'}
 templates={k:{'props':dict(bpy.data.objects[n].items()),'materials':list(bpy.data.objects[n].data.materials)} for k,n in [('plate','V32 slanted orbital brow 1'),('bearing','V32 recessed optic bearing 1')]}
 for n in names:bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
 added=[];solids=[]
 def add(name,geo,kind='plate',role='plate',smooth=False):
  verts,faces=geo;world=[origin+Vector(p) for p in verts];mesh=bpy.data.meshes.new(name+' finite mesh');o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.parent=head;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Identity(4);bpy.context.view_layer.update();inv=o.matrix_world.inverted();mesh.from_pydata([inv@p for p in world],[],faces);mesh.update()
  for m in templates[kind]['materials']:mesh.materials.append(m)
  for k,v in templates[kind]['props'].items():o[k]=v
  o['region']='head';o['surfaceRole']=role;o['proposal']=True;o['constructionOwner']='head';o['constructionClass']='inherited-passive';o['exteriorEras']='maker,mechanic,builder';o['articulatesAcrossJoint']=False;o['constructionDescription']='V33 formed directional orbital receiver; fixed head-owned finite passive plate'
  bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  volume=bm.calc_volume(signed=True);assert volume>0,name;bm.to_mesh(mesh);bm.free()
  for p in mesh.polygons:p.use_smooth=smooth
  err=max((o.matrix_world@v.co-w).length for v,w in zip(mesh.vertices,world));assert err<1e-6
  added.append(name);solids.append({'name':name,'owner':'head','positiveVolumeM3':volume,'closed':True,'finiteWallM':.0045 if kind=='plate' else None,'authoredWorldErrorM':err});return o
 def receiver(side,lo,hi,brow,layer=0):
  # Separate upper/front and lower/rear routes, not one broad spectacle.
  # The aperture's fixed inner seat is outside the unchanged cup radius;
  # outer boundaries have directional planes rather than a radial annulus.
  rows=BROW_OUT if brow else CHEEK_OUT
  def fn(u,v):
   t=lo+(hi-lo)*u;q=h['sample'](rows,t);angle=(math.pi*t if brow else math.pi+math.pi*t)
   cy,cz=EYE;r=.0545 if brow else .0555
   y=cy+r*math.cos(angle);z=cz+r*math.sin(angle)
   x=.148 if brow else .146
   # Central land, raised formed ridge, recessed structural root.
   if v<.55:
    a=v/.55;xx=x*(1-a)+(.156+layer)*a;yy=y*(1-a)+(y*.56+q[1]*.44)*a;zz=z*(1-a)+(z*.56+q[2]*.44)*a
   else:
    a=(v-.55)/.45;xx=(.156+layer)*(1-a)+(q[0]+layer)*a;yy=(y*.56+q[1]*.44)*(1-a)+q[1]*a;zz=(z*.56+q[2]*.44)*(1-a)+q[2]*a
   # Defined planes, modest three-dimensional curvature across each land.
   return Vector((side*xx,yy,zz))
  return h['finite_sheet'](fn,nu=32,nv=10,wall=.0045,side=side)
 for side in (-1,1):
  # Small deliberate angular seams; exact aperture is uninterrupted.
  for i,(a,b) in enumerate([(0,.30),(.307,.70),(.707,1)]):add(f'V33 diagonal brow receiver {side} {i}',receiver(side,a,b,True))
  for i,(a,b) in enumerate([(0,.47),(.479,1)]):add(f'V33 formed lower cheek receiver {side} {i}',receiver(side,a,b,False))
  # A narrow retaining rim shelters the existing receiving cup; no new
  # sensing or luminous surface. Lens/cup/floor remain exact original.
  add(f'V33 recessed optic retaining lip {side}',h['annular'](side,*EYE,[(.143,.0495),(.146,.0495),(.147,.053),(.143,.053)]),'bearing','bearing',True)
  # A broad formed return follows the rear cheek toward the jaw journal.
  # Its innermost X stays outside the independently rotating jaw cap.
  rows=[(.142,-.149,.210,.015),(.147,-.122,.193,.019),(.149,-.110,.171,.019),(.141,-.104,.147,.014)]
  add(f'V33 mandibular hinge cheek return {side}',h['ribbon'](side,rows,wall=.0045,bulge=.002))
 # Head-owned tapered throat plates terminate on the SAME receiving
 # envelope. They do not bridge into cervical-upper or alter its guards.
 # Longitudinal directions and staggered top ends avoid circular cuffs.
 def throat(side,lo,hi,col):
  def fn(u,v):
   width=.98-.13*h['smooth']((u-.50)/.50);a=(lo+hi)/2+(v-.5)*(hi-lo)*width
   top=(.96 if side==0 else .94)-.10*abs(2*v-1)**2+.026*math.sin(math.pi*v)
   t=u*top;z,cy,rx,ry=h['sample'](h['LOWER_SKULL'],t);x=rx*math.sin(a);y=cy-ry*math.cos(a)
   if side==-1:x=-x
   if side:
    rear=h['smooth']((a/math.pi-.50)/.50);z-=.029*t*t*t*rear;z+=.010*math.sin(a)*math.sin(math.pi*t)
    w=h['smooth']((a-1.43)/.28);r=math.hypot(y,z);seat=.117-.030*(abs(x)/.085)**2
    if seat>r and r>1e-8:ratio=1+w*(seat/r-1);y*=ratio;z*=ratio
   # Root remains at original envelope; upper plates acquire modest
   # formed ridges and nested 5mm plate offset only away from the joint.
   offset=(.0025*math.sin(math.pi*v)+.005*(col%2))*h['smooth']((u-.25)/.75)
   radial=Vector((x,y+.035,0));radial.normalize();return Vector((x,y,z))+offset*radial
  return h['finite_sheet'](fn,nu=32,nv=14,wall=.005,reference=lambda p:Vector((p.x,p.y+.035,0)))
 for side in (0,-1,1):
  bands=[(-.65,-.204),(-.217,.217),(.204,.65)] if side==0 else [(.670,1.506),(1.492,2.318),(2.304,math.pi-.018)]
  for i,(a,b) in enumerate(bands):add(f'V33 tapered throat cheek plate {side} {i}',throat(side,a,b,i),role='receiving-plate')
 bpy.context.view_layer.update()
 assert all(h['node'](bpy.data.objects[n])==s for n,s in nodes.items())
 assert all(h['snap'](bpy.data.objects[n])==s for n,s in protected.items())
 return {'region':'orbital-construction','status':'Reference-led visible proposal; fit/likeness acceptance pending','removed':names,'added':added,'changedMeshes':[],'changedNodes':[],'protectedMeshesExact':len(protected),'allOriginalNodesExact':len(nodes),'materialsChanged':False,'retainedEyeCenterNativeHeadOffset':[.158,*EYE],'finiteSolids':solids,'browOuterProfile':BROW_OUT,'cheekOuterProfile':CHEEK_OUT,'lensCupFloorExact':True,'throatReceivingEnvelope':'Same root/profile; staggered tapered head-owned finite plates, no cervical rigid bridge','limits':['Authored reference interpretation, no recovered image dimensions.','Preserves bill/jaw and cap root geometries; composed cap source must be checked independently.','Discrete jaw/cap and adjacent neck screens required; no continuous/engineering/artistic acceptance.']}
