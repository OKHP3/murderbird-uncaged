import bpy,json,hashlib,math,time
from pathlib import Path
R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
P=R/'assets/models/cg-supervised01/attempt07/murderbird-supervised-builder.blend'
report={'hypothetical':True,'description':'ONE core-area ablation: radius6.7 to19.5 source construction units; companion collar and opaque coating central clearance only. No material, emission, pose, outer cavity or retaining-ring changes. Judged native never saved.','native_before_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'changes':[],'light_shape':'SQUARE verified from frozen native; initial DISK test discarded and same geometry re-rendered with corrected fixed recipe'}
bpy.ops.wm.open_mainfile(filepath=str(P),use_scripts=False)
s=bpy.context.scene
# Alter only radial geometry in core and the central clearances blocking it.
for o in s.objects:
 mapping=None
 if o.name.startswith('CGO07 small recessed awakened core '): mapping={6.7:19.5,4.8:4.8*19.5/6.7}
 elif o.name.startswith('CGO07 small core aperture collar '): mapping={10.1:21.0,9.4:20.8,7.5:19.8,6.8:19.6}
 elif o.name.startswith('CGO07 recessed dark curved optical coating '): mapping={18:23,8:20.4}
 if mapping:
  radii=[]
  for v in o.data.vertices:
   dy,dz=v.co.y-.005,v.co.z-.020;r=math.hypot(dy,dz)/.0012
   radii.append(r)
   for old,new in mapping.items():
    if abs(r-old)<.01:
     v.co.y=.005+dy*new/old;v.co.z=.020+dz*new/old;break
  o.data.update()
  report['changes'].append({'object':o.name,'old_radii':sorted(set(round(x,3) for x in radii)),'radial_mapping':mapping,'depth_unchanged':True,'core_UV_unchanged_gradient_stretched':True})
bpy.context.view_layer.update()
receipt=json.loads((R/'assets/audit/cg-supervised01/attempt07/builder/receipt.json').read_text())
# Reconstitute the EXACT frozen workshop/head camera+light recipes; no relight optimization.
for name in ['canon-workshop','head-neck']:
 q=receipt['cameras'][name];c=s.camera;c.location=q['location'];c.rotation_euler=q['rotation_euler'];c.data.type=q['projection'];c.data.ortho_scale=q['ortho_scale'];c.data.shift_x,c.data.shift_y=q['shift'];c.data.lens=q['lens_mm']
 for o in list(s.objects):
  if o.type=='LIGHT':bpy.data.objects.remove(o,do_unlink=True)
 for j,a in enumerate(q['areas']):
  d=bpy.data.lights.new('hypothetical fixed receipt area '+str(j),'AREA');d.energy=a['power'];d.color=a['color'];d.shape='SQUARE';d.size=a['size'];o=bpy.data.objects.new(d.name,d);s.collection.objects.link(o);o.location=a['location'];o.rotation_euler=a['rotation_euler']
 s.world.use_nodes=True;b=s.world.node_tree.nodes.get('Background');b.inputs['Color'].default_value=q['world_color'];b.inputs['Strength'].default_value=q['world_strength']
 s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=12;s.cycles.use_denoising=True
 s.view_settings.view_transform=q['render_settings']['view_transform'];s.view_settings.look=q['render_settings']['look'];s.view_settings.exposure=0;s.view_settings.gamma=1
 s.render.resolution_x,s.render.resolution_y=q['resolution'];s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
 s.render.filepath='/tmp/cg-qa07-HYPOTHETICAL-'+name+'.png';bpy.ops.render.render(write_still=True)
 report[name]={'camera_light_recipe':q,'image':s.render.filepath,'sha256':hashlib.sha256(Path(s.render.filepath).read_bytes()).hexdigest()}
 Path('/tmp/cg-qa07-ablation-receipt.json').write_text(json.dumps(report,indent=2))
report['native_after_sha256']=hashlib.sha256(P.read_bytes()).hexdigest();report['native_unsaved_unchanged']=report['native_after_sha256']==report['native_before_sha256']
Path('/tmp/cg-qa07-ablation-receipt.json').write_text(json.dumps(report,indent=2))
