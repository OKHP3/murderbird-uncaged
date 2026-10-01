"""Read-only finite root-allocation duplicate and coplanar positive-area screen."""
import json,math
from pathlib import Path
P=Path(__file__).resolve().parent
r=json.loads((P/'receipt.json').read_text());patches=r['contract']['actualLeafReceivingPatches']
bows=json.loads((P.parent/'source-bow-stock.json').read_text())
alloc=[{'name':x['leaf'],'receiver':x['receiver'],'triangles':x['worldTriangles']}for x in patches]
for x in r['contract']['actualSharedCarrierBowSeats']:
 v=bows[x['receiver']]['world'];alloc.append({'name':x['carrier'],'receiver':x['receiver'],'triangles':[[v[i]for i in t['sourceIndices']]for t in x['actualSourceTriangles']]})
def sub(a,b):return [x-y for x,y in zip(a,b)]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def area(p):return abs(sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1]for i in range(len(p))))*.5 if len(p)>2 else 0

def overlap(a,b):
 n=cross(sub(a[1],a[0]),sub(a[2],a[0]));m=cross(sub(b[1],b[0]),sub(b[2],b[0]));ln=math.sqrt(dot(n,n));lm=math.sqrt(dot(m,m))
 if min(ln,lm)<1e-14:return 0
 n=[x/ln for x in n];m=[x/lm for x in m]
 if abs(dot(n,m))<1-1e-6 or max(abs(dot(n,sub(p,a[0])))for p in b)>1e-7:return 0
 axis=max(range(3),key=lambda i:abs(n[i]));project=lambda p:[p[i]for i in range(3)if i!=axis];poly=[project(p)for p in a];clip=[project(p)for p in b]
 orient=1 if sum(clip[i][0]*clip[(i+1)%3][1]-clip[(i+1)%3][0]*clip[i][1]for i in range(3))>=0 else -1
 for i in range(3):
  x=clip[i];y=clip[(i+1)%3]
  def d(p):return orient*((y[0]-x[0])*(p[1]-x[1])-(y[1]-x[1])*(p[0]-x[0]))
  out=[]
  for j,p in enumerate(poly):
   q=poly[(j+1)%len(poly)];dp=d(p);dq=d(q)
   if dp>=0:out.append(p)
   if (dp>=0)!=(dq>=0):
    t=dp/(dp-dq);out.append([p[k]+t*(q[k]-p[k])for k in range(2)])
  poly=out
  if not poly:return 0
 return area(poly)/abs(n[axis])
issues=[];duplicates=[];tested=0
for i,a in enumerate(alloc):
 for b in alloc[i+1:]:
  for ia,ta in enumerate(a['triangles']):
   ha=tuple(sorted(tuple(round(x,8)for x in p)for p in ta))
   for ib,tb in enumerate(b['triangles']):
    tested+=1;hb=tuple(sorted(tuple(round(x,8)for x in p)for p in tb))
    if ha==hb:duplicates.append({'a':a['name'],'b':b['name'],'triangleIndices':[ia,ib]})
    ov=overlap(ta,tb)
    if ov>1e-12:issues.append({'a':a['name'],'b':b['name'],'triangleIndices':[ia,ib],'coplanarOverlapAreaM2':ov})
out={'status':'Allocation screen only; assembled carrier landing remains HOLD','method':'Compare source finite receiving patches between distinct new allocations; exact coordinate triangle key rounded1e-8m and coplanar normals tolerance1e-6/plane1e-7m with projected polygon clipping, positive area threshold1e-12m2. Includes nine leaf roots and two carrier bow roots. Does not certify whole seat area contact, containment, carrier connectivity strength or fabrication.','allocations':[{'name':a['name'],'receiver':a['receiver'],'triangleCount':len(a['triangles'])}for a in alloc],'distinctAllocationTriangleComparisons':tested,'duplicateFiniteTriangles':duplicates,'coplanarPositiveAreaOverlaps':issues,'assembledSupportQualifier':'Left carrier Boolean union misses planned corners by0.003763535525649786m; right sampled corner error0. Corner correspondence does not establish full finite-area seating.'}
(P/'root-allocation-screen.json').write_text(json.dumps(out,indent=2)+'\n');print('ROOT_ALLOCATION',tested,'duplicates',len(duplicates),'coplanarOverlaps',len(issues))
