"""Successor lower-breast construction on loaded09. Import-safe, original payloads retained."""
import argparse, hashlib, importlib.util, json, math, sys
from pathlib import Path
import bpy, bmesh
from mathutils import Vector
ROOT=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
SHA09='c39a2fefcc9b4d277540a0406522e69b06975c14a0b8e281f183d1fca20dc2fc'
REF='645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114'
SECTIONS=[(1.37,-.321,.176,.180),(1.28,-.397,.234,.272),(1.15,-.442,.286,.353),(1.02,-.403,.276,.333),(.89,-.304,.222,.249),(.80,-.195,.132,.167)]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(root,name):
 p=Path(root)/'scripts'/name;s=importlib.util.spec_from_file_location(name.replace('-','_'),p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def apply(scene,root_path=None,era='builder',design=2):
 if any(o.get('cgRecursiveBody01') for o in scene.objects):raise RuntimeError('Reload09 before applying')
 mats={};sources={}
 for o in scene.objects:
  if o.type=='MESH' and o.get('cgSupervisedBody05'):
   for i,f in enumerate(json.loads(o.get('cgSurfaceFamilies','[]'))):
    if i<len(o.data.materials) and o.data.materials[i]:mats.setdefault(f,o.data.materials[i]);sources.setdefault(f,dict(object=o.name,slot=i,material=o.data.materials[i].name))
 hidden={}
 for o in scene.objects:
  if o.type!='MESH' or o.hide_render or not(o.get('cgSupervisedBody12') or o.get('cgSupervisedBody15')):continue
  zs=[(o.matrix_world@v.co).z for v in o.data.vertices]
  if min(zs)<1.335:
   hidden[o.name]=dict(before=[o.hide_render,o.hide_viewport,o.hide_get()],after=[True,o.hide_viewport,True]);o.hide_render=True;o.hide_set(True)
 assert hidden
 coll=bpy.data.collections.new('Recursive BODY01 rounded short-course successor');scene.collection.children.link(coll)
 def surface(a,z):
  for i in range(len(SECTIONS)-1):
   z0,y0,x0,d0=SECTIONS[i];z1,y1,x1,d1=SECTIONS[i+1]
   if z>=z1:break
  t=max(0,min(1,(z0-z)/(z0-z1)));t=t*t*(3-2*t);y=y0*(1-t)+y1*t;rx=x0*(1-t)+x1*t;depth=d0*(1-t)+d1*t
  if design==2:y+=.007*math.sin(math.pi*(z-.8)/.57);rx*=.975
  return Vector((rx*math.sin(a),y+depth*(1-math.cos(a)),z))
 records=[]
 # Staggered short metal courses: oblique side tracks, rounded corner/free edge.
 tracks=[(-1.12,-.76),(-.81,-.43),(-.48,-.09),(-.14,.25),(.20,.59),(.54,.91),(.86,1.12)]
 if design==2:tracks=[(-1.12,-.70),(-.76,-.31),(-.38,.10),(.025,.48),(.41,.85),(.78,1.12)]
 for col,(left,right) in enumerate(tracks):
  ends=[1.37,1.30,1.225,1.15,1.075,1.00,.925,.855,.80]
  if design==2:
   ends=[[1.37,1.28,1.17,1.075,.965,.875,.80],[1.37,1.255,1.145,1.045,.94,.855,.80],[1.37,1.29,1.185,1.075,.97,.865,.80],[1.37,1.25,1.155,1.05,.955,.85,.80],[1.37,1.28,1.17,1.06,.965,.875,.80],[1.37,1.255,1.145,1.035,.945,.85,.80]][col]
  for row,(top,bot) in enumerate(zip(ends,ends[1:])):
   stagger=(.012 if col%2 else -.006)*math.sin(math.pi*row/8);top+=stagger;bot+=stagger
   if row:top+=.019
   if row<7:bot-=.007
   verts=[];uv=[];nu,nv=9,11
   for j in range(nv):
    v=j/(nv-1)
    for i in range(nu):
     u=i/(nu-1);rounding=.07*(abs(2*v-1)**6)
     if design==2:rounding=.065*(abs(2*v-1)**6)+.135*v**4
     a=left+(right-left)*(rounding+(1-2*rounding)*u)
     sweep=.105*math.sin(math.pi*(1.37-top)/.57)*(1 if col>=3 else -1)
     if design==2:sweep=(.16+.06*(row%3))*math.sin(math.pi*(1.37-top)/.57)*(1 if col>=3 else -1)
     a+=sweep*v
     # Side plates turn obliquely into rounded breast, no elongated pointed bib.
     z=top+(bot-top)*v+.009*(2*u-1)*(col-3)/3*math.sin(math.pi*v)+.009*abs(2*u-1)**4*v**5
     if design==2:
      z+=.035*(2*u-1)*(1 if col>=3 else -1)*v+.027*abs(2*u-1)**2*v**5-.015*math.sin(math.pi*u)*v**5
      a+=.025*math.sin(math.pi*v)*(1 if (col+row)%2 else -1)
     p=surface(a,max(.80,min(1.37,z)));p.z=z
     da=surface(a+.0001,max(.80,min(1.37,z)))-surface(a-.0001,max(.80,min(1.37,z)));dz=surface(a,min(1.37,z+.0001))-surface(a,max(.80,z-.0001));n=da.cross(dz).normalized();n=-n if n.y>0 else n
     # Root is recessed beneath upper course; convex sheet crest terminates proud.
     p+=n*(-.004+.0045*math.sin(math.pi*u)*math.sin(math.pi*v)+.007*v**3)
     verts.append(tuple(p));uv.append((u,v))
   faces=[(j*nu+i,j*nu+i+1,(j+1)*nu+i+1,(j+1)*nu+i) for j in range(nv-1) for i in range(nu-1)]
   d=bpy.data.meshes.new(f'recursive-body01 short formed metal {col}-{row}');d.from_pydata(verts,[],faces);d.update();o=bpy.data.objects.new(f'CGRB01 rounded course {col}-{row}',d);coll.objects.link(o)
   for f in ('breast-armor','black-iron'):d.materials.append(mats[f])
   layer=d.uv_layers.new(name='recursive-body01-local-across-down')
   for p in d.polygons:
    p.use_smooth=True
    for li in p.loop_indices:layer.data[li].uv=uv[d.loops[li].vertex_index]
   bm=bmesh.new();bm.from_mesh(d);bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
   if sum((f.normal for f in bm.faces),Vector()).y>0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
   bm.to_mesh(d);bm.free();sol=o.modifiers.new('inward metal stock','SOLIDIFY');sol.thickness=.0015;sol.offset=-1;sol.material_offset=sol.material_offset_rim=1
   o['cgRecursiveBody01']=True;o['cg1cRegion']='body';o['surfaceRole']='breast-armor';o['cgConstructionStatus']='Inferred short convex breast courses from locked source; owner acceptance pending';o['exteriorEras']='maker,mechanic,builder';records.append(dict(name=o.name,track=col,course=row,zRoot=top,zEnd=bot))
 bpy.context.view_layer.update()
 return dict(module='cg-recursive-body01',era=era,design=design,newMeshes=[r['name'] for r in records],hideOverrides=hidden,sections=SECTIONS,panels=records,materialSources=sources,interface='upper throat retained; seam starts1.37 and replaces crossing panels with minz<1.335',status='Unaccepted visual proposal; source depths inferred, estimated camera not calibrated')

def run():
 p=argparse.ArgumentParser();p.add_argument('--input-root',default=str(ROOT));p.add_argument('--era',default='builder');p.add_argument('--design',type=int,default=2);p.add_argument('--resolution',type=int,default=640);p.add_argument('--samples',type=int,default=6);p.add_argument('--expand',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);root=Path(a.input_root);own=Path(__file__).resolve().parents[1];out=own/'assets/audit/cg-recursive-body01'/f'attempt{a.design:02d}'/a.era;asset=own/'assets/models/cg-recursive-body01'/f'attempt{a.design:02d}';out.mkdir(parents=True,exist_ok=True);asset.mkdir(parents=True,exist_ok=True)
 inp=root/'assets/models/cg-supervised01/attempt09'/f'murderbird-supervised-{a.era}.blend';expected={'builder':SHA09,'maker':'5783e79ba3dae12ea21db3d4b70d4973037b30ab91aa108b6635b9d3b96a7769','mechanic':'b8a26a287d73cf6f236b4aa0381aec4a3ef5b1437dee1ea03531b59c3af26fe6'};assert sha(inp)==expected[a.era];assert sha(root/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg')==REF
 bpy.ops.wm.open_mainfile(filepath=str(inp));s=bpy.context.scene;m=load(root,'cg-supervised-body12.py');pres=load(root,'cg-supervised-preservation.py');frozen={o.name:m.digest(o) for o in s.objects if o.type in ('MESH','EMPTY')};graphs=m.material_digest();packed=pres.packed_image_snapshot();vis={o.name:[o.hide_render,o.hide_viewport,o.hide_get()] for o in s.objects};savedRig={o.name:dict(location=list(o.location),rotation=list(o.rotation_euler),scale=list(o.scale),data=dict(type=o.data.type,ortho_scale=o.data.ortho_scale,lens=o.data.lens,shift_x=o.data.shift_x,shift_y=o.data.shift_y) if o.type=='CAMERA' else dict(energy=o.data.energy,color=list(o.data.color),size=o.data.size)) for o in s.objects if o.type in ('CAMERA','LIGHT')};bg=s.world.node_tree.nodes.get('Background');savedWorld=[list(bg.inputs[0].default_value),bg.inputs[1].default_value];prior=json.loads((root/'assets/audit/cg-supervised01/attempt09'/a.era/'receipt.json').read_text());receipt=dict(inputPath=str(inp),inputSHA256=sha(inp),sourceSHA256=REF,cameras={},images={})
 clay=bpy.data.materials.new('Recursive BODY01 diagnostic clay');clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.23,.23,.23,1);bs.inputs['Roughness'].default_value=.64
 def render(name,key,claypass=False):
  q=prior['cameras'][key];c=s.camera;c.location=q['location'];c.rotation_euler=q['rotation_euler'];c.data.type=q['projection'];c.data.ortho_scale=q['ortho_scale'];c.data.lens=q['lens_mm'];c.data.shift_x,c.data.shift_y=q['shift'];b=s.world.node_tree.nodes.get('Background');b.inputs[0].default_value=q['world_color'];b.inputs[1].default_value=q['world_strength'];lights=[o for o in s.objects if o.type=='LIGHT' and o.name.startswith('Supervised area')][-3:]
  for o,l in zip(lights,q['areas']):o.location=l['location'];o.rotation_euler=l['rotation_euler'];o.data.energy=l['power'];o.data.color=l['color'];o.data.size=l['size']
  s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=a.samples;s.cycles.use_denoising=True;s.render.threads_mode='FIXED';s.render.threads=2;s.render.resolution_x=a.resolution;s.render.resolution_y=round(a.resolution*q['resolution'][1]/q['resolution'][0]);s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_layers[0].material_override=clay if claypass else None;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True);actualq=dict(q);actualq['resolution']=[s.render.resolution_x,s.render.resolution_y];actualq['render_settings']=dict(samples=a.samples,CPUThreads=2);receipt['cameras'][name]=actualq;receipt['images'][name+'.png']=sha(out/(name+'.png'));(out/'receipt.json').write_text(json.dumps(receipt,indent=2));print('BODY01_IMAGE',out/(name+'.png'),flush=True)
 for cp in (False,True):render('before-whole-'+('clay' if cp else 'pbr'),'canon-neutral',cp)
 result=apply(s,root,a.era,a.design);receipt['application']=result
 for cp in (False,True):render('candidate-whole-'+('clay' if cp else 'pbr'),'canon-neutral',cp)
 if a.expand:
  for key in ('body-detail','side-profile','neutral-180','neutral-000'):
   render('candidate-'+key,key)
 s.view_layers[0].material_override=None
 for n,q in savedRig.items():
  o=s.objects[n];o.location=q['location'];o.rotation_euler=q['rotation'];o.scale=q['scale']
  for k,v in q['data'].items():setattr(o.data,k,v)
 bg.inputs[0].default_value=savedWorld[0];bg.inputs[1].default_value=savedWorld[1];receipt['cameraLightWorldStateRestoredBeforeSave']=True;pres.retain_packed_image_ids(s);bpy.context.preferences.filepaths.save_version=0;native=asset/f'murderbird-recursive-body-{a.era}.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),relative_remap=False);receipt['nativeSHA256']=sha(native);bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene
 changed=[n for n,d in frozen.items() if not s.objects.get(n) or m.digest(s.objects[n])!=d];aftergraphs=m.material_digest();gchanged=[n for n,d in graphs.items() if aftergraphs.get(n)!=d];vchanged=[n for n,v in vis.items() if n not in result['hideOverrides'] and [s.objects[n].hide_render,s.objects[n].hide_viewport,s.objects[n].hide_get()]!=v];assert not changed and not gchanged and not vchanged,(changed,gchanged,vchanged);assert packed==pres.packed_image_snapshot();assert sha(inp)==receipt['inputSHA256'];receipt['readback']=dict(originalPayloads=len(frozen),changed=changed,materialGraphsChanged=gchanged,visibilityOutsideManifestChanged=vchanged,packedImagesExact=True,sourceBinaryPreserved=True);receipt['originalPayloadDigests']=frozen;receipt['originalMaterialGraphs']=graphs;receipt['packedImages']=packed;receipt['originalVisibility']=vis;(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('BODY01_COMPLETE',out,flush=True)
if __name__=='__main__':run()
