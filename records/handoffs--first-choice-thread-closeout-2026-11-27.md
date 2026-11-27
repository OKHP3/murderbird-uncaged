# First Choice · Advanced study: closeout record

Date: November 27, 2026 (America/Chicago). Source thread: the Mac Studio Codex session that built First Choice (Apple M4 Max, Blender 5.2.1 LTS), merged to `main` by PR #105 from `private/first-choice-1123` on November 23. That thread left no closeout record of its own; this record closes it.

## Owner disposition

On November 27 the owner kept v1.1 as the final release ("Keep v1.1 final") and directed that the work be public ("No private all publicly published"). First Choice is therefore a **published, documented study**. It is not integrated into the exhibit, and its likeness is **not accepted**. The parked likeness status from November 13 is unchanged. See [goal.md](../goal.md).

## What the thread produced, and where it is

| Item | Identity | On `main` |
|---|---|---|
| Build, sculpt, motion, finish, cinema and delivery scripts | `atelier/` (finish, head, mantle, motion, pedal, cinema, delivery, runtime) | Yes |
| Integration contract: clip `First Choice`, 10.5 s, six pivots, intended host era Advanced | [atelier/delivery/integration.md](../atelier/delivery/integration.md) | Yes |
| Rebuild steps from the retained04 Advanced native | [atelier/delivery/rebuild.md](../atelier/delivery/rebuild.md) | Yes |
| Offline single-file viewer with the runtime GLB embedded (63,123,668 bytes; functional test passed offline with no network requests) | [atelier/runtime/.qa/First-Choice-portable.html](../atelier/runtime/.qa/First-Choice-portable.html), [result](../atelier/runtime/.qa/portable-functional-result.json) | Yes, as an ordinary Git file |
| Motion rig sample | [atelier/motion/native-only/rig-sample.glb](../atelier/motion/native-only/rig-sample.glb) | Yes |
| Material maps, review renders and verification evidence | `atelier/` evidence folders | Yes |
| Native scene `first-choice.blend` | SHA-256 `1e59785a11aadf491714ef1b5aa682ff1b9efa0a6a3b421414f3bb7de053a05b` | **No.** On the Mac Studio only |
| Standalone `first-choice.glb` | Embedded in the portable viewer above | Not as a separate file |
| Screening `first-choice-native-preview.mp4` (1920 × 1080, 24 fps, 252 frames, 1,820,642 bytes) | SHA-256 `fc618415923d0fcfc8332e4a4ee66607c6c81d581047782346833f15e06453ad`, [verification](../atelier/cinema/screening-verification.json) | **No.** On the Mac Studio only |
| Proof renders from `render_views.py` | Listed in the rebuild steps | **No.** On the Mac Studio only |

Labels: the study documents no longer call it private. The build and render scripts keep their original working labels ("private production candidate", "Private Advanced candidate") because they are the evidence that produced the recorded bytes; changing them would change what a rebuild writes.

## What is left, and who owns it

| Item | Owner | Next action |
|---|---|---|
| Publish the native `.blend`, the screening MP4 and the proofs | Owner, from the Mac Studio | Either attach them to a GitHub release (release assets do not use the Git LFS allowance), or commit them through Git LFS once the allowance is restored. Both make them public, so each waits on the owner's yes. Check each file against the SHA-256 above first. |
| Retire the merged branch `private/first-choice-1123` | Owner | It holds nothing that is not on `main`. Delete it when ready. |
| Archive the Codex thread | Owner | Archive it in the Codex app once the files above are published. |
