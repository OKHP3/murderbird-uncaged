"""Read-only attempt-14 joint cross-section and annular point-clearance screen."""
from pathlib import Path
import hashlib, json, math
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
NATIVE14 = ROOT / 'assets/models/uncaged-cervical-construction-study-v1/attempt-14/murderbird-cervical-construction-study-v1.blend'
NATIVE07 = ROOT / 'assets/models/uncaged-cervical-construction-study-v1/attempt-07/murderbird-cervical-construction-study-v1.blend'
POSES = ROOT / 'assets/audit/cervical-runtime-study-v1/expanded-runtime-poses/pose-snapshot.json'
OUT_JSON = OUT / 'joint-envelope-measurements.json'
OUT_SVG = OUT / 'joint-envelope-cross-section.svg'
EXPECTED_NATIVE14 = 'ef9e28ddbce9d62aabc8181a058640ea1e8b7a339b673df37b913d96699f9440'
EXPECTED_NATIVE07 = '751d8149032941774c6ba31824c76f6fa840bb0d767e433bae8000535f3a2b98'
EXPECTED_POSES = '1cb4a2f75ecae625a44c768ba543e9b99e1caa9791a3056e20f5d88bd73d2f26'
EXPECTED_GLTF = '5736ca592c5ebfa7da78315b136b53ad6a48050ede66f6d60b9ccf860afa8ecf'
if OUT_JSON.exists() or OUT_SVG.exists():
    raise RuntimeError('Refusing to overwrite rotary joint evidence outputs')

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def snapshot_pivots():
    pivots = {o.name:o for o in bpy.data.objects if o.type == 'EMPTY'}
    return {n:{'parent':p.parent.name if p.parent else None,'matrixLocal':[[round(float(p.matrix_local[r][c]),9) for c in range(4)] for r in range(4)],'matrixWorld':[[round(float(p.matrix_world[r][c]),9) for c in range(4)] for r in range(4)]} for n,p in pivots.items()}
def converted(flat):
    C=Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)))
    browser=Matrix([[flat[col*4+row] for col in range(4)] for row in range(4)])
    return C.inverted() @ browser @ C
def depth(obj): return 0 if obj.parent is None else 1+depth(obj.parent)
def apply_pose(pose,pivots):
    rows={r['name']:r for r in pose['pivotMatrices'] if r.get('kind')!='mesh'}
    for n in sorted(pivots,key=lambda x:depth(pivots[x])):
        pivots[n].matrix_world=converted(rows[n]['worldMatrix']); bpy.context.view_layer.update()
    return max(abs(pivots[n].matrix_world[r][c]-converted(rows[n]['worldMatrix'])[r][c]) for n in pivots for r in range(4) for c in range(4))
def is_descendant(o,root):
    while o:
        if o==root:return True
        o=o.parent
    return False

def owner_for(obj,pivots):
    if is_descendant(obj,pivots['breastplate']): return 'breastplate'
    current=obj
    while current is not None:
        if current.name in ('body','neck','cervical-upper','head','jaw','left-mantle','right-mantle'):
            return current.name
        current=current.parent
    return 'unassigned'

def build_local_bvhs(pivot):
    deps=bpy.context.evaluated_depsgraph_get(); inv=pivot.matrix_world.inverted()
    verts_by_owner={}; faces_by_owner={}; mesh_names={}
    for obj in bpy.data.objects:
        if obj.type!='MESH': continue
        owner=owner_for(obj,pivots)
        if owner=='unassigned':continue
        ev=obj.evaluated_get(deps); me=ev.to_mesh(); me.calc_loop_triangles()
        base=len(verts_by_owner.setdefault(owner,[])); dest=verts_by_owner[owner]
        dest.extend(inv @ (ev.matrix_world @ v.co) for v in me.vertices)
        fs=faces_by_owner.setdefault(owner,[])
        fs.extend(tuple(base+i for i in tri.vertices) for tri in me.loop_triangles)
        mesh_names.setdefault(owner,[]).extend([obj.name]*len(me.loop_triangles))
        ev.to_mesh_clear()
    trees={}
    for owner,faces in faces_by_owner.items():
        if faces: trees[owner]=BVHTree.FromPolygons(verts_by_owner[owner],faces,all_triangles=True,epsilon=0.0)
    return trees,mesh_names,verts_by_owner,faces_by_owner

