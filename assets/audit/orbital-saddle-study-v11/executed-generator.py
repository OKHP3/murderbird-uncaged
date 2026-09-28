"""One direct station-based annular wall repair for the held V6 orbital bed.

This is a neutral native study, not a selected or exported runtime asset.
It preserves the authored inner optic seat and changes only the two fixed
orbital mounting meshes. No Boolean or convex hull is used.
"""
from pathlib import Path
import datetime, hashlib, json, math, runpy, shutil

import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'assets/models/uncaged-orbital-saddle-study-v6/murderbird-orbital-saddle-study-v6.blend'
BASE_SHA = 'cb811241d241b0f18f529979b77635caecb83284b8b4df29c7564d4d2bf55eec'
OUT = ROOT / 'assets/models/uncaged-orbital-saddle-study-v11'
AUDIT = ROOT / 'assets/audit/orbital-saddle-study-v11'
HELPER = ROOT / 'scripts/build-uncaged-alignment-v7.py'
HELPER_SHA = '39b6ee2285d8c49df3a902f8fac0a07589da3d41f48ae24df1e06515c839033a'
PROFILE_SOURCE = ROOT / 'scripts/study-orbital-saddle-v3.py'
PROFILE_SOURCE_SHA = '2243a61ba5b03c7d2e649ec39b37a63e9f07d4db80b283d891e95b59e43adf40'
RENDERER = ROOT / 'scripts/study-v8-bill-envelope.py'
RENDERER_SHA = '2d3502a134cecb15c04ca0ce9f8db0f7555d6d8a52e5f7c9c74dfd55299f421a'
SIDES = (-1, 1)
CENTER_YZ = (-.369, 1.786)
LOWER = [(.145,-.272,1.866),(.153,-.308,1.875),(.153,-.353,1.863),(.143,-.405,1.853),(.112,-.449,1.846)]
SKIN_VERTS = 448
STATIONS = 64
RADIAL_SAMPLES = 7
MIN_WALL_M = .006
BELOW_BROW_M = .004


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path):
    return {'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size, 'sha256': sha(path)}


def lower_at_y(y, cubic):
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) * .5
        if cubic(LOWER, mid)[1] > y:
            lo = mid
        else:
            hi = mid
    return cubic(LOWER, (lo + hi) * .5)


def smoothstep(x):
    x = max(0.0, min(1.0, x))
    return x*x*(3.0-2.0*x)


def station_weight(i):
    if i < 20:
        return smoothstep((i-18)/2.0)
    if i <= 26:
        return 1.0
    return 1.0-smoothstep((i-26)/4.0)


def radius_clearance_limit(inner, current_radius, path_eval):
    cy, cz = CENTER_YZ
    dy, dz = inner.y-cy, inner.z-cz
    inner_radius = math.hypot(dy, dz)
    if inner_radius <= 1e-10:
        return current_radius, {'status': 'degenerate-inner-radius'}
    uy, uz = dy/inner_radius, dz/inner_radius

    def clearance(radius):
        y, z = cy+uy*radius, cz+uz*radius
        if not (LOWER[-1][1] <= y <= LOWER[0][1]):
            return None
        _, _, brow_z = lower_at_y(y, path_eval)
        return brow_z-BELOW_BROW_M-z

    # The original inner loop is fixed. A target must lie beyond it and below
    # the same-side lower brow envelope with the authored 4 mm nominal relief.
    if clearance(inner_radius) is None or clearance(inner_radius) < 0:
        return current_radius, {'status': 'no-valid-inner-ray-clearance', 'innerRadiusM': inner_radius}
    if clearance(current_radius) is None or clearance(current_radius) >= 0:
        return current_radius, {'status': 'current-radius-already-clear', 'innerRadiusM': inner_radius}
    lo, hi = inner_radius, current_radius
    for _ in range(48):
        mid = (lo+hi)*.5
        if clearance(mid) >= 0:
            lo = mid
        else:
            hi = mid
    return lo, {'status': 'reduced-to-brow-envelope', 'innerRadiusM': inner_radius,
                'safeOuterRadiusM': lo, 'clearanceAtSafeRadiusM': clearance(lo)}


