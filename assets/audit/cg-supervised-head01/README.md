# Supervised head and neck increment 01

Editable visual proposal, after two focused attempts. **Owner likeness acceptance remains pending.** The curved neck and swept crown replace the baseline helmet/collar reading. This result still falls well short of the pinned source's interlocking head construction.

Source base: `d4798d079c467892d4a5703caef77a1ed120d10e`, frozen `assets/models/cinematic-cg-milestone02b/murderbird-cg-2b-builder.blend`, SHA-256 `9ba7fc471a86e5f1f9b8db881900725f8abf56546c69fecb125a236ec5b4a64c`. Reviewed shared goal: `origin/main` `251f2f0243181e97140179c2aff6eb057e165438`; the parent's current owner authorization supersedes the historical budget stop for this increment.

Controlling pixels viewed: owner-reissued Sept22 full-bird JPEG (`645d47c00ff46acae244aecf595608e8f49eb8095f5ca125da6b2eeeb4204114`) and July head-only PNG (`47658dba6496f2c8594a40ad412a8bfaa087939e90044d1597329a27ca68d4e9`). No source artwork was used as a texture. Reference binaries and historic scripts/native studies were preserved. Creative assets remain all rights reserved under `NOTICE.md`.

## Visible result and unresolved gaps

- Curved layered neck with bilateral real openings, a connected dark spine, three linkage rods and three journals per side. The existing neck root and head junction are unchanged.
- Swept crown/nape plates replace the clipped blocky cap. Attempt02 narrows and staggers the crown leaves and restores the inherited recessed optical seating rings.
- Deep divided bill remains separate from forehead; cheek opening and lower mandible rails expose actual space rather than a black aperture decal.
- **Remaining mismatch:** crown still reads as broad horizontal sheets instead of the source's compact broken interlocking clusters. The broad diagonal brow-to-bill-root strap is insufficient. Upper bill is still too clean; the lower jaw reads as an open horizontal fork rather than following the bill-root curve. Source regional material richness remains absent. Back surfaces and construction are inferred.

## Evidence

`before-head.png` / `after-head.png`: identical head diagnostic camera and neutral lighting. `before-whole.png` / `after-whole.png`: construction01's canon-neutral camera and lighting, resolution reduced to 850×566. The registration is a source-camera estimate, not a recovered photographic camera. `attempt01-head.png` and `attempt01-whole.png` preserve the first visible checkpoint. The second attempt is the final native and `after-*` pair.

![Head before](before-head.png)
![Head after](after-head.png)
![Whole bird after](after-whole.png)

## Reproduce and integrate

API: load the frozen 2b native, then call `apply(scene, root_path=None, era='builder')` from `scripts/cg-supervised-head-neck.py`. It is intentionally single-application; reload the source to repeat. `builder` is the existing native era name for Advanced. The module adds 151 editable meshes with explicit UVs, hides and retains superseded head/neck meshes, and keeps the original anchors.

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --python assets/audit/cg-supervised-head01/render-study.py
/Applications/Blender.app/Contents/MacOS/Blender -b --python assets/audit/cg-supervised-head01/check-study.py
```

New native: `murderbird-supervised-head01.blend`. `receipt.json` records hashes, exact cameras, superseded names, anchors and scope. `checks.json` records native reload and dark optic checks. No animation, engineering, runtime replacement, purchase, publication, commit or push is performed by this worker.

## Validation

- **PASS:** Blender module execution and four matched render outputs per attempt; final native reload; 151 new meshes have explicit UVs.
- **PASS:** snapshot equality for 4,742 body/stance meshes (transform, visibility, vertex count and material names); all inherited empty anchor matrices remain unchanged. Exact source-native hash unchanged.
- **PASS:** Maker and Mechanic module application yields zero emission for every visible head optic; no era render was generated. Advanced preserves the restrained inherited amber core.
- **PASS:** Python syntax and whitespace checks.
- **WARN:** visual comparison confirms the gains and unresolved gaps above; neither a worker verdict nor these checks establish source likeness.
- **NOT RUN:** browser export/parity, eight-angle integrated QA, runtime/app build, CI or deployment. The module changes a native study only; the parent integrator owns full-character integration and wider review.

Next action: parent integrates the module with its shoulder work and judges the complete bird against the pinned sources. Stop after this second focused attempt.
