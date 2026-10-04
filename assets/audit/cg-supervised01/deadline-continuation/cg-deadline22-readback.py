import bpy,json,importlib.util
from pathlib import Path
R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
def load(n):
 s=importlib.util.spec_from_file_location(n,R/'scripts'/n);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
D=load('cg-supervised-head17.py');P=load('cg-supervised-preservation.py')
bpy.ops.wm.open_mainfile(filepath=str(R/'assets/models/cg-supervised01/attempt09/murderbird-supervised-builder.blend'));a=D.snap();imgs=P.packed_image_snapshot()
bpy.ops.wm.open_mainfile(filepath=str(R/'assets/models/cg-supervised-deadline22/murderbird-deadline22.blend'));b=D.snap();v={'object_count':len(a['objects']),'material_count':len(a['materials']),'changed_objects':[n for n,h in a['objects'].items() if b['objects'].get(n)!=h],'changed_materials':[n for n,h in a['materials'].items() if b['materials'].get(n)!=h],'packed':P.verify_receiving_images(imgs)};p=R/'assets/audit/cg-supervised-deadline22/receipt.json';d=json.loads(p.read_text());d['native_readback']=v;p.write_text(json.dumps(d,indent=2));print('D22_READBACK',v,flush=True)
