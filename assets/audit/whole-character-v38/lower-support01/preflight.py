import bpy,json,runpy,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];AUDIT=Path(__file__).resolve().parent;BASE=ROOT/'assets/models/whole-character-v38/upper-contour01/murderbird-v38-upper-contour01.blend';bpy.ops.wm.open_mainfile(filepath=str(BASE));bpy.context.view_layer.update()
trusses={}
for label in ('Left','Right'):
 o=bpy.data.objects[label+' metatarsus open passive truss'];neighbors={v.index:set()for v in o.data.vertices}
 for e in o.data.edges:a,b=e.vertices;neighbors[a].add(b);neighbors[b].add(a)
 remaining=set(neighbors);parts=[]
 while remaining:
  found=set();queue=[next(iter(remaining))]
  while queue:
   i=queue.pop()
   if i in found:continue
   found.add(i);queue.extend(neighbors[i]-found)
  remaining-=found;parts.append({'vertexIndices':sorted(found),'vertices':len(found),'faces':sum(all(i in found for i in p.vertices)for p in o.data.polygons)})
 trusses[o.name]={'connectedNativeSolidComponents':parts,'description':'Actual source15subsolids:2longitudinalshoulders,1toe-rootcrossmember,6splitreceivingcheeks,6connectingwebs per executedV37recipe. Whole source mesh preserved, including all these vertices/faces.'}
contract=runpy.run_path(str(ROOT/'scripts/regions/v38-lower-support.py'))['apply']();out={'status':'PRE-SAVE source stock/receiver preservation; no saved shape yet','actualSourceSubgeometry':trusses,'contract':contract};(AUDIT/'pre-save-proof.json').write_text(json.dumps(out,indent=2)+'\n')
print('PRE_SAVE_PROOF',json.dumps({'exactReceiverGeometry':contract['receiverGeometryExact'],'componentCounts':{n:[p['vertices']for p in t['connectedNativeSolidComponents']]for n,t in trusses.items()},'finiteDistalWitnesses':[{'name':r['name'],'insideSourceReceiver':r['actualFiniteDistalReceiver']['candidateReceiverInteriorWitnessCount'],'surfaceCrossingPairs':r['actualFiniteDistalReceiver']['surfaceCrossingTrianglePairs']}for r in contract['attachmentAndEraMap']if'actualFiniteDistalReceiver'in r],'changed':len(contract['changedMeshes'])}))
