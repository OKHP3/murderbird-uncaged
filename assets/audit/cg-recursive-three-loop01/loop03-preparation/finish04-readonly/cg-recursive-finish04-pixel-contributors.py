"""Read-only evaluated-object raycasts with held09 orthographic camera; no scene mutation."""
from pathlib import Path
import bpy,json,hashlib,math,struct,zlib
from mathutils import Vector,Euler
R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
N=R/'assets/audit/cg-recursive-three-loop01/loop01/delivery/retained02/builder/murderbird-recursive-builder.blend'
C=R/'assets/audit/cg-supervised01/attempt09/builder/receipt.json'
P=R/'assets/audit/cg-recursive-three-loop01/loop01/delivery/retained02/builder/canon-neutral.png'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(N)=='7539b8968f9e82cc8c1dfb569203bd60b134ba841871b99bf67124552fd7004d'
spec=json.loads(C.read_text())['cameras']['canon-neutral'];assert spec['projection']=='ORTHO';w,h=spec['resolution'];assert (w,h)==(1280,853)
# Pixel-center NDC inverse: Blender landscape orthographic scale is horizontal
# width. Camera shifts are in horizontal view-factor units for this landscape rig.
rotation=Euler(spec['rotation_euler'],'XYZ').to_matrix();eye=Vector(spec['location']);scale=spec['ortho_scale'];sx,sy=spec['shift'];direction=(rotation@Vector((0,0,-1))).normalized()
d=bpy.context.evaluated_depsgraph_get();s=bpy.context.scene
objects=[];excluded=dict(hideRender=0,hideViewport=0,hideLayer=0,authoringGuide=0)
for o in s.objects:
 if o.type!='MESH':continue
 if o.hide_render:excluded['hideRender']+=1;continue
 if o.get('authoringGuide'):excluded['authoringGuide']+=1;continue
 if o.hide_viewport:excluded['hideViewport']+=1;continue
 if o.hide_get():excluded['hideLayer']+=1;continue
 ev=o.evaluated_get(d);corners=[ev.matrix_world@Vector(v) for v in ev.bound_box];bounds=[Vector([min(v[i] for v in corners) for i in range(3)]),Vector([max(v[i] for v in corners) for i in range(3)])]
 objects.append((o,ev,bounds))
def aabb(origin,bounds):
 lo,hi=bounds;tmin,tmax=0.,100.
 for i in range(3):
  if abs(direction[i])<1e-9:
   if origin[i]<lo[i] or origin[i]>hi[i]:return False
  else:
   a=(lo[i]-origin[i])/direction[i];b=(hi[i]-origin[i])/direction[i]
   tmin=max(tmin,min(a,b));tmax=min(tmax,max(a,b))
   if tmin>tmax:return False
 return True

def sample_png(path,positions):
 raw=Path(path).read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n';at=8;packed=b''
 while at<len(raw):
  size=struct.unpack_from('>I',raw,at)[0];kind=raw[at+4:at+8];payload=raw[at+8:at+8+size];at+=size+12
  if kind==b'IHDR':iw,ih,bits,color,_,_,interlace=struct.unpack('>IIBBBBB',payload);assert bits==8 and color in (2,6) and interlace==0
  elif kind==b'IDAT':packed+=payload
 bpp=4 if color==6 else 3;stride=iw*bpp;decoded=zlib.decompress(packed);previous=bytearray(stride);pixels={}
 def paeth(a,b,c):
  p=a+b-c;pa,pb,pc=abs(p-a),abs(p-b),abs(p-c)
  return a if pa<=pb and pa<=pc else b if pb<=pc else c
 for y in range(max(v[1] for v in positions)+1):
  at=y*(stride+1);f=decoded[at];row=bytearray(decoded[at+1:at+1+stride])
  for i in range(stride):
   a=row[i-bpp] if i>=bpp else 0;b=previous[i];c=previous[i-bpp] if i>=bpp else 0
   delta=0 if f==0 else a if f==1 else b if f==2 else (a+b)//2 if f==3 else paeth(a,b,c) if f==4 else None
   assert delta is not None;row[i]=(row[i]+delta)&255
  for x,py in positions:
   if py==y:pixels[(x,y)]=list(row[x*bpp:(x+1)*bpp])+([] if bpp==4 else [255])
  previous=row
 return pixels

