"""Read-only, in-memory diagnosis of V10's first empty Boolean operation."""
import bpy, bmesh, json, math, hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'assets/models/uncaged-orbital-saddle-study-v6/murderbird-orbital-saddle-study-v6.blend'
BASE_SHA = 'cb811241d241b0f18f529979b77635caecb83284b8b4df29c7564d4d2bf55eec'
V10_RECEIPT = ROOT / 'assets/audit/orbital-saddle-study-v10/attempt-03/receipt.json'
V10_SCRIPT = ROOT / 'scripts/study-orbital-saddle-v10.py'
OUT = Path(__file__).resolve().parent / 'receipt.json'
SIDES = (-1, 1)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def vec(v): return [float(c) for c in v]
def bounds(points):
    if not points: return None
    return {'min':[min(p[i] for p in points) for i in range(3)], 'max':[max(p[i] for p in points) for i in range(3)]}
def q(values, f):
    vals=sorted(values)
    return vals[min(len(vals)-1, math.ceil(f*len(vals))-1)] if vals else None

def mesh_stats(mesh, matrix):
    mesh.calc_loop_triangles()
    points=[matrix @ v.co for v in mesh.vertices]
    tris=[tuple(t.vertices) for t in mesh.loop_triangles]
    bm=bmesh.new(); bm.from_mesh(mesh); bm.normal_update()
    incidence=[len(e.link_faces) for e in bm.edges]
    unseen=set(bm.faces); components=[]
    while unseen:
        stack=[unseen.pop()]; count=0
        while stack:
            face=stack.pop(); count+=1
            for edge in face.edges:
                for other in edge.link_faces:
                    if other in unseen: unseen.remove(other); stack.append(other)
        components.append(count)
    volume=0.0
    for tri in tris:
        a,b,c=(points[i] for i in tri)
        volume += a.dot(b.cross(c))/6.0
    result={'vertices':len(mesh.vertices),'polygons':len(mesh.polygons),'loopTriangles':len(tris),
            'edges':len(bm.edges),'boundaryEdges':sum(n==1 for n in incidence),
            'nonTwoFaceEdges':sum(n!=2 for n in incidence),'nonContiguousManifoldEdges':sum(e.is_manifold and not e.is_contiguous for e in bm.edges),
            'looseVertices':sum(not v.link_edges for v in bm.verts),'looseEdges':sum(not e.link_faces for e in bm.edges),
            'connectedFaceComponents':sorted(components,reverse=True),'eulerCharacteristic':len(bm.verts)-len(bm.edges)+len(bm.faces),
            'signedVolumeM3':volume,'absoluteSignedVolumeM3':abs(volume),'worldBoundsM':bounds(points),
            'limits':'Signed triangle volume is meaningful only for a closed consistently oriented shell; edge metrics are exact topology checks.'}
    bm.free()
    # Self-BVH broad-phase only, excluding triangles that share a vertex.
    tree=BVHTree.FromPolygons(points,tris,all_triangles=True,epsilon=0)
    candidates=tree.overlap(tree)
    unique=set()
    for a,b in candidates:
        if a>=b or set(tris[a]) & set(tris[b]): continue
        unique.add((a,b))
    result['selfIntersectionClues']={'nonAdjacentTriangleBVHCandidatePairs':len(unique),
        'method':'Broad-phase only; not a self-intersection proof or count.'}
    return result, points, tris, tree

def copy_object(source, name, evaluated=False, triangulate=False, recalc=False):
    deps=bpy.context.evaluated_depsgraph_get()
    obj=source.evaluated_get(deps) if evaluated else source
    if evaluated:
        temp=obj.to_mesh(); mesh=temp.copy(); obj.to_mesh_clear()
    else: mesh=source.data.copy()
    if triangulate or recalc:
        bm=bmesh.new(); bm.from_mesh(mesh)
        if triangulate:
            bmesh.ops.triangulate(bm, faces=list(bm.faces), quad_method='BEAUTY', ngon_method='BEAUTY')
        if recalc:
            bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(mesh); bm.free(); mesh.update()
    clone=bpy.data.objects.new(name,mesh); bpy.context.scene.collection.objects.link(clone)
    clone.matrix_world=obj.matrix_world.copy()
    return clone

def apply_difference(target, cutter, label):
    try:
        mod=target.modifiers.new(label,'BOOLEAN'); mod.operation='DIFFERENCE'; mod.solver='EXACT'; mod.object=cutter
        bpy.context.view_layer.objects.active=target; target.select_set(True)
        ok=bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.context.view_layer.update()
        return {'operatorResult':list(ok),'exception':None}
    except Exception as exc:
        return {'operatorResult':None,'exception':repr(exc)}

def dist_summary(tree, points):
    ds=[]
    for p in points:
        hit=tree.find_nearest(p)
        ds.append(float(hit[3]) if hit[0] is not None else None)
    finite=[d for d in ds if d is not None]
    return {'sampleCount':len(ds),'missingCount':len(ds)-len(finite),'minM':min(finite) if finite else None,
            'medianM':q(finite,.5),'p90M':q(finite,.9),'maxM':max(finite) if finite else None}

