from pathlib import Path
import bpy, hashlib, json
ROOT = Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
BASE = ROOT / 'assets/models/whole-character-v35/attempt-form01/murderbird-whole-character-v35.blend'
CAND = ROOT / 'assets/models/whole-character-v36/regional-studies/compact-feet/attempt02/murderbird-whole-character-v36-compact-feet.blend'
AUDIT = ROOT / 'assets/audit/whole-character-v36/regional-studies/compact-feet/attempt02'
RECEIPT = AUDIT / 'receipt.json'
REPORT = AUDIT / 'preservation-check.json'
EXPECTED_BASE = 'd2c704ccf89f3f0e7dbeb3613dcdbdd964c4ba69991783783830803eecf59cb0'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(BASE) == EXPECTED_BASE
prior_receipt = json.loads(RECEIPT.read_text())
changed_names = {entry['name'] for entry in prior_receipt['result']['changedFootMeshes']}
changed_nodes = set(prior_receipt['result']['changedNodes'])

def props(obj):
    return tuple(sorted((key, repr(obj[key])) for key in obj.keys()))

def matrix(m):
    return tuple(round(float(m[r][c]), 10) for r in range(4) for c in range(4))

def capture(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    bpy.context.view_layer.update()
    snapshots = {}
    contact = {'left': float('inf'), 'right': float('inf')}
    for obj in bpy.data.objects:
        item = {'type': obj.type, 'parent': obj.parent.name if obj.parent else None,
                'world': matrix(obj.matrix_world), 'local': matrix(obj.matrix_local),
                'props': props(obj)}
        if obj.type == 'MESH':
            item['geometry'] = (tuple(tuple(round(float(c), 10) for c in v.co) for v in obj.data.vertices),
                                tuple(tuple(int(i) for i in p.vertices) for p in obj.data.polygons),
                                tuple(int(p.material_index) for p in obj.data.polygons),
                                tuple(m.name if m else None for m in obj.data.materials))
            if obj.parent and obj.parent.name in {'left-foot','left-toes'} or obj.parent and obj.parent.name.startswith('left-digit-'):
                contact['left'] = min(contact['left'], min((obj.matrix_world @ v.co).z for v in obj.data.vertices))
            if obj.parent and obj.parent.name in {'right-foot','right-toes'} or obj.parent and obj.parent.name.startswith('right-digit-'):
                contact['right'] = min(contact['right'], min((obj.matrix_world @ v.co).z for v in obj.data.vertices))
        snapshots[obj.name] = item
    layout = bpy.data.objects['body'].get('mechanismLayoutV1')
    return snapshots, layout, contact

base, base_layout, base_contact = capture(BASE)
candidate, candidate_layout, candidate_contact = capture(CAND)
assert set(base) == set(candidate), (set(base) - set(candidate), set(candidate) - set(base))
actual_changed = {name for name in base if base[name] != candidate[name]}
expected_changed = changed_names | changed_nodes
assert actual_changed == expected_changed, {'unexpected': sorted(actual_changed - expected_changed), 'missing': sorted(expected_changed - actual_changed)}
assert base_layout == candidate_layout
layout = json.loads(candidate_layout)
assert layout['makerControlOffsets']['leg'] == [0.065, 0.015, 0.045]
ankles = ['left-foot', 'right-foot']
toe_roots = ['left-toes', 'right-toes']
proximal = [f'{side}-digit-{d}-proximal' for side in ('left','right') for d in range(1,4)]
assert all(base[n] == candidate[n] for n in ankles + toe_roots + proximal)
for n in changed_nodes:
    before, after = base[n], candidate[n]
    assert before['type'] == after['type'] == 'EMPTY'
    assert before['parent'] == after['parent']
    assert before['props'] == after['props']
    # The only rig change is a Y translation; rotation, scale, and axes stay fixed.
    before_m, after_m = before['local'], after['local']
    changed_indices = [i for i, (a,b) in enumerate(zip(before_m, after_m)) if a != b]
    assert changed_indices == [7], (n, changed_indices)

bearing_names = [name for name,item in base.items() if item['type']=='MESH'
                 and item['parent'] and ('left-digit-' in item['parent'] or 'right-digit-' in item['parent'])
                 and item['props'] and dict(item['props']).get('surfaceRole', "'") == "'bearing'"]
assert len(bearing_names) == 24, len(bearing_names)
assert all(base[n]['geometry'] == candidate[n]['geometry'] for n in bearing_names)
receivers = [
    'V21 left foot bearing receiver yoke', 'V21 right foot bearing receiver yoke',
    'left articulated bearing core.002', 'right articulated bearing core.002',
    'left open stepped bearing race -1.002', 'left open stepped bearing race 1.002',
    'right open stepped bearing race -1.002', 'right open stepped bearing race 1.002',
]
assert all(base[n] == candidate[n] for n in receivers)
assert all(abs(base_contact[s]-candidate_contact[s]) < 1e-7 for s in ('left','right'))

# Correct the two `beforeWorldBounds` entries in the transformation details
# from the frozen base/candidate files; no geometry or source is modified here.
for entry in prior_receipt['result']['talonReprofiles']:
    name = entry['name']
    def bounds(item):
        # Mesh local vertices plus its world matrix, reconstructed while each
        # file is open. Calculate directly from captured world bounds below.
        return None
# Small, detached snapshot pass for accurate talon bounds in both source and candidate.
def world_bounds(path, names):
    bpy.ops.wm.open_mainfile(filepath=str(path)); bpy.context.view_layer.update()
    result={}
    for name in names:
        obj=bpy.data.objects[name]; pts=[obj.matrix_world@v.co for v in obj.data.vertices]
        result[name]=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
    return result
forward_talons=[e['name'] for e in prior_receipt['result']['talonReprofiles']]
base_bounds=world_bounds(BASE,forward_talons)
candidate_bounds=world_bounds(CAND,forward_talons)
for entry in prior_receipt['result']['talonReprofiles']:
    entry['beforeWorldBounds']=base_bounds[entry['name']]
    entry['afterWorldBounds']=candidate_bounds[entry['name']]
prior_receipt['result']['talonReprofilesBoundsSource']='Corrected from detached V35 and attempt02 native world-vertex snapshots by executed-preservation-check.py.'
RECEIPT.write_text(json.dumps(prior_receipt,indent=2)+'\n')
report={
 'status':'passed bounded source-to-candidate preservation and leg attachment checks',
 'sourceNative':{'path':str(BASE.relative_to(ROOT)),'sha256':sha(BASE)},
 'regionalNative':{'path':str(CAND.relative_to(ROOT)),'sha256':sha(CAND),'bytes':CAND.stat().st_size},
 'objects':{'source':len(base),'candidate':len(candidate),'added':[],'removed':[],'actualChangedExactlyDeclared':True,
            'changedNodes':sorted(changed_nodes),'changedFootMeshes':len(changed_names),'actualChangedObjects':len(actual_changed)},
 'rig':{'ankleNodesUnchanged':True,'toeRootNodesUnchanged':True,'proximalNodesUnchanged':True,
        'distalNodesChanged':sorted(changed_nodes),'onlyLocalTranslationYChanged':True},
 'makerAttachment':{'mechanismLayoutV1Exact':True,'legLocalPoint':[0.065,0.015,0.045],
                    'ankleReceivingMeshesExact':receivers,'surfacePlacementChanged':False,
                    'scope':'The local Maker attachment contract and ankle bearing/core/yoke surfaces are byte-equivalent in mesh data and world placement. This proves preservation of the existing receiver, not runtime seating/force.'},
 'bearings':{'digitBearingMeshCount':len(bearing_names),'allLocalGeometryAndMaterialsExact':True,
             'distalBearingWorldPlacementFollowsMovedAxis':True},
 'restFootRegionLowestZBeforeAfterM':{side:[base_contact[side],candidate_contact[side]] for side in ('left','right')},
 'digitEndpointChecks':prior_receipt['result']['digitEndpointChecks'],
 'limits':['Endpoint values are projected Y-bounds overlap, not a full 3D surface-seat/collision test.',
           'No pose sweep, continuous clearance, balance, force, or engineering validation was run.',
           'The preserved rest geometry minimum is below the nominal zero plane; no physical floor-contact claim is made.']
}
REPORT.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'actualChangedObjects':len(actual_changed),'declaredChangedNodes':len(changed_nodes),'declaredChangedFootMeshes':len(changed_names),'digitBearingsExact':len(bearing_names),'makerLayoutExact':base_layout==candidate_layout,'floorMinBeforeAfter':report['restFootRegionLowestZBeforeAfterM']},indent=2))
