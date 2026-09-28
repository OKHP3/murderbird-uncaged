"""Build one conservative convex-hull brow relief from the pinned V6 native."""
from pathlib import Path
import hashlib, json, math, runpy, shutil
import bpy, bmesh
from mathutils import Matrix, Vector

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'assets/models/uncaged-orbital-saddle-study-v6/murderbird-orbital-saddle-study-v6.blend'
BASE_SHA='cb811241d241b0f18f529979b77635caecb83284b8b4df29c7564d4d2bf55eec'
HELPER=ROOT/'scripts/build-uncaged-alignment-v7.py'
HELPER_SHA='39b6ee2285d8c49df3a902f8fac0a07589da3d41f48ae24df1e06515c839033a'
SURFACE_HELPER=ROOT/'scripts/diagnose-native-regional-clearance.py'
OUT=ROOT/'assets/models/uncaged-orbital-saddle-study-v8'
AUDIT=ROOT/'assets/audit/orbital-saddle-study-v8'
SIDES=(-1,1)


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def artifact(p): return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
def signed_volume(mesh):
    mesh.calc_loop_triangles();v=0.0
    for tri in mesh.loop_triangles:
        a,b,c=(mesh.vertices[i].co for i in tri.vertices);v+=a.dot(b.cross(c))/6
    return v
def bounds(points): return [[min(float(p[i]) for p in points),max(float(p[i]) for p in points)] for i in range(3)]
def world_points(obj,dg):
    ev=obj.evaluated_get(dg);mesh=ev.to_mesh();pts=[ev.matrix_world@v.co for v in mesh.vertices];ev.to_mesh_clear();return pts
def topology(mesh):
    bm=bmesh.new();bm.from_mesh(mesh)
    nonman=sum(not e.is_manifold for e in bm.edges);unseen=set(bm.verts);components=[]
    while unseen:
        stack=[unseen.pop()];count=0
        while stack:
            v=stack.pop();count+=1
            for e in v.link_edges:
                q=e.other_vert(v)
                if q in unseen:unseen.remove(q);stack.append(q)
        components.append(count)
    result={'vertices':len(bm.verts),'edges':len(bm.edges),'faces':len(bm.faces),'nonManifoldEdges':nonman,
      'componentVertexCounts':sorted(components),'signedVolumeObjectLocalM3':signed_volume(mesh)}
    bm.free();return result
def hull_cutter(mount,side):
    dg=bpy.context.evaluated_depsgraph_get();pts=world_points(mount,dg)
    corners=[Vector((x*.001,y*.001,z*.001)) for x in (-1,1) for y in (-1,1) for z in (-1,1)]
    expanded=[p+off for p in pts for off in corners]
    data=bpy.data.meshes.new(f'V8 temporary conservative relief hull {side}')
    cutter=bpy.data.objects.new(data.name,data);bpy.context.scene.collection.objects.link(cutter)
    bm=bmesh.new()
    for p in expanded:bm.verts.new(p)
    bm.verts.ensure_lookup_table()
    hull=bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
    interior=hull.get('geom_interior',[])
    if interior:bmesh.ops.delete(bm,geom=interior,context='VERTS')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();data.update()
    cutter.matrix_world=Matrix.Identity(4);cutter.hide_render=True;cutter.hide_set(True)
    hull_info={'sourceEvaluatedWorldVertexCount':len(pts),'expandedPointCount':len(expanded),
       'expandedCornersPerSourceVertex':8,'worldAxisBoxHalfExtentM':.001,
       'rawHullVertexCount':len(data.vertices),'rawHullEdgeCount':len(data.edges),'rawHullFaceCount':len(data.polygons),
       'rawHullSignedVolumeM3':signed_volume(data),'rawHullWorldBoundsXYZ':bounds([v.co for v in data.vertices]),
       'construction':'Convex hull of every evaluated mounting-wall world vertex plus all eight ±1mm Cartesian corner offsets; conservative L-infinity box expansion, not a normal offset.'}
    return cutter,hull_info

def surface_distance(a,b):
    return {'maxAtoBVertexSurfaceDistanceM':max((float(b['tree'].find_nearest(p)[3]) for p in a['points']),default=0),
      'maxBtoAVertexSurfaceDistanceM':max((float(a['tree'].find_nearest(p)[3]) for p in b['points']),default=0)}

