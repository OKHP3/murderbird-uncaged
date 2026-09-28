"""Create a native-only, hash-bound head-construction study from frozen V7."""
from pathlib import Path
import bpy
import bmesh
import hashlib
import json
import math
import os
import shutil
import struct
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/models/uncaged-alignment-v7/murderbird-alignment-v7.blend"
INVENTORY = ROOT / "assets/models/uncaged-alignment-v7/alignment-inventory.json"
HEAD_RECIPE = ROOT / "scripts/alignment-v6-head.py"
JULY = ROOT / "context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png"
MODEL_DIR = ROOT / "assets/models/uncaged-head-construction-study-v2"
AUDIT_DIR = ROOT / "assets/audit/head-construction-study-v2"
ATTEMPT = "attempt-02"
ATTEMPT_MODEL_DIR = MODEL_DIR / "iterations" / ATTEMPT
ATTEMPT_AUDIT_DIR = AUDIT_DIR / "iterations" / ATTEMPT
CANDIDATE = ATTEMPT_MODEL_DIR / "murderbird-head-construction-study-v2.blend"
MANIFEST = ATTEMPT_AUDIT_DIR / "head-construction-study-v2.json"
PREMUTATION = ATTEMPT_AUDIT_DIR / "target-contracts-before-mutation.json"
SCRIPT_SNAPSHOT = ATTEMPT_AUDIT_DIR / "study-v7-head-construction.py"
EXPECTED = {
    "source": "a8fccaf024a096678415215029b34cae8270b348da2301b8872a34e72c75ed3f",
    "inventory": "9346323a07dd618dcb9680cf5d5d620aef1c6608c986a590a3a9aee90d550c5c",
    "headRecipe": "a921130111ac27f14f1ddda10328f7dd21bf2cffa1d4e34aee8d1756fd738472",
    "july": "47658dba6496f2c8594a40ad412a8bfaa087939e90044d1597329a27ca68d4e9",
}
UNUSED_RETAINED_MATERIALS = {"Neutral / edge.001", "Neutral / plate.001"}
TARGETS = {
    "Forged orbital brow -1": "cranial-cover", "Forged orbital brow 1": "cranial-cover",
    "Cere root transition -1": "upper-bill", "Cere root transition 1": "upper-bill",
    "Broad swept cheek band -1": "head", "Broad swept cheek band 1": "head",
    "Overlapping nasal hood": "upper-bill",
    "Profiled upper bill blade 0": "upper-bill", "Profiled upper bill blade 1": "upper-bill",
}
CAMERAS = [
    {"name":"front-bilateral", "position":(0,-6,1.78), "target":(0,-.30,1.78), "ortho":1.05},
    {"name":"left-profile", "position":(-6,-.30,1.78), "target":(0,-.30,1.78), "ortho":1.10},
    {"name":"right-profile", "position":(6,-.30,1.78), "target":(0,-.30,1.78), "ortho":1.10},
    {"name":"three-quarter-a", "position":(-6,-3,2.4), "target":(0,-.29,1.78), "ortho":.88},
    {"name":"three-quarter-b", "position":(-6,-4.2,2.1), "target":(0,-.29,1.78), "ortho":.88},
]
FINAL_OUTPUTS = [CANDIDATE, MANIFEST, PREMUTATION, SCRIPT_SNAPSHOT] + [
    ATTEMPT_AUDIT_DIR / f"{phase}-{spec['name']}.png" for phase in ("before", "after") for spec in CAMERAS
]
HEAD_SECTIONS = [(1.575,-.15,.065,.10),(1.65,-.20,.123,.185),(1.74,-.25,.149,.22),
                 (1.825,-.265,.153,.20),(1.915,-.24,.119,.175),(1.955,-.17,.025,.075)]

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def serial(v):
    if isinstance(v,(str,int,float,bool)) or v is None: return v
    if hasattr(v,"to_list"): return [serial(x) for x in v.to_list()]
    try: return [serial(x) for x in v]
    except TypeError: return str(v)

