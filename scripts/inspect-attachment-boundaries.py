"""Read-only, hash-pinned V20 attachment-boundary inventory for V21 planning.
Run with Blender against the exact native file. The script writes only the
assigned audit JSON and refuses to overwrite an existing result.
"""
import bpy
import hashlib
import json
import os
from pathlib import Path
from mathutils import Vector

ROOT = Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
EXPECTED_NATIVE = 'assets/models/whole-character-v20/attempt-runtime02/murderbird-whole-character-v20.blend'
EXPECTED_SHA256 = 'eb15a9d87de56fb8a06004d9c69448c38089f0ecacd888e3e7fde921a353d42a'
OUTPUT = ROOT / 'assets/audit/whole-character-v21/input/attachment-boundaries.json'
PIVOTS = ('murderbird','body','breastplate','neck','cervical-upper','head','jaw','upper-bill','cranial-cover','builder-optics','processing','left-mantle','right-mantle','left-wing-shield','right-wing-shield','winding-drive','power-core')
KEY_MESHES = {
 'body': ('Curved thoracic load rail','Passive rib behind access cover','V19 fixed aperture liner','V19 fixed bottom access bearing','V19 fixed bottom hinge support'),
 'breastplate': ('Breast inner access shell','V17 breast captive overlap fasteners','V17 breast center keel return','V17 breast directional lamina','V19 moving bottom access axle','V19 moving bottom cover return'),
 'neck': ('Cervical flank lamina','Throat formed lamina','V11 posterior cervical lap','Bowed passive cervical fork','Cervical intermediate clevis','Lower cervical open backing'),
 'cervical-upper': ('Cervical flank lamina','Throat formed lamina','V11 posterior cervical lap','Cervical articulated inner guards','Cervical intermediate axle','Upper cervical curved load rail'),
 'head': ('Broad swept cheek band','Coaxial mandible journal','Forged orbital','Recessed orbital bearing','Seated passive optic housing'),
 'cranial-cover': ('Rounded swept crown lamina','Swept temporal lamina','Continuous temporal shell','V4 cranial inner shell'),
 'jaw': ('Forked forged mandible','Distal mandible bridge','Mandible journal cap'),
 'upper-bill': ('Profiled upper bill blade','Overlapping nasal hood','Cere root transition','V19 fitted proximal bill cheek plate'),
 'left-mantle': (), 'right-mantle': (), 'left-wing-shield': (), 'right-wing-shield': (),
}

def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
 return h.hexdigest()
def vec(v): return [round(float(x),9) for x in v]
def matrix(m): return [[round(float(m[r][c]),9) for c in range(4)] for r in range(4)]
def bounds(o):
 pts=[o.matrix_world @ Vector(c) for c in o.bound_box]
 return {'min':vec([min(p[i] for p in pts) for i in range(3)]),'max':vec([max(p[i] for p in pts) for i in range(3)])}

native=Path(bpy.data.filepath).resolve()
expected=(ROOT/EXPECTED_NATIVE).resolve()
if native != expected:
 raise RuntimeError('Opened native path does not match pinned V20 runtime02 input')
actual=sha(native)
if actual != EXPECTED_SHA256:
 raise RuntimeError('Pinned native SHA256 mismatch: '+actual)
if OUTPUT.exists(): raise RuntimeError('Refusing to overwrite '+str(OUTPUT))
objects={o.name:o for o in bpy.data.objects}
missing=[n for n in PIVOTS if n not in objects]
if missing: raise RuntimeError('Required pivot/node missing: '+', '.join(missing))

def chain(o):
 out=[]; p=o.parent
 while p: out.append(p.name); p=p.parent
 return out
nodes={}
for name in PIVOTS:
 o=objects[name]
 nodes[name]={'parent':o.parent.name if o.parent else None,'localPosition':vec(o.location),'worldPosition':vec(o.matrix_world.translation),'localMatrix':matrix(o.matrix_local),'worldMatrix':matrix(o.matrix_world)}
mesh_groups={}
for owner in PIVOTS:
 owned=sorted((o for o in bpy.data.objects if o.type=='MESH' and o.parent==objects[owner]),key=lambda o:o.name)
 prefixes=KEY_MESHES.get(owner,())
 mesh_groups[owner]={'count':len(owned),'selectedNames':[o.name for o in owned if any(o.name.startswith(prefix) for prefix in prefixes)]}
# Capture exact extents of the most relevant moving/fixed boundary parts.
boundary_terms=('Breast inner access shell','Passive rib behind access cover','V19 fixed aperture liner','V19 fixed bottom access bearing','V19 fixed bottom hinge support','Throat formed lamina 4','Throat formed lamina 5','Throat formed lamina 6','Cervical flank lamina -1 4','Cervical flank lamina -1 5','Cervical flank lamina -1 6','Cervical flank lamina 1 4','Cervical flank lamina 1 5','Cervical flank lamina 1 6','V19 moving bottom access axle','V19 moving bottom cover return')
mesh_bounds=[]
for o in sorted((o for o in bpy.data.objects if o.type=='MESH' and any(o.name.startswith(t) for t in boundary_terms)),key=lambda o:o.name):
 mesh_bounds.append({'name':o.name,'owner':o.parent.name if o.parent else None,'worldBounds':bounds(o)})
breast=objects['breastplate']
user={k:breast.get(k) for k in ('inspectionAxis','inspectionOpenRadians') if k in breast}
result={'schema':'murderbird-v21-attachment-boundaries-v1','status':'read-only source inventory; current proposed geometry is not assumed approved','source':{'native':EXPECTED_NATIVE,'sha256':actual,'coordinateConvention':'native metres; +X anatomical left, -Y forward, +Z up','pivotCountFromSourceExportReceipt':52},'nodes':nodes,'directMeshOwners':mesh_groups,'breastplateInspectionProperties':user,'boundaryMeshBounds':mesh_bounds,'scopeLimits':['Owner parenting and pivot placement do not establish adequate surface fit, collision clearance, load capacity, or artistic acceptance.','Current V20 mesh contours are evidence of existing ownership only; they are replaceable proposals.','Any pivot relocation requires fresh owner-local socket derivation, inspection transforms, and pose evidence.']}
OUTPUT.parent.mkdir(parents=True,exist_ok=True)
OUTPUT.write_text(json.dumps(result,indent=2)+'\n')
print('Wrote',OUTPUT)
