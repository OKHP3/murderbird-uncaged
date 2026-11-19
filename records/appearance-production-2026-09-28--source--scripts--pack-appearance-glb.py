"""Losslessly deduplicate identical GLB bufferView payloads.

Only bufferView.byteOffset values and buffers[0].byteLength change in the
semantic glTF JSON. Geometry, materials and image payloads are never altered.
The utility is standard-library only and refuses to overwrite any file.
"""

from pathlib import Path
import argparse
import copy
import hashlib
import json
import struct
import sys


MAGIC = b'glTF'
JSON_CHUNK = 0x4E4F534A
BIN_CHUNK = 0x004E4942


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def parse_glb(raw):
    require(len(raw) >= 20 and raw[:4] == MAGIC, 'Input is not a GLB file')
    version, total = struct.unpack_from('<II', raw, 4)
    require(version == 2, f'Expected GLB version 2, received {version}')
    require(total == len(raw), 'GLB declared length does not match file size')
    chunks = []
    offset = 12
    while offset < total:
        require(offset + 8 <= total, 'Truncated GLB chunk header')
        length, kind = struct.unpack_from('<II', raw, offset)
        offset += 8
        require(length % 4 == 0, 'GLB chunk length is not four-byte aligned')
        require(offset + length <= total, 'GLB chunk exceeds declared file length')
        chunks.append((kind, raw[offset:offset + length]))
        offset += length
    require(chunks and chunks[0][0] == JSON_CHUNK,
            'GLB JSON chunk must be first')
    require(sum(kind == JSON_CHUNK for kind, _ in chunks) == 1,
            'Expected exactly one GLB JSON chunk')
    require(sum(kind == BIN_CHUNK for kind, _ in chunks) == 1,
            'Expected exactly one embedded BIN chunk')
    bin_index = next(i for i, (kind, _) in enumerate(chunks) if kind == BIN_CHUNK)
    require(bin_index == 1, 'GLB BIN chunk must follow the JSON chunk')
    try:
        gltf = json.loads(chunks[0][1].decode('utf-8').rstrip(' \t\r\n\0'))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f'Invalid GLB JSON chunk: {error}') from error
    return gltf, chunks


def semantic_json(gltf):
    """Copy glTF JSON and remove the only permitted rewrite fields."""
    value = copy.deepcopy(gltf)
    for view in value.get('bufferViews', []):
        view.pop('byteOffset', None)
    if value.get('buffers'):
        value['buffers'][0].pop('byteLength', None)
    return value


