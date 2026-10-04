"""Source-aspect comparison cameras; camera04 is inherited independent hypothesis.
July registration derives from authored source-plane scale, not recovered calibration.
"""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];O=R/'assets/audit/cg-supervised-head05'
C=Path('/Users/okh/.codex/worktrees/cg-supervised-camera04/murderbird-uncaged/assets/audit/cg-supervised-camera04/receipt.json')
cr=json.loads(C.read_text());camera=cr['hypotheses'][cr['proposed_hypothesis']]['camera']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for attempt in ('attempt01','attempt02'):
 A=O/attempt;r=json.loads((A/'receipt.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(A/'connected-head05.blend'));s=bpy.context.scene
 cams={};cam=s.camera;headframe=s.objects['CG2b head frame'].matrix_world.copy();origvis={o.name:o.hide_render for o in s.objects if o.type=='MESH'}
 for mode in ('july-head-only','locked-full-bird'):
  for stage in ('before','after'):
   for o in s.objects:
    if o.type!='MESH':continue
    if o.get('cgSupervisedHead05'):o.hide_render=stage=='before'
    elif o.name in r['hidden_originals']:o.hide_render=stage=='after'
    else:o.hide_render=origvis[o.name]
    if mode=='july-head-only' and o.get('cg1cRegion')!='head':o.hide_render=True
   if mode=='july-head-only':
    # Source's 1024x1536 aspect and authored .0012m/px; no fitting of July body.
    target=headframe@Vector((0,(788-512)*.0012+.005,(188-768)*.0012+.020))
    cam.location=target+(headframe.to_quaternion()@Vector((-5,0,0)))
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type='ORTHO';cam.data.ortho_scale=1536*.0012;cam.data.shift_x=cam.data.shift_y=0
    s.render.resolution_x=1024;s.render.resolution_y=1536
   else:
    cam.location=camera['location'];cam.rotation_euler=camera['rotation_euler'];cam.data.type=camera['projection'];cam.data.ortho_scale=camera['ortho_scale'];cam.data.shift_x,cam.data.shift_y=camera['shift'];cam.data.lens=camera['lens_mm'];s.render.resolution_x,s.render.resolution_y=camera['resolution']
   s.render.film_transparent=True;s.view_layers[0].material_override=None;s.cycles.samples=8;s.render.filepath=str(A/(stage+'-'+mode+'-registered.png'));bpy.ops.render.render(write_still=True)
   cams[mode+'-'+stage]={'location':list(cam.location),'rotation_euler':list(cam.rotation_euler),'ortho_scale':cam.data.ortho_scale,'shift':[cam.data.shift_x,cam.data.shift_y],'resolution':[s.render.resolution_x,s.render.resolution_y],'projection':cam.data.type}
 r['source_aspect_cameras']=cams;r['camera04_receipt_sha256']=sha(C);r['camera_status']='Independent camera04 inherited hypothesis; July registration is source-traced by construction. Neither recovers calibrated source camera.';r['images']={p.name:sha(p) for p in A.glob('*.png')}
 (A/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
print('HEAD05_SOURCE_VIEWS_PASS',flush=True)