def configure_render(scene):
    scene.render.engine='BLENDER_WORKBENCH';sh=scene.display.shading
    sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='MATERIAL'
    sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD'
    scene.world.color=(.11,.12,.13);scene.render.resolution_x=scene.render.resolution_y=1100
    scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
    for obj in bpy.data.objects:
        if obj.type=='MESH':obj.hide_render='builder' not in obj.get('exteriorEras','maker,mechanic,builder').split(',');obj.hide_set(False)
def camera(scene,name,position,target,scale):
    cd=bpy.data.cameras.new(name);cam=bpy.data.objects.new(name,cd);scene.collection.objects.link(cam);scene.camera=cam
    cam.location=position;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=scale
    return cam
def render_set(native,label):
    bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene;configure_render(scene)
    cam=camera(scene,'Temporary V8 matched camera',(-6,-3,2.4),(0,-.29,1.78),.88);records=[]
    for view,pos,target,scale in [('front',(0,-6,1.78),(0,-.3,1.78),1.05),('right-profile',(-6,-.3,1.78),(0,-.3,1.78),1.1),('three-quarter',(-6,-3,2.4),(0,-.29,1.78),.88)]:
        cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
        path=AUDIT/f'{label}-{view}.png';scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
        records.append({'view':view,'variant':label,'camera':{'position':pos,'target':target,'ortho':scale},**artifact(path)})
    return records
def render_open(native):
    bpy.ops.wm.open_mainfile(filepath=str(native));scene=bpy.context.scene;configure_render(scene)
    cam=camera(scene,'Temporary V8 opening camera',(-6,-3,2.4),(0,-.29,1.78),.88)
    cover=bpy.data.objects['cranial-cover'];rest=cover.location.copy();records=[]
    for fraction in (0,.125,1):
        cover.location=rest.copy();cover.location.z+=.08*fraction;bpy.context.view_layer.update()
        path=AUDIT/f'opening-{round(fraction*1000):04d}.png';scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
        records.append({'openFraction':fraction,'nativeLocalZLiftM':.08*fraction,**artifact(path)})
    return records

