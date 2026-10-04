import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'assets/audit/cg-supervised-head04/attempt02';a=json.loads((O/'receipt.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(O/'volumetric-head04.blend'));s=bpy.context.scene
pal={'head-armor':(.25,.5,.75,1),'black-iron':(.08,.08,.10,1),'machined-steel':(.55,.55,.6,1),'worn-bronze':(.8,.42,.08,1),'protected-optic':(.7,.12,.03,1),'protected-glass':(.15,.7,.6,1)};ids={}
for k,c in pal.items():
 d=bpy.data.materials.new('ID '+k);d.use_nodes=True;d.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=c;d.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.8;ids[k]=d
for o in s.objects:
 if o.type=='MESH' and o.get('cg1cRegion')=='head':
  for i,f in enumerate(json.loads(o.get('cgSurfaceFamilies','[]'))):
   if i<len(o.data.materials) and f in ids:o.data.materials[i]=ids[f]
for stage in ('before','after'):
 for o in s.objects:
  if o.get('cgSupervisedHead04'):o.hide_render=stage=='before'
  if o.name in a['hidden_originals']:o.hide_render=stage=='after'
 s.render.filepath=str(O/(stage+'-material-id-head-45.png'));bpy.ops.render.render(write_still=True)
