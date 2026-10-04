"""Thin curved regional feathers for integrated04; CG proposal, not engineering.
API apply(scene, root_path=None, era='builder'). Receiving meshes are hidden,
never modified. Body/neck/shield construction only; head and stance protected.
"""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy, bmesh
from mathutils import Vector

SOURCE_SHA='72e7e53daf40b7128cdf9b173006c639bcf123952547a2576fb2de29130f06d4'
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
 if any(o.get('cgSupervisedBody07') for o in scene.objects):raise RuntimeError('Reload completed06 before applying body07')
 old=list(scene.objects);hidden=[];made=[]
 # Select graphs by semantic family/role, never material name.
 mats={}
 for o in sorted(old,key=lambda o: (o.hide_render,not bool(o.get('cgSupervisedBody05')))):
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
  superseded=o.get('cgSupervisedBody05') and o.get('cg2bRegion') in ('body','neck','wing')
  if superseded:
   o.hide_render=True;o.hide_set(True);hidden.append(n)
 coll=bpy.data.collections.new('CG body07 neighboring root overlaps');scene.collection.children.link(coll)
 def mesh(name,vs,fs,families,indices=None,region='body',uvs=None):
  d=bpy.data.meshes.new(name);d.from_pydata(vs,[],fs);d.update()
  o=bpy.data.objects.new('CGB07 '+name,d);coll.objects.link(o)
  for key,value in {'cgSupervisedBody05':True,'cgSupervisedBody07':True,'cgBodyUVConvention':'body05 normalized local q,t; covered roots clamp t=0','cg1cRegion':region,'cg2bRegion':region,'surfaceRole':families[0],'cgSurfaceFamilies':json.dumps(families),'exteriorEras':'maker,mechanic,builder','cgConstructionStatus':'Source-directed CG inference; unaccepted; no engineering'}.items():o[key]=value
  for f in families:d.materials.append(mats[f])
  layer=d.uv_layers.new(name='body05-local-curved-uv')
  for p in d.polygons:
   p.use_smooth=(indices[p.index]==0) if indices else True;p.material_index=indices[p.index] if indices else 0
   for li in p.loop_indices:
    v=d.loops[li].vertex_index;layer.data[li].uv=uvs[v] if uvs else (vs[v][1],vs[v][2])
  bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(d);bm.free()
  made.append(o);return o
 def plate(name,root,normal,down,width,length,family,region,twist=0,curvature=2.5,gap=.0022,camber=.0015):
  """Each feather is its own smooth curved sheet in an independent tangent frame.
  The shallow crown falls toward edges; no root ridge, stand-off block, shared
  balloon or broad hard V. Curve, taper, cant and course placement are editable.
  """
  n=Vector(normal).normalized();v=Vector(down);v=(v-n*v.dot(n)).normalized();u=v.cross(n).normalized()
  a=math.radians(twist);u,v=u*math.cos(a)+v*math.sin(a),v*math.cos(a)-u*math.sin(a)
  root=Vector(root);vs=[];uv=[];ns=17;nq=9
  # Continuous asymmetric rounded feather outline, tapering more at the tip.
  for j in range(ns):
   t=-.20+1.20*j/(ns-1)
   tt=max(0,t)
   w=.83+.17*math.sin(math.pi*min(1,tt/.72)) if tt<.37 else max(.025,(1-((tt-.37)/.63)**1.35))
   for k in range(nq):
    q=2*k/(nq-1)-1
    x=.5*q*width*w*(1+.04*math.sin(t*math.pi)*q)
    # A smooth transverse crown, mild longitudinal convexity, shallow root.
    # The free end sits close to its under-course rather than projecting away.
    depth=camber*(1-q*q)*math.sin(math.pi*(.18+.72*t)) + gap*t - .5*length*math.tan(math.radians(curvature))*t*t
    vs.append(tuple(root+u*x+v*(t*length)+n*depth));uv.append(((q+1)*.5,max(0,t)))
  fs=[];ids=[]
  for j in range(ns-1):
   for k in range(nq-1):
    i=j*nq+k;fs.append((i,i+1,i+1+nq,i+nq));ids.append(0)
  normals=[Vector((0,0,0)) for _ in vs]
  for f in fs:
   nn=(Vector(vs[f[1]])-Vector(vs[f[0]])).cross(Vector(vs[f[3]])-Vector(vs[f[0]])).normalized()
   if nn.dot(n)<0:nn=-nn
   for i in f:normals[i]+=nn
  nt=len(vs);thickness=.0018
  vs += [tuple(Vector(p)-nn.normalized()*thickness) for p,nn in zip(vs,normals)];uv+=uv[:]
  for f in fs[:]:fs.append(tuple(i+nt for i in reversed(f)));ids.append(1)
  border=list(range(nq))+[j*nq+nq-1 for j in range(1,ns)]+list(range(nt-2,nt-nq-1,-1))+[j*nq for j in range(ns-2,0,-1)]
  for a,b in zip(border,border[1:]+border[:1]):fs.append((a,a+nt,b+nt,b));ids.append(1)
  o=mesh(name,vs,fs,[family,'black-iron'],ids,region,uv)
  bevel=o.modifiers.new('shallow formed metal edge','BEVEL');bevel.width=.0004;bevel.segments=2
  o['sheetThickness']=thickness;o['localCurvatureDegrees']=curvature;o['freeEndGap']=gap;o['plateRoot']=list(root);o['plateDown']=list(v);o['plateAcross']=list(u);o['plateWidth']=width;o['plateLength']=length;o['coveredRootExtensionFraction']=.20;o['plateNormal']=list(n);o['transverseCamber']=camber
  return o
 # Twelve shorter staggered breast courses follow the existing rounded envelope.
 # Source channel boundaries remain open; plates frame and connect them.
 for row in range(12):
  z=1.355-row*.047
  for col,a in enumerate((-1.09,-.37,-.08,.21,.50,.79,1.08)):
   a += .055*(-1 if row%2 else 1)+.018*math.sin(row+col)
   zz=z+.0025*math.sin(col*2+row);p,n=breast_root(a,zz)
   before,_=breast_root(a,zz-.008);after,_=breast_root(a,zz+.008);down=(before-after).normalized()
   n=down.cross(Vector((math.cos(a),math.sin(a),0))).normalized()
   if n.dot(Vector((math.sin(a),-math.cos(a),0)))<0:n=-n
   _,rx,ry=interpolate(BREAST,zz)
   width=(.055 if row<2 else .080 if row<9 else .070)*(1+.055*math.sin(col*1.7+row))
   length=(.098 if row<2 else .116 if row<9 else .105)*(1+.04*math.cos(col+row))
   plate(f'breast curved feather {row:02d}-{col}',p+n*(.008+(11-row)*.00035),n,down,width,length,'breast-armor','body',twist=3*math.sin(row+col),camber=.0015)
 # Narrow continuous laminae from upper neck into breast; spare the head join.
 for row in range(10):
  z=1.551-row*.025
  for col,a in enumerate((-1.08,-.34,.17,.68,1.85,2.38,2.91,3.44,3.98,4.52)):
   a+=.055*(-1 if row%2 else 1);p,n=breast_root(a,z)
   w=(.041 if row<5 else .048)*(1+.05*math.sin(col+row))
   plate(f'cervical curved lamina {row:02d}-{col}',p+n*(.008+(9-row)*.0002),n,(.008,-.010,-1),w,.061 if row<5 else .077,'breast-armor','neck',twist=3*math.sin(col+row),gap=.0017,camber=.0008)
 # Connected curved frames skirt the existing gear channel rather than seal it.
 for side in (-1,1):
  for j in range(11):
   z=1.49-j*.047;a=side*(1.06+.035*math.sin(j*.6));p,n=breast_root(a,z)
   plate(f'{side} channel edge curved lamina {j:02d}',p+n*.007,n,(side*.04,-.01,-1),.036 if j<3 else .045,.069 if j<4 else .083,'breast-armor','neck' if z>1.33 else 'body',twist=side*3,gap=.0017,camber=.0010)
 # Eleven fine shield courses. Compact silhouette is retained. Subtle cant and
 # graduated outlines make individually formed feathers, not upright root tiles.
 courses=[(1.380,4,.034,.037),(1.358,6,.044,.048),(1.328,7,.056,.066),(1.292,7,.064,.089),(1.252,6,.073,.121),(1.208,6,.076,.147),(1.163,5,.080,.168),(1.117,4,.084,.160),(1.073,3,.081,.127),(1.033,2,.073,.092),(.999,2,.056,.054)]
 for side in (-1,1):
  for row,(z,count,width,length) in enumerate(courses):
   f,r,x,b=interpolate(WING,z)
   for col in range(count):
    fraction=(col+.50+.14*(-1 if row%2 else 1))/count
    y=f+(r-f)*fraction+.0015*math.sin(row+col*2);q=2*fraction-1
    curve=math.sqrt(max(.02,1-q*q))
    def point_at(zz):
     ff,rr,xx,bb=interpolate(WING,zz)
     return Vector((side*(xx+bb*curve),ff+(rr-ff)*fraction,zz))
    down=(point_at(z-.006)-point_at(z+.006)).normalized()
    across=Vector((-side*2*b*q/curve,r-f,0)).normalized()
    normal=down.cross(across).normalized()
    if normal.x*side<0:normal=-normal
    root=point_at(z)+normal*(.006+(10-row)*.0002)
    root.y+=.0015*math.sin(row+col*2)
    plate(f'{side} shield curved feather {row:02d}-{col}',root,normal,down,width*(.96+.07*math.sin(col*1.7+row)),length*(1+.045*math.sin(col+row)),'wing-armor','wing',twist=7*math.sin(row+col*.7)+(-side*4 if row>3 else 0),curvature=1.4,gap=.0030 if row>3 else .0017,camber=.0015 if row>2 else .0007)
  for j,(y,z,w,l) in enumerate(((-.048,1.370,.034,.033),(-.09,1.349,.037,.040),(-.135,1.320,.044,.048),(-.177,1.284,.047,.055))):
   f,r,x,b=interpolate(WING,z);q=max(-1,min(1,2*(y-f)/(r-f)-1));xx=x+b*math.sqrt(max(.02,1-q*q))+.004
   ff,rr,xp,bp=interpolate(WING,z-.006);ff,rr,xn,bn=interpolate(WING,z+.006)
   down=Vector((side*(xp+bp*math.sqrt(max(.02,1-q*q))-xn-bn*math.sqrt(max(.02,1-q*q))),.002,-.012)).normalized()
   normal=down.cross(Vector((0,1,0))).normalized()
   if normal.x*side<0:normal=-normal
   plate(f'{side} small shoulder covert {j}',(side*xx,y,z),normal,down,w,l,'wing-armor','wing',twist=-3,camber=.0007,gap=.0015)
 # Fit covered lateral roots to actual neighboring sheet edges. No common shell.
 # Edge-to-edge intersections are solved in each sheet's tangent coordinates;
 # the center half-width of each gap is allocated to each adjacent plate.
 from mathutils.geometry import intersect_line_line
 overlap_records=[]
 groups={}
 for o in made:
  if 'shield curved feather' in o.name or 'breast curved feather' in o.name or 'cervical curved lamina' in o.name:
   token=o.name.rsplit(' ',1)[-1];row=int(token.split('-')[0]);group=(o.get('cg2bRegion'),o.name.split(' shield')[0] if 'shield' in o.name else 'front',row)
   groups.setdefault(group,[]).append(o)
 for group,leaves in groups.items():
  for left,right in zip(leaves,leaves[1:]):
   # Source machinery corridor is intentionally excluded from lateral joining.
   if group[0] in ('neck','body') and (Vector(left['plateRoot'])-Vector(right['plateRoot'])).length>.095:continue
   updates=0;distances=[]
   for j in range(8):
    il=j*9+8;ir=j*9
    lp=left.data.vertices[il].co.copy();rp=right.data.vertices[ir].co.copy()
    # Orient the nearest sides from the actual sheet vertices, not name order.
    candidates=[(a,b) for a in (j*9,j*9+8) for b in (j*9,j*9+8)]
    il,ir=min(candidates,key=lambda ab:(left.data.vertices[ab[0]].co-right.data.vertices[ab[1]].co).length)
    lp=left.data.vertices[il].co.copy();rp=right.data.vertices[ir].co.copy()
    u=Vector(left['plateAcross']);v=Vector(right['plateDown'])
    hit=intersect_line_line(lp-u*.3,lp+u*.3,rp-v*.3,rp+v*.3)
    if hit is None:continue
    gap=rp-lp;seam=(lp+rp)*.5
    if gap.length>max(left['plateWidth'],right['plateWidth'])*.80:continue
    # Covered root flare follows measured neighboring seam, fading before tip.
    weight=1-j/8;extension=min(.022,gap.length*.54)*weight
    if extension<.0004:continue
    direction=gap.normalized()
    for obj,idx,sign in ((left,il,1),(right,ir,-1)):
     nn=Vector(obj['plateNormal']);delta=direction*extension*sign;delta-=nn*delta.dot(nn)
     obj.data.vertices[idx].co+=delta;obj.data.vertices[idx+153].co+=delta
     # Interpolate inner q samples to avoid a narrow stretched edge strip.
     end=idx%9;rowstart=idx-end
     for k in range(1,8):
      factor=(k/8)**3 if end==8 else ((8-k)/8)**3
      obj.data.vertices[rowstart+k].co+=delta*factor;obj.data.vertices[rowstart+k+153].co+=delta*factor
     obj.data.update()
    updates+=1;distances.append(gap.length)
   overlap_records.append({'pair':[left.name,right.name],'coveredRowsFitted':updates,'measuredEdgeGaps':distances})
 bpy.context.view_layer.update()
 return {'module':'cg-supervised-body07','neighborFits':overlap_records,'era':era,'newMeshes':len(made),'retainedHidden':hidden,'method':'Independent smooth curved local sheets; continuous taper and shallow roots; normal-direction thickness; twelve breast and eleven shield courses','sheetThickness':.0018,'bevel':.0004,'localCurvatureDegrees':2.5,'freeEndGaps':[.0015,.0022],'overlapProposal':'Actual neighboring edge intersections extend covered root seams only; lower free ends retain independent tangent sheets, elongated sweep and gaps','surfaceGraphs':'Ordered breast-armor/wing-armor plus black-iron thickness slots inherited from receiving graphs; root owns finish04 rerouting','limits':['Unaccepted source-directed proposal','Exact source outlines and connected mechanical channels remain approximate','Rear unseen geometry inferred','Receiving head, leg, foot and anchors unchanged','Root owns finish and browser integration']}

