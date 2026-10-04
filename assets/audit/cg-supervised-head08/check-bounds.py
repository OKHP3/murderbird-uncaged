import bpy,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parents[3];A=R/'assets/audit/cg-supervised-head08';results={}
for attempt in ['attempt01','attempt02']:
 o=A/attempt;r=json.loads((o/'receipt.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(o/'formed-head08.blend'));s=bpy.context.scene;cam=s.camera;c=r['cameras']['after-clay-source-full-bird'];cam.location=c['location'];cam.rotation_euler=c['rotation_euler'];cam.data.ortho_scale=c['ortho_scale'];cam.data.shift_x,cam.data.shift_y=c['shift'];bpy.context.view_layer.update();pts=[];names=[]
 for obj in s.objects:
  if obj.type=='MESH' and not obj.hide_render and (obj.get('cg1cRegion') or obj.get('cg2bRegion')):
   names.append(obj.name)
   pts += [world_to_camera_view(s,cam,obj.matrix_world@Vector(p)) for p in obj.bound_box]
 xs=[v.x for v in pts];ys=[v.y for v in pts];zs=[v.z for v in pts];res={'camera':'global35 unchanged estimated source projection','visible_region_objects':len(names),'normalized_bounds':[min(xs),min(ys),max(xs),max(ys)],'positive_depth':min(zs)>0,'full_bird_fits':min(xs)>=0 and min(ys)>=0 and max(xs)<=1 and max(ys)<=1,'scope':'all visible tagged regional mesh bounding boxes, including head and feet'};results[attempt]=res
 assert res['full_bird_fits'] and res['positive_depth']
(A/'whole-bird-bounds.json').write_text(json.dumps(results,indent=2)+'\n');print('BOUNDS_PASS')
