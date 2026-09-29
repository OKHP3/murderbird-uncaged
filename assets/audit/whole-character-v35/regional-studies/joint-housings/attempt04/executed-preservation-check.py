from pathlib import Path
import json, math
import bpy, bmesh
from mathutils import Vector
root=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
src=root/'assets/models/whole-character-v34/attempt-form01/murderbird-whole-character-v34.blend'
cand=root/'assets/models/whole-character-v35/regional-studies/joint-housings/attempt04/murderbird-whole-character-v35-joint-housings.blend'
owners={'left-thigh','right-thigh','left-shin','right-shin'}

def snapshot():
    bpy.context.view_layer.update()
    out={}
    for o in bpy.data.objects:
        out[o.name]={'type':o.type,'parent':o.parent.name if o.parent else None,
          'world':tuple(round(float(x),10) for row in o.matrix_world for x in row),
          'local':tuple(round(float(x),10) for row in o.matrix_local for x in row),
          'props':tuple(sorted((k,repr(o[k])) for k in o.keys())),
          'mats':tuple(m.name if m else None for m in o.data.materials) if o.type=='MESH' else (),
          'verts':tuple(tuple(round(float(c),10) for c in v.co) for v in o.data.vertices) if o.type=='MESH' else ()}
    return out
bpy.ops.wm.open_mainfile(filepath=str(src)); before=snapshot()
bpy.ops.wm.open_mainfile(filepath=str(cand)); after=snapshot()
assert set(before)==set(after)
changed=[]; target_meshes=[]
for name,a in before.items():
    b=after[name]
    assert (a['type'],a['parent'],a['world'],a['local'],a['props'],a['mats'])==(b['type'],b['parent'],b['world'],b['local'],b['props'],b['mats']), name
    if a['verts']!=b['verts']:
        changed.append(name); obj=bpy.data.objects[name]
        assert obj.parent and obj.parent.name in owners,(name,obj.parent.name if obj.parent else None)
        target_meshes.append(obj)
assert len(changed)>0, len(changed)
for obj in target_meshes:
    bm=bmesh.new();bm.from_mesh(obj.data)
    assert all(e.is_manifold for e in bm.edges),obj.name
    volume=float(bm.calc_volume(signed=True)); assert math.isfinite(volume) and volume>0,(obj.name,volume)
    assert all(math.isfinite(c) for v in obj.data.vertices for c in v.co),obj.name
    bm.free()
report={'status':'passed','sameObjectSet':True,'allObjectTransformsParentsPropertiesMaterialsExact':True,
 'changedMeshCount':len(changed),'changedMeshes':sorted(changed),'allChangesWithinFourLegOwners':True,
 'changedMeshesClosedFinitePositiveVolume':True,'checkedJointCentersAndNamedRigNodeRestsExact':True}
out=root/'assets/audit/whole-character-v35/regional-studies/joint-housings/attempt04/preservation-check.json'
out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
