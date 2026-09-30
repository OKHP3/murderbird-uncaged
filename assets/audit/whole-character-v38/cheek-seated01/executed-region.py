"""Supported finite patch endlands first, asymmetric bridge guards second."""
import bpy,bmesh,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ALLOWED=[f'V38 optic cheek shield {s} {i}' for s in (-1,1) for i in range(3)]
PATCHES=[(('V33 diagonal brow receiver {side} 0',(-.491,1.815)),('V31 fixed temporal receiving wall {side}',(-.366,1.815))), (('V33 formed lower cheek receiver {side} 1',(-.484,1.691)),('V31 fixed temporal receiving wall {side}',(-.406,1.683))), (('V33 formed lower cheek receiver {side} 0',(-.638,1.676)),('V33 formed lower cheek receiver {side} 1',(-.520,1.674)))]
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def apply():
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();records=[]
 def tree(name):
  o=bpy.data.objects[name];e=o.evaluated_get(dg);m=e.to_mesh();t=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);e.to_mesh_clear();return t
 for side in (-1,1):
  for course,patches in enumerate(PATCHES):
   name=f'V38 optic cheek shield {side} {course}';o=bpy.data.objects[name];world=o.matrix_world.copy();inv=world.inverted();old=[v.co.copy() for v in o.data.vertices];assert len(old)==182;targets={n.format(side=side):tree(n.format(side=side)) for n,_ in patches};ends=[];samples=[]
   # Real 10x10mm footprint surveys, all corners/perimeter/center, before any bridge.
   for end,(target,(cy,cz)) in enumerate(patches):
    target=target.format(side=side);hits={}
    for row in range(3):
     y=cy+(row-1)*.005
     for col in range(7):
      z=cz+(col/6-.5)*.010;hit=targets[target].ray_cast(Vector((side*.8,y,z)),Vector((-side,0,0)));assert hit[0] is not None,(name,end,row,col,y,z);normal=hit[1].normalized();normal=normal if normal.x*side>0 else -normal;hits[row,col]=(hit[0],normal);samples.append({'end':end,'row':row,'col':col,'target':target,'surfacePoint':list(hit[0]),'surfaceNormal':list(normal),'front':list(hit[0]+normal*.006),'back':list(hit[0]+normal*.0015),'surfaceGapM':.0015,'stockM':.0045})
    ends.append((target,hits))
   verts=[];normals=[];foot_indices=[]
   a=ends[0][1][1,3][0];b=ends[1][1][1,3][0]
   for row in range(13):
    u=row/12
    for col in range(7):
     v=col/6
     if row<=2:point,normal=ends[0][1][row,col];front=point+normal*.006;foot_indices.append(row*7+col)
     elif row>=10:point,normal=ends[1][1][row-10,col];front=point+normal*.006;foot_indices.append(row*7+col)
     else:
      t=(u-1/6)/(2/3);y=(a.y+.005)*(1-t)+(b.y-.005)*t;width=.010+[.036,.026,.025][course]*math.sin(math.pi*t)**1.2;z=a.z*(1-t)+b.z*t+[.004,-.005,-.028][course]*math.sin(math.pi*t)+(v-.5)*width;x=abs(a.x)*(1-t)+abs(b.x)*t+.006+.009*math.sin(math.pi*t)
      # Only declared receiving scaffold may constrain the free bridge; a bore may have no hit.
      visible=[]
      for target,tgt in targets.items():
       hit=tgt.ray_cast(Vector((side*.8,y,z)),Vector((-side,0,0)))
       if hit[0] is not None:visible.append(abs(hit[0].x))
      if visible:x=max(x,max(visible)+.006)
      front=Vector((side*x,y,z));normal=Vector((side,0,0))
     verts.append(front);normals.append(normal)
   allworld=verts+[p-n*.0045 for p,n in zip(verts,normals)];o.data=o.data.copy()
   for v,p in zip(o.data.vertices,allworld):v.co=inv@p
   o.data.update();bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));closed=all(e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);assert closed and volume>0,name;bm.to_mesh(o.data);bm.free();actual=[world@v.co for v in o.data.vertices];stock=[(actual[i]-actual[i+91]).length for i in range(91)];assert max(abs(s-.0045) for s in stock)<3e-7
   measured=[]
   for q in samples:
    idx=(q['row'] if q['end']==0 else q['row']+10)*7+q['col'];back=actual[idx+91];near=targets[q['target']].find_nearest(back);measured.append({**q,'actualInnerVertex':list(back),'nearestFinitePoint':list(near[0]),'nearestFiniteNormal':list(near[1]),'actualFiniteGapM':near[3]})
   edges=[]
   for end,(target,hits) in enumerate(ends):
    rows=[0,1,2] if end==0 else [10,11,12]
    for row in rows:
     for col in range(7):
      if row not in (rows[0],rows[-1]) and col not in (0,6):continue
      idx=row*7+col
      for other in ([idx+1] if col<6 and row in (rows[0],rows[-1]) else [])+([idx+7] if row<rows[-1] and col in (0,6) else []):
       point=(actual[idx+91]+actual[other+91])*.5;near=targets[target].find_nearest(point);edges.append({'end':end,'edge':[idx,other],'innerMidpoint':list(point),'receiver':target,'nearestFinitePoint':list(near[0]),'normal':list(near[1]),'distanceM':near[3]})
   o['v38CheekSeated']='Finite curved rigid bridge between two surveyed supported endland patches; passive head-owned'
   records.append({'name':name,'owner':o.parent.name,'eras':o.get('exteriorEras'),'constructionClass':o.get('constructionClass'),'materials':[m.name if m else None for m in o.data.materials],'method':'Two actual finite10x10mm sampled endlands joined by tapered curved rigid bridge; 1.5mm normal seat gap and4.5mm normal/axial stock. Orbital void deliberately bridged, not required as support.','changedVertexIndices':[i for i,v in enumerate(o.data.vertices) if v.co!=old[i]],'sameSourceVertexFaceCounts':True,'supportedFootprintSamples':measured,'perimeterMidpointWitnesses':edges,'footprintGapMinMaxM':[min(q['actualFiniteGapM'] for q in measured),max(q['actualFiniteGapM'] for q in measured)],'perimeterGapMinMaxM':[min(q['distanceM'] for q in edges),max(q['distanceM'] for q in edges)],'stockMinMaxM':[min(stock),max(stock)],'maximumMovementM':max((v.co-old[i]).length for i,v in enumerate(o.data.vertices)),'closedEdgeManifold':closed,'positiveVolumeM3':volume})
 return {'changedMeshes':ALLOWED,'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'attachmentAndEraMap':records,'confirmation':'ActualJuly HEAD ONLY curved directional cheek/brow with circular inset optic; actualmaster03 checks wholebird. Footprints chosen on actual finite receiver patches first.','reconstruction':'Exact seatpatch/bridgeform dimensions are authored proposal, not reference metrology/fastener/load approval.','limits':['Six shields only; all optics/front/rear48, corrected lower4, bill397/jaw/truehinge/crown/neck/body/material/pivots exact.','Actual252foot samples/perimeter midpoint gaps/normals verified, not continuous swept fit or manufacturing acceptance.','Sevenpose union36 strict screen remains separate and any introduced contacts blockfit.']}
