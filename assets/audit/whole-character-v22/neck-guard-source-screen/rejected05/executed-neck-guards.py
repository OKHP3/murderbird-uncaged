"""V22 directional cervical guards on exact frame04; source-only proposal.

Native metres/Z-up/-Y-front. Existing named head/neck chain and all
53 rigid rests stay untouched. The frame and bearings remain exposed through
purposeful guard gaps; each formed solid stays on its original rigid owner.
"""
import bpy,bmesh,math
from mathutils import Vector

ERAS='maker,mechanic,builder'
BASE_SHA256='b3ac4677d2e76a0e08544323306c07f2ed7e61cd381d274a944d8e5b87031d1f'
WALL=.0035
TARGETS=('V21 lower swept throat keel','V21 upper swept throat keel',
 'V21 lower swept nape return','V21 upper swept nape return',
 'V21 ascending root yoke -1','V21 ascending root yoke 1',
 'V21 upper cervical directional guard -1','V21 upper cervical directional guard 1',
 'V21 linked joint front','V21 linked joint nape',
 'V21 linked joint side -1','V21 linked joint side 1')


def signature(o):
 return (o.parent.name if o.parent else None,tuple(tuple(float(v) for v in r) for r in o.matrix_world),tuple((k,repr(o[k])) for k in sorted(o.keys())))

def mesh_signature(o):
 return (signature(o),tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(f.vertices) for f in o.data.polygons),tuple(m.name if m else None for m in o.data.materials))

def surface(o):
 pts=[o.matrix_world@v.co for v in o.data.vertices];assert len(pts)==825,o.name
 def sample(t,q):
  y=max(0,min(1,t))*32;x=max(0,min(1,q))*24;j=min(31,int(y));k=min(23,int(x));a=y-j;b=x-k
  return pts[j*25+k].lerp(pts[j*25+k+1],b).lerp(pts[(j+1)*25+k].lerp(pts[(j+1)*25+k+1],b),a)
 return sample

def append_sheet(verts,faces,fun,normal,rows=12,cols=10):
 """Explicit finite wall; tapered sheet tips retain width and thickness."""
 base=len(verts);outer=[];inner=[]
 for j in range(rows+1):
  t=j/rows
  for k in range(cols+1):
   q=k/cols;p=Vector(fun(t,q))
   dt=Vector(fun(min(1,t+.001),q))-Vector(fun(max(0,t-.001),q))
   dq=Vector(fun(t,min(1,q+.001)))-Vector(fun(t,max(0,q-.001)))
   n=dt.cross(dq).normalized()
   if n.dot(normal)<0:n.negate()
   outer.append(p);inner.append(p-n*WALL)
 verts.extend(outer+inner);n=len(outer)
 for j in range(rows):
  for k in range(cols):
   a=base+j*(cols+1)+k;b=a+cols+1
   faces.extend(((a,a+1,b+1,b),(a+n,b+n,b+1+n,a+1+n)))
 edge=list(range(cols+1))+[j*(cols+1)+cols for j in range(1,rows+1)]
 edge += list(range(n-2,n-cols-2,-1))+[j*(cols+1) for j in range(rows-1,0,-1)]
 for i,a in enumerate(edge):
  b=edge[(i+1)%len(edge)];faces.append((base+a,base+b,base+b+n,base+a+n))


def sampled_panel(sample,t0,t1,center,half,normal,offset=0,sweep=0):
 def fun(t,q):
  # Narrow rounded root, broad formed middle, swept finite tapered free end.
  w=.86+.14*math.sin(math.pi*t)-.22*t*t
  uq=2*q-1;u=center+half*uq*w+sweep*t
  longitudinal=t0+(t1-t0)*t + .025*(uq*uq)*t
  return sample(longitudinal,u)+normal*offset
 return fun


def install(o,verts,faces,description):
 inv=o.matrix_world.inverted();m=bpy.data.meshes.new(o.name+' V22 directional construction')
 m.from_pydata([inv@Vector(v) for v in verts],[],faces);m.update()
 for mat in o.data.materials:m.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 assert all(e.is_manifold for e in bm.edges),o.name
 assert bm.calc_volume(signed=True)>0,o.name
 bm.to_mesh(m);bm.free();o.data=m;o.modifiers.clear()
 for f in m.polygons:f.use_smooth=True
 o['region']='neck-guards';o['surfaceRole']='guard';o['exteriorEras']=ERAS
 o['constructionClass']='inherited-passive';o['proposal']=True
 o['constructionDescription']=description
 o['jointMounting']='Single existing rigid owner; linked cover keeps existing half-angle motion'
 return o


def lower_front(t,q,half):
 # Actual throat tucks behind the breast top. No old guard descends into the
 # anterior breast backing. A slanted shoulder edge avoids a horizontal cuff.
 z=1.425-.095*t-.012*(q-.5)*half
 x=half*(.008+.062*q*(.82+.18*math.sin(math.pi*t)))
 y=-.324-.012*math.sin(math.pi*t)+.015*t+.055*math.sqrt(t)+.021*q*q
 return (x,y,z)


def lower_side(t,q,side):
 z=1.405-.090*t-.017*(q-.5)
 x=side*(.112+.044*t*t+.005*math.sin(math.pi*q))
 y=-.217+(q-.5)*(.112-.027*t)-.022*t+.055*t*t
 return (x,y,z)


