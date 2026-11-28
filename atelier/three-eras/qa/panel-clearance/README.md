# Regional panel clearance replay

This test measures the digital clearance of opening covers in the study's actual WebGL scene. It operates the inspection controls in a local Chromium session and reads the meshes Three.js reports to its scene observer. It exercises the head cover against its cranial compartment, the breast cover against its thoracic compartment and each mantle against its opposite, for all three eras.

## Run

Build the study once. Install the QA directory’s locked Playwright dependency and a matching Chromium using the instructions in [browser QA](../README.md). Supply Python 3 with NumPy. From the study directory, run the following command.

```sh
python3 qa/panel-clearance/replay.py
```

For the additional triangle-pair test, pass a Blender executable with its bundled NumPy and mathutils. The reference used Blender 5.2.1 LTS.

```sh
python3 qa/panel-clearance/replay.py --blender blender
```

The harness checks the standalone and hosted script against the frozen build manifest. It collects 51 positions per pair from closed to fully open in two-percent increments, then reassembles each cover. Temporary mesh buffers are discarded on exit. Results go to `qa/.results/panels/`. Use `--app` to select a separate built study or `--output` to change the results directory.

## Interpretation

For each vertex of a cover rotating about a stationary hinge, its signed X projection has a sinusoidal form. The test checks this form against every observed transform, evaluates both endpoints and all interior maxima, and compares the farthest moving vertex with the nearest stationary vertex. The published minimum bound across the twelve pairs is 0.012166331 model units. The optional Blender test checks transverse triangle intersections at each of the 612 sampled poses. Positive separation, fixed hinge positions and return to the starting matrices apply to those digital mesh pairs in regional inspection. Other surfaces and simultaneous motions need their own tests.
