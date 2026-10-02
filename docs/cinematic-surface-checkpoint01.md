# Cinematic surface checkpoint01

Status: implemented local visual proposal, rooted in the owner's October1 appearance-first direction. Final likeness remains unresolved. The released V37 exhibit is unchanged; this candidate is available through the development review selector, not a new Pages deployment.

The retained hanging-breast02 model supplies the complete body and existing articulation. This pass changes surface assignments, UVs and PBR response across the whole bird. It corrects empty material slots that left breast faces pale, reduces chrome-like gloss, and adds neutral base variation, roughness and forged relief maps. Maker remains bronze with dark optics; Mechanic uses subdued inherited metal and distinct repair finish; Advanced retains the body and uses restrained amber optics. Geometry, attachment transforms, parents and era tags are preserved, so this is not a structural reconstruction or fabrication specification.

## Sources and deliverables

- Editable native: `assets/models/whole-character-v38/cinematic-surface01/attempt02/murderbird-v38-cinematic-surface01-attempt02.blend` — SHA256 `735f866469a1c9a4a6c030c1b27f3843e74060a8d7ba522080df66bcd7794721`.
- Runtime derivative: adjacent `murderbird-v38-cinematic-surface01-attempt02-rigid.glb` — SHA256 `cd9e2a852f4021f1ad14bc432189ad0eda65f5c7d221068f95c2e084bf3932fc`.
- Editable generation recipe: `scripts/build-v38-cinematic-surface01.py`; write-once output guards require preserving existing native/manual work before any new version.
- Authoring comparison: `assets/audit/whole-character-v38/cinematic-surface01/attempt02/`:12 same-camera full-bird renders, before/candidate × three eras × neutral/exhibit light, packed map sources and author receipt.
- Actual browser comparison: `assets/audit/whole-character-v38/cinematic-surface-integration01/review.html`. Select Before or Candidate, era, reference, camera and light; existing motion, inspection and reassembly controls remain available.

Selected Maker, Mechanic and master03 images control their respective visible finishes. July remains head-only; its excluded body/wing proportions are not imported. First Choice frames at0/4seconds were extracted by root from the verified eight-second `assets/video/murderbird-first-choice-635f0e15.mp4`. Worker checkout retained an LFS pointer for that video and used the verified extracted frames. The receipt's phrase "Owner-reviewed selected-video frames" means frames from the selected clip; these new frame extractions were not separately reviewed by the owner. Unseen surfaces and new detail remain proposals.

## Regional material and attachment map

| Region | Controlling appearance | Surface treatment in this pass | Attachment |
|---|---|---|---|
| Crown and skull | July head-only + era images | Bronze/slate plate color, fine shared grain, separated rim/recess roles | Existing rigid head/crown parts |
| Bill and mandible | July head-only | Dark hard metal; differentiated edge and cheek roles | Existing bill and jaw owners |
| Optics | Era images | Clear dark lens without forged maps; amber emission in Advanced only | Existing recessed optic assembly |
| Neck | Master03 + era images | Subdued overlapping guard finish, darker bearings/frame | Existing individual rigid cervical parts |
| Breast and torso | Master03 + era images | Material on formerly unassigned faces; matte plate response and fine relief | Existing separate breast shields and opening assemblies |
| Shoulders and wings | Master03 + era images | Plate/guard, warm edge and distinct repair roles | Existing compact articulated shield owners; asymmetry retained |
| Pelvis and hips | Master03 + era images | Dark frame and protective shell roles | Existing torso/pelvis assembly |
| Legs and ankles | Master03 + era images | Dark exposed members, differentiated bearing and guard finish | Existing rigid articulated limb parts |
| Feet and talons | Master03 + era images | Dark feet, edge/contact contrast, selective hard-metal response | Existing toe/foot owners |
| Back, underside, rear | Scoped image continuity; unseen parts reconstructed | Continuation of shell/frame role palette | Existing compact rigid assemblies |

The shared512² maps supply microdetail, not the reference's complete plate construction. Regional factors and material roles differentiate the envelope; full era-specific weathering, rivet detail and plate-edge wear are still incomplete. Maker currently shares the neutral microdetail with later eras; do not claim recovered aging or final per-era wear accuracy.

## Evidence and limits

Root export comparison confirms679 node names, exact parent/transform and era/region/surface tags, three embedded images and626 UV-bearing primitives. Worker native checks report625 mapped meshes and unchanged geometry. Source and candidate GLBs both contain zero embedded animations; existing procedural runtime movement is retained.

The16,065,032-byte GLB embeds three maps, approximately4MiB RGBA with mipmaps. Its120 texture definitions refer to only three image/sampler pairs; the current Three.js loader caches those pairs. Root browser observed seven GPU textures total versus four in baseline. This is not an exhaustive memory profiler.

`npm ci` and `npm run build` pass. Dist contains52 files including its release manifest; audit, candidate, provenance and private trees are excluded. The four released V37 model/fallback binaries retain their prior hashes. Existing fsevents script allow-list and large-bundle warnings remain. Detailed local build/export/browser evidence lives in the integration audit. MutationObserver errors were observed before this candidate and after navigation; their origin is unresolved, while the scene and controls remained functional. No clean-console claim is made. No new behavior tests or full mechanical-envelope audit were run: this checkpoint changes visual surfaces and review selection, not behavior logic.

Independent visual review finds a visible but modest whole-bird gain and clearer era separation. Root agrees that the bird still lacks the reference's richer plate construction. Next exterior priority: fine plate-edge/rivet definition and deliberate local finish variation on breast and shoulder mantle, with Maker cleaner and Mechanic repairs selectively worn. No hidden-support or engineering gate precedes that work. Owner artistic acceptance remains outstanding.
