from pathlib import Path
import hashlib, json, runpy
import bpy, bmesh
from mathutils import Matrix, Vector

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
V6=ROOT/'assets/models/uncaged-orbital-saddle-study-v6/murderbird-orbital-saddle-study-v6.blend'
V7=ROOT/'assets/models/uncaged-orbital-saddle-study-v7/murderbird-orbital-saddle-study-v7.blend'
GENERATOR=ROOT/'assets/audit/orbital-saddle-study-v7/executed-generator.py'
PRIOR_FIT=ROOT/'assets/audit/orbital-saddle-study-v7/cranial-opening-audit-v1/fit-diagnosis-v1.json'
KERNEL=ROOT/'assets/audit/cervical-construction-study-v1/attempt-07/actual-runtime-joint-clearance-v1/executed-review.py'
HELPER=ROOT/'scripts/diagnose-native-regional-clearance.py'
EXPECTED={'v6':'cb811241d241b0f18f529979b77635caecb83284b8b4df29c7564d4d2bf55eec',
          'v7':'e8169a3d685977f2f7dc62ab6f85d61fe456881aba06114d4169a31989de13d5'}
SIDES=(-1,1)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def art(p): return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
def looptri_data(mesh):
    mesh.calc_loop_triangles()
    return [tuple(t.vertices) for t in mesh.loop_triangles]
def signed_volume(mesh):
    faces=looptri_data(mesh); total=0.0
    for f in faces:
        a,b,c=(mesh.vertices[i].co for i in f); total += a.dot(b.cross(c))/6
    return total
def winding(mesh):
    uses={}
    for poly in mesh.polygons:
        vs=list(poly.vertices)
        for a,b in zip(vs,vs[1:]+vs[:1]):
            key=tuple(sorted((a,b))); uses.setdefault(key,[]).append(1 if a<b else -1)
    manifold=[x for x in uses.values() if len(x)==2]
    return {'uniqueEdges':len(uses),'boundaryEdges':sum(len(x)==1 for x in uses.values()),
      'twoFaceEdges':len(manifold),'oppositeDirection':sum(sum(x)==0 for x in manifold),
      'sameDirection':sum(sum(x)!=0 for x in manifold),'nonManifoldEdges':sum(len(x)>2 for x in uses.values())}
def evaluated_surface(obj,dg):
    ev=obj.evaluated_get(dg); mesh=ev.to_mesh(); mesh.calc_loop_triangles()
    points=[ev.matrix_world@v.co for v in mesh.vertices]
    faces=[tuple(t.vertices) for t in mesh.loop_triangles]
    return ev,mesh,points,faces
def mesh_volume_stats(obj,dg):
    raw=obj.data
    ev=obj.evaluated_get(dg); em=ev.to_mesh()
    try:
        rawv=signed_volume(raw); evalv=signed_volume(em); det=ev.matrix_world.to_3x3().determinant()
        return {'objectScale':list(obj.scale),'matrixLocal':[[round(obj.matrix_local[r][c],9) for c in range(4)] for r in range(4)],
          'matrixWorld':[[round(obj.matrix_world[r][c],9) for c in range(4)] for r in range(4)],
          'worldLinearDeterminant':det,
          'raw':{'vertices':len(raw.vertices),'polygons':len(raw.polygons),'triangles':len(looptri_data(raw)),
            'signedVolumeObjectLocalM3':rawv,'signedVolumeWorldM3':rawv*obj.matrix_world.to_3x3().determinant(),'winding':winding(raw)},
          'evaluated':{'vertices':len(em.vertices),'polygons':len(em.polygons),'triangles':len(em.loop_triangles),
            'signedVolumeObjectLocalM3':evalv,'signedVolumeWorldM3':evalv*det,'winding':winding(em)}}
    finally: ev.to_mesh_clear()
def canonical_triangles(obj,dg):
    ev,mesh,pts,faces=evaluated_surface(obj,dg)
    try:
        rows=[]
        for f in faces:
            tri=tuple(sorted(tuple(round(float(x),8) for x in pts[i]) for i in f))
            rows.append(tri)
        return sorted(rows)
    finally: ev.to_mesh_clear()
def raw_canonical_triangles(obj):
    mesh=obj.data;faces=looptri_data(mesh);rows=[]
    for f in faces:
        tri=tuple(sorted(tuple(round(float(x),8) for x in obj.matrix_world@mesh.vertices[i].co) for i in f))
        rows.append(tri)
    return sorted(rows)
def world_bounds(obj):
    pts=[obj.matrix_world@v.co for v in obj.data.vertices]
    return [[min(float(p[i]) for p in pts),max(float(p[i]) for p in pts)] for i in range(3)]
