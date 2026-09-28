"""Bounded native collision screen and neutral views for joint-drive attempt 02."""
from pathlib import Path
import hashlib, json, math, runpy
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri

ROOT=Path(__file__).resolve().parents[6]
NATIVE=ROOT/'assets/models/uncaged-cervical-joint-drive-study-v1/iterations/attempt-02/murderbird-cervical-joint-drive-study-v1.blend'
NATIVE_SHA='dff9cf74e0b10819f86efed1bdf5c292ae38619d962d18afeba2b2cca291b9d1'
PACKET=ROOT/'assets/audit/cervical-joint-drive-study-v1/inspection-contract-v1/pose-snapshot.json'
PACKET_SHA='3ae1b5a0f81adcb70a567e66c906c4631eebf75758171fc7aeddc7bdf8033781'
MOTION_PACKET=ROOT/'assets/audit/cervical-runtime-study-v1/expanded-runtime-poses/pose-snapshot.json'
MOTION_PACKET_SHA='1cb4a2f75ecae625a44c768ba543e9b99e1caa9791a3056e20f5d88bd73d2f26'
OUT=Path(__file__).resolve().parent
HELPER=ROOT/'assets/audit/cervical-construction-study-v1/attempt-14/all-cervical-roles-source13-baseline/executed-review.py'
GEOM=ROOT/'scripts/diagnose-native-regional-clearance.py'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
if sha(NATIVE)!=NATIVE_SHA or sha(PACKET)!=PACKET_SHA or sha(MOTION_PACKET)!=MOTION_PACKET_SHA: raise RuntimeError('Pinned input hash mismatch')
if any((OUT/n).exists() for n in ['clearance.json','close-up-left.png','close-up-right.png','era-maker.png','era-mechanic.png','era-advanced.png']): raise RuntimeError('Refusing to overwrite evidence')
h=runpy.run_path(str(HELPER),run_name='joint_drive_helpers')
g=runpy.run_path(str(GEOM),run_name='joint_drive_geometry')
bpy.ops.wm.open_mainfile(filepath=str(NATIVE));scene=bpy.context.scene
packet=json.loads(PACKET.read_text());motion_packet=json.loads(MOTION_PACKET.read_text());pivots={o.name:o for o in bpy.data.objects if o.type=='EMPTY'}
new_names=['Joint-drive fixed bearing liner +1','Joint-drive fixed bearing liner -1','Maker external cervical sector −X','Maker cable attachment eye −X','Mechanic passive cervical lock brace +X','Advanced cervical rotary reaction housing +X','Advanced cervical keyed output collar +X']
new=[bpy.data.objects[n] for n in new_names]
owner_roots={'neck','cervical-upper','head','jaw','breastplate','body','left-mantle','right-mantle'}
def is_target(o):
    p=o.parent
    while p:
        if p.name in owner_roots:return True
        p=p.parent
    return False
targets=[o for o in bpy.data.objects if o.type=='MESH' and is_target(o) and o.name not in new_names]
rest={n:o.matrix_world.copy() for n,o in pivots.items()}
def set_rest():
    row=next(p for p in packet['poses'] if p['id']=='runtime-rest'); h['set_pose'](row,pivots); return row
def strict(a,b,pairs):
    idsA=set();idsB=set()
    for ia,ib in pairs:
        ta=[a['points'][v] for v in a['faces'][ia]];tb=[b['points'][v] for v in b['faces'][ib]]
        def crosses(t,o):
            norm=(o[1]-o[0]).cross(o[2]-o[0])
            if norm.length<1e-12:return False
            norm.normalize()
            for k in range(3):
                p,q=t[k],t[(k+1)%3];d0=norm.dot(p-o[0]);d1=norm.dot(q-o[0])
                if d0*d1>=0 or abs(d0)<=1e-7 or abs(d1)<=1e-7:continue
                hit=intersect_ray_tri(*o,q-p,p,True)
                if hit is not None:
                    den=(q-p).length_squared;tpar=(hit-p).dot(q-p)/den if den else -1
                    if 1e-6<tpar<1-1e-6:return True
            return False
        if crosses(ta,tb) or crosses(tb,ta):idsA.add(ia);idsB.add(ib)
    return len(idsA),len(idsB)
