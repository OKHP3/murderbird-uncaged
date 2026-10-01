import ast,bpy,hashlib,json
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[5];AUDIT=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();source=ROOT/'scripts/build-v38-breast-support02.py';defs=[n for n in ast.parse(source.read_text()).body if isinstance(n,ast.FunctionDef)and n.name in('require','art','render_views')];exec(compile(ast.Module(body=defs,type_ignores=[]),str(source),'exec'));records={}
for suffix,label in(('', 'source'),('-seam01','candidate')):
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/f'assets/models/whole-character-v38/breast-support02/murderbird-v38-breast-support02{suffix}.blend'));records[label]=render_views(label,[('breast-three-quarter',(-6,-3.5,2.1),(0,-.25,1.02),.85),('breast-front',(0,-7,1.8),(0,-.25,1.02),.72),('row3-row4-seam-three-quarter',(-6,-4,1.4),(0,-.27,.99),.45)])
(AUDIT/'detail-views.json').write_text(json.dumps(records,indent=2)+'\n')