def mesh_sig(mesh):
    coords=hashlib.sha256(); topo=hashlib.sha256()
    for v in mesh.vertices: coords.update(struct.pack('<3d',*v.co))
    for e in mesh.edges: topo.update(struct.pack('<2I',*e.vertices))
    for p in mesh.polygons:
        topo.update(struct.pack('<I',len(p.vertices))); topo.update(struct.pack('<%dI'%len(p.vertices),*p.vertices))
        topo.update(struct.pack('<i?',p.material_index,p.use_smooth))
    return {"name":mesh.name,"vertices":len(mesh.vertices),"edges":len(mesh.edges),"polygons":len(mesh.polygons),
            "coords":coords.hexdigest(),"topology":topo.hexdigest(),"materials":[m.name if m else None for m in mesh.materials]}

def obj_sig(o):
    if o.type=='MESH': data=mesh_sig(o.data)
    elif o.type=='CURVE':
        splines=[]
        for s in o.data.splines:
            if s.type=='BEZIER': points=[[list(p.co),list(p.handle_left),list(p.handle_right),p.handle_left_type,p.handle_right_type] for p in s.bezier_points]
            else: points=[list(p.co) for p in s.points]
            splines.append({"type":s.type,"cyclic":s.use_cyclic_u,"points":points})
        data={"name":o.data.name,"dimensions":o.data.dimensions,"resolutionU":o.data.resolution_u,
              "bevelDepth":o.data.bevel_depth,"splines":splines}
    else: data=o.data.name if o.data else None
    mods=[]
    for m in o.modifiers:
        props={k:serial(getattr(m,k)) for k in ("levels","render_levels","thickness","offset","width","segments","limit_method","angle_limit","use_clamp_overlap","use_even_offset") if hasattr(m,k)}
        mods.append({"name":m.name,"type":m.type,"properties":props})
    return {"type":o.type,"data":data,
            "parent":o.parent.name if o.parent else None,
            "matrixBasis":[float(x) for row in o.matrix_basis for x in row],
            "matrixParentInverse":[float(x) for row in o.matrix_parent_inverse for x in row],
            "location":list(o.location),"rotation":list(o.rotation_euler),"scale":list(o.scale),"rotationMode":o.rotation_mode,
            "parentType":o.parent_type,"hideRender":bool(o.hide_render),"props":{k:serial(o[k]) for k in sorted(o.keys())},"modifiers":mods}

