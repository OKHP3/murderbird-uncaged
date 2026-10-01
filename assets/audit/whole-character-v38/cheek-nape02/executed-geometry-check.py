import bpy,bmesh,json,sys
from pathlib import Path
from mathutils import Vector
source,candidate,receipt,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not out.exists();d=json.loads(receipt.read_text());names=d['contract']['changedMeshes'];saved={}
bpy.ops.wm.open_mainfile(filepath=str(source))
for name in names:
 o=bpy.data.objects[name]
 if name.startswith('V38 swept crown course'):saved[name]=[list(v.co)for v in o.data.vertices[:len(o.data.vertices)//2]]
bpy.ops.wm.open_mainfile(filepath=str(candidate));rows=[];bores=[]
for name in names:
 o=bpy.data.objects[name];m=o.data;m.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(m);seen=set();components=0
 for v in bm.verts:
  if v in seen:continue
  components+=1;todo=[v];seen.add(v)
  while todo:
   q=todo.pop()
   for e in q.link_edges:
    n=e.other_vert(q)
    if n not in seen:seen.add(n);todo.append(n)
 row={'name':name,'vertices':len(m.vertices),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'components':components,'signedVolumeM3':bm.calc_volume(signed=True)};bm.free()
 if name in saved:
  n=len(m.vertices)//2;assert [list(v.co)for v in m.vertices[:n]]==saved[name];pairs=[(m.vertices[i+n].co-m.vertices[i].co).length for i in range(n)];projection=[]
  for t in m.loop_triangles:
   if all(k<n for k in t.vertices):
    a,b,c=[m.vertices[k].co for k in t.vertices];normal=(b-a).cross(c-a).normalized()
    projection +=[abs(normal.dot(m.vertices[k+n].co-m.vertices[k].co))for k in t.vertices]
  row.update({'outerCoordinatesExact':True,'actualNormalPairLengthRangeM':[min(pairs),max(pairs)],'actualOuterTriangleStockProjectionRangeM':[min(projection),max(projection)]})
 if name.startswith('V33 formed lower cheek receiver')and name.endswith(' 1'):
  p=[o.matrix_world@v.co for v in m.vertices];r=[((v.y+.4792)**2+(v.z-1.615284)**2)**.5 for v in p];bores.append({'name':name,'actualInnerOuterRadiusM':[min(r),max(r)],'sourceAuthoredBoreRadiusM':.0115,'sourceRetainedAxleRadiusM':.008,'nominalRadialDifferenceM':.0035,'limits':'Actual saved finite receivingrim radii about explicit nativejournal centre. Doesnot prove neighbouringjournal/capfit; strictpairsreportedseparately.'})
 rows.append(row)
out.write_text(json.dumps({'meshes':rows,'receivingBores':bores,'limits':['Normal vertexpairs and triangle projections are bounded stock observations; self/interpart screen required separately.','No continuous solid thickness/loadcertificate.']},indent=2)+'\n')
