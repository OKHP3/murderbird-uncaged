"""One supported anterior/side oval backing and directional rigid plate assembly."""
import bpy,bmesh,math,json,bisect
from mathutils import Vector
from mathutils.bvhtree import BVHTree
LINER='V30 continuous tapered breast liner'
COUNTS=[5,6,7,6,5,4]
PLATES=[f'V34 formed breast course {r} plate {c}'for r,n in enumerate(COUNTS,1)for c in range(1,n+1)]
# Authored model controls, not measurements claimed from raster references.
SECTIONS=[(.685,.095,.140),(.725,.170,.230),(.775,.220,.290),(.85,.247,.335),(.95,.258,.360),(1.05,.258,.355),(1.145,.247,.337),(1.205,.231,.300),(1.248,.210,.248)]
CENTER_Y=-.08;ANGLE=1.09

def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
def component(z,k):
 zs=[p[0]for p in SECTIONS];i=max(0,min(len(zs)-2,bisect.bisect_right(zs,z)-1));h=zs[i+1]-zs[i];t=max(0,min(1,(z-zs[i])/h));v=[p[k]for p in SECTIONS];d=[(v[j+1]-v[j])/(zs[j+1]-zs[j])for j in range(len(zs)-1)]
 def m(j):
  if j==0:return d[0]
  if j==len(zs)-1:return d[-1]
  return 0 if d[j-1]*d[j]<=0 else 2*d[j-1]*d[j]/(d[j-1]+d[j])
 return(2*t**3-3*t*t+1)*v[i]+(t**3-2*t*t+t)*h*m(i)+(-2*t**3+3*t*t)*v[i+1]+(t**3-t*t)*h*m(i+1)
def point(z,a):return Vector((component(z,1)*math.sin(a),CENTER_Y-component(z,2)*math.cos(a),z))
def normal(z,a):
 dz=point(z+.0001,a)-point(z-.0001,a);da=point(z,a+.0001)-point(z,a-.0001);n=dz.cross(da).normalized()
 if n.dot(Vector((math.sin(a),-math.cos(a),0)))<0:n=-n
 return n

def solid(surface,rows,cols,wall):
 outer=[surface(i/rows,j/cols)for i in range(rows+1)for j in range(cols+1)];inner=[];N=len(outer);f=[]
 for i in range(rows+1):
  for j in range(cols+1):
   k=i*(cols+1)+j;du=outer[min(rows,i+1)*(cols+1)+j]-outer[max(0,i-1)*(cols+1)+j];dv=outer[i*(cols+1)+min(cols,j+1)]-outer[i*(cols+1)+max(0,j-1)];n=du.cross(dv).normalized();p=outer[k]
   if n.dot(Vector((p.x,p.y-CENTER_Y,0)))<0:n=-n
   assert n.length>.9;inner.append(p-n*wall)
 for i in range(rows):
  for j in range(cols):
   a=i*(cols+1)+j;b=a+1;c=b+cols+1;d=a+cols+1;f.extend([(a,b,c,d),(N+d,N+c,N+b,N+a)])
 edge=[j for j in range(cols+1)]+[i*(cols+1)+cols for i in range(1,rows+1)]+[rows*(cols+1)+j for j in range(cols-1,-1,-1)]+[i*(cols+1)for i in range(rows-1,0,-1)]
 f.extend((a,N+a,N+b,b)for a,b in zip(edge,edge[1:]+edge[:1]));return outer+inner,f

def install(o,v,f,label):
 old=o.data;mesh=bpy.data.meshes.new(o.name+' '+label);inv=o.matrix_world.inverted();mesh.from_pydata([inv@p for p in v],[],f);mesh.update()
 for m in old.materials:mesh.materials.append(m)
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),o.name
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 vol=bm.calc_volume(signed=True);assert vol>0;bm.to_mesh(mesh);bm.free();o.data=mesh
 for p in mesh.polygons:p.use_smooth=True
 return vol

def tree(o):
 o.data.calc_loop_triangles();return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(t.vertices)for t in o.data.loop_triangles],all_triangles=True,epsilon=0)
def bounds(row,q):
 # Directional shoulder-to-hip sweeps, shared boundaries across course identities.
 edges=[1.246-.018*abs(q),1.15-.036*abs(q)+.010*q,1.052-.033*abs(q)-.009*math.sin(math.pi*q),.956-.026*abs(q)+.009*math.sin(math.pi*q),.86-.017*abs(q)-.009*math.sin(math.pi*q),.767-.011*abs(q)+.008*q,.694+.023*abs(q)]
 return edges[row-1]+(.015 if row>1 else 0),edges[row]-(.005 if row<6 else 0)
