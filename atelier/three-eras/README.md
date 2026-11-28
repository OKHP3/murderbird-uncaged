# MurderBird three-era study

Build this study to operate the Maker bird, wind the Mechanic bird, or watch the Advanced bird make its first choice. All three use the same articulated exterior. Jamie accepted that exterior for era development. Final artistic likeness remains open. The published v1.1 exhibit has its own build at the repository root.

[Download the verified offline viewer](three-eras-offline.html?raw=1) and open it in your browser. [Watch the motion studies or hear the recorded foley](screenings/README.md). [Read the desktop test results and remaining product requirements](../../records/three-eras--desktop-verification-2026-11-24.md).

## Build and open the viewer

From this directory, use Node 24 or 26, npm and Python 3.8 or later. The recorded rebuild used Node 26.13.1 on Apple Silicon. The checked-in model streams, images, bindings, audio and pilot are sufficient to build the standalone. The package lock pins Three.js, Vite and their build dependencies.

```sh
npm ci
npm run build
npm run verify
```

Open `MurderBird-Three-Eras.html` directly in a desktop browser. Choose an era and select **Enter 3D exhibit**. The file contains the model, stage, controls, still walkthrough, procedural foley and full song. Network access is optional for the story and gallery links. To serve the built exhibit locally, run `npm run preview` and open the address it prints. For live source editing use `npm run dev`.

The standalone is 47,367,367 bytes with SHA-256 `ff21d980020c4654ced6e1617df1076e63eb599e99b9af1e6461643db6ad23e9`. Verification checks it and each of the 32 files in the compact `web/` build against [the recorded output identities](hosted-manifest.json).

### Optional lossless music loop

The hosted preview can stream the two segments of the lossless *Iron Verdict v3* recording. If the repository’s existing FLAC is available locally in full, run the following from this directory. You can also pass the path to an existing copy of that recording.

```sh
npm run build -- --loop ../../public/audio/iron-verdict-v3/seamless-loop.flac
npm run verify -- --full
```

The build checks the recording’s 30,880,257 bytes and SHA-256 `d9bc121c0c2f1a04ff8456b8aeea1ae6d48fdc1777119ef4823bebc458425a72` before emitting either segment. The full build verifies 34 hosted files and the same standalone. To play this version from the standalone, select **Seamless loop** and choose the FLAC when prompted. The full song and the silent First Choice pilot are embedded in both builds.

## Operate and inspect the bird

| Era | Interaction |
| --- | --- |
| Maker | Select the leg, wing, tail, neck or jaw lever and move it to operate the linkage. Return the lever to its starting position to reset that motion. |
| Mechanic | Wind the train and follow the cam and rod through one 5.2-second cycle. |
| Advanced | Play **First Choice** from the Saddle camera. Watch the weight shift and head dip, or wake the enclosure and approach from either side to explore its response. |

For each era, choose an assembly, select **Focus assembly** and move **Panel opening**. **Reassemble** closes the exterior. **Return to rest** restores the mechanism and camera. Reduced-motion preferences pause automatic movement and keep manual inspection available. The still walkthrough also works with WebGL disabled.

## Editable source and rights

The shared glTF model uses two streams in `assets/`. The runtime shows the preview textures first, verifies the full model digest, then promotes the live textures. The full model’s SHA-256 is `20632ff6116f93827bc814d53301749dec1ef035165749db2d819bb89edcd41c`. `src/` contains the era treatments, rig bindings, inspection, motion, foley, transport and workshop. `src/stage-assets/bake-workshop.py` regenerates the workshop texture sources using NumPy and Pillow. The standard browser build uses the supplied textures.

Jamie Hill / OverKill Hill P³ retains the character, art, music and other creative rights. See the [content notice](NOTICE.md), [source license](LICENSE) and [third-party notices](third-party.txt).
