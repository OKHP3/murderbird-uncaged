import ast,bpy,hashlib,json
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[4];AUDIT=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
source=ROOT/'scripts/build-v38-breast-envelope02.py';parsed=ast.parse(source.read_text());defs=[n for n in parsed.body if isinstance(n,ast.FunctionDef)and n.name in('require','art','render_views')];exec(compile(ast.Module(body=defs,type_ignores=[]),str(source),'exec'))
pose={'neck':.10675220489501955,'cervical-mid-a':.10675220489501955,'cervical-mid-b':.10675220489501955,'cervical-upper':.10675220489501955,'head':-.5090505059024657};records={}
for version,label in(('lower-support02','source'),('breast-envelope02','candidate')):
 bpy.ops.wm.open_mainfile(filepath=str(ROOT/f'assets/models/whole-character-v38/{version}/murderbird-v38-{version}.blend'))
 for n,a in pose.items():o=bpy.data.objects[n];o.matrix_basis=o.matrix_basis@Matrix.Rotation(a,4,'X')
 bpy.context.view_layer.update();records[label]=render_views(label+'-actual-center-contact',[('full-bird-three-quarter',(-6,-3.5,2.75),(0,-.08,1.03),2.4),('breast-profile',(-7,0,2.1),(0,-.30,1.12),.85)])
(AUDIT/'contact-views.json').write_text(json.dumps({'poseAnglesRad':pose,'views':records,'limits':'Actual captured angle matched model glances; no runtime path or continuous clearance claim'},indent=2)+'\n')
