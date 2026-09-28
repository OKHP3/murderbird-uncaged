from pathlib import Path
import bpy,json,hashlib
R=Path(__file__).resolve().parents[3]
p=R/'assets/models/uncaged-lower-leg-construction-study-v1/murderbird-lower-leg-construction-study-v1.blend'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='415a3aa7976c271c28187eb4ee1440dbcd858f4dfb5b84cb6ed69e381def982f'
bpy.ops.wm.open_mainfile(filepath=str(p))
def bounds(pts):return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
def read(label):
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();rows=[]
 for n in ['Short dorsal shell','left lower-leg partial anterior inspection guard','left lower-leg inboard boxed load spar']:
  o=bpy.data.objects[n];e=o.evaluated_get(dg);m=e.to_mesh();pts=[e.matrix_world@v.co for v in m.vertices];e.to_mesh_clear()
  rows.append({'name':n,'rawBounds':bounds([o.matrix_world@v.co for v in o.data.vertices]),'evaluatedBounds':bounds(pts),'worldMatrix':[list(r) for r in o.matrix_world]})
 return {'label':label,'frame':bpy.context.scene.frame_current,'rows':rows}
a=[read('saved')];bpy.context.scene.frame_set(1);a.append(read('frame1'))
out=Path(__file__).with_name('supervisor-frame-audit.json');assert not out.exists();out.write_text(json.dumps(a,indent=2)+'\n');print(out.read_text())
