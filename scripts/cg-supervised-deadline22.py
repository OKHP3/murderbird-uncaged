"""One coupled segmented crown/cheek/throat proposal; exact09 receiving native."""
import bpy,json,math,hashlib,importlib.util,datetime
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]; O=R/'assets/audit/cg-supervised-deadline22'; A=R/'assets/models/cg-supervised-deadline22';O.mkdir(parents=True,exist_ok=True);A.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
I=R/'assets/models/cg-supervised01/attempt09/murderbird-supervised-builder.blend';assert sha(I)=='c39a2fefcc9b4d277540a0406522e69b06975c14a0b8e281f183d1fca20dc2fc'
def load(n):
 s=importlib.util.spec_from_file_location(n,R/'scripts'/n);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
bpy.ops.wm.open_mainfile(filepath=str(I));S=bpy.context.scene;P=load('cg-supervised-preservation.py');D=load('cg-supervised-head17.py');before=D.snap();imgs=P.packed_image_snapshot();F=S.objects['CG2b head frame'].matrix_world.copy();M=list(S.objects['CGH06 swept overlapping dorsal brow plate L0'].data.materials);made=[];over={}
rc=json.loads((R/'assets/audit/cg-supervised01/attempt09/builder/receipt.json').read_text())['cameras']['canon-neutral']; C=S.camera
C.location=rc['location'];C.rotation_euler=rc['rotation_euler'];C.data.type=rc['projection'];C.data.ortho_scale=rc['ortho_scale'];C.data.shift_x,C.data.shift_y=rc['shift'];C.data.lens=rc['lens_mm']
S.world.node_tree.nodes['Background'].inputs[0].default_value=rc['world_color'];S.world.node_tree.nodes['Background'].inputs[1].default_value=rc['world_strength']
for o,sp in zip([o for o in S.objects if o.type=='LIGHT'],rc['areas']):
 o.location=sp['location'];o.rotation_euler=sp['rotation_euler'];o.data.energy=sp['power'];o.data.color=sp['color'];o.data.size=sp['size']
