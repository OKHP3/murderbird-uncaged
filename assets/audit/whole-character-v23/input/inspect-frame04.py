"""Read-only, hash-pinned inventory of V22 Frame04 regional construction."""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[4]


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def artifact(path):
    path = Path(path)
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': digest(path), 'bytes': path.stat().st_size}


def read_args():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument('--native', required=True)
    parser.add_argument('--native-sha256', required=True)
    parser.add_argument('--frame-receipt', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args(argv)
    for name in ('native', 'frame_receipt', 'out'):
        path = Path(getattr(args, name))
        if path.is_absolute():
            raise RuntimeError(f'--{name.replace("_", "-")} must be repository-relative')
        resolved = (ROOT / path).resolve()
        if resolved != ROOT and ROOT not in resolved.parents:
            raise RuntimeError(f'--{name.replace("_", "-")} escapes repository')
        setattr(args, name, resolved)
    return args


def source_assignments(relpath, wanted):
    path = ROOT / relpath
    tree = ast.parse(path.read_text())
    result = {}
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name) and target.id in wanted:
                    try:
                        result[target.id] = ast.literal_eval(value)
                    except Exception:
                        result[target.id] = ast.unparse(value)
    return {'source': artifact(path), 'assignments': result}


def bounds_for(objects, depsgraph):
    points = []
    for obj in objects:
        evaluated = obj.evaluated_get(depsgraph)
        matrix = evaluated.matrix_world
        for corner in evaluated.bound_box:
            points.append(matrix @ Vector(corner))
    if not points:
        return None
    return {
        'minNativeXYZ': [min(p[i] for p in points) for i in range(3)],
        'maxNativeXYZ': [max(p[i] for p in points) for i in range(3)],
        'meshObjectCount': len(objects),
    }


def owner_name(obj):
    parent = obj.parent
    return parent.name if parent else None


def mesh_record(obj):
    keys = ('region', 'surfaceRole', 'exteriorEras', 'constructionClass', 'proposal', 'authoringRole')
    props = {key: obj[key] for key in keys if key in obj}
    return {'name': obj.name, 'owner': owner_name(obj), 'metadata': props}