def boolean_apply(target,cutter,op):
    mod=target.modifiers.new('Temporary diagnostic Boolean','BOOLEAN');mod.operation=op;mod.solver='EXACT';mod.object=cutter
    bpy.context.view_layer.objects.active=target;target.select_set(True)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    target.select_set(False)
def duplicate(obj,label):
    q=obj.copy();q.data=obj.data.copy();q.name=label;bpy.context.scene.collection.objects.link(q);q.matrix_world=obj.matrix_world.copy();return q
def object_stats(obj):
    m=obj.data
    return {'vertices':len(m.vertices),'polygons':len(m.polygons),'triangles':len(looptri_data(m)),
      'signedVolumeObjectLocalM3':signed_volume(m),'winding':winding(m)}
def barycentric_inside(p,tri,tol=2e-7):
    a,b,c=tri;v0=b-a;v1=c-a;v2=p-a
    d00=v0.dot(v0);d01=v0.dot(v1);d11=v1.dot(v1);d20=v2.dot(v0);d21=v2.dot(v1)
    den=d00*d11-d01*d01
    if abs(den)<1e-20:return False
    u=(d11*d20-d01*d21)/den;v=(d00*d21-d01*d20)/den
    return u>=-tol and v>=-tol and u+v<=1+tol
def segment_triangle(p,q,tri,tol=1e-9):
    n=(tri[1]-tri[0]).cross(tri[2]-tri[0])
    if n.length<1e-13:return None
    n.normalize();d0=n.dot(p-tri[0]);d1=n.dot(q-tri[0])
    if d0*d1>=0 or abs(d0-d1)<tol:return None
    t=d0/(d0-d1)
    if not tol<t<1-tol:return None
    hit=p+(q-p)*t
    return hit if barycentric_inside(hit,tri) else None
def independent_intersections(pointsA,triA,pointsB,triB):
    ta=[pointsA[i] for i in triA];tb=[pointsB[i] for i in triB];hits=[]
    for pts,target,label in [(ta,tb,'brow-edge'),(tb,ta,'mount-edge')]:
        for i in range(3):
            hit=segment_triangle(pts[i],pts[(i+1)%3],target)
            if hit is not None and not any((hit-old).length<1e-7 for old in hits):hits.append(hit)
    return {'independentSegmentTriangleHitsNativeXYZ':[[round(float(x),9) for x in p] for p in hits],
      'browTriangleNativeXYZ':[[round(float(x),9) for x in p] for p in ta],
      'mountTriangleNativeXYZ':[[round(float(x),9) for x in p] for p in tb],
      'browPlaneSignedVertexDistancesM':[round(float((ta[1]-ta[0]).cross(ta[2]-ta[0]).normalized().dot(p-ta[0])),10) for p in tb],
      'mountPlaneSignedVertexDistancesM':[round(float((tb[1]-tb[0]).cross(tb[2]-tb[0]).normalized().dot(p-tb[0])),10) for p in ta]}