def svg_cross_section(vertices_by_owner,faces_by_owner):
    # Native x=0 slice in cervical-upper coordinates. Segment intersections are
    # exact linear triangle-plane cuts of evaluated triangles at this station.
    W=700; H=680; scale=2400; cx=W/2; cy=365
    palette={'neck':'#9a6b37','cervical-upper':'#254b70','head':'#626f7c','jaw':'#9a846c','body':'#b39b77','breastplate':'#c5a77c','left-mantle':'#87919a','right-mantle':'#87919a','unassigned':'#888'}
    parts=[]
    for owner,verts in vertices_by_owner.items():
        segs=[]
        for face in faces_by_owner[owner]:
            vv=[verts[i] for i in face]
            hits=[]
            for a,b in zip(vv,[vv[1],vv[2],vv[0]]):
                da,db=a.x,b.x
                if abs(da)<1e-8: hits.append((a.y,a.z))
                if da*db<0:
                    t=da/(da-db); p=a.lerp(b,t); hits.append((p.y,p.z))
            unique=[]
            for q in hits:
                if all((q[0]-u[0])**2+(q[1]-u[1])**2>1e-12 for u in unique):unique.append(q)
            if len(unique)>=2: segs.append(unique[:2])
        if not segs: continue
        paths=[]
        for (y1,z1),(y2,z2) in segs:
            x1=cx+y1*scale; y1p=cy-z1*scale; x2=cx+y2*scale; y2p=cy-z2*scale
            paths.append(f'M{x1:.2f},{y1p:.2f} L{x2:.2f},{y2p:.2f}')
        d=' '.join(paths)
        parts.append(f'<path d="{d}" fill="none" stroke="{palette.get(owner,"#777")}" stroke-width="1.2" opacity=".78"><title>{owner} evaluated mesh section</title></path>')
    circles=[]
    for r in [0.02,0.03,0.04,0.05,0.06,0.08]:
        circles.append(f'<circle cx="{cx}" cy="{cy}" r="{r*scale}" fill="none" stroke="#16837c" stroke-dasharray="4 4" stroke-width="1"><title>candidate radial station {r*1000:.0f} mm (reference only)</title></circle>')
    axes=f'<line x1="35" y1="{cy}" x2="665" y2="{cy}" stroke="#333"/><line x1="{cx}" y1="88" x2="{cx}" y2="642" stroke="#333"/>'
    labels=f'<text x="{cx+10}" y="{cy-10}" font-size="11">axis +X out of page</text><text x="{cx+192}" y="{cy+20}" font-size="11">+Y rear →</text><text x="{cx+8}" y="{cy-192}" font-size="11">+Z up</text><text x="18" y="16" font-size="14" font-weight="bold">Attempt 14 neutral: evaluated triangle cuts at cervical-upper-local X=0</text><text x="18" y="646" font-size="11">Cropped X=0 hinge section; full paired support span is not shown.</text><text x="18" y="665" font-size="11">Dashed radii: 20/30/40/50/60/80 mm. Proposed outer cap: 30 mm; not a solid-clearance proof.</text>'
    legend=[]
    for i,(owner,color) in enumerate(palette.items()):
        if owner not in vertices_by_owner:continue
        x=18+(i%4)*165;y=44+(i//4)*18
        legend.append(f'<line x1="{x}" y1="{y}" x2="{x+22}" y2="{y}" stroke="{color}" stroke-width="3"/><text x="{x+28}" y="{y+4}" font-size="12">{owner}</text>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>{axes}{"".join(circles)}{"".join(parts)}{"".join(legend)}{labels}</svg>'

assert bpy.data.filepath and Path(bpy.data.filepath).resolve()==NATIVE14.resolve()
assert sha(NATIVE14)==EXPECTED_NATIVE14 and sha(NATIVE07)==EXPECTED_NATIVE07 and sha(POSES)==EXPECTED_POSES
pivots={o.name:o for o in bpy.data.objects if o.type=='EMPTY'}
assert len(pivots)==52 and 'cervical-upper' in pivots
snap14=snapshot_pivots()
bpy.ops.wm.open_mainfile(filepath=str(NATIVE07)); snap07=snapshot_pivots()
assert set(snap07)==set(snap14) and len(snap07)==52
assert all(snap07[n]['parent']==snap14[n]['parent'] for n in snap14)
pivot_delta=max(abs(snap07[n][mat][r][c]-snap14[n][mat][r][c]) for n in snap14 for mat in ('matrixLocal','matrixWorld') for r in range(4) for c in range(4))
assert pivot_delta < 1e-8, f'Pivot transform mismatch {pivot_delta}'
bpy.ops.wm.open_mainfile(filepath=str(NATIVE14)); pivots={o.name:o for o in bpy.data.objects if o.type=='EMPTY'}
pose_data=json.loads(POSES.read_text()); assert pose_data['model']['sha256']==EXPECTED_GLTF and pose_data['poseCount']==21
pose_by_id={p['id']:p for p in pose_data['poses']}; assert len(pose_by_id)==21

# Record dynamic radial clearance over each real pose and open-panel endpoints.
pose_rows=list(pose_data['poses'])+[{'id':'inspection-open-0-standard','syntheticOpen':0.0},{'id':'inspection-open-1-standard','syntheticOpen':1.0}]
radial_values=[0.02,0.03,0.04,0.05,0.06,0.08]
angle_count=180
joint=pivots['cervical-upper']; results=[]; neutral_vertices=None; neutral_faces=None; owner_summary={}
for row in pose_rows:
    if 'pivotMatrices' in row: pose_error=apply_pose(row,pivots)
    else: pose_error=apply_pose(pose_by_id['runtime-rest'],pivots)
    breast=pivots['breastplate']
    if 'syntheticOpen' in row:
        # match production inspection law; only the breast cover moves.
        breast.rotation_euler.y=-1.35*row['syntheticOpen']; bpy.context.view_layer.update()
    trees,names,verts,faces=build_local_bvhs(joint)
    if row['id']=='runtime-rest': neutral_vertices,neutral_faces=verts,faces
    rings=[]
    for radius in radial_values:
        best=(float('inf'),None,None,None,None)
        for axial in [-0.02,0.0,0.02]:
            for ai in range(angle_count):
                a=2*math.pi*ai/angle_count; point=Vector((axial,radius*math.cos(a),radius*math.sin(a)))
                for owner,tree in trees.items():
                    hit=tree.find_nearest(point)
                    if hit[0] is not None and hit[3]<best[0]: best=(hit[3],owner,names[owner][hit[2]],axial,ai)
        rings.append({'candidateRadiusM':radius,'minimumSampledPointToSurfaceDistanceM':best[0], 'nearestOwner':best[1], 'nearestMesh':best[2], 'atAxialOffsetM':best[3], 'angleIndex':best[4], 'angleCount':angle_count,'axialStationsM':[-0.02,0.0,0.02]})
    results.append({'poseId':row['id'],'poseApplicationMaxError':pose_error,'annularPointSamples':rings})
    for r in rings:
        key=f"{r['candidateRadiusM']:.3f}"
        old=owner_summary.get(key)
        if old is None or r['minimumSampledPointToSurfaceDistanceM']<old['minimumSampledPointToSurfaceDistanceM']:
            owner_summary[key]={'minimumSampledPointToSurfaceDistanceM':r['minimumSampledPointToSurfaceDistanceM'],'poseId':row['id'],'nearestOwner':r['nearestOwner'],'nearestMesh':r['nearestMesh'],'atAxialOffsetM':r['atAxialOffsetM']}
# restore and output cross-section at actual runtime-rest.
apply_pose(pose_by_id['runtime-rest'],pivots)
trees,names,neutral_vertices,neutral_faces=build_local_bvhs(pivots['cervical-upper'])
OUT_SVG.write_text(svg_cross_section(neutral_vertices,neutral_faces))
result={'schema':'murderbird-cervical-joint-envelope-measurements/v1','status':'read-only sampled envelope measurement; rotary topology remains a reconstruction proposal','inputs':{'native14':{'path':str(NATIVE14.relative_to(ROOT)),'sha256':sha(NATIVE14),'bytes':NATIVE14.stat().st_size},'native07':{'path':str(NATIVE07.relative_to(ROOT)),'sha256':sha(NATIVE07)},'runtimePosePacket':{'path':str(POSES.relative_to(ROOT)),'sha256':sha(POSES),'modelSha256':pose_data['model']['sha256'],'poseCount':pose_data['poseCount']},'attempt14PivotNamesParentsAndLocalWorldMatricesEqual07':True,'maxPivotMatrixDifference':pivot_delta,'analyzer':{'path':str(Path(__file__).relative_to(ROOT)),'sha256':sha(Path(__file__))}},'frame':{'origin':'cervical-upper pivot origin','axis':'local +X; pivot coordinates are native X/Y/Z, section plane X=0 uses Y/Z','coordinates':'native X anatomical left, +Y rear, Z up; -Y forward','restWorldOriginNativeXYZ':list(pivots['cervical-upper'].matrix_world.translation),'meaning':'sample points lie on proposed annular centerline radii; distance is nearest evaluated mesh surface, not a full candidate solid clearance'},'measurement':{'sampledPoseCount':len(pose_rows),'capturedRuntimePoses':21,'extraInspectionEndpoints':['inspection-open-0-standard','inspection-open-1-standard'],'radialStationsM':radial_values,'axialStationsM':[-0.02,0.0,0.02],'angularSamplesPerStation':angle_count,'minimumSurfaceDistanceByRadiusAcrossAllSamples':owner_summary,'results':results,'sectionSvg':{'path':str(OUT_SVG.relative_to(ROOT)),'sha256':sha(OUT_SVG),'bytes':OUT_SVG.stat().st_size,'description':'exact neutral evaluated-triangle intersections at upper-joint-local X=0; cropped neutral section; paired supports are outside this slice; six sample radii are plotted and 30mm is only a proposed cap'}},'limits':['Ring samples do not model sector teeth, bearing races, plates, cable, motor, drive, fasteners or supports.','Point-to-surface distance does not detect whether a test point lies inside a closed solid; no solid containment claim.','21 poses plus two inspection endpoints are discrete; no continuous joint/inspection sweep certification.','Reference art supports mechanical bird/curved neck but not this joint topology or dimensions.']}
OUT_JSON.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'output':str(OUT_JSON),'pivotMatrixDelta':pivot_delta,'minimumSurfaceDistanceByRadius':owner_summary,'svg':str(OUT_SVG)},indent=2))
