# Rebuild the First Choice study

The accompanying patch starts from OKHP3/murderbird-uncaged main at `ca448adf1c069d3b5f74bac8784320707176dbb6`. Apply it in an isolated checkout that already contains the verified retained04 Advanced native source. The project source and image authority are listed by hash in the evidence directory.

The build used Blender 5.2.1 LTS, Python 3.14 with NumPy 2.4.4 and Pillow 12.3.0, the repository package lock, Three.js 0.186.1 and Vite 8.3.8. From the checkout root, with Blender on PATH, run the following commands.

```sh
python3 atelier/finish/make_surfaces.py
blender -b media/cg-retained04-builder-murderbird-recursive-builder.blend \
  --python-exit-code 1 -P atelier/finish/build_candidate.py -- --out ../candidate
python3 atelier/finish/stage-assets/bake-workshop.py ../candidate/first-choice.glb
npm ci
node node_modules/vite/bin/vite.js build --config atelier/runtime/vite.config.js --configLoader native
blender -b ../candidate/first-choice.blend --python-exit-code 1 \
  -P atelier/finish/render_views.py -- --out ../proofs
node atelier/runtime/make-portable.mjs atelier/runtime/dist \
  ../candidate/first-choice.glb ../proofs/portrait.jpg ../first-choice.html
```

The single-file viewer opens directly from disk. A host can instead copy the built `dist` contents to a local server root and place the GLB and `first-choice-still.jpg` beside its index. The cost-free reconstruction and reference inspection for this candidate were performed locally. Raw native archive masters remain in their original repository. The packaged derivative opens independently.

The native movie render script takes a verified native SHA-256 and uses local Apple Metal. Its encoder uses FFmpeg and validates the H.264 video.

The recorded hashes identify the delivered bytes. Blender file serialization, mesh ordering, GPU rendering and encoders can vary between rebuilds and machines.

## Archived outputs

The [editable packaged scene](first-choice.blend?raw=1) opens without external image files. The [original derived GLB](first-choice.glb?raw=1), [final Advanced viewer](../runtime/first-choice-final.html?raw=1) and [native screening](../cinema/first-choice-native-preview.mp4?raw=1) are available directly. The [three-era study](../three-eras/README.md) builds independently from its included runtime inputs. To reproduce its full-resolution GLB from the published native, follow the [normal-correction protocol](../three-eras/normal-correction/README.md).
