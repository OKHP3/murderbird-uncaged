import bpy, json, hashlib, math
from pathlib import Path
from mathutils import Vector
base=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
v18=base/'assets/models/whole-character-v18/attempt-01/murderbird-whole-character-v18.blend'
v19=base/'assets/models/whole-character-v19/attempt-head03/murderbird-whole-character-v19.blend'
out=base/'assets/audit/whole-character-v19/attempt-head03/bill-surface-check.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def xyz(v):return [round(float(a),7) for a in v]
def inspect_obj(o,dg):
    ev=o.evaluated_get(dg); me=ev.to_mesh(); mw=ev.matrix_world.copy()
    ps=[mw@v.co for v in me.vertices]
    edge_uses={}; tri_vol=0.0; polys=[]
    for poly in me.polygons:
        ids=list(poly.vertices); polys.append(ids)
        for a,b in zip(ids,ids[1:]+ids[:1]):
            key=(min(a,b),max(a,b)); edge_uses.setdefault(key,[]).append((a,b))
        if len(ids)>=3:
            p0=ps[ids[0]]
            for i in range(1,len(ids)-1): tri_vol += p0.dot(ps[ids[i]].cross(ps[ids[i+1]]))/6.0
    boundaries=sum(len(x)==1 for x in edge_uses.values()); nonmanifold=sum(len(x)!=2 for x in edge_uses.values())
    winding_errors=sum(1 for x in edge_uses.values() if len(x)==2 and x[0]!=(x[1][1],x[1][0]))
    # Face connected components by shared edges.
    byedge={}
    for fi,ids in enumerate(polys):
        for a,b in zip(ids,ids[1:]+ids[:1]): byedge.setdefault((min(a,b),max(a,b)),[]).append(fi)
    adj=[set() for _ in polys]
    for faces in byedge.values():
        for fi in faces:
            adj[fi].update(fj for fj in faces if fj!=fi)
    seen=set(); components=[]
    for i in range(len(polys)):
        if i in seen:continue
        stack=[i];seen.add(i);n=0
        while stack:
            f=stack.pop();n+=1
            for g in adj[f]:
                if g not in seen:seen.add(g);stack.append(g)
        components.append(n)
    ev.to_mesh_clear()
    return {'name':o.name,'owner':o.parent.name if o.parent else None,'vertices':len(ps),'faces':len(polys),
      'bounds':{'min':[round(min(p[i] for p in ps),6) for i in range(3)],'max':[round(max(p[i] for p in ps),6) for i in range(3)]},
      'boundaryEdges':boundaries,'nonManifoldEdges':nonmanifold,'adjacentWindingErrors':winding_errors,
      'faceComponents':len(components),'componentFaceCounts':components,'evaluatedSignedVolumeM3':round(tri_vol,9)}
# baseline marker
bpy.ops.wm.open_mainfile(filepath=str(v18)); bpy.context.scene.frame_set(1); bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
marker=bpy.data.objects.get('bill-contact'); assert marker
oldmat=marker.matrix_world.copy(); oldpoint=oldmat.translation.copy()
oldbill=[(o.matrix_world@v.co) for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name=='upper-bill' for v in o.data.vertices]
# V19
bpy.ops.wm.open_mainfile(filepath=str(v19)); bpy.context.scene.frame_set(1); bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
marker=bpy.data.objects.get('bill-contact'); assert marker
newmat=marker.matrix_world.copy(); newpoint=newmat.translation.copy()
newbill=[(o.matrix_world@v.co) for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name=='upper-bill' for v in o.data.vertices]
near_old=min(oldbill,key=lambda p:(p-oldpoint).length); near_new=min(newbill,key=lambda p:(p-newpoint).length)
report={'status':'evaluated native surface inspection; no geometry changed','sourceNative':{'path':str(v19.relative_to(base)),'sha256':sha(v19)},'baselineNative':{'path':str(v18.relative_to(base)),'sha256':sha(v18)},
 'evaluatedAtFrame':1,'newBillPanels':[inspect_obj(bpy.data.objects[n],dg) for n in ('V19 fitted proximal bill cheek plate left','V19 fitted proximal bill cheek plate right')],
 'contactMarker':{'name':'bill-contact','owner':marker.parent.name if marker.parent else None,'baselineWorldOrigin':xyz(oldpoint),'attempt03WorldOrigin':xyz(newpoint),'worldMatrixUnchanged':all(abs(oldmat[r][c]-newmat[r][c])<1e-8 for r in range(4) for c in range(4)),
  'baselineNearestUpperBillVertex':xyz(near_old),'attempt03NearestUpperBillVertex':xyz(near_new),'baselineMarkerToBillVertexM':round((near_old-oldpoint).length,7),'attempt03MarkerToBillVertexM':round((near_new-newpoint).length,7)}}
out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
