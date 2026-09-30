"""Cheek-layout02. Footprint-first guide on actual cheek-interface01.
Forty existing passive head-owned meshes reconstructed; true optics/jaw/bill exact.
"""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
BROWS=[f'V33 diagonal brow receiver {s} {i}'for s in(-1,1)for i in range(3)]
SHIELDS=[f'V38 optic cheek shield {s} {i}'for s in(-1,1)for i in range(3)]
LEAVES=[f'V33 swept temporal leaf {s} {i}'for s in(-1,1)for i in range(7)]
ROOTS=[f'V31 temporal fitting root {s} {i}'for s in(-1,1)for i in range(3)]
FITTINGS=[f'V31 passive temporal fitting {s} {i}'for s in(-1,1)for i in range(3)]
WALLS=[f'V31 fixed temporal receiving wall {s}'for s in(-1,1)]
NAMES=WALLS+BROWS+SHIELDS+LEAVES+ROOTS+FITTINGS

def install(name,verts,faces,kind,records):
 o=bpy.data.objects[name];m=bpy.data.meshes.new(name+' footprint-first finite shell');inv=o.matrix_world.inverted();m.from_pydata([inv@p for p in verts],[],faces);m.update()
 for mat in o.data.materials:m.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 volume=bm.calc_volume(signed=True);assert volume>0;bm.to_mesh(m);bm.free();o.data=m
 for f in m.polygons:f.use_smooth=False
 o['v38CheekLayout']='Footprint-first supported passive cheek reconstruction proposal'
 records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'kind':kind,'closedEdges':True,'positiveVolumeM3':volume,'materials':[q.name if q else None for q in m.materials]})

def smooth(poly,n=7):
 out=[]
 for i,b in enumerate(poly):
  a=poly[(i-1)%len(poly)];c=poly[(i+1)%len(poly)];d=poly[(i+2)%len(poly)]
  for j in range(n):
   t=j/n;out.append([.5*(2*b[k]+(-a[k]+c[k])*t+(2*a[k]-5*b[k]+4*c[k]-d[k])*t*t+(-a[k]+3*b[k]-3*c[k]+d[k])*t*t*t)for k in range(2)])
 return out

