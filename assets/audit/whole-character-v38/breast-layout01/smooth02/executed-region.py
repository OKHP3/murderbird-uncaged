"""New monotonic rigid lower breast lames on protected actual fuller backing."""
import bpy,bmesh,math,json,bisect,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
LINER='V30 continuous tapered breast liner'
BANDS=[(4,1.001,.867,6),(5,.903,.772,5),(6,.800,.708,4)]
LOWER=[f'V34 formed breast course {r} plate {c}'for r,top,bot,n in BANDS for c in range(1,n+1)]
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def apply():
 bpy.context.view_layer.update();liner=bpy.data.objects[LINER];liner.data.calc_loop_triangles();points=[liner.matrix_world@v.co for v in liner.data.vertices];faces=[tuple(t.vertices)for t in liner.data.loop_triangles];tree=BVHTree.FromPolygons(points,faces,all_triangles=True,epsilon=0)
 def hit(z,a):
  d=Vector((math.sin(a),-math.cos(a),0));origin=Vector((0,-.08,z));h=tree.ray_cast(origin+d*.8,-d,1.2)
  if h[0]is None or h[1].dot(d)<.08:return None
  return h,d
 # A smooth analytic radial loft follows measured section envelope rather
 # than reproducing each backing triangle bump. C1 Hermite interpolation.
 sections=[];fitErrors=[]
 for z in np.linspace(.696,1.025,34):
  maximum=0
  for a in np.arange(.02,1.12,.02):
   if hit(z,a)is None or hit(z,-a)is None:break
   maximum=float(a)
  assert maximum>.18;A=[];samples=[]
  for a in np.linspace(-.90*maximum,.90*maximum,31):
   h,d=hit(z,float(a));radius=(h[0]-Vector((0,-.08,float(z)))).length;A.append([float(a)**(2*k)for k in range(5)]);samples.append(radius)
  coeff=np.linalg.lstsq(np.asarray(A),np.asarray(samples),rcond=None)[0];err=np.asarray(samples)-np.asarray(A)@coeff;fitErrors.extend(float(e)for e in err);sections.append((float(z),maximum*.88,[float(x)for x in coeff]))
 zs=[p[0]for p in sections]
 def interp(z,slot):
  i=max(0,min(len(sections)-2,bisect.bisect_right(zs,z)-1));a,b=zs[i:i+2];t=max(0,min(1,(z-a)/(b-a)))
  values=[p[slot]for p in sections]
  if slot==2:values=[np.asarray(v)for v in values]
  def slope(k):
   lo=max(0,k-1);hi=min(len(zs)-1,k+1);return(values[hi]-values[lo])/(zs[hi]-zs[lo])
  return(2*t**3-3*t*t+1)*values[i]+(t**3-2*t*t+t)*(b-a)*slope(i)+(-2*t**3+3*t*t)*values[i+1]+(t**3-t*t)*(b-a)*slope(i+1)
 def cap(z):return float(interp(z,1))
 def radius(z,a):c=interp(z,2);return float(sum(c[k]*a**(2*k)for k in range(5)))+.0045
 between=[]
 for z in np.linspace(.696,1.025,133):
  values=[radius(float(z),float(a))for a in np.linspace(-cap(float(z)),cap(float(z)),41)];assert min(values)>.06;between.append({'z':float(z),'minimumRadiusM':min(values),'maximumRadiusM':max(values),'halfAngleRad':cap(float(z))})
 def bounds(row,q):
  b4=.886-.031*q+.008*math.sin(math.pi*q);b5=.789-.030*q-.006*math.sin(math.pi*q)
  if row==4:return 1.001+.005*q,b4-.008
  if row==5:return b4+.024,b5-.008
  return b5+.022,.712+.009*q
 rec=[];root=[];R,C=28,20;N=(R+1)*(C+1)
 for row,top,bottom,count in BANDS:
  for col in range(count):
   name=f'V34 formed breast course {row} plate {col+1}';o=bpy.data.objects[name];oldProps={k:json.loads(json.dumps(v,default=lambda x:list(x)))for k,v in o.items()if k in('constructionDescription','geometryStatus','wallM','courseTopM','courseBottomM','courseIndex','lateralSpanRadians','authoringRole','panelKind')or k.endswith('Revision')};center=-1+(col+.5)*2/count;step=2/count;sign=1 if center>0 else-1 if center<0 else 0;outer=[];backing=[];uvs=[]
   for i in range(R+1):
    u=i/R
    for j in range(C+1):
     v=j/C;t=2*v-1
     # Shared smoothly swept boundary curves, not circumferential ring hems.
     q=center+step*.5*.94*t;ztop,zbottom=bounds(row,q);z=ztop+(zbottom-ztop)*u;a=cap(z)*q
     d=Vector((math.sin(a),-math.cos(a),0));base=Vector((0,-.08,z))+d*radius(z,a);offset={4:.0055,5:.0050,6:.0045}[row]+.007*ease(u);outer.append(base+d*offset);backing.append((base,None,offset));uvs.append((u,v))

   inner=[];normals=[]
   for i in range(R+1):
    for j in range(C+1):
     ix=i*(C+1)+j;du=outer[min(i+1,R)*(C+1)+j]-outer[max(i-1,0)*(C+1)+j];dv=outer[i*(C+1)+min(j+1,C)]-outer[i*(C+1)+max(j-1,0)];n=du.cross(dv).normalized();rad=outer[ix]-Vector((0,-.08,outer[ix].z))
     if n.dot(rad)<0:n=-n
     assert n.length>.9;normals.append(n);inner.append(outer[ix]-n*.0035)
   f=[]
   for i in range(R):
    for j in range(C):
     a=i*(C+1)+j;b=a+1;c=a+C+2;d=a+C+1;f.extend([(a,b,c,d),(N+d,N+c,N+b,N+a)])
   boundary=[j for j in range(C+1)]+[i*(C+1)+C for i in range(1,R+1)]+[R*(C+1)+j for j in range(C-1,-1,-1)]+[i*(C+1)for i in range(R-1,0,-1)]
   for a,b in zip(boundary,boundary[1:]+boundary[:1]):f.append((a,N+a,N+b,b))
   m=bpy.data.meshes.new(name+' monotonic broad oblique finite topology');inv=o.matrix_world.inverted();m.from_pydata([inv@p for p in outer+inner],[],f);m.update()
   for mat in o.data.materials:m.materials.append(mat)
   bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),name
   if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
   volume=bm.calc_volume(signed=True);assert volume>0;bm.to_mesh(m);bm.free();o.data=m
   for p in m.polygons:p.use_smooth=True
   assert not o.modifiers;o['constructionHistoryBeforeBreastLayout01']=json.dumps(oldProps,separators=(',',':'));o['constructionDescription']='New broad oblique monotonic surface-parameter rigid breast lame; smooth analytic measured section envelope, finite3.5mm paired normal stock and controlled root-to-free radial lap spacing. Existing owner/era/material and all support hardware unchanged. Full seam/solid clearance unresolved.';o['geometryStatus']='Breast-layout01 newly authored rigid panel topology proposal; finite thickness samples do not certify manufacturing or full assembly';o['wallM']=.0035;o['courseTopM']=top;o['courseBottomM']=bottom;o['courseIndex']=row;o['authoringRole']='Passive independently identified directional lower breast panel, existing breastplate inspection owner';o['panelKind']='broad-oblique-breast';o['breastLayoutRevision']='breast-layout01'
   rec.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'class':'inherited-passive','newGrid':[R,C],'vertices':len(m.vertices),'faces':len(m.polygons),'positiveVolumeM3':volume,'nominalNormalWallM':.0035,'actualPairedNormalWallMaximumErrorM':max(abs((a-b).length-.0035)for a,b in zip(outer,inner)),'oldPerVertexProjectionUsed':False,'sourceOldTopologyDiscarded':True,'sectionAngleCapRangeRad':[min(cap(p.z)for p in outer),max(cap(p.z)for p in outer)]})
   sample=[]
   for ix in[0,C//2,C,R//2*(C+1),N-1]:
    near=tree.find_nearest(inner[ix]);sample.append({'newVertex':ix,'analyticSurfaceSample':True,'innerSurfaceDistanceM':near[3],'radialOuterOffsetM':backing[ix][2]})
   root.append({'name':name,'actualBackingSamples':sample,'meaning':'Finite proposed close-backed sliding lames; positive normal thickness at vertices. No old vertex projection. Actual between-vertex/corner/neighbor clearance decided by triangle screen.'})
 return {'changedMeshes':LOWER,'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'watchMeshes':LOWER,'attachmentAndEraMap':rec,'actualBackingSections':{'zRange':[sections[0][0],sections[-1][0]],'sectionCount':len(sections),'angleStepRad':.02,'availableFootprintInsetFraction':.88,'sampledSections':sections[::5],'radialFitOrder':8,'maximumActualBackingOutsideFitM':max(fitErrors),'analyticEnvelopeAllowanceM':.0045,'betweenKnotChecks':{'sampledSections':len(between),'minimumRadiusM':min(p['minimumRadiusM']for p in between),'maximumRadiusM':max(p['maximumRadiusM']for p in between),'extremaAreDiagnosticOnly':True}},'newPanelBoundaries':{'countPerCourse':[6,5,4],'commonSweep4':'Z=.886-.031q+.008sin(pi*q)','commonSweep5':'Z=.789-.030q-.006sin(pi*q)','row4Top':'Z=1.001+.005q','row6Bottom':'Z=.712+.009q','sharedVerticalLapM':[.032,.030]},'rigidLapControls':{'rootOuterRadialOffsetM':[.0055,.005,.0045],'freeOuterRadialOffsetM':[.0125,.012,.0115],'normalWallM':.0035,'row4To5VerticalLapM':.036,'row5To6VerticalLapM':.028,'lateralBinSpacingFraction':.06,'diagonalFreeEdgeM':.009,'notAFullBandClearanceCertificate':True},'actualBackingSeatingSamples':root,'protected':'Existing liner/integralreceivers/movingreturns/source upper18 and entire torso silhouette/head/neck/hips/wings/legs/feet/pivots/rest/material definitions/era eligibility byte-exact. No support or hardware change.','construction':'New smooth analytic sectionloft with C1 capsule/coefficients and sweeping broad oblique boundaries; protected underlyingliner inside, independently rigid15plates. Actual finite screen decides fullband clearance. No oldtriangle bump projection, scallopedfeatherfield, textureUV/image maps or blankhull.','limits':['Actual stock normals at finite gridvertices are3.5mm apart; full-wall perpendicular thickness/solid sweep/loading not certified.','Backing/return/source uppercourse junctions and original apertures require actual triangle screen; overlap math is not exemption.','Protected fuller supporting contour remains a PROPOSAL; inherited neck/frame/source defects remain unresolved.','No app/runtime edits or artistic/engineering acceptance.']}
