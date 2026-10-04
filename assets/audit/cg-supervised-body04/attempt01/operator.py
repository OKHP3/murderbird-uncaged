"""Locally formed regional plates for frozen cycle03; CG proposal, not engineering.
API apply(scene, root_path=None, era='builder'). Receiving meshes are hidden,
never modified. Body/neck/shield construction only; head and stance protected.
"""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy, bmesh
from mathutils import Vector

SOURCE_SHA='01103e35bcf16f03fc4a7b7d157bbe89d7267b8d0ca5ca8cd3f6167a6fcb8fce'
REF_SHA='645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114'
# Regional section guides place plate ROOTS only. No vertex is sampled from a
# common enclosing surface; each face is constructed in its own tangent frame.
BREAST=[(.76,-.02,.10,.16),(.84,-.03,.16,.24),(.94,-.035,.20,.30),(1.04,-.05,.224,.326),(1.14,-.06,.228,.329),(1.24,-.09,.195,.259),(1.31,-.102,.123,.147),(1.37,-.082,.100,.11),(1.43,-.062,.090,.103),(1.50,-.08,.10,.11),(1.56,-.114,.11,.115)]
WING=[(.95,.115,.192,.246,.009),(1.005,.002,.249,.255,.04),(1.075,-.099,.261,.238,.094),(1.155,-.178,.253,.221,.134),(1.235,-.205,.218,.205,.147),(1.31,-.180,.147,.191,.121),(1.365,-.10,.077,.178,.079),(1.393,-.025,.014,.170,.025)]
def interpolate(rows,z):
 z=max(rows[0][0],min(rows[-1][0],z))
 for a,b in zip(rows,rows[1:]):
  if a[0]<=z<=b[0]:
   t=(z-a[0])/(b[0]-a[0]);return [a[i]*(1-t)+b[i]*t for i in range(1,len(a))]
 return list(rows[-1][1:])
def breast_root(a,z):
 cy,rx,ry=interpolate(BREAST,z);p=Vector((rx*math.sin(a),cy-ry*math.cos(a),z))
 n=Vector((math.sin(a)/rx,-math.cos(a)/ry,0)).normalized()
 return p,n

