"""Check editable exterior placement against its backing meshes in Blender.

This catches the buried-overlay defect found during visual review. It samples
outer plate vertices in the rigid wing parent's coordinates; it is not a
continuous collision solver or an artistic acceptance test.
"""
from pathlib import Path
import bpy, json, datetime
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/models/uncaged-exterior-v1/murderbird-exterior-v1.blend'))
bpy.context.scene.frame_set(1)
bpy.context.view_layer.update()
meshes = [o for o in bpy.data.objects if o.type == 'MESH' and o.get('exteriorEras') == 'builder']
checks = []
legacy = [o.name for o in meshes if o.name.split(' [')[0] in ['left thigh', 'right thigh']]
checks.append({'name':'Legacy solid thigh tubes retired in favor of passive rails and selective guards', 'status':'passed' if not legacy else 'failed', 'remaining':legacy})
samples = []
for parent_name in ['left-mantle','right-mantle','left-wing-shield','right-wing-shield']:
    sign = 1 if parent_name.startswith('left') else -1
    parts = [o for o in meshes if o.parent and o.parent.name == parent_name]
    backing = [o for o in parts if any(s in o.name.lower() for s in ['shoulder mantle shell','folded forewing shield'])]
    plates = [o for o in parts if 'peened pin' not in o.name.lower() and any(s in o.name.lower() for s in ['upper-arm overlap','curved forewing guard','tapered trailing wing plate'])]
    assert backing and plates, f'Missing backing or plate coverage for {parent_name}'
    verts, faces = [], []
    for obj in backing:
        offset = len(verts)
        verts.extend(obj.matrix_local @ v.co for v in obj.data.vertices)
        faces.extend(tuple(offset+i for i in f.vertices) for f in obj.data.polygons)
    tree = BVHTree.FromPolygons(verts, faces)
    for plate in plates:
        exterior = {}
        for vertex in plate.data.vertices:
            v = plate.matrix_local @ vertex.co
            key = (round(v.y,5),round(v.z,5))
            if key not in exterior or sign*v.x > sign*exterior[key].x:
                exterior[key] = v
        clearances = []
        for point in exterior.values():
            hit,normal,index,distance = tree.ray_cast(Vector((sign*1.0,point.y,point.z)),Vector((-sign,0,0)),2.0)
            if hit is not None:
                clearances.append(sign*(point.x-hit.x))
        samples.append({'plate':plate.name,'parent':parent_name,'overBackingSamples':len(clearances),'minOutwardClearanceMeters':min(clearances) if clearances else None,'buriedSamples':sum(d<-.002 for d in clearances)})
checks.append({'name':'Wing overlay outer vertices remain outside their curved backing', 'status':'passed' if all(s['buriedSamples']==0 for s in samples) else 'failed', 'samples':samples, 'toleranceMeters':.002})
result = {'generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'passed' if all(c['status']=='passed' for c in checks) else 'failed','scope':'Editable rest-pose exterior visibility and retired legacy geometry; not continuous collision freedom or likeness approval','checks':checks}
out=ROOT/'assets/audit/exterior-v1/source-placement-validation.json'
out.write_text(json.dumps(result,indent=2)+'\n')
print('EXTERIOR_SOURCE_PLACEMENT',result['status'],len(samples),'plates')
if result['status']!='passed':
    raise RuntimeError('Exterior source placement failed; inspect '+str(out))
