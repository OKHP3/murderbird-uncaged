import bpy,json,hashlib
from pathlib import Path
R=Path('/Users/okh/.codex/worktrees/v38-cervical-envelope/murderbird-uncaged');S=R/'assets/models/whole-character-v38/jaw-stock01/murderbird-v38-jaw-stock01.blend';assert hashlib.sha256(S.read_bytes()).hexdigest()=='507a58f5670677276f8f06d3769deb9eb6cbd178a20f20a2993986d02374f63a';bpy.ops.wm.open_mainfile(filepath=str(S));bpy.context.view_layer.update();out=[]
for o in bpy.data.objects:
 if not o.name.startswith('V38 swept crown course '):continue
 print('COUNT',o.name,o.type,len(o.data.vertices)if o.type=='MESH'else 0,flush=True)
 if o.type!='MESH' or len(o.data.vertices)!=338:continue
 v=[o.matrix_world@p.co for p in o.data.vertices];h=len(v)//2;centers=[v[r*13+6]for r in[0,2,6,12]];out.append({'name':o.name,'owner':o.parent.name,'count':len(v),'rootNative':list(centers[0]),'freeNative':list(centers[-1]),'pathLengthM':sum((v[(i+1)*13+6]-v[i*13+6]).length for i in range(12)),'rowWidthsM':[(v[r*13+12]-v[r*13]).length for r in[0,2,6,12]],'rowStockM':[(v[r*13+6]-v[h+r*13+6]).length for r in[0,2,6,12]],'eras':o.get('exteriorEras'),'construction':o.get('constructionDescription'),'modifiers':[(x.name,x.type)for x in o.modifiers]})
A=R/'assets/audit/whole-character-v38/crown-plate01';(A/'inspect-crown.json').write_text(json.dumps({'sourceSHA256':hashlib.sha256(S.read_bytes()).hexdigest(),'ownerRest':list(sum((list(x)for x in bpy.data.objects['cranial-cover'].matrix_local),[])),'plates':out},indent=2)+'\n');print('PLATES',len(out));print(json.dumps([p for p in out if any(k in p['name']for k in['course 0 column 3','course 2 column 2','course 3 column 3','course 4 column 3'])],indent=2))