def apply():
 records=[];lands=[];layout=json.loads((Path(__file__).resolve().parents[2]/'assets/audit/whole-character-v38/cheek-layout01/plate-layout.json').read_text());shapes={s['id']:s['points']for s in layout['shapes']}
 for side in(-1,1):
  def lateral(y,z):return .128+.025*math.exp(-((y+.43)/.20)**2-((z-1.76)/.20)**2)
  def patch(name,poly,stock,lift,kind,curve=True):
   yz=smooth(poly)if curve else poly;p=[Vector((side*(lateral(y,z)+lift),y,z))for y,z in yz];tri=tessellate_polygon([p]);ids={id(v):i for i,v in enumerate(p)}
   # tessellate returns original vectors; coordinate fallback for Python bindings.
   idx=lambda v: v if isinstance(v,int) else next(i for i,q in enumerate(p)if (q-v).length<1e-8)
   fs=[tuple(idx(v)for v in t)for t in tri]
   # Refine actual side-domain cap triangulation; re-evaluate coherent lateral
   # surface at every shared midpoint. Caps and finite side returns have
   # separate normals, with a small real bevel on perimeter edges.
   for iteration in range(2):
    cache={};new=[]
    def mid(a,b):
     key=tuple(sorted((a,b)))
     if key not in cache:
      q=(p[a]+p[b])*.5;q.x=side*(lateral(q.y,q.z)+lift);cache[key]=len(p);p.append(q)
     return cache[key]
    for a,b,c in fs:
     ab,bc,ca=mid(a,b),mid(b,c),mid(c,a);new.extend([(a,ab,ca),(ab,b,bc),(ca,bc,c),(ab,bc,ca)])
    fs=new
   from collections import Counter
   count=Counter(tuple(sorted((f[j],f[(j+1)%3])))for f in fs for j in range(3));n=len(p);v=p+[q-Vector((side*stock,0,0))for q in p];faces=fs+[tuple(n+i for i in reversed(f))for f in fs]
   for f in fs:
    for j in range(3):
     a,b=f[j],f[(j+1)%3]
     if count[tuple(sorted((a,b)))]==1:faces.append((a,b,n+b,n+a))
   install(name,v,faces,kind,records)
   o=bpy.data.objects[name]
   # Only cap faces smooth across their refined field; side faces remain crisp.
   for i,f in enumerate(o.data.polygons):f.use_smooth=i<2*len(fs)
   bpy.context.view_layer.objects.active=o;o.select_set(True);bevel=o.modifiers.new('finite formed perimeter bevel','BEVEL');bevel.width=.00065;bevel.segments=2;bevel.limit_method='ANGLE';bevel.angle_limit=.70;bpy.ops.object.modifier_apply(modifier=bevel.name);o.select_set(False)
   bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges),name;assert bm.calc_volume()>0;bm.free()
   return p,fs
  # Recessed support is rear-bounded and shaped under the footprints, not an external orbital disk.
  back=[[-.612,1.814],[-.582,1.870],[-.461,1.871],[-.361,1.826],[-.284,1.758],[-.260,1.674],[-.330,1.612],[-.423,1.638],[-.476,1.697],[-.489,1.774]]
  wall=f'V31 fixed temporal receiving wall {side}';wp,wf=patch(wall,back,.005,0,'Recessed compound-curved rear receiving skull support beneath explicit guards; no filled exterior oval')
  # Actual guide brow partition has shaped boundaries, not orbital radial sectors.
  brows=[shapes['brow'][:4]+[shapes['brow'][6],shapes['brow'][7],shapes['brow'][8]],
   [[-.548,1.852],[-.458,1.838],[-.397,1.809],[-.411,1.784],[-.472,1.814],[-.558,1.827]],
   [[-.458,1.838],[-.381,1.803],[-.397,1.779],[-.472,1.814]]]
  for i,poly in enumerate(brows):patch(f'V33 diagonal brow receiver {side} {2-i}',poly,.0045,.008+i*.004,'Angled guide-derived compound curved brow with shaped taper; receiving footprint requires finite surface audit')
  patch(f'V38 optic cheek shield {side} 0',shapes['cheek-member'],.005,.014,'Dominant curved rising cheek member from guide; compact under/back optic, no complete eye ring')
  patch(f'V38 optic cheek shield {side} 1',shapes['rear-middle'],.0045,.011,'Short curved mid-temporal guard with deliberate tapered down/back boundary')
  patch(f'V38 optic cheek shield {side} 2',shapes['rear-lower'],.0045,.014,'Short jaw-side guard; actual jaw journal and mouth void remain source exact')
  leafpolys=[[[ -.586,1.862],[-.498,1.874],[-.415,1.844],[-.426,1.813],[-.511,1.836],[-.589,1.836]],
   [[-.560,1.832],[-.489,1.843],[-.409,1.818],[-.424,1.792],[-.496,1.816],[-.565,1.809]],
   [[-.390,1.789],[-.331,1.763],[-.296,1.727],[-.313,1.713],[-.353,1.741],[-.405,1.766]],
   [[-.377,1.746],[-.331,1.716],[-.298,1.684],[-.316,1.673],[-.351,1.699],[-.390,1.723]],
   [[-.338,1.692],[-.302,1.659],[-.321,1.635],[-.355,1.662]],
   [[-.426,1.682],[-.390,1.662],[-.365,1.629],[-.390,1.620],[-.440,1.660]],
   [[-.428,1.798],[-.450,1.777],[-.467,1.746],[-.448,1.735],[-.420,1.771]]]
  for i,p in enumerate(leafpolys):patch(f'V33 swept temporal leaf {side} {i}',p,.0035,.016+(i%3)*.004,'Short swept formed guard; upper two are compact tiered receiving coverage below independently moving crown; narrow reveal retained')
  # Finite fitting lands use actual largest receiver triangles with sufficient interior diameter.
  for i,target in enumerate([wall,f'V38 optic cheek shield {side} 1',f'V38 optic cheek shield {side} 2']):
   o=bpy.data.objects[target];o.data.calc_loop_triangles();pp=[o.matrix_world@v.co for v in o.data.vertices]
   def area(t):a,b,c=[pp[k]for k in t.vertices];return (b-a).cross(c-a).length
   t=max(o.data.loop_triangles,key=area);base=[pp[k]for k in t.vertices];center=sum(base,Vector())/3;plane=max(abs(q.x)for q in base)+.005;n=3;v=base+[Vector((side*plane,q.y,q.z))for q in base];faces=[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)]
   name=f'V31 temporal fitting root {side} {i}';install(name,v,faces,'Complete actual finite receiver triangle extrusion to planar passive fitting land; footprint audit separate',records)
   fit=f'V31 passive temporal fitting {side} {i}';count=48;rad=.004;profile=[(plane,rad),(plane+.001,rad),(plane+.003,rad*.85),(plane+.003,.0018),(plane,.0018)];fv=[Vector((side*x,center.y+r*math.cos(2*math.pi*j/count),center.z+r*math.sin(2*math.pi*j/count)))for x,r in profile for j in range(count)];faces=[]
   for row in range(5):
    nxt=(row+1)%5
    for j in range(count):k=(j+1)%count;faces.append((row*count+j,row*count+k,nxt*count+k,nxt*count+j))
   install(fit,fv,faces,'Passive8mm annular fitting base; full actual finite footprint must be checked, not inferred from centroid',records)
   lands.append({'root':name,'fitting':fit,'receiver':target,'actualInnerTriangles':1,'actualFullPatchYZExtentsM':[max(q.y for q in base)-min(q.y for q in base),max(q.z for q in base)-min(q.z for q in base)],'fittingFootDiameterM':.008,'returnOuterNativeSignedX':side*plane,'minimumAxialReturnDepthM':.005})
 return {'changedMeshes':NAMES,'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'attachmentAndEraMap':records,'pairedFittingSeats':lands,'guide':'assets/audit/whole-character-v38/cheek-layout01/plate-layout.json','construction':'Footprint-first compact cheek member and independent short staggered guards; recessed support authored beneath rear plate composition. Nominal stock and complete finite triangle fitting lands, not attachment/clearance acceptance.','rigidVsFlexible':'All40 head-owned passive inherited Maker/Mechanic/Builder; no sensing/power additions.','confirmation':'Actual July HEAD ONLY plus Master03/Maker-clean; native optic/journal landmarks from source inventory.','reconstruction':'Directional footprint/depth/receiving surfaces authored proposals; pixel observations not metrology.','protected':'Actual optic/bill/jaw283socket/journal/pivots/cranial cover/body exact.','limits':['No automatic solid fit from closed edges, shared field, root triangles or centroid. Full fitting footprint checked separately.','Current journal relation differs from inferred July fitting relation; no articulation move authorized.','Source backing closure/support extent and all plate-to-backing interfaces require actual review; not a sealed skull/load certificate.']}
