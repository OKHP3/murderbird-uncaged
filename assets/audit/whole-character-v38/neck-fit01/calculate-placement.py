import bpy,runpy,json,math
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[3];bpy.ops.wm.open_mainfile(filepath=str(R/'assets/models/whole-character-v38/neck-fit01/murderbird-v38-neck-fit01.blend'));bpy.context.view_layer.update();profile=runpy.run_path(str(R/'assets/audit/whole-character-v38/neck-profile01/attempt02/executed-region.py'))['profile'];out=[]
for name in ['V23 cervical 3 captive pin']+[f'V23 cervical 3 distal race {s}'for s in [-1,1]]+[f'V31 passive cranial load bow {s}'for s in [-1,1]]:
 o=bpy.data.objects[name];v=[o.matrix_world@v.co for v in o.data.vertices];center=sum(p.x for p in v)/len(v);caps=[];wrong=[]
 for p in v:
  if not 1.205<=p.z<=1.574:continue
  f,r,w=profile(p.z);cy=(f+r)/2;ry=(r-f)/2-.0035;q=1-((p.y-cy)/ry)**2
  if q<0:wrong.append(list(p));continue
  allowed=(w-.0035)*math.sqrt(q)-.001
  if 'bow'in name:caps.append({'requiredInboardDelta':max(0,abs(p.x)-allowed),'z':p.z,'x':p.x,'allowedX':allowed})
  elif 'race'in name:caps.append({'allowedCenterX':allowed-abs(abs(p.x)-abs(center)),'z':p.z})
  else:caps.append({'allowedPinHalfSpan':allowed,'z':p.z})
 out.append({'name':name,'oldAbsAxialCenter':abs(center),'minPlacementBound':min(x.get('allowedCenterX',x.get('allowedPinHalfSpan',1))for x in caps),'worstBowWitness':max(caps,key=lambda x:x.get('requiredInboardDelta',0))if'bow'in name else None,'outsideYZCount':len(wrong)})
(P/'calculated-placement.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)