def encode_glb(gltf, chunks):
    json_bytes = json.dumps(gltf, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    json_bytes += b' ' * ((-len(json_bytes)) % 4)
    encoded_chunks = []
    for index, (kind, payload) in enumerate(chunks):
        if index == 0:
            payload = json_bytes
        encoded_chunks.append(struct.pack('<II', len(payload), kind) + payload)
    total = 12 + sum(map(len, encoded_chunks))
    return MAGIC + struct.pack('<II', 2, total) + b''.join(encoded_chunks)


def pack(raw):
    gltf, chunks = parse_glb(raw)
    buffers = gltf.get('buffers')
    require(isinstance(buffers, list) and len(buffers) == 1,
            'Expected exactly one glTF buffer')
    require('uri' not in buffers[0], 'Buffer must be embedded in GLB')
    declared_buffer_length = buffers[0].get('byteLength')
    require(isinstance(declared_buffer_length, int) and declared_buffer_length >= 0,
            'Invalid embedded buffer byteLength')
    original_bin = chunks[1][1]
    require(declared_buffer_length <= len(original_bin),
            'Embedded buffer byteLength exceeds BIN chunk')
    bin_payload = original_bin[:declared_buffer_length]
    views = gltf.get('bufferViews')
    require(isinstance(views, list), 'glTF bufferViews must be an array')

    original_slices = []
    unique_by_digest = {}
    packed_bin = bytearray()
    reused_bytes = 0
    duplicate_count = 0
    for index, view in enumerate(views):
        require(view.get('buffer', 0) == 0,
                f'bufferView {index} refers to a non-embedded buffer')
        offset = view.get('byteOffset', 0)
        length = view.get('byteLength')
        require(isinstance(offset, int) and isinstance(length, int)
                and offset >= 0 and length >= 0,
                f'Invalid byte range in bufferView {index}')
        require(offset + length <= declared_buffer_length,
                f'bufferView {index} exceeds declared embedded buffer')
        payload = bin_payload[offset:offset + length]
        require(len(payload) == length, f'Truncated bytes in bufferView {index}')
        original_slices.append(payload)
        digest = sha256(payload)
        candidate = next((entry for entry in unique_by_digest.get(digest, [])
                          if entry[0] == payload), None)
        if candidate is not None:
            new_offset = candidate[1]
            duplicate_count += 1
            reused_bytes += length
        else:
            pad = (-len(packed_bin)) % 4
            if pad:
                packed_bin.extend(b'\0' * pad)
            new_offset = len(packed_bin)
            packed_bin.extend(payload)
            unique_by_digest.setdefault(digest, []).append((payload, new_offset))
        view['byteOffset'] = new_offset

    packed_payload_length = len(packed_bin)
    gltf['buffers'][0]['byteLength'] = packed_payload_length
    bin_chunk = bytes(packed_bin) + b'\0' * ((-len(packed_bin)) % 4)
    chunks[1] = (BIN_CHUNK, bin_chunk)

    # Prove that all non-offset JSON semantics stayed byte-for-byte equivalent
    # after canonical JSON decoding, and that each view resolves identically.
    output_raw = encode_glb(gltf, chunks)
    output_gltf, output_chunks = parse_glb(output_raw)
    output_bin = output_chunks[1][1]
    require(semantic_json(output_gltf) == semantic_json(parse_glb(raw)[0]),
            'Unexpected semantic JSON change')
    require(len(output_gltf['bufferViews']) == len(original_slices),
            'bufferView count changed')
    for index, (view, expected) in enumerate(zip(output_gltf['bufferViews'], original_slices)):
        new_offset = view.get('byteOffset', 0)
        length = view['byteLength']
        require(new_offset % 4 == 0, f'Packed bufferView {index} is not aligned')
        actual = output_bin[new_offset:new_offset + length]
        require(actual == expected, f'Packed bufferView {index} bytes changed')
    require(output_gltf['buffers'][0]['byteLength'] == packed_payload_length,
            'Packed declared buffer length mismatch')
    return output_raw, {
        'inputBytes': len(raw),
        'outputBytes': len(output_raw),
        'inputBufferBytes': declared_buffer_length,
        'outputBufferBytes': packed_payload_length,
        'bufferBytesSaved': declared_buffer_length - packed_payload_length,
        'bufferViews': len(views),
        'uniqueBufferPayloadBytes': sum(len(payload)
                                        for entries in unique_by_digest.values()
                                        for payload, _ in entries),
        'duplicateBufferViews': duplicate_count,
        'duplicatePayloadBytesReused': reused_bytes,
        'inputSha256': sha256(raw),
        'outputSha256': sha256(output_raw),
        'proofs': {
            'allBufferViewSlicesByteExact': True,
            'allOtherSemanticJsonUnchanged': True,
            'bufferViewIndicesAndCountUnchanged': True,
            'outputBufferViewsFourByteAligned': True,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--reportpath', type=Path)
    args = parser.parse_args()

    source = args.input.expanduser().resolve()
    destination = args.output.expanduser().resolve()
    report_path = args.reportpath.expanduser().resolve() if args.reportpath else None
    require(source != destination, 'Input and output paths must differ')
    require(source.is_file(), f'Input GLB does not exist: {source}')
    require(not destination.exists(), f'Refusing to overwrite output: {destination}')
    if report_path is not None:
        require(report_path not in (source, destination),
                'Report path must differ from input and output')
        require(not report_path.exists(), f'Refusing to overwrite report: {report_path}')

    output, facts = pack(source.read_bytes())
    facts['inputPath'] = str(source)
    facts['outputPath'] = str(destination)
    if report_path is not None:
        facts['reportPath'] = str(report_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('xb') as stream:
        stream.write(output)
    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open('x', encoding='utf-8') as stream:
            json.dump(facts, stream, indent=2)
            stream.write('\n')
    print(json.dumps(facts, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        raise SystemExit(1)
