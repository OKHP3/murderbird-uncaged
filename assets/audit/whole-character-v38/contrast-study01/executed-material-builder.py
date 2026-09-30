#!/usr/bin/env python3
"""Write-once regional contrast fork of the V37 material-study pipeline.

Run through Blender with --native-source, --glb-source, --output-directory.
The three named armor regions receive proposed PBR factors. Geometry and all
eligibility tags remain receipt-bound. No textures or geometry are introduced.
"""
import importlib.util
import json
import struct
from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[1]
recipe = ROOT / 'scripts/build-v37-mechanical-finish.py'
spec = importlib.util.spec_from_file_location('finish_recipe', recipe)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
STUDY = 'v38-regional-contrast-study01'

def profile(rgb, metal, rough):
    return {'baseColorFactor': [*rgb, 1.0], 'metallicFactor': metal, 'roughnessFactor': rough}

# Keep the established finish elsewhere; separate these actual rigid armor
# courses by region. These values are proposed albedo/response, not sampled
# photographic highlights or measured alloys.
REGIONAL = {
    'crown-plate': {
        'maker': profile((.135, .078, .037), .74, .49),
        'mechanic': profile((.050, .090, .070), .69, .49),
        'builder': profile((.050, .090, .070), .69, .49),
    },
    'breast-plate': {
        'maker': profile((.145, .085, .041), .72, .52),
        'mechanic': profile((.055, .102, .079), .67, .55),
        'builder': profile((.055, .102, .079), .67, .55),
    },
    'shoulder-plate': {
        'maker': profile((.125, .073, .034), .73, .54),
        'mechanic': profile((.043, .083, .066), .70, .57),
        'builder': profile((.043, .083, .066), .70, .57),
    },
}
original_role = base.mapped_role
def regional_role(source, name, region):
    role = original_role(source, name, region)
    if role != 'plate':
        return role
    if region == 'breast':
        return 'breast-plate'
    if region == 'shoulder':
        return 'shoulder-plate'
    if region == 'head' and any(t in name.lower() for t in ('swept cranial leaf', 'cranial cap', 'crown')):
        return 'crown-plate'
    return role
base.mapped_role = regional_role
base.mat_name = lambda role: 'V38 contrast / ' + role
base.FINISHES.update(REGIONAL)

def main():
    args = base.args_after_double_dash()
    native_source, glb_source = args.native_source.resolve(), args.glb_source.resolve()
    out = args.output_directory.resolve()
    audit = ROOT / 'assets/audit/whole-character-v38' / out.name
    native = out / 'murderbird-v38-material-contrast-study01.blend'
    glb = out / 'murderbird-v38-material-contrast-study01.glb'
    receipt = audit / 'receipt.json'
    if any(p.exists() for p in (native, glb, receipt)):
        raise FileExistsError('Preserve this study and choose a new versioned directory')
    if not native_source.is_file() or not glb_source.is_file():
        raise FileNotFoundError('Both actual source binaries are required')
    _, _, source_doc = base.glb_read(glb_source)
    bpy.ops.wm.open_mainfile(filepath=str(native_source))
    before = base.native_snapshot()
    assignments, rows = base.set_material_profiles()
    after = base.native_snapshot()
    if before != after:
        raise ValueError('Object/geometry/transform/eligibility snapshot changed')
    out.mkdir(parents=True, exist_ok=True)
    audit.mkdir(parents=True, exist_ok=True)
    profiles = {}
    for material in bpy.data.materials:
        if material.name.startswith('V38 contrast / '):
            material['finishStudy'] = STUDY
            profiles[material.name] = json.loads(material['eraFinishes'])
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(native), check_existing=False)
    exported = base.patch_glb(glb_source, glb, assignments)
    _, chunks, doc = base.glb_read(glb)
    for material in doc['materials'][len(source_doc['materials']):]:
        material['extras']['finishStudy'] = STUDY
    payload = json.dumps(doc, separators=(',', ':')).encode()
    payload += b' ' * ((-len(payload)) % 4)
    binary = bytearray(base.GLB_HEADER.pack(b'glTF', 2, 0))
    for kind, data in chunks:
        data = payload if kind == base.JSON_CHUNK else data
        binary.extend(base.CHUNK_HEADER.pack(len(data), kind)); binary.extend(data)
    struct.pack_into('<I', binary, 8, len(binary))
    glb.write_bytes(binary)
    exported['outputSha256'] = base.sha(binary)
    exported['outputBytes'] = len(binary)
    bpy.ops.wm.open_mainfile(filepath=str(native))
    if base.native_snapshot() != before:
        raise ValueError('Native save/reopen preservation failed')
    receipt.write_text(json.dumps({
        'status': 'one regional readability proposal; owner acceptance pending',
        'inputs': {str(p): base.sha(p.read_bytes()) for p in (native_source, glb_source)},
        'native': {'path': str(native.relative_to(ROOT)), 'bytes': native.stat().st_size, 'sha256': base.sha(native.read_bytes())},
        'glb': {'path': str(glb.relative_to(ROOT)), **exported},
        'preservation': {'nativeSnapshotsExact': True, 'binByteIdentical': True, 'nodesMeshReferencesAccessorsAndEligibilityExact': True},
        'regionalProfiles': REGIONAL, 'allMaterialProfiles': profiles,
        'regionalMap': [{'eras': key[0], 'region': key[1], 'surfaceRole': key[2], 'materialRole': key[3], 'sourceMaterial': key[4], 'slots': count} for key, count in rows.items()],
        'scriptSha256': base.sha(Path(__file__).read_bytes()),
        'limits': ['Geometry remains V37; no silhouette correction in this fork.', 'No textures, relief, wear or matching candidate fallback yet.', 'Regional values are proposed interpretations, not photographic measurements.', 'No runtime, motion, performance, deployment or artistic acceptance established by this receipt.'],
    }, indent=2) + '\n')
    print(json.dumps({'native': str(native), 'glb': str(glb), 'sha256': exported['outputSha256'], 'meshCount': exported['outputMeshCount']}))

if __name__ == '__main__':
    main()
