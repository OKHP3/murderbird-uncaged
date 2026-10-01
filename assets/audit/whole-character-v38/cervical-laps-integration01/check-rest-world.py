"""Independent glTF rest-world preservation check for a relocated skull pivot.
Usage: python3 check-rest-world.py source.glb candidate.glb scope.json
No claim about moved structure, animation, clearance or likeness.
"""
import json,math,struct,sys,hashlib
from pathlib import Path

def load(path):
 b=Path(path).read_bytes();assert b[:4]==b'glTF'
 size=struct.unpack_from('<I',b,12)[0]
 return json.loads(b[20:20+size])
def multiply(a,b):
 return [[sum(a[i][k]*b[k][j]for k in range(4))for j in range(4)]for i in range(4)]
def local(node):
 if 'matrix'in node:
  v=node['matrix'];return [[v[j*4+i]for j in range(4)]for i in range(4)]
 x,y,z,w=node.get('rotation',[0,0,0,1]);s=node.get('scale',[1,1,1]);t=node.get('translation',[0,0,0])
 m=[[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),t[0]],
    [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),t[1]],
    [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y),t[2]],
    [0,0,0,1]]
 for i in range(3):
  for j in range(3):m[i][j]*=s[j]
 return m
def worlds(doc):
 parents={i:j for j,n in enumerate(doc['nodes'])for i in n.get('children',[])};cache={}
 def world(i):
  if i not in cache:cache[i]=multiply(world(parents[i]),local(doc['nodes'][i]))if i in parents else local(doc['nodes'][i])
  return cache[i]
 return {n['name']:world(i)for i,n in enumerate(doc['nodes'])}
def point(m,p):return [sum(m[i][j]*p[j]for j in range(3))+m[i][3]for i in range(3)]
def descendants(doc,name):
 byname={n['name']:i for i,n in enumerate(doc['nodes'])};todo=[byname[name]];result=set()
 while todo:
  i=todo.pop();n=doc['nodes'][i];result.add(n['name']);todo.extend(n.get('children',[]))
 return result
source,candidate,scope_path=sys.argv[1:4];a=load(source);b=load(candidate);scope=json.loads(Path(scope_path).read_text())
na={n['name']:n for n in a['nodes']};nb={n['name']:n for n in b['nodes']};wa=worlds(a);wb=worlds(b)
changed=set(scope['changed']);removed=set(scope.get('removed',[]));head=descendants(a,'head')
checks=[];fail=[]
for name,node in na.items():
 if 'mesh' not in node or name in changed or name in removed:continue
 assert name in nb,name
 error=0
 for primitive in a['meshes'][node['mesh']]['primitives']:
  ac=a['accessors'][primitive['attributes']['POSITION']];lo=ac['min'];hi=ac['max']
  for mask in range(8):
   p=[hi[i]if mask&(1<<i)else lo[i]for i in range(3)];pa=point(wa[name],p);pb=point(wb[name],p)
   error=max(error,math.dist(pa,pb))
 checks.append({'name':name,'headDescendant':name in head,'maxRestBoundsCornerDriftM':error})
 if error>1e-5:fail.append(name)
assert any(c['headDescendant']for c in checks),'No protected head geometry checked'
report={'status':'FAIL'if fail else'PASS','scope':'Rest-world transforms of all unchanged source meshes; source geometry identity must be checked separately. Does not validate relocated structure or movement.',
 'sourceSHA256':hashlib.sha256(Path(source).read_bytes()).hexdigest(),'candidateSHA256':hashlib.sha256(Path(candidate).read_bytes()).hexdigest(),
 'toleranceM':1e-5,'checkedMeshes':len(checks),'protectedHeadMeshes':sum(c['headDescendant']for c in checks),'maxDriftM':max(c['maxRestBoundsCornerDriftM']for c in checks),'failures':fail,'checks':checks}
print(json.dumps(report,indent=2));sys.exit(bool(fail))
