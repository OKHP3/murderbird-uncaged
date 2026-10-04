import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
root=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');base=root/'assets/audit/cg-recursive-three-loop01/loop01/delivery/retained02/builder';p=base/'murderbird-recursive-builder.blend';h=hashlib.sha256(p.read_bytes()).hexdigest();assert h=='7539b8968f9e82cc8c1dfb569203bd60b134ba841871b99bf67124552fd7004d';bpy.ops.wm.open_mainfile(filepath=str(p));s=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();r={'nativeSHA256':h,'meshEmptyCount':sum(o.type in ('MESH','EMPTY') for o in s.objects),'materialCount':len(bpy.data.materials),'packedFileCount':sum(i.source=='FILE' and bool(i.packed_file) for i in bpy.data.images),'objects':[],'frontRayRows':[],'allMeshEmptyNames':[o.name for o in s.objects if o.type in ('MESH','EMPTY')],'cameraLightNames':[o.name for o in s.objects if o.type in ('CAMERA','LIGHT')]}
prior=json.loads((root/'assets/audit/cg-supervised01/attempt09/builder/receipt.json').read_text());q=prior['cameras']['neutral-000'];c=s.camera;c.location=q['location'];c.rotation_euler=q['rotation_euler'];c.data.type=q['projection'];c.data.ortho_scale=q['ortho_scale'];c.data.shift_x,c.data.shift_y=q['shift'];s.render.resolution_x,s.render.resolution_y=q['resolution'];s.render.resolution_percentage=100;bpy.context.view_layer.update();width,height=q['resolution']
for o in s.objects:
 if o.type!='MESH':continue
 ev=o.evaluated_get(deps);md=ev.to_mesh();co=[o.matrix_world@v.co for v in md.vertices];zs=[x.z for x in co]
 interesting=o.get('cgRecursiveBody01') or o.get('cgSupervisedBody12') or (not o.hide_render and (o.get('cg1cRegion') in ('body','wing','legs','feet') or o.name.startswith(('CGH','CGN','CGS'))))
 if interesting:
  bb={'min':[min(x[i] for x in co) for i in range(3)],'max':[max(x[i] for x in co) for i in range(3)]};pts=[world_to_camera_view(s,c,x) for x in co];r['objects'].append(dict(name=o.name,visible=not o.hide_render,bounds=bb,modifiers=[dict(name=m.name,type=m.type,thickness=getattr(m,'thickness',None),offset=getattr(m,'offset',None)) for m in o.modifiers],properties=dict(o.items()),frontPixels=dict(min=[min(t.x for t in pts)*width,(1-max(t.y for t in pts))*height],max=[max(t.x for t in pts)*width,(1-min(t.y for t in pts))*height]),materials=[m.name if m else None for m in o.data.materials]))
 ev.to_mesh_clear()
# Orthographic front pixel rays. Original camera receipt size1000x666 mapped rows normalized.
rot=c.matrix_world.to_quaternion();forward=rot@Vector((0,0,-1));right=rot@Vector((1,0,0));up=rot@Vector((0,1,0));vertical=c.data.ortho_scale*height/width;horizontal=c.data.ortho_scale
for yn in [.405,.42,.435,.45,.465,.48,.495,.51]:
 row=[]
 for xn in [.46,.475,.49,.5,.51,.525,.54]:
  origin=c.location+right*((xn-.5)*horizontal)+up*((.5-yn)*vertical);hit,loc,n,idx,obj,matrix=s.ray_cast(deps,origin,forward,distance=30);row.append(dict(x=xn,y=yn,object=obj.name if hit else None,point=list(loc) if hit else None,face=idx))
 r['frontRayRows'].append(row)
Path('/tmp/cg-recursive-body02-native-inspection.json').write_text(json.dumps(r,indent=2,default=str));assert hashlib.sha256(p.read_bytes()).hexdigest()==h;print('READONLY_BODY_INSPECTION',r['meshEmptyCount'],r['materialCount'],r['packedFileCount'],len(r['objects']))