def snapshot():
    mats=[]
    for m in bpy.data.materials:
        nodes=[]; links=[]
        if m.use_nodes and m.node_tree:
            for n in m.node_tree.nodes:
                vals=[]
                for s in n.inputs:
                    if s.enabled and hasattr(s,"default_value"): vals.append((s.identifier,serial(s.default_value)))
                nodes.append((n.name,n.bl_idname,sorted(vals)))
            links=sorted((l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links)
        mats.append((m.name,tuple(m.diffuse_color),m.metallic,m.roughness,m.use_nodes,m.use_fake_user,sorted(nodes),links))
    return {"objects":{o.name:obj_sig(o) for o in bpy.data.objects},"materials":sorted(mats)}

def spline(rows,t):
    x=max(0,min(1,t))*(len(rows)-1); i=min(int(x),len(rows)-2); u=x-i
    p0,p1=rows[max(0,i-1)],rows[i]; p2,p3=rows[i+1],rows[min(len(rows)-1,i+2)]
    return tuple(.5*(2*p1[k]+(-p0[k]+p2[k])*u+(2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*u*u+(-p0[k]+3*p1[k]-3*p2[k]+p3[k])*u*u*u) for k in range(len(p1)))

def cranial_width(y,z):
    for a,b in zip(HEAD_SECTIONS,HEAD_SECTIONS[1:]):
        if a[0]<=z<=b[0]:
            t=(z-a[0])/(b[0]-a[0]); cy=a[1]+(b[1]-a[1])*t; rx=a[2]+(b[2]-a[2])*t; ry=a[3]+(b[3]-a[3])*t; break
    else: cy,rx,ry=HEAD_SECTIONS[0][1:] if z<HEAD_SECTIONS[0][0] else HEAD_SECTIONS[-1][1:]
    q=(y-cy)/max(.05,ry)
    return rx*math.sqrt(max(.12,1-q*q))

def replace_mesh(obj, world_vertices, faces, smooth=False):
    inv=obj.matrix_world.inverted(); verts=[inv@Vector(v) for v in world_vertices]; materials=list(obj.data.materials)
    mesh=obj.data; mesh.clear_geometry(); mesh.from_pydata(verts,[],faces); mesh.materials.clear()
    for m in materials: mesh.materials.append(m)
    mesh.update(calc_edges=True)
    for p in mesh.polygons: p.use_smooth=smooth
    mesh.validate(clean_customdata=False)
    bm=bmesh.new(); bm.from_mesh(mesh); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(mesh); bm.free()

def swept_band(side, path, lift=.025):
    along, across=56,12; stride=across+1; verts=[]; faces=[]
    for skin in (0,1):
        for j in range(along+1):
            t=j/along; y,z,w,depth=spline(path,t)
            prev=spline(path,max(0,t-1/along)); nxt=spline(path,min(1,t+1/along))
            dy,dz=nxt[0]-prev[0],nxt[1]-prev[1]; mag=max(1e-8,math.hypot(dy,dz))
            for k in range(stride):
                u=k/across; offset=(2*u-1)*max(.001,w)
                yy=y-dz/mag*offset; zz=z+dy/mag*offset
                crown=.004*math.sin(math.pi*u)
                x=cranial_width(yy,zz)+lift+(crown if skin==0 else -max(.005,depth))
                verts.append((side*x,yy,zz))
    base=(along+1)*stride
    for j in range(along):
        for k in range(across):
            a=j*stride+k; b=a+1; c=b+stride; d=a+stride
            faces.extend([(a,b,c,d),(base+d,base+c,base+b,base+a)])
        a=j*stride; b=(j+1)*stride; faces.append((a,b,base+b,base+a))
        a=j*stride+across; b=(j+1)*stride+across; faces.append((b,a,base+a,base+b))
    for k in range(across):
        faces.append((k+1,k,base+k,base+k+1)); a=along*stride+k; faces.append((a,a+1,base+a+1,base+a))
    return verts,faces

def bridge_mesh(obj, side=0):
    # One continuous, thick crown-to-cere saddle. Its broad ends overlap the existing brow and bill root.
    rows=[(-.382,1.930,.043,.006),(-.414,1.921,.068,.008),(-.450,1.892,.071,.009),(-.484,1.854,.056,.008),(-.507,1.821,.028,.006)]
    along,across=40,16; stride=across+1; verts=[]; faces=[]
    for skin in (0,1):
        for j in range(along+1):
            y,z,w,d=spline(rows,j/along)
            for k in range(stride):
                u=2*k/across-1; x=w*u
                dome=.012*(1-u*u)
                zz=z+dome+(0 if skin==0 else -max(.006,d))
                verts.append((x,y,zz))
    base=(along+1)*stride
    for j in range(along):
        for k in range(across):
            a=j*stride+k; faces.extend([(a,a+1,a+1+stride,a+stride),(base+a+stride,base+a+1+stride,base+a+1,base+a)])
        a=j*stride; b=(j+1)*stride; faces.append((a,b,base+b,base+a))
        a=j*stride+across; b=(j+1)*stride+across; faces.append((b,a,base+a,base+b))
    for k in range(across):
        faces.append((k+1,k,base+k,base+k+1)); a=along*stride+k; faces.append((a,a+1,base+a+1,base+a))
    return verts,faces

def target_contracts(targets):
    return {n:{"type":o.type,"parent":o.parent.name if o.parent else None,"vertices":len(o.data.vertices),
               "polygons":len(o.data.polygons),"transform":{"basis":obj_sig(o)["matrixBasis"],"parentInverse":obj_sig(o)["matrixParentInverse"],"location":list(o.location),"rotation":list(o.rotation_euler),"scale":list(o.scale)},
               "materials":[m.name if m else None for m in o.data.materials],
               "inventory":inventory_by_name[n]} for n,o in sorted(targets.items())}

def create_candidate():
    for path,expected in [(SOURCE,EXPECTED['source']),(INVENTORY,EXPECTED['inventory']),(HEAD_RECIPE,EXPECTED['headRecipe']),(JULY,EXPECTED['july'])]:
        if not path.is_file() or sha(path)!=expected: raise RuntimeError(f"Frozen input hash mismatch: {path}")
    for d in (ATTEMPT_MODEL_DIR,ATTEMPT_AUDIT_DIR): d.mkdir(parents=True,exist_ok=True)
    found=[str(p) for p in FINAL_OUTPUTS if p.exists()]
    if found: raise RuntimeError(f"Refusing to overwrite existing study outputs: {found}")
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE)); before=snapshot()
    targets={name:bpy.data.objects.get(name) for name in TARGETS}
    if any(o is None or o.type!='MESH' for o in targets.values()): raise RuntimeError("Exact nine-mesh target allowlist not found")
    for n,o in targets.items():
        if not o.parent or o.parent.name!=TARGETS[n]: raise RuntimeError(f"Owner mismatch for {n}")
    PREMUTATION.write_text(json.dumps({"sourceSha256":EXPECTED['source'],"targets":target_contracts(targets),
        "unreferencedMaterialsRetainedOnSave":[{"name":n,"sourceUsers":bpy.data.materials[n].users,
          "sourceFakeUser":bpy.data.materials[n].use_fake_user,
          "signature":next(row for row in before['materials'] if row[0]==n)} for n in sorted(UNUSED_RETAINED_MATERIALS)],
        "note":"Exact native object identities, owners, transforms, material slots and inventory rows recorded before mesh mutation. Only the two confirmed zero-user material datablocks receive fake-user retention for Blender round-trip; their shader nodes, values, names and assignments are unchanged."},indent=2)+"\n")
    # First, reshape the four existing lateral construction plates into long fitted sweeps.
    brow=[(-.236,1.914,.022,.010),(-.274,1.944,.039,.013),(-.344,1.952,.052,.016),(-.414,1.917,.044,.014),(-.477,1.871,.024,.009),(-.500,1.850,.010,.006)]
    cheek=[(-.282,1.805,.010,.008),(-.291,1.783,.021,.010),(-.316,1.754,.026,.011),(-.365,1.731,.022,.010),(-.420,1.730,.018,.009),(-.465,1.754,.010,.007)]
    for side in (-1,1):
        v,f=swept_band(side,brow,lift=.033); replace_mesh(targets[f"Forged orbital brow {side}"],v,f,True)
        v,f=swept_band(side,cheek,lift=.037); replace_mesh(targets[f"Broad swept cheek band {side}"],v,f,True)
        # Cere is a short tapered bridge that overlaps, rather than a freestanding badge.
        cere=[(-.414,1.895,.020,.008),(-.448,1.878,.030,.009),(-.478,1.849,.025,.008),(-.500,1.822,.011,.006)]
        v,f=swept_band(side,cere,lift=.020); replace_mesh(targets[f"Cere root transition {side}"],v,f,True)
    v,f=bridge_mesh(targets['Overlapping nasal hood']); replace_mesh(targets['Overlapping nasal hood'],v,f,True)
    # Broadly join the root stations of the original blade meshes; blend to the exact distal geometry.
    for name in ("Profiled upper bill blade 0","Profiled upper bill blade 1"):
        obj=targets[name]; rows=57; cols=40
        if len(obj.data.vertices)!=rows*cols: raise RuntimeError(f"Unexpected bill blade topology: {name}")
        for j in range(rows):
            t=(.245*j/(rows-1)) if name.endswith('0') else (.25+.75*j/(rows-1))
            if t>=.34: continue
            weight=1.0 if t<=.22 else max(0.0,(.34-t)/.12)
            for k in range(cols):
                v=obj.data.vertices[j*cols+k]
                # Modest transverse flare with a shallow lower-root roll; outer apex remains fixed.
                v.co.x *= (1.0+.13*weight)
                v.co.z += (.005*weight)*(1.0 if v.co.z < 0 else -1.0)
    after=snapshot(); changed={n for n in before['objects'] if before['objects'][n]!=after['objects'][n]}
    assert changed==set(TARGETS), f"Out-of-allowlist mutation: {sorted(changed^set(TARGETS))}"
    assert before['materials']==after['materials'],"Material data changed during geometry mutation"
    for n in TARGETS:
        a,b=before['objects'][n],after['objects'][n]
        for key in ('type','parent','matrixBasis','matrixParentInverse','location','rotation','scale','rotationMode','hideRender','props','modifiers'):
            assert a[key]==b[key],f"Target metadata changed: {n}/{key}"
        assert a['data']['materials']==b['data']['materials'],f"Target materials changed: {n}"
    for n in before['objects'].keys()-set(TARGETS): assert before['objects'][n]==after['objects'][n],f"Unchanged object differs: {n}"
    unused={m.name for m in bpy.data.materials if m.users==0 and not m.use_fake_user}
    if unused!=UNUSED_RETAINED_MATERIALS:
        raise RuntimeError(f"Unexpected unreferenced material datablocks: {sorted(unused)}")
    for name in sorted(unused): bpy.data.materials[name].use_fake_user=True
    bpy.context.view_layer.update()
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(CANDIDATE),check_existing=False)
    saved=snapshot(); cand_sha=sha(CANDIDATE)
    bpy.ops.wm.open_mainfile(filepath=str(CANDIDATE)); reloaded=snapshot()
    assert saved==reloaded,"Saved candidate differs after reload"
    assert {n for n in before['objects'] if before['objects'][n]!=reloaded['objects'][n]}==set(TARGETS)
    return before,reloaded,cand_sha

