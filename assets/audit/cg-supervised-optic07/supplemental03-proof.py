"""Read-only supplemental views and independent Maker/Mechanic API executions."""
from pathlib import Path
import bpy, math, json, importlib.util
from mathutils import Vector
root=Path(__file__).resolve().parents[3]
inp=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
out=root/'assets/audit/cg-supervised-optic07/attempt03'
spec=importlib.util.spec_from_file_location('optic',root/'scripts/cg-supervised-optic07.py');optic=importlib.util.module_from_spec(spec);spec.loader.exec_module(optic)
source=inp/'assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend'
receipts={}
def render(s,name,view='matched',grazing=False):
 cam=s.camera;target=s.objects['CG2b head frame'].matrix_world@Vector((-.15,.005,.020))
 q=json.loads((inp/'assets/audit/cg-supervised-camera04/receipt.json').read_text())['hypotheses']['ortho-35']['camera']
 cam.rotation_euler=q['rotation_euler']
 direction=cam.rotation_euler.to_matrix()@Vector((0,0,-1));cam.location=target-direction*6
 if view in ('front','profile'):
  cam.location=(0,-6,target.z) if view=='front' else (-6,target.y,target.z)
  cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
 cam.data.type='ORTHO';cam.data.ortho_scale=.62;cam.data.shift_x=cam.data.shift_y=0
 if grazing:
  lights=[o for o in s.objects if o.type=='LIGHT'];lights[0].location=target+Vector((-1,-.8,.5));lights[0].rotation_euler=(target-lights[0].location).to_track_quat('-Z','Y').to_euler();lights[0].data.energy=80;lights[0].data.size=.15
  for o in lights[1:]:o.data.energy*=.18
 s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=6;s.cycles.use_denoising=True;s.render.resolution_x=1280;s.render.resolution_y=853;s.render.resolution_percentage=100;s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
 receipts[name]={'location':list(cam.location),'rotation':list(cam.rotation_euler),'scale':cam.data.ortho_scale,'grazing':grazing}
for era in ('maker','mechanic'):
 bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;r=optic.apply(s,inp,era)
 protected=[m for m in bpy.data.materials if m.get('cgOptic07Role')]
 assert all(m.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value==0 for m in protected)
 assert all(m.get('opticEra')==era for m in protected)
 render(s,era+'-dark-head');receipts[era]={'API':r,'allNewOpticEmissionZero':True}
for kind,path in [('before',source),('after',out/'murderbird-optic07.blend')]:
 for view in ('front','profile','grazing'):
  bpy.ops.wm.open_mainfile(filepath=str(path));s=bpy.context.scene
  render(s,kind+'-head-'+view,view if view!='grazing' else 'matched',view=='grazing')
(out/'supplemental-proof.json').write_text(json.dumps(receipts,indent=2)+'\n')
print('SUPPLEMENTAL_COMPLETE')
