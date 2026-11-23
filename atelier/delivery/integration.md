# First Choice · Advanced

The carrier asset is `first-choice.glb`. Load the scene at identity with glTF 2.0 semantics. Blender uses Z up, −Y forward and −X anatomical left. glTF maps Blender (x, y, z) to (x, z, −y), so +Y is up, +Z is forward and −X is left. The floor is y = 0. The numeric scale is part of this digital scene.

## Binding and playback

Import the scene and its single animation using Three.js GLTFLoader. The mounted bird and support are separate children of the same scene. Preserve both root transforms. All six pivot nodes carry the custom property `fc_region`, available under `object.userData.fc_region` in Three. The mesh batches carry `userData.region`. Bind the mixer to `gltf.scene` so that both hierarchies participate. Three converts spaces to underscores when binding tracks. Prefer the stable region property over a display-name lookup. The factory alongside this note implements seeking and leaves wall-clock ownership to the host.

```js
const gltf = await loader.loadAsync(modelUrl);
const firstChoice = attachFirstChoice(gltf);
scene.add(firstChoice.root);
// Seconds since this rendition of the beat began.
// Pass absolute time on every host frame, including after a seek.
firstChoice.seek(elapsedSeconds);
```

The authored clip is `First Choice`, lasts 10.5 seconds and contains four LINEAR quaternion rotation tracks. Source sampling is 24 fps, frames 0 through 252 inclusive. Clip replay starts at 0. The pose at 10.5 seconds matches the opening pose. The uncut screening encodes displayed frames 0–251, with the identical end pose held in the last frames.

| glTF pivot name | Binding value | Parent | Local rest translation (x, y, z) | World rest pivot (x, y, z) |
|---|---|---|---|---|
| FC \| Ground | ground | scene | 0, 0, 0 | 0, 0, 0 |
| FC \| Stand | stand | scene | 0, 0, 0 | 0, 0, 0 |
| FC \| Saddle | saddle | stand | .025, .808, .438 | .025, .808, .438 |
| FC \| Torso | torso | ground | 0, .865, −.105 | 0, .865, −.105 |
| FC \| Neck | neck | torso | 0, .435, .210 | 0, 1.300, .105 |
| FC \| Head | head | neck | 0, .24059, .08437 | 0, 1.54059, .18937 |

All pivot quaternions start at (0, 0, 0, 1) and scales at (1, 1, 1). The glTF leaf meshes have their own local transforms. Keeping the exported hierarchy intact preserves the visible bearing, shell registrations and optic placement. The JSON contract in the evidence directory records the exact float values and node indices.

## Timing for integration

| Native frame | Seconds | Visible beat |
|---|---:|---|
| 0–36 | 0–1.50 | Bird and saddle are seated. |
| 36–54 | 1.50–2.25 | The cradle gives at its retained pivot. Fixed cap and base stay seated. |
| 44–73 | 1.83–3.04 | Hips counterbalance over the planted feet as the breast leaves the shoe. |
| 98–155 | 4.08–6.46 | Neck and head incline toward the bearing. |
| 155–193 | 6.46–8.04 | The bird holds its attention on the fitting. |
| 193–252 | 8.04–10.50 | The body and saddle reseat and settle. |

The embedded acting belongs to the self-directed Advanced era. Maker requires external operation. Mechanic requires constrained clockwork. A host with all three eras should select this asset and play this clip for Advanced. The muted local screening has no instruction cue. A host adding audio can synchronize to the clip’s normalized or absolute time. Material textures, optics, vertex occlusion and fixture travel are embedded in the GLB. The workshop, contact art and camera are separate in the viewer.

## Asset data

The runtime model contains 721,254 indexed triangles across 49 draw primitives, 11 meshes and 17 nodes. It uses 16 materials and 28 embedded images, including the inherited amber optic and generated surface maps. Required host features include a glTF 2.0 PBR path and support for the clearcoat/emissive-strength material extensions used by the optic. The position, normal, index and animation accessor checks are in `evidence/model-contract.json`.

The native file preserves individually selectable castings, the six motion pivots, the staged camera, lights, packed surface maps and named NLA tracks. The mesh batch boundaries in the GLB preserve the acting pivot groups for real-time playback. Its shield wings travel with the torso in this beat.