def render(blend,phase):
    bpy.ops.wm.open_mainfile(filepath=str(blend)); scene=bpy.context.scene; scene.frame_set(1)
    scene.render.engine='BLENDER_WORKBENCH'; sh=scene.display.shading; sh.light='STUDIO'; sh.studio_light='paint.sl'; sh.color_type='MATERIAL'
    sh.show_shadows=True; sh.show_cavity=True; sh.cavity_type='BOTH'; sh.curvature_ridge_factor=1.2; sh.curvature_valley_factor=1.1
    sh.background_type='WORLD'; scene.world.color=(.11,.12,.13); scene.render.resolution_x=1100; scene.render.resolution_y=1100
    scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.render.film_transparent=False
    for o in scene.objects:
        if o.type=='MESH': o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
        o.hide_set(False)
    camdata=bpy.data.cameras.new('Head construction study camera'); cam=bpy.data.objects.new('Head construction study camera',camdata); scene.collection.objects.link(cam); scene.camera=cam
    rows=[]
    for spec in CAMERAS:
        cam.location=spec['position']; cam.rotation_euler=(Vector(spec['target'])-cam.location).to_track_quat('-Z','Y').to_euler()
        camdata.type='ORTHO'; camdata.ortho_scale=spec['ortho']; out=ATTEMPT_AUDIT_DIR/f"{phase}-{spec['name']}.png"; scene.render.filepath=str(out)
        bpy.ops.render.render(write_still=True); rows.append({"path":str(out.relative_to(ROOT)),"sha256":sha(out),"bytes":out.stat().st_size,"camera":{**spec,"projection":"ORTHO","resolution":[1100,1100]}})
    return rows