def apply(scene,root_path=None,era='builder'):
 if any(o.get('cgSupervisedBody04') for o in scene.objects):raise RuntimeError('Reload frozen cycle03 before applying body04')
 old=list(scene.objects);hidden=[];made=[]
 # Select graphs by semantic family/role, never material name.
 mats={}
 for o in old:
  if o.type!='MESH':continue
  try:families=json.loads(o.get('cgSurfaceFamilies','[]'))
  except (ValueError,TypeError):families=[]
  for i,f in enumerate(families):
   if i<len(o.data.materials) and o.data.materials[i]:mats.setdefault(f,o.data.materials[i])
 for family,roles in {'breast-armor':('armor','plate'),'wing-armor':('armor',),'black-iron':('inner',),'worn-bronze':('bearing','rivet'),'machined-steel':('shaft','steel')}.items():
  if family not in mats:
   mats[family]=next((o.data.materials[0] for o in old if o.type=='MESH' and o.data.materials and o.get('surfaceRole') in roles),None)
 if any(mats.get(f) is None for f in ('breast-armor','wing-armor','black-iron','worn-bronze','machined-steel')):raise RuntimeError('Missing receiving semantic graph')
 for o in old:
  if o.type!='MESH' or o.hide_render:continue
  n=o.name
  superseded=(o.get('cgSupervisedNeck03') and ('leaf' in n)) or (o.get('cgSupervisedShield03') and any(t in n for t in ('hard leaf','root recessed race','root metal lip','radial saddle')))
  if superseded:
   o.hide_render=True;o.hide_set(True);o['cgBody04Retained']=True;hidden.append(n)
 coll=bpy.data.collections.new('CG body04 regional formed metal');scene.collection.children.link(coll)
 def mesh(name,vs,fs,families,indices=None,region='body',uvs=None):
  d=bpy.data.meshes.new(name);d.from_pydata(vs,[],fs);d.update()
  o=bpy.data.objects.new('CGB04 '+name,d);coll.objects.link(o)
  for key,value in {'cgSupervisedBody04':True,'cg1cRegion':region,'cg2bRegion':region,'surfaceRole':families[0],'cgSurfaceFamilies':json.dumps(families),'exteriorEras':'maker,mechanic,builder','cgConstructionStatus':'Source-directed CG inference; unaccepted; no engineering'}.items():o[key]=value
  for f in families:d.materials.append(mats[f])
  layer=d.uv_layers.new(name='body04-local-formed-uv')
  for p in d.polygons:
   p.use_smooth=False;p.material_index=indices[p.index] if indices else 0
   for li in p.loop_indices:
    v=d.loops[li].vertex_index;layer.data[li].uv=uvs[v] if uvs else (vs[v][1],vs[v][2])
  bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(d);bm.free()
  made.append(o);return o
 def plate(name,root,normal,down,width,length,family,region,twist=0,dihedral=7,gap=.005,return_depth=.006):
  n=Vector(normal).normalized();v=Vector(down);v=(v-n*v.dot(n)).normalized();u=v.cross(n).normalized()
  # Local azimuth offset produces different plates rather than a shared pillow.
  angle=math.radians(twist);u,v=u*math.cos(angle)+v*math.sin(angle),v*math.cos(angle)-u*math.sin(angle)
  root=Vector(root);slope=math.tan(math.radians(dihedral));vs=[];uv=[]
  # Curved root occupies only first 12%; remaining two broad hard faces meet at
  # a genuine central crease. Taper and bent free-end return are explicit.
  stations=[(0,.80,-.004),(.065,.94,-.001),(.14,1,0),(.72,.83,gap*.72),(.94,.37,gap),(1,.08,gap-return_depth)]
  for t,w,bend in stations:
   for q in (-.5,0,.5):
    x=q*width*w;depth=bend-abs(x)*slope
    vs.append(tuple(root+u*x+v*(t*length)+n*depth));uv.append((q+.5,t))
  # True sheet thickness follows the separate hard-face vertex normal average.
  topcount=len(vs);fs=[];ids=[]
  for j in range(len(stations)-1):
   for k in range(2):a=j*3+k;fs.append((a,a+1,a+4,a+3));ids.append(0)
  normals=[Vector((0,0,0)) for _ in vs]
  for f in fs:
   nn=(Vector(vs[f[1]])-Vector(vs[f[0]])).cross(Vector(vs[f[3]])-Vector(vs[f[0]])).normalized()
   if nn.dot(n)<0:nn=-nn
   for i in f:normals[i]+=nn
  thickness=.0026
  vs += [tuple(Vector(p)-nn.normalized()*thickness) for p,nn in zip(vs,normals)];uv+=uv[:]
  for f in fs[:]:fs.append(tuple(i+topcount for i in reversed(f)));ids.append(1)
  border=[0,1,2]+[j*3+2 for j in range(1,len(stations))]+[topcount-2,topcount-3]+[j*3 for j in range(len(stations)-2,0,-1)]
  for a,b in zip(border,border[1:]+border[:1]):fs.append((a,a+topcount,b+topcount,b));ids.append(1)
  o=mesh(name,vs,fs,[family,'black-iron'],ids,region,uv)
  bevel=o.modifiers.new('metal cut edge bevel','BEVEL');bevel.width=.0006;bevel.segments=1
  o['sheetThickness']=thickness;o['localDihedralDegrees']=dihedral;o['freeEndGap']=gap;o['plateRoot']=list(root);o['plateNormal']=list(n)
  return o
 # Breast: broad uneven framing courses with a connected oblique left channel.
 # Preserve rounded overall volume with individually canted hard planes.
 breastcourses=[(1.31,.100,[(-.06,.082),(.52,.089),(1.02,.073)]),(1.26,.13,[(-.15,.087),(.34,.096),(.83,.09)]),(1.19,.14,[(-.35,.098),(.10,.11),(.56,.106),(1.00,.082)]),(1.115,.15,[(-.38,.101),(.08,.112),(.56,.108),(1.02,.076)]),(1.04,.145,[(-.42,.104),(.03,.111),(.51,.104),(.98,.084)]),(.965,.14,[(-.59,.09),(-.13,.107),(.34,.104),(.82,.089)]),(.892,.13,[(-.65,.078),(-.16,.102),(.37,.096),(.92,.072)]),(.825,.084,[(-.61,.063),(-.04,.081),(.59,.076)])]
 for row,(z,length,entries) in enumerate(breastcourses):
  for col,(a,w) in enumerate(entries):
   zz=z+.006*math.sin(col*2+row);p,n=breast_root(a,zz)
   # Independent vertical pitch approximates regional breast section slopes.
   before,_=breast_root(a,zz-.008);after,_=breast_root(a,zz+.008);down=(before-after).normalized()
   n=down.cross(Vector((math.cos(a),math.sin(a),0))).normalized()
   if n.dot(Vector((math.sin(a),-math.cos(a),0)))<0:n=-n
   plate(f'breast framing {row}-{col}',p+n*(.014+(7-row)*.0008),n,down,w,length,'breast-armor','body',twist=(-5 if col%2 else 5),dihedral=6+row%3,gap=.006)
 # Narrow unequal neck laminae flank open receiver/link channel. Rear neck uses
 # fewer coarse plates; head junction stays below z1.56.
 for row,z in enumerate((1.556,1.510,1.464,1.419,1.374,1.330)):
  for col,a in enumerate((-.28,.35,.92,1.70,2.50,3.30,4.05)):
   p,n=breast_root(a,z);w=.048 if row<3 else .062
   plate(f'cervical lamina {row}-{col}',p+n*.013,n,(.02,-.025,-1),w,.071 if row<3 else .082,'breast-armor','neck',twist=4*(-1 if col%2 else 1),dihedral=7,gap=.004,return_depth=.004)
 # Left/right channel-edge framing hugs mechanism; no full circular collar.
 for side in (-1,1):
  for j,(z,a,w,l) in enumerate(((1.45,1.02,.035,.09),(1.36,1.12,.043,.112),(1.26,1.08,.052,.13),(1.15,1.02,.066,.142),(1.04,1.04,.065,.13),(.94,1.08,.06,.115))):
   a*=side;p,n=breast_root(a,z)
   plate(f'{side} receiver channel rim {j}',p+n*.010,n,(side*.10,-.02,-1),w,l,'breast-armor','neck' if z>1.33 else 'body',twist=side*8,dihedral=5,gap=.004)
 # Shield root placement follows compact projected border. Each local face is
 # independent of the guide; lower blades lengthen and turn backward.
 courses=[(1.377,3,.045,.047),(1.350,5,.052,.064),(1.318,6,.064,.086),(1.277,6,.076,.103),(1.230,6,.084,.116),(1.180,5,.095,.128),(1.126,5,.096,.125),(1.071,4,.091,.106),(1.021,2,.082,.071)]
 for side in (-1,1):
  for row,(z,count,width,length) in enumerate(courses):
   f,r,x,b=interpolate(WING,z)
   for col in range(count):
    fraction=(col+.5)/count;y=f+(r-f)*fraction+.004*math.sin(row+col*2)
    q=2*fraction-1;normal=Vector((side,-.38*q,.14 if row<3 else .06)).normalized()
    root=Vector((side*(x+b*math.sqrt(max(.02,1-q*q))+.009),y,z))
    down=Vector((0,.27+.22*fraction,-1))
    plate(f'{side} shield hard blade {row}-{col}',root,normal,down,width*(.94+.08*math.sin(col*1.7)),length,'wing-armor','wing',twist=3*math.sin(row+col),dihedral=6+col%4,gap=.005)
  # Coverts bury the complete top/front shoulder race, previously detached ears.
  for j,(y,z,w,l) in enumerate(((-.20,1.352,.073,.093),(-.245,1.300,.070,.106),(-.265,1.245,.059,.099))):
   plate(f'{side} anterior shoulder covert {j}',(side*.29,y,z),(side,-.28,.18),(0,.18,-1),w,l,'wing-armor','wing',twist=-9,dihedral=8,gap=.004)
 bpy.context.view_layer.update()
 return {'module':'cg-supervised-body04','era':era,'newMeshes':len(made),'retainedHidden':hidden,'method':'Independent local frames; 2 hard longitudinal faces; bent root and tapered return; per-normal thickness','sheetThickness':.0026,'bevel':.0006,'dihedralDegrees':[5,9],'freeEndGaps':[.004,.006],'overlapProposal':'20-35% longitudinal; varies at silhouette','surfaceGraphs':'Receiving semantic role/family graph copies; no material-name dependence','limits':['Unaccepted source-directed proposal','Source-specific plate outlines and exact metal response remain approximate','Rear unseen geometry inferred','Receiving head, leg, foot and anchors unchanged','Root owns finish and browser integration']}

