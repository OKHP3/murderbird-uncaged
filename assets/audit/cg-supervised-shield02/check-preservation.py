import bpy,json,hashlib,math,sys
from pathlib import Path
root=Path(sys.argv[sys.argv.index('--')+1]);out=root/'assets/audit/cg-supervised-shield02'
def digest(o):
    h=hashlib.sha256()
    for d in ([tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],[tuple(r) for r in o.matrix_world],[(u.name,[tuple(v.uv) for v in u.data]) for u in o.data.uv_layers],[m.name if m else None for m in o.data.materials],[p.material_index for p in o.data.polygons]):h.update(repr(d).encode())
    return h.hexdigest()
def light(o):return [tuple(o.location),tuple(o.rotation_euler),o.data.energy,tuple(o.data.color),o.data.size]
bpy.ops.wm.open_mainfile(filepath=str(root/'assets/models/cg-supervised01/attempt01/murderbird-supervised-builder.blend'))
source={o.name:digest(o) for o in bpy.context.scene.objects if o.type=='MESH'}
lights={o.name:light(o) for o in bpy.context.scene.objects if o.type=='LIGHT'}
world=repr([(n.name,[(i.name,str(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in bpy.context.scene.world.node_tree.nodes])
bpy.ops.wm.open_mainfile(filepath=str(out/'murderbird-shield02.blend'))
s=bpy.context.scene
changed=[n for n,d in source.items() if not s.objects.get(n) or digest(s.objects[n])!=d]
lights_changed=[n for n,d in lights.items() if not s.objects.get(n) or light(s.objects[n])!=d]
currentworld=repr([(n.name,[(i.name,str(i.default_value)) for i in n.inputs if hasattr(i,'default_value')]) for n in s.world.node_tree.nodes])
new=[o for o in s.objects if o.get('cgSupervisedShield02')]
finite=all(math.isfinite(c) for o in new for v in o.data.vertices for c in v.co)
result={'originalMeshCount':len(source),'changedOriginalGeometryTransformUVOrMaterialAssignments':changed,'lightChanges':lights_changed,'worldUnchanged':world==currentworld,'newMeshes':len(new),'newMeshesFinite':finite,'newMeshesHaveUVsAndThreeMaterialSlots':all(len(o.data.uv_layers)>0 and len(o.data.materials)==3 for o in new),'allNewMeshesWingOnly':all(o.get('cg2bRegion')=='wing' for o in new),'status':'PASS' if not changed and not lights_changed and world==currentworld and finite else 'FAIL','notRun':['Three-era rendering','Browser export/GLB fidelity','App build/runtime checks','Owner likeness acceptance']}
(out/'preservation-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
