from pathlib import Path
import bpy,bmesh,json,hashlib,math,collections
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=ROOT/'assets/audit/whole-character-v20/attempt-runtime01/export-integrity'
FILES=[('v19',ROOT/'assets/models/whole-character-v19/attempt-02/murderbird-whole-character-v19.blend'),('runtime01',ROOT/'assets/models/whole-character-v20/attempt-runtime01/murderbird-whole-character-v20.blend')]
NAMES=['V17 breast directional lamina 3 1 left','V17 breast directional lamina 3 1 right'];results=[]
for label,path in FILES:
 oldhash=hashlib.sha256(path.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(path))
 for name in NAMES:
  o=bpy.data.objects[name];m=o.data;rawpoints=[v.co.copy() for v in m.vertices];mods=list(o.modifiers)
  r={'label':label,'name':name,'rawCounts':{'vertices':len(m.vertices),'edges':len(m.edges),'faces':len(m.polygons)},'rawZeroLengthEdgesLE1e10m':[e.index for e in m.edges if (m.vertices[e.vertices[0]].co-m.vertices[e.vertices[1]].co).length<=1e-10], 'duplicateRawPositionCount1e10m':len(rawpoints)-len(set(tuple(round(x,10) for x in p) for p in rawpoints)),'modifiers':[],'prefixes':[]}
  for mod in mods:
   r['modifiers'].append({k:getattr(mod,k,None) for k in ('name','type','thickness','offset','use_even_offset','width','segments','limit_method','angle_limit','use_clamp_overlap','miter_outer','miter_inner','affect')})
  for count in range(len(mods)+1):
   for i,mod in enumerate(mods):mod.show_viewport=i<count
   bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();e=o.evaluated_get(dg);mesh=e.to_mesh();mesh.calc_loop_triangles()
   invalid=[v.index for v in mesh.vertices if not all(math.isfinite(x) for x in v.co)];witness=[]
   for ix in invalid:
    faces=[p for p in mesh.polygons if ix in p.vertices];neighbors=set(v for p in faces for v in p.vertices if v!=ix);good=[mesh.vertices[n].co for n in neighbors if all(math.isfinite(x) for x in mesh.vertices[n].co)]
    witness.append({'index':ix,'coordinates':['nonfinite' if not math.isfinite(x) else x for x in mesh.vertices[ix].co],'incidentFaces':[p.index for p in faces],'finiteNeighborIndices':[n for n in neighbors if all(math.isfinite(x) for x in mesh.vertices[n].co)],'finiteNeighborLocalBounds':[[min(p[i] for p in good),max(p[i] for p in good)] for i in range(3)],'finiteNeighborWorldBounds':[[min((o.matrix_world@p)[i] for p in good),max((o.matrix_world@p)[i] for p in good)] for i in range(3)]})
   deg=0
   for t in mesh.loop_triangles:
    a,b,c=[mesh.vertices[i].co for i in t.vertices];area=((b-a).cross(c-a)).length/2
    if math.isfinite(area) and area<=1e-14:deg+=1
   bm=bmesh.new();bm.from_mesh(mesh);top={'boundary':sum(ed.is_boundary for ed in bm.edges),'wire':sum(ed.is_wire for ed in bm.edges),'over2face':sum(len(ed.link_faces)>2 for ed in bm.edges),'signedVolume':bm.calc_volume(signed=True)};bm.free()
   copy=mesh.copy();before=[v.co.copy() for v in copy.vertices];repaired=copy.validate(verbose=True);changes=[{'index':i,'after':list(v.co)} for i,v in enumerate(copy.vertices) if any(not math.isfinite(x) for x in before[i]) or (v.co-before[i]).length>1e-12]
   r['prefixes'].append({'enabledCount':count,'enabledModifiers':[x.name for x in mods[:count]],'vertices':len(mesh.vertices),'polygons':len(mesh.polygons),'triangles':len(mesh.loop_triangles),'nonfinite':witness,'degenerateTrianglesAreaLE1e14':deg,'topology':top,'validationRepaired':bool(repaired),'coordinateRepairs':changes})
   bpy.data.meshes.remove(copy);e.to_mesh_clear()
  for mod in mods:mod.show_viewport=True
  results.append(r)
 assert hashlib.sha256(path.read_bytes()).hexdigest()==oldhash
(OUT/'lamina-modifier-cause.json').write_text(json.dumps(results,indent=2));print(json.dumps([{'label':r['label'],'name':r['name'],'mods':r['modifiers'],'prefixNonfiniteCounts':[len(p['nonfinite']) for p in r['prefixes']],'rawZeroLengthEdges':r['rawZeroLengthEdgesLE1e10m']} for r in results],indent=2))
