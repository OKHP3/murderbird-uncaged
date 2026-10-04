"""Regional PBR routing with explicit per-slot families for new construction.

Historical surface generation remains unchanged. New authors may store a JSON
array in cgSurfaceFamilies, preserving dark thickness and separate metal edges.
"""
import importlib.util
import json
from pathlib import Path


def apply(scene, output_dir, era='builder', reference_root=None):
    root = Path(reference_root or Path(__file__).resolve().parents[1])
    path = root / 'scripts/cinematic-cg-2b-surface.py'
    spec = importlib.util.spec_from_file_location('supervised_surface03_base', path)
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    legacy_classify = base.classify
    routing = []

    def classify(obj, slot_material=None):
        default = legacy_classify(obj, slot_material)
        families = obj.get('cgSurfaceFamilies')
        if not families:
            return default
        if isinstance(families, str):
            families = json.loads(families)
        if len(families) != len(obj.data.materials):
            raise ValueError(f'{obj.name}: slot family count differs from slots')
        index = next((i for i, mat in enumerate(obj.data.materials)
                      if mat == slot_material), None)
        if index is None:
            raise ValueError(f'{obj.name}: cannot resolve material slot')
        family = families[index]
        if family in ('protected-optic', 'protected-glass') or (
                slot_material and slot_material.get('cg2aPreserveMaterial')):
            return None
        if family not in base.FAMILIES:
            raise ValueError(f'{obj.name}: unknown surface family {family!r}')
        routing.append({'object': obj.name, 'slot': index, 'family': family})
        return family

    base.classify = classify
    receipt = base.apply(scene, output_dir, era, root)
    for route in routing:
        obj = scene.objects[route['object']]
        actual = obj.data.materials[route['slot']].get('cg2bFamily')
        if actual != route['family']:
            raise RuntimeError(f'Explicit slot routing failed: {route}, actual={actual}')
    texture_root = Path(output_dir) / 'textures'
    receipt['texturePaths'] = {
        name: str((texture_root / name).relative_to(root))
        for name in receipt['textureHashes']
    }
    receipt['explicitSlotRouting'] = routing
    receipt['eraDisplayName'] = {'maker': 'Maker', 'mechanic': 'Mechanic',
                               'builder': 'Advanced'}[era]
    receipt['adapter'] = 'scripts/cg-supervised-surface03.py'
    (texture_root / 'surface-provenance.json').write_text(
        json.dumps(receipt, indent=2) + '\n')
    return receipt
