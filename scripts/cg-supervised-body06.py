"""Regional thin curved feather hierarchy for completed05; Partial CG proposal; triangular void removal remains failed, not engineering.
API apply(scene, root_path=None, era='builder'). Receiving meshes are hidden,
never modified. Body/neck/shield construction only; head and stance protected.
"""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy, bmesh
from mathutils import Vector

SOURCE_SHA='1c449c25ea48c22cc5e3a1781c26a49ee3268b9170298da2df4c923ed6171cc6'
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
 if any(o.get('cgSupervisedBody06') for o in scene.objects):raise RuntimeError('Reload completed05 before applying body06')
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
  superseded=o.get('cgSupervisedBody05') and o.get('cg2bRegion') in ('body','neck','wing')
  if superseded:
   o.hide_render=True;o.hide_set(True);hidden.append(n)
 coll=bpy.data.collections.new('CG body06 regional formed hierarchy');scene.collection.children.link(coll)
 def mesh(name,vs,fs,families,indices=None,region='body',uvs=None):
  d=bpy.data.meshes.new(name);d.from_pydata(vs,[],fs);d.update()
  o=bpy.data.objects.new('CGB06 '+name,d);coll.objects.link(o)
  for key,value in {'cgSupervisedBody05':True,'cgSupervisedBody06':True,'cgBodyUVConvention':'body05 normalized local q,t on equivalent curved sheets','cg1cRegion':region,'cg2bRegion':region,'surfaceRole':families[0],'cgSurfaceFamilies':json.dumps(families),'exteriorEras':'maker,mechanic,builder','cgConstructionStatus':'Source-directed CG inference; unaccepted; no engineering'}.items():o[key]=value
  for f in families:d.materials.append(mats[f])
  layer=d.uv_layers.new(name='body05-local-curved-uv')
  for p in d.polygons:
   p.use_smooth=(indices[p.index]==0) if indices else True;p.material_index=indices[p.index] if indices else 0
   for li in p.loop_indices:
    v=d.loops[li].vertex_index;layer.data[li].uv=uvs[v] if uvs else (vs[v][1],vs[v][2])
  bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(d);bm.free()
  made.append(o);return o
 def plate(name,root,normal,down,width,length,family,region,twist=0,curvature=3.8,gap=.0007,camber=.0007,guide=None,shape=0):
  """Each feather is its own smooth curved sheet in an independent tangent frame.
  The shallow crown falls toward edges; no root ridge, stand-off block, shared
  balloon or broad hard V. Curve, taper, cant and course placement are editable.
  """
  n=Vector(normal).normalized();v=Vector(down);v=(v-n*v.dot(n)).normalized();u=v.cross(n).normalized()
  a=math.radians(twist);u,v=u*math.cos(a)+v*math.sin(a),v*math.cos(a)-u*math.sin(a)
  root=Vector(root);vs=[];uv=[];ns=17;nq=9
  # Continuous asymmetric rounded feather outline, tapering more at the tip.
  for j in range(ns):
   t=j/(ns-1)
   shoulder=(.40 if region=='body' else .34 if region=='neck' else .24)+.06*math.sin(shape*1.7)
   w=(.82+.18*math.sin(math.pi*min(1,t/.48))) if t<shoulder else max(.020,(1-((t-shoulder)/(1-shoulder))**(1.25+.13*math.sin(shape))))
   for k in range(nq):
    q=2*k/(nq-1)-1
    x=.5*q*width*w*(1+(.045+.025*math.sin(shape))*math.sin(t*math.pi)*q)
    # A smooth transverse crown, mild longitudinal convexity, shallow root.
    # The free end sits close to its under-course rather than projecting away.
    depth=camber*(1-q*q)*math.sin(math.pi*(.18+.72*t)) + gap*t - .5*length*math.tan(math.radians(curvature))*t*t
    center,nn,uu=(root+v*(t*length),n,u) if guide is None else guide(t)
    vs.append(tuple(center+uu*x+nn*depth));uv.append(((q+1)*.5,t))
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
  o['sheetThickness']=thickness;o['localCurvatureDegrees']=curvature;o['freeEndGap']=gap;o['plateRoot']=list(root);o['plateNormal']=list(n);o['transverseCamber']=camber
  return o
 # Distinct graduated coverage uses conforming curved centerlines; every plate
 # remains an editable local sheet. No continuous enclosing mesh is generated.
 def breast_sheet(name,a,z,width,length,region,shape,offset=.0055):
  p,n=breast_root(a,z)
  lo,_=breast_root(a,z-.004);hi,_=breast_root(a,z+.004)
  tangent=(lo-hi).normalized();dz=length/max(1.0,(lo-hi).length/.008)
  def guide(t):
   aa=a+.018*math.sin(shape)*t;pp,nn=breast_root(aa,z-dz*t)
   uu=Vector((math.cos(aa),math.sin(aa),0)).normalized()
   return pp+nn*(offset+.0005*math.sin(math.pi*t)),nn,uu
  return plate(name,p+n*offset,n,tangent,width,length,'breast-armor',region,
       twist=0,gap=.0006,camber=.0007,curvature=0,guide=guide,shape=shape)
 # Finer upper breast graduates from cervical sheets; no level collar ring.
 zs=[1.354,1.325,1.293,1.259,1.224,1.185,1.143,1.098,1.052,1.006,.961,.916,.873,.832]
 for row,z in enumerate(zs):
  angles=(-.99,-.46,-.20,.07,.34,.61,.89,1.10) if row<4 else (-1.02,-.44,-.13,.19,.51,.83,1.10)
  for col,a in enumerate(angles):
   a+=.065*(-1 if row%2 else 1)+.020*math.sin(row*1.3+col*2.1)
   if col==0:a=-1.10+.018*math.sin(row)
   elif col==1:a=-.36+.018*math.sin(row)
   zz=z+.009*math.sin(col*1.8+row*.8)
   width=(.047 if row<2 else .064 if row<4 else .095 if row<9 else .088)*(1+.11*math.sin(col*1.7+row))
   if col<2:width=min(width,.044)
   length=(.060 if row<2 else .075 if row<4 else .095 if row<9 else .087)*(1+.08*math.cos(col*1.3+row))
   breast_sheet(f'breast graduated leaf {row:02d}-{col}',a,zz,width,length,'body',row*2+col,offset=.0047+(13-row)*.00050)
 # Neck sheets taper gradually into small upper breast leaves. a=-.75±.20
 # is the explicit connected-machinery06 channel; no sheets fill this zone.
 for row in range(12):
  z=1.551-row*.0208
  for col,a in enumerate((-.29,.20,.69,1.85,2.38,2.91,3.44,3.98,4.52)):
   a+=.036*math.sin(row*1.1+col)
   w=(.033 if row<5 else .036 if row<9 else .041)*(1+.07*math.sin(col+row))
   breast_sheet(f'cervical graduated lamina {row:02d}-{col}',a,z+.003*math.sin(col+row),w,.046 if row<6 else .060,'neck',row+col,offset=.0047+(11-row)*.00030)
 # Curved channel borders stop just outside -0.95..-0.55, leaving a clear
 # visible crescent for rings, yokes and the connected dark housings.
 for edge,a in enumerate((-1.09,-.41,1.06)):
  for j in range(12):
   z=1.49-j*.043
   breast_sheet(f'channel border {edge}-{j:02d}',a+.015*math.sin(j*.6),z,.024 if j<4 else .035,.060 if j<4 else .082,'neck' if z>1.33 else 'body',j+edge,offset=.0047)
 # Dense fine upper coverts graduate to longer narrow lower shield leaves.
 courses=[(1.381,4,.029,.034),(1.361,6,.035,.043),(1.337,8,.040,.051),(1.309,8,.047,.059),(1.278,8,.052,.070),(1.242,8,.055,.087),(1.204,7,.059,.109),(1.160,7,.060,.122),(1.114,6,.060,.124),(1.070,5,.058,.109),(1.029,4,.054,.091),(.992,3,.048,.067)]
 for side in (-1,1):
  for row,(z,count,width,length) in enumerate(courses):
   for col in range(count):
    fraction=(col+.50+.10*math.sin(row*1.1))/count;q=2*fraction-1
    curve=math.sqrt(max(.02,1-q*q))
    def point_at(zz):
     ff,rr,xx,bb=interpolate(WING,zz)
     return Vector((side*(xx+bb*curve),ff+(rr-ff)*fraction,zz))
    def frame_at(zz):
     ff,rr,xx,bb=interpolate(WING,zz)
     tangent=(point_at(zz-.004)-point_at(zz+.004)).normalized()
     across=Vector((-side*2*bb*q/curve,rr-ff,0)).normalized()
     nn=tangent.cross(across).normalized()
     if nn.x*side<0:nn=-nn
     return tangent,across,nn
    down,across,normal=frame_at(z)
    scale=max(1.,(point_at(z-.004)-point_at(z+.004)).length/.008)
    dz=min(length/scale,max(.022,z-.943))
    off=.0038+(11-row)*.00030
    def guide(t):
     zz=z-dz*t;dd,uu,nn=frame_at(zz)
     return point_at(zz)+nn*off,nn,uu
    plate(f'{side} shield hierarchy leaf {row:02d}-{col}',point_at(z)+normal*off,normal,down,width*1.30*(1+.08*math.sin(col*1.7+row)),length,'wing-armor','wing',twist=0,camber=.0007 if row>3 else .0004,gap=.0006,curvature=0,guide=guide,shape=row*3+col)
 bpy.context.view_layer.update()
 return {'module':'cg-supervised-body06','era':era,'newMeshes':len(made),'retainedHidden':hidden,'method':'Independent thin curved sheets with conforming centerlines; fine upper coverts, longer tapered lower shields and graduated cervical/breast leaves; explicit -0.75±0.20 machinery channel','sheetThickness':.0018,'bevel':.0004,'localCurvatureDegrees':0,'freeEndGaps':[.0006],'overlapProposal':'Graduated conforming courses; observed upper triangular voids remain failed, lower sheets sometimes merge visually; editable CG inference','surfaceGraphs':'Ordered breast-armor/wing-armor plus black-iron thickness slots inherited from receiving graphs; root owns finish04 rerouting','limits':['Unaccepted source-directed proposal','Exact source outlines and connected mechanical channels remain approximate','Rear unseen geometry inferred','Receiving head, leg, foot and anchors unchanged','Root owns finish and browser integration']}