def evaluated_surface(obj, depsgraph):
    ev = obj.evaluated_get(depsgraph)
    mesh = ev.to_mesh()
    mesh.calc_loop_triangles()
    matrix = ev.matrix_world.copy()
    points = [matrix @ vertex.co for vertex in mesh.vertices]
    triangles = [tuple(tri.vertices) for tri in mesh.loop_triangles]
    tree = BVHTree.FromPolygons(points, triangles, all_triangles=True, epsilon=0)
    ev.to_mesh_clear()
    return {'points': points, 'triangles': triangles, 'tree': tree}


def topology_profile(obj):
    bm = bmesh.new(); bm.from_mesh(obj.data); bm.normal_update()
    incidence = [len(edge.link_faces) for edge in bm.edges]
    unseen = set(bm.faces); component_sizes = []
    while unseen:
        stack = [unseen.pop()]; count = 0
        while stack:
            face = stack.pop(); count += 1
            for edge in face.edges:
                for neighbor in edge.link_faces:
                    if neighbor in unseen:
                        unseen.remove(neighbor); stack.append(neighbor)
        component_sizes.append(count)
    bm.free()
    mesh = obj.data; mesh.calc_loop_triangles()
    areas = []
    for tri in mesh.loop_triangles:
        p = [obj.matrix_world @ mesh.vertices[k].co for k in tri.vertices]
        areas.append((p[1]-p[0]).cross(p[2]-p[0]).length*.5)
    return {'vertices': len(mesh.vertices), 'polygons': len(mesh.polygons),
            'loopTriangles': len(mesh.loop_triangles),
            'boundaryEdgeCount': sum(n == 1 for n in incidence),
            'nonManifoldEdgeCount': sum(n != 2 for n in incidence),
            'connectedFaceComponentCount': len(component_sizes),
            'componentFaceCounts': sorted(component_sizes, reverse=True),
            'minimumLoopTriangleAreaM2': min(areas) if areas else None,
            'degenerateTriangleCountLe1e12M2': sum(a <= 1e-12 for a in areas)}


def barycentric_inside(p, tri, eps=1e-6):
    a,b,c=tri; v0=b-a; v1=c-a; v2=p-a
    d00=v0.dot(v0); d01=v0.dot(v1); d11=v1.dot(v1); d20=v2.dot(v0); d21=v2.dot(v1)
    den=d00*d11-d01*d01
    if abs(den)<1e-18: return False
    u=(d11*d20-d01*d21)/den; v=(d00*d21-d01*d20)/den
    return min(u,v,1-u-v)>eps


def edge_face(p,q,face):
    n=(face[1]-face[0]).cross(face[2]-face[0])
    if n.length<1e-12: return False
    n.normalize(); d0=n.dot(p-face[0]); d1=n.dot(q-face[0])
    if not (d0*d1<0 and abs(d0)>1e-7 and abs(d1)>1e-7): return False
    direction=q-p; hit=intersect_ray_tri(*face,direction,p,True)
    if hit is None: return False
    t=(hit-p).dot(direction)/max(direction.length_squared,1e-30)
    return 1e-6<t<1-1e-6 and barycentric_inside(hit,face)


def strict_crossings(a,b,candidates):
    ids_a, ids_b, examples = set(), set(), []
    for ia,ib in candidates:
        ta=[a['points'][v] for v in a['triangles'][ia]]
        tb=[b['points'][v] for v in b['triangles'][ib]]
        hit=any(edge_face(ta[i],ta[(i+1)%3],tb) or edge_face(tb[i],tb[(i+1)%3],ta)
                for i in range(3))
        if hit:
            ids_a.add(ia); ids_b.add(ib)
            if len(examples)<8:
                examples.append({'triangleA':ia,'triangleB':ib,
                    'worldTriangleA':[[float(c) for c in p] for p in ta],
                    'worldTriangleB':[[float(c) for c in p] for p in tb]})
    return {'candidateTrianglePairs':len(candidates),'crossingTriangleCountA':len(ids_a),
            'crossingTriangleCountB':len(ids_b),'examples':examples,
            'method':'Evaluated Blender loop triangles; noncoplanar segment-through-face crossings strictly inside the receiving triangle. Tangencies/coplanar overlap excluded.'}


