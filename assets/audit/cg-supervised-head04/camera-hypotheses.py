"""Constrained orthographic landmark fits; expressly not physical calibration."""
import bpy,json,math,numpy as np
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];O=R/'assets/audit/cg-supervised-head04/attempt02'
bpy.ops.wm.open_mainfile(filepath=str(O/'volumetric-head04.blend'));s=bpy.context.scene
frame=s.objects['CG2b head frame'].matrix_world
# Source pixels label corresponding authored 3D anchors. Cross-view association
# and hidden depth are uncertain; optimizing these sparse points is not likeness proof.
labels=['optic center','brow root','brow heel','beak root','upper bill tip','mandible tip','posterior skull']
source3=[(788,188,-.175),(675,53,0),(847,171,-.167),(916,220,-.091),(885,460,0),(876,423,-.001),(568,191,0)]
points=np.array([[d,(788-x)*.0012+.005,(188-y)*.0012+.020] for x,y,d in source3])
cases={'july-head':{'resolution':[1024,1536],'pixels':[[788,188],[675,53],[847,171],[916,220],[885,460],[876,423],[568,191]],'scope':'head-only; July body excluded','source':'context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png'},'locked-full-bird':{'resolution':[1280,853],'pixels':[[916,111],[833,27],[963,108],[981,132],[977,261],[976,225],[743,115]],'scope':'head anchors fit camera; body shown unchanged, not independently body-fitted','source':'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg'}}
result={'status':'camera hypotheses, not recovered physical calibration','method':'bounded yaw/elevation grid with least squares uniform scale and image translation; hand annotated source correspondences','uncertainty':'Source head anchors/occlusion uncertain; inferred width. July identity is source-traced, so low residual is partly by construction, not independent validation. Full-bird head-only fit can reveal body disagreement.'}
for name,case in cases.items():
 target=np.array([[x,-y] for x,y in case['pixels']]);best=None
 for yaw in range(0,36):
  for elev in range(-15,16):
   a,e=math.radians(yaw),math.radians(elev);normal=Vector((-math.cos(a)*math.cos(e),-math.sin(a)*math.cos(e),math.sin(e)));q=(-normal).to_track_quat('-Z','Y');right=q@Vector((1,0,0));up=q@Vector((0,1,0));xy=points@np.array([right,up]).T
   xc=xy-xy.mean(axis=0);yc=target-target.mean(axis=0);scale=float((xc*yc).sum()/(xc*xc).sum());shift=target.mean(axis=0)-scale*xy.mean(axis=0);pred=xy*scale+shift;res=np.linalg.norm(pred-target,axis=1);score=float((res**2).mean())
   if best is None or score<best[0]:best=(score,yaw,elev,scale,shift,pred,res,normal,right,up,q)
 score,yaw,elev,scale,shift,pred,res,normal,right,up,q=best;w,h=case['resolution'];center=right*((w/2-shift[0])/scale)+up*((-h/2-shift[1])/scale)
 cam=s.camera;cam.location=frame@(center+normal*5);cam.rotation_euler=(frame.to_quaternion()@q).to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=max(w,h)/scale;cam.data.shift_x=cam.data.shift_y=0;s.render.resolution_x=w;s.render.resolution_y=h;s.render.film_transparent=True;s.view_layers[0].material_override=None;s.cycles.samples=8
 s.render.filepath=str(O/(name+'-registered.png'));bpy.ops.render.render(write_still=True)
 result[name]={**case,'yaw_from_profile_degrees':yaw,'elevation_degrees':elev,'scale_pixels_per_unit':scale,'median_residual_px':float(np.median(res)),'rms_residual_px':math.sqrt(score),'camera':{'location':list(cam.location),'rotation_euler':list(cam.rotation_euler),'ortho_scale':cam.data.ortho_scale,'projection':'ORTHO'},'landmarks':[{'name':label,'source_pixel':case['pixels'][i],'predicted_pixel':[float(pred[i,0]),float(-pred[i,1])],'residual_px':float(res[i])} for i,label in enumerate(labels)]}
(O/'camera-hypotheses.json').write_text(json.dumps(result,indent=2)+'\n')
