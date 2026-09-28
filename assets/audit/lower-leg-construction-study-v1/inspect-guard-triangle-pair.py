"""Independent pure-Python edge/triangle check for a saved strict receipt pair."""
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
AUDIT=ROOT/'assets/audit/lower-leg-construction-study-v1'
STRICT=AUDIT/'guard-strict-crossings.json'
NATIVE=ROOT/'assets/models/uncaged-lower-leg-construction-study-v1/murderbird-lower-leg-construction-study-v1.blend'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def sub(a,b): return [x-y for x,y in zip(a,b)]
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def inside(p,t):
    v0=sub(t[1],t[0]);v1=sub(t[2],t[0]);v2=sub(p,t[0])
    d00=dot(v0,v0);d01=dot(v0,v1);d11=dot(v1,v1);d20=dot(v2,v0);d21=dot(v2,v1)
    den=d00*d11-d01*d01
    if abs(den)<1e-20:return False
    u=(d11*d20-d01*d21)/den;v=(d00*d21-d01*d20)/den
    return u>=-1e-7 and v>=-1e-7 and u+v<=1+1e-7

d=json.loads(STRICT.read_text())
row=next(r for r in d['rows'] if r['guard'].startswith('left '))
pair=next(p for p in row['strictOrNewMemberPairs'] if p['meshB']=='left shaped shin guard proximal')
example=pair['strictReceipt']['examples'][0]
a=example['subjectRestWorldNativeXYZ'];b=example['targetRestWorldNativeXYZ'];hits=[]
for tri,other,label in ((a,b,'guard-edge-to-source-triangle'),(b,a,'source-edge-to-guard-triangle')):
    n=cross(sub(other[1],other[0]),sub(other[2],other[0]))
    for i in range(3):
        p0,p1=tri[i],tri[(i+1)%3]
        d0=dot(n,sub(p0,other[0]));d1=dot(n,sub(p1,other[0]))
        if d0*d1>=0 or abs(d0-d1)<1e-12:continue
        t=d0/(d0-d1)
        if not 1e-6<t<1-1e-6:continue
        q=[p0[j]+t*(p1[j]-p0[j]) for j in range(3)]
        if inside(q,other):hits.append({'direction':label,'edgeIndex':i,'segmentParameter':t,'pointNativeWorldXYZ':[round(x,9) for x in q]})
assert hits, 'No independent strict edge/triangle intersection reproduced'
result={'status':'independent segment-triangle intersection reproduced from saved strict receipt coordinates',
    'nativeSha256':sha(NATIVE),'strictReceiptSha256':sha(STRICT),'inspectionScriptSha256':sha(Path(__file__)),
    'pair':{'meshA':pair['meshA'],'meshB':pair['meshB'],'triangleIndices':[example['subjectEvaluatedTriangle'],example['targetEvaluatedTriangle']],
      'coordinateFrame':'native rest world XYZ; evaluated triangles transformed through scripts/diagnose-native-regional-clearance.py surface()'},
    'independentIntersections':hits,
    'limits':['Independent check uses the triangle coordinates stored in the strict receipt; it is not a fresh native-mesh extraction.',
      'It confirms a surface crossing point, not penetration depth or continuous-pose clearance.']}
(AUDIT/'guard-triangle-intersection-check.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
