"""Compact hard feather sheets and connected lateral flank, visual proposal only.
API apply(scene, root_path=None, era='builder') on preserved attempt01 native.
"""
import argparse, hashlib, json, math, sys
from pathlib import Path
import bpy, bmesh
from mathutils import Vector

SECTIONS=[(.945,.115,.192,.246,.009),(1.005,.002,.249,.255,.040),
 (1.075,-.099,.261,.238,.094),(1.155,-.178,.253,.221,.134),
 (1.235,-.205,.218,.205,.147),(1.310,-.180,.147,.191,.121),
 (1.365,-.100,.077,.178,.079),(1.393,-.025,.014,.170,.025)]
SOURCE_SHA='e5fc6a39662bcb7f5ab82679dd719757edc4f0f39fc3cc5ae433bae962409d43'
REF_SHA='645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114'

def section(z):
 z=max(SECTIONS[0][0],min(SECTIONS[-1][0],z))
 for a,b in zip(SECTIONS,SECTIONS[1:]):
  if a[0]<=z<=b[0]:
   t=(z-a[0])/(b[0]-a[0]);t=t*t*(3-2*t)
   return [a[i]*(1-t)+b[i]*t for i in range(1,5)]
 return SECTIONS[-1][1:]

def apply(scene,root_path=None,era='builder'):
 if any(o.get('cgSupervisedShield03') for o in scene.objects):raise RuntimeError('Reload frozen native before applying shield03')
 old=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and o.get('cgSupervisedShoulder') and o.get('cg2bRegion')=='wing']
 if not old:raise RuntimeError('Frozen attempt01 shoulder geometry required')
 armor=next(o.data.materials[0] for o in old if o.get('surfaceRole')=='armor')
 def mat(role):return next((o.data.materials[0] for o in scene.objects if o.type=='MESH' and o.data.materials and o.get('surfaceRole')==role),armor)
 mats={'wing-armor':armor,'black-iron':mat('inner'),'worn-bronze':mat('rivet'),'steel':mat('shaft')}
 coll=bpy.data.collections.new('CG shield03 hard sheets and lateral mechanism');scene.collection.children.link(coll)
 made=[];hidden=[]
 for o in old:
  if 'compact shield recess' in o.name:continue
  o.hide_render=True;o.hide_set(True);hidden.append(o.name)
 def mesh(name,vs,fs,families,indices=None,smooth=False,uvs=None):
  d=bpy.data.meshes.new(name);d.from_pydata(vs,[],fs);d.update()
  o=bpy.data.objects.new(name,d);coll.objects.link(o)
  o['cgSupervisedShield03']=True;o['cg1cRegion']='wing';o['cg2bRegion']='wing'
  o['surfaceRole']=families[0];o['cgSurfaceFamilies']=json.dumps(families)
  o['detailStatus']='CG source-alignment proposal; no engineered fit or owner acceptance'
  o['exteriorEras']='maker,mechanic,builder'
  for f in families:d.materials.append(mats[f])
  layer=d.uv_layers.new(name='shield03-editable-uv')
  for p in d.polygons:
   p.use_smooth=smooth and (indices is None or indices[p.index]==0);p.material_index=indices[p.index] if indices else 0
   for li in p.loop_indices:
    v=d.loops[li].vertex_index;layer.data[li].uv=uvs[v] if uvs else (vs[v][1],vs[v][2])
  bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(d);bm.free()
  made.append(o);return o
 def point(side,y,z,lift=0):
  f,r,x,b=section(z);q=max(-1,min(1,(y-(f+r)/2)/max(.02,(r-f)/2)))
  return Vector((side*(x+b*math.sqrt(max(.02,1-q*q))+lift),y,z))
 def leaf(side,row,col,y,z,width,length,sweep):
  # Two longitudinal strips create a shallow folded metal crease, no puffy dome.
  # The free end stands proud of the following root, opening a genuine shadow gap.
  samples=[(0,.36),(.18,.49),(.43,.50),(.68,.42),(.84,.30),(.96,.14),(1,.015)]
  vs=[];uv=[]
  direction=Vector((sweep,-length));cross=Vector((-direction.y,direction.x)).normalized()
  for t,w in samples:
   for u in (-w,0,w):
    yy=y+t*sweep+u*width*cross.x;zz=z-t*length+u*width*cross.y
    lift=.003+(8-row)*.0017+.010*t+(.0018 if u==0 else 0)*math.sin(math.pi*t)
    p=point(side,yy,zz,lift);vs.append(tuple(p));uv.append((u+.5,t))
  n=len(vs);vs += [(x-side*.0022,y,z) for x,y,z in vs];uv += list(uv)
  fs=[];ids=[]
  for k in range(len(samples)-1):
   for j in range(2):
    a=k*3+j;fs.append((a,a+1,a+4,a+3));ids.append(0)
    fs.append((n+a+3,n+a+4,n+a+1,n+a));ids.append(1)
  border=[0,1,2]+[k*3+2 for k in range(1,len(samples))]+[len(samples)*3-2,len(samples)*3-3]+[k*3 for k in reversed(range(1,len(samples)-1))]
  for a,b in zip(border,border[1:]+border[:1]):fs.append((a,n+a,n+b,b));ids.append(2)
  o=mesh(f'CG shield03 {side:+d} hard leaf {row:02d}-{col:02d}',vs,fs,['wing-armor','black-iron','worn-bronze'],ids,True,uv)
  o['plateCourse']=row;o['sheetThickness']=.0022;o['distalStandOff']=.010
  bevel=o.modifiers.new('Restrained cut edge','BEVEL');bevel.width=.00035;bevel.segments=1
 def tube(name,points,radius,family):
  vs=[];fs=[];N=12
  for k,p in enumerate(points):
   p=Vector(p);t=(Vector(points[min(k+1,len(points)-1)])-Vector(points[max(0,k-1)])).normalized()
   a=t.cross(Vector((1,0,0)))
   if a.length<.1:a=t.cross(Vector((0,1,0)))
   a.normalize();b=t.cross(a).normalized()
   for j in range(N):vs.append(tuple(p+radius*(a*math.cos(j*2*math.pi/N)+b*math.sin(j*2*math.pi/N))))
  for k in range(len(points)-1):
   for j in range(N):fs.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
  fs += [tuple(reversed(range(N))),tuple(range((len(points)-1)*N,len(points)*N))]
  return mesh(name,vs,fs,[family],smooth=True)
 def cyl(name,a,b,r,fam):return tube(name,[a,b],r,fam)
 def ring(name,side,center,rad,width,depth,fam,start=0,stop=2*math.pi):
  vs=[];fs=[];N=max(6,round((stop-start)*18))
  for x,r in ((center[0],rad),(center[0],rad-width),(center[0]+side*depth,rad),(center[0]+side*depth,rad-width)):
   for i in range(N+1):
    a=start+(stop-start)*i/N;vs.append((x,center[1]+r*math.cos(a),center[2]+r*math.sin(a)))
  q=N+1
  for i in range(N):
   for a,b in ((0,1),(2,0),(1,3),(3,2)):fs.append((a*q+i,a*q+i+1,b*q+i+1,b*q+i))
  fs += [(0,q,3*q,2*q),(N,2*q+N,3*q+N,q+N)]
  return mesh(name,vs,fs,[fam],smooth=False)
 # Vary density, stagger and direction. Widths are actual metres, never a
 # normalized envelope fraction; free ends can retain their own tapered contour.
 courses=[(1.374,3,.042,.046),(1.350,5,.050,.063),(1.319,7,.059,.082),
           (1.284,7,.076,.101),(1.236,7,.080,.115),(1.184,6,.087,.123),
           (1.129,5,.094,.125),(1.074,4,.091,.111),(1.022,2,.084,.072)]
 for side in (-1,1):
  for row,(z,n,w,l) in reversed(list(enumerate(courses))):
   f,r,_,_=section(z-.02)
   for col in range(n):
    fraction=(col+.5)/n;y=f+(r-f)*fraction
    y+=.006*math.sin(col*2.4+row*1.6)
    sweep=(.008 if row<2 else .034+.028*fraction)
    length=l*(1+.08*math.sin(col*2.1+row))
    # At the outside edge, a shorter end keeps the terminal within the rounded envelope.
    if col==n-1:sweep*=.30
    leaf(side,row,col,y,z+.004*math.sin(col+row),w*(1+.1*math.cos(col*1.8+row)),length,sweep)
  # Recessed shoulder-root bearing with separate radial saddle sectors at the
  # anterior shield edge; below/front of wing but outside central breast work.
  root=Vector((side*.275,-.200,1.247))
  ring(f'CG shield03 {side} root recessed race',side,root,.072,.019,.010,'black-iron')
  ring(f'CG shield03 {side} root metal lip',side,root+Vector((side*.011,0,0)),.067,.005,.006,'steel')
  for j in range(8):
   a=j*math.pi/4+.05
   ring(f'CG shield03 {side} radial saddle {j}',side,root+Vector((side*.005,0,0)),.093,.021,.009,'worn-bronze',a,a+.55)
  # Connect shoulder ring to retained hip exterior. Every ram has end eyes,
  # telescoping barrel/shaft, collars and an inset return cable.
  hip=Vector((side*.238,.105,.865))
  for j in range(2):
   a=root+Vector((side*.017,-.015+j*.038,-.068+j*.004))
   b=hip+Vector((side*.004,-.045+j*.032,.035))
   axis=b-a
   cyl(f'CG shield03 {side} flank barrel {j}',a,a+axis*.57,.014,'steel')
   cyl(f'CG shield03 {side} flank piston {j}',a+axis*.44,b,.007,'steel')
   for k,t in enumerate((.08,.48,.58)):
    c=a+axis*t;half=axis.normalized()*.006
    cyl(f'CG shield03 {side} ram collar {j}-{k}',c-half,c+half,.017,'worn-bronze' if k==1 else 'steel')
   for k,c in enumerate((a,b)):
    ring(f'CG shield03 {side} ram eye {j}-{k}',side,c,.022,.007,.013,'steel')
    cyl(f'CG shield03 {side} ram pin {j}-{k}',c-Vector((side*.010,0,0)),c+Vector((side*.021,0,0)),.008,'worn-bronze')
   cable=[]
   for k in range(17):
    t=k/16;p=a.lerp(b,t)+Vector((-side*.014,.020*math.sin(math.pi*t),0));cable.append(tuple(p))
   tube(f'CG shield03 {side} inset connected return hose {j}',cable,.005,'black-iron')
  cyl(f'CG shield03 {side} hip tied cross collar',hip-Vector((0,.034,0)),hip+Vector((0,.044,0)),.010,'steel')
 return {'module':'cg-supervised-shield03','era':era,'newMeshes':len(made),'retainedHidden':hidden,'sheetThickness':.0022,'distalLift':.010,'sourceScope':'Pinned reissued full-bird only; July body excluded','changes':['Thin hard feather sheets with raised free ends and separate dark undersides','Staggered small coverts to medium diagonal lower leaves','Segmented radial root saddle and paired shoulder-to-hip cylinders and cables'],'limits':['Added hardware is visual CG inference only','Original compact backing retained','No front neck, breast, central mechanism, leg or anchor changes','Owner likeness acceptance pending']}

