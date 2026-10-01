"""Read-only bounded actual triangle surfaces; no continuous-fit acceptance."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[4];AUDIT=Path(__file__).resolve().parent
receipt=json.loads((AUDIT/'receipt.json').read_text());changed={f'V34 formed breast course {r} plate {i}'for r,n in((1,5),(2,6),(3,7),(4,6),(5,5),(6,4))for i in range(1,n+1)}|{'V30 continuous tapered breast liner','V23 breast moving return -1','V23 breast moving return 1','V30 breast liner receiving tab -1','V30 breast liner receiving tab 1'};LINER='V30 continuous tapered breast liner'
POSE={'neck':.10675220489501955,'cervical-mid-a':.10675220489501955,'cervical-mid-b':.10675220489501955,'cervical-upper':.10675220489501955,'head':-.5090505059024657}
def load(path,posed=False):
 bpy.ops.wm.open_mainfile(filepath=str(path))
 if isinstance(posed,str)and posed=='open':
  o=bpy.data.objects['breastplate'];o.matrix_basis=o.matrix_basis@Matrix.Rotation(o['inspectionOpenRadians'],4,'X')
 elif isinstance(posed,str)and posed=='openExploded':
  cover=bpy.data.objects['breastplate'];cover.matrix_basis=cover.matrix_basis@Matrix.Rotation(cover['inspectionOpenRadians'],4,'X');bpy.data.objects['cranial-cover'].location.z+=.08
  offsets={'breastplate':(-.70,-.18,-.12),'left-mantle':(.39,0,.09),'right-mantle':(-.39,0,.09),'left-wing-shield':(.11,-.12,-.04),'right-wing-shield':(-.11,-.12,-.04),'winding-drive':(-.45,-.22,-.10),'power-core':(.32,-.28,-.05),'processing':(.28,0,.20),'cranial-cover':(0,0,.14)}
  for n,offset in offsets.items():bpy.data.objects[n].location+=__import__('mathutils').Vector(offset)
 elif isinstance(posed,str)and posed=='separated':
  offsets={'breastplate':(-.70,-.18,-.12),'left-mantle':(.39,0,.09),'right-mantle':(-.39,0,.09),'left-wing-shield':(.11,-.12,-.04),'right-wing-shield':(-.11,-.125,-.04),'winding-drive':(-.45,-.22,-.10),'power-core':(.32,-.28,-.05),'processing':(.28,0,.20),'cranial-cover':(0,0,.14)}
  for n,offset in offsets.items():bpy.data.objects[n].location+=__import__('mathutils').Vector(offset)
 elif posed:
  for name,angle in POSE.items():o=bpy.data.objects[name];o.matrix_basis=o.matrix_basis@Matrix.Rotation(angle,4,'X')
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();data={};stocks=[];scopes={k:[]for k in('frame','apparatus','openingReceivers','neck')}
 for o in bpy.data.objects:
  if o.type!='MESH'or o.get('authoringGuide')is True:continue
  owner=o.parent.name if o.parent else None;n=o.name.lower();ancestors=[];p=o.parent
  while p:ancestors.append(p.name);p=p.parent
  if owner=='body'and any(t in n for t in('thoracic formed rib','sternal','hip receiving','hip load bow','pelvic formed load web','breast hinge','breast opening bearing','fixed joined posterior','posteriorstiffener','pelvic load')):scopes['frame'].append(o.name)
  if any(t in n for t in('spring','gearbox','transmission','power','winding','distribution','cervical actuator','processing','mind','brain')):scopes['apparatus'].append(o.name)
  if o.name.startswith(('V23 breast moving return ','V30 breast liner receiving tab ')):scopes['openingReceivers'].append(o.name)
  if any(t in ancestors for t in('neck','cervical-mid-a','cervical-mid-b','cervical-upper','head')):scopes['neck'].append(o.name)
  ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@p.co for p in m.vertices];f=[tuple(t.vertices)for t in m.loop_triangles]
  if v:data[o.name]={'bvh':BVHTree.FromPolygons(v,f,all_triangles=True,epsilon=0),'bounds':[(min(p[i]for p in v),max(p[i]for p in v))for i in range(3)],'owner':owner,'eras':str(o.get('exteriorEras','maker,mechanic,builder')).split(',')}
  if o.name in changed:
   bm=bmesh.new();bm.from_mesh(m);stocks.append({'name':o.name,'triangles':len(f),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'signedVolumeM3':bm.calc_volume(signed=True)});bm.free()
  ev.to_mesh_clear()
 def screen(pairs):
  result=[]
  for a,b in pairs:
   if a==b or a not in data or b not in data:continue
   x,y=data[a],data[b]
   if any(x['bounds'][i][1]<y['bounds'][i][0]or y['bounds'][i][1]<x['bounds'][i][0]for i in range(3)):continue
   hits=x['bvh'].overlap(y['bvh'])
   if hits:result.append({'changed':a,'other':b,'crossingTrianglePairs':len(hits),'changedTriangles':len({t[0]for t in hits}),'otherTriangles':len({t[1]for t in hits}),'owners':[x['owner'],y['owner']],'eraIntersection':sorted(set(x['eras'])&set(y['eras']))})
  return result
 out={k:screen((a,b)for a in sorted(changed)for b in names)for k,names in scopes.items()};out['plateBacking']=screen((a,LINER)for a in sorted(changed)if a!=LINER);plates=sorted(n for n in changed if n.startswith('V34 formed breast course '));out['plateNeighbors']=screen((a,b)for i,a in enumerate(plates)for b in plates[i+1:]);out['namedScopes']=scopes;out['changedEvaluatedStock']=stocks;return out
base=ROOT/'assets/models/whole-character-v38/breast-support01/murderbird-v38-breast-support01.blend';candidate=ROOT/'assets/models/whole-character-v38/breast-support02/murderbird-v38-breast-support02.blend'
out={'method':'Evaluated world-space mesh triangle BVH overlap epsilon0, actual native rest-relative local-X source/candidate pose. Counts include coincident contact, do not measure penetration depth or hidden volume containment.','actualCenterContactAnglesRad':POSE,'inspectionSamples':{'open':'Nativebreastplate inspectionOpenRadians(+1.1) about declaredX; source-restEuler0','openExploded':'Declared+1.1 nativeX opening plus all9 maximum exploded offsets transformed glTF XYZ→native X,-Z,Y; rightwingnativeY−.120m; cranial-cover nativeZ+.08 opening plus+.14 separation. Matched static model pose, not runtime path proof'},'limits':['Bounded named apparatus/frame/neck/receiving surface scope; no full mechanical or motion acceptance.','Root-land contacts can create crossing counts; those counts alone cannot certify surface seating or solid union.','Compared triangle counts are triangulation-dependent; changed counts highlight interface changes but are not physical penetration volume.'],'neutral':{'source':load(base),'candidate':load(candidate)},'centerContact':{'source':load(base,True),'candidate':load(candidate,True)},'open':{'source':load(base,'open'),'candidate':load(candidate,'open')},'openExploded':{'source':load(base,'openExploded'),'candidate':load(candidate,'openExploded')}}
for pose in('neutral','centerContact','open','openExploded'):
 out[pose]['comparison']={}
 for scope in('frame','apparatus','openingReceivers','neck','plateBacking','plateNeighbors'):
  source={(x['changed'],x['other']):x for x in out[pose]['source'][scope]};cand={(x['changed'],x['other']):x for x in out[pose]['candidate'][scope]};out[pose]['comparison'][scope]={'sourcePairs':len(source),'candidatePairs':len(cand),'newPairs':[cand[k]for k in cand.keys()-source.keys()],'removedPairs':[source[k]for k in source.keys()-cand.keys()],'inheritedCountChanges':[{'changed':k[0],'other':k[1],'sourceTrianglePairs':source[k]['crossingTrianglePairs'],'candidateTrianglePairs':cand[k]['crossingTrianglePairs'],'sourceChangedTriangles':source[k]['changedTriangles'],'candidateChangedTriangles':cand[k]['changedTriangles']}for k in source.keys()&cand.keys()if source[k]['crossingTrianglePairs']!=cand[k]['crossingTrianglePairs']]}
(AUDIT/'surface-screen.json').write_text(json.dumps(out,indent=2)+'\n');print('SCREEN',json.dumps({p:out[p]['comparison']for p in('neutral','centerContact','open','openExploded')}))