def digest(o):
 h=hashlib.sha256();data=[[tuple(r) for r in o.matrix_world],o.parent.name if o.parent else None,[(k,repr(o[k])) for k in sorted(o.keys())],o.hide_viewport]
 if o.type=='MESH':data += [[tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],[(u.name,[tuple(v.uv) for v in u.data]) for u in o.data.uv_layers],[m.name if m else None for m in o.data.materials],[p.material_index for p in o.data.polygons],[(a.name,a.domain,a.data_type,[tuple(d.color) for d in a.data]) for a in o.data.color_attributes],[tuple(v.normal) for v in o.data.vertices]]
 for v in data:h.update(repr(v).encode())
 return h.hexdigest()
def diagnostic():
 p=argparse.ArgumentParser();p.add_argument('--input-root',required=True);p.add_argument('--attempt',default='attempt01');p.add_argument('--resolution',type=int,default=800);p.add_argument('--samples',type=int,default=6);args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
 root=Path(__file__).resolve().parents[1];inp=Path(args.input_root);out=root/'assets/audit/cg-supervised-body06'/args.attempt;out.mkdir(parents=True,exist_ok=True)
 source=inp/'assets/models/cg-supervised01/attempt05/murderbird-supervised-builder.blend';ref=inp/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
 assert sha(source)==SOURCE_SHA;assert sha(ref)==REF_SHA
 bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
 frozen={o.name:digest(o) for o in s.objects if o.type in ('MESH','EMPTY')};visibility={o.name:o.hide_render for o in s.objects if o.type=='MESH'}
 s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=args.samples;s.cycles.use_denoising=True;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
 prior=json.loads((inp/'assets/audit/cg-supervised01/attempt05/builder/receipt.json').read_text());cam=s.camera;cameras={};initiallights={o.name:(o.location.copy(),o.rotation_euler.copy(),o.data.energy,o.data.color[:],o.data.size) for o in s.objects if o.type=='LIGHT'}
 clay=bpy.data.materials.new('Body06 diagnostic clay');clay.diffuse_color=(.34,.34,.34,1);clay.use_nodes=True;clay.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.64;clay.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.23,.23,.23,1)
 def render(name,view='whole',claypass=False,grazing=False):
  q=json.loads((inp/'assets/audit/cg-supervised-camera04/receipt.json').read_text())['hypotheses']['ortho-35']['camera'];cam.location=q['location'];cam.rotation_euler=q['rotation_euler'];cam.data.type='ORTHO';cam.data.ortho_scale=q['ortho_scale'];cam.data.shift_x,cam.data.shift_y=q['shift']
  s.render.resolution_x=args.resolution;s.render.resolution_y=round(args.resolution*853/1280)
  if view!='whole':
   position={'side':(-6,0,1.2),'front':(0,-6,1.2),'body':(-6,-2.4,1.5)}[view];target=(0,-.045,1.17);cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=1.00;cam.data.shift_x=cam.data.shift_y=0
  s.view_layers[0].material_override=clay if claypass else None
  for o in s.objects:
   if o.type!='LIGHT':continue
   loc,rot,power,color,size=initiallights[o.name];o.location=loc;o.rotation_euler=rot;o.data.energy=power;o.data.color=color;o.data.size=size
  if grazing:
   lights=[o for o in s.objects if o.type=='LIGHT'];lights[0].location=(-1,-.8,2.5);lights[0].rotation_euler=(Vector((0,0,1.1))-lights[0].location).to_track_quat('-Z','Y').to_euler();lights[0].data.size=.28;lights[0].data.energy=140
   for o in lights[1:]:o.data.energy*=.18
  cameras[name]={'location':list(cam.location),'rotation_euler':list(cam.rotation_euler),'scale':cam.data.ortho_scale,'shift':[cam.data.shift_x,cam.data.shift_y],'resolution':[s.render.resolution_x,s.render.resolution_y],'clay':claypass,'lights':[{'name':o.name,'location':list(o.location),'rotation':list(o.rotation_euler),'power':o.data.energy,'color':list(o.data.color),'size':o.data.size} for o in s.objects if o.type=='LIGHT']}
  s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 render('before-whole-clay',claypass=True);render('before-whole-pbr');render('before-body-grazing-clay','body',True,True);render('before-front-clay','front',True);render('before-side-clay','side',True);render('before-body-pbr','body');result=apply(s,inp,'builder')
 render('after-whole-clay',claypass=True);render('after-body-grazing-clay','body',True,True);render('after-front-clay','front',True);render('after-side-clay','side',True);render('after-whole-pbr');render('after-body-pbr','body')
 s.view_layers[0].material_override=None
 for i in range(8):
  a=math.radians(i*45);target=Vector((0,-.04,1));cam.location=target+Vector((6*math.sin(a),-6*math.cos(a),1.02));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2.15;cam.data.shift_x=cam.data.shift_y=0;s.render.resolution_x=640;s.render.resolution_y=427
  name=f'turn-{i*45:03d}';s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);cameras[name]={'location':list(cam.location),'rotation':list(cam.rotation_euler),'scale':cam.data.ortho_scale,'resolution':[640,427]}
 render('after-whole-pbr')
 s.view_layers[0].material_override=None
 changed=[n for n,d in frozen.items() if digest(s.objects[n])!=d];unexpected=[n for n,v in visibility.items() if s.objects[n].hide_render!=v and n not in result['retainedHidden']];assert not changed and not unexpected,(changed,unexpected)
 bpy.context.preferences.filepaths.save_version=0;native=out/'murderbird-body06.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native));nativehash=sha(native)
 bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;finite=[]
 for o in s.objects:
  if not o.get('cgSupervisedBody06'):continue
  assert o.type=='MESH'
  assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
  assert all(math.isfinite(c) and -.00001<=c<=1.00001 for uv in o.data.uv_layers for v in uv.data for c in v.uv)
  ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());md=ev.to_mesh()
  assert all(math.isfinite(c) for v in md.vertices for c in v.co)
  finite.append({'name':o.name,'vertices':len(md.vertices),'normalizedUV':True,'evaluatedFinite':True})
  ev.to_mesh_clear()
 changedreadback=[n for n,d in frozen.items() if digest(bpy.context.scene.objects[n])!=d];assert not changedreadback
 result.update(sourceSHA256=sha(source),sourceBinaryPreserved=sha(source)==SOURCE_SHA,referenceSHA256=sha(ref),nativeSHA256=nativehash,originalMeshesAndAnchorsChecked=len(frozen),receivingGeometryUVMaterialIndicesTransformsChanged=changed,savedNativePreservationReadback=changedreadback,unexpectedVisibilityChanges=unexpected,cameras=cameras,renderSettings={'engine':'CYCLES','samples':args.samples,'denoise':True,'viewTransform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure},images={f.name:sha(f) for f in out.glob('*.png')},finiteAttributesAndEvaluatedMeshes=finite,status='Unaccepted CG proposal; likeness not established')
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print('BODY06_COMPLETE',out)
if __name__=='__main__':diagnostic()