def digest(o):
 h=hashlib.sha256()
 values=[[tuple(r) for r in o.matrix_world]]
 if o.type=='MESH':values += [[tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],[(u.name,[tuple(v.uv) for v in u.data]) for u in o.data.uv_layers],[m.name if m else None for m in o.data.materials],[p.material_index for p in o.data.polygons]]
 for d in values:h.update(repr(d).encode())
 return h.hexdigest()

def diagnostic():
 p=argparse.ArgumentParser();p.add_argument('--input-root',required=True);p.add_argument('--resolution',type=int,default=1000);p.add_argument('--samples',type=int,default=16);p.add_argument('--attempt',default='attempt01');args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
 root=Path(__file__).resolve().parents[1];inp=Path(args.input_root);out=root/'assets/audit/cg-supervised-shield03'/args.attempt;out.mkdir(parents=True,exist_ok=True)
 source=inp/'assets/models/cg-supervised01/attempt01/murderbird-supervised-builder.blend';ref=inp/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg';sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
 assert sha(source)==SOURCE_SHA,'Frozen native pin mismatch';assert sha(ref)==REF_SHA,'Source pin mismatch'
 bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
 frozen={o.name:digest(o) for o in s.objects if o.type in ('MESH','EMPTY')};visibility={o.name:o.hide_render for o in s.objects if o.type=='MESH'}
 s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=args.samples;s.cycles.use_denoising=True;s.render.image_settings.file_format='PNG';s.render.resolution_percentage=100
 receipt=json.loads((inp/'assets/audit/cg-supervised01/attempt01/builder/receipt.json').read_text());cam=s.camera;cameras={}
 def render(name,close=False):
  q=receipt['cameras']['canon-neutral'];cam.location=q['location'];cam.rotation_euler=q['rotation_euler'];cam.data.type='ORTHO';cam.data.ortho_scale=q['ortho_scale'];cam.data.shift_x,cam.data.shift_y=q['shift']
  s.render.resolution_x=args.resolution;s.render.resolution_y=round(args.resolution*2/3)
  if close:
   cam.location=(-4,-1.7,1.72);cam.rotation_euler=(Vector((-.15,.01,1.12))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=.98;cam.data.shift_x=cam.data.shift_y=0;s.render.resolution_y=args.resolution
  cameras[name]={'location':list(cam.location),'rotation':list(cam.rotation_euler),'scale':cam.data.ortho_scale,'shift':[cam.data.shift_x,cam.data.shift_y],'resolution':[s.render.resolution_x,s.render.resolution_y]}
  s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 render('before-whole');render('before-shield-flank',True)
 result=apply(s,inp,'builder');render('after-whole');render('after-shield-flank',True)
 changed=[n for n,d in frozen.items() if digest(s.objects[n])!=d]
 unexpected=[n for n,v in visibility.items() if s.objects[n].hide_render!=v and n not in result['retainedHidden']]
 assert not changed and not unexpected,(changed,unexpected)
 result.update(sourceSHA256=sha(source),sourceBinaryPreserved=sha(source)==SOURCE_SHA,referenceSHA256=sha(ref),originalsChecked=len(frozen),geometryUVTransformsMaterialAssignmentsChanged=changed,emptyAnchorsChecked=sum(o.type=='EMPTY' for o in s.objects),unexpectedVisibilityChanges=unexpected,cameras=cameras,lighting='Frozen native unchanged; same camera/light before-after',status='Unaccepted CG proposal; no engineering fit')
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(out/'murderbird-shield03.blend'));result['nativeSHA256']=sha(out/'murderbird-shield03.blend');result['images']={f.name:sha(f) for f in out.glob('*.png')}
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print('SHIELD03_COMPLETE',out)
if __name__=='__main__':diagnostic()
