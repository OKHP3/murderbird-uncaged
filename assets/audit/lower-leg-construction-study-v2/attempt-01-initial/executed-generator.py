"""V2 fitted lower-leg replacement, based on hash-bound Alignment V9.

Run in Blender:
  blender --background --threads 1 --python scripts/study-lower-leg-construction-v2.py -- build
  blender --background --threads 1 --python scripts/study-lower-leg-construction-v2.py -- render
  blender --background --threads 1 --python scripts/study-lower-leg-construction-v2.py -- audit

This is one authored native study, not an engineering model or an app export.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import runpy
import sys

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'assets/models/uncaged-alignment-v9/murderbird-alignment-v9.blend'
SOURCE_SHA = '4d7568d1c2ba7cab716876f57a6c20cb6a788d4daeef1d5d34f85c1910ed2bbe'
NATIVE = ROOT / 'assets/models/uncaged-lower-leg-construction-study-v2/murderbird-lower-leg-construction-study-v2.blend'
AUDIT = ROOT / 'assets/audit/lower-leg-construction-study-v2'
FROZEN_SCRIPT = AUDIT / 'executed-generator.py'
REPLACE = {
    'left shaped shin guard proximal',
    'left shaped shin guard distal-overlap',
    'left tapered passive load rail.002',
    'left tapered passive load rail.003',
    'Limb sheath fixing.006', 'Limb sheath fixing.007', 'Limb sheath fixing.008',
    'Limb sheath fixing.009', 'Limb sheath fixing.010', 'Limb sheath fixing.011',
    'right shaped shin guard proximal',
    'right shaped shin guard distal-overlap',
    'right tapered passive load rail.002',
    'right tapered passive load rail.003',
    'Limb sheath fixing.018', 'Limb sheath fixing.019', 'Limb sheath fixing.020',
    'Limb sheath fixing.021', 'Limb sheath fixing.022', 'Limb sheath fixing.023',
}
ERA = 'maker,mechanic,builder'
ADDED = []
MATING = []

parser = argparse.ArgumentParser()
parser.add_argument('mode', choices=('build', 'render', 'audit'))
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def object_signature(obj):
    row = {
        'name': obj.name, 'type': obj.type,
        'parent': obj.parent.name if obj.parent else None,
        'matrixWorld': [round(v, 12) for r in obj.matrix_world for v in r],
        'matrixBasis': [round(v, 12) for r in obj.matrix_basis for v in r],
        'matrixParentInverse': [round(v, 12) for r in obj.matrix_parent_inverse for v in r],
        'dataName': obj.data.name if obj.data else None,
        'materials': [m.name if m else None for m in obj.data.materials] if obj.type == 'MESH' else [],
    }
    if obj.type == 'MESH':
        row['mesh'] = hashlib.sha256(json.dumps({
            'v': [[round(float(c), 10) for c in v.co] for v in obj.data.vertices],
            'f': [list(p.vertices) for p in obj.data.polygons],
        }, separators=(',', ':')).encode()).hexdigest()
    return row


def signatures():
    return {obj.name: object_signature(obj) for obj in bpy.data.objects}


def scene_material(role):
    prefs = {'frame': ('Neutral | frame', 'Neutral | bearing', 'Neutral | plate'),
             'bearing': ('Neutral | bearing', 'Neutral | frame', 'Neutral | plate'),
             'plate': ('Neutral | plate', 'Neutral | frame', 'Neutral | bearing')}
    for name in prefs[role]:
        material = bpy.data.materials.get(name)
        if material:
            return material
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.get('surfaceRole') == role and obj.data.materials:
            return obj.data.materials[0]
    raise RuntimeError(f'No existing native material for role {role}')


def attach_world_mesh(name, owner, role, note, vertices, faces, material_role=None):
    mesh = bpy.data.meshes.new(name + ' mesh')
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    import bmesh
    bm=bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    bm.to_mesh(mesh);bm.free();mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.parent = owner
    obj.matrix_parent_inverse = owner.matrix_world.inverted()
    obj.matrix_basis.identity()
    obj['region'] = 'leg'
    obj['surfaceRole'] = role
    obj['exteriorEras'] = ERA
    obj['constructionNote'] = note
    obj['studyOwner'] = owner.name
    obj['studyVersion'] = 'v2-fitted-replacement'
    obj.data.materials.append(scene_material(material_role or role))
    ADDED.append(name)
    return obj


def rounded_beam_mesh(a, b, u, v, hu, hv, sides=8):
    """Closed octagonal beam; endpoints/vertices are authored in rest-world XYZ."""
    a, b, u, v = Vector(a), Vector(b), Vector(u), Vector(v)
    axis = (b-a).normalized()
    u = (u-axis*u.dot(axis)).normalized()
    v = v-axis*v.dot(axis)-u*v.dot(u)
    if v.length < 1e-8:
        v = axis.cross(u)
    v.normalize()
    vertices=[]
    for p in (a,b):
        for k in range(sides):
            angle=math.tau*k/sides
            vertices.append(tuple(p+u*(hu*math.cos(angle))+v*(hv*math.sin(angle))))
    faces=[tuple(reversed(range(sides))), tuple(range(sides,2*sides))]
    for k in range(sides):
        j=(k+1)%sides
        faces.append((k,j,sides+j,sides+k))
    return vertices,faces


def beam_into(vv, ff, a, b, u, v, hu, hv, sides=8):
    p,q=rounded_beam_mesh(a,b,u,v,hu,hv,sides)
    n=len(vv);vv.extend(p);ff.extend([tuple(n+i for i in face) for face in q])


def tube_along(points, cross_u, cross_v, profiles, sides=8):
    """Closed tapered tube along a centerline of (point, half-u, half-v) stations."""
    verts=[];faces=[]
    for p,hu,hv in profiles:
        p=Vector(p)
        for k in range(sides):
            angle=math.tau*k/sides
            verts.append(tuple(p+cross_u*(hu*math.cos(angle))+cross_v*(hv*math.sin(angle))))
    faces.append(tuple(reversed(range(sides))))
    faces.append(tuple(range((len(profiles)-1)*sides,len(profiles)*sides)))
    for row in range(len(profiles)-1):
        a=row*sides;b=(row+1)*sides
        for k in range(sides):
            j=(k+1)%sides
            faces.append((a+k,a+j,b+j,b+k))
    return verts,faces


def wrapped_guard(owner, side, center, axis, across, front, frame_name):
    """Two closed anterior shell bands; their lateral hems nest into the rails."""
    v=[];f=[]
    # Each band leaves an open mid-shank window. The 120-degree wrap is close to
    # the shank axis and the shell hems overlap the inner faces of both load rails.
    bands=((.27,.405),(.595,.73))
    ntheta=18;nt=5
    outer=.053;inner=.048
    for t0,t1 in bands:
        base=len(v)
        # outer and inner layers, with 5 axial rows each
        for radius in (outer,inner):
            for ri in range(nt):
                t=t0+(t1-t0)*ri/(nt-1)
                c=center+axis*t
                for ci in range(ntheta+1):
                    angle=math.radians(-60+120*ci/ntheta)
                    p=c+front*(radius*math.cos(angle))+across*(radius*math.sin(angle))
                    v.append(tuple(p))
        row=ntheta+1;layer=nt*row
        # outer/inner grids and closed side/end hems
        for l in range(2):
            off=base+l*layer
            for ri in range(nt-1):
                for ci in range(ntheta):
                    a=off+ri*row+ci;b=a+1;c=a+row+1;d=a+row
                    f.append((a,b,c,d) if l==0 else (d,c,b,a))
        for ri in range(nt-1):
            for ci in (0,ntheta):
                a=base+ri*row+ci;b=a+row
                c=base+layer+ri*row+ci;d=c+row
                f.append((a,b,d,c))
        for ri in (0,nt-1):
            for ci in range(ntheta):
                a=base+ri*row+ci;b=a+1;c=base+layer+ri*row+ci+1;d=c-1
                f.append((a,d,c,b))
    obj=attach_world_mesh(f'{side} shin integrated anterior wrap guard',owner,'plate',
        'Two formed partial wraps with hems fitted into the paired load cage; central shank window remains open.',v,f,'plate')
    return obj


def build_side(side):
    owner=bpy.data.objects[side+'-shin'];foot=bpy.data.objects[side+'-foot']
    knee=owner.matrix_world.translation.copy();ankle=foot.matrix_world.translation.copy()
    axis=(ankle-knee).normalized()
    across=Vector((1,0,0))-axis*axis.x;across.normalize()
    front=Vector((0,-1,0))-axis*Vector((0,-1,0)).dot(axis);front.normalize()
    sign=1 if side=='left' else -1
    def c(t,x=0.0,f=0.0):return knee.lerp(ankle,t)+across*x+front*f
    # Main cage: two tapered curved spars and two fitted transverse load ties.
    mesh_v=[];mesh_f=[]
    rail_stations=[(.095,.060,.0105,.0135),(.17,.049,.012,.016),
                   (.34,.030,.0105,.015),(.63,.023,.0095,.0135),
                   (.83,.037,.010,.0145),(.91,.052,.0115,.016)]
    for sx in (-1,1):
        prof=[]
        for t,f,hw,hd in rail_stations:
            prof.append((c(t,sx*.055,f),hw,hd))
        rv,rf=tube_along([p for p,_,_ in prof],across,front,prof,10)
        offset=len(mesh_v);mesh_v.extend(rv);mesh_f.extend([tuple(offset+i for i in face) for face in rf])
    for t,foff,hu,hv in ((.18,.050,.012,.013),(.82,.043,.011,.0125)):
        beam_into(mesh_v,mesh_f,c(t,-.055,foff),c(t,.055,foff),axis,front,hu,hv,10)
    frame=attach_world_mesh(f'{side} shin twin-bearing load cage',owner,'frame',
        'Bilateral tapered boxed load spars, swept bearing shoulders and fitted cross ties; passive static assembly.',mesh_v,mesh_f,'frame')

    # The front guards are swept to the same shank envelope and wrap into the
    # rails at their hems, with an open center for inspection and moving parts.
    guard=wrapped_guard(owner,side,knee,axis,across,front,frame.name)

    # Separate end saddles form around the cage ends. Each has a broad cross
    # bridge and two swept return cheeks; open space is retained around the axle.
    for label,t0,t1,f0,f1 in (('proximal',.12,.24,.061,.036),('distal',.88,.76,.052,.029)):
        sv=[];sf=[]
        mid=(t0+t1)/2;fmid=(f0+f1)/2
        beam_into(sv,sf,c(t0,-.055,f0),c(t0,.055,f0),axis,front,.013,.011,10)
        for sx in (-1,1):
            beam_into(sv,sf,c(t0,sx*.055,f0),c(t1,sx*.055,f1),axis,front,.010,.012,10)
        beam_into(sv,sf,c(t1,-.055,f1),c(t1,.055,f1),axis,front,.011,.011,10)
        saddle=attach_world_mesh(f'{side} shin {label} fitted bearing saddle',owner,'bearing',
            f'Fitted passive {label} cradle closes into paired cage rails while preserving the native axle envelope.',sv,sf,'bearing')
        MATING.append({'pair':[frame.name,saddle.name],'type':'fixed cage-to-saddle seat','expected':True})
    MATING.append({'pair':[frame.name,guard.name],'type':'formed guard hems into load rails','expected':True})


def build():
    assert SOURCE.exists() and sha(SOURCE)==SOURCE_SHA,'Alignment V9 native hash mismatch'
    assert FROZEN_SCRIPT.exists() and sha(FROZEN_SCRIPT)==sha(Path(__file__)), 'Freeze generator before build execution'
    assert NATIVE.parent.exists() and not any(NATIVE.parent.iterdir()),'Preserve prior V2 model output'
    assert AUDIT.exists() and {p.name for p in AUDIT.iterdir()}=={FROZEN_SCRIPT.name},'Audit directory must contain only the frozen build script before execution'
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE));bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
    before=signatures();before_names=set(before)
    meshes={o.name:o for o in bpy.data.objects if o.type=='MESH'}
    assert set(REPLACE)<=set(meshes),f'Missing allowlisted source meshes: {sorted(set(REPLACE)-set(meshes))}'
    expected_parent={
        **{n:f'{n.split()[0]}-shin' for n in REPLACE if n.startswith(('left ','right '))},
        **{f'Limb sheath fixing.{i:03d}':('left-shin' if i<=11 else 'right-shin') for i in range(6,12)},
        **{f'Limb sheath fixing.{i:03d}':'right-shin' for i in range(18,24)},
    }
    for name in REPLACE:
        assert meshes[name].parent and meshes[name].parent.name==expected_parent[name],(name,expected_parent[name],meshes[name].parent.name if meshes[name].parent else None)
    for name in sorted(REPLACE):
        bpy.data.objects.remove(meshes[name],do_unlink=True)
    build_side('left');build_side('right')
    bpy.context.view_layer.update()
    after=signatures();preserved=before_names-set(REPLACE)
    changed=[n for n in sorted(preserved) if before[n]!=after.get(n)]
    missing=sorted(preserved-set(after))
    added=sorted(set(after)-before_names)
    assert not changed and not missing, f'Preservation failed; changed={changed[:6]}, missing={missing[:6]}'
    assert len(added)==8,added
    assert set(added)==set(ADDED), (added,ADDED)
    bpy.ops.wm.save_as_mainfile(filepath=str(NATIVE))
    report={
      'status':'single fitted bilateral shin replacement; visual and clearance review required',
      'source':{'path':str(SOURCE.relative_to(ROOT)),'sha256':SOURCE_SHA},
      'native':{'path':str(NATIVE.relative_to(ROOT)),'sha256':sha(NATIVE),'bytes':NATIVE.stat().st_size},
      'generator':{'path':str(Path(__file__).relative_to(ROOT)),'sha256':sha(Path(__file__)),
        'frozenCopy':str(FROZEN_SCRIPT.relative_to(ROOT)),'frozenCopySha256':sha(FROZEN_SCRIPT),'sameBytes':sha(FROZEN_SCRIPT)==sha(Path(__file__))},
      'blender':bpy.app.version_string,
      'replacementAllowlist':sorted(REPLACE),
      'addedMeshes':added,
      'preservation':{'unchangedSourceObjects':len(preserved),'changedOrMissingPreservedObjects':changed+missing,
        'sourceMeshCount':len(meshes),'removedMeshCount':len(REPLACE),'newMeshCount':len(added),
        'pivotCount':sum(o.type=='EMPTY' for o in bpy.data.objects),
        'curveCount':sum(o.type=='CURVE' for o in bpy.data.objects),
        'materialCount':len(bpy.data.materials)},
      'owners':{n:bpy.data.objects[n].parent.name for n in added},
      'eraEligibility':{n:bpy.data.objects[n]['exteriorEras'] for n in added},
      'intendedFixedMatingContacts':MATING,
      'centerlines':{'perSide':'Existing left/right shin pivot bearing center to corresponding foot pivot bearing center; no pivot transforms changed.',
        'railCenterOffsetsNativeM':{'lateral':0.055,'frontStations':[[0.095,0.060],[0.17,0.049],[0.34,0.030],[0.63,0.023],[0.83,0.037],[0.91,0.052]]}},
      'limits':['Authored interpretation based on reference images; dimensions are not measured from a source CAD model.',
        'Passive geometry only; runtime actuation, continuous swept clearance and engineering loads are not validated.']}
    (AUDIT/'native-receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'nativeSha256':report['native']['sha256'],'removed':sorted(REPLACE),'added':added},indent=2))


def render():
    assert NATIVE.exists() and sha(FROZEN_SCRIPT)==sha(Path(__file__)),'Missing frozen generator or native'
    dest=AUDIT/'renders';assert not dest.exists(),'Preserve existing renders'
    bpy.ops.wm.open_mainfile(filepath=str(NATIVE));scene=bpy.context.scene;scene.frame_set(1)
    scene.render.engine='BLENDER_WORKBENCH';sh=scene.display.shading
    sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='MATERIAL'
    sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH'
    sh.curvature_ridge_factor=1.2;sh.curvature_valley_factor=1.1
    sh.background_type='WORLD';scene.world.color=(.11,.12,.13)
    scene.render.resolution_x=scene.render.resolution_y=1100;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    camdata=bpy.data.cameras.new('Lower leg V2 review camera')
    camera=bpy.data.objects.new('Lower leg V2 review camera',camdata);scene.collection.objects.link(camera);scene.camera=camera
    views=[('three-quarter',(-4.7,-6.5,2.30),(0,-.1,1.08),2.4),
           ('side-right',(-6,0,1.08),(0,-.1,1.08),2.4),
           ('feet',(-4,-6,.6),(0,-.1,.31),.98),
           ('feet-side',(-6,-.1,.32),(0,-.1,.31),.98)]
    dest.mkdir();records=[]
    for era in ('maker','mechanic','builder'):
      for view,pos,target,scale in views:
        for obj in scene.objects:
          if obj.type=='MESH':
            obj.hide_render=era not in obj.get('exteriorEras',ERA).split(',');obj.hide_set(False)
        camera.location=pos;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
        camdata.type='ORTHO';camdata.ortho_scale=scale
        path=dest/f'{era}-{view}.png';scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
        records.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),'bytes':path.stat().st_size,
          'era':era,'view':view,'camera':pos,'target':target,'projection':'ORTHO','orthoScale':scale,'resolution':[1100,1100]})
    base=ROOT/'assets/audit/alignment-v9/neutral-views'
    before=[]
    for era in ('maker','mechanic','builder'):
      for view in ('three-quarter','side-right','feet','feet-side'):
        path=base/f'{era}-{view}.png';before.append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),'bytes':path.stat().st_size,'era':era,'view':view})
    reference_script=ROOT/'scripts/render-alignment-v7.py'
    manifest={'status':'matched fixed-rest V9 source and V2 candidate views; local authoring render',
      'source':{'path':str(SOURCE.relative_to(ROOT)),'sha256':SOURCE_SHA},
      'native':{'path':str(NATIVE.relative_to(ROOT)),'sha256':sha(NATIVE)},
      'generator':{'path':str(Path(__file__).relative_to(ROOT)),'sha256':sha(Path(__file__)),'frozenCopySha256':sha(FROZEN_SCRIPT)},
      'baselineRenderer':{'path':str(reference_script.relative_to(ROOT)),'sha256':sha(reference_script)},
      'renderSettings':'BLENDER_WORKBENCH, paint.sl studio, material colors, shadows/cavity, 1100px square.',
      'beforeImages':before,'afterImages':records,
      'limits':['Neutral authoring views at fixed rest, not browser/export appearance.',
        'Era eligibility marks additions visible in all three eras; all are passive and use the same static geometry.']}
    (AUDIT/'render-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Rendered',len(records),'V2 views')


def audit():
    assert NATIVE.exists() and sha(FROZEN_SCRIPT)==sha(Path(__file__)),'Missing frozen generator or native'
    helper=ROOT/'scripts/diagnose-native-regional-clearance.py'
    kernel=ROOT/'assets/audit/cervical-construction-study-v1/attempt-07/actual-runtime-joint-clearance-v1/executed-review.py'
    h=runpy.run_path(str(helper),run_name='lower_leg_v2_clearance_helpers')
    proper=runpy.run_path(str(kernel),run_name='lower_leg_v2_crossing_kernel')['proper_crossing_receipt']
    bpy.ops.wm.open_mainfile(filepath=str(NATIVE));bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get();meshes={o.name:o for o in bpy.data.objects if o.type=='MESH'}
    ADDED[:]=sorted(o.name for o in bpy.data.objects if o.type=='MESH' and o.get('studyVersion')=='v2-fitted-replacement')
    assert len(ADDED)==8,ADDED
    subjects=[meshes[n] for n in ADDED]
    for side in ('left','right'):
      frame=f'{side} shin twin-bearing load cage';guard=f'{side} shin integrated anterior wrap guard'
      MATING.extend([{'pair':[frame,f'{side} shin proximal fitted bearing saddle'],'type':'fixed cage-to-saddle seat','expected':True},
                     {'pair':[frame,f'{side} shin distal fitted bearing saddle'],'type':'fixed cage-to-saddle seat','expected':True},
                     {'pair':[frame,guard],'type':'formed guard hems into load rails','expected':True}])
    target_owners={'left-shin','right-shin','left-thigh','right-thigh','left-foot','right-foot','body'}
    targets=[o for o in meshes.values() if o.parent and o.parent.name in target_owners]
    surfaces={o.name:h['surface'](o,dg) for o in set(subjects+targets)}
    mates={tuple(sorted(row['pair'])) for row in MATING}
    rows=[];visited=set()
    for subject in subjects:
      for target in targets:
        a,b=surfaces[subject.name],surfaces[target.name]
        pairkey=tuple(sorted((subject.name,target.name)))
        if subject==target or pairkey in visited:continue
        visited.add(pairkey)
        if not a or not b or not h['bounds_overlap'](a,b):continue
        overlaps=a['tree'].overlap(b['tree'])
        if not overlaps:continue
        proof=proper(a,b,overlaps,Matrix.Identity(4),Matrix.Identity(4))
        strict=bool(proof['confirmedSubjectTriangleCount'] or proof['confirmedTargetTriangleCount'])
        if strict:
          rows.append({'meshA':subject.name,'ownerA':subject.parent.name,'meshB':target.name,
            'ownerB':target.parent.name,'category':'same-owner' if subject.parent==target.parent else 'different-owner',
            'bvhTrianglePairCandidateCount':len(overlaps),'strictNoncoplanarCrossing':True,
            'expectedFixedMate':tuple(sorted((subject.name,target.name))) in mates,
            'strictReceipt':proof})
        else:
          rows.append({'meshA':subject.name,'ownerA':subject.parent.name,'meshB':target.name,
            'ownerB':target.parent.name,'category':'same-owner' if subject.parent==target.parent else 'different-owner',
            'bvhTrianglePairCandidateCount':len(overlaps),'strictNoncoplanarCrossing':False,
            'expectedFixedMate':tuple(sorted((subject.name,target.name))) in mates,'strictReceipt':None})
    dest=AUDIT/'rest-clearance.json';assert not dest.exists(),'Preserve any previous clearance report'
    report={'status':'read-only rest-state proper-world surface/BVH screen for new shin parts against shin, adjacent thigh/foot and body owners',
      'native':{'path':str(NATIVE.relative_to(ROOT)),'sha256':sha(NATIVE)},
      'generatorSha256':sha(Path(__file__)),'blender':bpy.app.version_string,
      'surfaceHelper':{'path':str(helper.relative_to(ROOT)),'sha256':sha(helper),'coordinateFrame':'evaluated vertices transformed by evaluated.matrix_world into native world XYZ'},
      'strictKernel':{'path':str(kernel.relative_to(ROOT)),'sha256':sha(kernel),'method':'proper_crossing_receipt strict noncoplanar edge-through-face tests'},
      'scope':{'subjects':ADDED,'targetOwnerScope':sorted(target_owners),'targetMeshCount':len(targets),
        'sourceReplacementAllowlist':sorted(REPLACE),'sameOwnerPairsSeparate':True,'fullContainment':'not tested','poseSweep':'not tested'},
      'summary':{'bvhCandidatePairs':len(rows),'strictDifferentOwnerPairs':sum(r['category']=='different-owner' and r['strictNoncoplanarCrossing'] for r in rows),
        'strictSameOwnerPairs':sum(r['category']=='same-owner' and r['strictNoncoplanarCrossing'] for r in rows),
        'expectedFixedMatingCrossings':sum(r['expectedFixedMate'] and r['strictNoncoplanarCrossing'] for r in rows),
        'unexpectedStrictCrossings':[{'meshA':r['meshA'],'meshB':r['meshB'],'category':r['category']} for r in rows if r['strictNoncoplanarCrossing'] and not r['expectedFixedMate']]},
      'pairs':rows,'limits':['BVH-only candidates are retained separately from strict crossings.',
        'Strict surface crossing is not penetration depth or containment.',
        'Fixed rest only; pose packet and moving Mechanic/Builder surfaces are separate next checks.']}
    dest.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['summary'],indent=2))


if args.mode=='build':build()
elif args.mode=='render':render()
else:audit()
