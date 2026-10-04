import bpy,json,math,sys,hashlib
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:]
p=Path(args[0]);out=Path(args[1]);bpy.ops.wm.open_mainfile(filepath=str(p));scene=bpy.context.scene;dg=bpy.context.evaluated_depsgraph_get();objects=[o for o in scene.objects if o.get('cgRecursiveSourceHead03')];results=[]
for obj in objects:
 ev=obj.evaluated_get(dg);mesh=ev.to_mesh();issues=[]
 if not mesh.vertices or not mesh.polygons:issues.append('empty evaluated geometry')
 for kind,items in [('vertex',mesh.vertices),('polygon',mesh.polygons)]:
  for item in items:
   data=list(item.co) if kind=='vertex' else list(item.normal)
   if not all(math.isfinite(v) for v in data):issues.append('nonfinite '+kind);break
 bad=sum(f.material_index>=len(ev.material_slots) or ev.material_slots[f.material_index].material is None for f in mesh.polygons)
 if bad:issues.append('missing material faces '+str(bad))
 zero=sum(f.area<1e-12 for f in mesh.polygons)
 results.append({'name':obj.name,'evaluated_vertices':len(mesh.vertices),'evaluated_polygons':len(mesh.polygons),'material_slots':[s.material.name if s.material else None for s in ev.material_slots],'missing_material_faces':bad,'zero_area_polygons':zero,'issues':issues});ev.to_mesh_clear()
report={'status':'PASS' if all(not r['issues'] for r in results) and objects else 'FAIL','input':str(p),'input_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'added_mesh_count':len(objects),'new_material_graphs_created':0,'evaluated_checks':'finite vertices/polygon normals; nonempty geometry; material assigned for every polygon; zero-area counts reported separately','objects':results}
out.write_text(json.dumps(report,indent=2)+'\n');print('CG_SOURCE_HEAD03_GEOMETRY_CHECK',report['status'],len(objects),flush=True)
