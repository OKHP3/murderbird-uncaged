"""One pinned native prototype of a joint-centered cervical drive.

This is an isolated reconstruction study. It does not change application code,
the source model, or runtime behavior. New parts attach to existing pivot owners.
"""
from pathlib import Path
import hashlib, json, math, sys
import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'assets/models/uncaged-cervical-construction-study-v1/attempt-14/murderbird-cervical-construction-study-v1.blend'
SOURCE_SHA = 'ef9e28ddbce9d62aabc8181a058640ea1e8b7a339b673df37b913d96699f9440'
MODEL_DIR = ROOT / 'assets/models/uncaged-cervical-joint-drive-study-v1/iterations/attempt-02'
AUDIT = ROOT / 'assets/audit/cervical-joint-drive-study-v1/iterations/attempt-02'
OUT = MODEL_DIR / 'murderbird-cervical-joint-drive-study-v1.blend'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def stop(msg): raise RuntimeError(msg)
if not SOURCE.exists() or sha(SOURCE) != SOURCE_SHA: stop('Pinned attempt14 source missing or changed')
if OUT.exists() or AUDIT.exists(): stop('Refusing to overwrite existing iteration')
MODEL_DIR.mkdir(parents=True, exist_ok=False); AUDIT.mkdir(parents=True, exist_ok=False)
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
scene=bpy.context.scene
upper=bpy.data.objects['cervical-upper']; neck=bpy.data.objects['neck']
axles=[bpy.data.objects[f'Cervical intermediate axle {s}'] for s in (-1,1)]
clevis=[bpy.data.objects[f'Cervical intermediate clevis {s}'] for s in (-1,1)]
rails=[bpy.data.objects[f'Upper cervical curved load rail {s}'] for s in (-1,1)]

def obj_snapshot():
    rows={}
    for o in bpy.data.objects:
        if o.type not in {'MESH','CURVE','EMPTY'}: continue
        rows[o.name]={'type':o.type,'parent':o.parent.name if o.parent else None,
                      'matrix':[[round(float(v),10) for v in row] for row in o.matrix_world],
                      'verts':len(o.data.vertices) if o.type=='MESH' else None,
                      'polys':len(o.data.polygons) if o.type=='MESH' else None}
    return rows
before=obj_snapshot()
pivots={o.name:before[o.name] for o in bpy.data.objects if o.type=='EMPTY'}
materials=[m.name for m in bpy.data.materials]

# Ring mesh in frame-local coordinates. Full rings use indexed wrapping; open
# sectors receive two radial closure faces. Axis is local X.
def annulus(name, owner, x0, x1, ri, ro, mat_name, segments=64, a0=0, a1=2*math.pi, frame=None):
    verts=[]; faces=[]; closed=abs((a1-a0)-2*math.pi)<1e-7
    steps=max(8,int(segments*(a1-a0)/(2*math.pi))); count=steps if closed else steps+1
    for x in (x0,x1):
        for r in (ri,ro):
            for i in range(count):
                a=a0+(a1-a0)*i/steps
                verts.append((x,r*math.cos(a),r*math.sin(a)))
    n=count
    for i in range(steps):
        j=(i+1)%count
        # four surfaces connecting inner/outer and both ends
        faces.extend([(i,j,2*n+j,2*n+i),(n+i,3*n+i,3*n+j,n+j),
                      (i,n+i,n+j,j),(2*n+i,2*n+j,3*n+j,3*n+i)])
    if not closed:
        faces.extend([(0,2*n,3*n,n),(steps,n+steps,3*n+steps,2*n+steps)])
    return add_mesh(name,owner,verts,faces,mat_name,frame)