def lower_nape(t,q,half):
 z=1.40-.085*t+.012*(q-.5)*half
 x=half*(.012+.077*q*(.85+.15*math.sin(math.pi*t)))
 y=-.12+.071*t*t-.012*q*q
 return (x,y,z)


def linked_front(t,q,half,axis):
 # Two short concentric receiving blades. Their70mm radial seat stays
 # inside the opposed lower/upper guards; no full circumferential ring.
 a=-.10+.63*t+.065*(q-.5)*half;r=.070
 return (half*(.008+.040*q*(.86-.22*t)),axis.y-r*math.cos(a),axis.z+r*math.sin(a))


def crescent(t,q,side,axis):
 # Short swept visor above the actual native-X journal, not a full cheek mask.
 a=.27+2.55*q+.17*t;r=.047+.020*t
 return (side*(.092+WALL/2),axis.y-r*math.cos(a),axis.z+r*math.sin(a))


def apply():
 bpy.context.view_layer.update()
 nodes={o.name:signature(o) for o in bpy.data.objects if o.type=='EMPTY'}
 outside={o.name:mesh_signature(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in TARGETS}
 samples={n:surface(bpy.data.objects[n]) for n in TARGETS if 'linked joint side' not in n}
 pieces={};front=Vector((0,-1,0));rear=Vector((0,1,0));axis=bpy.data.objects['cervical-upper'].matrix_world.translation.copy()
 for name in TARGETS:
  o=bpy.data.objects[name];v=[];f=[];count=0
  if name=='V21 lower swept throat keel':
   for half in (-1,1):append_sheet(v,f,lambda t,q,h=half:lower_front(t,q,h),front);count+=1
  elif name=='V21 lower swept nape return':
   for half in (-1,1):append_sheet(v,f,lambda t,q,h=half:lower_nape(t,q,h),rear);count+=1
  elif 'ascending root yoke' in name:
   side=-1 if name.endswith('-1') else 1
   append_sheet(v,f,lambda t,q,s=side:lower_side(t,q,s),Vector((side,0,0)));count+=1
  elif name in ('V21 upper swept throat keel','V21 upper swept nape return'):
   normal=front if 'throat' in name else rear
   # Two long oblique halves carry the headward curve without circumferential
   # bands. Unequal free-edge lengths leave a staggered receiving joint.
   for half in (-1,1):
    c=(.25 if half<0 else .75) if 'throat' in name else (.40 if half<0 else .60)
    append_sheet(v,f,sampled_panel(samples[name],.035 if 'throat' in name else .82,(.92 if half<0 else .83) if 'throat' in name else .98,c,.222 if 'throat' in name else .08,normal,0,sweep=half*.026),normal);count+=1
  elif 'upper cervical directional guard' in name:
   side=-1 if name.endswith('-1') else 1;normal=Vector((side,0,0))
   # A short cheek-root guard and a narrower lower swept blade expose the
   # actual upper load bow. Their6mm radial lap exceeds3.5mm wall thickness.
   append_sheet(v,f,sampled_panel(samples[name],.68,.85,.16,.10,normal,.006,sweep=-side*.025),normal);count+=1
   append_sheet(v,f,sampled_panel(samples[name],.80,.99,.24,.12,normal,0,sweep=-side*.02),normal);count+=1
  elif name=='V21 linked joint front':
   for half in (-1,1):
    append_sheet(v,f,lambda t,q,h=half:linked_front(t,q,h,axis),front);count+=1
  elif name=='V21 linked joint nape':
   normal=front if name.endswith('front') else rear
   for half in (-1,1):
    append_sheet(v,f,sampled_panel(samples[name],.30 if name.endswith('front') else .22,.80 if name.endswith('front') else .78,.28 if half<0 else .72,.16,normal,.025 if name.endswith('front') else -.010,sweep=half*.018),normal);count+=1
  else:
   side=-1 if name.endswith('-1') else 1
   append_sheet(v,f,lambda t,q,s=side:crescent(t,q,s,axis),Vector((side,0,0)),rows=8,cols=24);count+=1
  install(o,v,f,'Directional swept guard with finite3.5mm wall, staggered returned edges and open frame/journal reveal; replaces oversized original cuff surface.')
  pieces[name]=count
 bpy.context.view_layer.update()
 assert nodes=={o.name:signature(o) for o in bpy.data.objects if o.type=='EMPTY'}
 assert all(mesh_signature(bpy.data.objects[n])==s for n,s in outside.items())
 return {'status':'V22 directional cervical construction proposal; visual and discrete motion checks required',
  'changed':list(TARGETS),'added':[],'removed':[],'stagedOut':'All12old cuff surface mesh data replaced; historical source/native preserved.',
  'finiteGuardSections':pieces,'sectionCount':sum(pieces.values()),'wallM':WALL,
  'preservedOriginalNodes':len(nodes),'preservedOtherMeshes':len(outside),
  'classification':'Passive inherited guards in Maker/Mechanic/Builder. Existing linked cover motion unchanged; no new runtime interface.',
  'construction':'Paired long swept throat/nape guards, short flank blades and partial journal visors replace the broad cuff. Lower throat tucks behind breast rather than descending onto its front backing. Upper flank overlap is radial6mm for3.5mm walls; all pieces retain a single rigid owner.',
  'limits':['Rest and discrete9pitch sampling only; no continuous clearance claim.','Existing frame/bearings/head/breast door unchanged.','Proposed open frame reveals and hidden receiving surfaces are authored construction, not historical source facts.']}
