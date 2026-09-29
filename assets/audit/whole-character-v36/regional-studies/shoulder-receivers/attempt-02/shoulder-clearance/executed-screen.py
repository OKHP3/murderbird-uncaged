"""Bounded pair screen for V36 fixed shoulder receiver study vs V35 base."""
from pathlib import Path
import bpy, hashlib, json, math
from mathutils import Vector, Matrix, Quaternion
from mathutils.geometry import intersect_ray_tri
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[7]
BASE=ROOT/'assets/models/whole-character-v35/attempt-form01/murderbird-whole-character-v35.blend'
BASE_SHA='d2c704ccf89f3f0e7dbeb3613dcdbdd964c4ba69991783783830803eecf59cb0'
CANDIDATE=ROOT/'assets/models/whole-character-v36/regional-studies/shoulder-receivers/attempt-02/murderbird-v36-shoulder-receivers.blend'
CANDIDATE_SHA='ff6e2ea64e41ecfb33a9b8ac9a530ae8a28c8b0793a94e4b80c9e46f316a364f'
OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(BASE)==BASE_SHA and sha(CANDIDATE)==CANDIDATE_SHA
assert not (OUT/'screen.json').exists()
CHANGED={f'V35 scapular receiving plate {side} {i}' for side in (-1,1) for i in range(3)}
CHANGED|={f'V35 oblique thoracic side guard {side} 0' for side in (-1,1)}
CHAIN=['neck','cervical-mid-a','cervical-mid-b','cervical-upper']
PIVOTS=['breastplate','left-mantle','right-mantle','left-wing-shield','right-wing-shield']
STATES=[
 ('rest', (0,0,0,0,0), (0,0,0,0,0)),
 ('maker-neck-jaw', (0,0,0,0,0), (-.14,-.45,.32,.32,0)),
 ('guard', (0,.065,-.24,.18,.38), (0,0,0,0,0)),
 # Existing discrete closed-short-shove envelope paired with the V35 thrust neck pose.
 ('thrust-short-shove', (0,.07,-.64,.18,.72), (-.07,0,-.035,0,0)),
]

def inside(point,tri):
    a,b,c=tri;v0=b-a;v1=c-a;v2=point-a;d00=v0.dot(v0);d01=v0.dot(v1);d11=v1.dot(v1);d20=v2.dot(v0);d21=v2.dot(v1);den=d00*d11-d01*d01
    if abs(den)<1e-18:return False
    u=(d11*d20-d01*d21)/den;v=(d00*d21-d01*d20)/den
    return min(u,v,1-u-v)>1e-6

def edge_cross(p,q,tri):
    n=(tri[1]-tri[0]).cross(tri[2]-tri[0])
    if n.length<1e-12:return False
    n.normalize();d0=n.dot(p-tri[0]);d1=n.dot(q-tri[0])
    if not(d0*d1<0 and abs(d0)>1e-7 and abs(d1)>1e-7):return False
    direction=q-p;hit=intersect_ray_tri(*tri,direction,p,True)
    if hit is None:return False
    t=(hit-p).dot(direction)/max(direction.length_squared,1e-30)
    return 1e-6<t<1-1e-6 and inside(hit,tri)

def pose(assembly,neck_state):
    q_angle,yaw,head_pitch,jaw_pitch,_unused=neck_state
    for n,angle in zip(PIVOTS,assembly):
        o=bpy.data.objects[n]
        o.matrix_local=REST[n]@Matrix.Rotation(angle,4,'X')
    for i,n in enumerate(CHAIN):
        o=bpy.data.objects[n];d=Quaternion((1,0,0),q_angle*.25)
        if i==0:d=d@Quaternion((0,0,1),yaw)
        o.rotation_mode='QUATERNION'
        o.rotation_quaternion=o.matrix_parent_inverse.to_quaternion().inverted()@REST[n].to_quaternion()@d
    for n,angle in [('head',head_pitch),('jaw',jaw_pitch)]:
        o=bpy.data.objects[n];o.rotation_mode='QUATERNION'
        o.rotation_quaternion=o.matrix_parent_inverse.to_quaternion().inverted()@REST[n].to_quaternion()@Quaternion((1,0,0),angle)
    bpy.context.view_layer.update()

def capture(obj,dg):
    ev=obj.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles()
    verts=[ev.matrix_world@v.co for v in m.vertices];tris=[tuple(t.vertices) for t in m.loop_triangles];ev.to_mesh_clear()
    assert verts and all(math.isfinite(c) for v in verts for c in v),obj.name
    bounds=[[min(v[k] for v in verts),max(v[k] for v in verts)] for k in range(3)]
    return {'name':obj.name,'owner':obj.parent.name if obj.parent else '<world>','bounds':bounds,'verts':verts,'tris':tris,'bvh':BVHTree.FromPolygons(verts,tris,all_triangles=True)}