def remove_obj(obj):
    mesh=obj.data
    bpy.data.objects.remove(obj,do_unlink=True)
    if mesh.users==0: bpy.data.meshes.remove(mesh)

def main():
    # Exact pinned identities are checked explicitly without trusting mutable V10 defaults.
    assert sha(BASE)==BASE_SHA
    receipt=json.loads(V10_RECEIPT.read_text())
    assert receipt['base']['sha256']==BASE_SHA and receipt['status']=='held'
    assert not OUT.exists(), 'Refusing to overwrite diagnostic receipt'
    bpy.ops.wm.open_mainfile(filepath=str(BASE))
    rows=[]
    for side in SIDES:
        brow=bpy.data.objects[f'Forged orbital brow {side}']
        mount=bpy.data.objects[f'Forged orbital mounting plate {side}']
        bstats,bpts,btris,btree=mesh_stats(brow.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh(), brow.matrix_world)
        # Release the temporary evaluated mesh used for stats.
        brow.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
        mstats,mpts,mtris,mtree=mesh_stats(mount.data,mount.matrix_world)
        lens=bpy.data.objects[f'Seated passive optic housing {side}']
        lens_ev=lens.evaluated_get(bpy.context.evaluated_depsgraph_get()); lens_mesh=lens_ev.to_mesh()
        lens_points=[lens_ev.matrix_world@v.co for v in lens_mesh.vertices]; lens_ev.to_mesh_clear()
        before_seat=dist_summary(mtree,lens_points)
        target_base=copy_object(mount,f'DIAG {side} target untri')
        cutter_base=copy_object(brow,f'DIAG {side} cutter untri',evaluated=True)
        direct=apply_difference(target_base,cutter_base,'DIAG direct exact Difference')
        direct_stats,dpts,dtris,dtree=mesh_stats(target_base.data,target_base.matrix_world)
        direct_seat=dist_summary(dtree,lens_points)
        remove_obj(target_base); remove_obj(cutter_base)
        target_tri=copy_object(mount,f'DIAG {side} target triangulated',triangulate=True,recalc=True)
        cutter_tri=copy_object(brow,f'DIAG {side} cutter triangulated',evaluated=True,triangulate=True,recalc=True)
        tri_target_before,_,_,_=mesh_stats(target_tri.data,target_tri.matrix_world)
        tri_cutter_before,_,_,_=mesh_stats(cutter_tri.data,cutter_tri.matrix_world)
        triangulated=apply_difference(target_tri,cutter_tri,'DIAG triangulated exact Difference')
        tri_stats,tpts,ttris,ttree=mesh_stats(target_tri.data,target_tri.matrix_world)
        tri_seat=dist_summary(ttree,lens_points)
        rows.append({'side':'left' if side==1 else 'right','sourceObjects':{'brow':brow.name,'mount':mount.name,'opticHousing':lens.name},
            'brow':bstats,'mountBefore':mstats,'opticHousingVerticesToMountBefore':before_seat,
            'directExactBooleanOnTemporaryCopies':{'operation':direct,'result':direct_stats,'opticHousingVerticesToMount':direct_seat},
            'triangulatedAndNormalRecalculatedOperandsExactBoolean':{'targetBefore':tri_target_before,'cutterBefore':tri_cutter_before,
                'operation':triangulated,'result':tri_stats,'opticHousingVerticesToMount':tri_seat,
                'procedure':'Separate temporary copies; triangulate all polygons with BMesh BEAUTY, recalculate face normals, then Blender EXACT Boolean Difference. No source object or file saved.'}})
        remove_obj(target_tri); remove_obj(cutter_tri)
    out={'status':'diagnostic complete; no candidate saved or exported','blenderVersion':bpy.app.version_string,
         'inputs':{'v6Native':{'path':str(BASE.relative_to(ROOT)),'sha256':sha(BASE)},
                   'v10Script':{'path':str(V10_SCRIPT.relative_to(ROOT)),'sha256':sha(V10_SCRIPT)},
                   'v10HeldReceipt':{'path':str(V10_RECEIPT.relative_to(ROOT)),'sha256':sha(V10_RECEIPT)}},
         'method':'Inspect original evaluated brow and mount topology/normals/volume and mesh bounds; compare direct EXACT Boolean on disposable copies with one controlled exact Boolean using triangulated, recalc-normal disposable copies. No render, native save, export, runtime change, or parameter grid.',
         'results':rows,'limits':['Self-BVH values are broad-phase candidates only, not self-intersection counts.','Nonempty/watertight output plus housing-distance retention is a plausibility screen, not full optical fit or artistic acceptance.','Triangulation and normal recalculation are diagnostic-only transformations.']}
    OUT.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'output':str(OUT),'results':[
        {'side':r['side'],'browTopology':r['brow'],'mountTopology':r['mountBefore'],
         'direct':r['directExactBooleanOnTemporaryCopies']['result'],
         'triangulated':r['triangulatedAndNormalRecalculatedOperandsExactBoolean']['result']} for r in rows]},indent=2))

if __name__=='__main__': main()
