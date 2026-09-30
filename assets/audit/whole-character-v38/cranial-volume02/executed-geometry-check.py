import bpy,bmesh,json,sys
from pathlib import Path
from mathutils import Vector
source,a,b,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not out.exists();rows=[]
for label,model in [('source',source),('study01',a),('study02',b)]:
 bpy.ops.wm.open_mainfile(filepath=str(model));record={'model':label,'meshes':[]};crown=[]
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  if o.name.startswith('V38 swept crown course'):crown +=[o.matrix_world@v.co for v in o.data.vertices]
  if label=='source' or 'v38CranialVolume'not in o:continue
  bm=bmesh.new();bm.from_mesh(o.data);seen=set();components=0
  for v in bm.verts:
   if v in seen:continue
   components+=1;todo=[v];seen.add(v)
   while todo:
    q=todo.pop()
    for e in q.link_edges:
     n=e.other_vert(q)
     if n not in seen:seen.add(n);todo.append(n)
  pairs=[]
  if o.name.startswith('V38 swept crown course')or o.name in ['V38 compact cranial inner shell','V38 fixed occipital closure plate','V31 frontal cranial cap receiving seat']:
   n=len(o.data.vertices)//2;pv=[o.matrix_world@v.co for v in o.data.vertices];pairs=[(pv[i+n]-pv[i]).length for i in range(n)]
  record['meshes'].append({'name':o.name,'vertices':len(bm.verts),'faces':len(bm.faces),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'connectedComponents':components,'signedLocalVolumeM3':bm.calc_volume(signed=True),'pairedWallLengthMinMaxM':[min(pairs),max(pairs)]if pairs else None});bm.free()
 record['actualCrownAllFiniteVertexBoundsNative']=[[min(p[k]for p in crown),max(p[k]for p in crown)]for k in range(3)];rows.append(record)
out.write_text(json.dumps({'models':rows,'limits':['Closed edge topology/component counts and paired stock vectors do not prove absence of triangle self-intersection.','Normal offset plate stock is a vertex pair length, not minimum continuous solid thickness.','No full-pool interobject/withdrawal motion screen or manufacturing acceptance.']},indent=2)+'\n')
