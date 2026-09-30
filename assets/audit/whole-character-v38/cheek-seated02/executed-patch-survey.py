import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/Users/okh/.codex/worktrees/v38-cervical-envelope/murderbird-uncaged');p=R/'assets/models/whole-character-v38/cheek-seated01/murderbird-v38-cheek-seated01.blend';assert hashlib.sha256(p.read_bytes()).hexdigest()=='499ae8c4710e783abaae4ffc1f5eb93dff33b499b60569522a26f40c1ad14a5b';bpy.ops.wm.open_mainfile(filepath=str(p));dg=bpy.context.evaluated_depsgraph_get();rows=[]
# Named supported candidate end patches; fixed target only, never arbitrary raised fitting.
patches=[('upper-front','V33 diagonal brow receiver -1 0',(-.491,1.815)),('upper-rear','V31 fixed temporal receiving wall -1',(-.366,1.815)),('lower-rearward-front','V31 fixed temporal receiving wall -1',(-.484,1.691)),('lower-rearward-rear','V31 fixed temporal receiving wall -1',(-.406,1.683)),('bill-front','V33 formed lower cheek receiver -1 0',(-.638,1.676)),('bill-rear','V31 fixed temporal receiving wall -1',(-.520,1.674))]
for label,name,(y,z) in patches:
 o=bpy.data.objects[name];e=o.evaluated_get(dg);m=e.to_mesh();tree=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);e.to_mesh_clear();hits=[]
 for dy in (-.005,0,.005):
  for dz in (-.005,0,.005):
   q=Vector((-.8,y+dy,z+dz));hit=tree.ray_cast(q,Vector((1,0,0)));hits.append({'dy':dy,'dz':dz,'hit':list(hit[0]) if hit[0] else None,'normal':list(hit[1]) if hit[1] else None})
 rows.append({'label':label,'receiver':name,'authoredCenterYZ':[y,z],'footprint':hits,'finiteHits':sum(h['hit'] is not None for h in hits)});print(label,rows[-1]['finiteHits'],flush=True)
Path('/tmp/murderbird-cheek-fit-patch-survey.json').write_text(json.dumps(rows,indent=2)+'\n')