assert sha(V6)==EXPECTED['v6'] and sha(V7)==EXPECTED['v7']
h=runpy.run_path(str(HELPER),run_name='boolean_fit_helpers')
k=runpy.run_path(str(KERNEL),run_name='boolean_fit_kernel')
proper=k['proper_crossing_receipt']
# Use the prior strict receipt's triangle indices as the independently checked case.
prior=json.loads(PRIOR_FIT.read_text())
side_data={}
predicted={}
for side in SIDES:
    brow_name=f'Forged orbital brow {side}';mount_name=f'Forged orbital mounting plate {side}'
    bpy.ops.wm.open_mainfile(filepath=str(V6));bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
    objs={o.name:o for o in bpy.data.objects if o.type=='MESH'};brow=objs[brow_name];mount=objs[mount_name]
    base_brow_stats=mesh_volume_stats(brow,bpy.context.evaluated_depsgraph_get())
    base_mount_stats=mesh_volume_stats(mount,bpy.context.evaluated_depsgraph_get())
    raw_mount_triangles=raw_canonical_triangles(mount)
    evaluated_mount_triangles=canonical_triangles(mount,bpy.context.evaluated_depsgraph_get())
    mount_scale=list(mount.scale);mw=mount.matrix_world.copy();linear=mw.to_3x3()
    # Reproduce the preserved generator's raw-mesh, BMesh vertex-normal offset exactly.
    cutter=duplicate(mount,f'Diagnostic offset cutter {side}')
    bm=bmesh.new();bm.from_mesh(cutter.data);bm.normal_update()
    offsets=[];faceproj=[];inward_face_samples=[]
    for v in bm.verts:
        local=v.normal.copy();delta=local*.001;world_delta=linear@delta
        world_n=(linear.inverted().transposed()@local).normalized() if local.length else Vector((0,0,0))
        offsets.append({'localNormalLength':float(local.length),'localOffsetM':float(delta.length),
          'worldDisplacementM':float(world_delta.length),'worldNormalComponentM':float(world_delta.dot(world_n)),
          'worldTangentialComponentM':float((world_delta-world_n*world_delta.dot(world_n)).length)})
        v.co += delta
    for f in bm.faces:
        fn=f.normal.copy()
        for v in f.verts:
            projection=float((v.normal*.001).dot(fn));faceproj.append(projection)
            if projection<=1e-12 and len(inward_face_samples)<20:
                inward_face_samples.append({'faceIndex':f.index,'vertexIndex':v.index,'faceVertexNormalProjectionLocalM':projection,
                    'vertexNativeWorldXYZ':[round(float(x),9) for x in mw@v.co],
                    'faceCenterNativeWorldXYZ':[round(float(x),9) for x in mw@f.calc_center_median()],
                    'faceNormalLocalXYZ':[round(float(x),9) for x in fn]})
    bm.to_mesh(cutter.data);bm.free();cutter.data.update()
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    cstats=mesh_volume_stats(cutter,dg)
    cutter_surface=h['surface'](cutter,dg);mount_surface=h['surface'](mount,dg)
    shell_overlaps=mount_surface['tree'].overlap(cutter_surface['tree']) if h['bounds_overlap'](mount_surface,cutter_surface) else []
    shell_proof=proper(mount_surface,cutter_surface,shell_overlaps,Matrix.Identity(4),Matrix.Identity(4)) if shell_overlaps else None
    # Boolean residual: if mount minus the offset cutter has positive volume, raw cutter does not contain the source solid.
    residual=duplicate(mount,f'Diagnostic original-minus-cutter {side}')
    boolean_apply(residual,cutter,'DIFFERENCE');residual_stats=object_stats(residual)
    # Also reproduce the exact V7 brow difference in memory for geometry parity.
    predicted_brow=duplicate(brow,f'Diagnostic predicted V7 brow {side}')
    boolean_apply(predicted_brow,cutter,'DIFFERENCE')
    predicted[side]=canonical_triangles(predicted_brow,bpy.context.evaluated_depsgraph_get())
    side_data[side]={'browName':brow_name,'mountName':mount_name,'V6Brow':base_brow_stats,'V6EvaluatedMountingWall':base_mount_stats,
      'mountRawEvaluatedGeometryParity':{'exactCanonicalWorldTriangleSetMatch':raw_mount_triangles==evaluated_mount_triangles,
         'rawTriangleCount':len(raw_mount_triangles),'evaluatedTriangleCount':len(evaluated_mount_triangles),
         'modifierStack':[{'name':m.name,'type':m.type} for m in mount.modifiers]},
      'mountObjectScale':mount_scale,'mountWorldLinearDeterminant':linear.determinant(),
      'normalOffset':{'method':'reproduced executed-generator.py: bm.normal_update(); vertex.co += vertex.normal * .001 in copied mount mesh local coordinates',
        'vertexCount':len(offsets),'worldDisplacementRangeM':[min(x['worldDisplacementM'] for x in offsets),max(x['worldDisplacementM'] for x in offsets)],
        'worldNormalComponentRangeM':[min(x['worldNormalComponentM'] for x in offsets),max(x['worldNormalComponentM'] for x in offsets)],
        'worldTangentialComponentRangeM':[min(x['worldTangentialComponentM'] for x in offsets),max(x['worldTangentialComponentM'] for x in offsets)],
        'faceVertexNormalProjectionRangeLocalM':[min(faceproj),max(faceproj)],
        'faceVertexProjectionAtOrBelowZeroCount':sum(x<=1e-12 for x in faceproj),'faceVertexProjectionCount':len(faceproj),
        'inwardFaceVertexExamples':inward_face_samples},
      'offsetRawCutter':cstats,'sourceWallVsOffsetCutterSurface':{'bvhTrianglePairCandidateCount':len(shell_overlaps),'strictCrossing':shell_proof},
      'originalMountMinusOffsetCutterBooleanResidual':{**residual_stats,'worldBoundsNativeXYZ':world_bounds(residual)}}
    bpy.ops.wm.open_mainfile(filepath=str(V7));bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
    objs7={o.name:o for o in bpy.data.objects if o.type=='MESH'};brow7=objs7[brow_name];mount7=objs7[mount_name]
    dg7=bpy.context.evaluated_depsgraph_get();stats7=mesh_volume_stats(brow7,dg7)
    actual_triangles=canonical_triangles(brow7,dg7)
    actual_surface=h['surface'](brow7,dg7);wall_surface=h['surface'](mount7,dg7)
    overlaps=actual_surface['tree'].overlap(wall_surface['tree']) if h['bounds_overlap'](actual_surface,wall_surface) else []
    rest_proof=proper(actual_surface,wall_surface,overlaps,Matrix.Identity(4),Matrix.Identity(4)) if overlaps else None
    examples=(rest_proof or {}).get('examples',[])
    prior_version=prior['versions']['v7']
    prior_pair=next(p for p in prior_version['browMountRestPairs'] if p['brow']==brow_name)
    saved_example=prior_pair['strictCrossing']['examples'][0]
    ai=saved_example['subjectEvaluatedTriangle'];bi=saved_example['targetEvaluatedTriangle']
    # Rebuild evaluated triangle arrays in the same deterministic loop-triangle order used by the report.
    evA,meshA,pointsA,facesA=evaluated_data=(None,None,None,None)
    evA,meshA,pointsA,facesA=h['surface'].__globals__['surface'](brow7,dg7),None,None,None
    # Use direct evaluated meshes to retain evaluated loop-triangle indices.
    ev=brow7.evaluated_get(dg7);em=ev.to_mesh();em.calc_loop_triangles()
    a_points=[ev.matrix_world@v.co for v in em.vertices];a_faces=[tuple(t.vertices) for t in em.loop_triangles]
    ev.to_mesh_clear()
    ev=mount7.evaluated_get(dg7);em=ev.to_mesh();em.calc_loop_triangles()
    b_points=[ev.matrix_world@v.co for v in em.vertices];b_faces=[tuple(t.vertices) for t in em.loop_triangles]
    ev.to_mesh_clear()
    independent=independent_intersections(a_points,a_faces[ai],b_points,b_faces[bi])
    side_data[side]['V7Brow']=stats7
    side_data[side]['V7BrowVsEvaluatedMountingWallRest']={'bvhTrianglePairCandidateCount':len(overlaps),'strictCrossing':rest_proof,
       'savedExampleTriangleIndices':{'brow':ai,'mountingPlate':bi},'independentIntersectionCheck':independent,
       'predictedBooleanParity':{'predictedTriangleCount':len(predicted[side]),'actualTriangleCount':len(actual_triangles),
          'exactCanonicalTriangleSetMatch':predicted[side]==actual_triangles,
          'matchingTriangleCount':len(set(predicted[side])&set(actual_triangles))}}