def self_crossings(surface):
    tree=surface['tree']; tris=surface['triangles']; pairs=set()
    for a,b in tree.overlap(tree):
        if a<b and not(set(tris[a])&set(tris[b])): pairs.add((a,b))
    return strict_crossings(surface,surface,sorted(pairs)), len(pairs)


def main():
    assert sha(BASE)==BASE_SHA, 'Pinned V6 source bytes changed'
    assert sha(HELPER)==HELPER_SHA and sha(PROFILE_SOURCE)==PROFILE_SOURCE_SHA and sha(RENDERER)==RENDERER_SHA
    assert not OUT.exists() and not AUDIT.exists(), 'Refusing to overwrite V11 output'
    AUDIT.mkdir(parents=True, exist_ok=False)
    shutil.copy2(__file__, AUDIT/'executed-generator.py')
    helper=runpy.run_path(str(HELPER),run_name='v11_snapshot_helpers')
    profile=runpy.run_path(str(ROOT/'scripts/study-head-continuous-plates-v2.py'),run_name='v11_profile_helpers')
    cubic=profile['lerp_rows']
    bpy.ops.wm.open_mainfile(filepath=str(BASE))
    bpy.context.scene.frame_set(1); bpy.context.view_layer.update()
    before=helper['scene_snapshot']()
    assert len(before['meshes'])==699 and len(before['empties'])==51 and len(before['curves'])==462
    mats_before={m.name:helper['material_signature'](m) for m in bpy.data.materials}
    world_before={o.name:o.matrix_world.copy() for o in bpy.data.objects}
    changed=[f'Forged orbital mounting plate {side}' for side in SIDES]
    brow_names=[f'Forged orbital brow {side}' for side in SIDES]
    pin6_names=[f'Orbital mounting fixing {side} 6' for side in SIDES]
    assert all(n in before['meshes'] for n in changed+brow_names+pin6_names)
    for orphan_name in ('Neutral / edge.001','Neutral / plate.001'):
        orphan=bpy.data.materials.get(orphan_name)
        if orphan is not None and orphan.users==0:
            orphan.use_fake_user=True
    mats_before={m.name:helper['material_signature'](m) for m in bpy.data.materials}
    profile_rows=[]; topology=[]; self_rows=[]; fail=[]
    for side in SIDES:
        name=f'Forged orbital mounting plate {side}'; obj=bpy.data.objects[name]
        mesh=obj.data; assert len(mesh.vertices)==896 and len(mesh.polygons)==896
        pre=topology_profile(obj); old=[obj.matrix_world@v.co for v in mesh.vertices]
        target_by_skin={}; station_rows=[]
        for skin in (0,1):
            values=[]
            for station in range(STATIONS):
                start=skin*SKIN_VERTS+station*RADIAL_SAMPLES
                ring=old[start:start+RADIAL_SAMPLES]
                radii=[math.hypot(p.y-CENTER_YZ[0],p.z-CENTER_YZ[1]) for p in ring]
                current=radii[-1]; safe,detail=radius_clearance_limit(ring[0],current,cubic)
                weight=station_weight(station)
                target=current+weight*(min(current,safe)-current)
                width=target-radii[0]
                row={'side':'left' if side==1 else 'right','skin':skin,'station':station,
                     'currentInnerRadiusM':radii[0],'currentOuterRadiusM':current,
                     'safeOuterRadiusM':safe,'targetOuterRadiusM':target,
                     'nominalReliefWeight':weight,'radialWidthM':width,'clearanceSolve':detail}
                values.append((radii,target,row))
                station_rows.append(row)
                if weight>0 and width<MIN_WALL_M:
                    fail.append(f'{name} skin {skin} station {station}: radial wall {width:.6f} m below {MIN_WALL_M:.3f} m')
            target_by_skin[skin]=values
        # Preserve each authored j=0 seat vertex and each X coordinate. Move
        # only the radial YZ samples by interpolating their original normalized
        # station fractions between that seat and the fitted outer boundary.
        inv=obj.matrix_world.inverted(); authored=[v.co.copy() for v in mesh.vertices]
        moved=0; max_move=0.0
        for skin in (0,1):
            for station,(radii,target,row) in enumerate(target_by_skin[skin]):
                start=skin*SKIN_VERTS+station*RADIAL_SAMPLES
                r0,ro=radii[0],radii[-1]
                if abs(ro-r0)<1e-10: continue
                inner=old[start]
                uy=(inner.y-CENTER_YZ[0])/r0; uz=(inner.z-CENTER_YZ[1])/r0
                for j in range(1,RADIAL_SAMPLES):
                    p=old[start+j]
                    fraction=max(0.0,min(1.0,(radii[j]-r0)/(ro-r0)))
                    new_r=r0+fraction*(target-r0)
                    new=Vector((p.x,CENTER_YZ[0]+uy*new_r,CENTER_YZ[1]+uz*new_r))
                    local=inv@new
                    delta=(new-p).length
                    if delta>1e-10: moved+=1; max_move=max(max_move,delta)
                    mesh.vertices[start+j].co=local
        mesh.update()
        # Exact authored inner-seat preservation in local coordinates.
        seat_deltas=[]
        for skin in (0,1):
            for station in range(STATIONS):
                idx=skin*SKIN_VERTS+station*RADIAL_SAMPLES
                seat_deltas.append((mesh.vertices[idx].co-authored[idx]).length)
        assert max(seat_deltas,default=0.0)==0.0, (name,'inner j=0 seat changed')
        post=topology_profile(obj)
        deps=bpy.context.evaluated_depsgraph_get(); surf=evaluated_surface(obj,deps)
        cross,pair_count=self_crossings(surf)
        row={'mesh':name,'before':pre,'after':post,'nonadjacentSelfBvhCandidates':pair_count,
             'strictSelfCrossings':cross,'changedVertexCount':moved,'maximumVertexDisplacementM':max_move,
             'innerSeatMaximumLocalDeltaM':max(seat_deltas,default=0.0)}
        topology.append(row); self_rows.append(row)
        profile_rows.extend(station_rows)
        if post['boundaryEdgeCount'] or post['nonManifoldEdgeCount'] or post['connectedFaceComponentCount']!=1:
            fail.append(f'{name}: topology not one closed connected manifold shell')
        if cross['crossingTriangleCountA']:
            fail.append(f'{name}: {cross["crossingTriangleCountA"]} triangles participate in strict self-crossings')
        if post['degenerateTriangleCountLe1e12M2']>pre['degenerateTriangleCountLe1e12M2']:
            fail.append(f'{name}: degenerate loop-triangle count increased')

    bpy.context.view_layer.update()
    after=helper['scene_snapshot']()
    assert set(before['meshes'])==set(after['meshes'])
    assert before['empties']==after['empties'] and before['curves']==after['curves']
    actual_changed=[n for n in before['meshes'] if before['meshes'][n]!=after['meshes'][n]]
    assert set(actual_changed)==set(changed),(actual_changed,changed)
    for n,old in before['meshes'].items():
        if n in changed:
            assert {k:v for k,v in old.items() if k!='mesh'}=={k:v for k,v in after['meshes'][n].items() if k!='mesh'},n
        else: assert old==after['meshes'][n],f'Unexpected mesh data change: {n}'
    world_error=max(max(abs(o.matrix_world[r][c]-world_before[o.name][r][c]) for r in range(4) for c in range(4)) for o in bpy.data.objects)
    assert world_error<2e-7,world_error
    assert mats_before=={m.name:helper['material_signature'](m) for m in bpy.data.materials}
    assert before['empties']==after['empties'] and before['curves']==after['curves']
    
    # Exact brow/mount evaluated loop-triangle crossings at rest and every
    # discrete cranial-cover lift in the existing V10 test convention.
    cover=bpy.data.objects['cranial-cover']; cover_local=cover.matrix_local.copy(); sweep=[]
    if not fail:
        for step in range(41):
            fraction=step/40
            cover.matrix_local=cover_local.copy()
            cover.location.z=cover_local.translation.z+.08*fraction
            bpy.context.view_layer.update(); deps=bpy.context.evaluated_depsgraph_get(); pairs=[]
            for side in SIDES:
                brow=bpy.data.objects[f'Forged orbital brow {side}']; mount=bpy.data.objects[f'Forged orbital mounting plate {side}']
                a=evaluated_surface(brow,deps); b=evaluated_surface(mount,deps)
                candidates=a['tree'].overlap(b['tree']); crossing=strict_crossings(a,b,candidates)
                pairs.append({'brow':brow.name,'mount':mount.name,'candidatePairs':len(candidates),'crossings':crossing})
            sweep.append({'fraction':fraction,'coverLocalZDeltaM':.08*fraction,'pairs':pairs})
        cover.matrix_local=cover_local.copy(); bpy.context.view_layer.update()
        count=sum(1 for s in sweep for p in s['pairs'] if p['crossings']['crossingTriangleCountA'] or p['crossings']['crossingTriangleCountB'])
        if count: fail.append(f'{count} brow/mount pair poses have strict crossings in 41-sample lift')
    else:
        count=None

    native=None; view_rows=[]
    if not fail:
        OUT.mkdir(parents=True,exist_ok=False)
        native=OUT/'murderbird-orbital-saddle-study-v11.blend'
        bpy.context.preferences.filepaths.save_version=0
        bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False)
        bpy.ops.wm.open_mainfile(filepath=str(native)); bpy.context.scene.frame_set(1); bpy.context.view_layer.update()
        assert helper['scene_snapshot']()==after,'V11 save/reload full-scene snapshot mismatch'
        assert sha(BASE)==BASE_SHA,'Pinned V6 source bytes changed during study'
        render=runpy.run_path(str(RENDERER),run_name='v11_renderer')
        render['AUDIT']=AUDIT
        view_rows=render['renders'](BASE,'before')+render['renders'](native,'after')

    result={'status':'held' if fail else 'neutral annular-wall geometry proposal; visual review pending',
        'generatedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'blenderVersion':bpy.app.version_string,
        'base':artifact(BASE),'native':artifact(native) if native else None,
        'generator':artifact(AUDIT/'executed-generator.py'),'snapshotHelper':artifact(HELPER),
        'profileSource':artifact(PROFILE_SOURCE),'renderer':artifact(RENDERER),
        'construction':{'changedMeshes':actual_changed,'operation':'Reparameterize each existing annular station on its original radial YZ ray around (-0.369, 1.786); preserve j=0 and per-vertex X; smoothly reduce upper outer radii in the diagnosed brow-interference span. No new objects, no Boolean, no convex hull.','stationRows':profile_rows,'minimumAuthoredRadialWallM':MIN_WALL_M,'nominalBrowReliefM':BELOW_BROW_M,'browEnvelope':'Cubic interpolation of retained V3 lower-edge authored stations; proposal coordinates, not reference metrology.'},
        'preservation':{'onlyTwoMountMeshesChanged':set(actual_changed)==set(changed),'other697MeshSnapshotsExact':all(after['meshes'][n]==old for n,old in before['meshes'].items() if n not in changed),'51PivotsExact':before['empties']==after['empties'],'462GuidesExact':before['curves']==after['curves'],'allObjectWorldMatricesMaxErrorM':world_error,'allMaterialsExact':mats_before=={m.name:helper['material_signature'](m) for m in bpy.data.materials},'innerSeatJ0MaximumLocalDeltaM':max(r['innerSeatMaximumLocalDeltaM'] for r in topology),'fullSaveReloadSnapshotExact':bool(native)},
        'topologyAndSelfCrossings':topology,
        'browMountLiftSweep':{'status':'run' if len(sweep)==41 else 'skipped because annular wall/topology precheck failed','sampleCount':len(sweep),'strictCrossingPairPoseCount':count,'samples':sweep,'limits':'Rest plus 40 additional discrete normalized cranial-cover lifts; no continuous clearance certificate.'},
        'views':view_rows,'failReasons':fail,
        'limits':['This locally fitted orbital bed proposal is not source-exact engineering or artistic acceptance.','Strict triangle tests exclude tangency and coplanar overlap; the lift sweep is discrete.','No runtime export, app selection, browser test, owner acceptance, or publication.']}
    (AUDIT/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    (AUDIT/'README.md').write_text('# Orbital saddle study V11\n\nOne direct annular-wall candidate from pinned V6. See [receipt.json](receipt.json) for exact source identity, preserved scene data, station changes, manifold and strict crossing checks, and the discrete 41-pose brow lift screen. This is a neutral geometry proposal only; it is not exported, selected, or accepted.\n')
    print(json.dumps({'status':result['status'],'native':result['native'],'failed':fail,'views':len(view_rows),'output':str(AUDIT/'receipt.json')},indent=2))


if __name__=='__main__':
    main()
