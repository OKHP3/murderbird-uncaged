import bpy,json,hashlib,math,time
from pathlib import Path
from mathutils import Vector,Matrix
from bpy_extras.object_utils import world_to_camera_view
# Read-only custody/first-hit primitives from the fresh reviewer; no baseline replay.
prefix=Path('/tmp/cg-qc17-head-native.py').read_text().split('bpy.ops.wm.open_mainfile(filepath=str(B));before=snap()')[0]
exec(prefix)
R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');O=R/'assets/audit/cg-supervised-head17';N=O/'attempt02/layered-head17.blend'
manifest=json.loads((O/'frozen-manifest.json').read_text());sources=json.loads((O/'source-hashes.json').read_text());paths=[R/f['path'] for f in manifest['files']]+[O/'frozen-manifest.json']+[R/p for p in sources['inputs']]+[Path('/tmp/cg-ablation17.py')]
paths=list(dict.fromkeys(paths));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pre={str(p):sha(p) for p in paths};assert sha(N)=='f95a7372f1af386ced4c7babda0ed250a99bb3760d6f78659804916ec9a12a2a'
assert all(pre[str(R/f['path'])]==f['sha256'] for f in manifest['files']);assert all(pre[str(R/p)]==h for p,h in sources['inputs'].items())
report={'scope':'HYPOTHETICAL UNSAVED HEAD17 posterior-crest-only omission; no candidate/native/export promotion','native_sha256':sha(N),'input_hashes_before':pre,'render_count':0,'script':'/tmp/cg-ablation17.py','manifest_match_count':len(manifest['files'])}
bpy.ops.wm.open_mainfile(filepath=str(N));s=bpy.context.scene;before=snap();omit=s.objects['CGH17 posterior swept crest'];assert not omit.hide_render
qs={};dg=bpy.context.evaluated_depsgraph_get()
for o in s.objects:
 if 'recessed optical glass' in o.name and not o.hide_render:
  e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();ps=[o.matrix_world@v.co for v in m.vertices];ps.extend(sum((o.matrix_world@m.vertices[i].co for i in f.vertices),Vector())/3 for f in m.loop_triangles);qs[o.name]=ps[::max(1,len(ps)//800)];e.to_mesh_clear()
vs=['source-full-bird','head-profile','head-grazing'];viewref=json.loads((O/'attempt02/receipt.json').read_text())['cameras'];t,owners=tree();base={}
for v in vs:
 setcam(viewref['after-pbr-'+v]);d=s.camera.matrix_world.to_quaternion()@Vector((0,0,-1));base[v]={n:hits(t,owners,p,d) for n,p in qs.items()}
omit.hide_render=True;omit.hide_set(True);bpy.context.view_layer.update();after=snap()
report['in_memory_payload_changes']=[n for n,h in before['objects'].items() if after['objects'].get(n)!=h];report['in_memory_material_changes']=[n for n,h in before['materials'].items() if after['materials'].get(n)!=h];report['in_memory_file_image_changes']=[n for n,h in before['images'].items() if h['source']=='FILE' and after['images'].get(n)!=h];report['in_memory_visibility_changes']=[n for n,h in before['visibility'].items() if after['visibility'].get(n)!=h];assert report['in_memory_visibility_changes']==['CGH17 posterior swept crest'];assert not report['in_memory_payload_changes'] and not report['in_memory_material_changes'] and not report['in_memory_file_image_changes']
verts={};dg=bpy.context.evaluated_depsgraph_get()
for o in s.objects:
 if o.type=='MESH' and not o.hide_render and not o.get('authoringGuide') and max((o.matrix_world@Vector(c)).z for c in o.bound_box)>=1.3:
  e=o.evaluated_get(dg);m=e.to_mesh();verts[o.name]=[o.matrix_world@v.co for v in m.vertices];e.to_mesh_clear()
p,n=max(((p,n) for n,ps in verts.items() for p in ps),key=lambda x:x[0].z);report['actual_highest_world_after_omission']={'owner':n,'xyz':list(p)}
report['retained_new_objects']=[n for n in json.loads((O/'attempt02/receipt.json').read_text())['new_objects'] if not s.objects[n].hide_render]
report['bounds_after_omission']={n:{'min':[min(p[a] for p in ps) for a in range(3)],'max':[max(p[a] for p in ps) for a in range(3)]} for n,ps in verts.items() if n.startswith('CGH17') or ('CGH06' in n and 'posterior' in n)}
t,owners=tree();report['views']={}
s.render.engine='CYCLES';s.cycles.samples=4;s.cycles.use_denoising=True;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_layers[0].material_override=None
report['native_render_state']={'engine':s.render.engine,'samples':s.cycles.samples,'denoising':s.cycles.use_denoising,'device':s.cycles.device,'view_transform':s.view_settings.view_transform,'look':s.view_settings.look,'exposure':s.view_settings.exposure,'gamma':s.view_settings.gamma,'lights':{o.name:{'matrix':list(map(list,o.matrix_world)),'type':o.data.type,'energy':o.data.energy,'color':list(o.data.color)} for o in s.objects if o.type=='LIGHT'}}
for v in vs:
 rc=viewref['after-pbr-'+v];setcam(rc);d=s.camera.matrix_world.to_quaternion()@Vector((0,0,-1));r={}
 for n,ps in qs.items():
  cand=hits(t,owners,ps,d);window=[i for i,h in enumerate(base[v][n]) if h==n];r[n]={'samples':len(ps),'frozen17_glass_first_hit_count':len(window),'after_omission_losses':sum(cand[i]!=n for i in window),'after_omission_glass_first_hit_count':sum(h==n for h in cand)}
 def proj(p):
  z=world_to_camera_view(s,s.camera,p);return [z.x*rc['resolution'][0],(1-z.y)*rc['resolution'][1]]
 top=min(((proj(p),n) for n,ps in verts.items() for p in ps),key=lambda x:x[0][1]);report['views'][v]={'camera':rc,'projected_highest_upper_owner':top[1],'projected_highest_upper_px':top[0],'projection_limit':'evaluated eligible upper vertices; no visibility ray test','optic_first_hits':r,'frozen17_render':str(O/'attempt02'/('after-pbr-'+v+'.png'))}
 path=Path('/tmp/cg-ablation17-'+v+'.png');s.render.filepath=str(path);bpy.ops.render.render(write_still=True);report['render_count']+=1;report['views'][v]['hypothetical_render']=str(path);report['views'][v]['hypothetical_sha256']=sha(path);Path('/tmp/cg-ablation17-native.json').write_text(json.dumps(report,indent=2));print('ABLATION_RENDERED',v,flush=True)
post={str(p):sha(p) for p in paths};report['input_hashes_after']=post;report['disk_input_changes']=[p for p in pre if pre[p]!=post[p]];assert not report['disk_input_changes'];report['native_saved']=False;report['exports']=0;Path('/tmp/cg-ablation17-native.json').write_text(json.dumps(report,indent=2));Path('/tmp/cg-ablation17-hashreceipt.json').write_text(json.dumps({'before':pre,'after':post,'changes':report['disk_input_changes']},indent=2));print('ABLATION_COMPLETE',flush=True)
