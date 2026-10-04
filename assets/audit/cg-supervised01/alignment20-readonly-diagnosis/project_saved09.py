import bpy, json, hashlib, math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
model=ROOT/'assets/models/cg-supervised01/attempt09/murderbird-supervised-builder.blend'
source=ROOT/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg'
camrec=json.loads((ROOT/'assets/audit/cg-supervised-camera04/receipt.json').read_text())
cam=camrec['hypotheses']['ortho-35']['camera']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected_model='c39a2fefcc9b4d277540a0406522e69b06975c14a0b8e281f183d1fca20dc2fc'
expected_source='645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114'
assert sha(model)==expected_model, 'saved09 hash mismatch'
assert sha(source)==expected_source, 'pinned source hash mismatch'
bpy.ops.wm.open_mainfile(filepath=str(model))
scene=bpy.context.scene
camera_data=bpy.data.cameras.new('temporary alignment20 camera')
camera_obj=bpy.data.objects.new('temporary alignment20 camera',camera_data)
scene.collection.objects.link(camera_obj); scene.camera=camera_obj
camera_obj.location=cam['location'];camera_obj.rotation_euler=cam['rotation_euler'];camera_data.type=cam['projection'];camera_data.ortho_scale=cam['ortho_scale'];camera_data.shift_x,camera_data.shift_y=cam['shift']
W,H=cam['resolution'];scene.render.resolution_x=W;scene.render.resolution_y=H;scene.render.resolution_percentage=100
bpy.context.view_layer.update()
def center(n):
 o=scene.objects[n]
 return sum((o.matrix_world@v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
def extreme(n,axis,fn):
 o=scene.objects[n]; pts=[o.matrix_world@v.co for v in o.data.vertices];return fn(pts,key=lambda p:getattr(p,axis))
landmarks=[
 ('crown',[834,28],extreme('CGH04 nine section cranial vault','z',max),1,'cranial vault highest vertex; source crest includes separate plates'),
 ('near-optic',[916,113],center('CGH04 solid optical glass L'),1,'visible circular optic center'),
 ('bill-hook',[989,257],extreme('CGH04 nine section convex hooked upper bill','z',min),1,'lowest upper-bill vertex; contour interpretation'),
 ('near-shoulder',[719,272],center('CGB04 -1 shield hard blade 0-1'),.7,'upper shield-root center; broad ambiguous region'),
 ('breast-center',[898,402],center('CGB04 breast framing 4-1'),.5,'frontal breast plate-course center; uncertain homologous surface'),
 ('near-knee',[610,550],center('CG1c left knee concentric hinge'),1,'visible upper circular leg hinge'),
 ('far-knee',[840,552],center('CG1c right knee concentric hinge'),1,'far upper hinge partly occluded'),
 ('near-hock',[610,644],center('CG1c left hock concentric hinge'),1,'source intermediate circular hinge'),
 ('far-hock',[830,643],center('CG1c right hock concentric hinge'),.7,'far hinge partly occluded'),
 ('near-ankle',[639,731],center('CG1c left ankle concentric hinge'),1,'source instep/ankle hinge center'),
 ('far-ankle',[856,728],center('CG1c right ankle concentric hinge'),.7,'source instep/ankle hinge center partly occluded'),
 ('near-foot',[665,768],center('CG1c left plantar foot housing'),.5,'proximal plantar housing, partly covered'),
 ('far-foot',[885,747],center('CG1c right plantar foot housing'),.5,'proximal plantar housing, partly covered'),
]
rows=[]
for name,src,world,weight,assumption in landmarks:
 v=world_to_camera_view(scene,camera_obj,world); px=[float(v.x*W),float((1-v.y)*H)]
 res=[px[0]-src[0],px[1]-src[1]]
 rows.append(dict(name=name,source_px=src,projected09_px=px,residual_px=res,distance_px=math.hypot(*res),weight=weight,assumption=assumption,world_xyz=[float(x) for x in world]))
by={x['name']:x for x in rows}
out={
 'status':'measured_projection',
 'model_path':str(model.relative_to(ROOT)),'model_sha256':sha(model),'source_path':str(source.relative_to(ROOT)),'source_sha256':sha(source),
 'camera_source':'assets/audit/cg-supervised-camera04/receipt.json hypothesis ortho-35 (35 degrees from side, 16 degrees elevation); reused exactly; not physical calibration',
 'resolution':[W,H], 'rows':rows,
 'projected_separations_px':{'knee':abs(by['far-knee']['projected09_px'][0]-by['near-knee']['projected09_px'][0]),'ankle':abs(by['far-ankle']['projected09_px'][0]-by['near-ankle']['projected09_px'][0])},
 'source_separations_px':{'knee':abs(by['far-knee']['source_px'][0]-by['near-knee']['source_px'][0]),'ankle':abs(by['far-ankle']['source_px'][0]-by['near-ankle']['source_px'][0])},
 'scope':'Projection only; no optimization, posing, camera fitting, rendering, or save.'
}
Path('/tmp/cg-alignment20/diagnosis.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'model_sha256':out['model_sha256'],'source_sha256':out['source_sha256'],'camera':cam,'separations':out['projected_separations_px'],'landmarks':[{k:r[k] for k in ['name','source_px','projected09_px','residual_px','distance_px']} for r in rows]},indent=2))
