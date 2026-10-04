import bpy,sys,json,hashlib,math,importlib.util
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[3];folder=root/'assets/audit/cg-supervised-body12/attempt02';native=folder/'murderbird-body12.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(native));s=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();panels=[o for o in s.objects if o.get('cgSupervisedBody12')];guides=[o for o in s.objects if o.get('cgSupervisedBody11')]
trees={};bounds=[];uv=[]
for o in panels:
 ev=o.evaluated_get(deps);md=ev.to_mesh();points=[o.matrix_world@v.co for v in md.vertices];bounds+=points;trees[o.name]=BVHTree.FromPolygons(points,[tuple(p.vertices) for p in md.polygons])
 values=[float(c) for layer in md.uv_layers for p in layer.data for c in p.uv];uv.append(dict(object=o.name,min=min(values),max=max(values),finite=all(math.isfinite(c) for c in values)));ev.to_mesh_clear()
records=[]
for o in panels:
 nu,nv=json.loads(o['body12Grid']);root_count=root_cover=tip_count=tip_buried=interior_count=interior_cover=0;center_tip_count=center_tip_buried=0;longrootcover=0;allhits=[]
 # Sample actual quad centers as surface-area probes, not just boundary edges.
 for p in o.data.polygons:
  co=sum((o.data.vertices[i].co for i in p.vertices),Vector())/len(p.vertices);v=sum(i//nu/(nv-1) for i in p.vertices)/len(p.vertices);n=p.normal.normalized();
  if n.y>0:n=-n
  origin=co+n*.035;hits=[]
  for name,tree in trees.items():
   if name==o.name:continue
   h,hn,idx,dist=tree.ray_cast(origin,-n,.075)
   if h is not None:hits.append((.035-dist,name))
  covered=bool(hits and max(a for a,nm in hits)>.0002)
  u=sum(i%nu/(nu-1) for i in p.vertices)/len(p.vertices)
  same_track_cover=bool([a for a,nm in hits if nm.split()[-1].split('-')[0]==o.name.split()[-1].split('-')[0] and a>.0002])
  if v<=.25:longrootcover+=same_track_cover
  if v>=.82 and .2<u<.8:center_tip_count+=1;center_tip_buried+=covered
  if v<=.25:root_count+=1;root_cover+=covered
  elif v>=.82:tip_count+=1;tip_buried+=covered
  else:interior_count+=1;interior_cover+=covered
  if covered:allhits.append(max(hits))
 records.append(dict(object=o.name,quadCenterAreaProbes=len(o.data.polygons),centerFreeEndSamples=center_tip_count,centerFreeEndBuriedSamples=center_tip_buried,rootCoveredByLongitudinalNeighbor=longrootcover,rootSamples=root_count,rootCoveredByAdjacentPanel=root_cover,rootCoveredFraction=root_cover/max(root_count,1),interiorSamples=interior_count,interiorCoveredByAdjacentPanel=interior_cover,freeEndSamples=tip_count,freeEndBuriedByAdjacentPanel=tip_buried,freeEndBuriedFraction=tip_buried/max(tip_count,1)))
receipt=json.loads((folder/'receipt.json').read_text())
from bpy_extras.object_utils import world_to_camera_view
frame_gates=[];cam=s.camera
character=[o for o in s.objects if o.type=='MESH' and not o.hide_render and not o.get('authoringGuide') and o.name.startswith('CG')]
for label,record in receipt['cameras'].items():
 if not ('whole' in label or label.startswith('turn-')):continue
 cam.location=record['location'];cam.rotation_euler=record.get('rotation_euler',record.get('rotation'));cam.data.type='ORTHO';cam.data.ortho_scale=record['scale'];cam.data.shift_x,cam.data.shift_y=record.get('shift',[0,0]);s.render.resolution_x,s.render.resolution_y=record['resolution'];bpy.context.view_layer.update()
 points=[world_to_camera_view(s,cam,o.matrix_world@Vector(c)) for o in character for c in o.bound_box]
 extent=dict(min=[min(p[i] for p in points) for i in range(2)],max=[max(p[i] for p in points) for i in range(2)])
 frame_gates.append(dict(view=label,characterObjectCount=len(character),projectedBounds=extent,headAndFeetFramingConservativeBoundsPass=all(v>=-.002 for v in extent['min']) and all(v<=1.002 for v in extent['max'])))
mismatches=[name for name,h in receipt['images'].items() if sha(folder/name)!=h]
r=dict(nativeSHA256=sha(native),nativeMatchesReceipt=sha(native)==receipt['nativeSHA256'],imageHashMismatches=mismatches,newPanelCount=len(panels),guideHidden=all(o.hide_render and o.hide_get() for o in guides),evaluatedWorldBounds=dict(min=[min(v[i] for v in bounds) for i in range(3)],max=[max(v[i] for v in bounds) for i in range(3)]),guideEnvelope=dict(xAbsMaximum=.2340206,yAnteriorMinimum=-.4202283),wholeFrameGates=frame_gates,uvChecks=uv,overlap=dict(method='Actual formed panel quad-center probes raycast along local surface normals against every evaluated adjacent panel; roots v<=.25, free ends v>=.82. Surface-area evidence, not edge-line intersections. Approximate sampled area; no pixel-visible area claim.',panels=records,rootsWithSurfaceCoverage=sum(x['rootCoveredByAdjacentPanel']>0 for x in records),panelsWithBuriedFreeEndSamples=sum(x['freeEndBuriedByAdjacentPanel']>0 for x in records)),scope='Read-only audit of final02, no native saved or changed')
(folder/'extra-preservation-and-overlap.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k not in ('uvChecks','overlap')},indent=2));print('rootsCovered',r['overlap']['rootsWithSurfaceCoverage'],'buriedTipPanels',r['overlap']['panelsWithBuriedFreeEndSamples'])
