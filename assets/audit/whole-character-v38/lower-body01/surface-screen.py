"""Read-only evaluated neutral surface/stock screen. No fabrication or continuous clearance claim."""
import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[4];AUDIT=Path(__file__).resolve().parent
receipt=json.loads((AUDIT/'receipt.json').read_text());changed=set(receipt['contract']['changedMeshes'])
legs={n for n in changed if 'metatars' in n.lower()or'instep' in n or'primary load member' in n}

def load(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();data={};topo=[]
 for o in bpy.data.objects:
  if o.type!='MESH' or o.get('authoringGuide')is True:continue
  ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@p.co for p in m.vertices];f=[tuple(t.vertices)for t in m.loop_triangles]
  if not v:ev.to_mesh_clear();continue
  data[o.name]={'v':v,'f':f,'owner':o.parent.name if o.parent else None,'eras':str(o.get('exteriorEras','maker,mechanic,builder')).split(','),'bvh':BVHTree.FromPolygons(v,f,all_triangles=True,epsilon=0),'min':[min(p[i]for p in v)for i in range(3)],'max':[max(p[i]for p in v)for i in range(3)]}
  if o.name in changed:
   bm=bmesh.new();bm.from_mesh(m);topo.append({'name':o.name,'nativeModifiers':[(x.name,x.type)for x in o.modifiers],'evaluatedVertices':len(m.vertices),'evaluatedTriangles':len(f),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'signedVolumeM3':bm.calc_volume(signed=True),'components':None});bm.free()
  ev.to_mesh_clear()
 pairs=[]
 for n in sorted(legs):
  a=data[n]
  side='left'if'left'in n.lower()else'right';owners=[side+'-thigh',side+'-shin',side+'-foot',side+'-toes',side+'-digit-1-proximal',side+'-digit-2-proximal',side+'-digit-3-proximal']
  for k,b in data.items():
   if k==n or(k in legs and k<n):continue
   if b['owner']not in owners and not(side in k and ('digit' in k or'bearing receiver' in k)):continue
   if any(a['max'][i]<b['min'][i]or b['max'][i]<a['min'][i]for i in range(3)):continue
   hit=a['bvh'].overlap(b['bvh'])
   if hit:pairs.append({'a':n,'b':k,'owners':[a['owner'],b['owner']],'crossingTrianglePairs':len(hit),'eraIntersection':sorted(set(a['eras'])&set(b['eras'])),'sameRigidOwner':a['owner']==b['owner']})
 # Lower torso vs retained mechanism objects: surface crossings, exact posed
 # volumes and hidden containment are deliberately outside this screen.
 apparatus=[n for n in data if any(w in n.lower()for w in ('spring','gearbox','transmission','power','winding','distribution','cervical actuator'))]
 apparatus_hits=[]
 for n in sorted(changed-legs):
  a=data[n]
  for k in apparatus:
   b=data[k]
   if any(a['max'][i]<b['min'][i]or b['max'][i]<a['min'][i]for i in range(3)):continue
   hit=a['bvh'].overlap(b['bvh'])
   if hit:apparatus_hits.append({'a':n,'b':k,'owners':[a['owner'],b['owner']],'crossingTrianglePairs':len(hit),'eraIntersection':sorted(set(a['eras'])&set(b['eras']))})
 return {'changedEvaluatedStock':topo,'legRestCrossings':pairs,'lowerSkinMechanismRestCrossings':apparatus_hits,'mechanismNamedScope':apparatus}
base=load(ROOT/'assets/models/whole-character-v38/upper-contour01/murderbird-v38-upper-contour01.blend');candidate=load(ROOT/'assets/models/whole-character-v38/lower-body01/murderbird-v38-lower-body01.blend')
out={'status':'WARN: exact neutral evaluated triangle-surface crossings reported; no continuous pose/swept clearance or engineering acceptance','method':'Blender evaluated mesh triangles, BVHTree overlap epsilon0; bounding rejection only accelerates; all returned crossings individually listed. Same-owner overlaps are possible fixed fabrication proposals, never blanket exempted. Intersections can include coincident boundaries. Hidden volume containment and finite receiving gaps not inferred from absence of crossings.','source':base,'candidate':candidate,'limits':['Neutral only; root owns actual runtime pose/era assessment.','Apparatus screen only names matched reported scope; no full concealed-supply containment guarantee.','Updated channel interfaces/stock and fixed torso-frame seating need reviewer judgment; topology does not prove valid section attachment.']}
(AUDIT/'surface-screen.json').write_text(json.dumps(out,indent=2)+'\n');print('SCREEN',json.dumps({'sourceLegCrossings':len(base['legRestCrossings']),'candidateLegCrossings':len(candidate['legRestCrossings']),'sourceApparatusCrossings':len(base['lowerSkinMechanismRestCrossings']),'candidateApparatusCrossings':len(candidate['lowerSkinMechanismRestCrossings']),'candidateNonManifold':[p['name']for p in candidate['changedEvaluatedStock']if p['nonManifoldEdges']]}))