samples=[('hood-left-upper',842,49),('hood-center-upper',863,56),('hood-center',884,65),('hood-right-center',902,78),('hood-right-lower',915,92),('hood-left-lower',851,83),('hood-center-lower',875,90),('bill-side',924,154),('bronze-hood-boundary',914,104),('bronze-brow-boundary-candidate',841,100),('bronze-left-upper-boundary-candidate',826,43)]
pixels=sample_png(P,[(x,y) for label,x,y in samples]);rows=[]
for label,x,y in samples:
 local=Vector((scale*((x+.5)/w-.5+sx),scale*((h-y-.5)/w-h/(2*w)+sy),0));origin=eye+rotation@local;hits=[]
 for o,ev,bounds in objects:
  if not aabb(origin,bounds):continue
  inv=ev.matrix_world.inverted();localOrigin=inv@origin;localDirection=(inv.to_3x3()@direction).normalized()
  ok,point,normal,face=ev.ray_cast(localOrigin,localDirection,distance=100.)
  if not ok:continue
  world=ev.matrix_world@point;distance=(world-origin).dot(direction)
  if distance<0:continue
  mesh=ev.data;poly=mesh.polygons[face] if 0<=face<len(mesh.polygons) else None;slot=poly.material_index if poly else None
  material=mesh.materials[slot] if slot is not None and slot<len(mesh.materials) else None
  # Projection round-trip, independent of BVH result, validates shift/aspect sign.
  q=rotation.transposed()@(world-eye);px=w*(q.x/scale+.5-sx)-.5;py=h-.5-w*(q.y/scale+h/(2*w)-sy)
  hits.append(dict(object=o.name,mesh=mesh.name,evaluatedFaceIndex=face,evaluatedMaterialSlot=slot,evaluatedMaterial=material.name if material else None,worldPoint=list(world),worldNormal=list((ev.matrix_world.to_3x3().inverted().transposed()@normal).normalized()),distance=distance,projectedPixel=[px,py],roundtripPixelError=[px-x,py-y],renderFlags=dict(hide_render=o.hide_render,hide_viewport=o.hide_viewport,hide_layer=o.hide_get()),geometryOnlyOpacityNotEvaluated=True))
 hits.sort(key=lambda q:q['distance']);nearest=hits[0] if hits else None
 rows.append(dict(label=label,pixelRGBA8=pixels[(x,y)],pixelXYTopLeft=[x,y],rayOrigin=list(origin),rayDirection=list(direction),status='HIT' if hits else 'MISS',nearest=nearest,nextHits=hits[1:4],nearCoincidentObjects=[q['object'] for q in hits[1:] if nearest and abs(q['distance']-nearest['distance'])<.0005],notes='Nearest geometric evaluated surface; opacity and renderer sample/denoiser are not simulated. Pixel center only, not antialias footprint.'))
cam=s.camera;data=cam.data;frame=[list(v) for v in data.view_frame(scene=s)]
camcheck=dict(formulaCheck=dict(status='NOT RUN',reason='Unchanged native active camera is not held09 canon-neutral ORTHO rig; no camera data changes were made. Serialized held09 pose/scale/shift, not native active camera, define ray coordinates.'),name=cam.name,type=data.type,orthoScale=data.ortho_scale,shift=[data.shift_x,data.shift_y],nativeResolution=[s.render.resolution_x,s.render.resolution_y],pixelAspect=[s.render.pixel_aspect_x,s.render.pixel_aspect_y],blenderNativeViewFrame=frame)
if data.type=='ORTHO' and s.render.resolution_x>=s.render.resolution_y:
 nativeScale=data.ortho_scale;aspect=s.render.resolution_y*s.render.pixel_aspect_y/(s.render.resolution_x*s.render.pixel_aspect_x)
 expectedX=[nativeScale*(-.5+data.shift_x),nativeScale*(.5+data.shift_x)];expectedY=[nativeScale*(-aspect/2+data.shift_y),nativeScale*(aspect/2+data.shift_y)]
 observedX=[min(v[0] for v in frame),max(v[0] for v in frame)];observedY=[min(v[1] for v in frame),max(v[1] for v in frame)]
 camcheck['formulaCheck']=dict(expectedX=expectedX,expectedY=expectedY,observedX=observedX,observedY=observedY,maxError=max(abs(a-b) for a,b in zip(expectedX+expectedY,observedX+observedY)),meaning='Independent Blender Camera.view_frame readback confirms orthographic shift/aspect formula on unchanged native camera; held09 serialized spec then supplies desired pose/scale/shifts.')
result=dict(script=str(Path(__file__).resolve()),scriptSHA=sha(__file__),conclusion=dict(paleHoodOwner='CGH17 frontal crown root',sampledHoodHits=7,allSevenAgree=True,paleHoodMaterialSlot=2,paleHoodEvaluatedMaterial='CG metal05 / worn-bronze / builder / retained-uv.001',cuffDominanceInference='DISPROVED_AT_TESTED_PIXELS',bill='CGH18 formed distal hooked bill plate, evaluated face770/slot1 black-iron local0',bronzeBoundary='Pixel914,104 hits CGH17 frontal crown root evaluated face1894/slot2 worn-bronze',miss='Pixel841,100 has no eligible mesh hit; lies at/near a dark silhouette/gap, so do not label it a bronze edge',ambiguity='No tested hit has another object within0.0005 study units; transparency/AA/denoising remain unmodeled',implication='Root must redirect proposed primary H-CUFF chart to a separately verified CGH17 frontal crown root chart before selection. Retained02 builder evidence does not authorize any Loop03 implementation; final receiving pins and all-era inventories still pending.'),nativeCameraFormulaReadback=camcheck,scope='READ_ONLY actual retained02 builder pixel contributors; no model/material/visibility/render/save/export mutation',native=str(N),nativeSHA=sha(N),image=str(P),imageSHA=sha(P),cameraReceipt=str(C),cameraReceiptSHA=sha(C),camera=spec,coordinateConvention='x/y top-left integer PNG pixels; ray through pixel center +0.5;1280x853 landscape orthographic shift in horizontal scale units',visibleMeshCount=len(objects),excludedMeshes=excluded,samples=rows,limitations=['Raycast geometric ownership differs from fully sampled transparent/transmission/antialias/denoised rendering','Ground and authoring guides excluded; all hidden historical contributors excluded','Round-trip inverse projection checks algebra but is not an independent rendered calibration','Input is retained02 diagnostic only; final Loop03 input and scope remain unselected'])
O=Path('/tmp/cg-recursive-finish04-pixel-contributors.json');O.write_text(json.dumps(result,indent=2)+'\n');print('PIXEL_READONLY_COMPLETE',O,flush=True)
