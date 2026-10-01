import bpy,json,runpy
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[3]
bpy.ops.wm.open_mainfile(filepath=str(R/'assets/models/whole-character-v38/neck-profile01/attempt02/murderbird-v38-neck-profile01-attempt02.blend'));bpy.context.view_layer.update();profile=runpy.run_path(str(R/'assets/audit/whole-character-v38/neck-profile01/attempt02/executed-region.py'))['profile'];rows=[]
for o in bpy.data.objects:
 if o.type!='MESH'or o.get('silhouetteStudyHistoricalHidden')is True or o.get('authoringGuide')is True:continue
 if not(o.name.startswith('V23 cervical ')or o.name.startswith('V31 cranial load bow')or o.name.startswith('V31 passive cranial load bow')or o.name=='V21 head captive shaft'):continue
 v=[o.matrix_world@p.co for p in o.data.vertices];outside=[]
 for i,p in enumerate(v):
  if not 1.205<=p.z<=1.574:continue
  f,r,w=profile(p.z);cy=(f+r)/2;ry=(r-f)/2;val=(p.x/w)**2+((p.y-cy)/ry)**2
  if val>1:outside.append({'index':i,'p':list(p),'ellipseResidual':val-1})
 rows.append({'name':o.name,'owner':o.parent.name,'bounds':[[min(p[i]for p in v),max(p[i]for p in v)]for i in range(3)],'outsideVertexCount':len(outside),'maxNormalizedEllipseResidual':max([x['ellipseResidual']for x in outside],default=0),'strongestWitnesses':sorted(outside,key=lambda x:-x['ellipseResidual'])[:3]})
(P/'inspect-stock.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps([x for x in rows if x['outsideVertexCount']],indent=2),flush=True)