def annotation(o,role):
 old={k:json.loads(json.dumps(v,default=lambda x:list(x)))for k,v in o.items()if k in('constructionDescription','geometryStatus','wallM','railEndpointWorld','courseTopM','courseBottomM','courseIndex','lateralSpanRadians','panelKind','authoringRole')or k.endswith('Revision')}
 o['historicalConstructionBeforeTorsoCoherent01']=json.dumps(old,separators=(',',':'));o['constructionDescription']=role;o['geometryStatus']='Torso-coherent01 construction proposal; finite interfaces/owner acceptance unresolved';o['torsoCoherentRevision']='torso-coherent01'

def receiving_channel(points):
 w=.025;d=.016;wall=.004;cross=[(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(w/2-wall,d/2),(w/2-wall,-d/2+wall),(-w/2+wall,-d/2+wall),(-w/2+wall,d/2),(-w/2,d/2)];v=[];f=[]
 axis=(points[-1]-points[0]).normalized();a=Vector((1,0,0));a=(a-axis*a.dot(axis)).normalized();b=axis.cross(a).normalized()
 for p in points:v.extend(p+a*x+b*y for x,y in cross)
 for i in range(len(points)-1):
  for j in range(8):a=i*8+j;b=i*8+(j+1)%8;f.append((a,b,b+8,a+8))
 f.extend([tuple(reversed(range(8))),tuple(range((len(points)-1)*8,len(points)*8))]);return v,f

def measure(o):
 v=[o.matrix_world@p.co for p in o.data.vertices];return {'boundsM':[[min(p[i]for p in v),max(p[i]for p in v)]for i in range(3)],'sections':[{'z':z,'samples':len(p),'widthM':max(q.x for q in p)-min(q.x for q in p),'frontY':min(q.y for q in p)}for z in(.725,.775,.85,.95,1.05,1.145)if(p:=[q for q in v if abs(q.z-z)<.009])]}

def apply():
 bpy.context.view_layer.update();liner=bpy.data.objects[LINER];before=measure(liner);oldmap=liner.get('integralPassiveReceivers');returnProof=[]
 for side in(-1,1):
  o=bpy.data.objects[f'V23 breast moving return {side}'];assert len(o.data.vertices)==248;v=[o.matrix_world@p.co for p in o.data.vertices];seat=sum((v[240+j]for j in(0,1,4,5)),Vector())/4;returnProof.append({'return':o.name,'side':side,'sourceRearWebSeatWorld':list(seat),'sourceTerminalRingCenterWorld':list(sum(v[240:248],Vector())/8),'wholeSourceMeshAndEndpointsExact':True})
 vv,ff=solid(lambda u,v:point(.685+(1.248-.685)*u,ANGLE*(2*v-1)),72,52,.004);volume=install(liner,vv,ff,'new coherent oval backing 4mm normal stock');annotation(liner,'New continuous anterior/side oval backing,4mm paired-normal stock; terminal receiving bridges reconstructed from source-exact moving return rear webs. Integral source component history retained separately; no fixed frame/hinge/rig change. All passive eras.');liner['wallM']=.004;liner['previousIntegralReceiverHistory']=oldmap or 'unknown';bpy.context.view_layer.update();outertree=tree(liner);routes=[];added=[]
 for p in returnProof:
  seat=Vector(p['sourceRearWebSeatWorld']);near=outertree.find_nearest(seat);end=near[0]-near[1]*.002;start=seat;points=[start,start.lerp(end,.35),start.lerp(end,.7),end];v,f=receiving_channel(points);name=f'V38 coherent breast receiving bridge {p["side"]}';mesh=bpy.data.meshes.new(name);mesh.from_pydata([liner.matrix_world.inverted()@q for q in v],[],f);mesh.update()
  frame=next((m for m in liner.data.materials if m and 'frame' in m.name.lower()),liner.data.materials[-1]);mesh.materials.append(frame);obj=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(obj);obj.parent=liner.parent;obj.matrix_world=liner.matrix_world.copy();obj['exteriorEras']='maker,mechanic,builder';obj['constructionClass']='inherited-passive';obj['constructionDescription']='Passive25x16mm4mm C receiving route from actual source return rearweb to new finite backing; paired same inspection owner; intended contact not accepted fit.'
  bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges)
  if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
  bm.to_mesh(mesh);bm.free();original=liner.data.copy();mod=liner.modifiers.new('Single integral receiving union '+str(p['side']),'BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=obj
  with bpy.context.temp_override(object=liner,active_object=liner,selected_objects=[liner],selected_editable_objects=[liner]):bpy.ops.object.modifier_apply(modifier=mod.name)
  bm=bmesh.new();bm.from_mesh(liner.data);ok=all(e.is_manifold for e in bm.edges)and bm.calc_volume(signed=True)>0;bm.free()
  if ok:bpy.data.objects.remove(obj,do_unlink=True)
  else:liner.data=original;added.append(name)
  routes.append({**p,'newInnerBackingLandWorld':list(end),'actualShellTriangle':near[2],'routeLengthM':(end-start).length,'nominalChannelCrossSectionM':[.025,.016,.004],'oneBooleanAttempt':True,'unionManifoldPositive':ok,'claim':'Endpoint construction/contact intention, not full cap seating or welded physical support proof. Return mesh/endpoints exact; new bridge may intersect return finite stock and must be screened.'})
 liner['integralPassiveReceivers']=json.dumps(routes,separators=(',',':'));records=[]
 for row,count in enumerate(COUNTS,1):
  for col in range(count):
   o=bpy.data.objects[f'V34 formed breast course {row} plate {col+1}'];center=-1+(col+.5)*2/count;step=2/count
   def surface(u,v):
    q=center+step*.5*.955*(2*v-1);top,bottom=bounds(row,q);z=top+(bottom-top)*u;a=ANGLE*q;offset=.005+.008*ease(u);return point(z,a)+normal(z,a)*offset
   v,f=solid(surface,24,16,.0035);vol=install(o,v,f,'coherent directional oblique3.5mm stock');annotation(o,'New broad directional rigid oval-body plate; shared smooth belly/backing design with20mm vertical laps and normal offsets5mm root to13mm free edge. Existing independent plate identity and breastplate opening owner retained; no textureUV/image-map work. Finite seams require actual surface screen.');o['wallM']=.0035;o['courseIndex']=row;o['courseTopM']=max(q.z for q in v);o['courseBottomM']=min(q.z for q in v);o['lateralSpanRadians']=ANGLE*step*.955;o['panelKind']='directional-breast-belly';o['authoringRole']='Inherited passive independently identified rigid plate on existing inspection owner';records.append({'name':o.name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'wallM':.0035,'closedPositiveVolumeM3':vol})
 checks=[{'z':z,'widthAxisM':2*component(z,1),'frontY':CENTER_Y-component(z,2)}for z in[.685,.725,.775,.85,.95,1.05,1.145,1.205,1.248]]
 bpy.context.view_layer.update();return {'changedMeshes':PLATES+[LINER],'changedNodes':[],'addedMeshes':added,'removedMeshes':[],'watchMeshes':PLATES+[LINER]+added,'attachmentAndEraMap':records,'sourceBasis':'Frozen ribcage-envelope01 attempt02; earlier smooth02 fit artifacts excluded.','modelEnvelopeMeasurements':{'source':before,'candidate':measure(liner),'authoredControls':checks,'notReferenceDimensions':True},'actualReceivingRoutes':routes,'geometryMechanism':'Continuous shape-preserving cubic ellipse-section backing and33 jointly authored broad oblique plates; normal-lap direction5→13mm,3.5mm plate stock/4mm shell.20mm course overlap with downward/back flank sweep; angular sector±1.09rad leaves deliberate bounded machine aperture, not opaque wholebody hull.','protected':'All fixed body frame, apparatus, moving returns including endpoint geometry, hinges/annular seats, named pivots/rest/hierarchy/head/neck/wings/hips/legs/feet/material definitions/era profiles exact; new plates can alter torso exterior.','limits':['New receiving bridges have one Boolean union attempt and manifold check; endpoint/nearest triangle is not continuous finite seating/load acceptance.','All actual source return mesh/endpoint coordinates exact, but relocated shell changes receiving load route; finite crossing screen required.','Existing neck/frame/source defects remain unresolved.','Nominal paired normal wall and analytic controls do not establish physical assembly, full movement or owner likeness.','No new UV, textures, runtime edits or promotion.']}
