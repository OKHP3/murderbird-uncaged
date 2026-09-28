"""Read-only hierarchy and evaluated bounds inventory for frozen V15 attempt 04."""
from pathlib import Path
import datetime, hashlib, json
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'assets/models/whole-character-v15/attempt-04/murderbird-whole-character-v15.blend'
EXPECTED_SOURCE = 'dd4e6a78396a384be6d38b00c23a3c43c47ab0a9371e6546ad4896b1c6a93cfe'
OUTPUT = ROOT / 'assets/audit/whole-silhouette-v16/base-topology.json'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def vector(v):
    return [round(float(x), 9) for x in v]


def matrix(m):
    return [[round(float(m[r][c]), 9) for c in range(4)] for r in range(4)]


def hierarchy(obj):
    chain=[]; cur=obj
    while cur is not None:
        chain.append(cur.name); cur=cur.parent
    return list(reversed(chain))


def owner(obj):
    cur=obj.parent
    while cur is not None:
        if cur.type=='EMPTY': return cur
        cur=cur.parent
    return None


def category(name):
    n=name.lower().replace('_','-')
    if any(k in n for k in ('cranial','upper-bill','lower-bill','jaw','optic','head','mandible','crown','eye')): return 'head'
    if any(k in n for k in ('neck','cervical','throat')): return 'neck'
    if any(k in n for k in ('shoulder','mantle','wing','shield','elbow')): return 'shoulders-shields'
    if any(k in n for k in ('leg','thigh','shin','knee','metatars','digit','toe','foot','tars')): return 'legs-feet-digits'
    if any(k in n for k in ('body','torso','breast','stern','pelvis','hip','tail','spine','keel')): return 'body-breast-pelvis'
    return 'unclassified'


assert Path(bpy.data.filepath).resolve()==SOURCE.resolve(), 'Wrong native opened'
assert sha(SOURCE)==EXPECTED_SOURCE, 'Frozen source hash changed'
if OUTPUT.exists():
    prior=json.loads(OUTPUT.read_text())
    assert prior.get('native',{}).get('sha256')==EXPECTED_SOURCE, 'Existing inventory has a different source identity'
scene=bpy.context.scene; scene.frame_set(1); bpy.context.view_layer.update()
depsgraph=bpy.context.evaluated_depsgraph_get()

empties=[]
for o in sorted((o for o in bpy.data.objects if o.type=='EMPTY'),key=lambda o:o.name):
    empties.append({'name':o.name,'parent':o.parent.name if o.parent else None,
        'hierarchy':hierarchy(o),'localPosition':vector(o.location),'worldPosition':vector(o.matrix_world.translation),
        'localMatrix':matrix(o.matrix_local),'worldMatrix':matrix(o.matrix_world)})

objects=[]
for o in sorted((o for o in bpy.data.objects if o.type in {'MESH','CURVE','SURFACE','FONT'}),key=lambda o:o.name):
    e=o.evaluated_get(depsgraph); mesh=None; points=[]; polygon_count=None
    if e.type=='MESH':
        mesh=e.to_mesh()
        try:
            points=[e.matrix_world @ v.co for v in mesh.vertices]
            polygon_count=len(mesh.polygons)
        finally: e.to_mesh_clear()
    else:
        points=[e.matrix_world @ Vector(corner) for corner in e.bound_box]
    bounds=None
    if points:
        bounds=[[round(min(p[i] for p in points),9),round(max(p[i] for p in points),9)] for i in range(3)]
    own=owner(o)
    objects.append({'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,
        'owner':own.name if own else None,'ownerParent':own.parent.name if own and own.parent else None,
        'hierarchy':hierarchy(o),'categoryFromOwner':category(own.name if own else ''),
        'worldBoundsXYZ':bounds,'evaluatedVertexCount':len(points) if o.type=='MESH' else None,
        'polygonCount':polygon_count,
        'curvePointBoundsSource':'evaluated object bound_box corners' if o.type!='MESH' else None})

