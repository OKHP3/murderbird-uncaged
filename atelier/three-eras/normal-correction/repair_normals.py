"""Create an additive, geometry-preserving strict-normal derivative of the frozen GLB.

Run in Blender with the original native scene, the original GLB and a new output
path. Input hashes are pinned; the output path must not be the frozen model.
"""
import hashlib
import json
from pathlib import Path
import struct
import sys

import bpy
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_normals as check

TYPES = {5121:'u1', 5123:'<u2', 5125:'<u4', 5126:'<f4'}
WIDTH = {'SCALAR':1, 'VEC2':2, 'VEC3':3, 'VEC4':4}


class Document:
    """This model uses one tightly packed, non-interleaved array per accessor."""
    def __init__(self,path):
        buf = path.read_bytes()
        n = struct.unpack_from('<I',buf,12)[0]
        self.data = json.loads(buf[20:20+n])
        blob = memoryview(buf)[28+n:]
        self.views = []
        for view in self.data['bufferViews']:
            assert view['buffer'] == 0 and 'byteStride' not in view
            off = view.get('byteOffset',0)
            self.views.append(blob[off:off+view['byteLength']])
        indices = [a['bufferView'] for a in self.data['accessors']]
        assert len(indices) == len(set(indices))

    def array(self, index):
        a = self.data['accessors'][index]
        assert not a.get('byteOffset') and 'sparse' not in a
        data = self.views[a['bufferView']]
        return np.frombuffer(data,TYPES[a['componentType']]).reshape(a['count'],WIDTH[a['type']])

    def update(self, index, array):
        a = self.data['accessors'][index]
        assert array.dtype == np.dtype(TYPES[a['componentType']])
        self.views[a['bufferView']] = array.tobytes()
        a['count'] = len(array)
        for field, reduction in [('min',np.min),('max',np.max)]:
            if field in a:
                a[field] = reduction(array,axis=0).tolist()

    def save(self, output):
        blob = bytearray()
        for view, block in zip(self.data['bufferViews'],self.views):
            blob.extend(bytes(-len(blob)%4))
            view.update(byteOffset=len(blob), byteLength=len(block))
            blob.extend(block)
        self.data['buffers'][0]['byteLength'] = len(blob)
        blob.extend(bytes(-len(blob)%4))
        manifest = json.dumps(self.data,ensure_ascii=False,separators=(',',':')).encode()
        manifest += b' ' * (-len(manifest)%4)
        with output.open('wb') as fp:
            fp.write(struct.pack('<4sII', b'glTF', 2, 28+len(manifest)+len(blob)))
            fp.write(struct.pack('<I4s',len(manifest),b'JSON'))
            fp.write(manifest)
            fp.write(struct.pack('<I4s',len(blob),b'BIN\0'))
            fp.write(blob)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def transfer(doc, primitive, desired_local):
    iacc = primitive['indices']
    attrs = primitive['attributes']
    indices = doc.array(iacc).ravel()
    old_vertex_count = len(doc.array(attrs['POSITION']))
    assert len(np.unique(indices)) == old_vertex_count
    # Key by original attribute row AND native corner-normal bits. This preserves
    # every seam, and splits a shared row if two corners require different normals.
    normal_bits = np.ascontiguousarray(desired_local.reshape(-1,3),dtype='<f4').view('<u4')
    keys = np.column_stack((indices.astype('<u4'),normal_bits))
    rows, inverse = np.unique(keys,axis=0,return_inverse=True)
    old_rows = rows[:,0]
    nrows = np.ascontiguousarray(rows[:,1:]).view('<f4')
    assert np.array_equal(nrows[inverse], normal_bits.view('<f4'))
    for name, index in attrs.items():
        if name == 'NORMAL':
            doc.update(index,nrows)
        else:
            doc.update(index,doc.array(index)[old_rows])
    if doc.data['accessors'][iacc]['componentType'] == 5123 and len(rows) > 65535:
        doc.data['accessors'][iacc]['componentType'] = 5125
    newtype = TYPES[doc.data['accessors'][iacc]['componentType']]
    doc.update(iacc,inverse.astype(newtype).reshape(-1,1))
    return len(rows)-old_vertex_count


if __name__ == '__main__':
    source, output = (Path(x).resolve() for x in sys.argv[sys.argv.index('--')+1:])
    native = Path(bpy.data.filepath)
    assert sha(source)==check.GLB_SHA and sha(native) in check.NATIVE_HASHES
    assert output not in {source, native.resolve()}
    model = Document(source)
    native_groups, names = check.mesh_groups()
    transforms = {}
    exported = check.gltf_groups(source,transforms)
    assert set(native_groups) == set(exported)
    splits = {}
    for key in sorted(native_groups):
        raw = native_groups.pop(key)
        pos, norm, _, _ = (np.concatenate(records) for records in zip(*raw))
        target, _ = exported.pop(key)
        ei,ni,perms,ed,nd,_ = check.associate(pos,target)
        assert len(ei)==len(pos)==len(target), key
        new = np.empty_like(target)
        new[ei] = norm[ni[:,None],check.PERMS[perms]]
        world, primitive = transforms[key]
        # Inverse of the row-vector inverse-transpose normal map used in the audit.
        local = check.unit(new @ world)
        splits[' / '.join(key)] = transfer(model,primitive,local)
    model.save(output)
    print(json.dumps({'file':output.name,'sha256':sha(output),'bytes':output.stat().st_size,
                      'additional_vertex_rows':sum(splits.values()),'splits_per_group':splits}))
