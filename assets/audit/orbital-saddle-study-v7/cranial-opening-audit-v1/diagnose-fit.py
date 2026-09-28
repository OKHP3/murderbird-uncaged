from pathlib import Path
import hashlib, json, runpy
import bpy
from mathutils import Matrix

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
V6=ROOT/'assets/models/uncaged-orbital-saddle-study-v6/murderbird-orbital-saddle-study-v6.blend'
V7=ROOT/'assets/models/uncaged-orbital-saddle-study-v7/murderbird-orbital-saddle-study-v7.blend'
KERNEL=ROOT/'assets/audit/cervical-construction-study-v1/attempt-07/actual-runtime-joint-clearance-v1/executed-review.py'
HELPER=ROOT/'scripts/diagnose-native-regional-clearance.py'
EXPECTED={'v6':'cb811241d241b0f18f529979b77635caecb83284b8b4df29c7564d4d2bf55eec',
          'v7':'e8169a3d685977f2f7dc62ab6f85d61fe456881aba06114d4169a31989de13d5'}
NAMES=[f'Forged orbital brow {s}' for s in (-1,1)]+[f'Forged orbital mounting plate {s}' for s in (-1,1)]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def art(p): return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
def signed_volume(mesh):
    mesh.calc_loop_triangles(); total=0.0
    for tri in mesh.loop_triangles:
        a,b,c=(mesh.vertices[i].co for i in tri.vertices)
        total += a.dot(b.cross(c))/6.0
    return total
def winding(mesh):
    uses={}
    for poly in mesh.polygons:
        vs=list(poly.vertices)
        for a,b in zip(vs,vs[1:]+vs[:1]):
            edge=tuple(sorted((a,b))); direction=1 if a<b else -1
            uses.setdefault(edge,[]).append(direction)
    manifold=[dirs for dirs in uses.values() if len(dirs)==2]
    return {'uniqueEdges':len(uses),'boundaryEdges':sum(len(v)==1 for v in uses.values()),
            'twoFaceEdges':len(manifold),'twoFaceEdgesOppositeWinding':sum(sum(v)==0 for v in manifold),
            'twoFaceEdgesSameWinding':sum(sum(v)!=0 for v in manifold),
            'nonManifoldEdges':sum(len(v)>2 for v in uses.values())}
def mesh_stats(obj,depsgraph):
    raw=obj.data
    raw_stats={'vertexCount':len(raw.vertices),'polygonCount':len(raw.polygons),
        'triangleCount':sum(max(0,len(p.vertices)-2) for p in raw.polygons),
        'signedVolumeObjectLocalM3':signed_volume(raw),'winding':winding(raw)}
    ev=obj.evaluated_get(depsgraph); em=ev.to_mesh()
    try:
        em.calc_loop_triangles(); vol=signed_volume(em)
        det=ev.matrix_world.to_3x3().determinant()
        evaluated={'vertexCount':len(em.vertices),'polygonCount':len(em.polygons),'triangleCount':len(em.loop_triangles),
            'signedVolumeObjectLocalM3':vol,'signedVolumeWorldM3':vol*det,
            'worldTransformDeterminant':det,'winding':winding(em)}
    finally: ev.to_mesh_clear()
    return {'raw':raw_stats,'evaluated':evaluated}

assert sha(V6)==EXPECTED['v6'] and sha(V7)==EXPECTED['v7']
h=runpy.run_path(str(HELPER),run_name='fit_diagnostic_helpers')
k=runpy.run_path(str(KERNEL),run_name='fit_diagnostic_kernel')
proper=k['proper_crossing_receipt']
versions={}
for label,path in [('v6',V6),('v7',V7)]:
    bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
    objs={o.name:o for o in bpy.data.objects if o.type=='MESH'}
    assert set(NAMES)<=set(objs)
    deps=bpy.context.evaluated_depsgraph_get()
    versions[label]={'native':art(path),'meshes':{n:mesh_stats(objs[n],deps) for n in NAMES}}
    pairs=[]
    for side in (-1,1):
        brow=objs[f'Forged orbital brow {side}'];plate=objs[f'Forged orbital mounting plate {side}']
        a=h['surface'](brow,deps);b=h['surface'](plate,deps)
        overlaps=a['tree'].overlap(b['tree']) if h['bounds_overlap'](a,b) else []
        proof=proper(a,b,overlaps,Matrix.Identity(4),Matrix.Identity(4)) if overlaps else None
        pairs.append({'brow':brow.name,'mountingPlate':plate.name,'bvhTrianglePairCandidateCount':len(overlaps),
            'strictCrossing':proof,'interpretation':'Geometry evidence only; no crossing is accepted as intended attachment.'})
    versions[label]['browMountRestPairs']=pairs

result={'status':'read-only native mesh fit diagnosis; no native save',
 'inputs':{'v6':art(V6),'v7':art(V7),'frozenStrictCrossingKernel':art(KERNEL),
           'regionalSurfaceDiagnostic':art(HELPER),'diagnosisRunner':art(Path(__file__))},
 'versions':versions,
 'comparison':{'signedVolumesAreSignedAndWindingSensitive':True,
   'strictPairCountAndBoundsAreRecordedPerVersion':True,
   'limits':['Signed volume is a winding-sensitive triangle sum; it does not establish watertightness or printability.',
     'Winding consistency counts edge-use orientation for edges shared by exactly two faces; boundary and nonmanifold edges are reported separately.',
     'Strict crossing receipts test noncoplanar edge-through-face crossings at the exact native rest state; containment and continuous motion are not tested.',
     'No mount or pin intersection is declared accepted based on ownership or appearance.']},
 'blenderVersion':bpy.app.version_string}
(OUT/'fit-diagnosis-v1.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'v6':{n:versions['v6']['meshes'][n]['raw']['signedVolumeObjectLocalM3'] for n in NAMES},
                  'v7':{n:versions['v7']['meshes'][n]['raw']['signedVolumeObjectLocalM3'] for n in NAMES},
                  'restCrossingCounts':{v:[(x['strictCrossing'] or {}).get('confirmedSubjectTriangleCount',0)+(x['strictCrossing'] or {}).get('confirmedTargetTriangleCount',0) for x in versions[v]['browMountRestPairs']] for v in versions}}))