def screen_stage(path,label):
    bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.scene.frame_set(1)
    for o in bpy.data.objects:
        if o.animation_data:o.animation_data_clear()
    bpy.context.view_layer.update()
    for n in PIVOTS+CHAIN+['head','jaw']:
        assert n in bpy.data.objects,n
        bpy.data.objects[n].rotation_mode='QUATERNION'
    REST={n:bpy.data.objects[n].matrix_local.copy() for n in PIVOTS+CHAIN+['head','jaw']}
    # Pose() uses this immutable rest table across the full stage.
    globals()['REST']=REST
    assert CHANGED.issubset(bpy.data.objects.keys()),sorted(CHANGED-set(bpy.data.objects.keys()))
    rows=[]
    for name,assembly,neck_state in STATES:
        pose(assembly,neck_state)
        dg=bpy.context.evaluated_depsgraph_get()
        changed=[capture(bpy.data.objects[n],dg) for n in sorted(CHANGED)]
        targets=[]
        for o in bpy.data.objects:
            if o.type!='MESH' or not o.parent:continue
            parent=o.parent.name
            if parent in ('left-mantle','right-mantle','neck','cervical-mid-a'):
                targets.append(o)
            elif parent=='breastplate' and (o.name.startswith('V23 breast moving return ') or o.name.startswith('V29 breast moving annular seat ') or o.name.startswith('V30 breast liner receiving tab ')):
                targets.append(o)
        target_rows=[capture(o,dg) for o in sorted(targets,key=lambda x:x.name)]
        pairs=[];candidate_pairs=0;strict_tri_total=0
        for a in changed:
            for b in target_rows:
                if any(a['bounds'][k][1]<b['bounds'][k][0] or b['bounds'][k][1]<a['bounds'][k][0] for k in range(3)):continue
                candidates=a['bvh'].overlap(b['bvh'])
                if candidates:candidate_pairs+=1
                witnesses=[]
                for ia,ib in candidates:
                    A=[a['verts'][v] for v in a['tris'][ia]];B=[b['verts'][v] for v in b['tris'][ib]]
                    if any(edge_cross(A[k],A[(k+1)%3],B) or edge_cross(B[k],B[(k+1)%3],A) for k in range(3)):
                        witnesses.append({'triangleIndices':[ia,ib],'changedTriangleWorld':[[round(c,7) for c in p] for p in A],'neighborTriangleWorld':[[round(c,7) for c in p] for p in B],'centroidWorld':[round(c,7) for c in sum(A+B,Vector())/6]})
                if witnesses:
                    strict_tri_total+=len(witnesses)
                    pairs.append({'receiver':a['name'],'neighbor':b['name'],'owners':[a['owner'],b['owner']],'strictTrianglePairCount':len(witnesses),'firstWitness':witnesses[0]})
        rows.append({'pose':name,'breastAndWingLocalXRad':dict(zip(PIVOTS,assembly)),'neckTuple':list(neck_state),'changedReceiverCount':len(changed),'neighborMeshCount':len(target_rows),'bvhCandidateObjectPairCount':candidate_pairs,'strictObjectPairCount':len(pairs),'strictTrianglePairCount':strict_tri_total,'pairs':pairs})
        print(label,name,'strict',len(pairs),'pairs',flush=True)
    return {'nativeSHA256':sha(path),'stage':label,'poses':rows}

base=screen_stage(BASE,'V35-baseline')
candidate=screen_stage(CANDIDATE,'V36-attempt02')
for old,new in zip(base['poses'],candidate['poses']):
    ids=lambda pose:{tuple(sorted((p['receiver'],p['neighbor']))) for p in pose['pairs']}
    old_ids=ids(old);new_ids=ids(new)
    new['inheritedPairIdentities']=sorted(old_ids&new_ids)
    new['introducedPairIdentities']=sorted(new_ids-old_ids)
    new['resolvedPairIdentities']=sorted(old_ids-new_ids)
result={
 'status':'Bounded read-only distinct-mesh pair comparison; not a clearance or art acceptance result',
 'base':{'path':str(BASE.relative_to(ROOT)),'sha256':BASE_SHA},
 'candidate':{'path':str(CANDIDATE.relative_to(ROOT)),'sha256':CANDIDATE_SHA},
 'changedReceivers':sorted(CHANGED),
 'neighbors':'All meshes parented to left/right mantle, lower neck owners neck/cervical-mid-a, and the breast door return/annular seat/receiving-tab meshes parented to breastplate. Only changed-receiver vs listed-neighbor pairs tested.',
 'poses':'Discrete rest; exact prior V35 maker-neck-jaw values; existing V34 closed-guard joint values; existing closed-short-shove joint values combined with prior V35 thrust-neck values. No continuous interpolation.',
 'method':'Frozen strict edge-through-face kernel copied from the V34 shoulder body-screen: evaluated world triangles, BVH candidate pruning, plane epsilon 1e-7m, edge/barycentric margin 1e-6. Coplanar/tangent contacts and containment are not confirmed. All pair witnesses retained.',
 'limits':['Only eight altered body-owned receivers against the named adjacent moving groups.','This is distinct-mesh strict crossing evidence; it does not test receiver intra-mesh self-intersections, full body clearance, contact seating, physical function or visual likeness.','Pose tuples are authored discrete screens; no live-browser or continuous-motion claim.'],
 'comparison':{'base':base,'candidate':candidate},
 'inputHashesVerified':sha(BASE)==BASE_SHA and sha(CANDIDATE)==CANDIDATE_SHA,
 'executedScriptSHA256':sha(Path(__file__))
}
(OUT/'screen.json').write_text(json.dumps(result,indent=2)+'\n')
assert result['inputHashesVerified']
print('SUMMARY',[(p['pose'],p['strictObjectPairCount'],len(p['introducedPairIdentities']),len(p['inheritedPairIdentities']),len(p['resolvedPairIdentities'])) for p in candidate['poses']],flush=True)