def main():
    assert sha(BASE)==BASE_SHA and sha(HELPER)==HELPER_SHA
    assert not OUT.exists() and not AUDIT.exists(),'Preserve existing V8 output'
    h=runpy.run_path(str(HELPER),run_name='snapshot_helpers')
    regional=runpy.run_path(str(SURFACE_HELPER),run_name='regional_helpers')
    bpy.ops.wm.open_mainfile(filepath=str(BASE));bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
    before=h['scene_snapshot']();materials={m.name:h['material_signature'](m) for m in bpy.data.materials}
    changed=[];records=[]
    for side in SIDES:
        brow=bpy.data.objects[f'Forged orbital brow {side}'];mount=bpy.data.objects[f'Forged orbital mounting plate {side}']
        assert brow.parent and mount.parent and brow.data!=mount.data
        before_obj={'parent':brow.parent.name,'matrixWorld':[[float(brow.matrix_world[r][c]) for c in range(4)] for r in range(4)],
           'mesh':topology(brow.data),'bounds':bounds(world_points(brow,bpy.context.evaluated_depsgraph_get()))}
        mount_world=world_points(mount,bpy.context.evaluated_depsgraph_get())
        cutter,hull_info=hull_cutter(mount,side)
        # Confirm the conservative hull encloses the entire closed source wall by exact in-memory difference.
        residual=mount.copy();residual.data=mount.data.copy();residual.name=f'Temporary wall containment check {side}';bpy.context.scene.collection.objects.link(residual);residual.matrix_world=mount.matrix_world.copy()
        check=residual.modifiers.new('Temporary hull containment check','BOOLEAN');check.operation='DIFFERENCE';check.solver='EXACT';check.object=cutter
        bpy.context.view_layer.objects.active=residual;bpy.ops.object.modifier_apply(modifier=check.name)
        residual_top=topology(residual.data);bpy.data.objects.remove(residual,do_unlink=True)
        assert residual_top['faces']==0 or abs(residual_top['signedVolumeObjectLocalM3'])<1e-12,(side,residual_top)
        before_surface=regional['surface'](brow,bpy.context.evaluated_depsgraph_get())
        modifier=brow.modifiers.new('Frozen conservative mounting-hull relief','BOOLEAN');modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
        bpy.context.view_layer.objects.active=brow;bpy.ops.object.modifier_apply(modifier=modifier.name)
        after_obj={'parent':brow.parent.name,'matrixWorld':[[float(brow.matrix_world[r][c]) for c in range(4)] for r in range(4)],'mesh':topology(brow.data),'bounds':bounds(world_points(brow,bpy.context.evaluated_depsgraph_get()))}
        after_surface=regional['surface'](brow,bpy.context.evaluated_depsgraph_get())
        relief={'name':brow.name,'parentUnchanged':before_obj['parent']==after_obj['parent'],'before':before_obj,'after':after_obj,
          'removedVolumeM3':before_obj['mesh']['signedVolumeObjectLocalM3']-after_obj['mesh']['signedVolumeObjectLocalM3'],
          'removedVolumeFraction':(before_obj['mesh']['signedVolumeObjectLocalM3']-after_obj['mesh']['signedVolumeObjectLocalM3'])/before_obj['mesh']['signedVolumeObjectLocalM3'],
          'surfaceDeviationM':surface_distance(before_surface,after_surface),
          'cutter':hull_info,'mountWorldBoundsXYZ':bounds(mount_world),
          'sourceWallMinusHullVolumeM3':residual_top['signedVolumeObjectLocalM3'],'sourceWallMinusHullFaceCount':residual_top['faces']}
        assert relief['parentUnchanged'] and after_obj['mesh']['nonManifoldEdges']==0 and len(after_obj['mesh']['componentVertexCounts'])==1 and after_obj['mesh']['signedVolumeObjectLocalM3']>0,relief
        records.append(relief);changed.append(brow.name)
        cutter_data=cutter.data
        bpy.data.objects.remove(cutter,do_unlink=True)
        if cutter_data.users==0:bpy.data.meshes.remove(cutter_data)
    bpy.context.view_layer.update();after=h['scene_snapshot']()
    assert before['empties']==after['empties'] and before['curves']==after['curves']
    assert len(before['empties'])==51 and len(before['curves'])==462
    assert set(before['meshes'])==set(after['meshes']) and len(before['meshes'])==699
    for name,signature in before['meshes'].items():
        if name not in changed:assert after['meshes'][name]==signature,name
    assert materials=={m.name:h['material_signature'](m) for m in bpy.data.materials}
    OUT.mkdir(parents=True);AUDIT.mkdir(parents=True)
    native=OUT/'murderbird-orbital-saddle-study-v8.blend';bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(native))
    assert h['scene_snapshot']()==after
    shutil.copy2(__file__,AUDIT/'executed-generator.py')
    receipt={'status':'unreviewed conservative hull brow relief; not selected','base':artifact(BASE),'native':artifact(native),
      'generator':artifact(AUDIT/'executed-generator.py'),'sourceGenerator':artifact(Path(__file__)),
      'changedMeshes':changed,'browRelief':records,
      'preservation':{'other697MeshesExact':True,'51PivotsAnd462CurvesExact':True,'materialsExact':True,'saveReloadExact':True,'temporaryCuttersRemoved':True},
      'construction':'For each fixed mounting plate, form a disposable cutter from its evaluated world vertices plus all eight ±1 mm Cartesian corner offsets, then take the convex hull. Apply exact Boolean Difference to the matching brow. This is conservative L-infinity box-expansion relief, not a normal-offset fit.',
      'limits':['The convex hull can remove more material than the local mount-wall footprint; surface deviation and removed volume are reported for review.',
        'No mount/pin intersection is accepted by ownership or geometry alone; retained pin6, crown and hood crossings are separately screened.',
        'No export, app edit, publication, commit, or owner acceptance.']}
    (AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    receipt['neutralRenders']=render_set(BASE,'before')+render_set(native,'after')
    receipt['openingRenders']=render_open(native)
    (AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'native':artifact(native),'changed':changed,'removedVolumeFractions':[r['removedVolumeFraction'] for r in records],
      'neutralRenderCount':len(receipt['neutralRenders']),'openingRenderCount':len(receipt['openingRenders'])}))

if __name__=='__main__':main()