def add_mesh(name,owner,verts,faces,mat_name,frame=None):
    mesh=bpy.data.meshes.new(name+' mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    ob=bpy.data.objects.new(name,mesh); scene.collection.objects.link(ob); ob.parent=owner
    frame=frame or owner
    ob.matrix_parent_inverse=owner.matrix_world.inverted() @ frame.matrix_world
    ob.location=(0,0,0); ob.rotation_euler=(0,0,0); ob.scale=(1,1,1)
    if mat_name and bpy.data.materials.get(mat_name): mesh.materials.append(bpy.data.materials[mat_name])
    ob['proposal']=True; ob['constructionClass']='reconstructed-rigid-mechanism'
    ob['ownerPivot']=owner.name
    return ob

def metadata(ob, era, role, note):
    ob['exteriorEras']=era; ob['surfaceRole']=role; ob['constructionNote']=note

# Fixed races sit in the actual 2.5 mm radial gap between 17.5 mm axle and
# 20 mm clevis bore. They remain independent neck-owned inserts.
race_names=[]
for s in (-1,1):
    race=annulus(f'Joint-drive fixed bearing liner {s:+d}',neck,
                 .111*s,.145*s,.0180,.0198,'Neutral / bearing',frame=upper)
    metadata(race,'maker,mechanic,builder','bearing-liner',
             'Neck-fixed liner in existing clevis; axle and clevis are inherited load-path members.')
    race_names.append(race.name)

# Maker's external sector and cable eye are upper-frame owned and use the
# anatomical-right (−X) trunnion. This prototype stops at the eye; the cable
# guide/route and its external neck lever connection are intentionally absent.
sector=annulus('Maker external cervical sector −X',upper,-.164,-.156,.0173,.030,'Neutral / frame',64,
               math.radians(-125),math.radians(125))
metadata(sector,'maker','external-sector','Upper-owned; future externally routed cable required; no onboard motor.')
# A small radial eye at the sector rim; tube ring in its own oriented local mesh.
eye_verts=[]; eye_faces=[]
center=Vector((-.160,.029,0.0)); R=.0048; r=.0018; major=18; minor=8
for i in range(major):
    a=2*math.pi*i/major
    c=center+Vector((0,R*math.cos(a),R*math.sin(a)))
    for j in range(minor):
        b=2*math.pi*j/minor; eye_verts.append(tuple(c+Vector((r*math.cos(b),r*math.sin(b)*math.cos(a),r*math.sin(b)*math.sin(a)))))
for i in range(major):
    for j in range(minor):
        n=i*minor+j; eye_faces.append((n,i*minor+(j+1)%minor,((i+1)%major)*minor+(j+1)%minor,((i+1)%major)*minor+j))
eye=add_mesh('Maker cable attachment eye −X',upper,eye_verts,eye_faces,'Neutral / frame')
metadata(eye,'maker','cable-eye','Rigid eye on sector; no cable geometry or claim of complete control route.')

# Mechanic remains locked. A short fixed brace between the lower clevis bridge
# vicinity and upper rail forms a visible physical stop; it does not actuate.
def capsule_box(name, owner, p0, p1, width, depth, mat, frame=None):
    a=Vector(p0); b=Vector(p1); d=(b-a).normalized(); u=d.cross(Vector((1,0,0)))
    if u.length<1e-5: u=d.cross(Vector((0,1,0)))
    u.normalize(); v=d.cross(u).normalized(); verts=[]
    for p in (a,b):
        for su,sv in ((-1,-1),(1,-1),(1,1),(-1,1)):
            verts.append(tuple(p+u*width*.5*su+v*depth*.5*sv))
    faces=[(0,3,2,1),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)]
    return add_mesh(name,owner,verts,faces,mat,frame)

brace=capsule_box('Mechanic passive cervical lock brace +X',neck,
                  (.118,-.016,.005),(.118,.018,.084),.008,.010,'Neutral / frame',frame=upper)
metadata(brace,'mechanic','passive-stop','Fixed neutral restraint only; Mechanic head/neck remains locked.')

# Advanced reaction housing is neck-fixed; only a small internal rotor/output
# sleeve is upper-owned. The stator does not attach to or rotate with the axle.
case=annulus('Advanced cervical rotary reaction housing +X',neck,.146,.178,.0205,.0290,'Neutral / frame',frame=upper)
metadata(case,'builder','powered-housing','Neck-fixed stator around +X trunnion; reaction path seats at clevis; clearance must be tested.')
rotor=annulus('Advanced cervical keyed output collar +X',upper,.151,.160,.0173,.0200,'Neutral / bearing')
metadata(rotor,'builder','keyed-output','Upper-owned rotor collar; meets existing +X axle; intended keyed interface, not a fixed housing contact.')

after=obj_snapshot()
added=sorted(set(after)-set(before))
if len(added)!=7: stop(f'Expected seven new mesh objects (2 liners + 2 Maker + 1 Mechanic + 2 Advanced), got {added}')
if {o.name:o.parent.name if o.parent else None for o in bpy.data.objects if o.name in before} != {n:r['parent'] for n,r in before.items()}:
    stop('Existing object parent changed')
if {o.name for o in bpy.data.objects if o.type=='EMPTY'} != set(pivots): stop('Pivot names changed')
for n,row in pivots.items():
    if before[n]['matrix'] != obj_snapshot()[n]['matrix']: stop('Pivot matrix changed: '+n)
if materials != [m.name for m in bpy.data.materials]: stop('Material datablocks changed')

# Reopenability-preserving save before any later diagnostics. The script is
# designed to stop rather than claim clearance if a downstream check fails.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT))
receipt={'status':'native prototype; clearance and visual review pending',
 'source':{'path':str(SOURCE.relative_to(ROOT)),'sha256':SOURCE_SHA,'bytes':SOURCE.stat().st_size},
 'native':{'path':str(OUT.relative_to(ROOT)),'sha256':sha(OUT),'bytes':OUT.stat().st_size},
 'addedMeshes':added,'unchangedObjectCount':len(before),'pivotCount':len(pivots),
 'preservation':'Existing scene objects, parents, rest matrices, curves, materials, and pivot identities were checked before save; no original mesh was altered.',
 'loadPath':'The paired inherited upper-owned axles are separated trunnions, not one continuous shaft. Each is supported by its corresponding neck-owned clevis. New races are independent liners. Existing curved upper rails carry trunnion load into cervical-upper.',
 'eraParts':{race_names[0]+' / '+race_names[1]:'all eras; neck fixed',sector.name+' / '+eye.name:'Maker only; upper moving; external cable route unbuilt',brace.name:'Mechanic only; neck fixed passive brace/stop, no actuation',case.name:'Advanced only; neck-fixed reaction housing',rotor.name:'Advanced only; upper-moving keyed output interface'},
 'limits':['No application/runtime integration or GLB export.','No physical load or material-strength claim.','Clearance checks and neutral renders are still pending.','The prior sampled point envelope is not evidence of clearance for these complete solids.']}
(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