def digest(o):
 h=hashlib.sha256();data=[[tuple(r) for r in o.matrix_world]]
 if o.type=='MESH':data += [[tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],[(u.name,[tuple(v.uv) for v in u.data]) for u in o.data.uv_layers],[m.name if m else None for m in o.data.materials],[p.material_index for p in o.data.polygons]]
 for v in data:h.update(repr(v).encode())
 return h.hexdigest()
def diagnostic():
 p=argparse.ArgumentParser();p.add_argument('--input-root',required=True);p.add_argument('--attempt',default='attempt01');p.add_argument('--resolution',type=int,default=800);p.add_argument('--samples',type=int,default=6);args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
 root=Path(__file__).resolve().parents[1];inp=Path(args.input_root);out=root/'assets/audit/cg-supervised-body07'/args.attempt;out.mkdir(parents=True,exist_ok=True)
 source=inp/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend';ref=inp/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
 assert sha(source)==SOURCE_SHA;assert sha(ref)==REF_SHA
 bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
 frozen={o.name:digest(o) for o in s.objects if o.type in ('MESH','EMPTY')};visibility={o.name:o.hide_render for o in s.objects if o.type=='MESH'}
 s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=args.samples;s.cycles.use_denoising=True;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
 prior=json.loads((inp/'assets/audit/cg-supervised01/attempt06/builder/receipt.json').read_text());cam=s.camera;cameras={};initiallights={o.name:(o.location.copy(),o.rotation_euler.copy(),o.data.energy,o.data.color[:],o.data.size) for o in s.objects if o.type=='LIGHT'}
 clay=bpy.data.materials.new('Body05 diagnostic clay');clay.diffuse_color=(.34,.34,.34,1);clay.use_nodes=True;clay.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.64;clay.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.23,.23,.23,1)
 def render(name,view='whole',claypass=False,grazing=False):
  q=json.loads((inp/'assets/audit/cg-supervised-camera04/receipt.json').read_text())['hypotheses']['ortho-35']['camera'];cam.location=q['location'];cam.rotation_euler=q['rotation_euler'];cam.data.type='ORTHO';cam.data.ortho_scale=q['ortho_scale'];cam.data.shift_x,cam.data.shift_y=q['shift']
  s.render.resolution_x=args.resolution;s.render.resolution_y=round(args.resolution*853/1280)
  if view!='whole':
   position={'side':(-6,0,1.2),'front':(0,-6,1.2),'body':(-6,-2.4,1.5)}[view];target=(0,-.045,1.17);cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.00;cam.data.shift_x=cam.data.shift_y=0;s.render.resolution_y=round(args.resolution*853/1280)
  s.view_layers[0].material_override=clay if claypass else None
  for o in s.objects:
   if o.type!='LIGHT':continue
   loc,rot,power,color,size=initiallights[o.name];o.location=loc;o.rotation_euler=rot;o.data.energy=power;o.data.color=color;o.data.size=size
  if grazing:
   lights=[o for o in s.objects if o.type=='LIGHT'];lights[0].location=(-1,-.8,2.5);lights[0].rotation_euler=(Vector((0,0,1.1))-lights[0].location).to_track_quat('-Z','Y').to_euler();lights[0].data.size=.28;lights[0].data.energy=140
   for o in lights[1:]:o.data.energy*=.18
  cameras[name]={'location':list(cam.location),'rotation_euler':list(cam.rotation_euler),'scale':cam.data.ortho_scale,'shift':[cam.data.shift_x,cam.data.shift_y],'resolution':[s.render.resolution_x,s.render.resolution_y],'clay':claypass,'lights':[{'name':o.name,'location':list(o.location),'rotation':list(o.rotation_euler),'power':o.data.energy,'color':list(o.data.color),'size':o.data.size} for o in s.objects if o.type=='LIGHT']}
  s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 render('before-whole-pbr');render('before-whole-clay',claypass=True);result=apply(s,inp,'builder');render('after-whole-pbr');render('after-whole-clay',claypass=True)
 for stage in ('before','after'):
  for o in s.objects:
   if o.get('cgSupervisedBody07'):o.hide_render=stage=='before'
   elif o.name in result['retainedHidden']:o.hide_render=stage=='after'
  render(stage+'-body-grazing-clay','body',True,True);render(stage+'-front-clay','front',True);render(stage+'-side-clay','side',True);render(stage+'-body-pbr','body')
 s.view_layers[0].material_override=None
 for i in range(8):
  a=math.radians(i*45);target=Vector((0,-.04,1));cam.location=target+Vector((6*math.sin(a),-6*math.cos(a),1.02));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.15;cam.data.shift_x=cam.data.shift_y=0;s.render.resolution_x=640;s.render.resolution_y=427
  name=f'turn-{i*45:03d}';s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);cameras[name]={'location':list(cam.location),'rotation':list(cam.rotation_euler),'scale':cam.data.ortho_scale,'resolution':[640,640]}
 render('after-whole-pbr')
 s.view_layers[0].material_override=None
 changed=[n for n,d in frozen.items() if digest(s.objects[n])!=d];unexpected=[n for n,v in visibility.items() if s.objects[n].hide_render!=v and n not in result['retainedHidden']];assert not changed and not unexpected,(changed,unexpected)
 bpy.context.preferences.filepaths.save_version=0;native=out/'murderbird-body07.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native));nativehash=sha(native)
 bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;finite=[]
 for o in s.objects:
  if not o.get('cgSupervisedBody07'):continue
  assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
  assert all(math.isfinite(c) and -.00001<=c<=1.00001 for uv in o.data.uv_layers for v in uv.data for c in v.uv)
  ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());md=ev.to_mesh();assert all(math.isfinite(c) for v in md.vertices for c in v.co);finite.append({'name':o.name,'vertices':len(md.vertices),'evaluatedFinite':True,'normalizedUV':True});ev.to_mesh_clear()
 changedreadback=[n for n,d in frozen.items() if digest(bpy.context.scene.objects[n])!=d];assert not changedreadback
 result.update(finiteEvaluatedGeometryAndUV=finite,receivingMaterialFamilies={f:mats for f,mats in []},sourceSHA256=sha(source),sourceBinaryPreserved=sha(source)==SOURCE_SHA,referenceSHA256=sha(ref),nativeSHA256=nativehash,originalMeshesAndAnchorsChecked=len(frozen),receivingGeometryUVMaterialIndicesTransformsChanged=changed,savedNativePreservationReadback=changedreadback,unexpectedVisibilityChanges=unexpected,cameras=cameras,renderSettings={'engine':'CYCLES','samples':args.samples,'denoise':True,'viewTransform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure},images={f.name:sha(f) for f in out.glob('*.png')},status='Unaccepted CG proposal; likeness not established')
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print('BODY07_COMPLETE',out)
if __name__=='__main__':diagnostic()
