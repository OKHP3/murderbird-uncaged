"""Exercise the rig and export enough surfaces to prove its clip in glTF."""
from math import degrees
from pathlib import Path
import sys,json,bpy
from mathutils import Vector

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from first_choice import apply_motion
if '--with-mantle' in sys.argv:
 sys.path.insert(0,str(HERE.parent/'mantle'))
 from mantle import apply_mantle
 apply_mantle()
 out=HERE/'with-mantle'
else:
 out=HERE/'native-only'
out.mkdir(exist_ok=True)
setup=apply_motion()
a=setup['anchors']
scene=bpy.context.scene
def vec(v):
 return [round(k,7) for k in v]
def matrix(o):
 return [list(row) for row in o.matrix_world]
def w(o):
 return vec(o.matrix_world.translation)
def named(name):
 return bpy.data.objects[name]
protected=[o for o in scene.objects if o.type=='MESH' and o.get('fc_region','') in ('stand','ground')]
names=[o.name for o in protected];rest=[matrix(o) for o in protected]
samples={};err=0;selected=[]
focals=['CG1c left hip concentric hinge','CGF03 left rear toe substantial descending talon','FC fixture | bed sole','FC fixture | seated mounting bolt']
for frame in range(scene.frame_end+1):
 scene.frame_set(frame)
 for o,r in zip(protected,rest):
  mat=o.matrix_world
  err=max(err,max(abs(mat[i][j]-r[i][j]) for i in range(4) for j in range(4)))
 if frame in (0,36,44,54,73,98,155,176,193,225,252):
  samples[frame]={k:{'origin':w(o),'relative_rx_ry_rz_deg':vec([degrees(r) for r in o.rotation_euler])} for k,o in a.items()}
  for n in ['FC fixture | shaped leather saddle liner','CGH18 formed distal hooked bill plate','CG2b left deep longitudinal transmission rib 0']:
   o=named(n);p=o.matrix_world @ Vector(o.bound_box[0]);samples[frame][n]=vec(p)
scene.frame_set(0)
report={'fps':scene.render.fps,'duration':scene.frame_end/scene.render.fps,'protected_meshes':len(protected),'max_matrix_element_delta':err,'selected_protected':focals,'key_samples':samples,'shoe_surface':setup['shoe_surface'],'group_counts':{k:sum(o.type=='MESH' and o.get('fc_region')==k for o in scene.objects) for k in a}}
(out/'kinematic-check.json').write_text(json.dumps(report,indent=2))
assert err<.000001
for s in setup['shoe_surface']:
 assert all(len(p)==3 for p in s)
bpy.ops.object.select_all(action='DESELECT')
for o in a.values():o.select_set(True)
for o in scene.objects:
 if o.name.startswith('FC fixture | ') or o.name in focals or o.name in ['CGH18 formed distal hooked bill plate','CG2b left deep longitudinal transmission rib 0','CGH01 curved cervical spine']:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'rig-sample.glb'),use_selection=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_extras=True,export_materials='EXPORT',export_apply=True)
print('Motion validation',report['duration'],err,report['group_counts'])
