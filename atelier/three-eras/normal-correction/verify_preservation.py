"""Face-wise, representation-independent comparison of the two runtime assets."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from repair_normals import Document

before, after, result = map(Path,sys.argv[sys.argv.index('--')+1:])
old, new = Document(before), Document(after)
metadata = set(old.data) - {'buffers','bufferViews','accessors'}
assert set(new.data) == set(old.data)
for field in metadata:
    assert old.data[field] == new.data[field], field

changed = set()
stats = {'primitives':0,'triangles':0,'compared_non_normal_corner_attributes':0}
for mesh in old.data['meshes']:
    for primitive in mesh['primitives']:
        stats['primitives'] += 1
        ia = primitive['indices']
        old_ids, new_ids = (d.array(ia).ravel() for d in (old,new))
        assert len(old_ids) == len(new_ids)
        stats['triangles'] += len(old_ids)//3
        changed.add(ia)
        for semantic, i in primitive['attributes'].items():
            changed.add(i)
            if semantic == 'NORMAL':
                continue
            old_attr = old.array(i)[old_ids]
            new_attr = new.array(i)[new_ids]
            assert old_attr.dtype == new_attr.dtype and np.array_equal(old_attr,new_attr), semantic
            stats['compared_non_normal_corner_attributes'] += len(old_attr)
independent = set(range(len(old.data['accessors']))) - changed
for i in independent:
    assert old.data['accessors'][i] == new.data['accessors'][i]
    assert old.array(i).tobytes() == new.array(i).tobytes()
for img in old.data['images']:
    i = img['bufferView']
    assert bytes(old.views[i]) == bytes(new.views[i])

stats.update(unchanged_animation_accessor_count=len(independent), images_identical=len(old.data['images']),
             materials_identical=len(old.data['materials']),nodes_identical=len(old.data['nodes']),
             unchanged_complete_glTF_fields=sorted(metadata),
             before_sha256=hashlib.sha256(before.read_bytes()).hexdigest(),
             after_sha256=hashlib.sha256(after.read_bytes()).hexdigest())
result.write_text(json.dumps(stats,indent=2)+'\n')
print(stats)