def main():
    args = read_args()
    if not args.native.is_file() or digest(args.native) != args.native_sha256:
        raise RuntimeError('Frame04 native missing or SHA-256 mismatch')
    if not args.frame_receipt.is_file():
        raise RuntimeError('Frame04 receipt missing')
    if args.out.exists():
        raise RuntimeError('Refusing to overwrite: ' + str(args.out))
    receipt = json.loads(args.frame_receipt.read_text())
    if receipt.get('native', {}).get('sha256') != args.native_sha256:
        raise RuntimeError('Frame receipt does not bind the requested native')
    bpy.ops.wm.open_mainfile(filepath=str(args.native))
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    pivots = [o for o in bpy.data.objects if o.type == 'EMPTY']

    head_owners = {'head', 'jaw', 'upper-bill', 'builder-optics', 'processing', 'cranial-cover', 'bill-contact',
                   'head-head-bearing', 'head-head-plate'}
    neck_owners = {'neck', 'cervical-upper', 'cervical-joint-cover', 'cervical-root-cover', 'cervical-skull-cover'}
    mantle_owners = {'left-mantle', 'right-mantle', 'left-wing-shield', 'right-wing-shield'}
    mesh_objects = [o for o in bpy.data.objects if o.type == 'MESH']
    groups = {
        'head': [o for o in mesh_objects if owner_name(o) in head_owners],
        'neck': [o for o in mesh_objects if owner_name(o) in neck_owners],
        'breast': [o for o in mesh_objects if owner_name(o) == 'breastplate' or
                   (owner_name(o) == 'body' and (o.get('region') in ('breast', 'back') or
                    any(k in o.name.lower() for k in ('breast', 'stern', 'rib', 'throat', 'cervical', 'journal'))))],
        'mantle': [o for o in mesh_objects if owner_name(o) in mantle_owners],
    }
    groups_json = {}
    for name, objects in groups.items():
        groups_json[name] = {
            'bounds': bounds_for(objects, depsgraph),
            'owners': sorted({owner_name(o) for o in objects}),
            'objects': [mesh_record(o) for o in sorted(objects, key=lambda item: item.name)],
        }

    relevant_body = [o for o in mesh_objects if owner_name(o) == 'body' and
                     (o.get('region') in ('breast', 'back') or
                      any(k in o.name.lower() for k in ('breast', 'stern', 'rib', 'throat', 'cervical', 'journal', 'shoulder')))]
    pivots_json = {}
    for obj in sorted(pivots, key=lambda item: item.name):
        pivots_json[obj.name] = {
            'parent': obj.parent.name if obj.parent else None,
            'localPositionNativeXYZ': list(obj.matrix_local.translation),
            'worldPositionNativeXYZ': list(obj.matrix_world.translation),
        }

    sources = {
        'v21BreastCourses': source_assignments('assets/audit/whole-character-v21/attempt-construction06/executed-breast-courses.py', ('PROFILE', 'COURSE_COUNTS', 'COURSE_Z', 'ANGLE_LIMIT', 'MAX_RELIEF')),
        'v21JointClearance': source_assignments('assets/audit/whole-character-v21/attempt-construction06/executed-joint-clearance.py', ('AXIS', 'ERAS')),
        'v21Mantle': source_assignments('assets/audit/whole-character-v21/attempt-construction06/executed-mantle-refined.py', ('SHOULDER', 'SHIELD', 'COURSES', 'SHIELD_COURSES')),
        'v21EnvelopeReference': source_assignments('scripts/regions/whole-character-v21-envelope.py', ('PROFILE', 'PIVOTS')),
        'v19TorsoNeckReference': source_assignments('scripts/regions/whole-character-v19-torso-neck.py', ('TORso', 'PROFILE')),
    }
    source_owner_rules = {
        'v21BreastCourses': {
            'sourcePath': sources['v21BreastCourses']['source']['path'],
            'owner': 'breastplate',
            'rule': 'The executed course module resolves the breastplate EMPTY and parents the recessed backing and all directional courses to that owner.',
        },
        'v21JointClearance': {
            'sourcePath': sources['v21JointClearance']['source']['path'],
            'declaredNewOwners': {'cervical-joint-cover': 'neck', 'upper captive intermediate eyes and upper load bows': 'cervical-upper'},
            'rule': 'Existing throat/nape/flank guard objects retain their native owners; the executed module declares the intermediate cover parent as neck and creates its added upper bearing members on cervical-upper.',
        },
        'v21Mantle': {
            'sourcePath': sources['v21Mantle']['source']['path'],
            'owners': ['left-mantle', 'right-mantle', 'left-wing-shield', 'right-wing-shield'],
            'rule': 'Each course and backing is attached to one of these four retained shoulder/elbow owners; no surface bridges the articulated seam.',
        },
        'v19TorsoNeck': {
            'sourcePath': sources['v19TorsoNeckReference']['source']['path'],
            'owners': {'movingAccessDoor': 'breastplate', 'fixedRearAndLateralReturns': 'body'},
            'rule': 'The V19 access construction explicitly separates the moving breastplate door from body-owned fixed returns. V21 current parents are listed in regionGroups/bodyRelevantMeshes.',
        },
    }
    data = {
        'status': 'read-only native inventory; bounds are evaluated Blender object bounds, not collision or acceptance results',
        'native': artifact(args.native),
        'frameReceipt': artifact(args.frame_receipt),
        'inspectorScript': artifact(Path(__file__)),
        'baseNative': receipt.get('base'),
        'nativeCoordinateConvention': 'metres, Z-up, -Y forward; positions are native coordinates',
        'pivotCount': len(pivots),
        'namedPivots': pivots_json,
        'regionGroups': groups_json,
        'bodyRelevantMeshes': [mesh_record(o) for o in sorted(relevant_body, key=lambda item: item.name)],
        'sourceConstruction': sources,
        'sourceOwnerRules': source_owner_rules,
        'limits': [
            'Current Frame04 geometry is a V22 rest-proportion study based on V21 Construction06; no runtime or clearance judgment is made.',
            'Source profile points below are authoring inputs, not measurements recovered from the illustration and not a claim that all current vertices still lie on those profiles.',
            'The V19 torso profile is a predecessor recipe; V21 Construction06 breast courses use their own explicit PROFILE and the V21 shared-envelope/joint sources.',
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x') as stream:
        json.dump(data, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'out': artifact(args.out), 'pivotCount': len(pivots),
                      'regionalMeshCounts': {k: len(v) for k, v in groups.items()},
                      'bodyRelevantMeshCount': len(relevant_body)}, indent=2))


main()
