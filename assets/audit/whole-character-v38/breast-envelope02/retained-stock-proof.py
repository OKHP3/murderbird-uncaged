import bpy,json,hashlib,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];AUDIT=Path(__file__).resolve().parent
names=['V23 breast moving return -1','V23 breast moving return 1']
def stock(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));return {n:[list(v.co)for v in bpy.data.objects[n].data.vertices[:32]]for n in names}
a=stock(ROOT/'assets/models/whole-character-v38/lower-support02/murderbird-v38-lower-support02.blend');b=stock(ROOT/'assets/models/whole-character-v38/breast-envelope02/murderbird-v38-breast-envelope02.blend');assert a==b
proof={n:{'first32LocalCoordinatesByteExact':a[n]==b[n],'originalAndCandidateFloat32Sha256':hashlib.sha256(b''.join(struct.pack('<3f',*v)for v in a[n])).hexdigest(),'ringScope':'Eight-vertex C stock rings0–3 retained at hinge end; remaining rings intentionally refitted, all original nodes/pivots exact per frozen receipt'}for n in names};(AUDIT/'retained-stock-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(proof)
