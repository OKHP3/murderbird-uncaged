from pathlib import Path
import bpy,hashlib,json
R=Path.cwd();A=R/'assets/audit/orbital-saddle-study-v2/transfer-check-v1'
receipt=json.loads((A.parent/'receipt.json').read_text())
def art(p):return {'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def snapshot(row):
 p=R/row['path'];assert art(p)['sha256']==row['sha256'];bpy.ops.wm.open_mainfile(filepath=str(p));deps=bpy.context.evaluated_depsgraph_get();result={};excluded=[]
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  if o.get('constructionTool'):
   excluded.append(o.name);continue
  e=o.evaluated_get(deps);m=e.to_mesh();m.calc_loop_triangles()
  result[o.name]={'points':[tuple(e.matrix_world@v.co) for v in m.vertices],'triangles':[tuple(t.vertices) for t in m.loop_triangles],'parent':o.parent.name if o.parent else None}
  e.to_mesh_clear()
 return result,excluded
native,tools=snapshot(receipt['native']);review,excluded=snapshot(receipt['reviewDerivative'])
assert set(native)==set(review) and len(native)==699 and not excluded
assert sorted(tools)==sorted(receipt['constructionTools'])
rows=[]
for name,original in native.items():
 other=review[name];assert original['parent']==other['parent'];assert len(original['points'])==len(other['points'])
 maximum=max(abs(a-b) for p,q in zip(original['points'],other['points']) for a,b in zip(p,q));assert maximum<1e-6,(name,maximum)
 assert original['triangles']==other['triangles'],name
 rows.append({'name':name,'vertices':len(original['points']),'triangles':len(original['triangles']),'maximumIndexedCoordinateDeltaM':maximum})
out={'status':'PASS','native':receipt['native'],'rigidReviewDerivative':receipt['reviewDerivative'],'source':art(Path(__file__)),'meshCount':len(rows),'excludedOnlyNamedConstructionTools':tools,'maximumCoordinateDifferenceM':max(r['maximumIndexedCoordinateDeltaM'] for r in rows),'rows':rows,'limits':['Saved-rest evaluated coordinates, triangle order and parent identity only; not normals, all custom data or motion clearance.','Unapplied construction native is a REST-ONLY authoring file. Pose and export the frozen rigid review derivative; otherwise moving Boolean dependencies could recut plates.']}
(A/'receipt.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='rows'}))
