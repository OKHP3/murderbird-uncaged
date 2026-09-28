"""Check pairwise contacts among the seven new solids over 21 packet poses."""
from pathlib import Path
import hashlib,json,runpy
import bpy
from mathutils.geometry import intersect_ray_tri
ROOT=Path(__file__).resolve().parents[5]
NATIVE=ROOT/'assets/models/uncaged-cervical-joint-drive-study-v1/iterations/attempt-02/murderbird-cervical-joint-drive-study-v1.blend'; NSHA='dff9cf74e0b10819f86efed1bdf5c292ae38619d962d18afeba2b2cca291b9d1'
PACKET=ROOT/'assets/audit/cervical-runtime-study-v1/expanded-runtime-poses/pose-snapshot.json'; PSHA='1cb4a2f75ecae625a44c768ba543e9b99e1caa9791a3056e20f5d88bd73d2f26'
OUT=Path(__file__).resolve().parent/'new-part-interfaces.json'
HELPER=ROOT/'assets/audit/cervical-construction-study-v1/attempt-14/all-cervical-roles-source13-baseline/executed-review.py'; GEOM=ROOT/'scripts/diagnose-native-regional-clearance.py'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(NATIVE)==NSHA and sha(PACKET)==PSHA and not OUT.exists()
h=runpy.run_path(str(HELPER),run_name='joint_interface_helpers');g=runpy.run_path(str(GEOM),run_name='joint_interface_geometry')
bpy.ops.wm.open_mainfile(filepath=str(NATIVE));pivots={o.name:o for o in bpy.data.objects if o.type=='EMPTY'};poses=json.loads(PACKET.read_text())['poses']
names=['Joint-drive fixed bearing liner +1','Joint-drive fixed bearing liner -1','Maker external cervical sector −X','Maker cable attachment eye −X','Mechanic passive cervical lock brace +X','Advanced cervical rotary reaction housing +X','Advanced cervical keyed output collar +X']
objs=[bpy.data.objects[n] for n in names]; counts={}; examples={}
def proper(a,b,pairs):
    A=set();B=set()
    def cross(t,o):
        norm=(o[1]-o[0]).cross(o[2]-o[0])
        if norm.length<1e-12:return False
        norm.normalize()
        for k in range(3):
            p,q=t[k],t[(k+1)%3];d0=norm.dot(p-o[0]);d1=norm.dot(q-o[0])
            if d0*d1>=0 or abs(d0)<=1e-7 or abs(d1)<=1e-7:continue
            hit=intersect_ray_tri(*o,q-p,p,True)
            if hit is not None and (q-p).length_squared:
                tpar=(hit-p).dot(q-p)/(q-p).length_squared
                if 1e-6<tpar<1-1e-6:return True
        return False
    for i,j in pairs:
        ta=[a['points'][v] for v in a['faces'][i]];tb=[b['points'][v] for v in b['faces'][j]]
        if cross(ta,tb) or cross(tb,ta):A.add(i);B.add(j)
    return len(A),len(B)
for pose in poses:
    h['set_pose'](pose,pivots);dg=bpy.context.evaluated_depsgraph_get();s={o.name:g['surface'](o,dg) for o in objs}
    for i,aobj in enumerate(objs):
        for bobj in objs[i+1:]:
            a,b=s[aobj.name],s[bobj.name]
            if not a or not b or not g['bounds_overlap'](a,b):continue
            pairs=a['tree'].overlap(b['tree'])
            if not pairs:continue
            key=f'{aobj.name} <> {bobj.name}';pr=proper(a,b,pairs);counts[key]=counts.get(key,0)+1
            examples[key]={'pose':pose['id'],'triangleCandidates':len(pairs),'strictCrossingTriangles':[pr[0],pr[1]],'owners':[aobj.parent.name,bobj.parent.name]}
result={'nativeSha256':NSHA,'packetSha256':PSHA,'poseCount':len(poses),'pairPoseCounts':counts,'lastExamplePerPair':examples,'limits':['Strict triangle crossing is a sampled surface test.','No separated nearest-distance/fit or strength result is implied.']}
OUT.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
