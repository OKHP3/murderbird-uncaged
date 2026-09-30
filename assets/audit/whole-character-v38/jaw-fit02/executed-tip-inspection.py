import bpy,json,sys
from pathlib import Path
from mathutils import Vector
model,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(model));o=bpy.data.objects['V32 formed mandibular bowl'];m=o.data;keys=[(r,k)for r in range(53)for k in range(33)if r<=5 or k<=6 or k>=26];half=len(keys);assert len(m.vertices)==2*half;lookup={k:i for i,k in enumerate(keys)};terminal={i for k,i in lookup.items()if k[0]==52};terminal|={i+half for i in list(terminal)};faces=[{'face':f.index,'indices':list(f.vertices),'actualWorldVertices':[list(o.matrix_world@m.vertices[i].co)for i in f.vertices]}for f in m.polygons if all(i in terminal for i in f.vertices)];adj={i:set()for i in range(len(m.vertices))}
for e in m.edges:a,b=e.vertices;adj[a].add(b);adj[b].add(a)
left=set(adj);components=[]
while left:
 todo=[left.pop()];n=0
 while todo:
  a=todo.pop();n+=1
  for b in adj[a]&left:left.remove(b);todo.append(b)
 components.append(n)
stock=[]
for side,cols in [(-1,range(7)),(1,range(26,33))]:
 for col in cols:
  i=lookup[(52,col)];a=o.matrix_world@m.vertices[i].co;b=o.matrix_world@m.vertices[i+half].co;stock.append({'side':side,'sourceColumn':col,'outerIndex':i,'outerWorld':list(a),'innerWorld':list(b),'sourcePreservedStockVector':list(b-a),'lengthM':(b-a).length})
out.write_text(json.dumps({'actualMesh':o.name,'connectedVertexComponentSizes':components,'terminalClosedStockFaces':faces,'terminalSourceStockPairs':stock,'interpretation':'Small far-side tip sliver belongs to the same connected jaw mesh: its finite terminal closing cap/paired inner rim, not a new or disconnected object. Source root-column stock direction was preserved while distal curve was shortened/upturned; terminal cap may read edge-on and overhang in oblique. Actual self/interobject diagnostics separate. This explains construction visibility, not artistic or fit acceptance.','limits':'Component/topology/cap inventory is not universal self-fold or depth proof; exact view pixel attribution remains inferred.'},indent=2)+'\n')