S.render.engine='CYCLES';S.cycles.device='CPU';S.cycles.samples=3;S.cycles.use_denoising=True;S.render.threads_mode='FIXED';S.render.threads=2;S.render.resolution_x=640;S.render.resolution_y=427;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG'
clay=bpy.data.materials.new('D22 diagnostic clay');clay.use_nodes=True;b=clay.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(.42,.42,.42,1);b.inputs['Roughness'].default_value=.75
report={'input':str(I.relative_to(R)),'input_sha256':sha(I),'design':'Segmented curved saddle scales flow around exposed optic into overlapping descending cheek lamellae and a narrow throat fan. Curvature and real gaps replace large continuous pale cap. Inferred depth/layout; no source tracing claim. One design, no polish retry.','source_sha256':sha(R/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg'),'july_head_sha256':sha(R/'context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png'),'status':'partial construction test; final and three-era acceptance not claimed','camera':rc,'render':{'samples':3,'resolution':[640,427],'device':'CPU','threads':2},'overrides':over,'new_objects':made}
def receipt(): (O/'receipt.json').write_text(json.dumps(report,indent=2))
def render(n,cl=False):
 S.view_layers[0].material_override=clay if cl else None;S.render.filepath=str(O/(n+'.png'));bpy.context.view_layer.update();bpy.ops.render.render(write_still=True);print('D22_RENDERED',S.render.filepath,flush=True);receipt()
render('before-pbr-whole');render('before-clay-whole',True)
for o in S.objects:
 if o.get('cgSupervisedHead17') and not o.hide_render:over[o.name]=[o.hide_render,o.hide_get()];o.hide_render=True;o.hide_set(True)
def mesh(n,vs,fs,frame=F):
 d=bpy.data.meshes.new('D22 '+n);d.from_pydata(vs,[],fs);d.update();o=bpy.data.objects.new(d.name,d);S.collection.objects.link(o);o.matrix_world=frame.copy();o['cgDeadline22']=True;o['constructionStatus']='Source-inspired coupled formed-metal proposal'
 for m in M:d.materials.append(m)
 uv=d.uv_layers.new(name='d22 local');lo=[min(v.co[a] for v in d.vertices) for a in (1,2)];hi=[max(v.co[a] for v in d.vertices) for a in (1,2)]
 for p in d.polygons:
  p.use_smooth=True
  for li in p.loop_indices:
   q=d.vertices[d.loops[li].vertex_index].co;uv.data[li].uv=((q.y-lo[0])/max(hi[0]-lo[0],1e-6),(q.z-lo[1])/max(hi[1]-lo[1],1e-6))
 z=o.modifiers.new('formed plate','SOLIDIFY');z.thickness=.0022;z.offset=-1;z.material_offset=1;z.material_offset_rim=2;v=o.modifiers.new('rolled edges','BEVEL');v.width=.0007;v.segments=2;made.append(o.name)
# Four transverse rows, each broken into overlapping curved scales, sweep crown to bill root.
for row,(y,z,w) in enumerate([(.16,.19,.118),(.075,.169,.145),(-.005,.147,.144),(-.08,.097,.116)]):
 for col in range(5):
  u0=-1+col*.4;vs=[]
  for j in range(9):
   t=j/8
   for k in range(7):
    u=u0+(k/6)*.48; taper=1-.40*t; x=w*(u0+.24)+(u-(u0+.24))*w*taper;yy=y+.095*t-.016*math.sin(math.pi*t);zz=z-.015*t-.046*(x/w)**2+.009*math.sin(math.pi*t);vs.append((x,yy,zz))
  mesh('crown scale %s %s'%(row,col),vs,[(j*7+k,j*7+k+1,(j+1)*7+k+1,(j+1)*7+k) for j in range(8) for k in range(6)])
# Side strips are broad curved lamellae, with tapered lower endpoints and staggered gaps.
for side in [-1,1]:
 for j in range(5):
  y=.155-.045*j;z=-.012-.023*j;vs=[]
  for a in range(12):
   t=a/11
   for b in range(7):
    u=b/6*2-1;ww=.034*(1-.65*t);yy=y-.035*t+.018*math.sin(math.pi*t)+u*ww;zz=z-.15*t+.022*u;xx=side*(.163-.037*t+.009*(1-u*u)+.007*math.sin(math.pi*t));vs.append((xx,yy,zz))
  mesh('descending cheek lamella %s %s'%(side,j),vs,[(a*7+b,a*7+b+1,(a+1)*7+b+1,(a+1)*7+b) for a in range(11) for b in range(6)])
# Under-jaw forward throat courses stay above breast, following current neck envelope.
for row in range(3):
 for col in range(3):
  vs=[]
  for j in range(9):
   t=j/8
   for k in range(7):
    x=(col-1)*.063+(k/6-.5)*.085*(1-.40*t);y=-.10-.015*row-.025*t-.05*(1-(x/.16)**2);z=-.17-.068*row-.10*t+.006*math.sin(math.pi*t);vs.append((x,y,z))
  mesh('throat fan %s %s'%(row,col),vs,[(j*7+k,j*7+k+1,(j+1)*7+k+1,(j+1)*7+k) for j in range(8) for k in range(6)])
S.view_layers[0].material_override=None;P.retain_packed_image_ids(S);bpy.context.preferences.filepaths.save_version=0;N=A/'murderbird-deadline22.blend';bpy.ops.wm.save_as_mainfile(filepath=str(N),relative_remap=False)
after=D.snap();report['preservation']={'packed':P.verify_receiving_images(imgs),'object_changes':[n for n,h in before['objects'].items() if after['objects'].get(n)!=h],'material_changes':[n for n,h in before['materials'].items() if after['materials'].get(n)!=h]};assert not report['preservation']['object_changes'] and not report['preservation']['material_changes'];report['native_sha256']=sha(N);receipt()
render('after-pbr-whole');render('after-clay-whole',True)
print('D22_FIRST_WHOLE_COMPLETE',flush=True)
