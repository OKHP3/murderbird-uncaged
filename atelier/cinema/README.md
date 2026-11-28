# First Choice screening render

The screening uses the fixed `first-choice.blend` with SHA-256 `1e59785a11aadf491714ef1b5aa682ff1b9efa0a6a3b421414f3bb7de053a05b`. The camera and lighting changes exist in the rendering process only. The supplied bird geometry, four animated pivots, saddle and seated stand perform the same timeline as the interactive model. The movie is a companion for viewing that performance in two dimensions.

The main camera observes the whole motion in one continuous shot. The render uses a 44.5 mm lens, the native studio cove, three-quarter framing and a darker, cooler floor with warm raking light on the shell. Cycles renders 1920 × 1080 on the local Apple M4 Max Metal GPU with a fixed sampling seed and OpenImageDenoise. Native frames 0 through 251 yield 252 displayed frames at 24 fps. The final pose is already at rest by frame 247. Frame 252 is separately available in the native timeline for an exact endpoint check.

Reproduce from the task root using Blender 5.2.1 LTS on the recorded hardware. Use a new frame directory when changing the camera, source or sampling settings. In an interrupted run, the script writes completed frames atomically and resumes missing frames in the same directory.

```sh
blender -b delivery/frozen/first-choice.blend --python-exit-code 1 \
  -P native/atelier/cinema/render_screening.py -- \
  --out review/cinema-work/final-frames

sips -s format jpeg -s formatOptions 95 \
  review/cinema-work/final-frames/hero-0000.png \
  --out delivery/final-screening/first-choice-opening.jpg

python3 native/atelier/cinema/encode_screening.py \
  --frames review/cinema-work/final-frames \
  --out delivery/final-screening \
  --receipt native/atelier/cinema/screening-verification.json
```

The output is silent H.264 High Profile in a fast-start MP4 with a limited-range BT.709 transfer. The verification step counts decoded frames, checks duration and stream format, performs a full decode and compares movement over the head, shoe, base and planted-toe image regions at selected native times. The opening JPEG is derived from the identical first rendered frame. The receipt records both file hashes and the source-frame hash.

## Published screening and scene

Download the [screening](first-choice-native-preview.mp4?raw=1), [opening still](first-choice-opening.jpg) and [proofs](proofs/). For a fresh screening from the public scene, run the renderer from the repository root with Blender 5.2.1 on a supported Metal GPU. The published scene has normalized image paths and its own source digest.

```sh
blender --disable-autoexec -b atelier/delivery/first-choice.blend --python-exit-code 1 \
  -P atelier/cinema/render_screening.py -- --out ./screening-frames \
  --source-sha 019949c70a8aaff3314244b5fc222d9332dcaf23a24ff208576d52791395ae95
```
