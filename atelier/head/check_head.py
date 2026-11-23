"""Measure the digital head mesh, scene-space aperture and selected clearances."""
import json, sys
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here))
from cranial import apply_head, point, CREATED
status=apply_head()
dg=bpy.context.evaluated_depsgraph_get()
headmeshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('fc_region')=='head' and not o.hide_render and o.visible_get()]
parts={o.name.removeprefix('FC head | '):o for o in CREATED}
blade=parts['continuous deep hooked blade']
ob=blade.evaluated_get(dg)
tree=BVHTree.FromObject(blade,dg)
jaw=[parts['continuous upturned mandibular toe'],parts['left cast mandible spar'],parts['right cast mandible spar']]
# The separate mandibular spars meet the skull posteriorly. This measurement samples
# the distal mandibular points against the actual hook surface, in the neutral head.
threshold=point(960,0,0).y
r=[]
for j in jaw:
    for v in j.data.vertices:
        wp=j.matrix_world@v.co
        if wp.y <= threshold:
            hit,_,_,dist=tree.find_nearest(ob.matrix_world.inverted()@wp)
            if dist is not None: r.append(float(dist))
probes={}
for u,v in [(960,179),(964,188),(956,183),(969,181),(984,151)]:
    origin=point(u,v,-.5)
    names=[]
    for o in headmeshes:
        inv=o.matrix_world.inverted()
        loc=inv@origin
        direction=inv.to_3x3()@Vector((1,0,0))
        ok,_,_,_=o.ray_cast(loc,direction,distance=1.0)
        if ok: names.append(o.name)
    probes[f'{u},{v}']=names
vs=[o.matrix_world@v.co for o in headmeshes for v in o.data.vertices]
m={
    'source_sha256':'9de7c4d1c9ac158135f9f846af61683528e00340a708820b2cfe1d942acc54d5',
    'created_mesh_objects':len(CREATED),'hidden_predecessors':len(status['retired']),
    'visible_head_parts':len(headmeshes),'derived_triangles':sum(len(p.vertices)-2 for o in CREATED for p in o.data.polygons),
    'world_bounds_m':[[round(min(v[i] for v in vs),6) for i in range(3)],[round(max(v[i] for v in vs),6) for i in range(3)]],
    'head_pivot_m':[0,-.11437,1.56159],'forward_axis':'-Y','up_axis':'Z',
    'distal_mandible_vertex_to_blade_minimum_m':min(r),'distal_sample_count':len(r),
    'transverse_neutral_rays_at_guide_stations':probes,
    'interpretation':'The distal measurement uses evaluated upper-bill geometry and vertices ahead of jaw station 960. Empty ray results in the oral opening establish sampled sightlines. All are geometry checks on the posed digital asset.'
}
assert not probes['960,179'] and min(r)>.001
(here/'head-check.json').write_text(json.dumps(m,indent=2)+'\n')
print(json.dumps(m))
