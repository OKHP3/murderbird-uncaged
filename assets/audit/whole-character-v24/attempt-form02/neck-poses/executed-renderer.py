"""Read-only native illustrations of declared V24 neck/jaw input angles.
Not full exhibit behavior, contact solving, collision clearance or physics.
"""
from pathlib import Path
import bpy, bmesh, hashlib, json, math, shutil
from mathutils import Matrix, Quaternion, Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
NATIVE=ROOT/'assets/models/whole-character-v24/attempt-form02/murderbird-whole-character-v24.blend'
EXPECTED='acb91013e0ca7cf98475e0d2ba6fb36d9c081c29c91b27e104bf7367d57f306d'
OUT=ROOT/'assets/audit/whole-character-v24/attempt-form02/neck-poses'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(NATIVE)==EXPECTED and not OUT.exists();OUT.mkdir()
shutil.copyfile(__file__,OUT/'executed-renderer.py');bpy.ops.wm.open_mainfile(filepath=str(NATIVE))
chain=['neck','cervical-mid-a','cervical-mid-b','cervical-upper']
owners=chain+['head','jaw']
rest={n:{'position':bpy.data.objects[n].location.copy(),'rotation':bpy.data.objects[n].rotation_quaternion.copy(),
         'matrix':bpy.data.objects[n].matrix_local.copy(),'scale':bpy.data.objects[n].scale.copy()} for n in owners}
for n in owners:bpy.data.objects[n].rotation_mode='QUATERNION'
scene=bpy.context.scene
for o in bpy.data.objects:
    if o.animation_data:o.animation_data_clear()
    if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
    elif o.type=='CURVE':o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';sh=scene.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='SINGLE';sh.single_color=(.56,.58,.60);sh.show_shadows=False;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';scene.world.color=(.12,.13,.14)
scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
camdata=bpy.data.cameras.new('V24 neck pose camera');camdata.type='ORTHO';camera=bpy.data.objects.new(camdata.name,camdata);scene.collection.objects.link(camera);scene.camera=camera
camera.location=(-6,-3.5,2.45);camera.rotation_euler=(Vector((0,-.27,1.48))-camera.location).to_track_quat('-Z','Y').to_euler();camdata.ortho_scale=1.40
receipt={'native':{'path':NATIVE.relative_to(ROOT).as_posix(),'sha256':EXPECTED},'executedRendererSha256':sha(OUT/'executed-renderer.py'),
 'status':'Discrete native angle illustrations, not runtime or continuous-clearance acceptance','poses':[],
 'limits':['Inputs reproduce selected required neck/head angles; no body motion, contact solver, stepping or jump is claimed.',
 'Intersection screen covers only new cervical plates against other-owner visible neck/head/breast plates. BVH overlap identities are potential surface crossings, not penetration depth, strict-triangle clearance or collision simulation.',
 'Neighbor bearings/pins and same-owner plate intersections are excluded from this screen.']}
states=[('rest',0,0,0,0),('maker-neck-jaw',-.14,-.45,0,.32),('attention',.08,.288,.02,0),('contact-neck',.65,0,-.731,.10),('thrust-neck',-.07,0,-.035,0)]
for label,pitch,yaw,head,jaw in states:
    for i,n in enumerate(chain):
        o=bpy.data.objects[n];base=rest[n]['matrix'].to_quaternion()
        delta=Quaternion((1,0,0),pitch*.25)
        if i==0:delta=delta@Quaternion((0,0,1),yaw)
        desired=base@delta;o.rotation_quaternion=o.matrix_parent_inverse.to_quaternion().inverted()@desired
    for n,value in [('head',head),('jaw',jaw)]:
        o=bpy.data.objects[n];o.rotation_quaternion=o.matrix_parent_inverse.to_quaternion().inverted()@rest[n]['matrix'].to_quaternion()@Quaternion((1,0,0),value)
    bpy.context.view_layer.update();expected={n:bpy.data.objects[n].matrix_local.copy() for n in owners}
    scene.render.filepath=str(OUT/f'{label}.png');bpy.ops.render.render(write_still=True)
    actual={n:bpy.data.objects[n].matrix_local for n in owners}
    error=max(abs(actual[n][r][c]-expected[n][r][c]) for n in owners for r in range(4) for c in range(4));assert error<2e-6
    translation=max((actual[n].translation-rest[n]['matrix'].translation).length for n in owners);assert translation<2e-6
    # Scoped broad phase and exact triangle surface crossing witnesses.
    visible=[];deps=bpy.context.evaluated_depsgraph_get()
    for o in bpy.data.objects:
        if o.type!='MESH' or o.hide_render or not o.parent:continue
        relevant=o.name.startswith('V23 cervical') and o.get('surfaceRole')=='plate'
        neighbor=o.parent.name in owners+['breastplate','body','cranial-cover','upper-bill'] and o.get('surfaceRole') in ('plate','guard','shell')
        if not relevant and not neighbor:continue
        ev=o.evaluated_get(deps);mesh=ev.to_mesh();verts=[ev.matrix_world@v.co for v in mesh.vertices]
        if verts:
            lo=Vector(tuple(min(p[k] for p in verts) for k in range(3)));hi=Vector(tuple(max(p[k] for p in verts) for k in range(3)))
            tree=BVHTree.FromPolygons(verts,[list(p.vertices) for p in mesh.polygons],all_triangles=False)
            visible.append((o.name,o.parent.name,relevant,lo,hi,tree))
        ev.to_mesh_clear()
    crossings=[]
    for i,A in enumerate(visible):
        for B in visible[i+1:]:
            if A[1]==B[1] or not(A[2] or B[2]):continue
            if any(A[4][k]<B[3][k] or B[4][k]<A[3][k] for k in range(3)):continue
            hits=A[5].overlap(B[5])
            if hits:crossings.append({'a':A[0],'b':B[0],'triangleCrossings':len(hits)})
    receipt['poses'].append({'name':label,'totalNeckPitch':pitch,'rootYaw':yaw,'headPitch':head,'jawPitch':jaw,
      'image':{'path':Path(scene.render.filepath).relative_to(ROOT).as_posix(),'sha256':sha(scene.render.filepath)},
      'postRenderLocalMatrixError':error,'fixedAttachmentTranslationError':translation,'crossingPairCount':len(crossings),'crossingPairs':crossings})
    (OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
assert sha(NATIVE)==EXPECTED
print(json.dumps({'nativeUnchanged':True,'poses':[{k:p[k] for k in ('name','crossingPairCount','postRenderLocalMatrixError','fixedAttachmentTranslationError')} for p in receipt['poses']]}))
