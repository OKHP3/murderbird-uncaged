"""Strict face-interior self-crossing check and annular station map for V6 mounts."""
import bpy,json,hashlib,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'assets/models/uncaged-orbital-saddle-study-v6/murderbird-orbital-saddle-study-v6.blend'
BASE_SHA='cb811241d241b0f18f529979b77635caecb83284b8b4df29c7564d4d2bf55eec'
V3=ROOT/'scripts/study-orbital-saddle-v3.py'
PRIOR=Path(__file__).resolve().parent/'self-crossing-followup.json'
OUT=Path(__file__).resolve().parent/'annular-self-crossing-map-v2.json'
CENTER_YZ=(-.369,1.786)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def barycentric_inside(p,tri,eps=1e-6):
    a,b,c=tri; v0=b-a; v1=c-a; v2=p-a
    d00=v0.dot(v0); d01=v0.dot(v1); d11=v1.dot(v1); d20=v2.dot(v0); d21=v2.dot(v1)
    den=d00*d11-d01*d01
    if abs(den)<1e-18:return False,None
    u=(d11*d20-d01*d21)/den; v=(d00*d21-d01*d20)/den; w=1-u-v
    return min(u,v,w)>eps,(u,v,w)
def edge_face(p,q,face):
    n=(face[1]-face[0]).cross(face[2]-face[0])
    if n.length<1e-12:return None
    n.normalize(); d0=n.dot(p-face[0]); d1=n.dot(q-face[0])
    if not(d0*d1<0 and abs(d0)>1e-7 and abs(d1)>1e-7):return None
    direction=q-p; hit=intersect_ray_tri(*face,direction,p,True)
    if hit is None:return None
    t=(hit-p).dot(direction)/max(direction.length_squared,1e-30)
    inside,bc=barycentric_inside(hit,face)
    if 1e-6<t<1-1e-6 and inside:
        return {'segmentFraction':float(t),'barycentricFaceWeights':[float(x) for x in bc],'worldPointM':[float(x) for x in hit]}
    return None
def pair_cross(i,j,tri_ids,points):
    ia,ib=tri_ids[i],tri_ids[j]; a=[points[k] for k in ia]; b=[points[k] for k in ib]; out=[]
    for e in range(3):
        h=edge_face(a[e],a[(e+1)%3],b)
        if h:out.append({'fromTriangle':i,'toTriangle':j,'fromEdgeIndex':e,**h})
        h=edge_face(b[e],b[(e+1)%3],a)
        if h:out.append({'fromTriangle':j,'toTriangle':i,'fromEdgeIndex':e,**h})
    return out
def decode(idx):
    skin=0 if idx<448 else 1; k=idx if skin==0 else idx-448
    return {'skin':skin,'station':k//7,'radialSample':k%7}
def main():
    assert sha(BASE)==BASE_SHA and not OUT.exists()
    prior=json.loads(PRIOR.read_text()); assert prior['inputs']['v6Native']['sha256']==BASE_SHA
    bpy.ops.wm.open_mainfile(filepath=str(BASE)); out=[]
    for side in (-1,1):
        obj=bpy.data.objects[f'Forged orbital mounting plate {side}']; mesh=obj.data; deps=bpy.context.evaluated_depsgraph_get()
        ev=obj.evaluated_get(deps); evaluated=ev.to_mesh(); evaluated.calc_loop_triangles()
        matrix=ev.matrix_world.copy(); points=[matrix@v.co for v in evaluated.vertices]; tris=[tuple(t.vertices) for t in evaluated.loop_triangles]
        tree=BVHTree.FromPolygons(points,tris,all_triangles=True,epsilon=0); pairs=set()
        for a,b in tree.overlap(tree):
            if a<b and not(set(tris[a])&set(tris[b])):pairs.add((a,b))
        crossings=[]
        for i,j in sorted(pairs):
            hits=pair_cross(i,j,tris,points)
            if hits:
                crossings.append({'triangleIndices':[i,j],'vertexIndices':[list(tris[i]),list(tris[j])],
                    'stationMapping':[ [decode(v) for v in tris[i]], [decode(v) for v in tris[j]] ],
                    'properInteriorCrossings':hits})
        allverts=[matrix@v.co for v in mesh.vertices]
        stations=[]
        for station in range(64):
            rows=[]
            for skin in (0,1):
                start=skin*448+station*7; ps=allverts[start:start+7]
                radii=[math.hypot(p.y-CENTER_YZ[0],p.z-CENTER_YZ[1]) for p in ps]
                rows.append({'skin':skin,'innerRadiusAtRadial0M':radii[0],'outerRadiusAtRadial6M':radii[6],
                    'currentRadialWidthM':radii[6]-radii[0],'radiusByRadialSampleM':radii})
            stations.append({'station':station,'skins':rows})
        involved=sorted({d['station'] for r in crossings for layer in r['stationMapping'] for d in layer})
        relevant=sorted({station for i in involved for station in range(max(0,i-1),min(63,i+1)+1)})
        allpoints=[p for r in crossings for h in r['properInteriorCrossings'] for p in [h['worldPointM']]]
        out.append({'side':'left' if side==1 else 'right','mount':obj.name,'loopTriangleCount':len(tris),
            'nonadjacentSelfBvhCandidates':len(pairs),'strictFaceInteriorCrossingPairCount':len(crossings),
            'crossingPairs':crossings,'crossingPointBoundsM':{'min':[min(p[k] for p in allpoints) for k in range(3)],'max':[max(p[k] for p in allpoints) for k in range(3)]} if allpoints else None,
            'involvedStations':involved,'adjacentRadialProfileRows': [stations[i] for i in relevant],
            'stationMappingBasis':'scripts/study-orbital-saddle-v3.py: points[i*7+j] and points[448+i*7+j], with j=0 inner and j=6 outer; topology-index mapping is inferred from that retained 896-vertex annulus recipe.',
            'radialWidthBasis':'Radius in world YZ about the authored V3 optic center (-0.369, 1.786), measured between retained j=0 inner loop and current j=6 outer edge; this is current V6 geometry, not independent engineering metrology.'})
        ev.to_mesh_clear()
    result={'status':'read-only strict self-intersection and annular map complete','blenderVersion':bpy.app.version_string,
        'inputs':{'v6Native':{'path':str(BASE.relative_to(ROOT)),'sha256':sha(BASE)},
                  'v3Recipe':{'path':str(V3.relative_to(ROOT)),'sha256':sha(V3)},
                  'priorBroadPhaseAndCrossingReceipt':{'path':str(PRIOR.relative_to(ROOT)),'sha256':sha(PRIOR)},
                  'script':{'path':str(Path(__file__).resolve().relative_to(ROOT)),'sha256':sha(Path(__file__).resolve())}},
        'method':'Exact evaluated loop triangles; candidates are self-BVH pairs with no shared vertex. Count only noncoplanar segment crossings that land strictly inside the opposite triangle using barycentric face coordinates. No model data changed; no file saved/exported.',
        'results':out,'limits':['Strict crossing count excludes tangencies, coplanar overlap, and intersections that occur only on a triangle boundary.','V3 radial mapping is a topology recipe inference checked against current 896-vertex mesh count; no V3 source was regenerated.','Radial widths describe current geometry, not a recommended design width or owner acceptance.']}
    OUT.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'output':str(OUT),'results':[{'side':x['side'],'candidatePairs':x['nonadjacentSelfBvhCandidates'],'properCrossings':x['strictFaceInteriorCrossingPairCount'],'stations':x['involvedStations'],'pointBounds':x['crossingPointBoundsM']} for x in out]},indent=2))
if __name__=='__main__':main()
