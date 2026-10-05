import bpy
import json
from pathlib import Path

out = Path(__file__).resolve().parent / 'native-runtime-receipt.json'
target = 'CGRF02 left forward toe 2 recessed joint shoulder 1'
obj = bpy.data.objects.get(target)
receipt = {
    'scope': 'Read-only loaded-source/runtime capability probe; no native normal evaluation, export or source save.',
    'runtime_version': bpy.app.version_string,
    'loaded_file_version': list(bpy.data.version),
    'source': 'assets/audit/cg-recursive-three-loop01/loop03/delivery/retained04/maker/murderbird-recursive-maker.blend',
    'mesh_object_count': sum(o.type == 'MESH' for o in bpy.data.objects),
    'worst_retained_object_found': obj is not None,
    'worst_retained_object_type': obj.type if obj else None,
    'fresh_normal_evaluation': 'NOT RUN',
    'source_saved': False,
}
out.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps(receipt))
