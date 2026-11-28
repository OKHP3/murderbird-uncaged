# First Choice · Advanced study: closeout record

Date: November 27, 2026 (America/Chicago). Source thread: the Mac Studio Codex session that built First Choice (Apple M4 Max, Blender 5.2.1 LTS), merged to `main` by PR #105 from `private/first-choice-1123` on November 23. The original checkpoint and the later three-era and Windows replay are recorded below.

## Owner disposition

On November 27 the owner kept v1.1 as the final release ("Keep v1.1 final") and directed that the work be public ("No private all publicly published"). First Choice is therefore a **published, documented study**. It is not integrated into the exhibit, and its likeness is **not accepted**. The parked likeness status from November 13 is unchanged. See [goal.md](../goal.md).

## What the thread produced, and where it is

| Item | Identity | On `main` |
|---|---|---|
| Build, sculpt, motion, finish, cinema and delivery scripts | `atelier/` (finish, head, mantle, motion, pedal, cinema, delivery, runtime) | Yes |
| Integration contract: clip `First Choice`, 10.5 s, six pivots, intended host era Advanced | [atelier/delivery/integration.md](../atelier/delivery/integration.md) | Yes |
| Rebuild steps from the retained04 Advanced native | [atelier/delivery/rebuild.md](../atelier/delivery/rebuild.md) | Yes |
| Earlier offline viewer, including its original embedded GLB (63,123,668 bytes; tested offline) | [atelier/runtime/.qa/First-Choice-portable.html](../atelier/runtime/.qa/First-Choice-portable.html), [result](../atelier/runtime/.qa/portable-functional-result.json) | Yes, as an ordinary Git file |
| Motion rig sample | [atelier/motion/native-only/rig-sample.glb](../atelier/motion/native-only/rig-sample.glb) | Yes |
| Material maps, review renders and verification evidence | `atelier/` evidence folders | Yes |
| Native scene `first-choice.blend` | SHA-256 `1e59785a11aadf491714ef1b5aa682ff1b9efa0a6a3b421414f3bb7de053a05b` | **Published.** See the verified copies below. |
| Standalone `first-choice.glb` | 54,411,132 bytes, SHA-256 `88ff5f671a7359c04177b77c3dc01630491189f58d24e6bc0d85d7ed98ccd12e` | [Original finished GLB](../atelier/delivery/first-choice.glb?raw=1) |
| Screening `first-choice-native-preview.mp4` (1920 × 1080, 24 fps, 252 frames, 1,820,642 bytes) | SHA-256 `fc618415923d0fcfc8332e4a4ee66607c6c81d581047782346833f15e06453ad`, [verification](../atelier/cinema/screening-verification.json) | **Published.** See the verified copies below. |
| Proof renders from `render_views.py` | Listed in the rebuild steps | **Published.** See the verified copies below. |

Labels: the study documents no longer call it private. The build and render scripts keep their original working labels ("private production candidate", "Private Advanced candidate") because they are the evidence that produced the recorded bytes; changing them would change what a rebuild writes.

## Publication of the outstanding files

The public [editable Blender scene](../atelier/delivery/first-choice.blend?raw=1) contains the four First Choice actions and all 28 packed images. Its SHA-256 is `019949c70a8aaff3314244b5fc222d9332dcaf23a24ff208576d52791395ae95`. The original frozen scene contains absolute image paths and a saved file-browser directory. For publication those fields were normalized. The decompressed scene bytes outside those fields matched the original. Blender 5.2.1 reopened the copy with matching mesh and material data, packed images and sampled world transforms. [Original and publication identities](../atelier/delivery/study-manifest.json)

The [silent 10.5-second screening](../atelier/cinema/first-choice-native-preview.mp4?raw=1) and [opening still](../atelier/cinema/first-choice-opening.jpg) preserve their original bytes. All [17 proof images](../atelier/cinema/proofs/) retain their decoded pixels after removal of the authoring location from their JPEG metadata. The [final Advanced viewer](../atelier/runtime/first-choice-final.html?raw=1) embeds the original 54,411,132-byte GLB and the normalized portrait. The earlier viewer listed above contains a different 45,161,920-byte GLB. [Final viewer browser verification](../atelier/delivery/final-viewer-browser.json)

The two related threads also produced an independently buildable three-era study and a Windows GPU replay tool. The [mission and disposition](three-eras--native-windows-closeout.md) links the complete requirements register, editable source, playable artifact, tests and remaining product gates. Retiring the old merged branch is optional.
