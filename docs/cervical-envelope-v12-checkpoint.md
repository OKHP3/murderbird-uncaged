# V12 curved neck construction — local correction checkpoint

September 28, 2026. **Proposal, not accepted or selected.** Continues V11 attempt 05 after the owner's rejection of V9/V10. No finished surface pass or new publication. [Actual 3D comparison](http://127.0.0.1:5183/assets/audit/uncaged-cervical-envelope-v12/index.html) and [local motion study](http://127.0.0.1:5183/?review-body=v12-02&review-seed=927).

## What changed

V11's broad posterior rings and separate throat stack made the neck read as two columns. V12 attempt 02 reshapes **51 existing rigid guards** around one forward-curving envelope: six throat plates, twelve flank plates, thirty posterior plates and three upper-breast transition plates. Staggered lower tongues break the horizontal collar lines. Attempt 01 is preserved; its narrow flank coverage left too large an opening, so attempt 02 widens those guards.

Head, bill, limbs, torso, shoulder restrictions, all 52 rest pivots and 688 other meshes remain exact relative to V11 attempt 05. The historical construction-guide curves remain unchanged and do not trace these new surfaces. Separate cervical owners retain rigid metal plates; no soft tissue or skin deformation was added.

The owner-resupplied target and Candidate 03 control the visible neck/breast relationship. July remains head-only authority. Exact guard shape, overlap, 4 mm wall thickness and unseen coverage are proposed construction, not dimensions measured from an illustration. Eligibility metadata stays inherited: these guards are passive in all eras; power and cognition are not introduced into earlier states.

## Assessment

The [independent visual review](../assets/audit/uncaged-cervical-envelope-v12/independent-visual-review.md) finds a better throat-to-breast curve and less of a separate tube. It still identifies a long head-to-breast run. Supervisor review also retains the broad cheek opening, smooth bill/optic forms and sparse leg machinery as important likeness gaps. This revision is an improvement to regional construction, not a whole-character pass. F01–F04 and the owner's whole-candidate gate remain open.

## Exact candidate

- Editable source: `assets/models/uncaged-cervical-envelope-v12/attempt-02/murderbird-cervical-envelope-v12.blend`, SHA-256 `28b18c810784a1e6872ef3743f16e5cff36e5aac66c01c9299e5195064ac7c60`.
- Runtime derivative: same directory, `murderbird-cervical-envelope-v12.glb`, 5,665,932 bytes, SHA-256 `6597cee218d7c86e741b3a942a8794f3b7e832cadb814c44d91b3e7c4e84dda3`.
- [Construction and preservation receipt](../assets/audit/uncaged-cervical-envelope-v12/attempt-02/receipt.json), [export receipt](../assets/audit/uncaged-cervical-envelope-v12/attempt-02/export-receipt.json) and frozen scripts accompany both attempts. The native is unchanged by export; all 52 pivot nodes survive. Full surface parity has not been established.

The app adds a development-only `review-body=v12-02` route and links its current geometry review to this candidate. The default model remains V9. Production builds do not contain the new model or diagnostic gallery. The V12 motion route explicitly labels its old V9 illustrated fallback.

## Movement and browser evidence

The [fresh runtime pose packet](../assets/audit/uncaged-cervical-envelope-v12/attempt-02/runtime-poses/pose-snapshot.json), SHA-256 `913fb2843d8a5ae7656c3dff26119a209789539d767179eb9b051496f4e37883`, captures 21 poses from this exact GLB. It includes all five Maker controls, combined neck/jaw, Mechanic turn/release, Advanced attention/strike/contact/recovery/jump/thrust and inspection/opening/separation. Its assertions confirm transform behavior, not surface clearance or physical dynamics. Separate mechanism offsets still require the reconciliation identified in the V11 motion note.

[Four final regional native renders](../assets/audit/uncaged-cervical-envelope-v12/attempt-02/native-poses-v3/pose-render-manifest.json) replay the exact Maker neck, Advanced contact, Advanced airborne and partial-separation samples. All 52 applied world matrices meet the unchanged strict tolerance. The initial renderer incorrectly compared grounded runtime rest with authored rest; the correction verifies raw exported rest instead. Its failed script/log and a preliminary render set that omitted the separate optic region remain preserved. Final renders include optics and share a camera following the rig root. They reveal remaining broad lateral openings and repetitive throat guards; they do not clear overlap or hidden contacts.

Actual local WebGL was checked for Maker neck control, Advanced opening, full separation and return to closed/unseparated state. The gallery's explicitly labeled fixed-native fallback and return to 3D were checked. Browser captures and state/pose records are under `attempt-02/browser/`. Review camera and lighting were set to neutral locally; this is distinct from an exhibit-light acceptance pass.

During the Maker full-neck hold on Apple M4 Max/ANGLE Metal, the canvas was 856 × 648 at pixel ratio 1. The rolling 180-frame observation reported median 10 ms, 95th-percentile 10.7 ms, 233 draw calls and 550,616 triangles. This short observation is not a whole-device or complete-motion benchmark.

`npm ci`, `npm run build`, publication-boundary validation and source syntax checks passed locally. The boundary retains 134 intended output paths and 16 exact selected runtime assets. The existing large-chunk warning remains. [Validation receipt and retained logs](../assets/audit/uncaged-cervical-envelope-v12/attempt-02/local-validation.json) identify the modified tree and served GLB. No remote CI or deployment claim is made.

Next work remains geometric: correct the constructed cheek/bill relationship and review its junction with the revised neck while keeping the whole bird in view. Guard overlap and hardware attachment clearance still require explicit checks. Do not disguise those defects with materials. The three finished era exteriors, reconciled mechanism attachments and owner artistic decisions remain outstanding.