def digest(o):
 h=hashlib.sha256();data=[[tuple(r) for r in o.matrix_world]]
 if o.type=='MESH':data += [[tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],[(u.name,[tuple(v.uv) for v in u.data]) for u in o.data.uv_layers],[m.name if m else None for m in o.data.materials],[p.material_index for p in o.data.polygons]]
 for v in data:h.update(repr(v).encode())
 return h.hexdigest()
def diagnostic():
 p=argparse.ArgumentParser();p.add_argument('--input-root',required=True);p.add_argument('--attempt',default='attempt01');p.add_argument('--resolution',type=int,default=800);p.add_argument('--samples',type=int,default=12);args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
 root=Path(__file__).resolve().parents[4];inp=Path(args.input_root);out=root/'assets/audit/cg-supervised-body04'/args.attempt;out.mkdir(parents=True,exist_ok=True)
 source=inp/'assets/models/cg-supervised01/attempt03/murderbird-supervised-builder.blend';ref=inp/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
 assert sha(source)==SOURCE_SHA;assert sha(ref)==REF_SHA
 bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
 frozen={o.name:digest(o) for o in s.objects if o.type in ('MESH','EMPTY')};visibility={o.name:o.hide_render for o in s.objects if o.type=='MESH'}
 s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=args.samples;s.cycles.use_denoising=True;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
 prior=json.loads((inp/'assets/audit/cg-supervised01/attempt03/builder/receipt.json').read_text());cam=s.camera;cameras={};initiallights={o.name:(o.location.copy(),o.rotation_euler.copy(),o.data.energy,o.data.color[:],o.data.size) for o in s.objects if o.type=='LIGHT'}
 clay=bpy.data.materials.new('Body04 diagnostic clay');clay.diffuse_color=(.34,.34,.34,1);clay.use_nodes=True;clay.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.64
 def render(name,view='whole',claypass=False,grazing=False):
  q=prior['cameras']['canon-neutral'];cam.location=q['location'];cam.rotation_euler=q['rotation_euler'];cam.data.type='ORTHO';cam.data.ortho_scale=q['ortho_scale'];cam.data.shift_x,cam.data.shift_y=q['shift']
  s.render.resolution_x=args.resolution;s.render.resolution_y=round(args.resolution*853/1280)
  if view!='whole':
   position={'side':(-6,0,1.2),'front':(0,-6,1.2),'body':(-6,-2.4,1.5)}[view];target=(0,-.045,1.17);cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.00;cam.data.shift_x=cam.data.shift_y=0;s.render.resolution_y=args.resolution
  s.view_layers[0].material_override=clay if claypass else None
  for o in s.objects:
   if o.type!='LIGHT':continue
   loc,rot,power,color,size=initiallights[o.name];o.location=loc;o.rotation_euler=rot;o.data.energy=power;o.data.color=color;o.data.size=size
  if grazing:
   lights=[o for o in s.objects if o.type=='LIGHT'];lights[0].location=(-1,-.8,2.5);lights[0].rotation_euler=(Vector((0,0,1.1))-lights[0].location).to_track_quat('-Z','Y').to_euler();lights[0].data.size=.28;lights[0].data.energy=140
   for o in lights[1:]:o.data.energy*=.18
  cameras[name]={'location':list(cam.location),'rotation_euler':list(cam.rotation_euler),'scale':cam.data.ortho_scale,'shift':[cam.data.shift_x,cam.data.shift_y],'resolution':[s.render.resolution_x,s.render.resolution_y],'clay':claypass,'lights':[{'name':o.name,'location':list(o.location),'rotation':list(o.rotation_euler),'power':o.data.energy,'color':list(o.data.color),'size':o.data.size} for o in s.objects if o.type=='LIGHT']}
  s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 render('before-whole-clay',claypass=True);render('before-whole-pbr');result=apply(s,inp,'builder')
 render('after-whole-clay',claypass=True);render('after-body-grazing-clay','body',True,True);render('after-front-clay','front',True);render('after-side-clay','side',True);render('after-whole-pbr');render('after-body-pbr','body')
 s.view_layers[0].material_override=None
 changed=[n for n,d in frozen.items() if digest(s.objects[n])!=d];unexpected=[n for n,v in visibility.items() if s.objects[n].hide_render!=v and n not in result['retainedHidden']];assert not changed and not unexpected,(changed,unexpected)
 bpy.context.preferences.filepaths.save_version=0;native=out/'murderbird-body04.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native));nativehash=sha(native)
 bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;changedreadback=[n for n,d in frozen.items() if digest(bpy.context.scene.objects[n])!=d];assert not changedreadback
 result.update(sourceSHA256=sha(source),sourceBinaryPreserved=sha(source)==SOURCE_SHA,referenceSHA256=sha(ref),nativeSHA256=nativehash,originalMeshesAndAnchorsChecked=len(frozen),receivingGeometryUVMaterialIndicesTransformsChanged=changed,savedNativePreservationReadback=changedreadback,unexpectedVisibilityChanges=unexpected,cameras=cameras,renderSettings={'engine':'CYCLES','samples':args.samples,'denoise':True,'viewTransform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure},images={f.name:sha(f) for f in out.glob('*.png')},status='Unaccepted CG proposal; likeness not established')
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print('BODY04_COMPLETE',out)
if __name__=='__main__':diagnostic()
