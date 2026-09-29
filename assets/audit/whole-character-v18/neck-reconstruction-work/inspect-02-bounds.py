from pathlib import Path
import json,runpy,bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4]
H=runpy.run_path(str(ROOT/'scripts/diagnose-native-regional-clearance.py'),run_name='surface_helpers')
N=ROOT/'assets/models/whole-character-v18/attempt-neck-reconstruction02/murderbird-whole-character-v18.blend'
bpy.ops.wm.open_mainfile(filepath=str(N));dg=bpy.context.evaluated_depsgraph_get();out={}
for name in ['Throat formed lamina 3','Throat formed lamina 4','Throat formed lamina 5','Throat formed lamina 6','Cervical flank lamina -1 5','Cervical flank lamina -1 6','Lower cervical open backing','Breast inner access shell']:
 s=H['surface'](bpy.data.objects[name],dg);out[name]={'owner':bpy.data.objects[name].parent.name,'evaluatedMin':s['min'],'evaluatedMax':s['max']}
 if name=='Breast inner access shell':
  bins=[]
  for x in [0,.05,.10,.15,.20,.25,.30]:
   points=[p for p in s['points'] if abs(abs(p.x)-x)<.009 and p.y<-.30]
   if points:
    z=max(p.z for p in points);top=[p for p in points if p.z>z-.001]
    bins.append({'absX':x,'frontSurfaceMaxZWithYBelowMinus300mm':z,'topVertexYRange':[min(p.y for p in top),max(p.y for p in top)]})
  out[name]['frontLipSpatialBins']=bins
  samples=[]
  for z in [1.18,1.22,1.26,1.28,1.30,1.32]:
   hit=s['tree'].ray_cast(Vector((0,-1,z)),Vector((0,1,0)),2)
   samples.append({'Z':z,'centerFrontY':hit[0].y if hit[0] else None})
  out[name]['centerFrontSections']=samples
p=ROOT/'assets/audit/whole-character-v18/attempt-neck-reconstruction02/readonly-junction-bounds.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
