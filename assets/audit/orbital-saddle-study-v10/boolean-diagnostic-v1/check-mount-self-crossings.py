"""Strictly test only the recorded nonadjacent mount self-BVH candidates."""
import bpy,bmesh,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'assets/models/uncaged-orbital-saddle-study-v6/murderbird-orbital-saddle-study-v6.blend'
BASE_SHA='cb811241d241b0f18f529979b77635caecb83284b8b4df29c7564d4d2bf55eec'
DIAG=Path(__file__).resolve().parent/'receipt.json'
PRIOR_SCRIPT=Path(__file__).resolve().parent/'diagnose-v10-boolean.py'
OUT=Path(__file__).resolve().parent/'self-crossing-followup.json'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def test_segment_face(p,q,face):
    normal=(face[1]-face[0]).cross(face[2]-face[0])
    if normal.length<1e-12: return None
    normal.normalize()
    d0,d1=normal.dot(p-face[0]),normal.dot(q-face[0])
    if not (d0*d1<0 and abs(d0)>1e-7 and abs(d1)>1e-7): return None
    direction=q-p
    hit=intersect_ray_tri(*face,direction,p,True)
    if hit is None: return None
    t=(hit-p).dot(direction)/max(direction.length_squared,1e-30)
    if 1e-6<t<1-1e-6: return {'segmentFraction':float(t),'worldPointM':[float(v) for v in hit]}
    return None

def strict_pair(i,j,tri_ids,points):
    ta_ids,tb_ids=tri_ids[i],tri_ids[j]
    ta=[points[k] for k in ta_ids]; tb=[points[k] for k in tb_ids]
    intersections=[]
    for edge in range(3):
        hit=test_segment_face(ta[edge],ta[(edge+1)%3],tb)
        if hit: intersections.append({'fromTriangle':i,'toTriangle':j,'edgeIndex':edge,**hit})
        hit=test_segment_face(tb[edge],tb[(edge+1)%3],ta)
        if hit: intersections.append({'fromTriangle':j,'toTriangle':i,'edgeIndex':edge,**hit})
    return intersections

def main():
    assert sha(BASE)==BASE_SHA and not OUT.exists()
    base_diag=json.loads(DIAG.read_text())
    assert base_diag['inputs']['v6Native']['sha256']==BASE_SHA
    bpy.ops.wm.open_mainfile(filepath=str(BASE)); deps=bpy.context.evaluated_depsgraph_get()
    results=[]
    for side in (-1,1):
        obj=bpy.data.objects[f'Forged orbital mounting plate {side}']
        ev=obj.evaluated_get(deps); mesh=ev.to_mesh(); mesh.calc_loop_triangles(); matrix=ev.matrix_world.copy()
        points=[matrix@v.co for v in mesh.vertices]
        tri_ids=[tuple(t.vertices) for t in mesh.loop_triangles]
        tree=BVHTree.FromPolygons(points,tri_ids,all_triangles=True,epsilon=0)
        pairs=set()
        for a,b in tree.overlap(tree):
            if a>=b or set(tri_ids[a])&set(tri_ids[b]): continue
            pairs.add((a,b))
        details=[]; intersecting=[]
        for i,j in sorted(pairs):
            hits=strict_pair(i,j,tri_ids,points)
            row={'triangleIndices':[i,j],'vertexIndices':[list(tri_ids[i]),list(tri_ids[j])],
                 'properEdgeFaceIntersectionCount':len(hits),'intersectionExamples':hits[:4]}
            details.append(row)
            if hits: intersecting.append(row)
        results.append({'side':'left' if side==1 else 'right','mesh':obj.name,
                        'evaluatedLoopTriangleCount':len(tri_ids),'nonadjacentSelfBVHCandidateCount':len(pairs),
                        'properCrossingPairCount':len(intersecting),'candidates':details,
                        'method':'Only broad-phase self-overlap candidates with no shared vertex were tested. A proper crossing requires a noncoplanar triangle edge to cross the other triangle interior; tangencies and coplanar overlaps are excluded.'})
        ev.to_mesh_clear()
    out={'status':'read-only self-crossing follow-up complete','blenderVersion':bpy.app.version_string,
         'inputs':{'v6Native':{'path':str(BASE.relative_to(ROOT)),'sha256':sha(BASE)},
                   'priorDiagnosticScript':{'path':'assets/audit/orbital-saddle-study-v10/boolean-diagnostic-v1/diagnose-v10-boolean.py','sha256':sha(PRIOR_SCRIPT)},
                   'priorDiagnosticReceipt':{'path':str(DIAG.relative_to(ROOT)),'sha256':sha(DIAG)},
                   'selfCrossingScript':{'path':str(Path(__file__).resolve().relative_to(ROOT)),'sha256':sha(Path(__file__).resolve())}},
         'results':results,'limits':['This tests only the exact nonadjacent self-BVH candidate pairs and exact exported evaluated loop triangles. It does not certify all forms of self-intersection or Boolean robustness. No source object was changed; no model was saved or exported.']}
    OUT.write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps({'output':str(OUT),'sides':[{'side':r['side'],'candidates':r['nonadjacentSelfBVHCandidateCount'],'crossings':r['properCrossingPairCount'],'examples':r['intersecting'][:3] if 'intersecting' in r else []} for r in results]},indent=2))
if __name__=='__main__': main()
