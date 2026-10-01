"""Read-only comparison of the saved jaw envelope and physical root."""
import bpy,json,hashlib,sys
from pathlib import Path
source,candidate,out=map(Path,sys.argv[sys.argv.index('--')+1:])
name='V32 formed mandibular bowl'
def data(p):
 bpy.ops.wm.open_mainfile(filepath=str(p));o=bpy.data.objects[name]
 return [tuple(v.co)for v in o.data.vertices],tuple(tuple(row)for row in o.matrix_local),o.parent.name
av,am,ap=data(source);bv,bm,bp=data(candidate)
keys=[(r,k)for r in range(53)for k in range(33)if r<=5 or k<=6 or k>=26 or r>=49];half=len(keys)
assert half==932 and len(av)==len(bv)==1864
assert av[:half]==bv[:half],'Exterior envelope changed'
protected=[i+layer*half for i,(r,k)in enumerate(keys)if r<=14 for layer in[0,1]]
assert all(av[i]==bv[i]for i in protected),'Jaw root changed'
assert av[283]==bv[283] and am==bm and ap==bp
changed=[i for i in range(len(av))if av[i]!=bv[i]]
report={'status':'PASS','source':str(source),'candidate':str(candidate),'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'candidateSHA256':hashlib.sha256(candidate.read_bytes()).hexdigest(),'exactOuterVertices':half,'exactRootVertices':len(protected),'exactSocketIndex':283,'changedVertexCount':len(changed),'allChangesInInnerFreeWall':all(i>=half and keys[i-half][0]>14 for i in changed),'jawOwnerAndTransformExact':True,'scope':'Saved native jaw vertex/attachment identity only, not collision, material or likeness approval.'}
assert report['allChangesInInnerFreeWall'];out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
