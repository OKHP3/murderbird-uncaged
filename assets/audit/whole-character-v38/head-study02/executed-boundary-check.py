"""Blender FILE -- BASE STUDY01 STUDY02 OUTPUT; read-only protected boundary screen."""
import bpy,json,sys,hashlib,math
from pathlib import Path
base,one,two,output=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not output.exists()
CHEEKS=[f'V33 formed lower cheek receiver {side} {i}' for side in (-1,1) for i in range(2)]
BILLS=[f'V32 returned upper bill course {i}' for i in range(3)]
def load(path):
 bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update()
 return {'points':{n:[list(bpy.data.objects[n].matrix_world@v.co) for v in bpy.data.objects[n].data.vertices] for n in CHEEKS},'bills':{n:json.dumps({'verts':[list(v.co) for v in bpy.data.objects[n].data.vertices],'faces':[list(p.vertices) for p in bpy.data.objects[n].data.polygons],'materials':[m.name for m in bpy.data.objects[n].data.materials]},sort_keys=True) for n in BILLS}}
original=load(base);first=load(one);second=load(two);rows=[]
for label,scene in [('01',first),('02',second)]:
 for name,points in original['points'].items():
  protected=[i for i,p in enumerate(points) if math.hypot(p[1]+.578800007,p[2]-1.725484034)<=.068 or math.hypot(p[1]+.4792000055,p[2]-1.615283966)<=.026]
  delta=max(math.dist(points[i],scene['points'][name][i]) for i in protected)
  assert delta<2e-7,(label,name,delta)
  rows.append({'study':label,'mesh':name,'protectedInnerOpticLipOrJournalBoreVertices':len(protected),'maximumNativeWorldErrorM':delta})
assert first['bills']==second['bills'],'02 changed the frozen01 bill geometry'
output.write_text(json.dumps({'status':'PASS protected inner optic/journal vertices within0.2micrometre arithmetic tolerance; study01/02 bill vertex/face/material data identical','inputs':[str(p) for p in (base,one,two)],'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'boundaryRows':rows,'limits':'Boundary positional check only; receiving lip fit, surface self-intersection and continuous motion are not certified.'},indent=2)+'\n')
print('BOUNDARY_CHECK',json.dumps(rows),flush=True)