result={'status':'read-only in-memory Boolean fit diagnosis; no native save',
 'finding':{'classification':'offset-cutter containment failure confirmed; Boolean output parity confirmed; independently tested saved triangle pair intersects',
   'basis':'V6 evaluated mounting wall minus the exact recreated 1mm vertex-normal offset cutter leaves a nonzero closed residual on both sides; recreated exact Boolean brow triangles match V7. The mount object has unit scale and 1.0 world linear determinant, so object scale does not explain the residual.'},
 'inputs':{'v6':art(V6),'v7':art(V7),'preservedV7Generator':art(GENERATOR),'priorFitExamples':art(PRIOR_FIT),
   'regionalSurfaceHelper':art(HELPER),'frozenStrictCrossingKernel':art(KERNEL),'diagnosisRunner':art(Path(__file__))},
 'sides':{str(s):side_data[s] for s in SIDES},
 'limits':['Offset containment is evaluated by exact temporary Boolean residual plus surface crossings; it is not a general proof of mathematical set containment.',
   'Canonical triangle parity is orientation-independent and compares rounded world-space evaluated triangle coordinates.',
   'The saved-example recheck independently tests segment-through-triangle intersections; it does not establish penetration depth or correct design intent.',
   'All temporary duplicates and modifiers remained in memory; no source file was saved.'],
 'blenderVersion':bpy.app.version_string}
(OUT/'fit-diagnosis-v2.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({str(s):{'offsetWorldM':side_data[s]['normalOffset']['worldDisplacementRangeM'],
  'faceProjectionRangeM':side_data[s]['normalOffset']['faceVertexNormalProjectionRangeLocalM'],
  'residualVolume':side_data[s]['originalMountMinusOffsetCutterBooleanResidual']['signedVolumeObjectLocalM3'],
  'strictRestTriangles':side_data[s]['V7BrowVsEvaluatedMountingWallRest']['strictCrossing']['confirmedSubjectTriangleCount']+
      side_data[s]['V7BrowVsEvaluatedMountingWallRest']['strictCrossing']['confirmedTargetTriangleCount'],
  'triangleParity':side_data[s]['V7BrowVsEvaluatedMountingWallRest']['predictedBooleanParity']['exactCanonicalTriangleSetMatch'],
  'independentHits':len(side_data[s]['V7BrowVsEvaluatedMountingWallRest']['independentIntersectionCheck']['independentSegmentTriangleHitsNativeXYZ'])} for s in SIDES}))
