"""Compare animated native and runtime joint frames and ground contacts.

blender -b /path/to/first-choice.blend --python-exit-code 1 \
  -P atelier/motion/verify_delivery.py -- /path/to/first-choice.glb
"""
import hashlib,json,sys
from pathlib import Path
import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parent
GLB=Path(sys.argv[sys.argv.index('--')+1]).resolve()
NATIVE=Path(bpy.data.filepath)
NAMES={'ground','stand','saddle','torso','neck','head'}
PROBES=[Vector((0,0,0)),Vector((0,-.1,0)),Vector((0,0,.1))]
FRAMES=range(253)

def sha(path):
 with path.open('rb') as file:
  return hashlib.file_digest(file,'sha256').hexdigest()

def joint_frames():
 sc=bpy.context.scene
 anchors={s:bpy.data.objects['FC | '+s.title()] for s in NAMES}
 fixed=[o for o in sc.objects if o.type=='MESH' and o.parent in {anchors['ground'],anchors['stand']}]
 assert all(not o.animation_data and not o.data.shape_keys for o in fixed), "Unexpected deforming planted part"
 sc.frame_set(0)
 initial={o:o.matrix_world.copy() for o in fixed}
 # Compute the fore-aft gap directly from actual rest geometry in Y.
 bb=lambda obj:[obj.matrix_world@Vector(k) for k in obj.bound_box]
 legfront=min(v.y for o in fixed if o.parent==anchors['ground'] for v in bb(o))
 standback=max(v.y for o in fixed if o.parent==anchors['stand'] for v in bb(o))
 records={};moving=set();max_drift=0.
 for f in FRAMES:
  sc.frame_set(f)
  records[f]={k:[ob.matrix_world@p for p in PROBES] for k,ob in anchors.items()}
  for ob,initial_matrix in initial.items():
   if ob.matrix_world != initial_matrix:
    max_drift=max(max_drift,max(abs(ob.matrix_world[i][j]-initial_matrix[i][j]) for i in range(4) for j in range(4)))
    moving.add(ob.name)
 sc.frame_set(0)
 return records,{'fixed_mesh_count':len(fixed),'changed_fixed_transforms':sorted(moving),'max_matrix_element_change':max_drift,'conservative_bounds_foot_to_stand_y_m':round(legfront-standback,5)}

def summarize(errors):
 return {key:float(f'{value:.9g}') for key,value in errors.items()}
native,protected=joint_frames()
assert protected['max_matrix_element_change']<1e-7
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.render.fps=24
bpy.ops.import_scene.gltf(filepath=str(GLB))
glb,protected_rt=joint_frames()
deltas={s:max((a-b).length for f in FRAMES for a,b in zip(native[f][s],glb[f][s])) for s in NAMES}
endpoint={s:max((a-b).length for a,b in zip(glb[0][s],glb[252][s])) for s in NAMES}
r={'native_sha256':sha(NATIVE),'glb_sha256':sha(GLB),'clip':'First Choice','tested_frames':len(FRAMES),'joint_probes_per_frame':3*len(NAMES),'probe_locations':'origin, 0.1 native units forward and 0.1 up, for each of six named pivots','native_fixed':protected,'glb_fixed':protected_rt,'max_native_to_glb_joint_probe_delta_m':summarize(deltas),'glb_start_to_end_joint_probe_delta_m':summarize(endpoint)}
(ROOT/'delivered-motion-check.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r))
assert max(deltas.values())<1e-5 and max(endpoint.values())<1e-5 and protected_rt['max_matrix_element_change']<1e-7
