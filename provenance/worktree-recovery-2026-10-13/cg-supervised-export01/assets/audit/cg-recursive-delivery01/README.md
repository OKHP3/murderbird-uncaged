# Saved09 successor delivery runner

Scope: reusable development authoring from the exact frozen three-era saved09 natives. The runner preserves original receiving payloads, material graphs, FILE image metadata and packed pixels. It creates a new versioned checkpoint; it changes no frozen09 source, production runtime, dependencies or published material. Root module selection can authorize a provisional whole-image study without artistic acceptance.

Runner: `scripts/cg-recursive-delivery01.py`. Run through Blender 5.2.1 with CPU threads 2. Check the process result **and** `CG_RECURSIVE_DELIVERY01_COMPLETE` in its log; Blender can return zero after a Python error. The script also emits `CG_RECURSIVE_DELIVERY01_FAILED` and calls `sys.exit(1)` on failure.

The required `--source-root` is the integrator checkout containing the saved09 frozen manifest. The manifest, native, per-era camera receipt, preservation helper, payload/graph auditors and material-faithful exporter are hash checked. There is no default receiving06 regeneration or frozen09 output path.

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background --threads 2 \
  --python /Users/okh/.codex/worktrees/cg-supervised-export01/murderbird-uncaged/scripts/cg-recursive-delivery01.py -- \
  --source-root /Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged \
  --output-root /path/to/new/successor-parent \
  --checkpoint-id loop01-study01 --mode candidate --era builder \
  --selection /path/to/root-selected-modules.json \
  --views whole-clay,whole-pbr --samples 4 --resolution 640
```

Root selection format:

```json
{
  "root_adjudication_complete": true,
  "visible_whole_candidate_approved": false,
  "selection_scope": "Provisional coherent whole-image study; no owner artistic acceptance",
  "modules": [
    {
      "path": "/absolute/path/to/head-module.py",
      "sha256": "exact-module-sha256",
      "root_path": "/optional/explicit/module-resource-root",
      "declared_superseded_render_hides": [
        {"name": "Exact receiving object name", "hide_set": true}
      ]
    }
  ]
}
```

Each module must expose `apply(scene, root_path, era)`. String hide entries permit `hide_render=True` only. Object entries with `hide_set=true` additionally permit the declared per-view-layer hide. Every receiving `hide_viewport` flag, payload, UV, slot, polygon assignment, transform and original graph remains exact. Changing original material graphs is rejected; a finish module may supply new materials only on newly added successor objects.

`--mode baseline` applies no modules. `--views none` performs custody/save/reopen and finite evaluated geometry checks without rendering. Whole views are aliases for the saved09 `canon-neutral` view; the clay view uses a temporary material override in a separate disposable scene. `head,body,profile,rear` map to saved09 `head-neck`, `body-detail`, `side-profile`, `neutral-180`. Individual exact saved09 camera keys are also accepted. `--views final` creates canon comparisons, head/body/feet/profile, eight neutral and eight workshop views plus hero; use `--era all` for the full inherited character packet. The baseline and candidate must use identical sample/resolution settings for comparison. `--resolution 0` retains saved09 pixel dimensions.

Final packets or `--export` require `visible_whole_candidate_approved=true` in root selection. Export uses the proven saved09 per-face material batching, original embedded maps and evaluated UV/normal corners; it excludes authoring guides and rejects animations, skins and external URIs. Native and browser illumination remain different; loading a GLB does not establish pixel parity or artistic acceptance.

The output is `<output-root>/<checkpoint-id>/<era>/`. Existing checkpoint/era outputs are rejected. `--continue-unfinalized` only permits adding an absent era to the exact same new unfinalized checkpoint with the same runner/selection signature; it never overwrites an existing era. Outputs under historical supervised asset/audit trees, `public/` or private archives are rejected. Failure leaves an unfinalized checkpoint and logs for diagnosis; use a new id for a changed selection.

The runner first saves/reopens the successor native before rendering; original09 cameras, lights and stage are used only through a separate review scene. The receiving stage is never unhidden or changed in the native. The temporary stage copy, world, camera, lights and clay are removed after rendering, then custody is checked again. Current receiving counts are verified from actual loaded files as 7,608 mesh/empty payloads, 62 original materials and 161 packed FILE records. Historical06 counts of 7,424/56/160 are not used as the receiving inventory.

Initial preflight: `custody-preflight01/builder/receipt.json` and `custody-preflight01.log`. Unchanged saved09 was saved into a new disposable native and reopened. All 7,608 original payloads, 62 graphs and 161 image bytes/metadata remained exact; 0 meshes were added. Finite positions, UVs, corner normals and assigned face materials passed for 1,974 visible meshes and 642,898 evaluated triangles. The 192 inherited zero-area triangles are recorded; no manifold/engineering gate is inferred. No candidate modules, final packet, export, browser, CI or publication were run in this preflight.

## Delivery02 correction and retained-loop support

`scripts/cg-recursive-delivery02.py` is the recommended successor version for all eras. Delivery01 stays unchanged at `3b7584630e71ca83dd7304eb940cdb8473d6c78e85a0756d4b0aaefe8a67a451` for the root's already pinned builder study. Its initial global 161-image guard is unsuitable for Maker/Mechanic. An independent hash-checked native inventory in `era-receiving-counts.json` confirms every era has 7,608 payloads / 7,599 meshes / 9 empties / 62 materials, while Advanced has 161 FILE/packed images and Maker/Mechanic have 160 each. Delivery02 uses these exact era inventories. The source native pins still control identity.

Delivery02 adds `--receiving-manifest /path/to/root-retained-loop-inputs.json`. This permits loop02/03 to start from the root-retained prior whole character instead of rebuilding from09. Saved09 remains the immutable camera/light/helper authority. The manifest must explicitly record root retention approval, loop number, each era's native path/hash and actual custody counts:

```json
{
  "root_retained_candidate_approved": true,
  "loop": 2,
  "approval_scope": "Root retained coherent whole-character gain; owner final likeness acceptance remains outstanding",
  "natives": {
    "builder": {
      "path": "/absolute/path/to/retained/builder.blend",
      "sha256": "exact-retained-native-sha256",
      "custody_counts": {
        "mesh_empty": 7650,
        "materials": 62,
        "file_images": 161,
        "packed_images": 161
      }
    }
  }
}
```

The counts in this example are placeholders, not evidence of a real candidate. Obtain actual counts from the retained native's custody readback. Include Maker/Mechanic entries when `--era all` is requested. The module selection still supplies the next modules and declared receiving render-hides; exact retention of every newly receiving object, graph and image is checked against that native. Historical09 inputs also remain hash checked. Existing output and stage/clay custody rules are unchanged. Delivery02 completion marker is `CG_RECURSIVE_DELIVERY02_COMPLETE`.
