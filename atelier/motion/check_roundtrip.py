"""Read independently imported GLB positions and axes vs native joint frames."""
from pathlib import Path
import json,sys,bpy
from mathutils import Vector
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from first_choice import apply_motion
source=HERE.parent.parent/'media/cg-retained04-builder-murderbird-recursive-builder.blend'
p=Path(sys.argv[sys.argv.index('--')+1]) if '--' in sys.argv else HERE/'native-only/rig-sample.glb'
sc=bpy.context.scene
r=apply_motion()
labels=['FC | '+s for s in ['Saddle','Torso','Neck','Head','Ground','Stand']]
local=[Vector((0,0,0)),Vector((0,-.1,0)),Vector((0,0,.1))]
frames=[0,36,44,54,73,98,155,193,225,252]
def sweep(shift):
 out={}
 for f in frames:
  bpy.context.scene.frame_set(f+shift)
  for n in labels:
   m=bpy.data.objects[n].matrix_world
   out[(f,n)]=[m@q for q in local]
 return out
ref=sweep(0)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.render.fps=24
bpy.ops.import_scene.gltf(filepath=str(p))
ob=bpy.data.objects['FC | Head']
data=ob.animation_data
print('NLA readback',[(t.name,[(s.name,s.frame_start,s.frame_end) for s in t.strips]) for t in data.nla_tracks])
start=min(s.frame_start for t in data.nla_tracks for s in t.strips)
print('import active',data.action and data.action.name, [(t.mute, s.action_frame_start,s.action_frame_end) for t in data.nla_tracks for s in t.strips])
for shift in (0,1,-1):
 result=sweep(shift)
 print('phase',shift,max((v1-v2).length for key in ref for v1,v2 in zip(ref[key],result[key])))
obs=sweep(0 if data.action else int(start))
errors={n:max((v1-v2).length for f in frames for v1,v2 in zip(ref[(f,n)],obs[(f,n)])) for n in labels}
dest=HERE/'roundtrip-result.json'
dest.write_text(json.dumps({'input_leaf':p.name,'frames_at_24fps':frames,'measure':'maximum displacement of native vs independently imported joint landmark in Blender units at pivot, 10cm forward and 10cm up','max_abs_positional_error':errors},indent=2))
print(errors);assert max(errors.values())<.0001
