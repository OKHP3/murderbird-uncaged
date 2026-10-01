"""Bounded first neck-bearing01: rigid short lower lames and finite race-root routes."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2]
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def components(m):
 links=[set()for _ in m.vertices]
 for e in m.edges:a,b=e.vertices;links[a].add(b);links[b].add(a)
 u=set(range(len(links)));s=[]
 while u:
  q=[u.pop()];n=0
  while q:
   a=q.pop();n+=1
   for b in links[a]&u:u.remove(b);q.append(b)
  s.append(n)
 return sorted(s,reverse=True)
def stock(o):
 bm=bmesh.new();bm.from_mesh(o.data);r={'components':components(o.data),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'signedVolumeM3':bm.calc_volume(signed=True)};bm.free();return r
def annotate(o,description):
 o['neckBearingHistory']=json.dumps({k:json.loads(json.dumps(v,default=lambda x:list(x)))for k,v in o.items()if k in ['constructionDescription','authoringRole','geometryStatus'] or k.endswith('Revision')},separators=(',',':'));o['constructionDescription']=description;o['geometryStatus']='neck-bearing01 proposed passive rigid assembly; finite support/motion and owner acceptance unresolved';o['neckBearingRevision']='neck-bearing01'
def install(o,v,f):
 old=o.data;m=bpy.data.meshes.new(o.name+' neck bearing stock');m.from_pydata([o.matrix_world.inverted()@p for p in v],[],f);m.update()
 for a in old.materials:m.materials.append(a)
 bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();o.data=m
 for p in m.polygons:p.use_smooth=True

def intersection_volume(a,b):
 # Temporary evaluated Boolean proves finite shared stock volume, not weld/fastener validity.
 m=a.data.copy();temp=bpy.data.objects.new('temporary seat-volume diagnosis',m);bpy.context.scene.collection.objects.link(temp);temp.matrix_world=a.matrix_world.copy();bpy.context.view_layer.update();mod=temp.modifiers.new('finite seat intersection','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=b
 dg=bpy.context.evaluated_depsgraph_get();ev=temp.evaluated_get(dg);q=ev.to_mesh();bm=bmesh.new();bm.from_mesh(q);volume=abs(bm.calc_volume(signed=True));count=len(q.vertices);bm.free();ev.to_mesh_clear();bpy.data.objects.remove(temp,do_unlink=True);bpy.data.meshes.remove(m);return {'intersectionVolumeM3':volume,'intersectionVertices':count,'qualification':'Actual finite common stock volume at intended rigid seat, not continuous welded route/fastener/load proof.'}
def apply():
 bpy.context.view_layer.update();changed=[];guards=[];lands=[]
 for row in(1,2):
  for g in range(1,6):
   o=bpy.data.objects[f'V23 cervical {row} directional guard {g}'];old=[p.co.copy()for p in o.data.vertices];world=[o.matrix_world@p for p in old];o.data=o.data.copy();inv=o.matrix_world.inverted();fixed=[];delta=[]
   # Upper rows / original receiving lands exact. Lower free lames are authored
   # C-profile sections, not an entire-skin projection onto a bearing cylinder.
   for i,p in enumerate(world):
    grid=i%475;r=grid//19;c=grid%19
    if r<=8:fixed.append(i);continue
    t=(r-8)/16;w=ease(t);q=p.copy();direction=(c/18-.5);stagger=(g%2-.5)*.003+direction*.004
    if row==1:
     # Lower guard tips descend and sweep backward toward breast, retaining a
     # compact anterior curvature and no horizontal free shelf.
     q.z=p.z-.015*w+stagger*w
     # New lower profile is carried forward only enough to remain outside the
     # deeper breast at descent. Side seams remain diagonal and separate.
     q.y=p.y-(.014+.004*math.cos((g-3)*.7))*w
    else:
     q.z=p.z-.007*w+stagger*w
     q.y=p.y-.004*w
    o.data.vertices[i].co=inv@q;delta.append((q-p).length)
   o.data.update();assert all(o.data.vertices[i].co==old[i]for i in fixed)
   annotate(o,'Independently rigid directional short shingle: original upper nine parameter rows and receiving stock exact; lower free lap descends diagonally along curved neck-to-breast transition. Original owner/rest/paired wall stock maintained; shared lap fit requires bounded actual pose screen, not certified sweep.')
   changed.append(o.name);guards.append({'name':o.name,'owner':o.parent.name,'protectedOriginalVertices':len(fixed),'parameterGridNotTextureUV':[25,19],'maximumFreeLapDeltaM':max(delta),'stock':stock(o),'upperReceivingRows0Through8Exact':True,'pairWallPreservation':'Paired outer/inner vertices share each authored delta; original paired separation exact, normal wall after forming qualified.'})
 for side in(-1,1):
  o=bpy.data.objects[f'V38 curved-neck formed yoke neck {side}'];race=bpy.data.objects[f'V23 cervical 1 distal race {side}'];guard=bpy.data.objects[f'V23 cervical 1 directional guard {1 if side<0 else 5}'];points=[race.matrix_world@p.co for p in race.data.vertices]
  # Actual anterior cap on outer bearing side: rooted on the annular race,
  # not a remote next link. Select a genuine planar ring-sector quad.
  faces=[p for p in race.data.polygons if len(p.vertices)==4 and max(points[i].x for i in p.vertices)-min(points[i].x for i in p.vertices)<1e-6]
  face=min(faces,key=lambda p:sum(points[i].y for i in p.vertices)/4 + .3*abs(sum(points[i].x for i in p.vertices)/4-side*.0775))
  raw=[points[i]for i in face.vertices];center=sum(raw,Vector())/4
  # Shrink sector by20% within finite land; sink 1mm into actual race stock.
  root=[center+(p-center)*.8-Vector((side*.001,0,0))for p in raw]
  ids=[475+4*19+8,475+4*19+9,475+5*19+9,475+5*19+8];rawend=[guard.matrix_world@guard.data.vertices[i].co for i in ids];ec=sum(rawend,Vector())/4
  end=[p+Vector((0,-.001,0))for p in rawend]
  # Supported lateral dogleg: outboard of 83mm captive tip, then anterior
  # across its own race. Each section is finite rectangular stock, no fan.
  xout=side*.096;midcenter=Vector((xout,min(center.y,ec.y)-.014,(center.z+ec.z)/2));
  a=Vector((0,0,.0025));b=Vector((0,.003,0));mid=[midcenter-a-b,midcenter-a+b,midcenter+a+b,midcenter+a-b]
  # Match section winding by nearest root ordering, retaining real rootcap.
  candidates=[mid[k:]+mid[:k]for k in range(4)]+[list(reversed(mid[k:]+mid[:k]))for k in range(4)]
  mid=min(candidates,key=lambda v:sum((root[i]-v[i]).length_squared for i in range(4)))
  candidates=[end[k:]+end[:k]for k in range(4)]+[list(reversed(end[k:]+end[:k]))for k in range(4)]
  end=min(candidates,key=lambda v:sum((mid[i]-v[i]).length_squared for i in range(4)))
  v=root+mid+end;f=[(3,2,1,0),(8,9,10,11)]
  for k in(0,4):
   for j in range(4):f.append((k+j,k+(j+1)%4,k+4+(j+1)%4,k+4+j))
  install(o,v,f);annotate(o,'Compact same-neck-owner outboard dogleg bracket: finite anterior annular-race root sector, outside captive-pin tip, to protected original side-guard inner root patch. Actual finite root/end common-stock volume sampled; no rigid neck/body bridge or moved pivot. Seat volume does not establish engineering acceptance.')
  changed.append(o.name);lands.append({'name':o.name,'owner':'neck','rootOwner':race.parent.name,'endOwner':guard.parent.name,'sourceRace':race.name,'actualRaceFace':face.index,'actualRaceFaceIndices':list(face.vertices),'actualRootLoopWorld':[list(x)for x in root],'actualMidLoopWorld':[list(x)for x in mid],'actualEndLoopWorld':[list(x)for x in end],'protectedEndGuardIndices':ids,'captivePinHalfSpanM':.083,'outboardRouteX':xout,'rootSeat':intersection_volume(o,race),'endSeat':intersection_volume(o,guard),'stock':stock(o)})
 return {'changedMeshes':changed,'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'guardConstruction':guards,'bearingRoutes':lands,'actualPivotsWorld':{n:list(bpy.data.objects[n].matrix_world.translation)for n in ['neck','cervical-mid-a','cervical-mid-b','cervical-upper','head']},'construction':'Two independently rigid lowest guard courses with retained original upper receiving lands and short diagonal free laps; two owner-local finite annular-race brackets. First torso exterior and supports protected.','protected':'All undeclared meshes/objects including torso liner/33plates/body frame/returns/scapular plates, all pivots/rest transforms/owners/material/era profiles exact. Upper course2 receiving lands exact; no optional half receiver.','limits':['Rigid authored construction proposal, not reference metrology, engineering or owner acceptance.','Common-stock volume qualifies deliberate seats but does not certify weld, fastener or load capacity.','Rest/Maker/captured-pitch/max-pitch samples are not full swept runtime motion.','Unchanged first support fixed frame/pelvic/scapular conflicts remain inherited HOLD.']}
