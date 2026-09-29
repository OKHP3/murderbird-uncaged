from pathlib import Path
import json, hashlib
import bpy
root=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
source=root/'scripts/render-construction-poses.py'
ns={'__file__':str(source),'__name__':'shadow_diagnostic_helpers'}
exec(compile(source.read_text().rsplit('\nmain()',1)[0],str(source),'exec'),ns)
manifest=json.loads((root/'assets/audit/whole-character-v18/attempt-01/motion-renders/render-02/pose-render-manifest.json').read_text())
native=root/manifest['native']['path']; packet=root/manifest['posePacket']['path']
assert ns['sha'](native)==manifest['native']['sha256'] and ns['sha'](packet)==manifest['posePacket']['sha256']
out=root/'assets/audit/whole-character-v19/render-shadow-diagnostic'
assert not out.exists();out.mkdir(parents=True)
(out/'executed-diagnostic.py').write_bytes(Path(__file__).read_bytes())
bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene
pivots={o.name:o for o in bpy.data.objects if o.type=='EMPTY'}
pose=next(p for p in json.loads(packet.read_text())['poses'] if p['id']=='advanced-contact')
ns['apply_pose'](pose,pivots)
for o in bpy.data.objects:
    if o.type=='CURVE':o.hide_render=True
    if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
cam,cd,floor,fm=ns['add_camera_and_floor'](scene);ns['configure'](scene)
scene.camera=cam
from mathutils import Vector
r=pivots['murderbird'].matrix_world;target=r@Vector((0,0,1));offset=r.to_quaternion()@Vector((-3.3,-4.4,1.8))
cam.location=target+offset;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
records=[]
for enabled in (True,False):
    scene.display.shading.show_shadows=enabled
    f=out/('shadows-on.png' if enabled else 'shadows-off.png');scene.render.filepath=str(f)
    bpy.ops.render.render(write_still=True);records.append({'shadows':enabled,'image':ns['artifact'](f)})
(out/'receipt.json').write_text(json.dumps({'native':manifest['native'],'posePacket':manifest['posePacket'],'poseId':pose['id'],'onlyDifference':'Workbench show_shadows true versus false; same meshes and historical curves hidden in both','renders':records,'nativeUnchanged':ns['sha'](native)==manifest['native']['sha256']},indent=2)+'\n')