if os.environ.get("HEAD_STUDY_DIAG") == "1":
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE)); baseline=snapshot()
    bpy.ops.wm.open_mainfile(filepath=str(CANDIDATE)); candidate_snapshot=snapshot()
    diffs={}
    for name in sorted(set(baseline['objects'])|set(candidate_snapshot['objects'])):
        a=baseline['objects'].get(name); b=candidate_snapshot['objects'].get(name)
        if a!=b:
            fields=sorted(k for k in set(a or {})|set(b or {}) if (a or {}).get(k)!=(b or {}).get(k))
            diffs[name]=fields
    print(json.dumps({"changedObjects":sorted(diffs),"fieldDifferences":diffs,
                      "materialDifference":baseline['materials']!=candidate_snapshot['materials']}))
    raise SystemExit(0)

inventory=json.loads(INVENTORY.read_text()); inventory_by_name={item['name']:item for item in inventory['parts'] if item['name'] in TARGETS}
if set(inventory_by_name)!=set(TARGETS): raise RuntimeError("Inventory does not contain every exact allowlisted target")
before,candidate,candidate_sha=create_candidate()
before_views=render(SOURCE,'before'); after_views=render(CANDIDATE,'after')
if sha(SOURCE)!=EXPECTED['source'] or sha(CANDIDATE)!=candidate_sha: raise RuntimeError("Input/output changed during study")
shutil.copy2(Path(__file__).resolve(),SCRIPT_SNAPSHOT)
manifest={
 "title":"V7 native head-construction study V2",
 "status":"isolated editable native-only proposal; held for review; no GLB, runtime integration, or acceptance",
 "source":{"nativeBlend":{"path":str(SOURCE.relative_to(ROOT)),"sha256":EXPECTED['source']},
           "nativeInventory":{"path":str(INVENTORY.relative_to(ROOT)),"sha256":EXPECTED['inventory']},
           "headRecipe":{"path":str(HEAD_RECIPE.relative_to(ROOT)),"sha256":EXPECTED['headRecipe']},
           "julyReference":{"path":str(JULY.relative_to(ROOT)),"sha256":EXPECTED['july'],"scope":"head only"}},
 "attempt":ATTEMPT,
 "candidate":{"path":str(CANDIDATE.relative_to(ROOT)),"sha256":candidate_sha,"bytes":CANDIDATE.stat().st_size},
 "scriptSnapshot":{"path":str(SCRIPT_SNAPSHOT.relative_to(ROOT)),"sha256":sha(SCRIPT_SNAPSHOT)},
 "preMutationContracts":{"path":str(PREMUTATION.relative_to(ROOT)),"sha256":sha(PREMUTATION)},
 "changeAllowlist":sorted(TARGETS),"targetOwners":TARGETS,
 "roundTripRetentionException":{"materials":sorted(UNUSED_RETAINED_MATERIALS),"change":"fake-user flag only, to retain two source zero-user material datablocks across Blender save/reload","shaderNodesValuesAndAssignmentsPreserved":True},
 "verification":{"onlyAllowlistedMeshGeometryChanged":True,"allNonallowlistedNativeObjectsPreservedExactly":True,
                 "allObjectTransformsAndAssignmentsPreservedExactly":True,"allMaterialShaderSignaturesAndMeshAssignmentsPreservedExactly":True,
                 "candidateReloadedAndCompared":True,
                 "beforeAfterUseMatchedCameras":True,"distalBillBladeRowsAboveStudyRootT034Unchanged":True,
                 "jawOpticsCrownPivotsAndContactObjectDataUnchanged":True},
 "renders":{"before":before_views,"after":after_views},
 "limits":["The July illustration guides head construction only; it is not exact-dimensional evidence.",
           "These are neutral static authoring renders, not runtime, shader, or animation evidence.",
           "Jaw, optic and crown native data were preserved, but full authored-motion collision checks were not run on this proposal.",
           "Visual coherence, opening clearance and likeness remain review questions; a preservation hash is not artistic acceptance."]}
MANIFEST.write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps({"candidate":str(CANDIDATE),"sha256":candidate_sha,"changedObjects":sorted(TARGETS),"beforeViews":len(before_views),"afterViews":len(after_views)}))