def topology(o):
    edges={tuple(sorted(e.vertices)):0 for e in o.data.edges}
    for f in o.data.polygons:
        for i in range(len(f.vertices)):edges[tuple(sorted((f.vertices[i],f.vertices[(i+1)%len(f.vertices)])))]+=1
    return {'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'boundaryEdges':sum(v==1 for v in edges.values()),'nonmanifoldEdges':sum(v!=2 for v in edges.values())}
def containment(target_surf, subject_surf):
    # Multi-ray parity over deterministic decimated subject vertices. This is
    # a sampled screen, not a complete solid-containment proof.
    dirs=[Vector((1,1.414,1.732)).normalized(),Vector((-1.618,1,2.236)).normalized(),Vector((2.645,-1,1)).normalized()]
    result={'samples':0,'inside':0,'outside':0,'ambiguous':0}
    for p in subject_surf['points'][::max(1,len(subject_surf['points'])//80)]:
        par=[]
        for d in dirs:
            origin=p+d*1e-6;hits=0
            for _ in range(64):
                hit=target_surf['tree'].ray_cast(origin,d,4.0)
                if hit[0] is None:break
                hits+=1;origin=hit[0]+d*1e-6
            par.append(hits%2)
        result['samples']+=1
        if len(set(par))!=1:result['ambiguous']+=1
        elif par[0]:result['inside']+=1
        else:result['outside']+=1
    return result

pose_rows=[]
samples=[('motion:'+p['id'],p) for p in motion_packet['poses']]
samples += [('inspection-derived:'+p['id'],p) for p in packet['poses']]
for label,pose in samples:
    h['set_pose'](pose,pivots)
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    surfaces={o.name:g['surface'](o,dg) for o in new+targets}
    hits=[];nearest=[]
    for aobj in new:
        a=surfaces[aobj.name]
        for bobj in targets:
            b=surfaces[bobj.name]
            if not a or not b or not g['bounds_overlap'](a,b):continue
            pairs=a['tree'].overlap(b['tree'])
            if not pairs:continue
            proper=strict(a,b,pairs)
            record={'newPart':aobj.name,'target':bobj.name,'newOwner':aobj.parent.name if aobj.parent else None,'targetOwner':bobj.parent.name if bobj.parent else None,'triangleOverlapCandidates':len(pairs),'strictCrossingTriangles':{'new':proper[0],'target':proper[1]}}
            # Exact keyed/race interfaces only; still report raw candidates.
            if ({aobj.name,bobj.name} in [
              {'Maker external cervical sector −X','Cervical intermediate axle -1'},
              {'Advanced cervical keyed output collar +X','Cervical intermediate axle 1'},
              {'Advanced cervical rotary reaction housing +X','Cervical intermediate clevis 1'},
              {'Joint-drive fixed bearing liner -1','Cervical intermediate axle -1'},
              {'Joint-drive fixed bearing liner +1','Cervical intermediate axle 1'}]):
                record['intentionalInterface']='proposed mating/keyed/bearing pair; exact candidate counts retained for review'
            hits.append(record)
    pose_rows.append({'sample':label,'overlapPairs':hits})

# The 41 direct samples above are linear steps open=0..1 with separation=0.
# Their monotonic order is explicit; the transform follows inspection-pose.js.
summary={'status':'corrected app-derived inspection screen; review required','native':{'path':str(NATIVE.relative_to(ROOT)),'sha256':sha(NATIVE)},'motionPosePacket':{'path':str(MOTION_PACKET.relative_to(ROOT)),'sha256':sha(MOTION_PACKET),'count':len(motion_packet['poses'])},'inspectionPosePacket':{'path':str(PACKET.relative_to(ROOT)),'sha256':sha(PACKET),'count':len(packet['poses']),'source':'Generated by importing actual unchanged applyInspectionPose from the app; matrices match five captured opening anchors per inspection-contract-v1/anchor-proof.json.'},'sampleCount':len(samples),'poseIds':[label for label,_ in samples],'newPartTopology':{o.name:topology(o) for o in new},'poses':pose_rows,'limits':['The 41 inspection poses are derived matrix samples, not 41 browser captures.','BVH overlap candidate lists and strict noncoplanar edge-through-face tests are surface screens; tangency/coplanar/keyed contact remain candidates for manual classification.','Containment classification is a deterministic decimated multi-ray sample only and was not run globally.','No continuous sweep proof, load, stress, or art approval.']}
(OUT/'clearance.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'samples':len(samples),'pairHitSamples':sum(bool(r['overlapPairs']) for r in pose_rows),'newParts':len(new),'boundaryEdges':{n:v['boundaryEdges'] for n,v in summary['newPartTopology'].items()}},indent=2))
