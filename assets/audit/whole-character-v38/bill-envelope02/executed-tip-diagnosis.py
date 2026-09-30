import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
base,candidate,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not out.exists();rows=[]
def head(o):
 while o:
  if o.name=='head':return True
  o=o.parent
 return False
for label,path in [('baseline',base),('candidate',candidate)]:
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();objects=[]
 for o in bpy.data.objects:
  if o.type!='MESH' or not head(o):continue
  pts=[o.matrix_world@v.co for v in o.data.vertices];hit=[i for i,p in enumerate(pts)if abs(p.x)<.04 and p.y<-.735 and p.z<1.58]
  if hit:objects.append({'name':o.name,'owner':o.parent.name if o.parent else None,'vertexCount':len(pts),'tipRegionVertices':len(hit),'tipRegionBounds':[[min(pts[i][k]for i in hit),max(pts[i][k]for i in hit)]for k in range(3)],'wholeBounds':[[min(p[k]for p in pts),max(p[k]for p in pts)]for k in range(3)],'tipWitnesses':[{'vertex':i,'world':list(pts[i])}for i in hit[:5]]})
 rows.append({'model':label,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'objects':objects})
out.write_text(json.dumps({'tipRegionNativeXYZ':'absX<40mm, Y<-735mm, Z<1.58m; actual head-owned finite vertices, not pixel attribution proof','models':rows,'interpretation':'Lists all actual mesh contributors near rendered frayed tip; excluded source detail geometry can remain incompatible with rebuilt primary shell. No shape correction or universal self-intersection claim.'},indent=2)+'\n')