def aggregate_bounds(rows):
    pts=[o['worldBoundsXYZ'] for o in rows if o['worldBoundsXYZ']]
    return None if not pts else [[round(min(b[i][0] for b in pts),9),round(max(b[i][1] for b in pts),9)] for i in range(3)]

groups={}
for label in ('head','neck','body-breast-pelvis','shoulders-shields','legs-feet-digits','unclassified'):
    rows=[o for o in objects if o['categoryFromOwner']==label]
    meshes=[o for o in rows if o['type']=='MESH']
    curves=[o for o in rows if o['type']!='MESH']
    owners=sorted({o['owner'] for o in rows if o['owner']})
    groups[label]={'objectCount':len(rows),'meshCount':len(meshes),'historicalGuideCurveCount':len(curves),
        'worldBoundsXYZ':aggregate_bounds(meshes),'meshWorldBoundsXYZ':aggregate_bounds(meshes),
        'historicalGuideCurveBoundsXYZ':aggregate_bounds(curves),'ownerNames':owners,
        'ownerPivots':[{'name':n,'parent':next((p['parent'] for p in empties if p['name']==n),None),
            'localPosition':next((p['localPosition'] for p in empties if p['name']==n),None),
            'worldPosition':next((p['worldPosition'] for p in empties if p['name']==n),None)} for n in owners],
        'meshObjects':[o['name'] for o in meshes],
        'historicalGuideCurves':[o['name'] for o in curves]}

# Name-based region and ownership crossings are surfaced explicitly for review.
regionOwnerCrossings=[]
for o in objects:
    owner_group=category(o['owner'] or '')
    name_group=category(o['name'])
    if owner_group!='unclassified' and name_group!='unclassified' and owner_group!=name_group:
        regionOwnerCrossings.append({'object':o['name'],'owner':o['owner'],
            'ownerCategory':owner_group,'nameCategory':name_group,'worldBoundsXYZ':o['worldBoundsXYZ']})

result={'schema':'whole-silhouette-v16/base-topology/v1','status':'read-only native topology and evaluated bounds inventory; not a model-change or fit claim',
    'generatedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'native':{'path':SOURCE.relative_to(ROOT).as_posix(),'sha256':sha(SOURCE),'bytes':SOURCE.stat().st_size},
    'reader':{'path':Path(__file__).resolve().relative_to(ROOT).as_posix(),'sha256':sha(__file__)},
    'blenderVersion':bpy.app.version_string,'sceneCounts':{'empties':len(empties),'objects':len(objects),
        'meshes':sum(o['type']=='MESH' for o in objects),'curvesOther':sum(o['type']!='MESH' for o in objects)},
    'boundsConvention':'Native Blender XYZ world coordinates; mesh bounds use evaluated mesh vertices including modifiers. Curves use evaluated bound_box corners and are listed separately as historical guide/assembly curves; they are excluded from anatomical mesh envelopes.',
    'groups':groups,'rigidNodes':empties,'objects':objects,'nameOwnerCategoryCrossings':regionOwnerCrossings,
    'limits':['Name categories are descriptive grouping hints, not anatomical or build authority.','Bounds overlap by itself does not establish contact or collision.','Historical guide curves are not active anatomy and should not drive whole-character proportion transforms.','No visual framing, articulation, collision, or owner acceptance was tested.']}
OUTPUT.parent.mkdir(parents=True,exist_ok=True)
OUTPUT.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'nativeSha256':sha(SOURCE),'output':str(OUTPUT.relative_to(ROOT)),
    'sceneCounts':result['sceneCounts'],'groups':{k:{'meshCount':v['meshCount'],'bounds':v['meshWorldBoundsXYZ'],'owners':v['ownerPivots']} for k,v in groups.items()},
    'crossingCount':len(regionOwnerCrossings)},indent=2))
