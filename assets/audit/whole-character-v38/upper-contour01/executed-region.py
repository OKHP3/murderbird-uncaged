"""Upper-contour01: continuous upper-body contour proposal from pinned bill-relationship02.
Four genuine articulated frames remain; small rest translation revision, rigid joints and refitted links.
"""
import bpy,json,math
from mathutils import Vector
CHAIN=['neck','cervical-mid-a','cervical-mid-b','cervical-upper','head']
COLLAR=[f'V33 tapered throat cheek plate {s} {r} {i}'for s in(-1,0,1)for r in(0,1)for i in range(3)]
BREAST=[f'V34 formed breast course {c} plate {i}'for c,n in[(1,5),(2,6)]for i in range(1,n+1)]+['V30 continuous tapered breast liner']+[f'V30 breast liner receiving tab {s}'for s in(-1,1)]
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def apply():
 bpy.context.view_layer.update();world={o.name:o.matrix_world.copy()for o in bpy.data.objects};local={o.name:o.matrix_local.copy()for o in bpy.data.objects};changed=[];records=[];frames=[]
 knots=[(1.215,0.,0.),(1.2735,-.005,-.008),(1.3281,-.014,-.017),(1.3827,-.018,-.027),(1.423884,-.018,-.035)]
 def pathdelta(z):
  if z<=knots[0][0]:return Vector((0,0,0))
  for (a,y0,z0),(b,y1,z1)in zip(knots,knots[1:]):
   if z<=b:
    t=(z-a)/(b-a);return Vector((0,y0+(y1-y0)*t,z0+(z1-z0)*t))
  return Vector((0,-.018,-.035))
 def neckfield(p,guard=False):
  q=p+pathdelta(p.z)
  if guard:
   # Sustained convex anterior line, with little lateral expansion and open side-joint strip.
   w=math.exp(-((p.z-1.305)/.105)**2);cy=-.188-.65*(p.z-1.215);anterior=smooth((cy-p.y)/.09)
   q.y-=.012*w*anterior;q.x*=1+.040*w*anterior
  return q
 neckmeshes=[o for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name in CHAIN[:4]]
 points={o.name:[world[o.name]@v.co for v in o.data.vertices]for o in neckmeshes+[bpy.data.objects[n]for n in COLLAR+BREAST]}
 for name in CHAIN:
  o=bpy.data.objects[name];m=world[name].copy();m.translation+=pathdelta(m.translation.z);o.matrix_world=m;bpy.context.view_layer.update()
  frames.append({'name':name,'sourceWorldTranslation':list(world[name].translation),'candidateWorldTranslation':list(o.matrix_world.translation),'sourceLocalTranslation':list(local[name].translation),'candidateLocalTranslation':list(o.matrix_local.translation),'rotationAxisAndOrientationExact':True})
 for o in neckmeshes:
  rigid=any(k in o.name for k in('captive pin','distal race','root captive shaft'))
  if rigid:
   if 'distal race' in o.name:
    idx=int(o.name.split()[2]);target=CHAIN[idx];m=world[o.name].copy();m.translation+=pathdelta(world[target].translation.z);o.matrix_world=m;bpy.context.view_layer.update()
   records.append({'name':o.name,'role':'Rigid unchanged journal/shaft geometry at actual revised joint center','meshGeometryExact':True})
  else:
   inv=o.matrix_world.inverted();src=points[o.name];guard='directional guard' in o.name
   for v,p in zip(o.data.vertices,src):v.co=inv@neckfield(p,guard)
   o.data.update();changed.append(o.name);records.append({'name':o.name,'role':'Refitted rigid load link between revised joint centers'if not guard else'Existing directional guard follows revised curve, independent owner retained','owner':o.parent.name,'maxWorldVertexDisplacementM':max((neckfield(p,guard)-p).length for p in src)})
 for name in COLLAR:
  o=bpy.data.objects[name];inv=o.matrix_world.inverted();src=points[name];d=pathdelta(world['head'].translation.z)
  for v,p in zip(o.data.vertices,src):
   q=p+d;t=smooth((1.665-p.z)/.19);q.x*=1-.13*t;q.y+=.018*t;q.z-=.006*t;v.co=inv@q
  o.data.update();changed.append(name);records.append({'name':name,'owner':'head','role':'Compact down/back existing throat boundary, revised in conjunction with joint curve; source roots are not claimed approved','sourceFoldStatus':'Inherited topology; strict self/attachment NOT established before visual gate'})
 def breastfield(p):
  t=smooth((p.z-1.09)/.155);q=p.copy();q.z+=.020*t;q.y-=.007*t*max(0,1-abs(p.x)/.28);q.x*=1-.020*t;return q
 for name in BREAST:
  o=bpy.data.objects[name];inv=o.matrix_world.inverted();src=points[name];new=[]
  for i,p in enumerate(src):
   q=p if 'receiving tab'in name and i<8 else breastfield(p);new.append(q);o.data.vertices[i].co=inv@q
  o.data.update()
  if max((p-q).length for p,q in zip(src,new))>1e-7:changed.append(name);records.append({'name':name,'owner':'breastplate','role':'Only upper envelope aboveZ1.09 rises into neck; lower barrel and real return-side tab vertices exact','maxWorldVertexDisplacementM':max((p-q).length for p,q in zip(src,new))})
 # Update authored owner-local runtime attachment points through the same geometry field.
 body=bpy.data.objects['body'];layout=json.loads(body['mechanismLayoutV1']);endpoint=[]
 def native(q):return Vector((q[0],-q[2],q[1]))
 def gltf(q):return [q.x,q.z,-q.y]
 oldneck=world['neck'];newneck=bpy.data.objects['neck'].matrix_world
 for e in layout['cervical']:
  p=oldneck@native(e['neckPoint']);mapped=neckfield(p);old=e['neckPoint'];e['neckPoint']=gltf(newneck.inverted()@mapped);endpoint.append({'role':'Builder cervical','side':e['side'],'sourceNeckLocalGltf':old,'candidateNeckLocalGltf':e['neckPoint'],'sourceWorld':list(p),'candidateWorld':list(mapped),'bodyPointExact':e['bodyPoint'],'surfaceFit':'Common field follows original receiving point; actual finite nearest-face proof still required, not marker-only attachment PASS'})
 old=layout['makerControlOffsets']['neck'];p=oldneck@native(old);mapped=neckfield(p);layout['makerControlOffsets']['neck']=gltf(newneck.inverted()@mapped);endpoint.append({'role':'Maker neck external control','sourceLocalGltf':old,'candidateLocalGltf':layout['makerControlOffsets']['neck'],'sourceWorld':list(p),'candidateWorld':list(mapped)})
 layout['source']='Upper-contour01 authored four-center loadpath and receiving-point field from actual bill-relationship02; exact finite seat/clearance not yet accepted';body['mechanismLayoutV1']=json.dumps(layout,separators=(',',':'))
 bpy.context.view_layer.update();nodes=[n for n in world if bpy.data.objects[n].matrix_world!=world[n] or bpy.data.objects[n].matrix_local!=local[n]];nodes.append('body')
 return {'changedMeshes':sorted(set(changed)),'changedNodes':sorted(set(nodes)),'addedMeshes':[],'removedMeshes':[],'watchMeshes':sorted(set(changed)),'attachmentAndEraMap':records,'revisedJointFrames':frames,'runtimeAttachmentEndpoints':endpoint,'geometryControls':{'headWorldShiftM':[0,-.018,-.035],'upperBreastZLiftM':.020,'upperBreastAnteriorShiftM':.007,'lowerBreastExactBelowZ':1.09,'lowerNeckAnteriorCurveReliefM':.012},'construction':'Retained four articulated joints and rigid journal geometry; continuous shorter S-curve refits load members, guard coverage and upper breast rather than adding a cuff. Head identity local geometry exact except declared18 throat plates.','inspection':'Breastplate pivot/localX+1.1 and actual return-side seats unchanged; upper receiving mismatch including existing16.25mm warning remains unvalidated, not a fit PASS.','protected':'All unrelated body/wing/leg/head identity geometry, era finish profiles and hierarchy remain exact. Head branch rest-position changes are declared, not disguised exclusions.','limits':['Source collar topology remains inherited and may retain folded surfaces; visual gate precedes expanded diagnostics.','Runtime points track common geometry field but exact finite attachment/posed clearance remains unproved.','No owner likeness, continuous motion, load/fabrication or release acceptance.']}
